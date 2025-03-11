from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Poultry ,BillPost,Total,DeadInfo
from django.contrib.auth.models import User
from datetime import datetime
import requests
from django.contrib import messages
from django.utils.timezone import now
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from decouple import config
from .service import getWeatherInfo,getContextOfPoultry,handleBillForm,handleDeadForm,CheckUser,createReport,UpdateTotal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import  NotificationUser
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from .models import Poultry, Total, DeadInfo
from django.contrib.auth.decorators import login_required
from collections import defaultdict
import datetime
app_name='userhome' 


@login_required
def userHome(request,user_id): 
    
    messages.success(request, "Welcome to Poultry Management System")
    if not CheckUser(request, user_id):
        return redirect('/')
    user_info = Poultry.objects.filter(user_id=user_id).order_by('-startDate')
    for poultry in user_info:
        poultryName = poultry.poultryName
        UpdateTotal(user_id,poultryName)
    return render(request, 'mainpage.html',{'parms':user_info})



@login_required
def submit_detail(request,user_id):
    if not CheckUser(request, user_id):
        return redirect('/')
    if request.method == 'POST':
        if 'detailform' in request.POST:
            farmname = request.POST.get('farmname')
            Total=request.POST.get('Total')
            startdate=request.POST.get('Startdate')
            if Poultry.objects.filter(user_id=user_id,poultryName=farmname).exists():
                messages.error(request, "Poultry Name Already Exists")
                messages.info(request, "Please Choose another Poultry Name")
                return redirect('userhome:mainpage', user_id=user_id)
            if Total is None or farmname is None:
                messages.error(request, "Please Fill all the Fields")
                return redirect('userhome:mainpage', user_id=user_id)
            if int(Total) < 0:
                messages.error(request, "Total Chicken must be greater than 0")
                return redirect('userhome:mainpage', user_id=user_id)
            Poultry.objects.create(
            user=get_object_or_404(User, id=user_id),
            poultryName=farmname,
            totalChicken=Total,
           
            )
            messages.success(request, "Poultry Register SucessFully")
    


    return redirect('userhome:mainpage', user_id=user_id)





@login_required
def profile(request, user_id, poultryName):
    if not CheckUser(request, user_id):
        return redirect('/')
   
    temp_data = getWeatherInfo(request)

    context = getContextOfPoultry(request, user_id, poultryName)
    return render(request, 'profile.html', {
            'context': context,
            'temp': temp_data,
        })

    








@login_required
def submit_bill(request, user_id, poultryName):
    if not CheckUser(request, user_id):
        return redirect('/')
    poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                if 'billform' in request.POST:
                    image_file = request.FILES.get('imageofbill')
                    vaccine = request.POST.get('vaccine')
                    TotalChickenFeed = request.POST.get('TotalChickenFeed', 0)
                    totalMedicine = request.POST.get('totalMedicine', 0)
                    total = request.POST.get('total', 0)
                    totalBhus = request.POST.get('totalBhus', 0)
                    desc =request.POST.get('desc')
                    if not handleBillForm(request,TotalChickenFeed, totalMedicine, total, totalBhus, vaccine, desc, image_file, poultry,user_id, poultryName):
                        return redirect('userhome:profile', user_id=user_id, poultryName=poultryName)
                    


                if 'Deadform' in request.POST:
                    deadbirds = int(request.POST.get("TotalChickenDead", 0))
                    deaddesc = request.POST.get('deaddesc')
                    if not  handleDeadForm(request, deadbirds, deaddesc, poultry, user_id, poultryName):
                        return redirect('userhome:profile', user_id=user_id, poultryName=poultryName)   
                    

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            transaction.rollback()

    return redirect('userhome:profile', user_id=user_id, poultryName=poultryName)



@login_required
def showBills(request, user_id, poultryName):
    if not CheckUser(request, user_id):
        return redirect('/')
    poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)
    bills = BillPost.objects.filter(poultryName=poultry).order_by('posted_date')

    return render(request, 'showbills.html', {'bills': bills,
                                              'poultryName': poultryName,
                                              'user_id': user_id})





@login_required
def showVaccine(request, user_id, poultryName):
    if not CheckUser(request, user_id):
        return redirect('/')
    poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)
    bills = BillPost.objects.filter(poultryName=poultry).order_by('posted_date')
    return render(request, 'showVaccine.html', {'bills': bills,
                                                'poultryName': poultryName,
                                              'user_id': user_id})

@login_required
def showDeads(request, user_id, poultryName):
    if not CheckUser(request, user_id):
        return redirect('/')
    poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)
    deads = DeadInfo.objects.filter(poultryName=poultry).order_by('-deadDate')
    return render(request, 'showdeads.html', {'deads': deads,
                                              'poultryName': poultryName,
                                              'user_id': user_id})

def notFound(request,exception):
    return render(request,'pageNotFound.html',status=404)



@csrf_exempt
def mark_notification_as_read(request,notification_id):
    print("Marking notification as read")
    """Mark a notification as read for the current user."""
    if request.method == "POST":
        print("Marking notification as read,ENteringPOst")
        user = request.user
        
        if not CheckUser(request, user.user_id):
            return redirect('/')
        print("User:", user)
        try:
            notification_user = NotificationUser.objects.get(user=user, notification_id=notification_id)
            notification_user.is_read = True
            notification_user.save()
            print("Notification marked as read")
            return JsonResponse({"status": "success"})
        except NotificationUser.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Notification not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

def get_unread_notifications(request):
    print("Getting unread notifications")
    user = request.user
        
    
    unread_notifications = NotificationUser.objects.filter(user=user, is_read=False)
    data = [{"id": n.notification.id, "message": n.notification.message} for n in unread_notifications]
    print("Unread notifications:", data)
    return JsonResponse({"notifications": data})

def mark_all_notifications_as_read(request):
    print("Marking all notifications as read")
    user = request.user
        
    if not CheckUser(request, user.user_id):
            return redirect('/')
    notifications = NotificationUser.objects.filter(user=user, is_read=False)
    for notification_user in notifications:
            notification_user.is_read = True
            notification_user.save()
    return JsonResponse({"status": "success"})



@login_required
def generate_pdf(request):
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="poultry_comparison_report.pdf"'
    
    # Create the PDF object using reportlab
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []
    
    # Get styles for text
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    dateToday = datetime.date.today()
    # Add title
    elements.append(Paragraph("Poultry Comparison Report", title_style))
    elements.append(Paragraph(f"Generated on: {dateToday.strftime('%B %d, %Y')}", normal_style))
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
        ["Poultry Name", "Total Chickens", "Current Chickens", "Dead Chickens", "Days Running", "Mortality Rate"]
    ]
    
    for poultry in poultries:
        mortality_rate = (poultry.totalDead / poultry.totalChicken * 100) if poultry.totalChicken > 0 else 0
        comparison_data.append([
            poultry.poultryName,
            str(poultry.totalChicken),
            str(poultry.totalChickenNow),
            str(poultry.totalDead),
            str(poultry.totalDays),
            f"{mortality_rate:.2f}%"
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
    expenses_data = [["Poultry Name", "Feed", "Medicine", "Vaccine", "Bhus", "Total Amount", "Cost per Chicken"]]
    
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
                str(total.totalAmount),
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
    
    # Build the PDF
    doc.build(elements)
    return response


import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from decouple import config
def getMedicineInfo(medicine_name):
    print("Iam at getMedicineInfo")
    print("Medicine Name:", medicine_name)
    client = OpenAI(api_key=config
    ('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
messages=[
    {
        "role": "system",
        "content": "You are a professional veterinary pharmacologist specializing in poultry medicine with extensive experience in the field. Provide standardized, structured information following a consistent format for all medicine queries."
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
max_tokens=1000
    )
    medicine_info = response.choices[0].message.content.strip()
    # print("Medicine Info:", medicine_info)
    return medicine_info

# Initialize the OpenAI client
client = OpenAI(api_key=config('OPENAI_API_KEY'))
# @csrf_exempt
# def get_medicine_info(request):
#     """API endpoint to get medicine information"""
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             medicine_name = data.get('medicine_name')

#             if not medicine_name:
#                 return JsonResponse({'error': 'Medicine name is required'}, status=400)
            
#             medicine_info = getMedicineInfo(medicine_name)
#             return JsonResponse({'medicine_info': medicine_info, 'success': True})

#         except Exception as e:
#             return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
#     return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

def medicine_view(request):  
    # getMedicineInfo("Amoxicillin")  
    """View to render the medicine information page"""
    messages.success(request, "Welcome to the Medicine Information Page")
    messages.info(request, "Enter the name of the medicine to get detailed information")
    return render(request, 'medicine.html')


def search_medicine(request):
    """
    API endpoint to handle medicine search requests
    """
    if request.method == 'POST':
        medicine_name = request.POST.get('medicine', '')
        if not medicine_name:
            return JsonResponse({'error': 'No medicine name provided'}, status=400)
        # Call your custom function to get medicine information
        medicine_info = getMedicineInfo(medicine_name)
        return JsonResponse({
            'medicine_name': medicine_name,
            'medicine_info': medicine_info
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)