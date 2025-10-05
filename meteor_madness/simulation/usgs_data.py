"""
USGS Earthquake and Seismic Zone Data Integration
"""
import requests
from datetime import datetime, timedelta
import math


def fetch_recent_earthquakes(days=30, min_magnitude=4.5):
    """
    Fetch recent earthquake data from USGS API.
    
    Args:
        days: Number of days to look back
        min_magnitude: Minimum earthquake magnitude
    
    Returns:
        List of earthquake events
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        'format': 'geojson',
        'starttime': start_date.strftime('%Y-%m-%d'),
        'endtime': end_date.strftime('%Y-%m-%d'),
        'minmagnitude': min_magnitude,
        'orderby': 'time'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        earthquakes = []
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            coords = feature.get('geometry', {}).get('coordinates', [])
            
            earthquakes.append({
                'id': feature.get('id'),
                'magnitude': props.get('mag'),
                'place': props.get('place'),
                'time': datetime.fromtimestamp(props.get('time', 0) / 1000).isoformat(),
                'latitude': coords[1] if len(coords) > 1 else None,
                'longitude': coords[0] if len(coords) > 0 else None,
                'depth_km': coords[2] if len(coords) > 2 else None,
                'url': props.get('url'),
                'tsunami': props.get('tsunami', 0) == 1
            })
        
        return earthquakes
    
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}


def check_seismic_zone(latitude, longitude):
    """
    Check if location is in a known seismic zone.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
    
    Returns:
        Dictionary with seismic zone information
    """
    # Major tectonic plate boundaries (simplified)
    seismic_zones = [
        {'name': 'Pacific Ring of Fire', 'risk': 'Very High', 'bounds': {'lat': (-60, 60), 'lon': (120, -60)}},
        {'name': 'Alpide Belt', 'risk': 'High', 'bounds': {'lat': (10, 50), 'lon': (-10, 140)}},
        {'name': 'Mid-Atlantic Ridge', 'risk': 'Moderate', 'bounds': {'lat': (-60, 60), 'lon': (-40, -10)}},
    ]
    
    # Check if coordinates are in any major seismic zone
    in_zone = False
    zone_info = {'name': 'Low Risk Zone', 'risk': 'Low'}
    
    # Ring of Fire check (Pacific Ocean rim)
    if (latitude >= -60 and latitude <= 60):
        if (longitude >= 120 or longitude <= -60):
            in_zone = True
            zone_info = {'name': 'Pacific Ring of Fire', 'risk': 'Very High'}
    
    # Alpide Belt (Mediterranean to Indonesia)
    if (latitude >= 10 and latitude <= 50) and (longitude >= -10 and longitude <= 140):
        in_zone = True
        zone_info = {'name': 'Alpide Belt', 'risk': 'High'}
    
    return {
        'in_seismic_zone': in_zone,
        'zone_name': zone_info['name'],
        'seismic_risk': zone_info['risk']
    }


def check_tsunami_zone(latitude, longitude):
    """
    Check if location is in a tsunami-prone area.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
    
    Returns:
        Dictionary with tsunami zone information
    """
    # Major tsunami-prone regions
    tsunami_zones = {
        'Pacific Ocean': {'risk': 'Very High', 'reason': 'Ring of Fire activity'},
        'Indian Ocean': {'risk': 'High', 'reason': 'Subduction zones'},
        'Mediterranean Sea': {'risk': 'Moderate', 'reason': 'Tectonic activity'},
        'Atlantic Ocean': {'risk': 'Low', 'reason': 'Limited subduction zones'},
    }
    
    # Determine ocean/region based on coordinates
    if longitude >= 120 or longitude <= -60:
        zone = 'Pacific Ocean'
    elif longitude >= 40 and longitude <= 100 and latitude >= -40 and latitude <= 30:
        zone = 'Indian Ocean'
    elif longitude >= -10 and longitude <= 40 and latitude >= 30 and latitude <= 50:
        zone = 'Mediterranean Sea'
    else:
        zone = 'Atlantic Ocean'
    
    zone_data = tsunami_zones.get(zone, {'risk': 'Unknown', 'reason': 'Unknown region'})
    
    return {
        'ocean_region': zone,
        'tsunami_risk': zone_data['risk'],
        'reason': zone_data['reason']
    }


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def get_nearby_earthquakes(latitude, longitude, radius_km=500, earthquakes=None):
    """
    Find earthquakes near a given location.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        radius_km: Search radius in kilometers
        earthquakes: List of earthquakes (if None, fetches recent ones)
    
    Returns:
        List of nearby earthquakes
    """
    if earthquakes is None:
        earthquakes = fetch_recent_earthquakes()
    
    if isinstance(earthquakes, dict) and 'error' in earthquakes:
        return earthquakes
    
    nearby = []
    for eq in earthquakes:
        if eq['latitude'] and eq['longitude']:
            distance = calculate_distance(latitude, longitude, eq['latitude'], eq['longitude'])
            if distance <= radius_km:
                eq['distance_km'] = round(distance, 2)
                nearby.append(eq)
    
    # Sort by distance
    nearby.sort(key=lambda x: x['distance_km'])
    
    return nearby


def assess_impact_location(latitude, longitude):
    """
    Comprehensive assessment of impact location.
    
    Args:
        latitude: Impact latitude
        longitude: Impact longitude
    
    Returns:
        Complete location risk assessment
    """
    seismic_info = check_seismic_zone(latitude, longitude)
    tsunami_info = check_tsunami_zone(latitude, longitude)
    
    # Determine if it's an ocean impact
    is_ocean = is_ocean_location(latitude, longitude)
    
    return {
        'coordinates': {
            'latitude': latitude,
            'longitude': longitude
        },
        'is_ocean_impact': is_ocean,
        'seismic_zone': seismic_info,
        'tsunami_zone': tsunami_info,
        'overall_risk': calculate_overall_risk(seismic_info, tsunami_info, is_ocean)
    }


def is_ocean_location(latitude, longitude):
    """
    Simple check if coordinates are likely in ocean.
    This is a simplified version - in production, use proper ocean/land dataset.
    """
    # Major ocean regions (simplified)
    # Pacific Ocean
    if (longitude >= 120 or longitude <= -60) and abs(latitude) < 60:
        return True
    # Atlantic Ocean
    if (longitude >= -80 and longitude <= -10) and abs(latitude) < 60:
        return True
    # Indian Ocean
    if (longitude >= 40 and longitude <= 120) and (latitude >= -60 and latitude <= 30):
        return True
    
    return False


def calculate_overall_risk(seismic_info, tsunami_info, is_ocean):
    """Calculate overall risk level."""
    risk_scores = {
        'Very High': 4,
        'High': 3,
        'Moderate': 2,
        'Low': 1,
        'Unknown': 0
    }
    
    seismic_score = risk_scores.get(seismic_info['seismic_risk'], 0)
    tsunami_score = risk_scores.get(tsunami_info['tsunami_risk'], 0) if is_ocean else 0
    
    avg_score = (seismic_score + tsunami_score) / 2 if is_ocean else seismic_score
    
    if avg_score >= 3.5:
        return 'Very High'
    elif avg_score >= 2.5:
        return 'High'
    elif avg_score >= 1.5:
        return 'Moderate'
    else:
        return 'Low'
