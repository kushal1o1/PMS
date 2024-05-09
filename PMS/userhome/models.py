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


class Total(models.Model):
    poultryName = models.ForeignKey(Poultry, on_delete=models.CASCADE)
    totalDana = models.IntegerField(default=0)
    totalMedicine = models.IntegerField(default=0)
    totalVaccine = models.IntegerField(default=0)
    totalAmount = models.IntegerField(default=0)
    totalBhus = models.IntegerField(default=0)


    def calculate_totals(self, user):
        # Filter bills based on poultryName and user
        bills = BillPost.objects.filter(poultryName=self.poultryName, poultryName__user=user)
        self.totalDana = sum(bill.totalChickenFeed for bill in bills)
        self.totalMedicine = sum(bill.totalMedicine for bill in bills)
        self.totalVaccine = sum(bill.totalVaccine for bill in bills)
        self.totalAmount = sum(bill.totalAmount for bill in bills)
        self.totalBhus = sum(bill.totalBhus for bill in bills)


    def save(self, *args, **kwargs):
        self.calculate_totals(self.poultryName.user)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Totals for {self.poultryName}"
