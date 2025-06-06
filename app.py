import streamlit as st
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import requests
import os
import random
from transformers import pipeline
from selenium_music import Music

# Initialize session state
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# TTS
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('voice', engine.getProperty('voices')[1].id)

# DialoGPT model
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-medium")

# ========== CORE FUNCTIONS ==========

def speak(text):
    st.session_state.chat_log.append({"bot": text})
    st.markdown(f"**Assistant**: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        st.success(f"**You said**: {command}")
        st.session_state.chat_log.append({"user": command})
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
    except sr.RequestError:
        speak("Could not connect to the speech service.")
    return ""

def chat_with_local_gpt(prompt):
    try:
        context = f"Human: {prompt}\nAI:"
        result = chatbot(context, max_new_tokens=100, pad_token_id=50256)
        response = result[0]['generated_text'].split("AI:")[-1].strip()
        speak(response)
    except Exception as e:
        speak("Sorry, I couldn't respond.")
        st.error(f"Chat Error: {e}")

def get_weather(city):
    try:
        api_key = "a70f063f4b2d5483416a59e9bb2d64be"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        data = requests.get(url).json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temp}°C with {desc}.")
        else:
            speak("City not found.")
    except Exception as e:
        speak("Sorry, couldn't fetch weather.")
        st.error(f"Weather Error: {e}")

def take_note():
    speak("What should I note?")
    note = listen()
    if note:
        with open("notes.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {note}\n")
        speak("Note saved.")

def read_notes():
    try:
        with open("notes.txt", "r", encoding="utf-8") as f:
            notes = f.readlines()[-5:]
            if notes:
                speak("Here are your latest notes.")
                for line in notes:
                    speak(line.strip())
            else:
                speak("No notes found.")
    except:
        speak("Notes file not found.")

def save_reminder(reminder):
    with open("reminders.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {reminder}\n")
    speak("Reminder saved.")

def list_reminders():
    try:
        with open("reminders.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()[-5:]
            if lines:
                speak("Here are your reminders:")
                for line in lines:
                    speak(line.strip())
            else:
                speak("You have no reminders.")
    except:
        speak("Reminders file not found.")

def clear_reminders():
    open("reminders.txt", "w").close()
    speak("All reminders cleared.")

def execute_system_command(command):
    if "notepad" in command:
        os.system("start notepad")
        speak("Opening Notepad.")
    elif "chrome" in command:
        os.system("start chrome")
        speak("Launching Chrome.")
    elif "explorer" in command:
        os.system("start explorer")
        speak("Opening File Explorer.")
    elif "calculator" in command:
        os.system("start calc")
        speak("Opening Calculator.")
    else:
        speak("Sorry, I can't open that.")

# ========== STREAMLIT UI ==========

st.set_page_config(page_title="Anushka's Assistant", layout="centered")
st.title("🧠 Your Personal Voice Assistant")

tab1, tab2, tab3 = st.tabs(["🎙️ Assistant", "📝 Notes & Reminders", "💬 Chat Log"])

with tab1:
    st.markdown("Click the mic button and give a voice command.")
    if st.button("🎙️ Start Listening"):
        command = listen()
        if "play" in command:
            speak("What should I play?")
            song = listen()
            if song:
                speak(f"Playing {song} on YouTube.")
                Music().play_music(song)
        elif "note" in command:
            take_note()
        elif "read notes" in command:
            read_notes()
        elif "remind me" in command:
            speak("What should I remind you about?")
            reminder = listen()
            if reminder:
                save_reminder(reminder)
        elif "show reminders" in command:
            list_reminders()
        elif "clear reminders" in command:
            clear_reminders()
        elif "weather" in command:
            speak("For which city?")
            city = listen()
            if city:
                get_weather(city)
        elif "wikipedia" in command:
            speak("What should I search?")
            topic = listen()
            if topic:
                try:
                    summary = wikipedia.summary(topic, sentences=2)
                    speak(f"According to Wikipedia: {summary}")
                except:
                    speak("Couldn't find that.")
        elif "chat" in command:
            speak("What would you like to talk about?")
            q = listen()
            if q:
                chat_with_local_gpt(q)
        elif "open" in command:
            execute_system_command(command)
        elif "stop" in command or "exit" in command:
            speak("Goodbye Anushka!")
        else:
            speak("Sorry, I didn’t understand that.")

with tab2:
    st.markdown("### Recent Notes")
    if os.path.exists("notes.txt"):
        with open("notes.txt", "r", encoding="utf-8") as f:
            st.text(f.read()[-500:])
    else:
        st.info("No notes found.")
    
    st.markdown("### Recent Reminders")
    if os.path.exists("reminders.txt"):
        with open("reminders.txt", "r", encoding="utf-8") as f:
            st.text(f.read()[-500:])
    else:
        st.info("No reminders found.")

with tab3:
    st.markdown("### Chat History")
    for entry in st.session_state.chat_log[-10:][::-1]:
        if "user" in entry:
            st.markdown(f"**You**: {entry['user']}")
        if "bot" in entry:
            st.markdown(f"**Assistant**: {entry['bot']}")
