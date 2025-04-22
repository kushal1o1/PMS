from decouple import config
from django.conf import settings
import requests
from django.http import JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404
from .models import Poultry ,BillPost,Total,DeadInfo
from django.utils.timezone import now, timedelta
from django.contrib import messages
from openai import OpenAI
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import os
from datetime import datetime
from collections import defaultdict



def getWeatherInfo(request):
        url = f'http://api.openweathermap.org/data/2.5/weather?q=pokhara&appid={config("OPENWEATHER_API_KEY")}&units=metric'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            data = response.json()
        except requests.RequestException as e:
            messages.error(request, "Weather API request failed")
            return JsonResponse({'error': 'Weather API request failed', 'details': str(e)}, status=500)
        except ValueError as e:
            messages.error(request, "Failed to parse JSON response from Weather")
            return JsonResponse({'error': 'Failed to parse JSON response from Weather API', 'details': str(e)}, status=500)

        # Extract weather data
        try:
            temperature = data['main']['temp']
            rain = data.get('rain', {}).get('1h', 0)
            wind_speed = data['wind']['speed']
        except KeyError as e:
            messages.error(request, "Expected weather data not found in API response")
            return JsonResponse({'error': 'Expected weather data not found in API response', 'details': str(e)}, status=500)
        
        # Weather conditions
        is_raining = rain > 0
        is_sunny = not is_raining and temperature > 25
        is_windy = wind_speed > 5
        is_hot = temperature > 30
        is_cold = temperature < 10
        is_moderate = not (is_raining or is_sunny or is_windy or is_hot or is_cold)
        temp_data = {
            'temperature': temperature,
            'rain': rain,
            'wind_speed': wind_speed,
            'is_raining': is_raining,
            'is_sunny': is_sunny,
            'is_windy': is_windy,
            'is_hot': is_hot,
            'is_cold': is_cold,
            'is_moderate': is_moderate
        }
        return temp_data
        
def UpdateTotal(user_id,poultryName):
    poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)
    total_obj, created = Total.objects.get_or_create(poultryName=poultry)
    total_obj.calculate_totals(poultry.user)
    total_obj.save()
    
def getContextOfPoultry(request, user_id, poultryName):
    try:
   
        poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)
        bills = BillPost.objects.filter(poultryName=poultryName).order_by('-posted_date')
        total_bills = bills.count()

        total_obj, created = Total.objects.get_or_create(poultryName=poultry)
        total_obj.calculate_totals(poultry.user)
        total_obj.save()

        total_dana = total_obj.totalDana
        total_medicine = total_obj.totalMedicine
        total_vaccine = total_obj.totalVaccine
        total_amount = total_obj.totalAmount
        total_bhus = total_obj.totalBhus

 
        adjusted_time = now() + timedelta(hours=5, minutes=45)


        context = {
            'poultry': poultry,
            'bills': bills,
            'dana': total_dana,
            'medicine': total_medicine,
            'vaccine': total_vaccine,
            'total_amount': total_amount,
            'total_bhus': total_bhus,
            'todayDate': adjusted_time,
            'total_bills': total_bills
        }

        return context

    except Poultry.DoesNotExist:
        messages.error(request, "Poultry not found")
        return JsonResponse({'error': 'Poultry not found'}, status=404)
    except Total.DoesNotExist:
        messages.error(request, "Total object not found")
        return JsonResponse({'error': 'Total object not found'}, status=404)
    except Exception as e:
        messages.error(request, "An unexpected error occurred")
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

def handleBillForm(request,TotalChickenFeed, totalMedicine, total, totalBhus, vaccine, desc, image_file, poultry,user_id, poultryName):
    try:
        TotalChickenFeed = int(TotalChickenFeed) if TotalChickenFeed else 0
        totalMedicine = int(totalMedicine) if totalMedicine else 0
        total = int(total) if total else 0
        totalBhus = int(totalBhus) if totalBhus else 0

        if TotalChickenFeed < 0 or totalMedicine < 0 or total < 0 or totalBhus < 0:
            messages.error(request, "Values cannot be negative.")
            return False

    except ValueError:
            messages.error(request, "Please enter valid integer values.")
            return False

    totalvaccine = 1 if vaccine else 0

    new_bill = BillPost(
                        poultryName=poultry,
                        imgfile=image_file,
                        totalChickenFeed=TotalChickenFeed,
                        totalMedicine=totalMedicine,
                        totalBhus=totalBhus,
                        totalAmount=total,
                        totalVaccine=totalvaccine,
                        description=desc
                    )
    new_bill.save()
    messages.success(request, "Bill Submitted Successfully")
    return True

def handleDeadForm(request, deadbirds, deaddesc, poultry, user_id, poultryName):
    if deadbirds < 0:
        messages.error(request, "Total Dead cannot be negative.")
        return False

    poultry.totalDead += deadbirds
    poultry.save()

    new_dead_hen_post = DeadInfo(
                        poultryName=poultry,
                        totalDead=deadbirds,
                        description=deaddesc
                    )
    new_dead_hen_post.save()
    messages.success(request, "Dead info of Chicken submitted successfully")
    return True

def CheckUser(request, user_id):
    if request.user.id != user_id:
        messages.error(request, "You are not authorized to view this page.")
        return False
    return True


def createReport(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="poultry_comparison_report.pdf"'
    
    # Create the PDF object using reportlab
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []
    
    # Get styles for text
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = TA_CENTER  # Center the text
    subtitle_style = ParagraphStyle(
    'SubtitleStyle',
    parent=styles['Heading2'],
    alignment=TA_CENTER  # Center the text
    )

# Centered Normal Text Style
    normal_style = ParagraphStyle(
    'NormalStyle',
    parent=styles['Normal'],
    alignment=TA_CENTER  # Center the text
)
    dateToday = now()
    # Company Logo 
    logo_path = os.path.join(settings.BASE_DIR, "userhome/static/images/chickenlogo.jpg")
    elements.append(Image(logo_path, width=100, height=50))
    elements.append(Spacer(1, 0.25*inch))

    # Add Company Name
    elements.append(Paragraph("Poultry Solutions ltd.", subtitle_style))

    # Add Contact Information
    elements.append(Paragraph("Email: support@poultry.com", normal_style))
    elements.append(Paragraph("Phone: +1 234 567 890", normal_style))
    elements.append(Spacer(1, 0.25*inch))

    # Add title
    elements.append(Paragraph("Poultry Comparison Report", title_style))    
    # Add metadata
    elements.append(Paragraph(f"Generated on: {dateToday.strftime('%B %d, %Y')}", normal_style))
    
    # Add user information
    elements.append(Paragraph(f"User: {request.user.username}", normal_style))
    elements.append(Spacer(1, 0.25*inch))
    
    
    # Get all poultry for the current user
    poultries = Poultry.objects.filter(user=request.user)
    
    if not poultries.exists():
        elements.append(Paragraph("No poultry records found.", normal_style))
        doc.build(elements)
        return response
    
    # Comparative overview section
    elements.append(Paragraph("Comparative Overview", subtitle_style))
    
    # Basic comparison table
    comparison_data = [
        ["Poultry Name", "Total Chickens",  "Dead Chickens",  "Mortality Rate","Status","Total Weight","Earned Amount"]
    ]
    for poultry in poultries:
        total = Total.objects.get(poultryName=poultry.poultryName)
        
        mortality_rate = (poultry.totalDead / poultry.totalChicken * 100) if poultry.totalChicken > 0 else 0
        comparison_data.append([
            poultry.poultryName,
            str(poultry.totalChicken),
            str(poultry.totalDead),
            f"{mortality_rate:.2f}%",
            poultry.Status,
            str(poultry.TotalWeight),
            str(abs((total.totalAmount+ poultry.TransportCost) - total.totalAmount))
            
        ])
    
    comparison_table = Table(comparison_data, colWidths=[1.5*inch]*6)
    comparison_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    elements.append(comparison_table)
    elements.append(Spacer(1, 0.3*inch))
    
    elements.append(Paragraph("Selling Overview", subtitle_style))
    
    # Basic Selling comparison table
    comparison_data = [
        ["Poultry Name", "Total Chickens","Status","RatePerKg","Total Weight","TotalAmount","Earned Amount"]
    ]
    
    
    for poultry in poultries:
        total = Total.objects.get(poultryName=poultry.poultryName)
        
        mortality_rate = (poultry.totalDead / poultry.totalChicken * 100) if poultry.totalChicken > 0 else 0
        comparison_data.append([
            poultry.poultryName,
            str(poultry.totalChickenNow),
            poultry.Status,
            str(poultry.RatePerKg),
            str(poultry.TotalWeight),
            str(total.totalAmount+ poultry.TransportCost),
            str(abs((total.totalAmount+ poultry.TransportCost) - total.totalAmount))
        ])
    
    comparison_table = Table(comparison_data, colWidths=[1.5*inch]*6)
    comparison_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    elements.append(comparison_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Get expense data for comparison
    expenses_data = [["Poultry Name", "Feed", "Medicine", "Vaccine", "Bhus", "Transport Cost","Total Amount", "Cost per Chicken"]]
    
    for poultry in poultries:
        try:
            total = Total.objects.get(poultryName=poultry.poultryName)
            cost_per_chicken = total.totalAmount / poultry.totalChickenNow if poultry.totalChickenNow > 0 else 0
            expenses_data.append([
                poultry.poultryName,
                (total.totalDana),
                str(total.totalMedicine),
                str(total.totalVaccine),
                str(total.totalBhus),
                str(poultry.TransportCost),
                str(total.totalAmount+ poultry.TransportCost),
                f"{cost_per_chicken:.2f}"
            ])
        except Total.DoesNotExist:
            expenses_data.append([
                poultry.poultryName,
                "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
            ])
    
    elements.append(Paragraph("Expense Comparison", subtitle_style))
    expenses_table = Table(expenses_data, colWidths=[1.3*inch] * 7)
    expenses_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    elements.append(expenses_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Mortality trend comparison
    elements.append(Paragraph("Mortality Trend Comparison", subtitle_style))
    
    # Create a dictionary to store mortality by date for each poultry
    mortality_by_poultry = defaultdict(lambda: defaultdict(int))
    all_dates = set()
    
    for poultry in poultries:
        dead_infos = DeadInfo.objects.filter(poultryName=poultry).order_by('deadDate')
        for info in dead_infos:
            mortality_by_poultry[poultry.poultryName][info.deadDate] += info.totalDead
            all_dates.add(info.deadDate)
    
    if all_dates:
        # Sort dates for consistent ordering
        sorted_dates = sorted(all_dates)
        
        # Create table headers with dates
        mortality_data = [["Poultry Name"] + [date.strftime('%Y-%m-%d') for date in sorted_dates] + ["Total"]]
        
        for poultry_name in mortality_by_poultry:
            row = [poultry_name]
            total_dead = 0
            for date in sorted_dates:
                dead_count = mortality_by_poultry[poultry_name][date]
                total_dead += dead_count
                row.append(str(dead_count))
            row.append(str(total_dead))
            mortality_data.append(row)
        
        # Calculate column widths based on number of dates
        date_width = min(0.8, 8.0 / (len(sorted_dates) + 2)) * inch
        mortality_table = Table(mortality_data, colWidths=[1.5*inch] + [date_width] * (len(sorted_dates)) + [date_width])
        
        mortality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))
        elements.append(mortality_table)
    else:
        elements.append(Paragraph("No mortality data available for comparison", normal_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary statistics section
    elements.append(Paragraph("Summary Statistics", subtitle_style))
    
    # Calculate overall statistics
    total_chickens = sum(p.totalChicken for p in poultries)
    total_current = sum(p.totalChickenNow for p in poultries)
    total_dead = sum(p.totalDead for p in poultries)
    avg_mortality_rate = (total_dead / total_chickens * 100) if total_chickens > 0 else 0
    
    # Calculate average expenses
    try:
        totals = Total.objects.filter(poultryName__in=poultries)
        total_expenses = sum(t.totalAmount for t in totals)
        avg_cost_per_chicken = total_expenses / total_current if total_current > 0 else 0
    except:
        total_expenses = 0
        avg_cost_per_chicken = 0
    
    summary_data = [
        ["Total Chickens", "Current Chickens", "Total Dead", "Overall Mortality Rate", "Total Expenses", "Avg. Cost per Chicken"],
        [
            str(total_chickens),
            str(total_current),
            str(total_dead),
            f"{avg_mortality_rate:.2f}%",
            str(total_expenses),
            f"{avg_cost_per_chicken:.2f}"
        ]
    ]
    
    summary_table = Table(summary_data, colWidths=[1.5*inch]*6)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
    ]))
    elements.append(summary_table)
    elements.append(Paragraph("Executive Summary", subtitle_style))
    elements.append(Paragraph("This report provides a comparative analysis of various poultry Details.", normal_style))
    elements.append(Spacer(1, 0.25*inch))

    # Build the PDF
    doc.build(elements)
    return response


        
def getMedicineInfo(medicine_name):
    print("Iam at getMedicineInfo")
    print("Medicine Name:", medicine_name)
    client = OpenAI(api_key=config('OPENAI_API_KEY'))
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
        messages=[
        {
            "role": "system",
            "content": "You are a professional veterinary pharmacologist specializing in poultry medicine with extensive experience in the field. Provide standardized, structured information following a consistent format for all medicine queries.Answer in Nepali Language all responses"
        },
        {
            "role": "user",
            "content": f"""
            Provide a comprehensive profile for the poultry medication: {medicine_name}

            Format your response in HTML with Bootstrap classes, Font Awesome icons, and an actual image not dummy url. Use the following structured format:

            <div class="container mt-4">
                <div class="card shadow-lg">
                    <div class="card-header bg-primary text-white">
                        <h2 class="text-center"><i class="fas fa-capsules"></i> {medicine_name} - Poultry Medication Profile</h2>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4 text-center">
                            <img src="[url ]" class="img-fluid rounded" alt="Poultry Medicine Image">

                            </div>
                            <div class="col-md-8">
                                <h3 class="text-primary"><i class="fas fa-info-circle"></i> General Information</h3>
                                <ul class="list-group">
                                    <li class="list-group-item"><strong>Type/Class:</strong> [Type of Medication]</li>
                                    <li class="list-group-item"><strong>Active Ingredients:</strong> [Active Ingredients]</li>
                                    <li class="list-group-item"><strong>Pharmacological Classification:</strong> [Classification]</li>
                                    <li class="list-group-item"><strong>Target Pathogens/Diseases:</strong> [Pathogens/Diseases]</li>
                                </ul>

                                <h3 class="text-success mt-4"><i class="fas fa-stethoscope"></i> Therapeutic Uses</h3>
                                <ul class="list-group">
                                    <li class="list-group-item"><strong>Primary Indications:</strong> [Primary Indications]</li>
                                    <li class="list-group-item"><strong>Secondary Uses:</strong> [Secondary Uses]</li>
                                    <li class="list-group-item"><strong>Disease States Treated:</strong> [Disease States]</li>
                                </ul>
                            </div>
                        </div>

                        <h3 class="text-warning mt-4"><i class="fas fa-prescription-bottle-alt"></i> Dosage & Administration</h3>
                        <ul class="list-group">
                            <li class="list-group-item"><strong>Recommended Dosage:</strong> [Dosage]</li>
                            <li class="list-group-item"><strong>Route of Administration:</strong> [Route]</li>
                            <li class="list-group-item"><strong>Treatment Duration:</strong> [Duration]</li>
                            <li class="list-group-item"><strong>Preparation Instructions:</strong> [Instructions]</li>
                        </ul>

                        <h3 class="text-danger mt-4"><i class="fas fa-exclamation-triangle"></i> Precautions & Contraindications</h3>
                        <ul class="list-group">
                            <li class="list-group-item"><strong>Safety Warnings:</strong> [Warnings]</li>
                            <li class="list-group-item"><strong>Known Contraindications:</strong> [Contraindications]</li>
                            <li class="list-group-item"><strong>Drug Interactions:</strong> [Interactions]</li>
                        </ul>

                        <h3 class="text-info mt-4"><i class="fas fa-clock"></i> Withdrawal Period</h3>
                        <ul class="list-group">
                            <li class="list-group-item"><strong>Meat Withdrawal Time:</strong> [Meat Withdrawal]</li>
                            <li class="list-group-item"><strong>Egg Withdrawal Time:</strong> [Egg Withdrawal]</li>
                        </ul>

                        <h3 class="text-primary mt-4"><i class="fas fa-warehouse"></i> Storage & Handling</h3>
                        <ul class="list-group">
                            <li class="list-group-item"><strong>Storage Conditions:</strong> [Storage Conditions]</li>
                            <li class="list-group-item"><strong>Shelf Life:</strong> [Shelf Life]</li>
                            <li class="list-group-item"><strong>Special Handling Requirements:</strong> [Handling Requirements]</li>
                        </ul>

                        <h3 class="text-success mt-4"><i class="fas fa-language"></i> नेपाली अनुवाद (Nepali Translation)</h3>
                        <p class="alert alert-success">
                            <strong>मुख्य प्रयोग:</strong> [Uses in Nepali] <br>
                            <strong>खुराक:</strong> [Dosage in Nepali] <br>
                            <strong>सावधानी:</strong> [Precautions in Nepali]
                        </p>
                    </div>
                </div>
            </div>
            """
            }
        ],
        max_tokens=800
        )
        medicine_info = response.choices[0].message.content.strip()
    except Exception as e:
        print("Error:", e)
        medicine_info = "<p>Error fetching medicine information. Please try again later.</p>"
    return medicine_info


