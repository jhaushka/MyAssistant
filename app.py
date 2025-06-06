import streamlit as st
import speech_recognition as sr
import pyttsx3
import datetime
import random
import os
import requests
import wikipedia
from transformers import pipeline
from selenium_music import Music
import randfacts

# Initialize voice
engine = pyttsx3.init()
engine.setProperty('rate', 180)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Chatbot pipeline
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-medium")

def speak(text):
    st.text(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        r.adjust_for_ambient_noise(source, duration=1.2)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        st.success(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
    except sr.RequestError:
        speak("Could not connect to the speech service.")
    return ""

def save_reminder(reminder):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("reminders.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {reminder}\n")
    speak("Reminder saved.")

def list_reminders():
    try:
        with open("reminders.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                speak("Here are your latest reminders:")
                for line in lines[-5:]:
                    speak(line.strip())
            else:
                speak("No reminders found.")
    except FileNotFoundError:
        speak("You don't have any reminders yet.")

def take_note():
    speak("What should I note?")
    note = listen()
    if note:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("notes.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {note}\n")
        speak("Note saved.")

def read_notes():
    try:
        with open("notes.txt", "r", encoding="utf-8") as f:
            notes = f.readlines()
            if notes:
                speak("Here are your recent notes:")
                for line in notes[-5:]:
                    speak(line.strip())
            else:
                speak("No notes found.")
    except FileNotFoundError:
        speak("No notes found.")

def chat_with_local_gpt(prompt):
    context = f"Human: {prompt}\nAI:"
    result = chatbot(context, max_new_tokens=100, pad_token_id=50256)
    response = result[0]['generated_text'].split("AI:")[-1].strip()
    speak(response)

def get_weather(city):
    api_key = "a70f063f4b2d5483416a59e9bb2d64be"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temp}°C with {desc}.")
        else:
            speak("City not found.")
    except:
        speak("Failed to get weather info.")

# App layout
st.set_page_config(page_title="Anushka's Assistant", layout="centered")
st.title("🎙️ Voice Assistant UI")

if st.button("Start Listening"):
    command = listen()
    if not command:
        st.stop()

    if any(word in command for word in ["stop", "exit", "quit"]):
        speak("Goodbye Anushka!")

    elif "play" in command:
        speak("What should I play?")
        song = listen()
        if song:
            speak(f"Playing {song} on YouTube.")
            Music().play_music(song)

    elif "remind me" in command:
        speak("What should I remind you about?")
        reminder = listen()
        if reminder:
            save_reminder(reminder)

    elif "show my reminders" in command or "list my reminders" in command:
        list_reminders()

    elif "note" in command:
        take_note()

    elif "read notes" in command or "show notes" in command:
        read_notes()

    elif "fact" in command:
        fact = randfacts.getFact()
        speak(f"Did you know? {fact}")

    elif any(k in command for k in ["wikipedia", "who is", "what is"]):
        speak("What should I search on Wikipedia?")
        topic = listen()
        if topic:
            try:
                summary = wikipedia.summary(topic, sentences=2)
                speak(f"According to Wikipedia: {summary}")
            except:
                speak("Could not fetch information from Wikipedia.")

    elif "weather" in command or "temperature" in command:
        speak("For which city?")
        city = listen()
        if city:
            get_weather(city)

    elif any(k in command for k in ["chat", "talk", "question"]):
        speak("What would you like to talk about?")
        topic = listen()
        if topic:
            chat_with_local_gpt(topic)

    else:
        speak("Sorry, I didn't get that. Try saying play, note, remind, or chat.")
