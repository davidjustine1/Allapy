from django.db import models

# Create your models here.
class Houseboat(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    capacity = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    type = models.CharField(max_length=50)
    amenities = models.JSONField(default=dict)

    def __str__(self):
        return self.name
