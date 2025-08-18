import requests
import os
from dotenv import load_dotenv
import streamlit as st
import openai

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('API_KEY')

openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="Pogodowy Asystent", layout="centered")
st.title("Pogodowy Asystent")


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Jesteś pomocnym asystentem pogodowym. Ciekawie o pogodzie w danym mieście."}
    ]
if "last_weather" not in st.session_state:
    st.session_state.last_weather = None
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "city" not in st.session_state:
    st.session_state.city = ""

if st.button("Resetuj", key="reset"):
    st.session_state.messages = [
        {"role": "system", "content": "Jesteś pomocnym asystentem pogodowym. Odpowiadaj krótko, ale ciekawie i wymień wszystkie dostępne informacje o pogodzie."}
    ]
    st.session_state.last_weather = None
    st.session_state.show_chat = False
    st.session_state.city = ""

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=pl"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        return data, None
    else:
        return None, response.json().get("message", "Błąd")

def info_weather(data):
    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    temp_max = data["main"]["temp_max"]
    temp_min = data["main"]["temp_min"]
    description = data["weather"][0]["description"]
    cloud = data["clouds"]["all"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind = round(data["wind"]["speed"] * 3.6, 2)

    raport = (
        f"Aktualna temperatura wynosi {temp}\N{DEGREE SIGN}C. "
        f"Odczuwalna jest jak {feels}\N{DEGREE SIGN}C. "
        f"Warunki: {description}. "
        f"Temperatura maksymalna: {temp_max}\N{DEGREE SIGN}C. "
        f"Temperatura minimalna: {temp_min}\N{DEGREE SIGN}C. "
        f"Zachmurzenie: {cloud}%, wilgotność: {humidity}%. "
        f"Ciśnienie: {pressure} hPa. "
        f"Prędkość wiatru: {wind} km/h."
    )
    return raport

def chat_openai(messages):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except openai.error.OpenAIError:
        return "Przekroczono limit zapytań do API OpenAI. Proszę spróbuj później."
    except Exception as e:
        return f"Wystąpił błąd: {e}"

st.session_state.show_chat = st.checkbox("Włącz tryb rozmowy z asystentem pogodowym", value=st.session_state.show_chat)

city = st.text_input("Podaj miasto:", value=st.session_state.city, key="styledcity")
st.session_state.city = city

if city and not st.session_state.last_weather:
    with st.spinner("Pobieram dane pogodowe..."):
        weather_data, error = get_weather(city)

    if error:
        st.error(f"Błąd: {error}")
    else:
        weather_report = info_weather(weather_data)
        st.session_state.last_weather = weather_report

        st.session_state.messages.append({
            "role": "system",
            "content": f"Oto szczegółowe dane pogodowe dla miasta {city}: {weather_report}"
        })
        st.session_state.messages.append({
            "role": "user",
            "content": f"Jaka jest pogoda w mieście {city}?"
        })

        with st.spinner("Generuję odpowiedź..."):
            answer = chat_openai(st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.markdown("Pogoda:")
        st.write(answer)

if st.session_state.show_chat:
    st.markdown("---")
    st.subheader("Porozmawiaj o pogodzie:")

    user_input = st.text_input("Twoja wiadomość:", key="user_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Asystent odpowiada..."):
            answer = chat_openai(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": answer})

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**Ty:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**Asystent Pogodowy:** {msg['content']}")