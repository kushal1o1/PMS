from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Poultry ,BillPost
from django.contrib.auth.models import User
# # Create your views here.
# @login_required
# def userHome(request,user_id):
#     user_info = get_object_or_404(UserInfo, user_id=user_id)
#     # alluser_info=UserInfo.objects.all()
#     # videos = Video.objects.all().order_by('-posted_date')
#     # allquotes = Quote.objects.all().order_by('-posted_date')
#     # allimg = ImagePost.objects.all().order_by('-posted_date')


    
app_name='userhome' 
#     return render(request, 'userhome/userhome.html',{'user_info': user_info ,'videos': videos ,'quotes':allquotes,'imgquote':allimg})
print(Poultry)
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
    Bill_info = BillPost.objects.filter(user_id=user_id).order_by('-posted_date')

    return render(request, 'profile.html',{'parm':poultry_info[0],
    'bill':Bill_info[0]})


@login_required
def submit_bill(request,user_id,poultryName):
    poultry_info = Poultry.objects.filter(user_id=user_id).filter(poultryName=poultryName)
    if request.method == 'POST':

        if 'billform' in request.POST:
            image_file = request.FILES.get('imageofbill')
            feed = request.POST.get('feed')
            medicine=request.POST.get('medicine')
            vaccine=request.POST.get('vaccine')
            TotalChickenFeed=request.POST.get('TotalChickenFeed')
            totalMedicine=request.POST.get('totalMedicine')
            total=request.POST.get('total')
            totalBhus=request.POST.get('totalBhus')
            if vaccine:
                totalvaccine=1
\
            new_image_post = BillPost(
            user=get_object_or_404(User, id=user_id),
            imgfile=image_file,
            poultryName=poultry_info[0],
            TotalChickenFeed=TotalChickenFeed,
            totalMedicine=totalMedicine,
            totalBhus=totalBhus,
            totalAmount=total,
            totalVaccine=totalvaccine
             )
            new_image_post.save()

    return redirect('userhome:profile', user_id=user_id,poultryName=poultryName)
@login_required
def showBills(request,user_id,poultryName):
     Bill_info = BillPost.objects.filter(user_id=user_id).order_by('-posted_date')
     return render(request, 'showbills.html',{
    'bills':Bill_info})
    

@login_required
def showVaccine(request,user_id,poultryName):
     Bill_info = BillPost.objects.filter(user_id=user_id).order_by('-posted_date')
     return render(request, 'showVaccine.html',{
    'bills':Bill_info})