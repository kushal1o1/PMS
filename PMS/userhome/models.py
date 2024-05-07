from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Poultry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poultryName=models.CharField(max_length=20)
    totalChicken=models.IntegerField()
    startDate=models.DateField(auto_now_add=True)
 
    def __str__(self):
        return self.poultryName


class BillPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poultryName = models.ForeignKey(Poultry, on_delete=models.CASCADE)
    imgfile = models.ImageField(upload_to='images/')
    posted_date = models.DateTimeField(auto_now_add=True)
    TotalChickenFeed=models.IntegerField()
    totalMedicine=models.IntegerField()
    totalBhus=models.IntegerField()
    totalAmount=models.IntegerField()
    totalVaccine=models.IntegerField()



    def __str__(self):
        return f"{self.user.username} - {self.posted_date}"