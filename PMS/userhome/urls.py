from django.contrib import admin
from django.urls import path
from .import views

app_name = 'userhome'
urlpatterns = [
   

    # path('mainpage/<int:user_id>/contactUs',views.contactUs,name='contactus'),
    # path('mainpage/<int:user_id>/aboutUs',views.aboutUs,name='aboutus'),
   
    # path('mainpage/<int:user_id>/profile',views.profile,name='profile'),
    path('mainpage/<int:user_id>/', views.userHome, name='mainpage'),
    # path('mainpage/<int:user_id>/submit_quote/', views.submit_quote, name='submit_quote'),

    
]