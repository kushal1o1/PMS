from django.contrib import admin
from django.urls import include, path, re_path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('',views.landingpage,name='landingpage'),
    path('accounts/login/',views.landingpage,name='landingpage'),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signout', views.signout, name='signout'),
    path('userhome/', include('userhome.urls'),name='userhome'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    re_path(r'^.*$',views.notFound,name='notFound')
]