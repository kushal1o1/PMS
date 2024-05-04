from django.db import models

# Create your models here.
class Poultry(models.Model):
    poultryId=models.AutoField
    poultryName=models.CharField(max_length=20)
    totalChicken=models.IntegerField()
    startDate=models.DateField()
    def __str__(self):
        return self.poultryName
