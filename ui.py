import sys
import random
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QMessageBox, QGridLayout, 
                             QListWidget, QInputDialog)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from textblob import TextBlob
from nltk.corpus import wordnet
import pyttsx3

# Initialize text-to-speech engine
eng = pyttsx3.init()

# Flashcard class to store flashcard data
class Flashcard:
    def __init__(self, word, meaning, synonyms, example):
        self.word = word
        self.meaning = meaning
        self.synonyms = synonyms
        self.example = example

class PhraseCraftApp(QWidget):
    def __init__(self):
        super().__init__()
        self.flashcards = []
        self.correct_answers = 0
        self.total_questions = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PhraseCraft v0.5 - Updated")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("QWidget { background-color: #1C1C1C; font-family: 'Segoe Print'; }")
        
        layout = QVBoxLayout()
        self.create_app_bar(layout)
        self.create_search_area(layout)
        self.create_action_buttons(layout)
        self.create_output_area(layout)
        self.setLayout(layout)

    def create_app_bar(self, layout):
        appbar_layout = QHBoxLayout()
        title_label = QLabel("PhraseCraft", self)
        title_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFEA00;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        appbar_layout.addWidget(title_label)
        appbar_layout.addStretch(1)
        layout.addLayout(appbar_layout)

    def create_search_area(self, layout):
        search_layout = QHBoxLayout()
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter text here...")
        self.text_input.setFont(QFont("Arial", 18))
        self.text_input.setFixedHeight(60)
        self.text_input.setStyleSheet("""
            QLineEdit { border-radius: 20px; padding: 15px; border: 2px solid #FFEA00; background-color: #2A2A2A; color: white; }
            QLineEdit:focus { border: 2px solid #76b852; }
        """)
        search_layout.addWidget(self.text_input)

        self.btn_spellcheck = QPushButton("Spellcheck", self)
        self.btn_spellcheck.setFont(QFont("Arial", 20))
        self.btn_spellcheck.setFixedHeight(60)
        self.btn_spellcheck.setStyleSheet("""
            QPushButton { border-radius: 20px; padding: 15px; background-color: #FFEA00; color: #000000; }
            QPushButton:hover { background-color: #FFD700; }
            QPushButton:pressed { background-color: #FFC107; }
        """)
        self.btn_spellcheck.clicked.connect(self.spellcheck)
        search_layout.addWidget(self.btn_spellcheck)
        layout.addLayout(search_layout)

    def create_action_buttons(self, layout):
        buttons_layout = QGridLayout()
        self.btn_pronounce = QPushButton("Pronounce", self)
        self.set_button_style(self.btn_pronounce)
        self.btn_pronounce.clicked.connect(self.pronounce_word)
        buttons_layout.addWidget(self.btn_pronounce, 0, 0)

        self.btn_meaning_origin = QPushButton("Get Meanings and Origin", self)
        self.set_button_style(self.btn_meaning_origin)
        self.btn_meaning_origin.clicked.connect(self.get_word_info)
        buttons_layout.addWidget(self.btn_meaning_origin, 0, 1)

        self.btn_synonyms = QPushButton("Get Synonyms", self)
        self.set_button_style(self.btn_synonyms)
        self.btn_synonyms.clicked.connect(self.get_synonyms)
        buttons_layout.addWidget(self.btn_synonyms, 1, 0)

        self.btn_create_flashcard = QPushButton("Create Flashcard", self)
        self.set_button_style(self.btn_create_flashcard)
        self.btn_create_flashcard.clicked.connect(self.create_flashcard)
        buttons_layout.addWidget(self.btn_create_flashcard, 1, 1)

        self.btn_review_flashcards = QPushButton("Review Flashcards", self)
        self.set_button_style(self.btn_review_flashcards)
        self.btn_review_flashcards.clicked.connect(self.review_flashcards)
        buttons_layout.addWidget(self.btn_review_flashcards, 2, 0)

        self.btn_quiz_user = QPushButton("Quiz Me", self)
        self.set_button_style(self.btn_quiz_user)
        self.btn_quiz_user.clicked.connect(self.quiz_user)
        buttons_layout.addWidget(self.btn_quiz_user, 2, 1)

        self.btn_progress = QPushButton("Show Progress", self)
        self.set_button_style(self.btn_progress)
        self.btn_progress.clicked.connect(self.show_progress)
        buttons_layout.addWidget(self.btn_progress, 3, 0)

        layout.addLayout(buttons_layout)

    def set_button_style(self, button):
        button.setFont(QFont("Arial", 20))
        button.setFixedHeight(70)
        button.setStyleSheet("""
            QPushButton { border-radius: 20px; padding: 15px; background-color: #2E7D32; color: white; }
            QPushButton:hover { background-color: #66bb6a; }
            QPushButton:pressed { background-color: #388e3c; }
        """)

    def create_output_area(self, layout):
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Arial", 18))
        self.output_area.setStyleSheet("""
            QTextEdit { background-color: #2A2A2A; border-radius: 20px; padding: 15px; border: 2px solid #FFEA00; color: white; }
        """)
        layout.addWidget(self.output_area)

    def spellcheck(self):
        text = self.text_input.text()
        blob = TextBlob(text)
        corrected_text = str(blob.correct())
        
        if corrected_text != text:
            question = f"Did you mean: '{corrected_text}'?"
            reply = QMessageBox.question(self, 'Spell Check', question, 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.text_input.setText(corrected_text)
        else:
            self.output_area.setText("No spelling errors found.")

    def pronounce_word(self):
        word = self.text_input.text()
        eng.say(word)
        eng.runAndWait()

    def get_word_info(self):
        word = self.text_input.text()
        synsets = wordnet.synsets(word)
        meanings = [syn.definition() for syn in synsets] if synsets else []
        example = "Example usage: " + (meanings[0] if meanings else "No examples available.")
        synonyms = self.get_synonyms(word)
        
        output = f"Word: {word}\nMeanings: {meanings}\nSynonyms: {synonyms}\nExample: {example}"
        self.output_area.setText(output)

    def get_synonyms(self, word):
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        return ", ".join(synonyms) if synonyms else "No synonyms found."

    def create_flashcard(self):
        word = self.text_input.text()
        if not word:
            QMessageBox.warning(self, "Warning", "Please enter a word to create a flashcard.")
            return

        meanings = [syn.definition() for syn in wordnet.synsets(word)]
        synonyms = self.get_synonyms(word)
        example = "Example usage: " + (meanings[0] if meanings else "No examples available.")
        
        flashcard = Flashcard(word, meanings, synonyms, example)
        self.flashcards.append(flashcard)
        QMessageBox.information(self, "Flashcard Created", f"Flashcard for '{word}' created successfully.")

    def review_flashcards(self):
        if not self.flashcards:
            QMessageBox.information(self, "Review Flashcards", "No flashcards available.")
            return

        review_window = QWidget()
        review_layout = QVBoxLayout()
        flashcard_list = QListWidget()
        
        for card in self.flashcards:
            flashcard_list.addItem(card.word)  # Display flashcard words
        
        review_layout.addWidget(flashcard_list)
        review_window.setLayout(review_layout)
        review_window.setWindowTitle("Review Flashcards")
        review_window.setGeometry(200, 200, 400, 300)
        review_window.show()

    def quiz_user(self):
        if not self.flashcards:
            QMessageBox.information(self, "Quiz", "No flashcards available.")
            return

        self.total_questions += 1
        flashcard = random.choice(self.flashcards)
        answer, ok = QInputDialog.getText(self, "Quiz", f"What is the meaning of '{flashcard.word}'?")
        
        if ok and answer.lower() == flashcard.meaning[0].lower():  # Compare with the first meaning
            self.correct_answers += 1
            QMessageBox.information(self, "Quiz", "Correct!")
        else:
            QMessageBox.information(self, "Quiz", f"Wrong! The correct answer is: {flashcard.meaning[0]}")

    def show_progress(self):
        if self.total_questions == 0:
            accuracy = 0
        else:
            accuracy = (self.correct_answers / self.total_questions) * 100
        progress = f"Words Learned: {len(self.flashcards)}\nAccuracy: {accuracy:.2f}%"
        QMessageBox.information(self, "Progress", progress)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhraseCraftApp()
    window.show()
    sys.exit(app.exec())
