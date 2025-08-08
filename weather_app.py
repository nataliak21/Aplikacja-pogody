import requests

from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv('API_KEY')

city = input("Podaj miasto:")
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=pl"

response = requests.get(url)
data = response.json()

if response.status_code == 200:
    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    temp_max = data["main"]["temp_max"]
    temp_min = data["main"]["temp_min"]
    description = data["weather"][0]["description"]
    cloud = data["clouds"]["all"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind = data["wind"]["speed"]
    wind = round(wind*3.6,2)

    print(f"Miasto: {city}")
    print(f"Temperatura: {temp}\N{DEGREE SIGN}C")
    print(f"Temperatura odczuwalna: {feels}\N{DEGREE SIGN}C")
    print(f"Temperatura maksymalna: {temp_max}\N{DEGREE SIGN}C")
    print(f"Temperatura minimalna: {temp_min}\N{DEGREE SIGN}C")
    print(f"{description}")
    print(f"Zachmurzenie: {cloud}%")
    print(f"Wilgotność: {humidity}%")
    print(f"Ciśnienie:{pressure} hPa")
    print(f"Prędkość wiatru: {wind}km/h")
else:
    print("Błąd w pobieraniu danych:", data.get("message", "Nieznany błąd"))