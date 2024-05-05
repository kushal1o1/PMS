from django.contrib import admin
from django.urls import include, path
from .import views

urlpatterns = [

    path('',views.landingpage,name='landingpage'),
    path('accounts/login/',views.landingpage,name='landingpage'),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signout', views.signout, name='signout'),
    path('userhome/', include('userhome.urls'),name='userhome'),
    
    


]