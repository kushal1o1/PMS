from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Poultry ,BillPost,Total,DeadInfo
from django.contrib.auth.models import User
from datetime import datetime
import requests
from info import api_key
    
app_name='userhome' 


@login_required
def userHome(request,user_id): 
    user_info = Poultry.objects.filter(user_id=user_id).order_by('startDate')
    return render(request, 'mainpage.html',{'parms':user_info})



@login_required
def submit_detail(request,user_id):
   
    if request.method == 'POST':
        print(1.2)
        if 'detailform' in request.POST:
            farmname = request.POST.get('farmname')
            Total=request.POST.get('Total')
            startdate=request.POST.get('Startdate')
            poultryobj=Poultry.objects.create(
            user=get_object_or_404(User, id=user_id),
            poultryName=farmname,
            totalChicken=Total,
           
            )
        


    return redirect('userhome:mainpage', user_id=user_id)



    

def profile(request,user_id,poultryName):
    poultry_info = Poultry.objects.filter(user_id=user_id).filter(poultryName=poultryName)
    Bill_info = BillPost.objects.filter(poultryName=poultryName).order_by('-posted_date')
    total_bills=BillPost.objects.count()
    poultry = Poultry.objects.get(user_id=user_id, poultryName=poultryName)

    # Fetch or create the Total object for the specific poultry
    total_obj, created = Total.objects.get_or_create(poultryName=poultry)

    # Now you can call calculate_totals method to update the totals
    total_obj.calculate_totals(poultry.user)

    # Access the total values
    total_dana = total_obj.totalDana
    total_medicine = total_obj.totalMedicine
    total_vaccine = total_obj.totalVaccine
    total_amount = total_obj.totalAmount
    total_Bhus = total_obj.totalBhus
    todayDate=datetime.now()
    context={"poultry":poultry,"bills":Bill_info,'dana':total_dana,'medicine':total_medicine,'vaccine':total_vaccine,'total_amount':total_amount,
    'total_bhus':total_Bhus,'todayDate':todayDate,
    'total_bills':total_bills
    }

    url = f'http://api.openweathermap.org/data/2.5/weather?q=pokhara&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    print(data)
    
    temperature = data['main']['temp']
    rain = data.get('rain', {}).get('1h', 0)  # Assuming rain volume in the last hour
    wind_speed = data['wind']['speed']
        
    is_raining = rain > 0
    is_sunny = not is_raining and temperature > 25
    is_windy = wind_speed > 5
    is_hot = temperature > 30
    is_cold = temperature < 10
    is_moderate=not is_raining and not is_sunny and not is_windy and not is_hot and not is_cold
    temp_data = {
        'temperature': temperature,
        'rain': rain,
        'wind_speed': wind_speed,
        'is_raining': is_raining,
        'is_sunny': is_sunny,
        'is_windy': is_windy,
        'is_hot': is_hot,
        'is_cold': is_cold,
        'is_moderate':is_moderate
    }
    print(is_moderate)
    return render(request, 'profile.html',{'parm':poultry_info[0],
    'bill':Bill_info,'context':context,
    'temp':temp_data})


@login_required
def submit_bill(request, user_id, poultryName):
    poultry_info = Poultry.objects.filter(user_id=user_id).filter(poultryName=poultryName)
    if request.method == 'POST':

        if 'billform' in request.POST:
            image_file = request.FILES.get('imageofbill')
            feed = request.POST.get('feed')
            medicine = request.POST.get('medicine')
            vaccine = request.POST.get('vaccine')
            TotalChickenFeed = request.POST.get('TotalChickenFeed')
            totalMedicine = request.POST.get('totalMedicine')
            total = request.POST.get('total')
            totalBhus = request.POST.get('totalBhus')
            if vaccine:
                totalvaccine = 1
            else:
                totalvaccine = 0
            new_image_post = BillPost(
                poultryName=poultry_info[0],  # Assign the poultry instance
                imgfile=image_file,
                totalChickenFeed=TotalChickenFeed,
                totalMedicine=totalMedicine,
                totalBhus=totalBhus,
                totalAmount=total,
                totalVaccine=totalvaccine
            )
            new_image_post.save()

        if 'Deadform' in request.POST:
                    deadbirds = int(request.POST.get("TotalChickenDead"))
                    poultry_info = Poultry.objects.filter(user_id=user_id, poultryName=poultryName).first()  
                    poultry_info.totalDead += deadbirds 
                    poultry_info.save() 
                    new_dead_hen_post = DeadInfo(
                            poultryName=poultry_info, 
                            totalDead=deadbirds
                        )
                    new_dead_hen_post.save()

                
    return redirect('userhome:profile', user_id=user_id, poultryName=poultryName)

@login_required
def showBills(request, user_id, poultryName):
    poultry_info = Poultry.objects.filter(user_id=user_id).filter(poultryName=poultryName)
    bills = BillPost.objects.filter(poultryName=poultry_info[0], poultryName__poultryName=poultryName).order_by('-posted_date')
    print(bills)
    return render(request, 'showbills.html', {'bills': bills})




@login_required
def showVaccine(request,user_id,poultryName):
     poultry_info = Poultry.objects.filter(user_id=user_id).filter(poultryName=poultryName)
     Bill_info = BillPost.objects.filter(poultryName=poultry_info[0], poultryName__poultryName=poultryName).order_by('-posted_date')
     Dead_info = DeadInfo.objects.filter( poultryName__poultryName=poultryName).order_by('-deadDate')
     print(Dead_info)
     return render(request, 'showVaccine.html',{
    'bills':Bill_info})

    
@login_required
def showDeads(request,user_id,poultryName):
     poultry_info = Poultry.objects.filter(user_id=user_id).filter(poultryName=poultryName)
     Dead_info = DeadInfo.objects.filter( poultryName__poultryName=poultryName).order_by('-deadDate')
     print(Dead_info)
     return render(request, 'showdeads.html',{
    'deads':Dead_info})