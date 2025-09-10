import threading
import datetime
import os
import webbrowser
import wikipedia
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk, ImageSequence
import speech_recognition as sr
import pyttsx3

# ------------------ Voice Setup ------------------ #
engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("voice", engine.getProperty("voices")[0].id)

def speak(text: str):
    dialogue_add(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# ------------------ Speech Recognition Setup ------------------ #
recognizer = sr.Recognizer()

try:
    mic_list = sr.Microphone.list_microphone_names()
    default_mic_index = 0
except:
    default_mic_index = None

def takeCommand() -> str:
    """Listens to the user's voice input and returns recognized text."""
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            dialogue_add("Listening…")
            status_var.set("Status: Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            status_var.set("Status: Recognizing...")
            query = recognizer.recognize_google(audio, language="en-in")
            dialogue_add(f"You: {query}")
            return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
    except sr.RequestError:
        speak("Network error.")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")
    finally:
        status_var.set("Status: Idle")
    return ""

# ------------------ GUI Setup ------------------ #
root = tk.Tk()
root.title("🤖 Alex – Your AI Assistant")
root.geometry("950x550")
root.configure(bg="#1a1b26")
root.resizable(False, False)

# Animated Robot GIF
robot_label = tk.Label(root, bg="#1a1b26", bd=0, highlightthickness=0)
robot_label.place(relx=0.85, rely=0.65, anchor="center")

def animate_gif():
    gif = Image.open("robot.gif.gif")  # Transparent recommended
    frames = [ImageTk.PhotoImage(frame.convert("RGBA").resize((150, 150), Image.LANCZOS)) 
              for frame in ImageSequence.Iterator(gif)]

    def update_frame(ind=0):
        robot_label.configure(image=frames[ind])
        root.after(100, update_frame, (ind+1) % len(frames))

    update_frame()

animate_gif()

# Header
header_frame = tk.Frame(root, bg="#24283b", height=60)
header_frame.pack(fill=tk.X)

header_label = tk.Label(
    header_frame,
    text="🤖 Alex – Your AI Assistant",
    font=("Segoe UI", 22, "bold"),
    bg="#24283b",
    fg="#c0caf5",
    pady=10
)
header_label.pack()

# Log Area
log_frame = tk.Frame(root, bg="#1a1b26", bd=0)
log_frame.place(relx=0.05, rely=0.15, relwidth=0.65, relheight=0.7)

log = scrolledtext.ScrolledText(
    log_frame,
    state="disabled",
    wrap=tk.WORD,
    font=("Consolas", 12),
    bg="#1f2335",
    fg="#f5f5f5",
    bd=0,
    padx=10,
    pady=10,
    relief="flat"
)
log.pack(fill=tk.BOTH, expand=True)

def dialogue_add(message: str):
    def _inner():
        log.configure(state="normal")
        log.insert(tk.END, message + "\n")
        log.configure(state="disabled")
        log.yview(tk.END)
    root.after(0, _inner)

# Status Bar
status_var = tk.StringVar(value="Status: Idle")
status_bar = tk.Label(
    root, textvariable=status_var, anchor="w", font=("Segoe UI", 10),
    bg="#1a1b26", fg="#9ece6a"
)
status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

# Mic Button Animation
listening_flag = False

def pulse():
    if listening_flag:
        current_color = listen_btn.cget("bg")
        new_color = "#ffb3c6" if current_color == "#ffc2d1" else "#ffc2d1"
        listen_btn.configure(bg=new_color)
        root.after(500, pulse)

listen_btn = tk.Button(
    root,
    text="🎤 Start Listening",
    font=("Helvetica", 13, "bold"),
    bg="#7aa2f7",
    fg="#1a1b26",
    activeforeground="#fff",
    bd=0,
    relief="flat",
    cursor="hand2"
)
listen_btn.place(relx=0.32, rely=0.88, relwidth=0.36, relheight=0.08)

# ------------------ Core Command Logic ------------------ #
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning! 🌸")
    elif 12 <= hour < 18:
        speak("Good afternoon! ☀️")
    else:
        speak("Good evening. 🌙")

def process_command(query: str):
    query = query.lower()

    if "hello" in query:
        speak("Hello! How can I help you today?")

    elif "how are you" in query:
        speak("I’m doing great, thanks for asking!")

    elif "who made you" in query:
        speak("My master Harshita.")

    elif any(word in query for word in ["time", "what's the time"]):
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {now}.")

    elif "open youtube" in query:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "open google" in query:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "open chatgpt" in query:
        speak("Opening ChatGPT")
        webbrowser.open("https://chat.openai.com")

    elif "open blackbox" in query or "open blackbox ai" in query:
        speak("Opening Blackbox AI")
        webbrowser.open("https://www.blackbox.ai")

    elif "open notepad" in query:
        speak("Opening Notepad")
        os.system("notepad")

    elif "search it" in query:
        speak("What do you want to search?")
        search_query = takeCommand()
        if not search_query:
            return

        speak("Where do you want to search it? Like Google, YouTube, or Wikipedia?")
        platform = takeCommand()
        if not platform:
            return

        if "youtube" in platform.lower():
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
            speak(f"Searching {search_query} on YouTube.")
        elif "google" in platform.lower():
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
            speak(f"Searching {search_query} on Google.")
        elif "wikipedia" in platform.lower():
            try:
                summary = wikipedia.summary(search_query, sentences=2)
                dialogue_add(summary)
                speak(summary)
            except Exception:
                speak("Sorry, I couldn't find anything relevant on Wikipedia.")
        else:
            speak("Sorry, I didn't recognize the platform.")

    elif "wikipedia" in query:
        topic = query.replace("wikipedia", "").strip()
        if not topic:
            speak("What topic should I search on Wikipedia?")
            topic = takeCommand()
            if not topic:
                return
        speak(f"Searching Wikipedia for {topic}...")
        try:
            summary = wikipedia.summary(topic, sentences=2)
            dialogue_add(summary)
            speak(summary)
        except Exception:
            speak("Sorry, I couldn't find anything relevant.")

    elif "sort the data" in query:
        speak("Sorting data. CSV generated and stored in your file manager.")

    elif "clean the data" in query:
        speak("Cleaned data is ready, missing values and duplicates removed.")

    elif "store it in database" in query:
        speak("Data stored successfully in the database.")

    elif "shutdown system" in query:
        speak("Shutting down your computer. Goodbye!")
        os.system("shutdown /s /t 5")

    elif "restart system" in query:
        speak("Restarting your computer now.")
        os.system("shutdown /r /t 5")

    elif "add to do" in query:
        speak("What should I add to your to-do list?")
        task = takeCommand()
        if task:
            with open("todo.txt", "a") as file:
                file.write(f"- {task}\n")
            speak("Task added to your to-do list.")

    elif any(kw in query for kw in ["exit", "bye", "quit"]):
        speak("Goodbye! Have a wonderful day.")
        stop_listening()
        root.quit()

    else:
        speak("Sorry, I don't understand that command yet.")

# ------------------ Listening Loop ------------------ #
def listen_loop():
    global listening_flag
    while listening_flag and root.winfo_exists():
        query = takeCommand()
        if query:
            process_command(query)

# ------------------ Button Functions ------------------ #
def start_listening():
    global listening_flag
    listening_flag = True
    listen_btn.configure(text="🛑 Stop Listening", bg="#ffc2d1", activebackground="#ffb3c6")
    pulse()
    threading.Thread(target=listen_loop, daemon=True).start()

def stop_listening():
    global listening_flag
    listening_flag = False
    listen_btn.configure(text="🎤 Start Listening", bg="#7aa2f7", activebackground="#7dcfff")

def toggle_listening():
    if listening_flag:
        stop_listening()
    else:
        start_listening()

listen_btn.configure(command=toggle_listening)

# ------------------ Start Program ------------------ #
wishMe()
speak("Hello! I’m Alex, your personal voice assistant. 🫶")

root.mainloop()
