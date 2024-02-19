import os
import tkinter as tk
from tkinter import messagebox, simpledialog

# Paths to the folders containing the txt files
folder_paths = ['/home/bane/Dropbox/Jeopardy/Questions/Sanitized_Questions/Jeopardy!', '/home/bane/Dropbox/Jeopardy/Questions/Sanitized_Questions/DoubleJeopardy!']

# Function to count the number of questions in a file
def count_questions_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return sum(1 for line in file)

# Function to find files with less than 5 questions
def find_files_with_few_questions(folders):
    files_with_few_questions = []
    for folder in folders:
        for filename in os.listdir(folder):
            if filename.endswith('.txt'):
                file_path = os.path.join(folder, filename)
                if count_questions_in_file(file_path) < 5:
                    files_with_few_questions.append(file_path)
    return files_with_few_questions

# Function to delete files
def delete_files(files):
    for file in files:
        os.remove(file)
        print(f"Deleted {file}")

# GUI functions
def on_delete():
    if files_with_few_questions:
        response = messagebox.askyesno("Delete Files", f"Found {len(files_with_few_questions)} files with less than 5 questions. Do you want to delete these files?")
        if response:
            delete_files(files_with_few_questions)
            messagebox.showinfo("Deletion Complete", "Files deleted.")
            window.destroy()
        else:
            messagebox.showinfo("Cancelled", "No files were deleted.")
            window.destroy()
    else:
        messagebox.showinfo("No Files Found", "No files with less than 5 questions were found.")
        window.destroy()

# Main GUI application
if __name__ == '__main__':
    files_with_few_questions = find_files_with_few_questions(folder_paths)
    
    # Create the main window
    window = tk.Tk()
    window.title("File Checker")

    # Label to display information
    info_label = tk.Label(window, text=f"Found {len(files_with_few_questions)} files with less than 5 questions.", padx=10, pady=10)
    info_label.pack()

    # Button to trigger deletion
    delete_button = tk.Button(window, text="Delete Files", command=on_delete)
    delete_button.pack(pady=5)

    # Start the GUI event loop
    window.mainloop()
