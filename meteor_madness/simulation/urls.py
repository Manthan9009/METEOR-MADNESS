from django.urls import path
from . import views

urlpatterns = [
    # Web Pages
    path('', views.home, name='home'),
    path('asteroids/', views.asteroid_list, name='asteroid_list'),
    path('asteroids/fetch/', views.fetch_asteroids, name='fetch_asteroids'),
    path('asteroids/<str:neo_id>/', views.asteroid_detail, name='asteroid_detail'),
    path('earthquakes/', views.earthquake_list, name='earthquake_list'),
    path('earthquakes/fetch/', views.fetch_earthquakes_view, name='fetch_earthquakes'),
    path('earthquakes/<str:usgs_id>/', views.earthquake_detail, name='earthquake_detail'),
    path('apod/', views.apod_view, name='apod'),
    path('simulator/', views.simulator_view, name='simulator'),
    
    # API Endpoints
    path('api/asteroids/', views.api_fetch_asteroid_data, name='api_fetch_asteroids'),
    path('api/simulate/', views.api_simulate_impact, name='api_simulate_impact'),
    path('api/impact-calc/', views.api_quick_impact_calc, name='api_impact_calc'),
    path('api/earthquakes/', views.api_fetch_earthquakes, name='api_earthquakes'),
    path('api/assess-location/', views.api_assess_location, name='api_assess_location'),
    path('api/asteroids/<str:neo_id>/impact-potential/', views.api_asteroid_impact_potential, name='api_asteroid_impact_potential'),
    
    # ML Prediction Endpoints
    path('api/ml/predict-location/', views.api_predict_impact_location, name='api_ml_predict_location'),
    path('api/ml/predict-date/', views.api_predict_impact_date, name='api_ml_predict_date'),
    path('api/ml/asteroids/<str:neo_id>/predictions/', views.api_asteroid_ml_prediction, name='api_ml_asteroid_predictions'),
    
    # Keplerian Orbital Mechanics Endpoints
    path('api/keplerian/trajectory/', views.api_keplerian_trajectory, name='api_keplerian_trajectory'),
    path('api/keplerian/asteroids/<str:neo_id>/analysis/', views.api_asteroid_keplerian_analysis, name='api_keplerian_analysis'),
    path('api/keplerian/realtime-impact/', views.api_realtime_impact_prediction, name='api_realtime_impact'),
]
