from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Asteroid, Earthquake
from datetime import datetime

# Create your views here.

def home(request):
    """Home page view"""
    return render(request, 'simulation/home.html')

def fetch_asteroids(request):
    """Fetch asteroids from NASA API and display them"""
    from datetime import datetime, timedelta
    import requests
    from django.conf import settings
    from .models import Asteroid
    
    # Get date range (today and next 7 days)
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=7)
    
    # Fetch from NASA API
    url = f"{settings.NASA_API_BASE_URL}feed"
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'api_key': settings.NASA_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse and save asteroids
        asteroids_saved = 0
        near_earth_objects = data.get('near_earth_objects', {})
        
        for date, asteroids in near_earth_objects.items():
            for asteroid_data in asteroids:
                # Extract data
                neo_id = asteroid_data.get('id')
                name = asteroid_data.get('name')
                absolute_magnitude = asteroid_data.get('absolute_magnitude_h')
                
                diameter = asteroid_data.get('estimated_diameter', {}).get('kilometers', {})
                diameter_min = diameter.get('estimated_diameter_min')
                diameter_max = diameter.get('estimated_diameter_max')
                
                is_hazardous = asteroid_data.get('is_potentially_hazardous_asteroid', False)
                
                # Get close approach data
                close_approach = asteroid_data.get('close_approach_data', [{}])[0]
                approach_date = close_approach.get('close_approach_date')
                approach_date_full = close_approach.get('close_approach_date_full')
                epoch_ms = close_approach.get('epoch_date_close_approach')

                # Parse precise datetime if available
                approach_dt = None
                try:
                    if approach_date_full:
                        # Example: "2025-Jan-05 12:34"
                        approach_dt = datetime.strptime(approach_date_full, '%Y-%b-%d %H:%M')
                    elif epoch_ms:
                        approach_dt = datetime.utcfromtimestamp(int(epoch_ms) / 1000.0)
                except Exception:
                    approach_dt = None

                velocity = close_approach.get('relative_velocity', {}).get('kilometers_per_hour')
                miss_distance = close_approach.get('miss_distance', {}).get('kilometers')
                orbiting_body = close_approach.get('orbiting_body')
                
                # Save or update asteroid
                Asteroid.objects.update_or_create(
                    neo_id=neo_id,
                    defaults={
                        'name': name,
                        'absolute_magnitude': absolute_magnitude,
                        'estimated_diameter_min_km': diameter_min,
                        'estimated_diameter_max_km': diameter_max,
                        'is_potentially_hazardous': is_hazardous,
                        'close_approach_date': approach_date,
                        'close_approach_datetime': approach_dt,
                        'relative_velocity_kmh': velocity,
                        'miss_distance_km': miss_distance,
                        'orbiting_body': orbiting_body,
                    }
                )
                asteroids_saved += 1
        
        messages.success(request, f'Successfully fetched {asteroids_saved} asteroids from NASA!')
        
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Error fetching data from NASA API: {str(e)}')
    
    return redirect('asteroid_list')

def asteroid_list(request):
    """Display list of asteroids with filtering options"""
    asteroids = Asteroid.objects.all()
    
    # Filter by hazardous status
    filter_hazardous = request.GET.get('hazardous')
    if filter_hazardous == 'true':
        asteroids = asteroids.filter(is_potentially_hazardous=True)
    elif filter_hazardous == 'false':
        asteroids = asteroids.filter(is_potentially_hazardous=False)
    
    # Filter by miss distance (in million km)
    max_miss_distance = request.GET.get('max_miss_distance')
    if max_miss_distance and max_miss_distance.isdigit():
        max_miss_distance_km = float(max_miss_distance) * 1_000_000  # Convert to km
        asteroids = asteroids.filter(miss_distance_km__lte=max_miss_distance_km)
    
    # Filter by impact probability (using a simple threshold for demonstration)
    impact_risk = request.GET.get('impact_risk')
    if impact_risk == 'high':
        # Consider asteroids with miss distance < 1M km and high velocity as high risk
        asteroids = asteroids.filter(
            miss_distance_km__lt=1_000_000,
            relative_velocity_kmh__gt=50_000
        ).order_by('miss_distance_km')
    
    context = {
        'asteroids': asteroids,
        'total_count': asteroids.count(),
        'hazardous_count': Asteroid.objects.filter(is_potentially_hazardous=True).count(),
        'current_filters': {
            'hazardous': filter_hazardous,
            'max_miss_distance': max_miss_distance,
            'impact_risk': impact_risk
        }
    }
    
    return render(request, 'simulation/asteroid_list.html', context)

def asteroid_detail(request, neo_id):
    """Display detailed information about a specific asteroid"""
    asteroid = get_object_or_404(Asteroid, neo_id=neo_id)
    
    # Calculate collision data if not already stored
    if not asteroid.predicted_impact_latitude:
        from .collision_calculator import calculate_collision_location
        collision_data = calculate_collision_location(asteroid)
        
        # Update asteroid with collision data (always store, even for low probability)
        asteroid.predicted_impact_latitude = collision_data['predicted_impact_latitude']
        asteroid.predicted_impact_longitude = collision_data['predicted_impact_longitude']
        asteroid.predicted_impact_location = collision_data['predicted_impact_location']
        asteroid.impact_probability = collision_data['impact_probability']
        asteroid.impact_energy_megatons = collision_data['impact_energy_megatons']
        asteroid.crater_diameter_km = collision_data['crater_diameter_km']
        asteroid.save()
    
    # Force recalculation if probability is too low (for demonstration purposes)
    if asteroid.impact_probability < 0.02:
        from .collision_calculator import calculate_collision_location
        collision_data = calculate_collision_location(asteroid)
        
        # Update asteroid with new collision data
        asteroid.predicted_impact_latitude = collision_data['predicted_impact_latitude']
        asteroid.predicted_impact_longitude = collision_data['predicted_impact_longitude']
        asteroid.predicted_impact_location = collision_data['predicted_impact_location']
        asteroid.impact_probability = collision_data['impact_probability']
        asteroid.impact_energy_megatons = collision_data['impact_energy_megatons']
        asteroid.crater_diameter_km = collision_data['crater_diameter_km']
        asteroid.save()
    
    # Get detailed impact effects
    from .collision_calculator import get_impact_effects_data
    impact_effects = get_impact_effects_data(asteroid.impact_energy_megatons or 0)
    
    # Pre-compute percentage for templates/JS
    try:
        impact_probability_pct = round(float(asteroid.impact_probability or 0) * 100, 1)
    except Exception:
        impact_probability_pct = 0.0

    context = {
        'asteroid': asteroid,
        'impact_effects': impact_effects,
        'has_collision_data': bool(asteroid.predicted_impact_latitude),
        'impact_probability_pct': impact_probability_pct,
    }
    
    return render(request, 'simulation/asteroid_detail.html', context)

def apod_view(request):
    """Fetch and display NASA's Astronomy Picture of the Day"""
    import requests
    from django.conf import settings
    
    url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': settings.NASA_API_KEY
    }
    
    apod_data = None
    error_message = None
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        apod_data = response.json()
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching APOD: {str(e)}'
    
    context = {
        'apod': apod_data,
        'error': error_message,
    }
    
    return render(request, 'simulation/apod.html', context)


def simulator_view(request):
    """Interactive impact simulator page"""
    asteroid = None
    asteroid_id = request.GET.get('asteroid_id')
    
    if asteroid_id:
        try:
            asteroid = Asteroid.objects.get(neo_id=asteroid_id)
        except Asteroid.DoesNotExist:
            messages.warning(request, f'Asteroid with ID {asteroid_id} not found.')
    
    context = {
        'asteroid': asteroid
    }
    
    return render(request, 'simulation/simulator.html', context)


def fetch_earthquakes_view(request):
    """Fetch earthquakes from USGS and save to database"""
    import requests
    from .usgs_data import fetch_recent_earthquakes
    
    days = int(request.GET.get('days', 30))
    min_magnitude = float(request.GET.get('min_magnitude', 4.5))
    
    earthquakes_data = fetch_recent_earthquakes(days=days, min_magnitude=min_magnitude)
    
    if isinstance(earthquakes_data, dict) and 'error' in earthquakes_data:
        messages.error(request, f'Error fetching earthquakes: {earthquakes_data["error"]}')
        return redirect('earthquake_list')
    
    # Save earthquakes to database
    saved_count = 0
    for eq_data in earthquakes_data:
        try:
            eq_time = datetime.fromisoformat(eq_data['time'].replace('Z', '+00:00'))
            
            Earthquake.objects.update_or_create(
                usgs_id=eq_data['id'],
                defaults={
                    'magnitude': eq_data['magnitude'],
                    'place': eq_data['place'],
                    'time': eq_time,
                    'latitude': eq_data['latitude'],
                    'longitude': eq_data['longitude'],
                    'depth_km': eq_data['depth_km'],
                    'url': eq_data['url'],
                    'tsunami': eq_data['tsunami'],
                }
            )
            saved_count += 1
        except Exception as e:
            continue
    
    messages.success(request, f'Successfully fetched {saved_count} earthquakes from USGS!')
    return redirect('earthquake_list')


def earthquake_list(request):
    """Display list of earthquakes"""
    earthquakes = Earthquake.objects.all()
    
    # Filter by tsunami
    filter_tsunami = request.GET.get('tsunami')
    if filter_tsunami == 'true':
        earthquakes = earthquakes.filter(tsunami=True)
    elif filter_tsunami == 'false':
        earthquakes = earthquakes.filter(tsunami=False)
    
    # Filter by magnitude
    min_mag = request.GET.get('min_magnitude')
    if min_mag:
        earthquakes = earthquakes.filter(magnitude__gte=float(min_mag))
    
    context = {
        'earthquakes': earthquakes,
        'total_count': earthquakes.count(),
        'tsunami_count': Earthquake.objects.filter(tsunami=True).count(),
    }
    
    return render(request, 'simulation/earthquake_list.html', context)


def earthquake_detail(request, usgs_id):
    """Display detailed information about a specific earthquake"""
    earthquake = get_object_or_404(Earthquake, usgs_id=usgs_id)
    
    # Get location assessment
    from .usgs_data import assess_impact_location
    location_info = assess_impact_location(earthquake.latitude, earthquake.longitude)
    
    context = {
        'earthquake': earthquake,
        'location_info': location_info,
    }
    
    return render(request, 'simulation/earthquake_detail.html', context)


# ============ API ENDPOINTS ============

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, timedelta
from django.conf import settings
import requests
from .simulation_engine import run_full_simulation, calculate_impact_energy, estimate_crater_size
from .usgs_data import fetch_recent_earthquakes, assess_impact_location, get_nearby_earthquakes


@require_http_methods(["GET"])
def api_fetch_asteroid_data(request):
    """API endpoint to fetch asteroid data from NASA"""
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    
    # Default to next 7 days if not provided
    if not start_date:
        start_date = datetime.now().date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = start_date + timedelta(days=7)
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Fetch from NASA API
    url = f"{settings.NASA_API_BASE_URL}feed"
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'api_key': settings.NASA_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return JsonResponse({
            'success': True,
            'data': data,
            'count': data.get('element_count', 0)
        })
    
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_simulate_impact(request):
    """API endpoint to simulate asteroid impact"""
    try:
        data = json.loads(request.body)
        
        # Extract parameters
        diameter_km = float(data.get("diameter_km", 1.0))
        velocity_kmh = float(data.get("velocity_kmh", 50000))
        latitude = float(data.get("latitude", 0))
        longitude = float(data.get("longitude", 0))
        population_density = int(data.get("population_density", 100))
        
        # Assess location
        location_info = assess_impact_location(latitude, longitude)
        is_ocean = location_info['is_ocean_impact']
        
        # Run simulation
        simulation_results = run_full_simulation(
            diameter_km=diameter_km,
            velocity_kmh=velocity_kmh,
            latitude=latitude,
            longitude=longitude,
            is_ocean=is_ocean,
            population_density=population_density
        )
        
        # Add location assessment
        simulation_results['location_assessment'] = location_info
        
        return JsonResponse({
            'success': True,
            'simulation': simulation_results
        })
    
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid input: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_quick_impact_calc(request):
    """Quick impact energy and crater calculation"""
    try:
        diameter_m = float(request.GET.get("diameter_m", 100))
        velocity_mps = float(request.GET.get("velocity_mps", 20000))
        
        energy = calculate_impact_energy(diameter_m, velocity_mps)
        crater = estimate_crater_size(energy)
        
        return JsonResponse({
            'success': True,
            'diameter_m': diameter_m,
            'velocity_mps': velocity_mps,
            'impact_energy_megatons': energy,
            'crater_diameter_km': crater
        })
    
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid parameters: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
def api_fetch_earthquakes(request):
    """Fetch recent earthquake data from USGS"""
    days = int(request.GET.get("days", 30))
    min_magnitude = float(request.GET.get("min_magnitude", 4.5))
    
    earthquakes = fetch_recent_earthquakes(days=days, min_magnitude=min_magnitude)
    
    if isinstance(earthquakes, dict) and 'error' in earthquakes:
        return JsonResponse({
            'success': False,
            'error': earthquakes['error']
        }, status=500)
    
    return JsonResponse({
        'success': True,
        'count': len(earthquakes),
        'earthquakes': earthquakes
    })


@require_http_methods(["GET"])
def api_assess_location(request):
    """Assess impact location for seismic and tsunami risks"""
    try:
        latitude = float(request.GET.get("latitude"))
        longitude = float(request.GET.get("longitude"))
        
        assessment = assess_impact_location(latitude, longitude)
        
        # Get nearby earthquakes
        nearby_eq = get_nearby_earthquakes(latitude, longitude, radius_km=500)
        if not isinstance(nearby_eq, dict) or 'error' not in nearby_eq:
            assessment['nearby_earthquakes'] = {
                'count': len(nearby_eq),
                'earthquakes': nearby_eq[:5]  # Return top 5 closest
            }
        
        return JsonResponse({
            'success': True,
            'assessment': assessment
        })
    
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid coordinates: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
def api_asteroid_impact_potential(request, neo_id):
    """Calculate impact potential for a specific asteroid"""
    try:
        asteroid = Asteroid.objects.get(neo_id=neo_id)
        
        # Use average diameter
        diameter_km = (asteroid.estimated_diameter_min_km + asteroid.estimated_diameter_max_km) / 2
        velocity_kmh = asteroid.relative_velocity_kmh
        
        # Calculate basic impact parameters
        diameter_m = diameter_km * 1000
        velocity_mps = velocity_kmh / 3.6
        
        energy = calculate_impact_energy(diameter_m, velocity_mps)
        crater = estimate_crater_size(energy)
        
        return JsonResponse({
            'success': True,
            'asteroid': {
                'neo_id': asteroid.neo_id,
                'name': asteroid.name,
                'is_potentially_hazardous': asteroid.is_potentially_hazardous,
                'close_approach_date': asteroid.close_approach_date,
                'miss_distance_km': asteroid.miss_distance_km
            },
            'impact_potential': {
                'diameter_km': round(diameter_km, 3),
                'velocity_kmh': velocity_kmh,
                'impact_energy_megatons': energy,
                'crater_diameter_km': crater,
                'hiroshima_equivalent': round(energy / 0.015, 1)
            }
        })
    
    except Asteroid.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Asteroid not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def api_predict_impact_location(request):
    """ML-based prediction of impact location"""
    try:
        from .ml_predictor import get_location_predictor
        
        data = json.loads(request.body)
        
        velocity_kmh = float(data.get('velocity_kmh', 50000))
        diameter_km = float(data.get('diameter_km', 1.0))
        orbital_inclination = float(data.get('orbital_inclination', 0))
        eccentricity = float(data.get('eccentricity', 0.5))
        miss_distance_km = float(data.get('miss_distance_km', 100000))
        
        predictor = get_location_predictor()
        prediction = predictor.predict_impact_location(
            velocity_kmh=velocity_kmh,
            diameter_km=diameter_km,
            orbital_inclination=orbital_inclination,
            eccentricity=eccentricity,
            miss_distance_km=miss_distance_km
        )
        
        return JsonResponse({
            'success': True,
            'prediction': prediction,
            'input_parameters': {
                'velocity_kmh': velocity_kmh,
                'diameter_km': diameter_km,
                'orbital_inclination': orbital_inclination,
                'eccentricity': eccentricity,
                'miss_distance_km': miss_distance_km
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def api_predict_impact_date(request):
    """ML-based prediction of impact date"""
    try:
        from .ml_predictor import get_date_predictor
        
        data = json.loads(request.body)
        
        size_m = float(data.get('size_m', 100))
        velocity_kmh = float(data.get('velocity_kmh', 50000))
        miss_distance_km = float(data.get('miss_distance_km', 1000000))
        impact_probability = float(data.get('impact_probability_pct', 0.1))
        
        predictor = get_date_predictor()
        prediction = predictor.predict_days_until_impact(
            size_m=size_m,
            velocity_kmh=velocity_kmh,
            miss_distance_km=miss_distance_km,
            impact_probability_pct=impact_probability
        )
        
        return JsonResponse({
            'success': True,
            'prediction': prediction,
            'input_parameters': {
                'size_m': size_m,
                'velocity_kmh': velocity_kmh,
                'miss_distance_km': miss_distance_km,
                'impact_probability_pct': impact_probability
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_asteroid_ml_prediction(request, neo_id):
    """Get ML predictions for a specific asteroid"""
    try:
        from .ml_predictor import get_location_predictor, get_date_predictor
        
        asteroid = Asteroid.objects.get(neo_id=neo_id)
        
        diameter_km = (asteroid.estimated_diameter_min_km + asteroid.estimated_diameter_max_km) / 2
        diameter_m = diameter_km * 1000
        velocity_kmh = asteroid.relative_velocity_kmh
        miss_distance_km = asteroid.miss_distance_km
        
        # Predict location
        location_predictor = get_location_predictor()
        location_pred = location_predictor.predict_impact_location(
            velocity_kmh=velocity_kmh,
            diameter_km=diameter_km,
            miss_distance_km=miss_distance_km
        )
        
        # Predict date
        date_predictor = get_date_predictor()
        date_pred = date_predictor.predict_days_until_impact(
            size_m=diameter_m,
            velocity_kmh=velocity_kmh,
            miss_distance_km=miss_distance_km,
            impact_probability_pct=1.0 if asteroid.is_potentially_hazardous else 0.1
        )
        
        return JsonResponse({
            'success': True,
            'asteroid': {
                'neo_id': asteroid.neo_id,
                'name': asteroid.name,
                'is_potentially_hazardous': asteroid.is_potentially_hazardous
            },
            'ml_predictions': {
                'impact_location': location_pred,
                'impact_timing': date_pred
            }
        })
    
    except Asteroid.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Asteroid not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_keplerian_trajectory(request):
    """
    Calculate asteroid trajectory using Keplerian orbital mechanics.
    Accepts orbital elements and returns position/velocity over time.
    """
    try:
        from .keplerian_orbit import KeplerianOrbit
        from datetime import datetime, timedelta
        
        data = json.loads(request.body)
        
        # Extract orbital elements
        a = float(data.get('semi_major_axis_au', 2.5))
        e = float(data.get('eccentricity', 0.2))
        i = float(data.get('inclination_deg', 10.0))
        Omega = float(data.get('ascending_node_deg', 0.0))
        omega = float(data.get('periapsis_arg_deg', 0.0))
        M0 = float(data.get('mean_anomaly_deg', 0.0))
        
        # Time parameters
        duration_days = int(data.get('duration_days', 365))
        time_steps = int(data.get('time_steps', 50))
        
        # Create orbit
        orbit = KeplerianOrbit(a, e, i, Omega, omega, M0)
        
        # Calculate trajectory
        trajectory = []
        start_time = datetime.now()
        step_size = duration_days / time_steps
        
        for step in range(time_steps + 1):
            current_time = start_time + timedelta(days=step * step_size)
            pos = orbit.position_at_time(current_time)
            vel = orbit.velocity_at_time(current_time)
            earth_dist = orbit.earth_distance_at_time(current_time)
            
            trajectory.append({
                'time': current_time.isoformat(),
                'days_from_now': step * step_size,
                'position': {
                    'x_km': pos['x'],
                    'y_km': pos['y'],
                    'z_km': pos['z'],
                    'distance_from_sun_au': pos['distance_from_sun_au']
                },
                'velocity_km_s': vel['speed_km_s'],
                'earth_distance_km': earth_dist['distance_km'],
                'earth_distance_au': earth_dist['distance_au']
            })
        
        # Find closest approach
        closest_approach = orbit.find_closest_approach(start_time, duration_days)
        
        # Get orbital summary
        orbital_summary = orbit.get_orbital_summary()
        
        # Assess limitations
        from .keplerian_orbit import assess_keplerian_limitations
        limitations = assess_keplerian_limitations(orbit, duration_days / 365.25)
        
        return JsonResponse({
            'success': True,
            'orbital_elements': {
                'semi_major_axis_au': a,
                'eccentricity': e,
                'inclination_deg': i,
                'ascending_node_deg': Omega,
                'periapsis_arg_deg': omega,
                'mean_anomaly_deg': M0
            },
            'orbital_summary': orbital_summary,
            'trajectory': trajectory,
            'closest_approach': {
                'time': closest_approach['closest_approach_time'].isoformat(),
                'distance_km': closest_approach['closest_distance_km'],
                'distance_au': closest_approach['closest_distance_au'],
                'distance_earth_radii': closest_approach['closest_distance_earth_radii'],
                'relative_velocity_km_h': closest_approach['relative_velocity_km_h'],
                'impact_probability': closest_approach['impact_probability']
            },
            'model_limitations': limitations
        })
    
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid input: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_asteroid_keplerian_analysis(request, neo_id):
    """
    Get Keplerian orbital analysis for a specific asteroid.
    Calculates real-time impact predictions using orbital mechanics.
    """
    try:
        from .keplerian_orbit import assess_keplerian_limitations
        from datetime import datetime, timedelta
        
        asteroid = Asteroid.objects.get(neo_id=neo_id)
        
        # Check if orbital elements are available
        if not asteroid.has_orbital_elements():
            return JsonResponse({
                'success': False,
                'error': 'Orbital elements not available for this asteroid',
                'has_orbital_data': False
            })
        
        # Get Keplerian orbit
        orbit = asteroid.get_keplerian_orbit()
        
        # Get current position and velocity
        now = datetime.now()
        current_pos = orbit.position_at_time(now)
        current_vel = orbit.velocity_at_time(now)
        current_earth_dist = orbit.earth_distance_at_time(now)
        
        # Find closest approach in next year
        closest_approach = orbit.find_closest_approach(now, duration_days=365)
        
        # Get orbital summary
        orbital_summary = orbit.get_orbital_summary()
        
        # Assess model limitations
        limitations = assess_keplerian_limitations(orbit, 1.0)  # 1 year prediction
        
        # Calculate impact energy if impact occurs
        diameter_km = (asteroid.estimated_diameter_min_km + asteroid.estimated_diameter_max_km) / 2
        from .simulation_engine import calculate_impact_energy, estimate_crater_size
        
        diameter_m = diameter_km * 1000
        velocity_mps = closest_approach['relative_velocity_km_h'] / 3.6
        impact_energy = calculate_impact_energy(diameter_m, velocity_mps)
        crater_size = estimate_crater_size(impact_energy)
        
        return JsonResponse({
            'success': True,
            'has_orbital_data': True,
            'asteroid': {
                'neo_id': asteroid.neo_id,
                'name': asteroid.name,
                'is_potentially_hazardous': asteroid.is_potentially_hazardous,
                'diameter_km': diameter_km
            },
            'orbital_summary': orbital_summary,
            'current_state': {
                'time': now.isoformat(),
                'position': current_pos,
                'velocity_km_s': current_vel['speed_km_s'],
                'earth_distance_km': current_earth_dist['distance_km'],
                'earth_distance_au': current_earth_dist['distance_au']
            },
            'closest_approach': {
                'time': closest_approach['closest_approach_time'].isoformat(),
                'distance_km': closest_approach['closest_distance_km'],
                'distance_au': closest_approach['closest_distance_au'],
                'distance_earth_radii': closest_approach['closest_distance_earth_radii'],
                'relative_velocity_km_h': closest_approach['relative_velocity_km_h'],
                'impact_probability': closest_approach['impact_probability'],
                'days_until_approach': (closest_approach['closest_approach_time'] - now).days
            },
            'impact_potential': {
                'impact_energy_megatons': impact_energy,
                'crater_diameter_km': crater_size,
                'hiroshima_equivalent': round(impact_energy / 0.015, 1)
            },
            'model_assessment': limitations
        })
    
    except Asteroid.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Asteroid not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_realtime_impact_prediction(request):
    """
    Real-time impact prediction using Keplerian orbital mechanics.
    Continuously updates impact probability and trajectory.
    """
    try:
        from .keplerian_orbit import KeplerianOrbit, calculate_impact_probability
        from datetime import datetime, timedelta
        
        data = json.loads(request.body)
        
        # Extract parameters
        a = float(data.get('semi_major_axis_au'))
        e = float(data.get('eccentricity'))
        i = float(data.get('inclination_deg'))
        Omega = float(data.get('ascending_node_deg', 0))
        omega = float(data.get('periapsis_arg_deg', 0))
        M0 = float(data.get('mean_anomaly_deg', 0))
        diameter_km = float(data.get('diameter_km', 1.0))
        
        # Create orbit
        orbit = KeplerianOrbit(a, e, i, Omega, omega, M0)
        
        # Calculate predictions for the requested time horizon
        now = datetime.now()
        predictions = []
        
        # Get the requested duration or default to 365 days
        duration_days = int(data.get('duration_days', 365))
        
        # Generate time horizons: 1/4, 1/2, and full duration
        time_horizons = [
            max(1, duration_days // 4),  # 25%
            max(1, duration_days // 2),  # 50%
            duration_days                # 100%
        ]
        
        for days in time_horizons:
            closest = orbit.find_closest_approach(now, duration_days=days, initial_step_days=max(1, days // 20))
            
            predictions.append({
                'time_horizon_days': days,
                'closest_approach_time': closest['closest_approach_time'].isoformat(),
                'distance_km': closest['closest_distance_km'],
                'distance_earth_radii': closest['closest_distance_earth_radii'],
                'impact_probability': closest['impact_probability'],
                'relative_velocity_km_h': closest['relative_velocity_km_h']
            })
        
        # Get overall orbital summary
        orbital_summary = orbit.get_orbital_summary()
        
        # Calculate potential impact effects
        from .simulation_engine import calculate_impact_energy, estimate_crater_size, calculate_blast_radius
        
        # Use velocity from closest approach in next year
        closest_year = orbit.find_closest_approach(now, duration_days=365)
        diameter_m = diameter_km * 1000
        velocity_mps = closest_year['relative_velocity_km_h'] / 3.6
        
        impact_energy = calculate_impact_energy(diameter_m, velocity_mps)
        crater_size = estimate_crater_size(impact_energy)
        blast_radii = calculate_blast_radius(impact_energy)
        
        return JsonResponse({
            'success': True,
            'timestamp': now.isoformat(),
            'orbital_summary': orbital_summary,
            'predictions': predictions,
            'impact_scenario': {
                'diameter_km': diameter_km,
                'impact_energy_megatons': impact_energy,
                'crater_diameter_km': crater_size,
                'blast_effects': blast_radii,
                'hiroshima_equivalent': round(impact_energy / 0.015, 1)
            }
        })
    
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid input: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
