from django.contrib import admin
from .models import Houseboat

class HouseboatAdmin(admin.ModelAdmin):
    # Fields that are absolutely required
    fields = [
        'name', 
        'price_per_night',
        'rating',
        'description',
        'capacity',
        'bedrooms',
        'type',
        'amenities'
    ]
    
    # Mark only essential fields as required
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].required = True
        form.base_fields['price_per_night'].required = True
        form.base_fields['type'].required = True
        # Make other fields optional
        form.base_fields['rating'].required = False
        form.base_fields['description'].required = False
        form.base_fields['capacity'].required = False
        form.base_fields['bedrooms'].required = False
        form.base_fields['amenities'].required = False
        return form

admin.site.register(Houseboat, HouseboatAdmin)
