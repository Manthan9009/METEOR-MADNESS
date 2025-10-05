from django.db import models

# Create your models here.

class Asteroid(models.Model):
    """Model to store asteroid/meteor data from NASA API"""
    neo_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    absolute_magnitude = models.FloatField(null=True, blank=True)
    estimated_diameter_min_km = models.FloatField(null=True, blank=True)
    estimated_diameter_max_km = models.FloatField(null=True, blank=True)
    is_potentially_hazardous = models.BooleanField(default=False)
    close_approach_date = models.DateField(null=True, blank=True)
    close_approach_datetime = models.DateTimeField(null=True, blank=True)
    relative_velocity_kmh = models.FloatField(null=True, blank=True)
    miss_distance_km = models.FloatField(null=True, blank=True)
    orbiting_body = models.CharField(max_length=50, null=True, blank=True)
    
    # Keplerian Orbital Elements
    semi_major_axis_au = models.FloatField(null=True, blank=True, help_text="Semi-major axis in AU")
    eccentricity = models.FloatField(null=True, blank=True, help_text="Orbital eccentricity (0-1)")
    inclination_deg = models.FloatField(null=True, blank=True, help_text="Inclination in degrees")
    ascending_node_deg = models.FloatField(null=True, blank=True, help_text="Longitude of ascending node")
    periapsis_arg_deg = models.FloatField(null=True, blank=True, help_text="Argument of periapsis")
    mean_anomaly_deg = models.FloatField(null=True, blank=True, help_text="Mean anomaly at epoch")
    orbital_period_days = models.FloatField(null=True, blank=True, help_text="Orbital period in days")
    
    # Collision Impact Location (calculated if impact occurs)
    predicted_impact_latitude = models.FloatField(null=True, blank=True, help_text="Predicted impact latitude")
    predicted_impact_longitude = models.FloatField(null=True, blank=True, help_text="Predicted impact longitude")
    predicted_impact_location = models.CharField(max_length=255, null=True, blank=True, help_text="Human-readable impact location")
    impact_probability = models.FloatField(default=0.0, help_text="Probability of impact (0-1)")
    impact_energy_megatons = models.FloatField(null=True, blank=True, help_text="Estimated impact energy in megatons")
    crater_diameter_km = models.FloatField(null=True, blank=True, help_text="Estimated crater diameter in km")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-close_approach_date']
        verbose_name = 'Asteroid'
        verbose_name_plural = 'Asteroids'
    
    def __str__(self):
        return f"{self.name} ({self.neo_id})"
    
    def has_orbital_elements(self):
        """Check if orbital elements are available"""
        return all([
            self.semi_major_axis_au is not None,
            self.eccentricity is not None,
            self.inclination_deg is not None
        ])
    
    def get_keplerian_orbit(self):
        """
        Create KeplerianOrbit object from stored orbital elements.
        Returns None if orbital elements are not available.
        """
        if not self.has_orbital_elements():
            return None
        
        from .keplerian_orbit import KeplerianOrbit
        from datetime import datetime
        
        return KeplerianOrbit(
            a=self.semi_major_axis_au,
            e=self.eccentricity,
            i=self.inclination_deg,
            Omega=self.ascending_node_deg or 0,
            omega=self.periapsis_arg_deg or 0,
            M0=self.mean_anomaly_deg or 0,
            epoch=datetime.combine(self.close_approach_date, datetime.min.time()) if self.close_approach_date else datetime.now()
        )


class Earthquake(models.Model):
    """Model to store earthquake data from USGS API"""
    usgs_id = models.CharField(max_length=100, unique=True)
    magnitude = models.FloatField()
    place = models.CharField(max_length=255)
    time = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    depth_km = models.FloatField(null=True, blank=True)
    url = models.URLField(max_length=500, null=True, blank=True)
    tsunami = models.BooleanField(default=False)
    felt_reports = models.IntegerField(null=True, blank=True)
    significance = models.IntegerField(null=True, blank=True)
    alert_level = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-time']
        verbose_name = 'Earthquake'
        verbose_name_plural = 'Earthquakes'
    
    def __str__(self):
        return f"M{self.magnitude} - {self.place}"
    
    @property
    def tsunami_status(self):
        return "Yes" if self.tsunami else "No"
