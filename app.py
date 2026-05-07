import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def get_health_advice(temp, humidity, wind, aqi):
    advice = []
    if temp > 30:
        advice.append("High heat alert: Stay hydrated and seek shade.")
    elif temp < 10:
        advice.append("Cold weather: Dress in warm layers.")
    
    if humidity > 75:
        advice.append("High humidity: May cause respiratory discomfort.")
    
    if wind > 25:
        advice.append("High winds: Be cautious outdoors.")
    
    if aqi > 100:
        advice.append("Poor air quality: Avoid prolonged outdoor activities.")
    elif aqi > 50:
        advice.append("Moderate air quality: Sensitive groups should take precautions.")
    
    if not advice:
        advice.append("Weather conditions are moderate. Stay healthy!")
    
    return " ".join(advice)

@app.route('/weather')
def weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'No city provided'}), 400
    
    try:
        # Geocoding API to get lat/long
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url).json()
        
        if not geo_resp.get('results'):
            return jsonify({'error': 'City not found'}), 404
        
        location = geo_resp['results'][0]
        lat = location['latitude']
        lon = location['longitude']
        city_name = location['name']
        
        # Forecast API for current weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        weather_resp = requests.get(weather_url).json()
        
        # Air Quality API
        aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
        aqi_resp = requests.get(aqi_url).json()
        
        current_w = weather_resp['current']
        current_a = aqi_resp['current']
        
        temp = current_w['temperature_2m']
        humidity = current_w['relative_humidity_2m']
        wind = current_w['wind_speed_10m']
        aqi = current_a['us_aqi']
        
        advice = get_health_advice(temp, humidity, wind, aqi)
        
        return jsonify({
            'city': city_name,
            'temperature': temp,
            'humidity': humidity,
            'wind_speed': wind,
            'aqi': aqi,
            'advice': advice
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
