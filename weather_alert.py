# Bronze Level - Weather Alert Bot
# Fetches weather from OpenWeatherMap
# Sends email alert if temp > 35°C or rain predicted

import requests
import smtplib
import ssl
import os
from email.message import EmailMessage

# -- FUNCTION 1: Get Weather --
def get_weather():
    api_key = os.environ.get("OPENWEATHER_KEY")
    city = "Alappuzha"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temp = data["main"]["temp"]
        weather = data["weather"][0]["main"]
        description = data["weather"][0]["description"]
        return temp, weather, description
    except Exception as e:
        print(f"Weather fetch failed: {e}")
        return None, None, None

# -- FUNCTION 2: Send Email --
def send_email(temp, weather, description):
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    subject = "⚠️ Weather Alert - Pulse Bot"
    body = f"""
Weather Alert for Bengaluru!

Temperature : {temp}°C
Condition   : {weather}
Description : {description}

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

# -- FUNCTION 3: Check and Alert --
def check_and_alert():
    temp, weather, description = get_weather()

    if temp is None:
        print("Could not fetch weather.")
        return

    print(f"Current temp: {temp}°C, Condition: {weather}")

    # Check if alert needed
    if temp > 20 or "rain" in weather.lower() or "rain" in description.lower():
        print("⚠️ Alert condition met! Sending email...")
        send_email(temp, weather, description)
    else:
        print("✅ Weather is fine. No alert needed.")

if __name__ == "__main__":
    check_and_alert()