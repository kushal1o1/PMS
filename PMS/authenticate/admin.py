from django.contrib import admin

# Register your models here.
class UserAdmin (admin.ModelAdmin):
    list_display = ['id','username','email','password','role','created_at','updated_at']
    search_fields = ['username','email','role']
    list_filter = ['role']
    list_per_page = 10
    list_display_links = ['id','username']
    list_editable = ['email','role']
    readonly_fields = ['created_at','updated_at']
    