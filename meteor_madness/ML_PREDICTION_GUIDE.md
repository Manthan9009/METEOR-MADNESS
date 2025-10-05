# Machine Learning Prediction Guide

## Overview

Meteor Madness now includes **Machine Learning models** to predict:
1. **Impact Location** - Where an asteroid might hit Earth
2. **Impact Date** - When an asteroid might impact

## Models

### 1. Impact Location Predictor

Uses **Random Forest Regression** to predict latitude and longitude based on:
- Asteroid velocity (km/h)
- Asteroid diameter (km)
- Orbital inclination (degrees)
- Orbital eccentricity (0-1)
- Miss distance (km)

**Features:**
- Predicts impact coordinates
- Provides confidence score (0-100%)
- Confidence levels: Very Low, Low, Moderate, High, Very High

### 2. Impact Date Predictor

Uses **Random Forest Regression** to predict days until impact based on:
- Asteroid size (meters)
- Velocity (km/h)
- Miss distance (km)
- Impact probability (%)

**Features:**
- Predicts days until impact
- Converts to years
- Provides predicted impact date
- Risk assessment: Low, Moderate, High, Critical

## API Endpoints

### 1. Predict Impact Location

**POST** `/api/ml/predict-location/`

```bash
curl -X POST http://127.0.0.1:8000/api/ml/predict-location/ \
  -H "Content-Type: application/json" \
  -d '{
    "velocity_kmh": 50000,
    "diameter_km": 1.0,
    "orbital_inclination": 15,
    "eccentricity": 0.6,
    "miss_distance_km": 500000
  }'
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "latitude": 12.3456,
    "longitude": -45.6789,
    "confidence": 67.5,
    "confidence_level": "High"
  },
  "input_parameters": {...}
}
```

### 2. Predict Impact Date

**POST** `/api/ml/predict-date/`

```bash
curl -X POST http://127.0.0.1:8000/api/ml/predict-date/ \
  -H "Content-Type: application/json" \
  -d '{
    "size_m": 500,
    "velocity_kmh": 60000,
    "miss_distance_km": 1000000,
    "impact_probability_pct": 0.5
  }'
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "days_until_impact": 365.5,
    "predicted_impact_date": "2026-10-04",
    "years": 1.0,
    "risk_level": "Moderate"
  },
  "input_parameters": {...}
}
```

### 3. Get ML Predictions for Asteroid

**GET** `/api/ml/asteroids/<neo_id>/predictions/`

```bash
curl "http://127.0.0.1:8000/api/ml/asteroids/3370286/predictions/"
```

**Response:**
```json
{
  "success": true,
  "asteroid": {
    "neo_id": "3370286",
    "name": "Asteroid Name",
    "is_potentially_hazardous": false
  },
  "ml_predictions": {
    "impact_location": {
      "latitude": 23.4567,
      "longitude": -67.8901,
      "confidence": 72.3,
      "confidence_level": "High"
    },
    "impact_timing": {
      "days_until_impact": 1825.0,
      "predicted_impact_date": "2030-10-04",
      "years": 5.0,
      "risk_level": "Low"
    }
  }
}
```

## Python Usage

### Example 1: Predict Location

```python
import requests

url = 'http://127.0.0.1:8000/api/ml/predict-location/'
data = {
    'velocity_kmh': 75000,
    'diameter_km': 2.5,
    'orbital_inclination': 30,
    'eccentricity': 0.7,
    'miss_distance_km': 200000
}

response = requests.post(url, json=data)
result = response.json()

if result['success']:
    pred = result['prediction']
    print(f"Predicted Impact: {pred['latitude']}°, {pred['longitude']}°")
    print(f"Confidence: {pred['confidence']}% ({pred['confidence_level']})")
```

### Example 2: Predict Date

```python
import requests

url = 'http://127.0.0.1:8000/api/ml/predict-date/'
data = {
    'size_m': 1000,
    'velocity_kmh': 80000,
    'miss_distance_km': 5000000,
    'impact_probability_pct': 1.5
}

response = requests.post(url, json=data)
result = response.json()

if result['success']:
    pred = result['prediction']
    print(f"Days until impact: {pred['days_until_impact']}")
    print(f"Predicted date: {pred['predicted_impact_date']}")
    print(f"Risk level: {pred['risk_level']}")
```

### Example 3: Get Predictions for Stored Asteroid

```python
import requests

neo_id = "3370286"
url = f'http://127.0.0.1:8000/api/ml/asteroids/{neo_id}/predictions/'

response = requests.get(url)
result = response.json()

if result['success']:
    location = result['ml_predictions']['impact_location']
    timing = result['ml_predictions']['impact_timing']
    
    print(f"Asteroid: {result['asteroid']['name']}")
    print(f"Predicted Location: {location['latitude']}°, {location['longitude']}°")
    print(f"Predicted Date: {timing['predicted_impact_date']}")
    print(f"Risk: {timing['risk_level']}")
```

## Model Details

### Training Data

The models are trained on **synthetic data** generated based on:
- Orbital mechanics principles
- Historical asteroid trajectories
- Impact probability distributions

**Note:** In production, these would be trained on real historical asteroid data from NASA/JPL.

### Model Architecture

- **Algorithm:** Random Forest Regressor
- **Estimators:** 100 trees
- **Features:** 5 for location, 4 for date
- **Training samples:** 1000 for location, 500 for date

### Confidence Calculation

Location prediction confidence is based on:
- **Velocity:** Moderate velocities (40,000-60,000 km/h) = higher confidence
- **Diameter:** Larger asteroids = higher confidence
- **Miss Distance:** Closer approaches = higher confidence

### Risk Assessment

Date prediction risk levels:
- **Critical:** < 1 year AND > 1% probability
- **High:** < 5 years AND > 0.5% probability
- **Moderate:** < 10 years AND > 0.1% probability
- **Low:** All others

## Limitations

1. **Synthetic Training Data:** Models are trained on simulated data, not real impact events
2. **Simplified Physics:** Doesn't account for atmospheric entry, fragmentation
3. **No Gravitational Perturbations:** Doesn't model planetary influences
4. **Static Predictions:** Doesn't update with new observations

## Future Improvements

- [ ] Train on real historical asteroid data
- [ ] Add uncertainty quantification
- [ ] Include atmospheric entry modeling
- [ ] Incorporate gravitational perturbations
- [ ] Real-time model updates with new observations
- [ ] Deep learning models for complex trajectories
- [ ] Ensemble methods combining multiple models

## Installation

Install required packages:

```bash
pip install scikit-learn==1.3.2 numpy==1.24.3
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

## Model Persistence

Models are automatically trained on first use and cached in memory. To save/load models:

```python
from simulation.ml_predictor import ImpactLocationPredictor

# Train and save
predictor = ImpactLocationPredictor()
predictor.train()
predictor.save_model('my_model.pkl')

# Load later
predictor = ImpactLocationPredictor()
predictor.load_model('my_model.pkl')
```

## Disclaimer

⚠️ **These predictions are for educational and simulation purposes only.**

They should NOT be used for:
- Real asteroid threat assessment
- Emergency planning
- Public safety decisions

For actual asteroid impact predictions, consult:
- NASA's Center for Near-Earth Object Studies (CNEOS)
- ESA's Space Situational Awareness Programme
- International Asteroid Warning Network (IAWN)

---

**Meteor Madness ML** - Predicting cosmic chaos with science! 🤖🌠
