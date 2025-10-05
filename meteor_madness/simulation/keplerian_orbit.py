"""
Keplerian Orbital Mechanics Module
Implements pure Keplerian orbital calculations for asteroid trajectory prediction
and real-time impact assessment.

Based on Johannes Kepler's three laws of planetary motion.
"""
import math
import numpy as np
from datetime import datetime, timedelta


# Constants
AU_TO_KM = 149597870.7  # 1 Astronomical Unit in kilometers
G = 6.67430e-11  # Gravitational constant (m³/kg·s²)
M_SUN = 1.989e30  # Mass of the Sun (kg)
M_EARTH = 5.972e24  # Mass of Earth (kg)
R_EARTH = 6371.0  # Earth radius (km)
MU_SUN = G * M_SUN / 1e9  # Standard gravitational parameter for Sun (km³/s²)


def classify_orbit_type(semi_major_axis_au, eccentricity, perihelion_au):
    """
    Classify the orbit type based on orbital elements.
    
    Args:
        semi_major_axis_au: Semi-major axis in AU
        eccentricity: Orbital eccentricity (0-1)
        perihelion_au: Perihelion distance in AU
        
    Returns:
        String describing the orbit type
    """
    if eccentricity >= 1.0:
        return "Hyperbolic (not bound to solar system)"
    elif semi_major_axis_au < 0.98:
        return "Aten (Earth-crossing, semi-major axis < 1 AU)"
    elif perihelion_au < 1.3:
        return "Apollo (Earth-crossing, semi-major axis > 1 AU)"
    elif 1.0 < semi_major_axis_au < 1.3 and eccentricity < 0.35:
        return "Amor (Near-Earth, perihelion between 1.017-1.3 AU)"
    elif semi_major_axis_au < 2.5:
        return "Inner Solar System Object"
    elif 2.5 <= semi_major_axis_au <= 3.2 and eccentricity < 0.3:
        return "Main Belt Asteroid"
    elif semi_major_axis_au > 3.2:
        if perihelion_au < 1.3:
            return "Potentially Hazardous Object (PHO)"
        else:
            return "Outer Solar System Object"
    else:
        return "Unknown Orbit Type"


class KeplerianOrbit:
    """
    Represents an asteroid's orbit using Keplerian orbital elements.
    
    Orbital Elements:
    - a: Semi-major axis (AU)
    - e: Eccentricity (dimensionless, 0 = circle, <1 = ellipse)
    - i: Inclination (degrees)
    - Omega: Longitude of ascending node (degrees)
    - omega: Argument of periapsis (degrees)
    - M0: Mean anomaly at epoch (degrees)
    - epoch: Reference time for orbital elements
    """
    
    def __init__(self, a, e, i, Omega, omega, M0, epoch=None):
        """
        Initialize Keplerian orbital elements.
        
        Args:
            a: Semi-major axis in AU
            e: Eccentricity (0 to 1)
            i: Inclination in degrees
            Omega: Longitude of ascending node in degrees
            omega: Argument of periapsis in degrees
            M0: Mean anomaly at epoch in degrees
            epoch: Reference datetime (default: now)
        """
        self.a = a  # Semi-major axis (AU)
        self.e = e  # Eccentricity
        self.i = math.radians(i)  # Inclination (radians)
        self.Omega = math.radians(Omega)  # Longitude of ascending node (radians)
        self.omega = math.radians(omega)  # Argument of periapsis (radians)
        self.M0 = math.radians(M0)  # Mean anomaly at epoch (radians)
        self.epoch = epoch if epoch else datetime.now()
        
        # Calculate derived parameters
        self.a_km = self.a * AU_TO_KM
        self.period = self.calculate_orbital_period()
        self.perihelion = self.a * (1 - self.e)  # Closest approach to Sun (AU)
        self.aphelion = self.a * (1 + self.e)  # Farthest from Sun (AU)
    
    def calculate_orbital_period(self):
        """
        Calculate orbital period using Kepler's Third Law.
        T² = (4π²/μ) * a³
        
        Returns:
            Orbital period in days
        """
        # Period in seconds
        T_seconds = 2 * math.pi * math.sqrt((self.a_km ** 3) / MU_SUN)
        # Convert to days
        return T_seconds / 86400
    
    def mean_anomaly_at_time(self, target_time):
        """
        Calculate mean anomaly at a given time.
        M(t) = M0 + n(t - t0), where n is mean motion
        
        Args:
            target_time: datetime object
            
        Returns:
            Mean anomaly in radians
        """
        # Time difference in days
        dt_days = (target_time - self.epoch).total_seconds() / 86400
        
        # Mean motion (radians per day)
        n = 2 * math.pi / self.period
        
        # Mean anomaly at target time
        M = self.M0 + n * dt_days
        
        # Normalize to [0, 2π]
        M = M % (2 * math.pi)
        
        return M
    
    def solve_kepler_equation(self, M, tolerance=1e-8, max_iterations=100):
        """
        Solve Kepler's equation: M = E - e*sin(E)
        Uses Newton-Raphson iteration to find eccentric anomaly E.
        
        Args:
            M: Mean anomaly (radians)
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations
            
        Returns:
            Eccentric anomaly E (radians)
        """
        # Initial guess
        E = M if self.e < 0.8 else math.pi
        
        for _ in range(max_iterations):
            f = E - self.e * math.sin(E) - M
            f_prime = 1 - self.e * math.cos(E)
            
            E_new = E - f / f_prime
            
            if abs(E_new - E) < tolerance:
                return E_new
            
            E = E_new
        
        return E  # Return best estimate if not converged
    
    def true_anomaly_from_eccentric(self, E):
        """
        Calculate true anomaly from eccentric anomaly.
        
        Args:
            E: Eccentric anomaly (radians)
            
        Returns:
            True anomaly (radians)
        """
        # tan(ν/2) = sqrt((1+e)/(1-e)) * tan(E/2)
        nu = 2 * math.atan2(
            math.sqrt(1 + self.e) * math.sin(E / 2),
            math.sqrt(1 - self.e) * math.cos(E / 2)
        )
        return nu
    
    def position_at_time(self, target_time):
        """
        Calculate 3D position of asteroid at given time.
        Returns position in heliocentric ecliptic coordinates.
        
        Args:
            target_time: datetime object
            
        Returns:
            Dictionary with x, y, z coordinates (km) and distance from Sun
        """
        # Get mean anomaly at target time
        M = self.mean_anomaly_at_time(target_time)
        
        # Solve for eccentric anomaly
        E = self.solve_kepler_equation(M)
        
        # Calculate true anomaly
        nu = self.true_anomaly_from_eccentric(E)
        
        # Calculate distance from Sun
        r = self.a_km * (1 - self.e * math.cos(E))
        
        # Position in orbital plane
        x_orb = r * math.cos(nu)
        y_orb = r * math.sin(nu)
        
        # Transform to ecliptic coordinates
        cos_Omega = math.cos(self.Omega)
        sin_Omega = math.sin(self.Omega)
        cos_i = math.cos(self.i)
        sin_i = math.sin(self.i)
        cos_omega = math.cos(self.omega)
        sin_omega = math.sin(self.omega)
        
        x = (cos_Omega * cos_omega - sin_Omega * sin_omega * cos_i) * x_orb + \
            (-cos_Omega * sin_omega - sin_Omega * cos_omega * cos_i) * y_orb
        
        y = (sin_Omega * cos_omega + cos_Omega * sin_omega * cos_i) * x_orb + \
            (-sin_Omega * sin_omega + cos_Omega * cos_omega * cos_i) * y_orb
        
        z = (sin_omega * sin_i) * x_orb + (cos_omega * sin_i) * y_orb
        
        return {
            'x': x,
            'y': y,
            'z': z,
            'distance_from_sun_km': r,
            'distance_from_sun_au': r / AU_TO_KM,
            'true_anomaly_deg': math.degrees(nu),
            'eccentric_anomaly_deg': math.degrees(E),
            'mean_anomaly_deg': math.degrees(M)
        }
    
    def velocity_at_time(self, target_time):
        """
        Calculate velocity vector at given time using vis-viva equation.
        v² = μ(2/r - 1/a)
        
        Args:
            target_time: datetime object
            
        Returns:
            Dictionary with velocity components and magnitude
        """
        pos = self.position_at_time(target_time)
        r = pos['distance_from_sun_km']
        
        # Vis-viva equation for speed
        v_magnitude = math.sqrt(MU_SUN * (2 / r - 1 / self.a_km))
        
        # Get mean anomaly and solve for E
        M = self.mean_anomaly_at_time(target_time)
        E = self.solve_kepler_equation(M)
        nu = self.true_anomaly_from_eccentric(E)
        
        # Velocity components in orbital plane
        h = math.sqrt(MU_SUN * self.a_km * (1 - self.e ** 2))  # Specific angular momentum
        
        vx_orb = -(MU_SUN / h) * math.sin(nu)
        vy_orb = (MU_SUN / h) * (self.e + math.cos(nu))
        
        # Transform to ecliptic coordinates
        cos_Omega = math.cos(self.Omega)
        sin_Omega = math.sin(self.Omega)
        cos_i = math.cos(self.i)
        sin_i = math.sin(self.i)
        cos_omega = math.cos(self.omega)
        sin_omega = math.sin(self.omega)
        
        vx = (cos_Omega * cos_omega - sin_Omega * sin_omega * cos_i) * vx_orb + \
             (-cos_Omega * sin_omega - sin_Omega * cos_omega * cos_i) * vy_orb
        
        vy = (sin_Omega * cos_omega + cos_Omega * sin_omega * cos_i) * vx_orb + \
             (-sin_Omega * sin_omega + cos_Omega * cos_omega * cos_i) * vy_orb
        
        vz = (sin_omega * sin_i) * vx_orb + (cos_omega * sin_i) * vy_orb
        
        return {
            'vx': vx,
            'vy': vy,
            'vz': vz,
            'speed_km_s': v_magnitude,
            'speed_km_h': v_magnitude * 3600
        }
    
    def earth_distance_at_time(self, target_time):
        """
        Calculate distance from asteroid to Earth at given time.
        Simplified: assumes Earth at 1 AU circular orbit.
        
        Args:
            target_time: datetime object
            
        Returns:
            Distance from Earth in kilometers
        """
        # Get asteroid position
        ast_pos = self.position_at_time(target_time)
        
        # Simplified Earth position (circular orbit at 1 AU)
        # Earth's orbital period is 365.25 days
        days_since_epoch = (target_time - self.epoch).total_seconds() / 86400
        earth_angle = (days_since_epoch / 365.25) * 2 * math.pi
        
        earth_x = AU_TO_KM * math.cos(earth_angle)
        earth_y = AU_TO_KM * math.sin(earth_angle)
        earth_z = 0  # Earth in ecliptic plane
        
        # Calculate distance
        dx = ast_pos['x'] - earth_x
        dy = ast_pos['y'] - earth_y
        dz = ast_pos['z'] - earth_z
        
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        return {
            'distance_km': distance,
            'distance_au': distance / AU_TO_KM,
            'asteroid_position': ast_pos,
            'earth_position': {'x': earth_x, 'y': earth_y, 'z': earth_z}
        }
    
    def find_closest_approach(self, start_time, duration_days=365, initial_step_days=5):
        """
        Find the closest approach to Earth within a time window using adaptive time stepping.
        
        Args:
            start_time: Starting datetime
            duration_days: Duration to search (days)
            initial_step_days: Initial time step for search (days), will be reduced near close approaches
            
        Returns:
            Dictionary with closest approach information
        """
        def scan_approaches(start, end, step_days):
            min_distance = float('inf')
            closest_time = None
            closest_data = None
            
            current_time = start
            while current_time <= end:
                try:
                    distance_data = self.earth_distance_at_time(current_time)
                    distance = distance_data['distance_km']
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_time = current_time
                        closest_data = distance_data
                except Exception as e:
                    # Skip any time steps that cause calculation errors
                    print(f"Warning: Error calculating distance at {current_time}: {str(e)}")
                
                current_time += timedelta(days=step_days)
            
            return closest_time, closest_data, min_distance
        
        try:
            # Initial coarse scan
            end_time = start_time + timedelta(days=duration_days)
            closest_time, closest_data, min_distance = scan_approaches(
                start_time, end_time, initial_step_days
            )
            
            if not closest_time:
                print("Warning: No closest approach found in initial scan")
                return None
                
            # Refine search with progressively smaller steps
            for step_days in [1, 0.1, 0.01]:
                window_days = step_days * 10  # Look 10 steps before and after
                window_start = max(start_time, closest_time - timedelta(days=window_days))
                window_end = min(end_time, closest_time + timedelta(days=window_days))
                
                new_closest_time, new_closest_data, new_min_distance = scan_approaches(
                    window_start, window_end, step_days
                )
                
                # Only update if we found a closer approach
                if new_closest_time and new_min_distance < min_distance:
                    closest_time, closest_data, min_distance = new_closest_time, new_closest_data, new_min_distance
            
            # Final refinement with hourly precision
            window_start = closest_time - timedelta(days=1)
            window_end = closest_time + timedelta(days=1)
            final_closest_time, final_closest_data, final_min_distance = scan_approaches(
                window_start, window_end, 1/24  # Hourly steps
            )
            
            # Use the most accurate results
            if final_closest_time and final_min_distance <= min_distance:
                closest_time, closest_data, min_distance = final_closest_time, final_closest_data, final_min_distance
            
            # Get detailed orbital data at closest approach
            velocity_data = self.velocity_at_time(closest_time)
            position_data = self.position_at_time(closest_time)
            
            # Calculate relative velocity vector to Earth
            earth_velocity = self._calculate_earth_velocity(closest_time)
            relative_velocity = {
                'vx': velocity_data['vx'] - earth_velocity['vx'],
                'vy': velocity_data['vy'] - earth_velocity['vy'],
                'vz': velocity_data['vz'] - earth_velocity['vz']
            }
            relative_speed = math.sqrt(
                relative_velocity['vx']**2 + 
                relative_velocity['vy']**2 + 
                relative_velocity['vz']**2
            )
            
            # Calculate days to impact
            days_to_impact = (closest_time - datetime.now()).days
            
            # Calculate impact probability with more factors
            impact_result = calculate_impact_probability(
                miss_distance_km=min_distance,
                distance_from_sun_au=position_data['distance_from_sun_au'],
                relative_velocity_km_s=relative_speed,
                days_to_impact=days_to_impact
            )
            
            # Ensure we have a valid probability value
            impact_probability = 0.0
            if isinstance(impact_result, dict) and 'probability' in impact_result:
                impact_probability = max(0.0, min(1.0, float(impact_result['probability'])))
            
            # Calculate uncertainty based on time from now
            time_until_approach = (closest_time - datetime.now()).total_seconds() / (3600 * 24)  # days
            uncertainty_factor = max(0.1, min(1.0, 1 - (time_until_approach / 365)))
            
            return {
                'closest_approach_time': closest_time,
                'closest_distance_km': min_distance,
                'closest_distance_au': min_distance / AU_TO_KM,
                'closest_distance_earth_radii': min_distance / R_EARTH,
                'relative_velocity_km_s': relative_speed,
                'relative_velocity_km_h': relative_speed * 3600,
                'impact_probability': impact_probability,
                'impact_confidence': impact_result.get('confidence', 0.5) if isinstance(impact_result, dict) else 0.5,
                'impact_factors': impact_result.get('factors', []) if isinstance(impact_result, dict) else [],
                'position_data': closest_data,
                'relative_velocity_components': relative_velocity,
                'uncertainty_factor': uncertainty_factor
            }
            
        except Exception as e:
            print(f"Error in find_closest_approach: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calculate_earth_velocity(self, target_time):
        """
        Calculate Earth's velocity vector at a given time (simplified circular orbit).
        
        Args:
            target_time: datetime object
            
        Returns:
            Dictionary with Earth's velocity components (km/s)
        """
        # Earth's orbital parameters (simplified circular orbit)
        earth_semi_major_axis_km = 149.6e6  # km
        earth_orbital_period_days = 365.25
        
        # Calculate Earth's position angle (mean anomaly)
        days_since_epoch = (target_time - datetime(target_time.year, 1, 1)).days
        mean_anomaly = (2 * math.pi * days_since_epoch) / earth_orbital_period_days
        
        # Earth's orbital speed (km/s)
        earth_speed = 29.78  # km/s (average)
        
        # Velocity components in ecliptic plane
        vx = -earth_speed * math.sin(mean_anomaly)
        vy = earth_speed * math.cos(mean_anomaly)
        
        return {
            'vx': vx,
            'vy': vy,
            'vz': 0.0,
            'speed_km_s': earth_speed,
            'speed_km_h': earth_speed * 3600
        }
        
    def get_orbital_summary(self):
        """
        Get summary of orbital characteristics.
        
        Returns:
            Dictionary with orbital parameters and characteristics
        """
        return {
            'semi_major_axis_au': self.a,
            'semi_major_axis_km': self.a_km,
            'eccentricity': self.e,
            'inclination_deg': math.degrees(self.i),
            'longitude_ascending_node_deg': math.degrees(self.Omega),
            'argument_periapsis_deg': math.degrees(self.omega),
            'mean_anomaly_epoch_deg': math.degrees(self.M0),
            'orbital_period_days': self.period,
            'orbital_period_years': self.period / 365.25,
            'perihelion_au': self.perihelion,
            'aphelion_au': self.aphelion,
            'perihelion_km': self.perihelion * AU_TO_KM,
            'aphelion_km': self.aphelion * AU_TO_KM,
            'orbit_type': classify_orbit_type(self.a, self.e, self.perihelion)
        }


def calculate_impact_probability(miss_distance_km, distance_from_sun_au, relative_velocity_km_s=None, days_to_impact=None):
    """
    Calculate impact probability based on miss distance, orbit, relative velocity, and time to impact.
    
    Args:
        miss_distance_km: Closest approach distance to Earth (km)
        distance_from_sun_au: Distance from Sun at closest approach (AU)
        relative_velocity_km_s: Relative velocity at closest approach (km/s, optional)
        days_to_impact: Days until closest approach (optional, used for uncertainty modeling)
        
    Returns:
        Dictionary with impact probability (0 to 1), confidence metrics, and factors
    """
    try:
        # Ensure valid inputs
        if miss_distance_km is None or miss_distance_km < 0:
            return {'probability': 0.0, 'confidence': 0.0, 'factors': ['Invalid distance']}
            
        # Convert miss distance to Earth radii, ensure it's not zero
        miss_distance_er = max(0.1, miss_distance_km / R_EARTH)
        
        # Handle negative or zero relative velocity
        relative_velocity = max(0.1, relative_velocity_km_s) if relative_velocity_km_s and relative_velocity_km_s > 0 else 30.0
        
        # 1. Base impact probability based on miss distance (exponential decay)
        # Earth's radius is 1 in Earth radii units
        if miss_distance_er <= 1.0:  # Inside Earth's radius
            return {
                'probability': 1.0,
                'confidence': 0.95,
                'factors': ['Inside Earth radius']
            }
        
        # 2. Calculate gravitational focusing effect
        earth_escape_velocity = 11.2  # km/s
        focus_factor = 1.0 + (earth_escape_velocity / relative_velocity) ** 2
        
        # 3. Distance-based probability (exponential decay with distance)
        # Scale factor to make probability decrease rapidly with distance
        distance_decay = math.exp(-0.5 * (miss_distance_er - 1.0))
        
        # 4. Time-based uncertainty (if days_to_impact is provided)
        time_uncertainty = 1.0
        if days_to_impact is not None:
            # Uncertainty increases with time, but not linearly
            # After 30 days, uncertainty starts to increase more significantly
            time_uncertainty = min(1.0, max(0.1, 1.0 / (1.0 + math.log1p(days_to_impact / 30.0))))
        
        # 5. Combine factors
        base_probability = distance_decay * focus_factor * time_uncertainty
        
        # 6. Apply sigmoid function to get smooth probability between 0 and 1
        # This gives us a nice S-curve that's very low at large distances
        # and approaches 1 as distance approaches 0
        probability = 1.0 / (1.0 + math.exp(10.0 * (miss_distance_er - 2.0)))
        
        # 7. Adjust probability based on time uncertainty
        probability *= time_uncertainty
        
        # 8. Calculate confidence based on distance and time
        # Closer approaches have higher confidence
        distance_confidence = max(0.1, 1.0 - (miss_distance_er / 100.0))
        
        # If we have time information, adjust confidence
        time_confidence = 1.0
        if days_to_impact is not None:
            # Confidence decreases with time to impact
            time_confidence = 1.0 / (1.0 + (days_to_impact / 365.0))
        
        confidence = min(0.9, max(0.1, 0.7 * distance_confidence * time_confidence))
        
        # 9. Prepare factors for the return value
        factors = []
        if miss_distance_er < 5.0:
            factors.append('Very close approach')
        elif miss_distance_er < 20.0:
            factors.append('Moderate approach')
        else:
            factors.append('Distant approach')
            
        if focus_factor > 1.5:
            factors.append('High gravitational focusing')
            
        if days_to_impact is not None and days_to_impact > 30:
            factors.append(f'Long time horizon ({days_to_impact} days)')
        
        return {
            'probability': min(0.9999, max(1e-20, probability)),  # Ensure probability is in (0,1)
            'confidence': confidence,
            'factors': factors,
            'distance_er': miss_distance_er,
            'time_uncertainty': time_uncertainty
        }
            
    except Exception as e:
        # Fallback in case of any calculation errors
        return {
            'probability': 0.0,
            'confidence': 0.0,
            'factors': [f'Calculation error: {str(e)}']
        }


def assess_keplerian_limitations(orbit, time_horizon_years):
    """
    Assess limitations of pure Keplerian model for given orbit and timeframe.
    
    Args:
        orbit: KeplerianOrbit object
        time_horizon_years: Prediction timeframe in years
        
    Returns:
        Dictionary with limitation assessment
    """
    warnings = []
    confidence = 100.0  # Start at 100% confidence
    
    # Check for Jupiter resonance (major perturbation source)
    jupiter_a = 5.2  # AU
    period_ratio = orbit.period / (11.86 * 365.25)  # Jupiter's period
    
    # Check for mean motion resonances (e.g., 2:1, 3:1, 3:2)
    resonances = [2/1, 3/1, 3/2, 5/2, 7/3]
    for resonance in resonances:
        if abs(period_ratio - resonance) < 0.05:
            warnings.append(f"Potential {resonance:.1f}:1 resonance with Jupiter")
            confidence -= 20
    
    # High eccentricity increases perturbation effects
    if orbit.e > 0.3:
        warnings.append(f"High eccentricity ({orbit.e:.2f}) increases perturbation sensitivity")
        confidence -= 10
    
    # Long time horizons reduce accuracy
    if time_horizon_years > 10:
        warnings.append(f"Long prediction horizon ({time_horizon_years:.1f} years) reduces accuracy")
        confidence -= time_horizon_years * 2
    
    # Close approaches to planets
    if orbit.perihelion < 1.3:  # Close to Earth's orbit
        warnings.append("Close approaches to Earth may cause significant perturbations")
        confidence -= 15
    
    # Yarkovsky effect (thermal radiation pressure)
    warnings.append("Yarkovsky effect not modeled (can alter orbit over decades)")
    confidence -= 5
    
    confidence = max(0, confidence)
    
    return {
        'confidence_percent': confidence,
        'warnings': warnings,
        'recommendation': get_recommendation(confidence),
        'requires_numerical_integration': confidence < 50
    }


def get_recommendation(confidence):
    """Get recommendation based on confidence level."""
    if confidence >= 80:
        return "Keplerian model suitable for short-term predictions"
    elif confidence >= 50:
        return "Keplerian model acceptable with caution; consider perturbations"
    else:
        return "Numerical integration required for accurate predictions"
