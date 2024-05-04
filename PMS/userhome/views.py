from django.shortcuts import render
from . models import Poultry
from django.contrib import messages
from django.shortcuts import render,redirect
# Create your views here.
def mainpage(request):
    print("i am here")
    return render(request, 'mainpage.html')

def landingPage(request):
    print("hi")
    return render(request,'landingpage.html')

def addNewPoultry(request):
     if request.method == "POST":
        FarmName = request.POST['FarmName']
        date = request.POST['date']
        TotalChicken=request.POST['TotalChicken']
       
        if Poultry.objects.filter(poultryName=FarmName):
            messages.error(request, "FarmName already exist! Please try some other username.")
            return redirect('/userhome')
        
    
        
        Pobj = Poultry.objects.create_user(FarmName, TotalChicken, date)
        # myuser.is_active = False
        Pobj.is_active = True
        Pobj.save()
        messages.success(request, "Your Poultry has been created succesfully!!")
        return render(request,'mainpage.html')