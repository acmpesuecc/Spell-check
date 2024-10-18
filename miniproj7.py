import tkinter as tk
from textblob import TextBlob
from googletrans import Translator
import pyttsx3
from tkinter import PhotoImage
from PIL import ImageTk, Image
from tkinter import ttk
import customtkinter
from tkinter import messagebox

# Initialize spell checkers and language detection
translator = Translator()
eng = pyttsx3.init()
history_tracking = []

def detect_language(text):
    try:
        detection = translator.detect(text)
        return detection.lang  # Returns the language code, e.g., 'en', 'fr'
    except Exception as e:
        print(f"Error detecting language: {e}")
        return None

def spellcheck():
    text = text_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("Spell Check", "Please enter some text to check.")
        return

    # Detect language of the text
    detected_lang = detect_language(text)
    if detected_lang is None:
        messagebox.showinfo("Error", "Could not detect the language.")
        return

    # Track history
    history_tracking.append(text)

    if detected_lang == 'en':  # Spell check works better for English in TextBlob
        blob = TextBlob(text)
        corrected_text = str(blob.correct())
    else:
        messagebox.showinfo("Error", f"Spell checking is only supported for English currently. Detected language: {detected_lang}")
        return

    # Update the Text widget with the corrected text
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, corrected_text)

def pronun():
    word = text_box.get("1.0", tk.END).strip()
    eng.say(word)
    eng.runAndWait()

def get_word_info():
    word = text_box.get("1.0", tk.END).strip()
    blob = TextBlob(word)
    definitions = blob.definitions if blob.definitions else ["No definition found"]

    output = {
        "word": word,
        "meanings": definitions
    }
    global label_out
    label_out = tk.Label(root, text=output, font=("georgia", 24))
    label_out.place(x=2, y=600)

user_dict = set()

def add_to_user_dict():
    word = text_box.get("1.0", tk.END).strip()
    user_dict.add(word)

def disp_ud():
    global label_ud
    label_ud = tk.Label(master=root, text=list(user_dict)[:], font=("georgia", 24))
    label_ud.place(x=2, y=700)

def disp_history():
    global label_hist
    label_hist = tk.Label(master=root, text=history_tracking[:10], font=("georgia", 24))
    label_hist.place(x=2, y=800)

def remove():
    if "label_ud" in globals():
        label_ud.place_forget()
    if "label_out" in globals():
        label_out.place_forget()
    if "label_hist" in globals():
        label_hist.place_forget()

def update_colors():
    bg_color = "#1c1c1e" if dark_mode_var.get() else "#fff8c9"
    text_color = "white" if dark_mode_var.get() else "black"

    root.configure(bg=bg_color)
    mode_button.configure(bg=bg_color, fg=text_color)

def toggle_mode():
    current_mode = dark_mode_var.get()
    new_mode = not current_mode
    dark_mode_var.set(new_mode)
    mode_text = "Light Mode" if new_mode else "Dark Mode"
    mode_button.configure(text=mode_text)
    update_colors()

root = tk.Tk()
root.title("PhraseCraft v0.5-Presentable")
root.geometry("1000x1000")

speaker = ImageTk.PhotoImage(Image.open(r"C:\Users\gonel\OneDrive\Desktop\hacknight-24\hknyt24-Spell-check\speaker.jpeg"))

dark_mode_var = tk.BooleanVar()
dark_mode_var.set(False)

heading = ImageTk.PhotoImage(Image.open(r"C:\Users\gonel\OneDrive\Desktop\hacknight-24\hknyt24-Spell-check\title_dark.jpeg"))
mainlabel = tk.Label(image=heading)
mainlabel.place(x=0, y=0)

label1 = tk.Label(root, text="Enter text here:", font=("georgia", 24))
label1.place(x=2, y=200)

text_box = tk.Text(root, font="georgia", fg="black", height=10, width=60)
text_box.place(x=240, y=210)

b1 = customtkinter.CTkButton(master=root, text="Spell Check", command=spellcheck)
b1.place(x=440, y=210)

b2 = tk.Button(root, text="Meanings and Origin", bg="pink", fg="black", font="georgia", borderwidth=10, command=get_word_info)
b2.place(x=2, y=260)

b4 = tk.Button(root, text="My Dictionary", bg="pink", fg="black", font="georgia", borderwidth=10, command=disp_ud)
b4.place(x=315, y=260)

b5 = tk.Button(root, text="Add to my Dictionary", bg="pink", fg="black", font="georgia", borderwidth=10, command=add_to_user_dict)
b5.place(x=450, y=260)

b7 = tk.Button(root, text="My History", bg="pink", fg="black", font="georgia", borderwidth=10, command=disp_history)
b7.place(x=250, y=320)

b8 = tk.Button(root, text="Pronunciation", bg="pink", fg="black", font="georgia", borderwidth=10, command=pronun)
b8.place(x=640, y=220)

b9 = tk.Button(root, text="Clear", bg="pink", fg="black", font="georgia", borderwidth=10, command=remove)
b9.place(x=370, y=320)

mode_button = tk.Button(root, text="Light Mode", bg="pink", fg="black", font="georgia", borderwidth=10, command=toggle_mode)
mode_button.place(x=510, y=320)

root.mainloop()
