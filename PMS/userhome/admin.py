from django.contrib import admin

# Register your models here.
from . models import Poultry,BillPost
admin.site.register(Poultry)
admin.site.register(BillPost)
