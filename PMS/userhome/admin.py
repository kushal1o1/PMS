from django.contrib import admin

# Register your models here.
from . models import Poultry,BillPost,Total,DeadInfo
admin.site.register(Poultry)
admin.site.register(BillPost)
admin.site.register(Total)
admin.site.register(DeadInfo)





