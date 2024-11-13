import random
from datetime import datetime
import json
import os
from FlashCards.wordlists import *

class FlashcardLogic:
    def __init__(self):
        self.progress_file = "learning_progress.json"
        self.load_progress()
        self.word_lists = self.load_word_lists()
        
        if not self.word_lists:
            raise ValueError("No word lists found!")
        
        # Initialize current state
        self.current_set = list(self.word_lists.keys())[0]
        self.current_category = list(self.word_lists[self.current_set].keys())[0]
        self.current_list = self.word_lists[self.current_set][self.current_category]
        self.showing_korean = True
        self.current_pair = None
        
        # Initialize UI
        from flashcard_ui import FlashcardUI
        self.ui = FlashcardUI(self)
        self.next_card()

    def load_word_lists(self):
        word_lists = {}
        for name, value in globals().items():
            if isinstance(value, dict) and name.startswith('korean_'):
                display_name = name[7:]  # Remove 'korean_' prefix
                word_lists[display_name] = value
        return word_lists

    def load_progress(self):
        self.learning_progress = {}
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.learning_progress = json.load(f)

    def save_progress(self):
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.learning_progress, f, ensure_ascii=False, indent=2)

    def get_word_score(self, word):
        if word not in self.learning_progress:
            return 0
        
        progress = self.learning_progress[word]
        correct_count = progress['correct']
        incorrect_count = progress['incorrect']
        last_seen = datetime.fromisoformat(progress['last_seen'])
        days_since = (datetime.now() - last_seen).days
        
        return correct_count - incorrect_count + (days_since / 7)

    def change_set(self, selection):
        self.current_set = selection
        categories = self.word_lists[selection].keys()
        self.current_category = list(categories)[0]
        self.current_list = self.word_lists[selection][self.current_category]
        self.ui.update_category_menu(categories, self.current_category)
        if self.ui.showing_list:
            self.ui.update_list_view()
        self.next_card()

    def change_category(self, selection):
        self.current_category = selection
        self.current_list = self.word_lists[self.current_set][selection]
        if self.ui.showing_list:
            self.ui.update_list_view()
        self.next_card()

    def mark_progress(self, known):
        word = self.current_pair[0]
        if word not in self.learning_progress:
            self.learning_progress[word] = {
                'correct': 0,
                'incorrect': 0,
                'last_seen': datetime.now().isoformat()
            }
        
        if known:
            self.learning_progress[word]['correct'] += 1
        else:
            self.learning_progress[word]['incorrect'] += 1
        
        self.learning_progress[word]['last_seen'] = datetime.now().isoformat()
        self.save_progress()
        
        self.next_card()

    def flip_card(self):
        self.showing_korean = not self.showing_korean
        self.update_display()

    def next_card(self):
        if not self.current_list:
            self.ui.update_card("No words in this category", True)
            return
        
        words = list(self.current_list.items())
        scores = [self.get_word_score(word[0]) for word in words]
        
        max_score = max(scores) + 1
        probabilities = [(max_score - score) for score in scores]
        total = sum(probabilities)
        probabilities = [p/total for p in probabilities]
        
        self.current_pair = random.choices(words, probabilities)[0]
        self.showing_korean = True
        self.update_display()

    def update_display(self):
        self.ui.update_card(
            self.current_pair[0] if self.showing_korean else self.current_pair[1],
            self.showing_korean
        )

    def run(self):
        self.ui.run()

if __name__ == "__main__":
    app = FlashcardLogic()
    app.run()
