from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Poultry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    poultryId=models.AutoField
    poultryName=models.CharField(max_length=20)
    totalChicken=models.IntegerField()
    startDate=models.DateField()
    def __str__(self):
        return self.poultryName

