from django.contrib import admin
from django.urls import path
from . import views

app_name = 'userhome'
urlpatterns = [
   

    # path('mainpage/<int:user_id>/contactUs',views.contactUs,name='contactus'),
    # path('mainpage/<int:user_id>/aboutUs',views.aboutUs,name='aboutus'),

    path('mainpage/<int:user_id>/profile/<str:poultryName>',views.profile,name='profile'),
    path('mainpage/<int:user_id>/', views.userHome, name='mainpage'),
    path('mainpage/<int:user_id>/submit_detail/', views.submit_detail, name='submit_detail'),
    path('mainpage/<int:user_id>/profile/submit_bill/<str:poultryName>', views.submit_bill, name='submit_bill'),
    path('mainpage/<int:user_id>/profile/bills/<str:poultryName>',views.showBills, name='showBills'),
    path('mainpage/<int:user_id>/profile/vaccine/<str:poultryName>',views.showVaccine, name='showVaccine'),
    
]