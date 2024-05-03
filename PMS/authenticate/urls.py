from django.contrib import admin
from django.urls import path,include
from . import views
app_name='authenticate'
urlpatterns = [
    
    path('',views.index,name='index'),
    path('/signin', views.signin, name='signin'),
    path('userhome/', include('userhome.urls')),
]