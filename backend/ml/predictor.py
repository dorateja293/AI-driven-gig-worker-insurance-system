"""
MODULE 3: Disruption Prediction (Basic Forecast)

Predicts likelihood of weather disruptions using simple moving averages.
Provides recommendations for workers on whether to buy insurance.
"""

import statistics


def predict_disruption(last_7_days_weather):
    """
    Predict disruption risk based on recent weather patterns.

    Args:
        last_7_days_weather (dict): {
            "temperatures": list of floats (°C),
            "rainfall": list of floats (mm)
        }

    Returns:
        dict: {
            "heat_risk": float (0-1),
            "rain_risk": float (0-1),
            "overall_risk": float (0-1),
            "recommendation": str ("BUY_POLICY" | "SAFE"),
            "forecast": dict
        }
    """
    temperatures = last_7_days_weather.get('temperatures', [])
    rainfall = last_7_days_weather.get('rainfall', [])

    # Calculate moving averages
    avg_temp = statistics.mean(temperatures) if temperatures else 0
    avg_rain = statistics.mean(rainfall) if rainfall else 0

    # Calculate max values
    max_temp = max(temperatures) if temperatures else 0
    max_rain = max(rainfall) if rainfall else 0

    # Heat risk calculation
    # High heat if avg > 40°C or max > 43°C
    heat_risk = 0.0
    if avg_temp > 40:
        heat_risk += 0.5
    if max_temp > 43:
        heat_risk += 0.5
    elif max_temp > 40:
        heat_risk += 0.3

    # Additional gradual increase
    if avg_temp > 35:
        heat_risk += min((avg_temp - 35) / 10, 0.3)

    # Rain risk calculation
    # High rain if avg > 30mm or max > 50mm
    rain_risk = 0.0
    if avg_rain > 30:
        rain_risk += 0.5
    if max_rain > 50:
        rain_risk += 0.5
    elif max_rain > 30:
        rain_risk += 0.3

    # Additional gradual increase
    if avg_rain > 15:
        rain_risk += min((avg_rain - 15) / 30, 0.3)

    # Clamp risks between 0 and 1
    heat_risk = max(0.0, min(1.0, heat_risk))
    rain_risk = max(0.0, min(1.0, rain_risk))

    # Overall risk (weighted average)
    overall_risk = max(heat_risk, rain_risk)  # Take the higher risk

    # Recommendation
    if overall_risk > 0.5:
        recommendation = "BUY_POLICY"
        message = "High disruption risk detected. Insurance recommended."
    elif overall_risk > 0.3:
        recommendation = "CONSIDER_POLICY"
        message = "Moderate risk. Consider purchasing insurance for protection."
    else:
        recommendation = "SAFE"
        message = "Low risk currently. You may skip insurance for now."

    # Calculate trend (is it getting worse?)
    temp_trend = "INCREASING" if len(temperatures) >= 3 and temperatures[-1] > temperatures[0] else "STABLE"
    rain_trend = "INCREASING" if len(rainfall) >= 3 and rainfall[-1] > rainfall[0] else "STABLE"

    return {
        "heat_risk": round(heat_risk, 3),
        "rain_risk": round(rain_risk, 3),
        "overall_risk": round(overall_risk, 3),
        "recommendation": recommendation,
        "message": message,
        "forecast": {
            "avg_temperature": round(avg_temp, 1),
            "max_temperature": round(max_temp, 1),
            "avg_rainfall": round(avg_rain, 1),
            "max_rainfall": round(max_rain, 1),
            "temperature_trend": temp_trend,
            "rainfall_trend": rain_trend
        }
    }


def predict_next_7_days(historical_data):
    """
    Simple forecast for next 7 days based on historical patterns.
    Uses basic trend analysis - in production, use time series models.

    Args:
        historical_data (dict): {
            "temperatures": list of last 30 days temps,
            "rainfall": list of last 30 days rainfall
        }

    Returns:
        dict: Predicted weather for next 7 days
    """
    temps = historical_data.get('temperatures', [])
    rain = historical_data.get('rainfall', [])

    if not temps or not rain:
        return {"error": "Insufficient historical data"}

    # Simple moving average for prediction
    avg_temp = statistics.mean(temps[-7:])  # Last week average
    avg_rain = statistics.mean(rain[-7:])

    # Calculate trend
    if len(temps) >= 14:
        recent_avg = statistics.mean(temps[-7:])
        older_avg = statistics.mean(temps[-14:-7])
        temp_delta = (recent_avg - older_avg) / 7  # Change per day
    else:
        temp_delta = 0

    if len(rain) >= 14:
        recent_avg = statistics.mean(rain[-7:])
        older_avg = statistics.mean(rain[-14:-7])
        rain_delta = (recent_avg - older_avg) / 7
    else:
        rain_delta = 0

    # Predict next 7 days
    predicted_temps = []
    predicted_rain = []

    for day in range(1, 8):
        predicted_temp = avg_temp + (temp_delta * day)
        predicted_rainfall = max(0, avg_rain + (rain_delta * day))

        predicted_temps.append(round(predicted_temp, 1))
        predicted_rain.append(round(predicted_rainfall, 1))

    return {
        "predicted_temperatures": predicted_temps,
        "predicted_rainfall": predicted_rain,
        "confidence": "LOW",  # Simple model = low confidence
        "note": "Basic trend forecast. Actual weather may vary significantly."
    }


def get_insurance_urgency(last_7_days_weather):
    """
    Get urgency score for buying insurance (0-10 scale).

    Args:
        last_7_days_weather (dict): Recent weather data

    Returns:
        dict: {
            "urgency_score": int (0-10),
            "urgency_level": str,
            "action": str
        }
    """
    prediction = predict_disruption(last_7_days_weather)

    overall_risk = prediction['overall_risk']

    # Convert to 0-10 scale
    urgency_score = int(overall_risk * 10)

    if urgency_score >= 7:
        urgency_level = "CRITICAL"
        action = "Buy insurance immediately - high disruption risk"
    elif urgency_score >= 5:
        urgency_level = "HIGH"
        action = "Strongly recommend buying insurance"
    elif urgency_score >= 3:
        urgency_level = "MODERATE"
        action = "Consider insurance for protection"
    else:
        urgency_level = "LOW"
        action = "Insurance optional - low risk currently"

    return {
        "urgency_score": urgency_score,
        "urgency_level": urgency_level,
        "action": action,
        "prediction_details": prediction
    }


if __name__ == "__main__":
    # Test the predictor
    print("=== Disruption Predictor Test ===\n")

    # Test 1: High heat risk
    result = predict_disruption({
        "temperatures": [41, 42, 43, 44, 45, 44, 43],
        "rainfall": [0, 0, 2, 1, 0, 0, 3]
    })
    print(f"High Heat Risk: {result}")

    # Test 2: High rain risk
    result = predict_disruption({
        "temperatures": [32, 33, 31, 30, 32, 33, 31],
        "rainfall": [45, 52, 60, 48, 55, 50, 58]
    })
    print(f"\nHigh Rain Risk: {result}")

    # Test 3: Safe conditions
    result = predict_disruption({
        "temperatures": [28, 29, 30, 29, 28, 30, 29],
        "rainfall": [5, 8, 3, 0, 2, 6, 4]
    })
    print(f"\nSafe Conditions: {result}")

    # Test 4: Urgency scoring
    result = get_insurance_urgency({
        "temperatures": [42, 43, 44, 45, 46, 45, 44],
        "rainfall": [0, 0, 0, 0, 0, 0, 0]
    })
    print(f"\nInsurance Urgency: {result}")
