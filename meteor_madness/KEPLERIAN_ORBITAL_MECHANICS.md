# Keplerian Orbital Mechanics Implementation

## Overview

This implementation adds **real-time impact prediction** using Keplerian orbital mechanics based on Johannes Kepler's three laws of planetary motion. The system calculates asteroid trajectories, predicts closest approaches to Earth, and estimates impact probabilities.

## Theoretical Foundation

### The Pure Keplerian Model

The Keplerian model uses six orbital elements to completely define an asteroid's orbit:

1. **Semi-major axis (a)**: Half of the longest diameter of the elliptical orbit. Determines the orbital period via Kepler's Third Law.

2. **Eccentricity (e)**: Measures deviation from a circular orbit (0 = circle, approaching 1 = elongated ellipse).

3. **Inclination (i)**: The angle of the orbital plane relative to Earth's orbital plane (the ecliptic).

4. **Longitude of ascending node (Ω)**: The angle from the vernal equinox to where the orbit crosses the ecliptic from south to north.

5. **Argument of periapsis (ω)**: The angle from the ascending node to the point of closest approach to the Sun (perihelion).

6. **Mean anomaly (M)**: An angular position that changes linearly with time, specifying the asteroid's location at a given epoch.

### Key Equations

#### Kepler's Third Law (Orbital Period)
```
T² = (4π²/μ) × a³
```
Where μ is the standard gravitational parameter for the Sun.

#### Kepler's Equation (Position at Time)
```
M = E - e·sin(E)
```
Solved iteratively using Newton-Raphson method to find eccentric anomaly E.

#### True Anomaly (Actual Position)
```
tan(ν/2) = √((1+e)/(1-e)) × tan(E/2)
```

#### Vis-viva Equation (Velocity)
```
v² = μ(2/r - 1/a)
```

## Implementation Components

### 1. Core Module: `keplerian_orbit.py`

**Key Classes:**
- `KeplerianOrbit`: Main class representing an asteroid's orbit

**Key Functions:**
- `calculate_orbital_period()`: Computes period using Kepler's Third Law
- `mean_anomaly_at_time()`: Calculates mean anomaly at any time
- `solve_kepler_equation()`: Iteratively solves for eccentric anomaly
- `position_at_time()`: Returns 3D position in heliocentric coordinates
- `velocity_at_time()`: Calculates velocity vector
- `earth_distance_at_time()`: Computes distance from Earth
- `find_closest_approach()`: Finds minimum Earth distance in time window
- `assess_keplerian_limitations()`: Evaluates model accuracy

### 2. Database Model Extensions

Added to `Asteroid` model:
```python
semi_major_axis_au      # Semi-major axis in AU
eccentricity            # Orbital eccentricity (0-1)
inclination_deg         # Inclination in degrees
ascending_node_deg      # Longitude of ascending node
periapsis_arg_deg       # Argument of periapsis
mean_anomaly_deg        # Mean anomaly at epoch
orbital_period_days     # Orbital period in days
```

### 3. API Endpoints

#### `/api/keplerian/trajectory/` (POST)
Calculate full orbital trajectory over time.

**Request:**
```json
{
  "semi_major_axis_au": 2.5,
  "eccentricity": 0.2,
  "inclination_deg": 10.0,
  "ascending_node_deg": 0.0,
  "periapsis_arg_deg": 0.0,
  "mean_anomaly_deg": 0.0,
  "duration_days": 365,
  "time_steps": 50
}
```

**Response:**
- Orbital summary (period, perihelion, aphelion, orbit type)
- Trajectory points (position, velocity, Earth distance)
- Closest approach data
- Model limitations assessment

#### `/api/keplerian/asteroids/<neo_id>/analysis/` (GET)
Get Keplerian analysis for a specific asteroid.

**Response:**
- Current orbital state
- Closest approach in next year
- Impact potential calculations
- Model confidence assessment

#### `/api/keplerian/realtime-impact/` (POST)
Real-time impact prediction with multiple time horizons.

**Request:**
```json
{
  "semi_major_axis_au": 2.5,
  "eccentricity": 0.2,
  "inclination_deg": 10.0,
  "diameter_km": 1.0
}
```

**Response:**
- Predictions for 7, 30, 90, 180, 365 day horizons
- Impact probability for each horizon
- Potential impact effects (energy, crater, blast radii)

### 4. User Interface

**Simulator Page** (`/simulator/`)

Two simulation modes:

1. **Basic Impact**: Simple impact calculations with location parameters
2. **Keplerian Orbital**: Advanced orbital mechanics with:
   - Input fields for all six orbital elements
   - Real-time trajectory calculation
   - Multiple time horizon predictions
   - Orbital characteristics display
   - Impact probability assessment

## Model Limitations

The pure Keplerian model has important limitations for long-term predictions:

### 1. Gravitational Perturbations
The model assumes only solar gravity. In reality:
- Jupiter's gravity significantly affects asteroid orbits
- Other planets also exert gravitational forces
- These perturbations accumulate over time

### 2. Orbital Resonances
When an asteroid's orbital period is in a simple ratio with a planet's period (e.g., 2:1, 3:1), small periodic perturbations add up, causing substantial long-term orbital changes.

**Example:** Kirkwood gaps in the asteroid belt are caused by resonances with Jupiter.

### 3. Non-gravitational Forces

**Yarkovsky Effect:**
- Uneven absorption and re-emission of solar radiation
- Creates tiny but constant thrust
- Can significantly alter trajectory over decades
- Not modeled in pure Keplerian mechanics

### 4. Three-Body Problem
The motion of three gravitationally interacting bodies is chaotic and has no general analytical solution. Accurate long-term predictions require numerical integration.

### Confidence Assessment

The implementation includes `assess_keplerian_limitations()` which evaluates:
- Proximity to orbital resonances with Jupiter
- Eccentricity (high values increase perturbation sensitivity)
- Time horizon (accuracy decreases with longer predictions)
- Close planetary approaches
- Returns confidence percentage and recommendations

**Confidence Levels:**
- **≥80%**: Keplerian model suitable for short-term predictions
- **50-80%**: Acceptable with caution; consider perturbations
- **<50%**: Numerical integration required for accuracy

## Usage Examples

### Example 1: Calculate Asteroid Trajectory

```python
from simulation.keplerian_orbit import KeplerianOrbit
from datetime import datetime

# Create orbit with typical Near-Earth Asteroid parameters
orbit = KeplerianOrbit(
    a=1.5,           # 1.5 AU semi-major axis
    e=0.3,           # Moderate eccentricity
    i=15.0,          # 15° inclination
    Omega=45.0,      # Ascending node
    omega=90.0,      # Argument of periapsis
    M0=0.0           # Mean anomaly at epoch
)

# Get orbital summary
summary = orbit.get_orbital_summary()
print(f"Orbital Period: {summary['orbital_period_years']:.2f} years")
print(f"Orbit Type: {summary['orbit_type']}")

# Find closest approach to Earth in next year
closest = orbit.find_closest_approach(datetime.now(), duration_days=365)
print(f"Closest Distance: {closest['closest_distance_earth_radii']:.1f} Earth radii")
print(f"Impact Probability: {closest['impact_probability']:.2e}")
```

### Example 2: Real-time Impact Prediction via API

```javascript
// JavaScript example for web interface
const response = await fetch('/api/keplerian/realtime-impact/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        semi_major_axis_au: 2.5,
        eccentricity: 0.2,
        inclination_deg: 10.0,
        diameter_km: 1.0
    })
});

const data = await response.json();
console.log('Predictions:', data.predictions);
console.log('Impact Scenario:', data.impact_scenario);
```

### Example 3: Analyze Stored Asteroid

```python
from simulation.models import Asteroid

# Get asteroid from database
asteroid = Asteroid.objects.get(neo_id='2000433')

# Check if orbital elements are available
if asteroid.has_orbital_elements():
    orbit = asteroid.get_keplerian_orbit()
    
    # Calculate current position
    from datetime import datetime
    pos = orbit.position_at_time(datetime.now())
    print(f"Distance from Sun: {pos['distance_from_sun_au']:.3f} AU")
```

## Testing the Implementation

### 1. Run Database Migration
```bash
python manage.py migrate simulation
```

### 2. Access Simulator
Navigate to: `http://localhost:8000/simulator/`

### 3. Test Keplerian Mode
1. Click "Keplerian Orbital" tab
2. Enter orbital elements (or use defaults)
3. Click "Calculate Orbital Trajectory"
4. Review results:
   - Orbital characteristics
   - Closest approach predictions
   - Impact probabilities
   - Model limitations

### 4. Test API Endpoints

**Example cURL command:**
```bash
curl -X POST http://localhost:8000/api/keplerian/realtime-impact/ \
  -H "Content-Type: application/json" \
  -d '{
    "semi_major_axis_au": 2.5,
    "eccentricity": 0.2,
    "inclination_deg": 10.0,
    "diameter_km": 1.0
  }'
```

## Future Enhancements

### 1. Numerical Integration
Implement n-body numerical integration to account for:
- Planetary perturbations
- Relativistic effects
- Solar radiation pressure

### 2. Uncertainty Propagation
Add Monte Carlo simulations to:
- Account for orbital element uncertainties
- Generate probability distributions
- Provide confidence intervals

### 3. Resonance Detection
Automatically detect and warn about:
- Mean motion resonances
- Secular resonances
- Kozai-Lidov mechanism

### 4. Visualization
Add interactive 3D orbital visualization:
- Plot asteroid trajectory
- Show Earth's orbit
- Display closest approach points
- Animate orbital motion

## References

1. **Kepler's Laws**: Murray, C. D., & Dermott, S. F. (1999). *Solar System Dynamics*. Cambridge University Press.

2. **Orbital Mechanics**: Vallado, D. A. (2013). *Fundamentals of Astrodynamics and Applications*. Microcosm Press.

3. **Yarkovsky Effect**: Vokrouhlický, D., et al. (2015). "The Yarkovsky and YORP Effects." *Asteroids IV*.

4. **Near-Earth Objects**: Milani, A., et al. (2005). "Asteroid Close Approaches: Analysis and Potential Impact Detection." *Icarus*.

## License

This implementation is part of the Meteor Madness project and follows the same license terms.

## Contact

For questions or issues related to the Keplerian orbital mechanics implementation, please open an issue in the project repository.
