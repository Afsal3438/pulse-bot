import requests
import smtplib
import ssl
import os
from email.message import EmailMessage

# ----------------------------
# Get Weather Data
# ----------------------------
def get_weather():
    api_key = os.environ.get("OPENWEATHER_KEY")
    city = "Alappuzha"

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        weather = data["weather"][0]["main"]
        description = data["weather"][0]["description"]

        return temp, humidity, weather, description

    except Exception as e:
        print("Error:", e)
        return None, None, None, None


# ----------------------------
# Check Rain Condition
# ----------------------------
def is_rain_predicted(weather, description):

    rain_keywords = [
        "rain",
        "drizzle",
        "shower",
        "thunderstorm"
    ]

    weather = weather.lower()
    description = description.lower()

    for word in rain_keywords:
        if word in weather or word in description:
            return True

    return False


# ----------------------------
# Send Email
# ----------------------------
def send_email(temp, humidity, weather, description, alert=False):

    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    subject = "Daily Weather Update"

    body = f"""
Weather Update - Alappuzha

Temperature : {temp}°C
Humidity    : {humidity}%
Condition   : {weather}
Description : {description}
"""

    # Alert only when BOTH conditions are true
    if alert:
        body += f"""

⚠️ WEATHER ALERT ⚠️

High Temperature (>35°C)
AND
Rain Expected

Please take precautions.
"""

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = sender
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        context=context
    ) as server:

        server.login(sender, password)
        server.send_message(msg)

    print("Email sent successfully!")


# ----------------------------
# Main Logic
# ----------------------------
def check_weather():

    temp, humidity, weather, description = get_weather()

    if temp is None:
        print("Failed to get weather data.")
        return

    rain = is_rain_predicted(weather, description)

    # Alert only when BOTH conditions are true
    alert = temp > 35 and rain

    send_email(
        temp,
        humidity,
        weather,
        description,
        alert
    )


if __name__ == "__main__":
    check_weather()