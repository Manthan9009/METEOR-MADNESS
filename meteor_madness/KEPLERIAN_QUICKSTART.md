# Keplerian Orbital Mechanics - Quick Start Guide

## What's New?

Your Meteor Madness simulator now includes **real-time impact prediction** using Keplerian orbital mechanics! This allows you to:

✅ Calculate asteroid trajectories using orbital elements  
✅ Predict closest approaches to Earth  
✅ Estimate impact probabilities over multiple time horizons  
✅ Understand model limitations and confidence levels  

## Getting Started

### 1. Run Database Migration

First, apply the new database schema:

```bash
cd meteor_madness
python manage.py migrate simulation
```

### 2. Access the Simulator

Navigate to: **http://localhost:8000/simulator/**

### 3. Switch to Keplerian Mode

Click the **"Keplerian Orbital"** tab to access the new features.

## Understanding Orbital Elements

### Required Inputs

| Element | Symbol | Description | Typical Range |
|---------|--------|-------------|---------------|
| **Semi-major Axis** | a | Orbital size | 1.0 - 5.0 AU |
| **Eccentricity** | e | Orbital shape | 0.0 - 0.9 |
| **Inclination** | i | Orbital tilt | 0° - 180° |
| **Ascending Node** | Ω | Orbital orientation | 0° - 360° |
| **Argument of Periapsis** | ω | Perihelion location | 0° - 360° |
| **Mean Anomaly** | M₀ | Starting position | 0° - 360° |

### Quick Examples

**Near-Earth Asteroid (Potentially Hazardous):**
- Semi-major Axis: 1.5 AU
- Eccentricity: 0.4
- Inclination: 15°
- Duration: 365 days

**Main Belt Asteroid (Low Risk):**
- Semi-major Axis: 2.7 AU
- Eccentricity: 0.15
- Inclination: 10°
- Duration: 365 days

**Earth-Crossing Asteroid (High Risk):**
- Semi-major Axis: 1.2 AU
- Eccentricity: 0.6
- Inclination: 5°
- Duration: 180 days

## Interpreting Results

### Risk Levels

| Risk Level | Distance from Earth | What It Means |
|------------|---------------------|---------------|
| **EXTREME** | < 10 Earth Radii | Imminent impact threat |
| **High** | 10-50 Earth Radii | Close approach, monitoring required |
| **Moderate** | 50-100 Earth Radii | Notable approach |
| **Low** | > 100 Earth Radii | Safe distance |

*Note: 1 Earth Radius = 6,371 km*

### Orbital Characteristics

The results show:
- **Orbital Period**: Time to complete one orbit around the Sun
- **Perihelion**: Closest distance to Sun
- **Aphelion**: Farthest distance from Sun
- **Orbit Type**: Classification (Near-Earth, Main Belt, etc.)

### Closest Approach Predictions

Multiple time horizons are analyzed:
- **7 days**: Immediate threat assessment
- **30 days**: Short-term monitoring
- **90 days**: Medium-term tracking
- **180 days**: Half-year outlook
- **365 days**: Annual prediction

Each prediction includes:
- **Distance**: How close the asteroid comes to Earth
- **Impact Probability**: Statistical likelihood of impact
- **Approach Time**: When the closest approach occurs

### Impact Scenario

If an impact were to occur:
- **Impact Energy**: Explosive force in megatons of TNT
- **Crater Size**: Expected crater diameter
- **Blast Effects**: Damage radii at various levels

## Model Limitations

⚠️ **Important**: The pure Keplerian model has limitations!

### What's NOT Included:

1. **Gravitational Perturbations**: Effects from Jupiter and other planets
2. **Orbital Resonances**: Long-term changes from periodic interactions
3. **Yarkovsky Effect**: Thermal radiation pressure altering trajectory
4. **Three-Body Dynamics**: Complex gravitational interactions

### When to Trust the Results:

- ✅ **Short-term predictions** (< 1 year): Generally reliable
- ⚠️ **Medium-term** (1-10 years): Use with caution
- ❌ **Long-term** (> 10 years): Numerical integration required

The system automatically assesses confidence and provides warnings.

## API Usage

### Real-time Impact Prediction

**Endpoint:** `POST /api/keplerian/realtime-impact/`

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/keplerian/realtime-impact/ \
  -H "Content-Type: application/json" \
  -d '{
    "semi_major_axis_au": 2.5,
    "eccentricity": 0.2,
    "inclination_deg": 10.0,
    "ascending_node_deg": 0.0,
    "periapsis_arg_deg": 0.0,
    "mean_anomaly_deg": 0.0,
    "diameter_km": 1.0
  }'
```

### Analyze Specific Asteroid

**Endpoint:** `GET /api/keplerian/asteroids/<neo_id>/analysis/`

**Example:**
```bash
curl http://localhost:8000/api/keplerian/asteroids/2000433/analysis/
```

### Calculate Full Trajectory

**Endpoint:** `POST /api/keplerian/trajectory/`

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/keplerian/trajectory/ \
  -H "Content-Type: application/json" \
  -d '{
    "semi_major_axis_au": 2.5,
    "eccentricity": 0.2,
    "inclination_deg": 10.0,
    "duration_days": 365,
    "time_steps": 50
  }'
```

## Tips & Best Practices

### 1. Start with Defaults
Use the pre-filled default values to understand the system before experimenting.

### 2. Vary One Parameter at a Time
Change one orbital element at a time to see its effect on the trajectory.

### 3. Check Confidence Levels
Always review the model limitations section in the results.

### 4. Compare Time Horizons
Look at all prediction horizons to understand trajectory evolution.

### 5. Realistic Values
Use realistic orbital elements:
- Near-Earth asteroids: a < 2.0 AU
- Main belt: 2.0 < a < 3.5 AU
- Eccentricity: Usually < 0.5 for stable orbits

## Educational Use

### Learning Kepler's Laws

**Experiment 1: Orbital Period**
- Keep all parameters constant
- Vary semi-major axis: 1.0, 2.0, 3.0 AU
- Observe: Period increases with distance (Kepler's 3rd Law)

**Experiment 2: Orbital Shape**
- Keep semi-major axis constant at 2.0 AU
- Vary eccentricity: 0.0, 0.3, 0.6
- Observe: Higher eccentricity = more elliptical orbit

**Experiment 3: Orbital Tilt**
- Keep a=2.0, e=0.2 constant
- Vary inclination: 0°, 30°, 60°
- Observe: Effect on Earth approach geometry

## Troubleshooting

### "Orbital elements not available"
The asteroid in the database doesn't have orbital elements stored. Use the manual input form instead.

### Very high impact probabilities
Check if the orbit crosses Earth's orbit (perihelion < 1 AU and aphelion > 1 AU).

### Unrealistic results
Verify orbital elements are within reasonable ranges. Extreme values may produce invalid results.

## Next Steps

1. **Explore the UI**: Try different orbital configurations
2. **Read Full Documentation**: See `KEPLERIAN_ORBITAL_MECHANICS.md` for technical details
3. **Test API Endpoints**: Integrate with your own applications
4. **Compare Models**: Run both Basic and Keplerian simulations to see differences

## Support

For detailed technical information, see:
- `KEPLERIAN_ORBITAL_MECHANICS.md` - Complete technical documentation
- `simulation/keplerian_orbit.py` - Source code with inline comments

Happy asteroid tracking! 🌠
