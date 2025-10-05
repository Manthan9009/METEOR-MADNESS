import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meteor_madness.settings')
django.setup()

from simulation.keplerian_orbit import KeplerianOrbit
from datetime import datetime

print("Testing Keplerian Orbital Mechanics...")
print("=" * 50)

# Test 1: Create orbit
try:
    orbit = KeplerianOrbit(
        a=2.5,      # 2.5 AU
        e=0.2,      # Moderate eccentricity
        i=10.0,     # 10 degrees inclination
        Omega=0,
        omega=0,
        M0=0
    )
    print("✓ KeplerianOrbit instantiation successful")
except Exception as e:
    print(f"✗ Error creating orbit: {e}")
    exit(1)

# Test 2: Get orbital summary
try:
    summary = orbit.get_orbital_summary()
    print("✓ Orbital summary calculation successful")
    print(f"  - Orbital period: {summary['orbital_period_years']:.2f} years")
    print(f"  - Orbit type: {summary['orbit_type']}")
    print(f"  - Perihelion: {summary['perihelion_au']:.3f} AU")
    print(f"  - Aphelion: {summary['aphelion_au']:.3f} AU")
except Exception as e:
    print(f"✗ Error getting orbital summary: {e}")
    exit(1)

# Test 3: Calculate position at current time
try:
    now = datetime.now()
    pos = orbit.position_at_time(now)
    print("✓ Position calculation successful")
    print(f"  - Distance from Sun: {pos['distance_from_sun_au']:.3f} AU")
except Exception as e:
    print(f"✗ Error calculating position: {e}")
    exit(1)

# Test 4: Calculate velocity
try:
    vel = orbit.velocity_at_time(now)
    print("✓ Velocity calculation successful")
    print(f"  - Speed: {vel['speed_km_s']:.2f} km/s")
except Exception as e:
    print(f"✗ Error calculating velocity: {e}")
    exit(1)

# Test 5: Find closest approach
try:
    closest = orbit.find_closest_approach(now, duration_days=365)
    print("✓ Closest approach calculation successful")
    print(f"  - Distance: {closest['closest_distance_earth_radii']:.1f} Earth radii")
    print(f"  - Impact probability: {closest['impact_probability']:.2e}")
except Exception as e:
    print(f"✗ Error finding closest approach: {e}")
    exit(1)

print("=" * 50)
print("All tests passed! ✓")
