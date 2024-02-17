import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import csv
import random
import sys
import os
import json
import tkinter.simpledialog as simpledialog
from PIL import Image, ImageTk

class JeopardyGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Jeopardy Trivia Game")
        self.root.geometry("1000x800")

        # Initialize default settings before loading from file
        self.answer_time = 6000  # Default answer time in milliseconds
        self.question_directory = "question_bank"  # Default question directory

        # Some Scoreboard shit
        self.scoreboard_window = None

        # Now safe to load settings, as defaults are set
        self.load_settings_from_file()

        #Player Information update 2.16.24
        self.players = []  # Store player names
        self.player_photos = {}  # Maps player names to their photo paths
        self.player_scores = {}  # Maps player names to their scores
        self.photo_images = []

        self.categories = []
        self.category_buttons = []
        self.question_buttons = {}  # Keep track of question buttons
        self.questions = {}
        self.selected_category = None
        self.selected_question = None
        self.answer_shown = False
        self.game_in_progress = False
        self.answered_questions = set()

        # Create a main game frame
        self.game_frame = tk.Frame(self.root)
        # Don't pack or grid this frame yet; it will be done after player setup
        
        # Start with the player selection screen
        self.show_start_screen()

        self.load_categories_and_questions()
        self.create_category_buttons()
        self.create_question_buttons()

        self.create_display_with_shadow()
        self.display_frame.place_forget()
        self.shadow_label.place_forget()

        #Experimental progress bar that has been replaced with a timer
        #self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=100, mode='determinate')

        self.root.bind("`", self.open_settings)
        self.root.bind("=", self.toggle_scoreboard)
        # self.root.bind("-", lambda event: self.show_winner())  # Test hotkey to make sure the game over logic is working

    def show_start_screen(self):
        self.start_frame = tk.Frame(self.root)
        self.start_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.start_frame, text="Select number of players (1-4):").pack()
        num_players = tk.IntVar(value=1)  # Default value

        def update_players(*args):
            print("Number of players selected:", num_players.get())
            # Additional logic can be added here if needed

        num_players.trace("w", update_players)
        player_selector = tk.OptionMenu(self.start_frame, num_players, 1, 2, 3, 4)
        player_selector.pack()

        tk.Button(self.start_frame, text="Next", command=lambda: self.enter_player_names(num_players.get())).pack()


    def enter_player_names(self, num_players):
        self.start_frame.destroy()
        self.names_frame = tk.Frame(self.root)
        self.names_frame.pack(fill=tk.BOTH, expand=True)

        self.player_name_entries = []
        self.player_photo_buttons = []
        self.player_photos = {}  # This will map player names to their photo paths

        for i in range(num_players):
            tk.Label(self.names_frame, text=f"Player {i+1} Name:").pack(side=tk.TOP, fill=tk.X)
            name_entry = tk.Entry(self.names_frame)
            name_entry.pack(side=tk.TOP, fill=tk.X)
            self.player_name_entries.append(name_entry)

            # Initialize all players with a default photo path
            self.player_photos[i] = "avatar.png"  # Replace with the actual path to your default avatar

            # Create a "Choose Photo" button for each player
            photo_button = tk.Button(self.names_frame, text="Choose Photo",
                                    command=lambda i=i: self.select_player_photo(i))
            photo_button.pack(side=tk.TOP, fill=tk.X)
            self.player_photo_buttons.append(photo_button)

        tk.Button(self.names_frame, text="Start Game", command=self.finalize_players).pack(side=tk.BOTTOM)

    def display_player_list(self):
        self.player_list_window = tk.Toplevel(self.root)
        self.player_list_window.title("Select Player")

        player_frame = tk.Frame(self.player_list_window)
        player_frame.pack()

        for player_name in self.players:
            photo_path = self.player_photos[player_name]
            try:
                # Load the image
                original_photo = Image.open(photo_path)
                # Resize the photo to a uniform size, e.g., 100x100 pixels
                resized_photo = original_photo.resize((100, 100), Image.Resampling.LANCZOS)
                photo_image = ImageTk.PhotoImage(resized_photo)
                # Keep a reference to avoid garbage collection
                if not hasattr(self, 'photo_references'):
                    self.photo_references = []
                self.photo_references.append(photo_image)

                # Create and display the button with the resized photo
                player_button = tk.Button(player_frame, image=photo_image, compound=tk.TOP, text=player_name,
                                        command=lambda name=player_name: self.award_points_to_player(name))
                player_button.pack(side=tk.LEFT, padx=10, pady=10)
            except Exception as e:
                print(f"Error loading image for {player_name}: {e}")

    def show_auto_close_messagebox(self, title, message, duration=1000):
        # Create a top-level window
        messagebox = tk.Toplevel(self.root)
        messagebox.title(title)
        messagebox.geometry("300x100")  # Adjust size as necessary

        # Center the messagebox
        window_width = messagebox.winfo_reqwidth()
        window_height = messagebox.winfo_reqheight()
        position_right = int(messagebox.winfo_screenwidth()/2 - window_width/2)
        position_down = int(messagebox.winfo_screenheight()/2 - window_height/2)
        messagebox.geometry(f"+{position_right}+{position_down}")

        tk.Label(messagebox, text=message, wraplength=280).pack(side="top", fill="both", expand=True)
        # Automatically close the messagebox after 'duration' milliseconds
        messagebox.after(duration, messagebox.destroy)

    def check_game_over(self):
        expected_total_questions = 30  # For debugging
        if len(self.answered_questions) == expected_total_questions:
            self.show_winner()
            print("The game is over")
        else:
            print(f"Answered: {len(self.answered_questions)}, Expected Total: {expected_total_questions}")




    def show_winner(self):
        # Find the highest scoring player
        highest_score = max(self.player_scores.values())
        winners = [name for name, score in self.player_scores.items() if score == highest_score]
        winner_name = winners[0]  # In case of a tie, show the first winner

        winner_window = tk.Toplevel(self.root)
        winner_window.title("Game Over!")
        winner_window.geometry("400x300")  # Adjust size as necessary

        try:
            # Load and display the winner's photo
            photo_path = self.player_photos[winner_name]
            photo_image = Image.open(photo_path)
            photo_image = photo_image.resize((150, 150), Image.Resampling.LANCZOS)  # Resize photo
            photo_image = ImageTk.PhotoImage(photo_image)

            photo_label = tk.Label(winner_window, image=photo_image)
            photo_label.image = photo_image  # Keep a reference
            photo_label.pack(pady=10)

            # Display the winner's name and score
            winner_info = f"{winner_name} wins with a score of ${highest_score}!"
            winner_label = tk.Label(winner_window, text=winner_info, font=("Helvetica", 16))
            winner_label.pack(pady=10)

            # Optionally, display a trophy image or message
            trophy_label = tk.Label(winner_window, text="🏆", font=("Helvetica", 24))
            trophy_label.pack(pady=10)
        except Exception as e:
            print(f"Error displaying winner info: {e}")


    def award_points_to_player(self, player_name):
        if not self.selected_question:
            messagebox.showerror("Error", "No question selected.")
            return

        category, row = self.selected_question
        dollar_amount, _, _ = self.questions[category][row]

        try:
            points_to_award = int(dollar_amount)
        except ValueError:
            messagebox.showerror("Error", f"Invalid dollar amount: {dollar_amount}")
            return

        if player_name in self.player_scores:
            self.player_scores[player_name] += points_to_award
            # old message box - messagebox.showinfo("Points Awarded", f"{player_name} has been awarded ${points_to_award}.")
            self.show_auto_close_messagebox("Points Awarded", f"{player_name} has been awarded ${points_to_award}.", 1000)
            self.check_game_over()
            self.display_player_info()  # Update the scoreboard
            self.player_list_window.destroy()  # Close the award window
        else:
            messagebox.showerror("Error", "Player name not found. Please enter a valid player name.")
        






    def select_player_for_points(self, window, player_name, dollar_amount):
        if player_name in self.player_scores:
            self.player_scores[player_name] += int(dollar_amount)
            messagebox.showinfo("Points Awarded", f"{player_name} has been awarded ${dollar_amount}.")
        else:
            messagebox.showerror("Error", "Player name not found. Please enter a valid player name.")
        window.destroy()




    def select_player_photo(self, player_index):
        # Open file dialog to select photo for the player
        photo_path = filedialog.askopenfilename(
            title="Select Player Photo",
            filetypes=[("PNG Files", "*.png")]
        )
        print("slected photo path:", photo_path)

        if photo_path:
            self.player_photos[player_index] = photo_path
        else:
            pass
    def toggle_scoreboard(self, event=None):
        if self.scoreboard_window is not None:
            if self.scoreboard_window.state() == "normal":
                self.scoreboard_window.withdraw()  # Hide the window
            else:
                self.scoreboard_window.deiconify()  # Show the window
        else:
            # The scoreboard window hasn't been created yet, so let's create and show it
            self.display_player_info()

    def display_player_info(self):
        if self.scoreboard_window is None or not tk.Toplevel.winfo_exists(self.scoreboard_window):
            self.scoreboard_window = tk.Toplevel(self.root)
            self.scoreboard_window.title("Scoreboard")
        
        # Clear the window if it already has widgets
        for widget in self.scoreboard_window.winfo_children():
            widget.destroy()

        # Create a frame within the scoreboard window to hold player info
        scoreboard_frame = tk.Frame(self.scoreboard_window)
        scoreboard_frame.pack(fill=tk.BOTH, expand=True)
        self.scoreboard_window.state()

        for index, player_name in enumerate(self.players):
            try:
                photo_path = self.player_photos[player_name]
                original_photo = Image.open(photo_path)
                resized_photo = original_photo.resize((150, 150), Image.Resampling.LANCZOS)
                photo_image = ImageTk.PhotoImage(resized_photo)
                self.photo_images.append(photo_image)  # Store reference to avoid garbage collection

                # Display each player's photo
                photo_label = tk.Label(scoreboard_frame, image=photo_image)
                photo_label.grid(row=index, column=0, padx=10, pady=5)

                # Display player's name and score
                score_label = tk.Label(scoreboard_frame, text=f"{player_name}: ${self.player_scores.get(player_name, 0)}", font=("Helvetica", 14))
                score_label.grid(row=index, column=1, padx=10, pady=5)
            except Exception as e:
                print(f"Error displaying info for {player_name}: {e}")





    def finalize_players(self):
        # Finalize player names and photos, then start the game
        for i, entry in enumerate(self.player_name_entries):
            player_name = entry.get().strip()
            if player_name:  # Ensure the name is not empty
                self.players.append(player_name)
                # If a photo was not selected, keep the default avatar
                photo_path = self.player_photos.get(i, "avatar.png")
                self.player_photos[player_name] = photo_path
            else:
                messagebox.showerror("Error", "Player names cannot be empty.")
                return
        for player_name in self.players:
            self.player_scores[player_name] = 0

        self.names_frame.destroy()
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        self.display_player_info()
        self.start_game()


    def start_game(self):
        # Now that player setup is complete, we prepare the game UI within the game_frame

        # Ensure any previous game UI components are cleared
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        # Initialize game components that depend on player setup being complete
        self.load_categories_and_questions()

        # Instead of self.root, use self.game_frame for game UI components
        self.create_category_buttons()
        self.create_question_buttons()
        self.create_display_with_shadow()

        self.display_frame.place_forget()
        self.shadow_label.place_forget()

        # Since these elements are now part of the game frame, make sure they are placed or gridded within self.game_frame
        # Note: You don't need to pack or grid self.game_frame here if it's already been done in select_player_photos

        # Enable or disable category buttons based on game logic or state
        # test removal - self.update_category_buttons_state()

        # If there's any other setup or initialization needed for starting the game, include it here



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
        self.shadow_label = tk.Label(self.game_frame, bg="gray", font=("Helvetica", 24))
        self.shadow_label.place(relx=0.505, rely=0.505, anchor="center", relwidth=0.805, relheight=0.305)
        self.shadow_label.lower()

        self.display_frame = tk.Frame(self.game_frame, bg="blue", bd=1, relief="solid")
        self.display_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.3)

        self.question_display = tk.Label(self.display_frame, text="", bg="blue", fg="white", font=("Helvetica", 24), wraplength=690)
        self.question_display.pack(expand=True, fill=tk.BOTH, padx=1, pady=1)

         # Label for countdown timer within the display_frame
        self.timer_label = tk.Label(self.display_frame, text="", bg="blue", fg="white", font=("Helvetica", 20))
        self.timer_label.pack(side="bottom", fill="x")  # Place it at the bottom of the question display


    def load_categories_and_questions(self):
        self.questions = {}
        file_names = [file for file in os.listdir(self.question_directory) if file.endswith(".txt")]
        self.categories = random.sample(file_names, min(6, len(file_names)))

        for category in self.categories:
            with open(os.path.join(self.question_directory, category), "r") as file:
                self.questions[category] = list(csv.reader(file))
                print(f"Loaded {len(self.questions[category])} questions for category '{category}'")

        # After loading all questions, print the total count for verification
        total_questions = sum(len(questions) for questions in self.questions.values())
        print(f"Total questions loaded: {total_questions}")

    def create_category_buttons(self):
        for col, category in enumerate(self.categories):
            category_label = os.path.splitext(category)[0]
            button = tk.Button(self.game_frame, text=category_label, bg="blue", fg="white", state=tk.DISABLED, wraplength=80, height=3, width=20)
            button.grid(row=0, column=col, sticky="nsew")
            self.category_buttons.append(button)
            self.game_frame.grid_columnconfigure(col, weight=1)

    def create_question_buttons(self):
        for col, category in enumerate(self.categories):
            self.question_buttons[category] = []
            for row, question_info in enumerate(self.questions[category]):
                # print(question_info)  # Add this to see the problematic line
                dollar_amount, question, answer = question_info
                button = tk.Button(self.game_frame, text=f"${dollar_amount}", bg="blue", fg="white", height=3, width=20, command=lambda c=category, r=row: self.select_question(c, r))
                button.grid(row=row + 1, column=col, sticky="nsew")
                self.question_buttons[category].append(button)
                self.game_frame.grid_rowconfigure(row + 1, weight=1)

    def select_question(self, category, row):
        if self.answer_shown or (category, row) in self.answered_questions:
            return

        self.answered_questions.add((category, row))
        self.answer_shown = True
        self.selected_question = (category, row)

        # Extract the dollar amount, question, and answer from the selected question.
        question_info = self.questions[category][row]
        dollar_amount, question, _ = question_info

        # Display the question
        self.shadow_label.place(relx=0.505, rely=0.505, anchor="center", relwidth=0.81, relheight=0.31)
        self.display_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.3)
        self.question_display.config(text=question)

        # Blank out the button text and disable it
        self.question_buttons[category][row].config(text="", state="disabled")

        # Note: The actual awarding of points is handled elsewhere, after the answer is shown and a player is selected.
        self.start_countdown(self.answer_time // 1000)  # Ensure this is called to start the timer



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
            # Delay displaying the player list for, e.g., 3 seconds (3000 milliseconds)
            self.root.after(1000, self.display_player_list)  # Adjust the time as needed
            self.root.after(1000, self.reset_display)  # Ensure this still works as intended
        else:
            self.reset_display()

    def declare_winner(self):
        # Called at the end of the game to declare the winner
        highest_score = max(self.player_scores.values())
        winners = [name for name, score in self.player_scores.items() if score == highest_score]
        winner_text = " and ".join(winners)
        messagebox.showinfo("Game Over", f"The winner is: {winner_text} with ${highest_score}")


    def reset_display(self):
        self.shadow_label.place_forget()
        self.display_frame.place_forget()
        #self.progress.place_forget()
        self.answer_shown = False

        for cat, buttons in self.question_buttons.items():
            for row, btn in enumerate(buttons):
                if btn.winfo_exists():  # Check if the button still exists
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
        tk.Label(settings_window, text="Thank you for playing my game! - Arlen Kirkaldie Jr", fg="blue").grid(row=3, column=0, columnspan=3, sticky="w")

    def browse_for_folder(self, entry_widget):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder_selected)

    def save_settings(self, answer_time, question_dir, settings_window):
        try:
            answer_time_int = int(answer_time)
            if not 1 <= answer_time_int <= 30:
                raise ValueError("Answer time must be between 1 and 30 seconds.")
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
