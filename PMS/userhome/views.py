from django.shortcuts import render

# Create your views here.
def mainpage(request):
    print("i am here")
    return render(request, 'mainpage.html')
