import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import random
import sys
import os
import json

class JeopardyGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Jeopardy Trivia Game")
        self.root.geometry("1000x800")

        # Initialize default settings before loading from file
        self.answer_time = 6000  # Default answer time in milliseconds
        self.question_directory = "question_bank"  # Default question directory

        # Now safe to load settings, as defaults are set
        self.load_settings_from_file()

        self.categories = []
        self.category_buttons = []
        self.question_buttons = {}  # Keep track of question buttons
        self.questions = {}
        self.selected_category = None
        self.selected_question = None
        self.answer_shown = False
        self.game_in_progress = False
        self.answered_questions = set()

        self.load_categories_and_questions()
        self.create_category_buttons()
        self.create_question_buttons()

        self.create_display_with_shadow()
        self.display_frame.place_forget()
        self.shadow_label.place_forget()

        #Experimental progress bar that has been replaced with a timer
        #self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=100, mode='determinate')

        self.root.bind("<s>", self.open_settings)


    def load_settings_from_file(self):
        try:
            with open('game_settings.json', 'r') as f:
                settings = json.load(f)
                self.answer_time = settings.get('answer_time', 6000)
                self.question_directory = settings.get('question_directory', 'question_bank')
        except FileNotFoundError:
            self.save_settings_to_file()

    def save_settings_to_file(self):
        settings = {
            'answer_time': self.answer_time,
            'question_directory': self.question_directory,
        }
        with open('game_settings.json', 'w') as f:
            json.dump(settings, f)

    def create_display_with_shadow(self):
        self.shadow_label = tk.Label(self.root, bg="gray", font=("Helvetica", 24))
        self.shadow_label.place(relx=0.505, rely=0.505, anchor="center", relwidth=0.805, relheight=0.305)
        self.shadow_label.lower()

        self.display_frame = tk.Frame(self.root, bg="blue", bd=1, relief="solid")
        self.display_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.3)

        self.question_display = tk.Label(self.display_frame, text="", bg="blue", fg="white", font=("Helvetica", 24), wraplength=690)
        self.question_display.pack(expand=True, fill=tk.BOTH, padx=1, pady=1)

         # Label for countdown timer within the display_frame
        self.timer_label = tk.Label(self.display_frame, text="", bg="blue", fg="white", font=("Helvetica", 20))
        self.timer_label.pack(side="bottom", fill="x")  # Place it at the bottom of the question display


    def load_categories_and_questions(self):
        file_names = [file for file in os.listdir(self.question_directory) if file.endswith(".txt")]
        self.categories = random.sample(file_names, min(6, len(file_names)))

        for category in self.categories:
            with open(os.path.join(self.question_directory, category), "r") as file:
                self.questions[category] = list(csv.reader(file))

    def create_category_buttons(self):
        for col, category in enumerate(self.categories):
            category_label = os.path.splitext(category)[0]
            button = tk.Button(self.root, text=category_label, bg="blue", fg="white", state=tk.DISABLED)
            button.grid(row=0, column=col, sticky="nsew")
            self.category_buttons.append(button)
            self.root.grid_columnconfigure(col, weight=1)

    def create_question_buttons(self):
        for col, category in enumerate(self.categories):
            self.question_buttons[category] = []
            for row, question_info in enumerate(self.questions[category]):
                dollar_amount, question, answer = question_info
                button = tk.Button(self.root, text=f"${dollar_amount}", command=lambda c=category, r=row: self.select_question(c, r), bg="blue", fg="white")
                button.grid(row=row + 1, column=col, sticky="nsew")
                self.question_buttons[category].append(button)
                self.root.grid_rowconfigure(row + 1, weight=1)

    def select_question(self, category, row):
        if self.answer_shown or (category, row) in self.answered_questions:
            return

        self.answered_questions.add((category, row))
        self.answer_shown = True
        self.selected_question = (category, row)

        _, question, _ = self.questions[category][row]
        
        # Display setup
        self.shadow_label.place(relx=0.505, rely=0.505, anchor="center", relwidth=0.81, relheight=0.31)
        self.display_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.3)
        self.question_display.config(text=question)
        #self.progress.place(relx=0.5, rely=0.9, anchor="center", relwidth=0.8)
        
        # Start countdown
        self.start_countdown(self.answer_time // 1000)

        # Disable all question buttons
        for cat, buttons in self.question_buttons.items():
            for btn in buttons:
                btn.config(state=tk.DISABLED)

    def start_countdown(self, remaining_seconds):
        if remaining_seconds >= 0:
            self.timer_label.config(text=str(remaining_seconds))
            self.root.after(1000, self.start_countdown, remaining_seconds - 1)
        else:
            # Time's up: display the answer
            self.display_answer(show_answer=True)

    def start_progress_bar(self):
        self.progress['value'] = 0
        self.update_progress_bar(60)

    def update_progress_bar(self, steps_remaining):
        if steps_remaining > 0:
            self.progress['value'] += 100 / 60
            self.root.after(100, self.update_progress_bar, steps_remaining - 1)

    def display_answer(self, show_answer=False):
        category, row = self.selected_question
        _, _, answer = self.questions[category][row]
        if show_answer:
            self.question_display.config(text=f"Answer: {answer}")
            self.root.after(4000, self.reset_display)
        else:
            self.reset_display()

    def reset_display(self):
        self.shadow_label.place_forget()
        self.display_frame.place_forget()
        #self.progress.place_forget()
        self.answer_shown = False

        for cat, buttons in self.question_buttons.items():
            for row, btn in enumerate(buttons):
                if (cat, row) not in self.answered_questions:
                    btn.config(state=tk.NORMAL)

    def open_settings(self, event=None):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        tk.Label(settings_window, text="Answer Time (seconds):").grid(row=0, column=0, sticky="w")
        answer_time_entry = tk.Entry(settings_window)
        answer_time_entry.insert(0, str(self.answer_time // 1000))
        answer_time_entry.grid(row=0, column=1, sticky="ew")

        tk.Label(settings_window, text="Question Directory:").grid(row=1, column=0, sticky="w")
        question_dir_entry = tk.Entry(settings_window)
        question_dir_entry.insert(0, self.question_directory)
        question_dir_entry.grid(row=1, column=1, sticky="ew")

        tk.Button(settings_window, text="Browse", command=lambda: self.browse_for_folder(question_dir_entry)).grid(row=1, column=2)
        tk.Button(settings_window, text="Save", command=lambda: self.save_settings(answer_time_entry.get(), question_dir_entry.get(), settings_window)).grid(row=2, column=0, columnspan=3)
        tk.Label(settings_window, text="Thank you for playing my game! - The Creator", fg="blue").grid(row=3, column=0, columnspan=3, sticky="w")

    def browse_for_folder(self, entry_widget):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder_selected)

    def save_settings(self, answer_time, question_dir, settings_window):
        try:
            answer_time_int = int(answer_time)
            if not 3 <= answer_time_int <= 30:
                raise ValueError("Answer time must be between 3 and 30 seconds.")
            self.answer_time = answer_time_int * 1000
            self.question_directory = question_dir

            self.save_settings_to_file()
            settings_window.destroy()
            messagebox.showinfo("Settings Saved", "Your settings have been saved successfully. The program will now restart.")

            # Restart the program
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    game = JeopardyGame(root)
    root.mainloop()
