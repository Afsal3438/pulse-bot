import requests
import smtplib
import ssl
import os
from email.message import EmailMessage

# -- FUNCTION 1: Get Weather --
def get_weather():
    api_key = os.environ.get("OPENWEATHER_KEY")
    city = "Mumbai"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temp = data["main"]["temp"]
        weather = data["weather"][0]["main"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        return temp, weather, description, humidity
    except Exception as e:
        print(f"Weather fetch failed: {e}")
        return None, None, None, None

# -- FUNCTION 2: Check if Rain Predicted --
def is_rain_predicted(weather, description):
    rain_keywords = [
        "rain", "drizzle", "shower",
        "thunderstorm", "squall", "tornado"
    ]
    weather_lower = weather.lower()
    desc_lower = description.lower()

    for keyword in rain_keywords:
        if keyword in weather_lower or keyword in desc_lower:
            return True
    return False

# -- FUNCTION 3: Send Email --
def send_email(temp, weather, description, humidity, reason):
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    subject = "⚠️ Weather Alert - Pulse Bot"
    body = f"""
Weather Alert for Mumbai!

🌡️  Temperature  : {temp}°C
🌤️  Condition    : {weather}
📝  Description  : {description}
💧  Humidity     : {humidity}%

⚠️  Alert Reason : {reason}

Stay safe! 🌧️
    """

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = sender
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.send_message(msg)
        print("✅ Alert email sent!")

# -- FUNCTION 4: Check and Alert --
def check_and_alert():
    temp, weather, description, humidity = get_weather()

    if temp is None:
        print("Could not fetch weather.")
        return

    print(f"Temp: {temp}°C | Condition: {weather} | {description}")

    # Check conditions
    rain = is_rain_predicted(weather, description)
    hot = temp > 35

    if hot and rain:
        reason = f"Temperature is {temp}°C AND rain predicted ({description})"
        send_email(temp, weather, description, humidity, reason)
    elif hot:
        reason = f"Temperature is too high: {temp}°C"
        send_email(temp, weather, description, humidity, reason)
    elif rain:
        reason = f"Rain predicted: {description}"
        send_email(temp, weather, description, humidity, reason)
    else:
        print("✅ Weather is fine. No alert needed.")

if __name__ == "__main__":
    check_and_alert()