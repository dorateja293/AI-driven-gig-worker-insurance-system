import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/insurex')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # OpenWeather API
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')

    # Insurance Business Logic Constants
    BASE_PREMIUM = 25  # Base rate in rupees

    # Claim Thresholds
    THRESHOLDS = {
        'extreme_heat': {
            'temp_celsius': 43,
            'min_duration_hours': 2,
            'payout': 200
        },
        'heavy_rain': {
            'rainfall_mm': 50,
            'window_hours': 3,
            'payout': 200
        },
        'platform_outage': {
            'downtime_minutes': 30,
            'payout': 150
        },
        'severe_smog': {
            'aqi_level': 450,
            'duration_hours': 4,
            'payout': 100
        },
        'internet_blackout': {
            'downtime_minutes': 60,
            'payout': 120
        }
    }

    # Fraud Detection Thresholds
    FRAUD_THRESHOLDS = {
        'low': 0.3,      # Auto-approve
        'medium': 0.6,   # Delayed approval
        'high': 0.8      # Flag and hold
    }

    # Zone Risk Profiles (mocked historical data)
    ZONE_RISK_PROFILES = {
        'Zone-A': {
            'rain_frequency': 12,  # rainy days per month
            'heat_days': 8,        # days > 43°C per month
            'zone_risk': 0.6,      # flood/waterlog risk (0-1)
            'seasonal_factor': 1.2  # current season multiplier
        },
        'Zone-B': {
            'rain_frequency': 8,
            'heat_days': 15,
            'zone_risk': 0.4,
            'seasonal_factor': 1.3
        },
        'Zone-C': {
            'rain_frequency': 5,
            'heat_days': 10,
            'zone_risk': 0.3,
            'seasonal_factor': 1.0
        },
        'Zone-D': {
            'rain_frequency': 15,
            'heat_days': 5,
            'zone_risk': 0.7,
            'seasonal_factor': 1.1
        }
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
