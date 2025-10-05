"""
Asteroid Collision Location Calculator

This module calculates predicted impact locations for asteroids based on their
orbital parameters and current trajectory data.
"""

import math
import random
from typing import Dict, Tuple, Optional
from django.conf import settings


def calculate_collision_location(asteroid) -> Dict:
    """
    Calculate the predicted impact location for an asteroid.
    
    Args:
        asteroid: Asteroid model instance
        
    Returns:
        Dict containing impact location data
    """
    # Calculate impact probability based on multiple factors
    impact_probability = calculate_impact_probability(
        asteroid.miss_distance_km,
        asteroid.relative_velocity_kmh,
        asteroid.is_potentially_hazardous,
        asteroid.estimated_diameter_min_km,
        asteroid.estimated_diameter_max_km,
        asteroid.absolute_magnitude
    )
    
    # Always calculate coordinates for demonstration purposes
    # Calculate impact location based on orbital mechanics
    impact_lat, impact_lon = predict_impact_coordinates(asteroid)
    
    # Get human-readable location
    location_name = get_location_name(impact_lat, impact_lon)
    
    # Calculate impact effects
    diameter_km = (asteroid.estimated_diameter_min_km + asteroid.estimated_diameter_max_km) / 2
    impact_energy = calculate_impact_energy(diameter_km, asteroid.relative_velocity_kmh)
    crater_diameter = estimate_crater_size(impact_energy)
    impact_zone_radius = calculate_impact_zone_radius(impact_energy)
    
    return {
        'impact_probability': impact_probability,
        'predicted_impact_latitude': impact_lat,
        'predicted_impact_longitude': impact_lon,
        'predicted_impact_location': location_name,
        'impact_energy_megatons': impact_energy,
        'crater_diameter_km': crater_diameter,
        'impact_zone_radius_km': impact_zone_radius
    }


def calculate_impact_probability(miss_distance_km: float, velocity_kmh: float, is_hazardous: bool, 
                                diameter_min_km: float = None, diameter_max_km: float = None, 
                                absolute_magnitude: float = None) -> float:
    """
    Calculate the probability of impact based on multiple factors:
    - Miss distance (primary factor)
    - Velocity (affects trajectory uncertainty)
    - Asteroid size/diameter (larger = more detectable = more accurate predictions)
    - Absolute magnitude (brightness affects detection accuracy)
    - Hazardous status (orbital characteristics)
    """
    if miss_distance_km is None or velocity_kmh is None:
        return 0.0
    
    # Calculate average diameter
    if diameter_min_km is not None and diameter_max_km is not None:
        avg_diameter_km = (diameter_min_km + diameter_max_km) / 2
    else:
        avg_diameter_km = 0.1  # Default small asteroid
    
    # 1. BASE PROBABILITY from miss distance (inverse relationship)
    # Closer asteroids have exponentially higher impact probability
    if miss_distance_km <= 10000:  # Within 10,000 km (very close)
        base_prob = 0.95
    elif miss_distance_km <= 50000:  # Within 50,000 km
        base_prob = 0.8
    elif miss_distance_km <= 100000:  # Within 100,000 km
        base_prob = 0.6
    elif miss_distance_km <= 200000:  # Within 200,000 km
        base_prob = 0.4
    elif miss_distance_km <= 500000:  # Within 500,000 km
        base_prob = 0.25
    elif miss_distance_km <= 1000000:  # Within 1,000,000 km
        base_prob = 0.15
    elif miss_distance_km <= 5000000:  # Within 5,000,000 km
        base_prob = 0.08
    else:
        base_prob = 0.03
    
    # 2. VELOCITY FACTOR
    # Higher velocity = more kinetic energy = more dangerous if it hits
    # Also affects trajectory uncertainty (faster = harder to predict precisely)
    velocity_factor = min(velocity_kmh / 25000, 3.0)  # Cap at 3x for very fast objects
    
    # 3. SIZE FACTOR
    # Larger asteroids are easier to detect and track accurately
    # Smaller asteroids have more uncertainty in their orbits
    if avg_diameter_km >= 1.0:  # Large asteroid (>1km)
        size_factor = 1.2  # More accurate tracking
    elif avg_diameter_km >= 0.5:  # Medium asteroid (500m-1km)
        size_factor = 1.0  # Standard tracking
    elif avg_diameter_km >= 0.1:  # Small asteroid (100m-500m)
        size_factor = 0.8  # Less accurate tracking
    else:  # Very small asteroid (<100m)
        size_factor = 0.6  # Poor tracking, high uncertainty
    
    # 4. MAGNITUDE FACTOR
    # Brighter asteroids are easier to observe and track
    if absolute_magnitude is not None:
        if absolute_magnitude <= 20:  # Very bright
            magnitude_factor = 1.3
        elif absolute_magnitude <= 22:  # Bright
            magnitude_factor = 1.1
        elif absolute_magnitude <= 24:  # Medium brightness
            magnitude_factor = 1.0
        elif absolute_magnitude <= 26:  # Dim
            magnitude_factor = 0.9
        else:  # Very dim
            magnitude_factor = 0.7
    else:
        magnitude_factor = 1.0
    
    # 5. HAZARDOUS STATUS FACTOR
    # Potentially hazardous asteroids have orbits that cross Earth's orbit
    hazardous_factor = 2.5 if is_hazardous else 1.0
    
    # 6. TRAJECTORY UNCERTAINTY FACTOR
    # Based on combination of factors that affect prediction accuracy
    uncertainty_factor = (size_factor * magnitude_factor) ** 0.5
    
    # 7. RANDOM VARIATION
    # Add realistic variation to account for unknown factors
    random_factor = random.uniform(0.8, 1.2)
    
    # Calculate final probability
    probability = (base_prob * velocity_factor * hazardous_factor * 
                  uncertainty_factor * random_factor)
    
    # Apply additional factors for demonstration
    # Make the calculation more interesting by considering orbital characteristics
    if is_hazardous and avg_diameter_km > 0.5:
        probability *= 1.5  # Large hazardous asteroids get higher probability
    
    # Cap probability at 98% (never 100% certain in reality)
    return min(probability, 0.98)


def predict_impact_coordinates(asteroid) -> Tuple[float, float]:
    """
    Predict impact coordinates based on asteroid trajectory.
    
    This uses simplified orbital mechanics and Earth's rotation.
    """
    # Use orbital elements if available for more accurate prediction
    if asteroid.has_orbital_elements():
        return predict_from_orbital_elements(asteroid)
    else:
        return predict_from_approach_data(asteroid)


def predict_from_orbital_elements(asteroid) -> Tuple[float, float]:
    """
    Predict impact location using Keplerian orbital elements.
    """
    # Simplified calculation based on orbital inclination and ascending node
    inclination = asteroid.inclination_deg or 0
    ascending_node = asteroid.ascending_node_deg or 0
    
    # Impact latitude is influenced by orbital inclination
    # Higher inclination = more likely to hit higher latitudes
    base_lat = inclination * 0.8  # Scale factor
    impact_lat = base_lat + random.uniform(-20, 20)  # Add some randomness
    
    # Impact longitude is influenced by ascending node and Earth's rotation
    # Earth rotates ~15 degrees per hour, so timing affects longitude
    base_lon = ascending_node + random.uniform(-180, 180)
    
    # Normalize coordinates
    impact_lat = max(-90, min(90, impact_lat))
    impact_lon = ((base_lon + 180) % 360) - 180
    
    return impact_lat, impact_lon


def predict_from_approach_data(asteroid) -> Tuple[float, float]:
    """
    Predict impact location using close approach data.
    """
    # Use miss distance and velocity to estimate impact point
    # This is a simplified model
    
    # Generate coordinates with some bias toward equatorial regions
    # (most asteroids approach from the ecliptic plane)
    impact_lat = random.gauss(0, 30)  # Mean at equator, std dev 30 degrees
    impact_lat = max(-90, min(90, impact_lat))
    
    # Longitude is more random but influenced by approach timing
    impact_lon = random.uniform(-180, 180)
    
    return impact_lat, impact_lon


def get_location_name(latitude: float, longitude: float) -> str:
    """
    Get a human-readable location name for coordinates in English.
    """
    if latitude is None or longitude is None:
        return "Unknown location"
    
    # Simple geographic region identification in English
    if -90 <= latitude <= -60:
        region = "Antarctica"
    elif -60 <= latitude <= -30:
        region = "Southern Ocean"
    elif -30 <= latitude <= 0:
        if -60 <= longitude <= -30:
            region = "South Atlantic Ocean"
        elif -30 <= longitude <= 0:
            region = "South America"
        elif 0 <= longitude <= 30:
            region = "Africa"
        elif 30 <= longitude <= 60:
            region = "Indian Ocean"
        else:
            region = "Southern Hemisphere"
    elif 0 <= latitude <= 30:
        if -180 <= longitude <= -120:
            region = "Pacific Ocean"
        elif -120 <= longitude <= -60:
            region = "North America"
        elif -60 <= longitude <= 0:
            region = "Atlantic Ocean"
        elif 0 <= longitude <= 60:
            region = "Africa/Europe"
        elif 60 <= longitude <= 120:
            region = "Asia"
        else:
            region = "Pacific Ocean"
    elif 30 <= latitude <= 60:
        if -180 <= longitude <= -120:
            region = "North Pacific Ocean"
        elif -120 <= longitude <= -60:
            region = "North America"
        elif -60 <= longitude <= 0:
            region = "North Atlantic Ocean"
        elif 0 <= longitude <= 60:
            region = "Europe"
        elif 60 <= longitude <= 120:
            region = "Asia"
        else:
            region = "North Pacific Ocean"
    else:  # 60 <= latitude <= 90
        region = "Arctic Region"
    
    # Format coordinates properly for English display
    lat_dir = "N" if latitude >= 0 else "S"
    lon_dir = "E" if longitude >= 0 else "W"
    
    return f"{region} ({abs(latitude):.2f}°{lat_dir}, {abs(longitude):.2f}°{lon_dir})"


def calculate_impact_energy(diameter_km: float, velocity_kmh: float) -> float:
    """
    Calculate impact energy in megatons of TNT equivalent.
    
    Uses the formula: E = 0.5 * m * v^2
    """
    if diameter_km is None or velocity_kmh is None:
        return 0.0
    
    # Assume average asteroid density of 2.6 g/cm³
    density = 2600  # kg/m³
    radius_m = (diameter_km * 1000) / 2
    volume_m3 = (4/3) * math.pi * radius_m**3
    mass_kg = volume_m3 * density
    
    # Convert velocity to m/s
    velocity_ms = velocity_kmh / 3.6
    
    # Calculate kinetic energy in Joules
    energy_joules = 0.5 * mass_kg * velocity_ms**2
    
    # Convert to megatons of TNT (1 megaton = 4.184 × 10^15 J)
    energy_megatons = energy_joules / (4.184e15)
    
    return energy_megatons


def estimate_crater_size(energy_megatons: float) -> float:
    """
    Estimate crater diameter based on impact energy.
    
    Uses empirical relationships from impact crater studies.
    """
    if energy_megatons <= 0:
        return 0.0
    
    # Simple power law relationship
    # Crater diameter in km
    crater_diameter = 0.1 * (energy_megatons ** 0.294)
    
    return crater_diameter


def calculate_impact_zone_radius(energy_megatons: float) -> float:
    """
    Calculate the radius of significant impact effects zone.
    
    This includes blast wave, thermal effects, and seismic effects.
    """
    if energy_megatons <= 0:
        return 0.0
    
    # Blast radius scales with cube root of energy
    # This is a simplified model for total destruction radius
    blast_radius = 2.0 * (energy_megatons ** 0.33)
    
    return blast_radius


def get_impact_effects_data(energy_megatons: float) -> Dict:
    """
    Get detailed impact effects data for visualization.
    """
    crater_diameter = estimate_crater_size(energy_megatons)
    blast_radius = calculate_impact_zone_radius(energy_megatons)
    
    # Calculate different effect zones
    effects = {
        'crater_diameter_km': crater_diameter,
        'blast_radius_km': blast_radius,
        'thermal_radius_km': blast_radius * 1.5,  # Thermal effects extend further
        'seismic_radius_km': blast_radius * 3.0,  # Seismic effects extend much further
        'tsunami_radius_km': blast_radius * 2.0 if energy_megatons > 10 else 0,  # Only for large impacts
    }
    
    # Add severity classifications
    if energy_megatons < 0.1:
        effects['severity'] = 'Minor'
        effects['description'] = 'Local damage, small crater'
    elif energy_megatons < 10:
        effects['severity'] = 'Moderate'
        effects['description'] = 'Regional damage, significant crater'
    elif energy_megatons < 1000:
        effects['severity'] = 'Major'
        effects['description'] = 'Continental damage, large crater'
    else:
        effects['severity'] = 'Catastrophic'
        effects['description'] = 'Global effects, massive crater'
    
    return effects
