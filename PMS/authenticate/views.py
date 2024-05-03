from django.shortcuts import render,redirect

# Create your views here.
def index(request):
    return render(request, 'index.html')

def signin(request):
    if request.method == 'POST':
        # username = request.POST['username']
        # pass1 = request.POST['password']
        # parms={
        #     username:username,
        #     password:pass1
        # }
        return redirect('userhome:mainpage')

    
    return render(request, "authenticate/index.html")

