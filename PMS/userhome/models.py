from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Poultry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poultryName = models.CharField(max_length=20, primary_key=True)
    totalChicken = models.IntegerField()
    totalDead = models.IntegerField(default=0)
    startDate = models.DateField(auto_now_add=True)

    @property
    def totalDays(self):
        return ((date.today() - self.startDate)).days+1

    @property
    def totalChickenNow(self):
        return ((self.totalChicken-self.totalDead))


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
    description = models.TextField(blank=True, null=True)


    @property
    def totalDays(self):
        return (self.posted_date.date() - self.poultryName.startDate).days+1

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

class DeadInfo(models.Model):
    poultryName = models.ForeignKey(Poultry, on_delete=models.CASCADE)
    totalDead = models.IntegerField(default=0)
    deadDate = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    @property
    def totalDays(self):
        return (self.deadDate - self.poultryName.startDate).days+1

    def __str__(self):
        return f"DEAD_INFO OF {self.poultryName}"


class Mail(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mail: {self.message}"
    
class Notification(models.Model):
    users = models.ManyToManyField(User,related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification: {self.message}"
    
