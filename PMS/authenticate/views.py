from django.shortcuts import  render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token
from  .Service import ValidateSignUpForm,createUserObject



def landingpage(request):
    return render(request,"index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['password']

        if not  ValidateSignUpForm(request,username,email,pass1):
            return redirect('/')
        
            
            
        if not createUserObject(request,username,email,pass1):
            messages.error(request, "Something went wrong!!")
            return redirect('/')
       
        return redirect('/')
        
        
    return render(request, "index.html")


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect("/")
    else:
        print("I am here")
        return render(request,'activation_failed.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['password']
        
        user = authenticate(username=username, password=pass1)
 
        if user is not None:
            login(request, user)
            

            params = {
            "username": user.username,
            "fname": user.first_name,
            "lname": user.last_name,
            "email": user.email,
            "id":user.id,
            
            }
            messages.success(request, "Logged In Sucessfully!!")

            return redirect('userhome:mainpage', user_id=user.id)

        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('/')
    
    return render(request, "index.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('/')

def notFound(request):
    return render(request,'pageNotFound.html')