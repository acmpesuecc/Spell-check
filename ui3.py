import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QGridLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from textblob import TextBlob
from nltk.corpus import wordnet
import pyttsx3
from g2p_en import G2p
import sqlite3

# Initialize text-to-speech engine
eng = pyttsx3.init()

g2p = G2p()

# User dictionary and history
user_dict = set()
history_tracking = []

class DatabaseManager:
    def __init__(self, db_name="spell_checker.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        # Create a table with two columns: history and custom_words
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history TEXT,
                custom_words TEXT
            )
        ''')
        self.connection.commit()

    def add_to_history(self, word):
        # Add a word to the history column, leaving custom_words as NULL
        self.cursor.execute('INSERT INTO words (history, custom_words) VALUES (?, NULL)', (word,))
        self.connection.commit()

    def add_to_custom_words(self, word):
        # Add a word to the custom_words column, leaving history as NULL
        self.cursor.execute('INSERT INTO words (history, custom_words) VALUES (NULL, ?)', (word,))
        self.connection.commit()

    def get_all_history(self):
        # Retrieve all words from the history column
        self.cursor.execute('SELECT history FROM words WHERE history IS NOT NULL')
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_custom_words(self):
        # Retrieve all words from the custom_words column
        self.cursor.execute('SELECT custom_words FROM words WHERE custom_words IS NOT NULL')
        return [row[0] for row in self.cursor.fetchall()]
    
    def remove_from_custom_words(self, word):
        # Remove a word from the custom_words column
        self.cursor.execute('DELETE FROM words WHERE custom_words = ?', (word,))
        self.connection.commit()

    def close(self):
        self.connection.close()

class PhraseCraftApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PhraseCraft v0.5 - Updated")
        self.setGeometry(100, 100, 1000, 700)

        self.setStyleSheet("""
            QWidget {
                background-color: #1C1C1C; 
                font-family: 'Segoe Print'; 
            }
        """)

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

        self.btn_add_dict = QPushButton("Add to My Dictionary", self)
        self.set_button_style(self.btn_add_dict)
        self.btn_add_dict.clicked.connect(self.add_to_custom_words)
        buttons_layout.addWidget(self.btn_add_dict, 1, 1)

        self.btn_display_dict = QPushButton("Display My Dictionary", self)
        self.set_button_style(self.btn_display_dict)
        self.btn_display_dict.clicked.connect(self.show_custom_words)
        buttons_layout.addWidget(self.btn_display_dict, 2, 0)

        self.btn_remove_dict = QPushButton("Remove from my Dictionary", self)
        self.set_button_style(self.btn_remove_dict)
        self.btn_remove_dict.clicked.connect(self.remove_from_custom_words)
        buttons_layout.addWidget(self.btn_remove_dict, 2, 1)

        self.btn_display_history = QPushButton("Display History", self)
        self.set_button_style(self.btn_display_history)
        self.btn_display_history.clicked.connect(self.show_history)
        buttons_layout.addWidget(self.btn_display_history, 3, 0)

        self.clear_btn = QPushButton("Clear", self)
        self.set_button_style(self.clear_btn)
        self.clear_btn.clicked.connect(self.clear_output)
        buttons_layout.addWidget(self.clear_btn, 3, 1)

        self.btn_phonetics = QPushButton("Phonetics", self)
        self.set_button_style(self.btn_phonetics)
        self.btn_phonetics.clicked.connect(self.phonetics)
        buttons_layout.addWidget(self.btn_phonetics, 4, 0)

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
        self.db.add_to_history(text)
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
################################################################################################################
    def add_to_custom_words(self):
        word = self.text_input.text()
        custom_words = self.db.get_all_custom_words()
        if word not in ", ".join(custom_words):
            self.db.add_to_custom_words(word)
            self.output_area.setText(f"'{word}' added to My Dictionary.")
        else:
            self.output_area.setText("Already in My Dictionary")

    def remove_from_custom_words(self):
        word = self.text_input.text()
        if word:
            self.db.remove_from_custom_words(word)
            self.output_area.setText("Success "+ f"'{word}' has been removed from My Dictionary.")
        else:
            self.output_area.setText("Nothing has been entered")

    def show_history(self):        
        history = self.db.get_all_history()
        if history:
            self.output_area.setText(f"History:\n" + ", ".join(history))
        else:
            self.output_area.setText("History is empty.")

    def show_custom_words(self):
        custom_words = self.db.get_all_custom_words()
        if custom_words:
            self.output_area.setText(f"My Dictionary:\n" + ", ".join(custom_words))
        else:
            self.output_area.setText("My Dictionary is empty.")
####################################################################################################################
    def clear_output(self):
        self.output_area.setText("")

    def arpabet_to_human_conversion(self,arpabet_phonemes):
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PhraseCraftApp()
    window.show()
    sys.exit(app.exec())
