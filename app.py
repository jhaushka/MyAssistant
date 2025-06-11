import streamlit as st
import speech_recognition as sr
import datetime
import wikipedia
import requests
import os
import platform
from transformers import pipeline
from gtts import gTTS
from io import BytesIO

# ========== Optional YouTube (Selenium) ==========
USE_SELENIUM = platform.system() == "Windows"
if USE_SELENIUM:
    try:
        from selenium_music import Music
    except ImportError:
        USE_SELENIUM = False

# ========== Ensure Files Exist ==========
for filename in ["notes.txt", "reminders.txt"]:
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("")

# ========== Setup ==========
st.set_page_config(page_title="Anushka's Assistant", layout="centered")
st.title("🧠 Your Personal Voice Assistant")

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "greeted" not in st.session_state:
    st.session_state.greeted = False

# ========== Text-to-Speech ==========
def speak(text):
    st.session_state.chat_log.append({"bot": text})
    st.markdown(f"**Assistant**: {text}")
    try:
        tts = gTTS(text=text, lang='en')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        st.audio(audio_fp.getvalue(), format="audio/mp3")
    except Exception as e:
        st.error("Audio playback failed.")

# ========== Listen ==========
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Speak now.")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            st.warning("⏰ Listening timed out.")
            return ""
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

# ========== Chatbot Setup ==========
try:
    chatbot = pipeline("text-generation", model="distilgpt2")
except:
    chatbot = None
    def chat_with_local_gpt(prompt):
        speak("Chat feature is not available.")
else:
    def chat_with_local_gpt(prompt):
        context = f"Human: {prompt}\nAI:"
        result = chatbot(context, max_new_tokens=80, pad_token_id=50256)
        response = result[0]['generated_text'].split("AI:")[-1].strip()
        speak(response)

# ========== Features ==========
def get_weather(city):
    api_key = "a70f063f4b2d5483416a59e9bb2d64be"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        data = requests.get(url).json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temp}°C with {desc}.")
        else:
            speak("City not found.")
    except:
        speak("Weather error.")

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
            for line in f.readlines()[-5:]:
                speak(line.strip())
    except:
        speak("No notes found.")

def save_reminder(reminder):
    with open("reminders.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {reminder}\n")
    speak("Reminder saved.")

def list_reminders():
    try:
        with open("reminders.txt", "r", encoding="utf-8") as f:
            for line in f.readlines()[-5:]:
                speak(line.strip())
    except:
        speak("No reminders found.")

def clear_reminders():
    open("reminders.txt", "w").close()
    speak("All reminders cleared.")

def execute_system_command(command):
    speak("This feature only works in the desktop version.")

# ========== Greeting ==========
if not st.session_state.greeted:
    today = datetime.datetime.now().strftime("%d %B %Y")
    speak(f"Hello Anushka, welcome back! Today is {today}.")
    st.markdown("### 💡 Try saying:")
    st.markdown("""
    - 🎵 **Play [song] (local only)**  
    - 📝 **Take a note**, **Read notes**  
    - 🔔 **Remind me to...**, **Show reminders**  
    - 🌤️ **Weather in Delhi**  
    - 📚 **Search Wikipedia**  
    - 💬 **Chat with AI (local only)**  
    """)
    st.session_state.greeted = True

# ========== Tabs ==========
tab1, tab2, tab3 = st.tabs(["🎙️ Assistant", "📝 Notes & Reminders", "💬 Chat Log"])

with tab1:
    if st.button("🎙️ Start Listening"):
        command = listen()
        if "play" in command:
            speak("What should I play?")
            song = listen()
            if song:
                if USE_SELENIUM:
                    speak(f"Playing {song} on YouTube.")
                    Music().play_music(song)
                else:
                    speak("Music playback works only on desktop.")
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
            speak("Which city?")
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
                    speak("Not found.")
        elif "chat" in command:
            speak("What's on your mind?")
            prompt = listen()
            if prompt:
                chat_with_local_gpt(prompt)
        elif "open" in command:
            execute_system_command(command)
        elif "stop" in command or "exit" in command:
            speak("Goodbye Anushka!")
        else:
            speak("Command not recognized. Try again.")

with tab2:
    st.markdown("### 📓 Notes")
    if os.path.exists("notes.txt"):
        with open("notes.txt", "r", encoding="utf-8") as f:
            st.text(f.read()[-500:])
    else:
        st.info("No notes found.")

    st.markdown("### 🔔 Reminders")
    if os.path.exists("reminders.txt"):
        with open("reminders.txt", "r", encoding="utf-8") as f:
            st.text(f.read()[-500:])
    else:
        st.info("No reminders found.")

with tab3:
    st.markdown("### 🧠 Conversation History")
    for entry in st.session_state.chat_log[-10:][::-1]:
        if "user" in entry:
            st.markdown(f"**You**: {entry['user']}")
        if "bot" in entry:
            st.markdown(f"**Assistant**: {entry['bot']}")
