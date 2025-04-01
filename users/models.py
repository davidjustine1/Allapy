from django.db import models

# Create your models here.
class Houseboat(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    amenities = models.TextField()
    image = models.ImageField(upload_to='houseboats/', null=True, blank=True)

    def __str__(self):
        return self.name
