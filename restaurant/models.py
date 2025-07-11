from django.db import models

class Menu(models.Model):
    Title = models.CharField(max_length=255)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Inventory = models.IntegerField()

    def __str__(self):
        return f"{self.Title} : {str(self.Price)}"

class Booking(models.Model):
    Name = models.CharField(max_length=255)
    No_of_guests = models.IntegerField()
    reservation_date = models.DateTimeField()
    reservation_slot = models.SmallIntegerField(default=10)

    def __str__(self):
        return f"{self.Name} - {self.No_of_guests} guests on {self.reservation_date.strftime('%Y-%m-%d %H:%M')}"