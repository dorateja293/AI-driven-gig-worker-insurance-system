import requests
from datetime import datetime
from flask import current_app
from app import db
from app.models import Event
from app.services.queue_service import push_event_to_queue

def poll_weather():
    """
    Poll weather data from OpenWeather API
    Check against thresholds and create events if breached
    """
    try:
        print(f"[{datetime.utcnow()}] Polling weather data...")

        api_key = current_app.config.get('OPENWEATHER_API_KEY')
        if not api_key:
            print("OpenWeather API key not configured, skipping weather polling")
            return

        # Get zone profiles to check weather for each zone
        zone_profiles = current_app.config['ZONE_RISK_PROFILES']
        thresholds = current_app.config['THRESHOLDS']

        # City mappings for zones (you can customize this)
        zone_city_map = {
            'Zone-A': 'Hyderabad',
            'Zone-B': 'Mumbai',
            'Zone-C': 'Delhi',
            'Zone-D': 'Bangalore'
        }

        for zone, city in zone_city_map.items():
            try:
                # Fetch weather data from OpenWeather API
                url = f"http://api.openweathermap.org/data/2.5/weather"
                params = {
                    'q': city,
                    'appid': api_key,
                    'units': 'metric'
                }

                response = requests.get(url, params=params, timeout=10)
                if response.status_code != 200:
                    print(f"Failed to fetch weather for {city}: {response.status_code}")
                    continue

                data = response.json()

                # Extract temperature
                temp = data['main']['temp']
                print(f"{zone} ({city}): Temperature = {temp}°C")

                # Check extreme heat threshold
                heat_threshold = thresholds['extreme_heat']['temp_celsius']
                if temp >= heat_threshold:
                    # Threshold breached - create event
                    print(f"ALERT: Extreme heat detected in {zone}: {temp}°C")

                    # Check if event already exists for this zone in the last hour
                    from datetime import timedelta
                    recent_event = Event.query.filter(
                        Event.zone == zone,
                        Event.event_type == 'extreme_heat',
                        Event.detected_at >= datetime.utcnow() - timedelta(hours=1)
                    ).first()

                    if not recent_event:
                        # Create new event
                        event = Event(
                            zone=zone,
                            event_type='extreme_heat',
                            trigger_value=f"{temp}°C",
                            duration=2.5,  # Default duration
                            detected_at=datetime.utcnow()
                        )
                        db.session.add(event)
                        db.session.commit()

                        print(f"Created event {event.id} for {zone}")

                        # Push to queue for claim processing
                        push_event_to_queue(event.id)
                        print(f"Pushed event {event.id} to queue")

                # Check for heavy rain (if available in API)
                if 'rain' in data and '3h' in data['rain']:
                    rainfall = data['rain']['3h']
                    rain_threshold = thresholds['heavy_rain']['rainfall_mm']

                    if rainfall >= rain_threshold:
                        print(f"ALERT: Heavy rain detected in {zone}: {rainfall}mm")

                        # Check if event already exists
                        from datetime import timedelta
                        recent_event = Event.query.filter(
                            Event.zone == zone,
                            Event.event_type == 'heavy_rain',
                            Event.detected_at >= datetime.utcnow() - timedelta(hours=1)
                        ).first()

                        if not recent_event:
                            event = Event(
                                zone=zone,
                                event_type='heavy_rain',
                                trigger_value=f"{rainfall}mm",
                                duration=3.0,
                                detected_at=datetime.utcnow()
                            )
                            db.session.add(event)
                            db.session.commit()

                            push_event_to_queue(event.id)
                            print(f"Created and queued heavy rain event {event.id}")

            except Exception as e:
                print(f"Error polling weather for {zone}: {e}")
                continue

        print(f"Weather polling completed at {datetime.utcnow()}")

    except Exception as e:
        print(f"Error in weather polling: {e}")
        db.session.rollback()
