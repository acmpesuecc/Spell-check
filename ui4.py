import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, 
                             QMessageBox, QGridLayout, QTabWidget, QListWidget, QInputDialog)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from textblob import TextBlob
from nltk.corpus import wordnet
import pyttsx3
from g2p_en import G2p
import random
import json

# Initialize text-to-speech engine
eng = pyttsx3.init()

g2p = G2p()

class Flashcard:
    def __init__(self, word, meaning, synonyms, example):
        self.word = word
        self.meaning = meaning
        self.synonyms = synonyms
        self.example = example
        self.reviewed_count = 0
        self.correct_count = 0

class FlashcardManager:
    def __init__(self):
        self.flashcards = {}
        self.load_flashcards()

    def add_flashcard(self, word, meaning, synonyms, example):
        self.flashcards[word] = Flashcard(word, meaning, synonyms, example)
        self.save_flashcards()

    def delete_flashcard(self, word):
        if word in self.flashcards:
            del self.flashcards[word]
            self.save_flashcards()

    def get_flashcard(self, word):
        return self.flashcards.get(word)

    def get_all_flashcards(self):
        return list(self.flashcards.values())

    def update_flashcard_progress(self, word, is_correct):
        if word in self.flashcards:
            self.flashcards[word].reviewed_count += 1
            if is_correct:
                self.flashcards[word].correct_count += 1
            self.save_flashcards()

    def save_flashcards(self):
        with open('flashcards.json', 'w') as f:
            json.dump({word: vars(card) for word, card in self.flashcards.items()}, f)

    def load_flashcards(self):
        try:
            with open('flashcards.json', 'r') as f:
                data = json.load(f)
                self.flashcards = {word: Flashcard(**card_data) for word, card_data in data.items()}
        except FileNotFoundError:
            self.flashcards = {}

class PhraseCraftApp(QWidget):
    def __init__(self):
        super().__init__()
        self.flashcard_manager = FlashcardManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PhraseCraft v1.0 - Vocabulary Builder")
        self.setGeometry(100, 100, 1200, 800)

        self.setStyleSheet("""
            QWidget {
                background-color: #1C1C1C; 
                font-family: 'Segoe Print'; 
            }
        """)

        layout = QVBoxLayout()

        self.create_app_bar(layout)
        self.create_tab_widget(layout)

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

    def create_tab_widget(self, layout):
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Arial", 14))
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #FFEA00;
                background: #2A2A2A;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #2E7D32;
                color: white;
                padding: 10px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #66bb6a;
            }
        """)

        self.create_word_lookup_tab()
        self.create_flashcard_review_tab()
        self.create_progress_tracking_tab()

        layout.addWidget(self.tab_widget)

    def create_word_lookup_tab(self):
        word_lookup_tab = QWidget()
        word_lookup_layout = QVBoxLayout()

        self.create_search_area(word_lookup_layout)
        self.create_action_buttons(word_lookup_layout)
        self.create_output_area(word_lookup_layout)

        word_lookup_tab.setLayout(word_lookup_layout)
        self.tab_widget.addTab(word_lookup_tab, "Word Lookup")

    def create_flashcard_review_tab(self):
        flashcard_review_tab = QWidget()
        flashcard_review_layout = QVBoxLayout()

        self.flashcard_list = QListWidget()
        self.flashcard_list.setFont(QFont("Arial", 16))
        self.flashcard_list.setStyleSheet("""
            QListWidget {
                background-color: #2A2A2A;
                border: 1px solid #FFEA00;
                border-radius: 5px;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #66bb6a;
            }
        """)
        self.update_flashcard_list()
        flashcard_review_layout.addWidget(self.flashcard_list)

        review_buttons_layout = QHBoxLayout()
        
        self.btn_review_flashcard = QPushButton("Review Selected")
        self.set_button_style(self.btn_review_flashcard)
        self.btn_review_flashcard.clicked.connect(self.review_selected_flashcard)
        review_buttons_layout.addWidget(self.btn_review_flashcard)

        self.btn_quiz_flashcard = QPushButton("Quiz Me")
        self.set_button_style(self.btn_quiz_flashcard)
        self.btn_quiz_flashcard.clicked.connect(self.start_quiz)
        review_buttons_layout.addWidget(self.btn_quiz_flashcard)

        self.btn_delete_flashcard = QPushButton("Delete Flashcard")
        self.set_button_style(self.btn_delete_flashcard)
        self.btn_delete_flashcard.clicked.connect(self.delete_selected_flashcard)
        review_buttons_layout.addWidget(self.btn_delete_flashcard)

        flashcard_review_layout.addLayout(review_buttons_layout)

        flashcard_review_tab.setLayout(flashcard_review_layout)
        self.tab_widget.addTab(flashcard_review_tab, "Flashcard Review")

    def create_progress_tracking_tab(self):
        progress_tracking_tab = QWidget()
        progress_tracking_layout = QVBoxLayout()

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setFont(QFont("Arial", 16))
        self.progress_text.setStyleSheet("""
            QTextEdit {
                background-color: #2A2A2A;
                border: 1px solid #FFEA00;
                border-radius: 5px;
                color: white;
            }
        """)
        progress_tracking_layout.addWidget(self.progress_text)

        self.update_progress_tracking()

        progress_tracking_tab.setLayout(progress_tracking_layout)
        self.tab_widget.addTab(progress_tracking_tab, "Progress Tracking")

    def create_search_area(self, layout):
        search_layout = QHBoxLayout()

        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter text here...")
        self.text_input.setFont(QFont("Arial", 18))
        self.text_input.setFixedHeight(60)
        self.text_input.setStyleSheet("""
            QLineEdit {
                border-radius: 20px;
                padding: 15px;
                border: 2px solid #FFEA00;
                background-color: #2A2A2A;  
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #76b852;
            }
        """)
        search_layout.addWidget(self.text_input)

        self.btn_spellcheck = QPushButton("Spellcheck", self)
        self.btn_spellcheck.setFont(QFont("Arial", 20))
        self.btn_spellcheck.setFixedHeight(60)
        self.btn_spellcheck.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                padding: 15px;
                background-color: #FFEA00;  
                color: #000000;
            }
            QPushButton:hover {
                background-color: #FFD700;  
            }
            QPushButton:pressed {
                background-color: #FFC107;  
            }
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

        self.btn_phonetics = QPushButton("Phonetics", self)
        self.set_button_style(self.btn_phonetics)
        self.btn_phonetics.clicked.connect(self.phonetics)
        buttons_layout.addWidget(self.btn_phonetics, 2, 0)

        self.clear_btn = QPushButton("Clear", self)
        self.set_button_style(self.clear_btn)
        self.clear_btn.clicked.connect(self.clear_output)
        buttons_layout.addWidget(self.clear_btn, 2, 1)

        layout.addLayout(buttons_layout)

    def set_button_style(self, button):
        button.setFont(QFont("Arial", 20))
        button.setFixedHeight(70)
        button.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                padding: 15px;
                background-color: #2E7D32;  
                color: white;
            }
            QPushButton:hover {
                background-color: #66bb6a;  
            }
            QPushButton:pressed {
                background-color: #388e3c;  
            }
        """)

    def create_output_area(self, layout):
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Arial", 18))
        self.output_area.setStyleSheet("""
            QTextEdit {
                background-color: #2A2A2A;  
                border-radius: 20px;
                padding: 15px;
                border: 2px solid #FFEA00;  
                color: white;
            }
        """)
        layout.addWidget(self.output_area)

    def spellcheck(self):
        text = self.text_input.text()
        blob = TextBlob(text)
        corrected_text = str(blob.correct())

        if corrected_text != text:
            question = f"Did you mean: '{corrected_text}'?"
            reply = QMessageBox.question(self, 'Spell Check', question, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.text_input.setText(corrected_text)
            else:
                self.output_area.setText("No better suggestions were found.")
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
        origins = self.get_word_origin(word)

        output = f"Word: {word}\nMeanings: {meanings}\nOrigin: {origins}"
        self.output_area.setText(output)

    def get_word_origin(self, word):
        synsets = wordnet.synsets(word)
        origins = set()
        for syn in synsets:
            for lemma in syn.lemmas():
                origins.add(lemma.name())
        return origins

    def get_synonyms(self):
        word = self.text_input.text()
        synonyms = set()

        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())

        if synonyms:
            self.output_area.setText(f"Synonyms of '{word}':\n" + ", ".join(synonyms))
        else:
            self.output_area.setText(f"No synonyms found for '{word}'.")

    def clear_output(self):
        self.output_area.setText("")

    def arpabet_to_human_conversion(self, arpabet_phonemes):
    arpabet_to_human = {
        'AA': 'ah', 'AA0': 'ah', 'AA1': 'ah', 'AA2': 'ah',
        'AE': 'ae', 'AE0': 'ae', 'AE1': 'ae', 'AE2': 'ae',
        'AH': 'uh', 'AH0': 'uh', 'AH1': 'uh', 'AH2': 'uh',
        'AO': 'aw', 'AO0': 'aw', 'AO1': 'aw', 'AO2': 'aw',
        'AW': 'ow', 'AW0': 'ow', 'AW1': 'ow', 'AW2': 'ow',
        'AY': 'ai', 'AY0': 'ai', 'AY1': 'ai', 'AY2': 'ai',
        'B': 'b',
        'CH': 'ch',
        'D': 'd',
        'DH': 'th',
        'EH': 'eh', 'EH0': 'eh', 'EH1': 'eh', 'EH2': 'eh',
        'ER': 'er', 'ER0': 'er', 'ER1': 'er', 'ER2': 'er',
        'EY': 'ey', 'EY0': 'ey', 'EY1': 'ey', 'EY2': 'ey',
        'F': 'f',
        'G': 'g',
        'HH': 'h',
        'IH': 'ih', 'IH0': 'ih', 'IH1': 'ih', 'IH2': 'ih',
        'IY': 'ee', 'IY0': 'ee', 'IY1': 'ee', 'IY2': 'ee',
        'JH': 'j',
        'K': 'k',
        'L': 'l',
        'M': 'm',
        'N': 'n',
        'NG': 'ng',
        'OW': 'oh', 'OW0': 'oh', 'OW1': 'oh', 'OW2': 'oh',
        'OY': 'oi', 'OY0': 'oi', 'OY1': 'oi', 'OY2': 'oi',
        'P': 'p',
        'R': 'r',
        'S': 's',
        'SH': 'sh',
        'T': 't',
        'TH': 'th',
        'UH': 'uh', 'UH0': 'uh', 'UH1': 'uh', 'UH2': 'uh',
        'UW': 'oo', 'UW0': 'oo', 'UW1': 'oo', 'UW2': 'oo',
        'V': 'v',
        'W': 'w',
        'Y': 'y',
        'Z': 'z',
        'ZH': 'zh'
    }
    human_readable = [arpabet_to_human.get(phoneme, phoneme) for phoneme in arpabet_phonemes]
    return ' '.join(human_readable)
  def phonetics(self):
          word = self.text_input.text()
          arpabet_phonemes = g2p(word)
          human_readable_transcription = self.arpabet_to_human_conversion(arpabet_phonemes)
          self.output_area.setText(f"Phonetics: {human_readable_transcription}")
  
      def create_flashcard(self):
          word = self.text_input.text()
          if not word:
              QMessageBox.warning(self, "Error", "Please enter a word first.")
              return
  
          meaning, ok = QInputDialog.getText(self, "Create Flashcard", "Enter the meaning of the word:")
          if ok and meaning:
              synonyms, ok = QInputDialog.getText(self, "Create Flashcard", "Enter synonyms (comma-separated):")
              if ok:
                  example, ok = QInputDialog.getText(self, "Create Flashcard", "Enter an example sentence:")
                  if ok:
                      self.flashcard_manager.add_flashcard(word, meaning, synonyms, example)
                      self.update_flashcard_list()
                      self.update_progress_tracking()
                      QMessageBox.information(self, "Success", f"Flashcard for '{word}' created successfully!")
  
      def update_flashcard_list(self):
          self.flashcard_list.clear()
          for flashcard in self.flashcard_manager.get_all_flashcards():
              self.flashcard_list.addItem(flashcard.word)
  
      def review_selected_flashcard(self):
          selected_items = self.flashcard_list.selectedItems()
          if not selected_items:
              QMessageBox.warning(self, "Error", "Please select a flashcard to review.")
              return
  
          word = selected_items[0].text()
          flashcard = self.flashcard_manager.get_flashcard(word)
          if flashcard:
              review_text = f"Word: {flashcard.word}\n\n"
              review_text += f"Meaning: {flashcard.meaning}\n\n"
              review_text += f"Synonyms: {flashcard.synonyms}\n\n"
              review_text += f"Example: {flashcard.example}\n\n"
              review_text += f"Times reviewed: {flashcard.reviewed_count}\n"
              review_text += f"Correct answers: {flashcard.correct_count}"
  
              self.output_area.setText(review_text)
              self.flashcard_manager.update_flashcard_progress(word, True)
              self.update_progress_tracking()
  
      def start_quiz(self):
          flashcards = self.flashcard_manager.get_all_flashcards()
          if not flashcards:
              QMessageBox.warning(self, "Error", "No flashcards available for quiz.")
              return
  
          flashcard = random.choice(flashcards)
          user_answer, ok = QInputDialog.getText(self, "Quiz", f"What's the meaning of '{flashcard.word}'?")
          
          if ok:
              is_correct = user_answer.lower() == flashcard.meaning.lower()
              self.flashcard_manager.update_flashcard_progress(flashcard.word, is_correct)
              
              if is_correct:
                  QMessageBox.information(self, "Quiz Result", "Correct!")
              else:
                  QMessageBox.information(self, "Quiz Result", f"Incorrect. The correct meaning is: {flashcard.meaning}")
  
              self.update_progress_tracking()
  
      def delete_selected_flashcard(self):
          selected_items = self.flashcard_list.selectedItems()
          if not selected_items:
              QMessageBox.warning(self, "Error", "Please select a flashcard to delete.")
              return
  
          word = selected_items[0].text()
          reply = QMessageBox.question(self, 'Delete Flashcard', 
                                       f"Are you sure you want to delete the flashcard for '{word}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
  
          if reply == QMessageBox.StandardButton.Yes:
              self.flashcard_manager.delete_flashcard(word)
              self.update_flashcard_list()
              self.update_progress_tracking()
              QMessageBox.information(self, "Success", f"Flashcard for '{word}' deleted successfully!")
  
      def update_progress_tracking(self):
          flashcards = self.flashcard_manager.get_all_flashcards()
          total_words = len(flashcards)
          total_reviews = sum(card.reviewed_count for card in flashcards)
          total_correct = sum(card.correct_count for card in flashcards)
  
          accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
  
          progress_text = f"Total words learned: {total_words}\n"
          progress_text += f"Total reviews: {total_reviews}\n"
          progress_text += f"Correct answers: {total_correct}\n"
          progress_text += f"Accuracy: {accuracy:.2f}%\n\n"
          progress_text += "Top 5 most reviewed words:\n"
  
          sorted_flashcards = sorted(flashcards, key=lambda x: x.reviewed_count, reverse=True)
          for i, card in enumerate(sorted_flashcards[:5], 1):
              progress_text += f"{i}. {card.word} (Reviewed: {card.reviewed_count}, Correct: {card.correct_count})\n"
  
          self.progress_text.setText(progress_text)
  
  if __name__ == '__main__':
      app = QApplication(sys.argv)
      window = PhraseCraftApp()
      window.show()
      sys.exit(app.exec())
