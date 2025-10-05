"""
Meteor Impact Simulation Engine
Calculates impact energy, crater size, and damage estimates
"""
import math


def calculate_impact_energy(diameter_m, velocity_mps, density=3000):
    """
    Calculate impact energy in megatons of TNT.
    
    Args:
        diameter_m: Asteroid diameter in meters
        velocity_mps: Velocity in meters per second
        density: Density in kg/m³ (default: 3000 for rocky asteroids)
    
    Returns:
        Energy in megatons of TNT
    """
    radius = diameter_m / 2
    volume = (4/3) * math.pi * radius**3
    mass = volume * density  # kg
    energy_joules = 0.5 * mass * velocity_mps**2
    energy_megatons = energy_joules / 4.184e15  # 1 megaton TNT = 4.184e15 J
    return round(energy_megatons, 2)


def estimate_crater_size(energy_megatons):
    """
    Estimate crater diameter based on scaling laws.
    
    Args:
        energy_megatons: Impact energy in megatons
    
    Returns:
        Crater diameter in kilometers
    """
    # Simplified scaling law: D ≈ E^0.3 * 1.8
    return round((energy_megatons ** 0.3) * 1.8, 2)


def calculate_blast_radius(energy_megatons):
    """
    Calculate blast radius for different damage levels.
    
    Args:
        energy_megatons: Impact energy in megatons
    
    Returns:
        Dictionary with damage radii in kilometers
    """
    # Scaling based on nuclear blast data
    return {
        'total_destruction_km': round((energy_megatons ** 0.33) * 2.5, 2),
        'severe_damage_km': round((energy_megatons ** 0.33) * 5.0, 2),
        'moderate_damage_km': round((energy_megatons ** 0.33) * 10.0, 2),
        'light_damage_km': round((energy_megatons ** 0.33) * 20.0, 2),
    }


def estimate_casualties(energy_megatons, population_density=100):
    """
    Rough estimate of potential casualties.
    
    Args:
        energy_megatons: Impact energy in megatons
        population_density: People per square kilometer
    
    Returns:
        Estimated casualties
    """
    blast_radii = calculate_blast_radius(energy_megatons)
    severe_area = math.pi * (blast_radii['severe_damage_km'] ** 2)
    estimated_casualties = int(severe_area * population_density * 0.7)  # 70% casualty rate
    return estimated_casualties


def calculate_seismic_magnitude(energy_megatons):
    """
    Estimate Richter scale magnitude from impact energy.
    
    Args:
        energy_megatons: Impact energy in megatons
    
    Returns:
        Estimated Richter magnitude
    """
    # Conversion: log10(E) = 1.5M + 4.8 (E in joules)
    energy_joules = energy_megatons * 4.184e15
    magnitude = (math.log10(energy_joules) - 4.8) / 1.5
    return round(magnitude, 1)


def assess_tsunami_risk(energy_megatons, is_ocean_impact=False):
    """
    Assess tsunami generation potential.
    
    Args:
        energy_megatons: Impact energy in megatons
        is_ocean_impact: Whether impact is in ocean
    
    Returns:
        Dictionary with tsunami assessment
    """
    if not is_ocean_impact:
        return {
            'risk_level': 'None',
            'wave_height_m': 0,
            'affected_radius_km': 0
        }
    
    # Simplified tsunami model
    wave_height = round(math.sqrt(energy_megatons) * 5, 1)
    affected_radius = round(energy_megatons ** 0.4 * 100, 1)
    
    if energy_megatons < 1:
        risk = 'Low'
    elif energy_megatons < 100:
        risk = 'Moderate'
    elif energy_megatons < 1000:
        risk = 'High'
    else:
        risk = 'Catastrophic'
    
    return {
        'risk_level': risk,
        'wave_height_m': wave_height,
        'affected_radius_km': affected_radius
    }


def run_full_simulation(diameter_km, velocity_kmh, latitude, longitude, 
                       is_ocean=False, population_density=100):
    """
    Run complete impact simulation.
    
    Args:
        diameter_km: Asteroid diameter in kilometers
        velocity_kmh: Velocity in km/h
        latitude: Impact latitude
        longitude: Impact longitude
        is_ocean: Whether impact is in ocean
        population_density: Local population density
    
    Returns:
        Complete simulation results dictionary
    """
    # Convert units
    diameter_m = diameter_km * 1000
    velocity_mps = velocity_kmh / 3.6
    
    # Calculate impact parameters
    energy = calculate_impact_energy(diameter_m, velocity_mps)
    crater_size = estimate_crater_size(energy)
    blast_radii = calculate_blast_radius(energy)
    casualties = estimate_casualties(energy, population_density)
    magnitude = calculate_seismic_magnitude(energy)
    tsunami = assess_tsunami_risk(energy, is_ocean)
    
    # Determine impact severity
    if energy < 1:
        severity = 'Minor'
    elif energy < 100:
        severity = 'Moderate'
    elif energy < 1000:
        severity = 'Major'
    elif energy < 10000:
        severity = 'Severe'
    else:
        severity = 'Extinction Level Event'
    
    return {
        'impact_location': {
            'latitude': latitude,
            'longitude': longitude,
            'is_ocean_impact': is_ocean
        },
        'asteroid_parameters': {
            'diameter_km': diameter_km,
            'velocity_kmh': velocity_kmh,
            'velocity_mps': round(velocity_mps, 2)
        },
        'impact_energy': {
            'megatons': energy,
            'joules': energy * 4.184e15,
            'hiroshima_equivalent': round(energy / 0.015, 1)  # Hiroshima = ~15 kilotons
        },
        'crater': {
            'diameter_km': crater_size,
            'depth_km': round(crater_size / 5, 2)  # Typical depth is ~1/5 diameter
        },
        'blast_effects': blast_radii,
        'casualties': {
            'estimated': casualties,
            'population_density': population_density
        },
        'seismic_effects': {
            'magnitude': magnitude,
            'description': get_earthquake_description(magnitude)
        },
        'tsunami_risk': tsunami,
        'severity': severity
    }


def get_earthquake_description(magnitude):
    """Get description of earthquake magnitude."""
    if magnitude < 4.0:
        return 'Minor - Often felt, but rarely causes damage'
    elif magnitude < 5.0:
        return 'Light - Can cause damage to poorly constructed buildings'
    elif magnitude < 6.0:
        return 'Moderate - Can cause significant damage in populated areas'
    elif magnitude < 7.0:
        return 'Strong - Can cause serious damage over larger areas'
    elif magnitude < 8.0:
        return 'Major - Can cause serious damage over very large areas'
    else:
        return 'Great - Devastating effects over vast areas'
