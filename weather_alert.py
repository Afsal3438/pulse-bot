import requests
import smtplib
import ssl
import os
from email.message import EmailMessage

# ----------------------------------
# FUNCTION 1: Get Weather Data
# ----------------------------------
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

        return temp, weather, description, humidity

    except Exception as e:
        print("Weather fetch failed:", e)
        return None, None, None, None


# ----------------------------------
# FUNCTION 2: Check Rain Condition
# ----------------------------------
def is_rain_predicted(weather, description):

    rain_keywords = [
        "rain",
        "drizzle",
        "shower",
        "thunderstorm",
        "squall",
        "tornado"
    ]

    weather = weather.lower()
    description = description.lower()

    for keyword in rain_keywords:
        if keyword in weather or keyword in description:
            return True

    return False


# ----------------------------------
# FUNCTION 3: Send Email Alert
# ----------------------------------
def send_email(temp, weather, description, humidity, reason):

    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    msg = EmailMessage()

    msg["Subject"] = "⚠️ Weather Alert"
    msg["From"] = sender
    msg["To"] = sender

    body = f"""
Weather Alert for Alappuzha

🌡 Temperature : {temp}°C
🌤 Condition   : {weather}
📝 Description : {description}
💧 Humidity    : {humidity}%

⚠ Alert Reason:
{reason}

Stay Safe!
"""

    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        context=context
    ) as server:

        server.login(sender, password)
        server.send_message(msg)

    print("✅ Alert email sent successfully!")


# ----------------------------------
# FUNCTION 4: Check Conditions
# ----------------------------------
def check_and_alert():

    temp, weather, description, humidity = get_weather()

    if temp is None:
        print("Could not fetch weather data.")
        return

    print(
        f"Temperature: {temp}°C | "
        f"Weather: {weather} | "
        f"{description}"
    )

    hot = temp > 35
    rain = is_rain_predicted(weather, description)

    # OR CONDITION
    if hot or rain:

        reasons = []

        if hot:
            reasons.append(
                f"High Temperature Detected ({temp}°C)"
            )

        if rain:
            reasons.append(
                f"Rain Predicted ({description})"
            )

        reason_text = "\n".join(reasons)

        send_email(
            temp,
            weather,
            description,
            humidity,
            reason_text
        )

    else:
        print("✅ Weather is normal. No alert required.")


# ----------------------------------
# MAIN
# ----------------------------------
if __name__ == "__main__":
    check_and_alert()