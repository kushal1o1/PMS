from django.db import models
from django.contrib.auth.models import User

class Poultry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poultryName = models.CharField(max_length=20, primary_key=True)
    totalChicken = models.IntegerField()
    startDate = models.DateField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.poultryName} by {self.user}"

class BillPost(models.Model):
    poultryName = models.ForeignKey(Poultry, on_delete=models.CASCADE)  # Foreign key to Poultry
    imgfile = models.ImageField(upload_to='images/')
    posted_date = models.DateTimeField(auto_now_add=True)
    totalChickenFeed = models.IntegerField()
    totalMedicine = models.IntegerField()
    totalBhus = models.IntegerField()
    totalAmount = models.IntegerField()
    totalVaccine = models.IntegerField()

    def __str__(self):
        return f"{self.poultryName.poultryName} - {self.posted_date}"
