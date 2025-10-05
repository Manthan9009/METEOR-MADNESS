from django.contrib import admin
from .models import Asteroid, Earthquake

# Register your models here.

@admin.register(Asteroid)
class AsteroidAdmin(admin.ModelAdmin):
    list_display = ['name', 'neo_id', 'close_approach_date', 'is_potentially_hazardous', 'estimated_diameter_max_km']
    list_filter = ['is_potentially_hazardous', 'close_approach_date', 'orbiting_body']
    search_fields = ['name', 'neo_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-close_approach_date']


@admin.register(Earthquake)
class EarthquakeAdmin(admin.ModelAdmin):
    list_display = ['magnitude', 'place', 'time', 'tsunami', 'depth_km', 'alert_level']
    list_filter = ['tsunami', 'alert_level', 'time']
    search_fields = ['place', 'usgs_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-time']
