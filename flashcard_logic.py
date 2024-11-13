import random
from datetime import datetime
import json
import os
from FlashCards.wordlists import *
from tkinter import messagebox

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

        self.current_quiz_pair = None
        self.quiz_showing_korean = True
        
        self.quiz_scores = {}  # Track scores for each word
        self.locked_words = set()  # Track words that are locked (learned)
        self.current_quiz_pair = None
        self.quiz_showing_korean = True

        # Initialize UI
        from flashcard_ui import FlashcardUI
        self.ui = FlashcardUI(self)
        self.next_card()

    def start_quiz(self):
        self.next_quiz()

    def next_quiz(self):
        if not self.current_list:
            self.ui.update_quiz("No words in this category", True)
            return
            
        # Filter out locked words
        available_words = [(k, v) for k, v in self.current_list.items() 
                        if k not in self.locked_words]
        
        if not available_words:
            self.ui.update_quiz("All words in this category are learned! 🎉", True)
            return
        
        # Prioritize words with lower scores
        word_scores = [self.quiz_scores.get(word[0], 0) for word in available_words]
        max_score = max(word_scores) + 1
        probabilities = [(max_score - score) for score in word_scores]
        total = sum(probabilities)
        probabilities = [p/total for p in probabilities]
        
        self.current_quiz_pair = random.choices(available_words, probabilities)[0]
        self.quiz_showing_korean = random.choice([True, False])
        
        question = self.current_quiz_pair[0] if self.quiz_showing_korean else self.current_quiz_pair[1]
        self.ui.update_quiz(question, self.quiz_showing_korean)
        self.ui.clear_feedback()    

    def check_answer(self):
        user_answer = self.ui.answer_entry.get().strip()
        correct_answer = self.current_quiz_pair[1] if self.quiz_showing_korean else self.current_quiz_pair[0]
        word = self.current_quiz_pair[0]  # Korean word is always the key
        
        is_correct = user_answer.lower() == correct_answer.lower()
        self.manage_quiz_score(word, is_correct)
        
        if is_correct:
            score_text = f"Correct! ✨ ({self.quiz_scores[word]}/3)"
            self.ui.show_feedback(True, score_text=score_text)
            self.mark_progress(True)
        else:
            self.ui.show_feedback(False, user_answer, correct_answer)
            self.mark_progress(False)

    def reveal_answer(self):
        correct_answer = self.current_quiz_pair[1] if self.quiz_showing_korean else self.current_quiz_pair[0]
        self.ui.show_answer(correct_answer)
    
    def manage_quiz_score(self, word, is_correct):
        if word not in self.quiz_scores:
            self.quiz_scores[word] = 0
        
        if is_correct:
            self.quiz_scores[word] += 1
            if self.quiz_scores[word] >= 3:  # Word has been correct 3 times
                self.locked_words.add(word)
        else:
            self.quiz_scores[word] = max(0, self.quiz_scores[word] - 1)  # Don't go below 0

    def reset_quiz(self):
        self.quiz_scores = {}
        self.locked_words = set()
        self.next_quiz()

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
