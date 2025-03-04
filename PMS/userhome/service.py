from decouple import config
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Poultry ,BillPost,Total,DeadInfo
from django.utils.timezone import now, timedelta
from django.contrib import messages
from django.shortcuts import redirect

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
        

def getContextOfPoultry(request, user_id, poultryName):
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

