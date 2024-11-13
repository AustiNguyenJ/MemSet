import random
from tkinter import *
from tkinter import ttk
from datetime import datetime, timedelta
import json
import os

# Import the dictionaries directly
from FlashCards.wordlists import *

class Flashcard:
    def __init__(self):
        self.window = Tk()
        self.window.title("Korean Flashcards")
        self.window.geometry("400x600")
        self.window.configure(bg="#f0f0f0")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('Modern.TButton', 
                           font=('Arial', 12),
                           padding=10)
        self.style.configure('Modern.TMenubutton',
                           font=('Arial', 12),
                           padding=5)
        
        # Learning progress data
        self.progress_file = "learning_progress.json"
        self.load_progress()
        
        # Initialize word lists
        self.word_lists = self.load_word_lists()
        if not self.word_lists:
            raise ValueError("No word lists found!")
            
        first_set_name = list(self.word_lists.keys())[0]
        first_category = list(self.word_lists[first_set_name].keys())[0]
        
        self.current_set = first_set_name
        self.current_category = first_category
        self.current_list = self.word_lists[first_set_name][first_category]
        self.showing_korean = True
        
        # Create main frame
        main_frame = Frame(self.window, bg="#f0f0f0")
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Stats frame
        self.stats_frame = Frame(main_frame, bg="#f0f0f0")
        self.stats_frame.pack(fill='x', pady=(0, 10))
        self.stats_label = Label(
            self.stats_frame,
            text="",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.stats_label.pack()
        
        # Set selection frame
        set_frame = Frame(main_frame, bg="#f0f0f0")
        set_frame.pack(fill='x', pady=(0, 10))
        
        # Set dropdown
        self.set_var = StringVar(value=first_set_name)
        self.set_menu = ttk.OptionMenu(
            set_frame, 
            self.set_var,
            first_set_name,
            *self.word_lists.keys(),
            command=self.change_set,
            style='Modern.TMenubutton'
        )
        self.set_menu.pack(side='left', padx=5)
        
        # Category dropdown
        self.category_var = StringVar(value=first_category)
        self.category_menu = ttk.OptionMenu(
            set_frame, 
            self.category_var,
            first_category,
            *self.word_lists[first_set_name].keys(),
            command=self.change_category,
            style='Modern.TMenubutton'
        )
        self.category_menu.pack(side='right', padx=5)
        
        # Card frame
        self.card_frame = Frame(
            main_frame,
            bg="white",
            highlightbackground="#e0e0e0",
            highlightthickness=1,
        )
        self.card_frame.pack(fill='both', expand=True, pady=20)
        
        # Card content
        self.card = Label(
            self.card_frame,
            text="",
            font=("Arial", 32),
            bg="white",
            fg="#333333"
        )
        self.card.pack(expand=True, pady=40)
        
        # Button frame
        button_frame = Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill='x', pady=(20, 0))
        
        # Buttons
        self.flip_button = ttk.Button(
            button_frame,
            text="Flip",
            command=self.flip_card,
            style='Modern.TButton'
        )
        self.flip_button.pack(side='left', expand=True, padx=5)
        
        self.next_button = ttk.Button(
            button_frame,
            text="Next",
            command=self.next_card,
            style='Modern.TButton'
        )
        self.next_button.pack(side='right', expand=True, padx=5)
        
        # Learning progress buttons
        progress_frame = Frame(main_frame, bg="#f0f0f0")
        progress_frame.pack(fill='x', pady=(10, 0))
        
        self.known_button = ttk.Button(
            progress_frame,
            text="✓ I Know This",
            command=lambda: self.mark_progress(True),
            style='Modern.TButton'
        )
        self.known_button.pack(side='left', expand=True, padx=5)
        
        self.unknown_button = ttk.Button(
            progress_frame,
            text="✗ Still Learning",
            command=lambda: self.mark_progress(False),
            style='Modern.TButton'
        )
        self.unknown_button.pack(side='right', expand=True, padx=5)
        
        # Initialize first card
        self.next_card()
        
        # Bind keyboard shortcuts
        self.window.bind('<space>', lambda e: self.flip_card())
        self.window.bind('<Return>', lambda e: self.next_card())
        self.window.bind('<Right>', lambda e: self.mark_progress(True))
        self.window.bind('<Left>', lambda e: self.mark_progress(False))

    def load_word_lists(self):
        word_lists = {}
        for name, value in globals().items():
            if isinstance(value, dict) and name.startswith('korean_'):
                display_name = name[7:]  # Remove 'korean_' prefix
                word_lists[display_name] = value
        return word_lists

    def change_set(self, selection):
        self.current_set = selection
        # Update category dropdown
        menu = self.category_menu['menu']
        menu.delete(0, 'end')
        categories = self.word_lists[selection].keys()
        self.current_category = list(categories)[0]
        self.category_var.set(self.current_category)
        for category in categories:
            menu.add_command(label=category, 
                           command=lambda c=category: self.change_category(c))
        self.current_list = self.word_lists[selection][self.current_category]
        self.next_card()

    def change_category(self, selection):
        self.current_category = selection
        self.current_list = self.word_lists[self.current_set][selection]
        self.next_card()

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
        
        score = correct_count - incorrect_count + (days_since / 7)
        return score
            
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
        
    def update_stats(self):
        word = self.current_pair[0]
        if word in self.learning_progress:
            progress = self.learning_progress[word]
            correct = progress['correct']
            incorrect = progress['incorrect']
            total = correct + incorrect
            if total > 0:
                percentage = (correct / total) * 100
                stats_text = f"Success rate: {percentage:.1f}% ({correct}/{total} attempts)"
            else:
                stats_text = "New word"
        else:
            stats_text = "New word"
        self.stats_label.config(text=stats_text)
        
    def flip_card(self):
        self.showing_korean = not self.showing_korean
        self.update_display()
        
    def next_card(self):
        if not self.current_list:
            self.card.config(text="No words in this category")
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
        self.update_stats()
        
    def update_display(self):
        if self.showing_korean:
            self.card.config(text=self.current_pair[0])
            self.card_frame.configure(bg="white")
            self.card.configure(bg="white")
        else:
            self.card.config(text=self.current_pair[1])
            self.card_frame.configure(bg="#f8f8f8")
            self.card.configure(bg="#f8f8f8")
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = Flashcard()
    app.run()
