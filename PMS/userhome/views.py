from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Poultry ,BillPost,Total,DeadInfo
from django.contrib.auth.models import User
from datetime import datetime
import requests
from django.contrib import messages
from django.utils.timezone import now, timedelta
from info import api_key
from django.http import JsonResponse
from django.db import transaction

    
app_name='userhome' 


@login_required
def userHome(request,user_id): 
    user_info = Poultry.objects.filter(user_id=user_id).order_by('startDate')
    return render(request, 'mainpage.html',{'parms':user_info})



@login_required
def submit_detail(request,user_id):
   
    if request.method == 'POST':
        if 'detailform' in request.POST:
            farmname = request.POST.get('farmname')
            Total=request.POST.get('Total')
            startdate=request.POST.get('Startdate')
            poultryobj=Poultry.objects.create(
            user=get_object_or_404(User, id=user_id),
            poultryName=farmname,
            totalChicken=Total,
           
            )
            messages.success(request, "Poultry Register SucessFully")
    


    return redirect('userhome:mainpage', user_id=user_id)






def profile(request, user_id, poultryName):
    try:
   
        poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)
        bills = BillPost.objects.filter(poultryName=poultryName).order_by('-posted_date')
        total_bills = bills.count()

        total_obj, created = Total.objects.get_or_create(poultryName=poultry)
        total_obj.calculate_totals(poultry.user)


        total_dana = total_obj.totalDana
        total_medicine = total_obj.totalMedicine
        total_vaccine = total_obj.totalVaccine
        total_amount = total_obj.totalAmount
        total_bhus = total_obj.totalBhus

 
        adjusted_time = now() + timedelta(hours=6, minutes=15)


   
        url = f'http://api.openweathermap.org/data/2.5/weather?q=pokhara&appid={api_key}&units=metric'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            data = response.json()
        except requests.RequestException as e:
            return JsonResponse({'error': 'Weather API request failed', 'details': str(e)}, status=500)
        except ValueError as e:
            return JsonResponse({'error': 'Failed to parse JSON response from Weather API', 'details': str(e)}, status=500)

        # Extract weather data
        try:
            temperature = data['main']['temp']
            rain = data.get('rain', {}).get('1h', 0)
            wind_speed = data['wind']['speed']
        except KeyError as e:
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

        return render(request, 'profile.html', {
            'parm': poultry,
            'bill': bills,
            'context': context,
            'temp': temp_data
        })

    except Poultry.DoesNotExist:
        return JsonResponse({'error': 'Poultry not found'}, status=404)
    except Total.DoesNotExist:
        return JsonResponse({'error': 'Total object not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)








@login_required
def submit_bill(request, user_id, poultryName):
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

                    # Validate non-negative values
                    if (float(TotalChickenFeed) < 0 or float(totalMedicine) < 0 or
                        float(total) < 0 or float(totalBhus) < 0):
                        messages.error(request, "Values cannot be negative.")
                        return redirect('userhome:profile', user_id=user_id, poultryName=poultryName)

                    totalvaccine = 1 if vaccine else 0

                    new_bill = BillPost(
                        poultryName=poultry,
                        imgfile=image_file,
                        totalChickenFeed=TotalChickenFeed,
                        totalMedicine=totalMedicine,
                        totalBhus=totalBhus,
                        totalAmount=total,
                        totalVaccine=totalvaccine
                    )
                    new_bill.save()
                    messages.success(request, "Bill Submitted Successfully")

                if 'Deadform' in request.POST:
                    deadbirds = int(request.POST.get("TotalChickenDead", 0))

                    # Validate non-negative values
                    if deadbirds < 0:
                        messages.error(request, "Total Dead cannot be negative.")
                        return redirect('userhome:profile', user_id=user_id, poultryName=poultryName)

                    poultry.totalDead += deadbirds
                    poultry.save()

                    new_dead_hen_post = DeadInfo(
                        poultryName=poultry,
                        totalDead=deadbirds
                    )
                    new_dead_hen_post.save()
                    messages.success(request, "Dead info of Chicken submitted successfully")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            transaction.rollback()

    return redirect('userhome:profile', user_id=user_id, poultryName=poultryName)



@login_required
def showBills(request, user_id, poultryName):
    poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)
    bills = BillPost.objects.filter(poultryName=poultry).order_by('posted_date')

    return render(request, 'showbills.html', {'bills': bills})





@login_required
def showVaccine(request, user_id, poultryName):
    poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)
    bills = BillPost.objects.filter(poultryName=poultry).order_by('posted_date')
    return render(request, 'showVaccine.html', {'bills': bills})

@login_required
def showDeads(request, user_id, poultryName):
    poultry = get_object_or_404(Poultry, user_id=user_id, poultryName=poultryName)
    deads = DeadInfo.objects.filter(poultryName=poultry).order_by('-deadDate')
    return render(request, 'showdeads.html', {'deads': deads})

def notFound(request):
    return render(request,'pageNotFound.html')