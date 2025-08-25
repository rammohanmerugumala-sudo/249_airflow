#import requests
from datetime import datetime, timedelta

def get_past_seven_days_dates():
    today = datetime.utcnow().date()
    dates = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    return dates

def fetch_weather_data(lat, lon):
    dates = get_past_seven_days_dates()
    start_date = dates[0]
    end_date = dates[-1]

    url = ("your_api_key"
        #f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&timezone=UTC"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def analyze_weather(data):
    dates = data['daily']['time']
    max_temps = data['daily']['temperature_2m_max']
    min_temps = data['daily']['temperature_2m_min']

    print("Weather records for last 7 days:")
    for d, max_t, min_t in zip(dates, max_temps, min_temps):
        print(f"Date: {d}, Max Temp: {max_t if max_t is not None else 'N/A'}°C, Min Temp: {min_t if min_t is not None else 'N/A'}°C")

    # Filter out None values before computing max/min
    filtered_max_temps = [(t, dates[i]) for i, t in enumerate(max_temps) if t is not None]
    filtered_min_temps = [(t, dates[i]) for i, t in enumerate(min_temps) if t is not None]

    if not filtered_max_temps or not filtered_min_temps:
        print("Insufficient data to analyze temperatures.")
        return

    highest_temp, date_highest = max(filtered_max_temps, key=lambda x: x[0])
    lowest_temp, date_lowest = min(filtered_min_temps, key=lambda x: x[0])

    print(f"\nHighest temperature recorded: {highest_temp}°C on {date_highest}")
    print(f"Lowest temperature recorded: {lowest_temp}°C on {date_lowest}")

    # Spot anomalies - check sudden changes in max temp (>8°C difference)
    anomalies = []
    for i in range(1, len(max_temps)):
        if max_temps[i] is None or max_temps[i-1] is None:
            continue
        diff = abs(max_temps[i] - max_temps[i-1])
        if diff > 8:
            anomalies.append(dates[i])

    if anomalies:
        print("\nAnomalies detected on these dates (sudden temp changes > 8°C):")
        for anomaly_date in anomalies:
            print(anomaly_date)
    else:
        print("\nNo anomalies detected based on sudden temperature changes.")

def main():
    # Hyderabad coordinates
    latitude = 17.3850
    longitude = 78.4867

    try:
        weather_data = fetch_weather_data(latitude, longitude)
        analyze_weather(weather_data)
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")

if __name__ == "__main__":
    main()