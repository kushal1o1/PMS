from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Poultry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poultryName=models.CharField(max_length=20,unique=True)
    totalChicken=models.IntegerField()
    startDate=models.DateField(auto_now_add=True)
 
    def __str__(self):
        return self.poultryName

