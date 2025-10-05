"""
Machine Learning Model for Impact Location Prediction
Uses asteroid trajectory data to predict potential impact coordinates
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import pickle
import os


class ImpactLocationPredictor:
    """Predicts impact location based on asteroid parameters"""
    
    def __init__(self):
        self.latitude_model = None
        self.longitude_model = None
        self.is_trained = False
        
    def generate_training_data(self, n_samples=1000):
        """
        Generate synthetic training data based on orbital mechanics
        In production, this would use real historical asteroid data
        """
        np.random.seed(42)
        
        # Features: [velocity_kmh, diameter_km, orbital_inclination, eccentricity, miss_distance_km]
        velocities = np.random.uniform(20000, 100000, n_samples)
        diameters = np.random.uniform(0.01, 10, n_samples)
        inclinations = np.random.uniform(-90, 90, n_samples)  # degrees
        eccentricities = np.random.uniform(0, 0.9, n_samples)
        miss_distances = np.random.uniform(0, 1000000, n_samples)
        
        X = np.column_stack([velocities, diameters, inclinations, eccentricities, miss_distances])
        
        # Target: [latitude, longitude]
        # Simulate impact locations based on orbital parameters
        # Higher inclination -> higher latitude potential
        # Eccentricity and velocity affect trajectory
        latitudes = (inclinations * 0.8 + 
                    np.random.normal(0, 10, n_samples) + 
                    (eccentricities - 0.5) * 20)
        latitudes = np.clip(latitudes, -90, 90)
        
        # Longitude is more random but influenced by velocity and eccentricity
        longitudes = (np.random.uniform(-180, 180, n_samples) + 
                     (velocities / 1000 - 50) * 0.5 +
                     eccentricities * 30)
        longitudes = np.clip(longitudes, -180, 180)
        
        return X, latitudes, longitudes
    
    def train(self):
        """Train the ML models"""
        print("Training impact location prediction models...")
        
        # Generate training data
        X, y_lat, y_lon = self.generate_training_data(n_samples=1000)
        
        # Train latitude predictor
        self.latitude_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.latitude_model.fit(X, y_lat)
        
        # Train longitude predictor
        self.longitude_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.longitude_model.fit(X, y_lon)
        
        self.is_trained = True
        print("Models trained successfully!")
        
        return self
    
    def predict_impact_location(self, velocity_kmh, diameter_km, 
                               orbital_inclination=0, eccentricity=0.5, 
                               miss_distance_km=100000):
        """
        Predict potential impact location
        
        Args:
            velocity_kmh: Asteroid velocity in km/h
            diameter_km: Asteroid diameter in km
            orbital_inclination: Orbital inclination in degrees (-90 to 90)
            eccentricity: Orbital eccentricity (0 to 1)
            miss_distance_km: Current miss distance in km
        
        Returns:
            dict with predicted latitude, longitude, and confidence
        """
        if not self.is_trained:
            self.train()
        
        # Prepare features
        features = np.array([[velocity_kmh, diameter_km, orbital_inclination, 
                            eccentricity, miss_distance_km]])
        
        # Predict
        predicted_lat = self.latitude_model.predict(features)[0]
        predicted_lon = self.longitude_model.predict(features)[0]
        
        # Clip to valid ranges
        predicted_lat = np.clip(predicted_lat, -90, 90)
        predicted_lon = np.clip(predicted_lon, -180, 180)
        
        # Calculate confidence based on feature importance
        # In production, use proper uncertainty quantification
        confidence = self._calculate_confidence(features)
        
        return {
            'latitude': round(float(predicted_lat), 4),
            'longitude': round(float(predicted_lon), 4),
            'confidence': round(float(confidence), 2),
            'confidence_level': self._get_confidence_level(confidence)
        }
    
    def _calculate_confidence(self, features):
        """Calculate prediction confidence (0-100%)"""
        # Simplified confidence based on feature values
        velocity = features[0][0]
        diameter = features[0][1]
        miss_distance = features[0][4]
        
        # Higher confidence for:
        # - Moderate velocities (easier to track)
        # - Larger asteroids (better detection)
        # - Smaller miss distances (more data available)
        
        velocity_score = 100 - abs(velocity - 50000) / 1000
        diameter_score = min(diameter * 10, 100)
        distance_score = max(100 - miss_distance / 10000, 0)
        
        confidence = (velocity_score + diameter_score + distance_score) / 3
        return np.clip(confidence, 0, 100)
    
    def _get_confidence_level(self, confidence):
        """Convert confidence percentage to level"""
        if confidence >= 80:
            return 'Very High'
        elif confidence >= 60:
            return 'High'
        elif confidence >= 40:
            return 'Moderate'
        elif confidence >= 20:
            return 'Low'
        else:
            return 'Very Low'
    
    def save_model(self, filepath='impact_predictor.pkl'):
        """Save trained model to file"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'latitude_model': self.latitude_model,
            'longitude_model': self.longitude_model,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='impact_predictor.pkl'):
        """Load trained model from file"""
        if not os.path.exists(filepath):
            print(f"Model file not found. Training new model...")
            return self.train()
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.latitude_model = model_data['latitude_model']
        self.longitude_model = model_data['longitude_model']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {filepath}")
        return self


class ImpactDatePredictor:
    """Predicts days until potential impact"""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
    
    def generate_training_data(self, n_samples=500):
        """Generate synthetic training data for impact date prediction"""
        np.random.seed(42)
        
        # Features: [size_m, velocity_kmh, miss_distance_km, impact_probability_%]
        sizes = np.random.uniform(10, 1000, n_samples)
        velocities = np.random.uniform(15000, 100000, n_samples)
        distances = np.random.uniform(100000, 10000000, n_samples)
        probabilities = np.random.uniform(0.001, 5.0, n_samples)
        
        X = np.column_stack([sizes, velocities, distances, probabilities])
        
        # Target: days until impact
        # Closer distance and higher probability = sooner impact
        days = (distances / 10000) - (probabilities * 100) + np.random.normal(0, 50, n_samples)
        days = np.clip(days, 1, 36500)  # 1 day to 100 years
        
        return X, days
    
    def train(self):
        """Train the impact date prediction model"""
        print("Training impact date prediction model...")
        
        X, y = self.generate_training_data()
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        self.is_trained = True
        print("Impact date model trained successfully!")
        
        return self
    
    def predict_days_until_impact(self, size_m, velocity_kmh, 
                                  miss_distance_km, impact_probability_pct=0.1):
        """
        Predict days until potential impact
        
        Args:
            size_m: Asteroid size in meters
            velocity_kmh: Velocity in km/h
            miss_distance_km: Current miss distance
            impact_probability_pct: Impact probability percentage
        
        Returns:
            dict with predicted days and date
        """
        if not self.is_trained:
            self.train()
        
        features = np.array([[size_m, velocity_kmh, miss_distance_km, impact_probability_pct]])
        
        predicted_days = self.model.predict(features)[0]
        predicted_days = max(1, predicted_days)  # At least 1 day
        
        from datetime import datetime, timedelta
        impact_date = datetime.now() + timedelta(days=predicted_days)
        
        return {
            'days_until_impact': round(float(predicted_days), 1),
            'predicted_impact_date': impact_date.strftime('%Y-%m-%d'),
            'years': round(predicted_days / 365.25, 2),
            'risk_level': self._assess_risk(predicted_days, impact_probability_pct)
        }
    
    def _assess_risk(self, days, probability):
        """Assess risk level based on timeframe and probability"""
        if days < 365 and probability > 1.0:
            return 'Critical'
        elif days < 1825 and probability > 0.5:  # 5 years
            return 'High'
        elif days < 3650 and probability > 0.1:  # 10 years
            return 'Moderate'
        else:
            return 'Low'


# Global predictor instances
_location_predictor = None
_date_predictor = None


def get_location_predictor():
    """Get or create location predictor instance"""
    global _location_predictor
    if _location_predictor is None:
        _location_predictor = ImpactLocationPredictor()
        _location_predictor.train()
    return _location_predictor


def get_date_predictor():
    """Get or create date predictor instance"""
    global _date_predictor
    if _date_predictor is None:
        _date_predictor = ImpactDatePredictor()
        _date_predictor.train()
    return _date_predictor
