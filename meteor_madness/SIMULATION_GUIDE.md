# Meteor Madness Simulation Engine Guide

## Overview

The Meteor Madness simulation engine provides comprehensive asteroid impact modeling with:
- Impact energy calculations
- Crater size estimation
- Blast radius modeling
- Casualty estimates
- Seismic magnitude prediction
- Tsunami risk assessment
- USGS earthquake data integration

## Features

### 1. Simulation Engine (`simulation_engine.py`)

#### Core Functions:

**`calculate_impact_energy(diameter_m, velocity_mps, density=3000)`**
- Calculates kinetic energy of impact
- Returns energy in megatons of TNT
- Default density: 3000 kg/m³ (rocky asteroid)

**`estimate_crater_size(energy_megatons)`**
- Estimates crater diameter using scaling laws
- Returns diameter in kilometers

**`calculate_blast_radius(energy_megatons)`**
- Calculates damage zones
- Returns dict with 4 damage levels

**`run_full_simulation(...)`**
- Complete impact simulation
- Includes all effects and assessments

### 2. USGS Integration (`usgs_data.py`)

#### Functions:

**`fetch_recent_earthquakes(days=30, min_magnitude=4.5)`**
- Fetches real earthquake data from USGS API
- Returns list of recent earthquakes

**`assess_impact_location(latitude, longitude)`**
- Evaluates seismic and tsunami risks
- Identifies tectonic zones

**`check_seismic_zone(latitude, longitude)`**
- Determines if location is in active seismic zone
- Includes Ring of Fire, Alpide Belt, etc.

## Web Interface

### Interactive Simulator

Visit: `http://127.0.0.1:8000/simulator/`

**Features:**
- Real-time impact calculations
- Visual results display
- Adjustable parameters:
  - Asteroid diameter
  - Velocity
  - Impact coordinates
  - Population density

**Example Scenarios:**

1. **Small Urban Impact (New York City)**
   - Diameter: 0.1 km
   - Velocity: 50,000 km/h
   - Lat: 40.7128, Lon: -74.0060
   - Population: 10,000/km²

2. **Large Ocean Impact (Pacific)**
   - Diameter: 2.0 km
   - Velocity: 70,000 km/h
   - Lat: 0, Lon: -140
   - Population: 0/km²

3. **Extinction Event (Chicxulub-scale)**
   - Diameter: 10 km
   - Velocity: 72,000 km/h
   - Lat: 21.3, Lon: -89.5
   - Population: 100/km²

## API Usage

### Example 1: Quick Impact Calculation

```bash
curl "http://127.0.0.1:8000/api/impact-calc/?diameter_m=500&velocity_mps=25000"
```

Response:
```json
{
  "success": true,
  "impact_energy_megatons": 1234.56,
  "crater_diameter_km": 15.8
}
```

### Example 2: Full Simulation

```bash
curl -X POST http://127.0.0.1:8000/api/simulate/ \
  -H "Content-Type: application/json" \
  -d '{
    "diameter_km": 1.0,
    "velocity_kmh": 50000,
    "latitude": 35.6762,
    "longitude": 139.6503,
    "population_density": 15000
  }'
```

### Example 3: Fetch Earthquakes

```bash
curl "http://127.0.0.1:8000/api/earthquakes/?days=7&min_magnitude=5.0"
```

### Example 4: Assess Location Risk

```bash
curl "http://127.0.0.1:8000/api/assess-location/?latitude=35.6762&longitude=139.6503"
```

### Example 5: Asteroid Impact Potential

```bash
# First fetch asteroids, then:
curl "http://127.0.0.1:8000/api/asteroids/2000433/impact-potential/"
```

## Python Integration

```python
import requests

# Run simulation
def simulate_impact(diameter_km, velocity_kmh, lat, lon):
    url = 'http://127.0.0.1:8000/api/simulate/'
    data = {
        'diameter_km': diameter_km,
        'velocity_kmh': velocity_kmh,
        'latitude': lat,
        'longitude': lon,
        'population_density': 5000
    }
    
    response = requests.post(url, json=data)
    return response.json()

# Example usage
result = simulate_impact(0.5, 60000, 40.7128, -74.0060)
print(f"Impact Energy: {result['simulation']['impact_energy']['megatons']} MT")
print(f"Crater Size: {result['simulation']['crater']['diameter_km']} km")
print(f"Casualties: {result['simulation']['casualties']['estimated']:,}")
```

## Understanding Results

### Severity Levels

- **Minor**: < 1 MT (local damage)
- **Moderate**: 1-100 MT (city-scale)
- **Major**: 100-1,000 MT (regional)
- **Severe**: 1,000-10,000 MT (continental)
- **Extinction Level Event**: > 10,000 MT (global)

### Damage Zones

1. **Total Destruction**: Complete obliteration
2. **Severe Damage**: Buildings collapse, 90%+ casualties
3. **Moderate Damage**: Structural damage, 50% casualties
4. **Light Damage**: Windows broken, minor injuries

### Seismic Effects

The Richter scale magnitude is estimated from impact energy:
- < 4.0: Minor tremors
- 4.0-5.0: Light damage
- 5.0-6.0: Moderate damage
- 6.0-7.0: Strong earthquake
- 7.0-8.0: Major earthquake
- > 8.0: Great earthquake

### Tsunami Risk

For ocean impacts:
- **Low**: < 1 MT
- **Moderate**: 1-100 MT
- **High**: 100-1,000 MT
- **Catastrophic**: > 1,000 MT

## Real-World Comparisons

### Historical Events

1. **Tunguska (1908)**
   - Diameter: ~60 m
   - Energy: ~10-15 MT
   - Flattened 2,000 km² of forest

2. **Chelyabinsk (2013)**
   - Diameter: ~20 m
   - Energy: ~0.5 MT
   - Injured 1,500 people

3. **Chicxulub (66 million years ago)**
   - Diameter: ~10 km
   - Energy: ~100 million MT
   - Caused mass extinction

### Test Scenarios

```python
# Tunguska-like event
simulate_impact(0.06, 54000, 60.886, 101.894)

# Chelyabinsk-like event
simulate_impact(0.02, 66000, 54.8, 61.1)

# Hypothetical NYC impact
simulate_impact(0.5, 70000, 40.7128, -74.0060)
```

## Limitations

1. **Simplified Models**: Uses scaling laws, not full physics simulation
2. **Ocean Detection**: Basic coordinate-based detection
3. **Population**: Uniform density assumed
4. **Atmosphere**: Entry effects not modeled
5. **Angle**: Assumes vertical impact

## Advanced Usage

### Batch Simulations

```python
import requests
import pandas as pd

locations = [
    {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
    {'name': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503},
    {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
]

results = []
for loc in locations:
    sim = simulate_impact(1.0, 50000, loc['lat'], loc['lon'])
    results.append({
        'location': loc['name'],
        'energy_mt': sim['simulation']['impact_energy']['megatons'],
        'casualties': sim['simulation']['casualties']['estimated']
    })

df = pd.DataFrame(results)
print(df)
```

### Custom Analysis

```python
# Analyze asteroid database
import requests

# Get all asteroids
asteroids = requests.get('http://127.0.0.1:8000/api/asteroids/').json()

# Calculate impact potential for each
for asteroid in asteroids['data']['near_earth_objects'].values():
    for ast in asteroid:
        neo_id = ast['id']
        potential = requests.get(
            f'http://127.0.0.1:8000/api/asteroids/{neo_id}/impact-potential/'
        ).json()
        
        if potential['success']:
            print(f"{ast['name']}: {potential['impact_potential']['impact_energy_megatons']} MT")
```

## Support & Resources

- **API Documentation**: See `API_DOCUMENTATION.md`
- **NASA NeoWs**: https://api.nasa.gov/
- **USGS Earthquakes**: https://earthquake.usgs.gov/
- **Impact Calculator**: https://impact.ese.ic.ac.uk/ImpactEarth/

## Contributing

To add new features:
1. Extend `simulation_engine.py` for new calculations
2. Add API endpoints in `views.py`
3. Update URL routing in `urls.py`
4. Document in this guide

Enjoy simulating cosmic catastrophes! 🌠💥
