from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404

app_name = 'userhome'
urlpatterns = [
   


    path('mainpage/<int:user_id>/profile/<str:poultryName>',views.profile,name='profile'),
    path('mainpage/<int:user_id>/', views.userHome, name='mainpage'),
    path('mainpage/<int:user_id>/submit_detail/', views.submit_detail, name='submit_detail'),
    path('mainpage/<int:user_id>/profile/submit_bill/<str:poultryName>', views.submit_bill, name='submit_bill'),
    path('mainpage/<int:user_id>/profile/bills/<str:poultryName>',views.showBills, name='showBills'),
    path('mainpage/<int:user_id>/profile/vaccine/<str:poultryName>',views.showVaccine, name='showVaccine'),
    path('mainpage/<int:user_id>/profile/deads/<str:poultryName>',views.showDeads, name='showDeads'),
    path('mark_notification_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('unread-notifications/', views.get_unread_notifications, name='get_unread_notifications'),
    path('mark_all_notifications_as_read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('mainpage/<int:user_id>/profile/medicine_info/<str:poultryName>', views.medicine_view, name='medicine_view'),
    path('get_medicine_info', views.search_medicine, name='get_medicine_info'),

    
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'userhome.views.notFound'