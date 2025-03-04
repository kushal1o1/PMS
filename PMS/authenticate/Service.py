from django.contrib.auth.models import User
from django.contrib import messages
import os
from django.core.mail import EmailMultiAlternatives
from PMS import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import  urlsafe_base64_encode
from django.utils.encoding import force_bytes 
from . tokens import generate_token


def ValidateSignUpForm(request,username,email,pass1):
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return False
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return False
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return False
        
       
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return False   
        return True
    
    
def createUserObject(request,username,email,pass1):
        myuser = User.objects.create_user(username, email, pass1)
        # myuser.is_active = False
        myuser.is_active = False
        # myuser.save()
        print("User Created")
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")  
        return SendWelcomeEmail(request,myuser)
           

def ValidateSignInForm():
    pass

def SendWelcomeEmail(request,myuser):
        subject = "Welcome to PMS!!"
             
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        # test
        template_path = os.path.join(settings.BASE_DIR, "authenticate/templates/emails/WelcomeEmail.html")

        # Read HTML content
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        msg = EmailMultiAlternatives(subject, "", from_email, to_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send() 
        return SendConfirmEmail(request,myuser)  

def SendConfirmEmail(request,myuser):
    # Email Address Confirmation Email
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        template_path = os.path.join(settings.BASE_DIR, "authenticate/templates/emails/email_confirmation.html")
        current_site = get_current_site(request)
        email_subject = "Confirm your Email for - Quotes login!!"
        context ={ 
            'name': myuser.username,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        }
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Replace placeholders manually
        for key, value in context.items():
            html_content = html_content.replace(f"{{{{ {key} }}}}", value)  # Replace {{ name }} with actual value

        # Send the email
        msg = EmailMultiAlternatives(email_subject, "", from_email, to_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        msg.failed_silently = True
        return True

