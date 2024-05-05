from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Poultry
# # Create your views here.
# @login_required
# def userHome(request,user_id):
#     user_info = get_object_or_404(UserInfo, user_id=user_id)
#     # alluser_info=UserInfo.objects.all()
#     # videos = Video.objects.all().order_by('-posted_date')
#     # allquotes = Quote.objects.all().order_by('-posted_date')
#     # allimg = ImagePost.objects.all().order_by('-posted_date')


    
    
#     return render(request, 'userhome/userhome.html',{'user_info': user_info ,'videos': videos ,'quotes':allquotes,'imgquote':allimg})

@login_required
def userHome(request,user_id):
    print("here1")
    user_info = get_object_or_404(Poultry, user_id=user_id)
    print("ima here")
    # videos = Video.objects.all().order_by('-posted_date')
    # allquotes = Quote.objects.all().order_by('-posted_date')
    # allimg = ImagePost.objects.all().order_by('-posted_date')
    print(Poultry)

    
    
    return render(request, 'mainhome.html')

