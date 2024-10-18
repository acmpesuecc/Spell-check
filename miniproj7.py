import tkinter as tk
from spellchecker import SpellChecker as sc
from nltk.corpus import wordnet
import pyttsx3

from tkinter import PhotoImage
from PIL import ImageTk,Image

from tkinter import ttk
import customtkinter
from tkinter import messagebox


spell_checker = sc()
eng = pyttsx3.init()
history_tracking = []



def spellcheck():
	text=entry1.get()
	history_tracking.append(text)
	misspelled = spell_checker.unknown(text.lower().split())
	corrected_text = text

	for word in misspelled:
		suggestions = spell_checker.correction(word)
		if suggestions != word:
			question = f"Is '{suggestions}' the correct spelling for '{word}'? (Y/N)"
			user_response = messagebox.askquestion("Spelling Check", question)
			if user_response == "yes":
				corrected_text = corrected_text.replace(word, suggestions)
				entry1.delete(0,"end")
				entry1.insert(10, corrected_text)
			else:
				suggestions_text = f"Suggestions for {word}: {', '.join(spell_checker.candidates(word))}"
				messagebox.showinfo("Spelling Suggestions", suggestions_text)

def pronun():
	word=entry1.get()
	eng.say(word)
	eng.runAndWait()

def get_word_info():
	word = entry1.get()
	synsets = wordnet.synsets(word)
	meanings = [syn.definition() for syn in synsets] if synsets else []

	output= {
		"word": word,
		"meaning": meanings,
		"origin": get_word_origin(word),
	}
	global label_out
	label_out=tk.Label(root,text=output,font=("georgia",24))
	label_out.place(x=2,y=600)


def get_word_origin(word):
	synsets = wordnet.synsets(word)
	og = set()
	for syn in synsets:
		for lemma in syn.lemmas():
			og.add(lemma.name())
	return list(og)


def get_synonyms():
	word = entry1.get()
	synsets = wordnet.synsets(word)
	synonyms = set()
	for syn in synsets:
		for lemma in syn.lemmas():
			synonyms.add(lemma.name())

	op=list(synonyms)[:10]
	global label_synonym
	label_synonym=tk.Label(master=root,text=op,font=("georgia",24))
	label_synonym.place(x=2,y=900)
	

user_dict = set()

def track_history(word):
	history_tracking.insert(0, word)
	if len(history_tracking) > 10:
		history_tracking = history_tracking[:10]

def add_to_user_dict():
	word= entry1.get()
	user_dict.add(word)

def disp_ud():
	global label_ud
	label_ud=tk.Label(master=root,text=list(user_dict)[:],font=("georgia",24))
	label_ud.place(x=2,y=700)
def remove_from_dic():
	word = entry1.get()
	user_dict.discard(word)
def disp_history():
	global label_hist
	label_hist=tk.Label(master=root,text=history_tracking[:10],font=("georgia",24))
	label_hist.place(x=2,y=800)

def remove():
	if "label_ud" in globals():
		label_ud.place_forget()
	if "label_out" in globals():
		label_out.place_forget()
	if "label_synonym" in globals():
		label_synonym.place_forget()
	if "label_hist" in globals():
		label_hist.place_forget()

def update_colors():
	bg_color = "#1c1c1e" if dark_mode_var.get() else "#fff8c9"
	text_color = "white" if dark_mode_var.get() else "black"

	if dark_mode_var.get():
		mainlabel.config(image = heading_dark)
	else:
		mainlabel.config(image = heading_light)

	root.configure(bg=bg_color)
	mode_button.configure(bg=bg_color, fg=text_color)
	

def toggle_mode():
	current_mode = dark_mode_var.get()
	new_mode = not current_mode
	dark_mode_var.set(new_mode)
	mode_text = "Light Mode" if new_mode else "Dark Mode"
	mode_button.configure(text=mode_text)
	update_colors()

	
root=tk.Tk()
root.title("PhraseCraft v0.5-Presentable")
root.geometry("1000x1000")
#
speaker=ImageTk.PhotoImage(Image.open(r"/home/Suchitra/Desktop/code./dictionary/speaker.jpeg"))


dark_mode_var = tk.BooleanVar()
dark_mode_var.set(False)

heading_light =ImageTk.PhotoImage(Image.open(r"/home/Suchitra/Desktop/code./dictionary/title_light.jpg"))
heading_dark =ImageTk.PhotoImage(Image.open(r"/home/Suchitra/Desktop/code./dictionary/title_dark.jpeg"))
mainlabel=tk.Label(image = heading_light)
mainlabel.place(x=0,y=0)

label1=tk.Label(root,text="Enter text here:",font=("georgia",24))
label1.place(x=2,y=200)

entry1=tk.Entry(font="georgia",fg="black")
entry1.place(x=240,y=210)

b1=customtkinter.CTkButton(master=root,text="spellcheck",command=spellcheck)
b1.place(x=440,y=210)

b2=tk.Button(root,text="Meanings and Origin",bg="pink",fg="black",font="georgia",borderwidth=10,command=get_word_info)
b2.place(x=2,y=260)

b3=tk.Button(root,text="Synonyms",bg="pink",fg="black",font="georgia",borderwidth=10,command=get_synonyms)
b3.place(x=200,y=260)

b4=tk.Button(root,text="My Dictionary",bg="pink",fg="black",font="georgia",borderwidth=10,command=disp_ud)
b4.place(x=315,y=260)

b5=tk.Button(root,text="Add to my dictionary",bg="pink",fg="black",font="georgia",borderwidth=10,command=add_to_user_dict)
b5.place(x=450,y=260)

b6=tk.Button(root,text="Remove from my Dictionary",bg="pink",fg="black",font="georgia",borderwidth=10,command=remove_from_dic)
b6.place(x=2,y=320)

b7=tk.Button(root,text="My History",bg="pink",fg="black",font="georgia",borderwidth=10,command=disp_history)
b7.place(x=250,y=320)


b8=tk.Button(root,image=speaker,command=pronun)
#b8=tk.Button(root,text="Pronounciation",bg="pink",fg="black",font="georgia",borderwidth=10,command=pronun)
b8.place(x=640,y=220)

b9=tk.Button(root,text="Clear",bg="pink",fg="black",font="georgia",borderwidth=10,command=remove)
b9.place(x=370,y=320)

mode_button = tk.Button(root, text="Light Mode",bg="pink",fg="black",font="georgia",borderwidth=10, command=toggle_mode)
mode_button.place(x=510,y=320)




root.mainloop()
