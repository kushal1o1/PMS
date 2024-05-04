from django.contrib import admin
from django.urls import path,include
from . import views
app_name='userhome'
urlpatterns = [
  
    path('/mainpage',views.mainpage,name='mainpage'),  # home page
    
    path('/addNewPoultry',views.addNewPoultry,name='addNewPoultry'),

    path('/landingPage',views.landingPage,name='landingPage'),  # home page


    # path('mainpage/<int:user_id>/submit_bill/', views.submit_bill, name='submit_bill'),
]
