from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Poultry ,BillPost,Total,DeadInfo
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.timezone import now
from django.http import  JsonResponse
from django.db import transaction
from decouple import config
from .service import getWeatherInfo,getContextOfPoultry,handleBillForm,handleDeadForm,CheckUser,createReport,UpdateTotal,getMedicineInfo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import  NotificationUser
from django.contrib.auth.decorators import login_required

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

                if 'Closeform' in request.POST:
                    TransportCost = int(request.POST.get('TransportCost', 0))
                    RatePerKg = float(request.POST.get('RatePerKg', 0))
                    TotalWeight = float(request.POST.get('TotalWeight', 0))
                    TotalAmount = RatePerKg*TotalWeight
                    description = request.POST.get('description')
                   
                    poultry.Closedstatus = 'True' 
                    poultry.closedDate = now()
                    total_obj, created = Total.objects.get_or_create(poultryName=poultry)   
                    total_obj.calculate_totals(poultry.user)
                    total_obj.save()
                    total_amount = total_obj.totalAmount     
                    Coststatus = 'Profit' if TotalAmount >= total_amount else 'Loss'
                    poultry.Status=Coststatus
                    poultry.TransportCost = TransportCost
                    poultry.RatePerKg = RatePerKg
                    poultry.TotalWeight = TotalWeight
                    poultry.TotalAmount = TotalAmount
                    poultry.description = description
                    poultry.save()
                    messages.success(request, "Farm Closed Successfully")
                    return redirect('userhome:profile', user_id=user_id,poultryName=poultryName)

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
    return createReport(request)


def medicine_view(request,user_id,poultryName):  
    # getMedicineInfo("Amoxicillin")  
    """View to render the medicine information page"""
    messages.success(request, "Welcome to the Medicine Information Page")
    messages.info(request, "Enter the name of the medicine to get detailed information")
    return render(request, 'medicine.html', {
        'user_id':user_id,
        'poultryName':poultryName
    })


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