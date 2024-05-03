from django.contrib import admin
from django.urls import path,include
from . import views
app_name='userhome'
urlpatterns = [
  
    path('/mainpage',views.mainpage,name='mainpage'),  # home page
]
