# Meteor Madness API Documentation

## Base URL
```
http://127.0.0.1:8000/api/
```

## API Endpoints

### 1. Fetch Asteroid Data from NASA
**GET** `/api/asteroids/`

Fetches Near-Earth Object data from NASA's NeoWs API.

**Query Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format (default: today)
- `end_date` (optional): End date in YYYY-MM-DD format (default: start_date + 7 days)

**Example:**
```bash
curl "http://127.0.0.1:8000/api/asteroids/?start_date=2025-10-01&end_date=2025-10-05"
```

**Response:**
```json
{
  "success": true,
  "data": { ... },
  "count": 42
}
```

---

### 2. Simulate Asteroid Impact
**POST** `/api/simulate/`

Runs a complete impact simulation with damage assessment.

**Request Body:**
```json
{
  "diameter_km": 1.0,
  "velocity_kmh": 50000,
  "latitude": 40.7128,
  "longitude": -74.0060,
  "population_density": 10000
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/simulate/ \
  -H "Content-Type: application/json" \
  -d '{
    "diameter_km": 0.5,
    "velocity_kmh": 60000,
    "latitude": 35.6762,
    "longitude": 139.6503,
    "population_density": 15000
  }'
```

**Response:**
```json
{
  "success": true,
  "simulation": {
    "impact_location": {
      "latitude": 35.6762,
      "longitude": 139.6503,
      "is_ocean_impact": false
    },
    "asteroid_parameters": {
      "diameter_km": 0.5,
      "velocity_kmh": 60000,
      "velocity_mps": 16666.67
    },
    "impact_energy": {
      "megatons": 245.67,
      "joules": 1.027e+18,
      "hiroshima_equivalent": 16378.0
    },
    "crater": {
      "diameter_km": 8.45,
      "depth_km": 1.69
    },
    "blast_effects": {
      "total_destruction_km": 15.75,
      "severe_damage_km": 31.5,
      "moderate_damage_km": 63.0,
      "light_damage_km": 126.0
    },
    "casualties": {
      "estimated": 65432,
      "population_density": 15000
    },
    "seismic_effects": {
      "magnitude": 6.8,
      "description": "Strong - Can cause serious damage over larger areas"
    },
    "tsunami_risk": {
      "risk_level": "None",
      "wave_height_m": 0,
      "affected_radius_km": 0
    },
    "severity": "Major",
    "location_assessment": {
      "coordinates": {...},
      "is_ocean_impact": false,
      "seismic_zone": {...},
      "tsunami_zone": {...}
    }
  }
}
```

---

### 3. Quick Impact Calculation
**GET** `/api/impact-calc/`

Quick calculation of impact energy and crater size.

**Query Parameters:**
- `diameter_m`: Asteroid diameter in meters (default: 100)
- `velocity_mps`: Velocity in meters per second (default: 20000)

**Example:**
```bash
curl "http://127.0.0.1:8000/api/impact-calc/?diameter_m=500&velocity_mps=25000"
```

**Response:**
```json
{
  "success": true,
  "diameter_m": 500,
  "velocity_mps": 25000,
  "impact_energy_megatons": 1234.56,
  "crater_diameter_km": 15.8
}
```

---

### 4. Fetch Recent Earthquakes (USGS)
**GET** `/api/earthquakes/`

Fetches recent earthquake data from USGS.

**Query Parameters:**
- `days` (optional): Number of days to look back (default: 30)
- `min_magnitude` (optional): Minimum magnitude (default: 4.5)

**Example:**
```bash
curl "http://127.0.0.1:8000/api/earthquakes/?days=7&min_magnitude=5.0"
```

**Response:**
```json
{
  "success": true,
  "count": 15,
  "earthquakes": [
    {
      "id": "us7000abcd",
      "magnitude": 6.2,
      "place": "123 km NE of Tokyo, Japan",
      "time": "2025-10-03T14:23:45",
      "latitude": 36.5,
      "longitude": 140.8,
      "depth_km": 35.2,
      "url": "https://earthquake.usgs.gov/...",
      "tsunami": false
    }
  ]
}
```

---

### 5. Assess Impact Location
**GET** `/api/assess-location/`

Assesses seismic and tsunami risks for a location.

**Query Parameters:**
- `latitude`: Location latitude (required)
- `longitude`: Location longitude (required)

**Example:**
```bash
curl "http://127.0.0.1:8000/api/assess-location/?latitude=35.6762&longitude=139.6503"
```

**Response:**
```json
{
  "success": true,
  "assessment": {
    "coordinates": {
      "latitude": 35.6762,
      "longitude": 139.6503
    },
    "is_ocean_impact": false,
    "seismic_zone": {
      "in_seismic_zone": true,
      "zone_name": "Pacific Ring of Fire",
      "seismic_risk": "Very High"
    },
    "tsunami_zone": {
      "ocean_region": "Pacific Ocean",
      "tsunami_risk": "Very High",
      "reason": "Ring of Fire activity"
    },
    "overall_risk": "Very High",
    "nearby_earthquakes": {
      "count": 3,
      "earthquakes": [...]
    }
  }
}
```

---

### 6. Asteroid Impact Potential
**GET** `/api/asteroids/<neo_id>/impact-potential/`

Calculates impact potential for a specific asteroid in the database.

**Example:**
```bash
curl "http://127.0.0.1:8000/api/asteroids/2000433/impact-potential/"
```

**Response:**
```json
{
  "success": true,
  "asteroid": {
    "neo_id": "2000433",
    "name": "433 Eros (A898 PA)",
    "is_potentially_hazardous": false,
    "close_approach_date": "2025-10-15",
    "miss_distance_km": 28500000
  },
  "impact_potential": {
    "diameter_km": 16.84,
    "velocity_kmh": 25000,
    "impact_energy_megatons": 4500000000,
    "crater_diameter_km": 2500,
    "hiroshima_equivalent": 300000000000
  }
}
```

---

## Error Responses

All endpoints return error responses in this format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error

---

## Usage Examples

### Python
```python
import requests

# Simulate impact
response = requests.post('http://127.0.0.1:8000/api/simulate/', json={
    'diameter_km': 1.0,
    'velocity_kmh': 50000,
    'latitude': 40.7128,
    'longitude': -74.0060,
    'population_density': 10000
})

data = response.json()
print(f"Impact Energy: {data['simulation']['impact_energy']['megatons']} MT")
```

### JavaScript
```javascript
// Fetch earthquakes
fetch('http://127.0.0.1:8000/api/earthquakes/?days=7')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} earthquakes`);
    data.earthquakes.forEach(eq => {
      console.log(`${eq.magnitude} - ${eq.place}`);
    });
  });
```

### cURL
```bash
# Quick impact calculation
curl "http://127.0.0.1:8000/api/impact-calc/?diameter_m=1000&velocity_mps=30000"
```

---

## Simulation Engine Details

### Impact Energy Formula
```
E = 0.5 × m × v²
```
Where:
- m = mass (volume × density)
- v = velocity
- Energy converted to megatons of TNT (1 MT = 4.184×10¹⁵ J)

### Crater Size Estimation
```
D ≈ E^0.3 × 1.8
```
Simplified scaling law based on impact energy.

### Seismic Magnitude
```
M = (log₁₀(E) - 4.8) / 1.5
```
Richter scale estimation from impact energy.

---

## Rate Limits

Currently no rate limits are enforced. For production use, implement rate limiting.

## Support

For issues or questions, refer to the project README.md
