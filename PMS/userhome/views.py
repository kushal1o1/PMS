from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Poultry ,BillPost,Total,DeadInfo
from django.contrib.auth.models import User
from datetime import datetime
import requests
from django.contrib import messages
from django.utils.timezone import now, timedelta
from django.http import JsonResponse
from django.db import transaction
from decouple import config
from .service import getWeatherInfo,getContextOfPoultry,handleBillForm,handleDeadForm,CheckUser

    
app_name='userhome' 


@login_required
def userHome(request,user_id): 
    messages.success(request, "Welcome to Poultry Management System")
    if not CheckUser(request, user_id):
        return redirect('/')
    user_info = Poultry.objects.filter(user_id=user_id).order_by('-startDate')
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
            'temp': temp_data
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
