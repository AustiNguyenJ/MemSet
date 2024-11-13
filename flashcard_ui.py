from tkinter import *
from tkinter import ttk,messagebox

class FlashcardUI:
    def __init__(self, controller):
        self.controller = controller
        self.window = Tk()
        self.setup_window()
        self.setup_styles()
        self.showing_list = False
        self.showing_quiz = False  # New flag for quiz mode
        self.create_widgets()
        self.bind_shortcuts()

    def setup_window(self):
        self.window.title("MemSet - Korean Flashcards")
        self.window.geometry("1000x700")
        self.window.configure(bg="#ffffff")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        self.style.configure(
            'Quiz.TButton',
            font=('Helvetica', 11),
            padding=8,
            background='#9c27b0',
            borderwidth=0,
            relief='flat'
        )
        self.style.map('Quiz.TButton',
            background=[('active', '#ab47bc')]
        )

        # Modern button style with subtle hover effect
        self.style.configure(
            'Modern.TButton',
            font=('Helvetica', 11),
            padding=10,
            background='#4a90e2',
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            relief='flat'
        )
        self.style.map('Modern.TButton',
            background=[('active', '#5a9ee2')],
            relief=[('pressed', 'flat'),
                ('!pressed', 'flat')]
        )
        
        # Minimalist dropdown style
        self.style.configure(
            'Modern.TMenubutton',
            font=('Helvetica', 11),
            padding=8,
            background='#ffffff',
            arrowcolor='#4a90e2',
            borderwidth=1,
            relief='flat'
        )
        self.style.map('Modern.TMenubutton',
            background=[('active', '#f8f8f8')],
            relief=[('pressed', 'flat'),
                ('!pressed', 'flat')]
        )
        
        # Toggle button style
        self.style.configure(
            'Toggle.TButton',
            font=('Helvetica', 11),
            padding=8,
            background='#f0f0f0',
            borderwidth=0,
            relief='flat'
        )
        self.style.map('Toggle.TButton',
            background=[('active', '#e8e8e8')]
        )
        
        # Known/Unknown button styles
        self.style.configure(
            'Correct.TButton',
            font=('Helvetica', 11),
            padding=10,
            background='#4caf50',
            borderwidth=0,
            relief='flat'
        )
        self.style.map('Correct.TButton',
            background=[('active', '#5cb860')]
        )
        
        self.style.configure(
            'Incorrect.TButton',
            font=('Helvetica', 11),
            padding=10,
            background='#f44336',
            borderwidth=0,
            relief='flat'
        )
        self.style.map('Incorrect.TButton',
            background=[('active', '#f55549')]
        )

        # Minimal scrollbar style
        self.style.configure(
            "Modern.Vertical.TScrollbar",
            background="#e0e0e0",
            bordercolor="#ffffff",
            arrowcolor="#999999",
            troughcolor="#ffffff",
            width=8,
            relief="flat"
        )
        self.style.map("Modern.Vertical.TScrollbar",
            background=[('active', '#d0d0d0'),
                    ('disabled', '#f0f0f0')]
        )

    def create_widgets(self):
        # Main container
        self.container = Frame(self.window, bg="#ffffff")
        self.container.pack(expand=True, fill='both', padx=30, pady=20)
        
        # Header frame
        header_frame = Frame(self.container, bg="#ffffff")
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title and view toggle in same row
        title_toggle_frame = Frame(header_frame, bg="#ffffff")
        title_toggle_frame.pack(fill='x')
        
        # Title
        title_label = Label(
            title_toggle_frame,
            text="Korean Flashcards",
            font=("Helvetica", 24, "bold"),
            bg="#ffffff",
            fg="#333333"
        )
        title_label.pack(side='left', pady=(0, 10))
        
        # View buttons frame
        view_buttons_frame = Frame(title_toggle_frame, bg="#ffffff")
        view_buttons_frame.pack(side='right', pady=(0, 10))
        
        # Quiz mode button
        self.quiz_button = ttk.Button(
            view_buttons_frame,
            text="✍ Quiz Mode",
            command=self.toggle_quiz,
            style='Quiz.TButton'
        )
        self.quiz_button.pack(side='left', padx=5)
        
        # Study list button
        self.toggle_button = ttk.Button(
            view_buttons_frame,
            text="📋 Study List",
            command=self.toggle_view,
            style='Toggle.TButton'
        )
        self.toggle_button.pack(side='left')
        
        # Content frame to hold all views
        self.content_frame = Frame(self.container, bg="#ffffff")
        self.content_frame.pack(fill='both', expand=True)
        
        # Create all views
        self.create_flashcard_view()
        self.create_list_view()
        self.create_quiz_view()
        
        # Initially show only flashcard view
        self.flashcard_frame.pack(in_=self.content_frame, fill='both', expand=True)

    def create_flashcard_view(self):
        self.flashcard_frame = Frame(self.container, bg="#ffffff")
        
        # Set selection frame
        set_frame = Frame(self.flashcard_frame, bg="#ffffff")
        set_frame.pack(fill='x', pady=(0, 20))
        
        # Set dropdown
        self.set_var = StringVar(value=self.controller.current_set)
        self.set_menu = ttk.OptionMenu(
            set_frame, 
            self.set_var,
            self.controller.current_set,
            *self.controller.word_lists.keys(),
            command=self.controller.change_set,
            style='Modern.TMenubutton'
        )
        self.set_menu.pack(side='left', padx=5, fill='x', expand=True)
        
        # Category dropdown
        self.category_var = StringVar(value=self.controller.current_category)
        self.category_menu = ttk.OptionMenu(
            set_frame, 
            self.category_var,
            self.controller.current_category,
            *self.controller.word_lists[self.controller.current_set].keys(),
            command=self.controller.change_category,
            style='Modern.TMenubutton'
        )
        self.category_menu.pack(side='right', padx=5, fill='x', expand=True)
        
        # Card frame
        self.card_frame = Frame(
            self.flashcard_frame,
            bg="white",
            highlightbackground="#e0e0e0",
            highlightthickness=1,
            relief="solid",
            bd=1
        )
        self.card_frame.pack(fill='both', expand=True, pady=20)
        
        # Card content
        self.card = Label(
            self.card_frame,
            text="",
            font=("Helvetica", 36),
            bg="white",
            fg="#333333"
        )
        self.card.pack(expand=True, pady=60)
        
        # Control buttons frame
        control_frame = Frame(self.flashcard_frame, bg="#ffffff")
        control_frame.pack(fill='x', pady=(20, 0))
        
        # Flip and Next buttons
        self.flip_button = ttk.Button(
            control_frame,
            text="↻ Flip",
            command=self.controller.flip_card,
            style='Modern.TButton'
        )
        self.flip_button.pack(side='left', expand=True, padx=5)
        
        self.next_button = ttk.Button(
            control_frame,
            text="→ Next",
            command=self.controller.next_card,
            style='Modern.TButton'
        )
        self.next_button.pack(side='right', expand=True, padx=5)
        
        # Progress buttons frame
        progress_frame = Frame(self.flashcard_frame, bg="#ffffff")
        progress_frame.pack(fill='x', pady=(15, 0))
        
        # Known/Unknown buttons
        self.known_button = ttk.Button(
            progress_frame,
            text="✓ I Know This",
            command=lambda: self.controller.mark_progress(True),
            style='Correct.TButton'
        )
        self.known_button.pack(side='left', expand=True, padx=5)
        
        self.unknown_button = ttk.Button(
            progress_frame,
            text="✗ Still Learning",
            command=lambda: self.controller.mark_progress(False),
            style='Incorrect.TButton'
        )
        self.unknown_button.pack(side='right', expand=True, padx=5)
        
        # Shortcuts info
        shortcuts_frame = Frame(self.flashcard_frame, bg="#ffffff")
        shortcuts_frame.pack(fill='x', pady=(20, 0))
        
        shortcuts_label = Label(
            shortcuts_frame,
            text="Shortcuts: Space (Flip) | Enter (Next) | ←→ (Mark Progress)",
            font=("Helvetica", 9),
            bg="#ffffff",
            fg="#999999"
        )
        shortcuts_label.pack()

    def create_list_view(self):
        self.list_frame = Frame(self.container, bg="#ffffff")
        
        # Main scrollable container
        self.canvas = Canvas(self.list_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self.list_frame,
            orient="vertical",
            command=self.canvas.yview,
            style="Modern.Vertical.TScrollbar"
        )
        self.scrollable_frame = Frame(self.canvas, bg="#ffffff")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=940)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Add hover effect to canvas
        self.canvas.bind('<Enter>', lambda e: self._bind_mousewheel())
        self.canvas.bind('<Leave>', lambda e: self._unbind_mousewheel())

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_list_view(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        header = Label(
            self.scrollable_frame,
            text=f"{self.controller.current_set}",
            font=("Helvetica", 18, "bold"),
            bg="#ffffff",
            fg="#333333"
        )
        header.pack(pady=(0, 20), anchor='w')

        columns_frame = Frame(self.scrollable_frame, bg="#ffffff")
        columns_frame.pack(fill='x', expand=True)

        left_column = Frame(columns_frame, bg="#ffffff")
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_column = Frame(columns_frame, bg="#ffffff")
        right_column.pack(side='right', fill='both', expand=True, padx=(10, 0))

        current_set_data = self.controller.word_lists[self.controller.current_set]
        total_items = sum(len(words) for words in current_set_data.values())
        target_items_per_column = total_items / 2

        current_column = left_column
        current_count = 0
        
        for category, words in current_set_data.items():
            if current_count >= target_items_per_column and current_column == left_column:
                current_column = right_column
            
            category_frame = Frame(current_column, bg="#ffffff")
            category_frame.pack(fill='x', pady=(5, 0))
            
            category_header = Label(
                category_frame,
                text=category,
                font=("Helvetica", 14, "bold"),
                bg="#ffffff",
                fg="#4a90e2"
            )
            category_header.pack(anchor='w')

            for korean, english in words.items():
                word_frame = Frame(current_column, bg="#ffffff")
                word_frame.pack(fill='x', pady=2)
                
                text_frame = Frame(word_frame, bg="#ffffff")
                text_frame.pack(side='left', fill='x', expand=True)
                
                korean_label = Label(
                    text_frame,
                    text=korean,
                    font=("Helvetica", 12),
                    bg="#ffffff",
                    fg="#333333",
                    width=20,
                    anchor='w'
                )
                korean_label.pack(side='left')
                
                english_label = Label(
                    text_frame,
                    text=english,
                    font=("Helvetica", 12),
                    bg="#ffffff",
                    fg="#666666",
                    anchor='w'
                )
                english_label.pack(side='left', padx=(10, 0))
                
                current_count += 1

            Frame(current_column, height=10, bg="#ffffff").pack()

    def toggle_view(self):
        self.flashcard_frame.pack_forget()
        self.list_frame.pack_forget()
        self.quiz_frame.pack_forget()
        
        self.showing_list = not self.showing_list
        self.showing_quiz = False
        
        if self.showing_list:
            self.list_frame.pack(in_=self.content_frame, fill='both', expand=True)
            self.toggle_button.configure(text="🎴 Flashcards")
            self.quiz_button.configure(state='disabled')
            self.update_list_view()
        else:
            self.flashcard_frame.pack(in_=self.content_frame, fill='both', expand=True)
            self.toggle_button.configure(text="📋 Study List")
            self.quiz_button.configure(state='normal')

    def bind_shortcuts(self):
        self.window.bind('<space>', lambda e: self.controller.flip_card())
        self.window.bind('<Return>', lambda e: self.controller.next_card())
        self.window.bind('<Right>', lambda e: self.controller.mark_progress(True))
        self.window.bind('<Left>', lambda e: self.controller.mark_progress(False))

    def update_card(self, text, is_korean):
        self.card.config(text=text)
        if is_korean:
            self.card_frame.configure(bg="white")
            self.card.configure(bg="white")
        else:
            self.card_frame.configure(bg="#f8f8f8")
            self.card.configure(bg="#f8f8f8")

    def update_category_menu(self, categories, current_category):
        menu = self.category_menu['menu']
        menu.delete(0, 'end')
        self.category_var.set(current_category)
        for category in categories:
            menu.add_command(
                label=category, 
                command=lambda c=category: self.controller.change_category(c)
            )

    def create_quiz_view(self):
        self.quiz_frame = Frame(self.container, bg="#ffffff")
        
        # Set selection frame
        set_frame = Frame(self.quiz_frame, bg="#ffffff")
        set_frame.pack(fill='x', pady=(0, 20))
        
        self.quiz_set_var = StringVar(value=self.controller.current_set)
        self.quiz_set_menu = ttk.OptionMenu(
            set_frame, 
            self.quiz_set_var,
            self.controller.current_set,
            *self.controller.word_lists.keys(),
            command=self.controller.change_set,
            style='Modern.TMenubutton'
        )
        self.quiz_set_menu.pack(side='left', padx=5, fill='x', expand=True)
        
        self.quiz_category_var = StringVar(value=self.controller.current_category)
        self.quiz_category_menu = ttk.OptionMenu(
            set_frame, 
            self.quiz_category_var,
            self.controller.current_category,
            *self.controller.word_lists[self.controller.current_set].keys(),
            command=self.controller.change_category,
            style='Modern.TMenubutton'
        )
        self.quiz_category_menu.pack(side='right', padx=5, fill='x', expand=True)
        
        # Question frame
        self.question_frame = Frame(self.quiz_frame, bg="white", pady=20)
        self.question_frame.pack(fill='x')
        
        self.question_label = Label(
            self.question_frame,
            text="",
            font=("Helvetica", 24),
            bg="white",
            fg="#333333",
            wraplength=800
        )
        self.question_label.pack()
        
        # Answer frame
        answer_frame = Frame(self.quiz_frame, bg="#ffffff")
        answer_frame.pack(fill='x', pady=20)
        
        self.answer_entry = ttk.Entry(
            answer_frame,
            font=("Helvetica", 18),
            width=40
        )
        self.answer_entry.pack(pady=10)
        
        # Feedback frame
        self.feedback_frame = Frame(self.quiz_frame, bg="#ffffff")
        self.feedback_frame.pack(fill='x', pady=(0, 20))
        
        self.feedback_label = Label(
            self.feedback_frame,
            text="",
            font=("Helvetica", 14),
            bg="#ffffff",
            wraplength=800
        )
        self.feedback_label.pack()
        
        # Button frame
        button_frame = Frame(self.quiz_frame, bg="#ffffff")
        button_frame.pack(fill='x', pady=10)
        
        self.check_button = ttk.Button(
            button_frame,
            text="Check Answer",
            command=self.controller.check_answer,
            style='Modern.TButton'
        )
        self.check_button.pack(side='left', expand=True, padx=5)
        
        self.reveal_button = ttk.Button(
            button_frame,
            text="Reveal Answer",
            command=self.controller.reveal_answer,
            style='Toggle.TButton'
        )
        self.reveal_button.pack(side='left', expand=True, padx=5)
        
        self.next_quiz_button = ttk.Button(
            button_frame,
            text="Next Question",
            command=self.controller.next_quiz,
            style='Modern.TButton'
        )
        self.next_quiz_button.pack(side='right', expand=True, padx=5)

        self.reset_button = ttk.Button(
            button_frame,
            text="Reset Progress",
            command=self.controller.reset_quiz,
            style='Toggle.TButton'
        )
        self.reset_button.pack(side='right', expand=True, padx=5)
        
        # Bind Enter key to check answer
        self.answer_entry.bind('<Return>', lambda e: self.controller.check_answer())

    def show_feedback(self, is_correct, user_answer="", correct_answer="", score_text=None):
        if is_correct:
            self.feedback_label.config(
                text=score_text if score_text else "Correct! ✨",
                fg="#4caf50"
            )
        else:
            self.feedback_label.config(
                text=f"Incorrect\nYour answer: {user_answer}\nCorrect answer: {correct_answer}",
                fg="#f44336"
            )

    def clear_feedback(self):
        self.feedback_label.config(text="")

    def show_answer(self, answer):
        self.feedback_label.config(
            text=f"The correct answer is:\n{answer}",
            fg="#4a90e2"
        )

    def update_quiz(self, question, is_korean):
        self.question_label.config(text=question)
        self.answer_entry.delete(0, END)
        self.answer_entry.focus()

    def toggle_quiz(self):
        # Hide all frames first
        self.flashcard_frame.pack_forget()
        self.list_frame.pack_forget()
        self.quiz_frame.pack_forget()
        
        self.showing_quiz = not self.showing_quiz
        self.showing_list = False
        
        if self.showing_quiz:
            self.quiz_frame.pack(in_=self.content_frame, fill='both', expand=True)
            self.quiz_button.configure(text="🎴 Flashcards")
            self.toggle_button.configure(state='disabled')
            self.controller.reset_quiz()  # Reset quiz when starting new session
        else:
            self.flashcard_frame.pack(in_=self.content_frame, fill='both', expand=True)
            self.quiz_button.configure(text="✍ Quiz Mode")
            self.toggle_button.configure(state='normal')



    def run(self):
        self.window.mainloop()