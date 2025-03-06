from django.contrib import admin
from .models import Poultry, BillPost, Total, DeadInfo, Mail, Notification, NotificationUser
from django.utils.html import format_html
# Define the PoultryAdmin class
class PoultryAdmin(admin.ModelAdmin):
    list_display = ['poultryName', 'totalChicken', 'totalDead', 'startDate']
    search_fields = ['poultryName', 'totalChicken']
    list_filter = ['totalChicken']
    list_per_page = 10
    list_display_links = ['poultryName']
    list_editable = ['totalChicken', 'totalDead']
    readonly_fields = ['startDate']


class TotalInline(admin.TabularInline):
    model = Total
    extra = 1
    fields = ['poultryName', 'totalDana', 'totalMedicine', 'totalVaccine', 'totalAmount', 'totalBhus']
    readonly_fields = ['totalDana', 'totalMedicine', 'totalVaccine', 'totalAmount', 'totalBhus']

class TotalAdmin(admin.ModelAdmin):
    list_display = ['poultryName', 'totalDana', 'totalMedicine', 'totalVaccine', 'totalAmount', 'totalBhus']
    search_fields = ['poultryName__poultryName']
    list_filter = ['poultryName']
    readonly_fields = ['totalDana', 'totalMedicine', 'totalVaccine', 'totalAmount', 'totalBhus']
    list_per_page = 10
    

class DeadInfoAdmin(admin.ModelAdmin):
    list_display = ['poultryName', 'totalDead', 'deadDate', 'totalDays']
    search_fields = ['poultryName__poultryName', 'totalDead']
    list_filter = ['poultryName', 'deadDate']
    readonly_fields = ['totalDays']
    list_per_page = 10
    

class BillPostAdmin(admin.ModelAdmin):
    list_display = ['poultryName', 'imgfile_preview', 'posted_date', 'totalChickenFeed', 'totalMedicine', 'totalVaccine', 'totalAmount', 'totalBhus', 'totalDays']
    search_fields = ['poultryName__poultryName', 'totalChickenFeed', 'totalMedicine', 'totalAmount']
    list_filter = ['poultryName', 'posted_date']
    readonly_fields = ['totalDays']
    list_per_page = 10

    def imgfile_preview(self, obj):
        if obj.imgfile:
            return format_html('<img src="{}" width="100" height="100" />', obj.imgfile.url)
        return "No image"
    imgfile_preview.short_description = 'Image Preview'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at')
    filter_horizontal = ('users',)  # Enable multi-user selection

admin.site.register(NotificationUser)

admin.site.register(Poultry, PoultryAdmin)
admin.site.register(BillPost, BillPostAdmin)
admin.site.register(Total, TotalAdmin)
admin.site.register(DeadInfo, DeadInfoAdmin)
admin.site.site_header = 'Poultry Management System'
admin.site.site_title = 'PMS'
admin.site.index_title = 'Welcome to PMS'
admin.site.register(Mail)

