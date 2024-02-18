import tkinter as tk
from tkinter import filedialog, messagebox
import json
import re
import os

# Define utility functions
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def adjust_quotes(s):
    adjusted = s.replace('"', "'").replace("''", "'")
    return adjusted

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def process_data(split_into_years, stats_label):
    filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not filename:  # If no file is selected
        return

    with open(filename, 'r') as file:
        data = json.load(file)

    original_categories = set()
    original_questions_count = len(data)
    standard_categories = set()
    double_categories = set()
    standard_questions = 0
    double_questions = 0

    valid_categories = {}
    for item in data:
        if item.get('value') is not None and item.get('value') != "None":
            item['value'] = int(item['value'].replace('$', '').replace(',', ''))
            category = item['category']
            original_categories.add(category)
            if category not in valid_categories:
                valid_categories[category] = []
            valid_categories[category].append(item)

    categories_to_process = {k: sorted(v, key=lambda x: x['value']) for k, v in valid_categories.items() if len(v) == 5}

    for category, items in categories_to_process.items():
        sanitized_category = sanitize_filename(category)
        for item in items:
            air_date = item['air_date']
            round_type = item['round']
            year = air_date.split('-')[0]

            folder_name = "StandardJeopardyQuestions" if round_type == "Jeopardy!" else "DoubleJeopardyQuestions"
            path = os.path.join(folder_name, year if split_into_years else '')
            os.makedirs(path, exist_ok=True)

            file_path = os.path.join(path, f"{sanitized_category}.txt")

            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write(f'"{item["value"]}","{adjust_quotes(clean_html(item["question"]))}","{adjust_quotes(item["answer"])}"\n')

            if round_type == "Jeopardy!":
                standard_categories.add(category)
                standard_questions += 1
            else:
                double_categories.add(category)
                double_questions += 1

    stats_text = f"Original categories: {len(original_categories)}\n" \
                 f"Original questions: {original_questions_count}\n" \
                 f"Standard Jeopardy categories: {len(standard_categories)}\n" \
                 f"Standard Jeopardy questions: {standard_questions}\n" \
                 f"Double Jeopardy categories: {len(double_categories)}\n" \
                 f"Double Jeopardy questions: {double_questions}"

    stats_label.config(text=stats_text)
    messagebox.showinfo("Completion", "Processing completed successfully.")

# Set up the GUI
root = tk.Tk()
root.title("Jeopardy Data Processor")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

split_var = tk.BooleanVar()

split_checkbox = tk.Checkbutton(frame, text="Split into years", variable=split_var)
split_checkbox.grid(row=0, column=0, sticky="w")

stats_label = tk.Label(frame, text="", justify=tk.LEFT)
stats_label.grid(row=2, column=0, sticky="w")

process_button = tk.Button(frame, text="Process Data", command=lambda: process_data(split_var.get(), stats_label))
process_button.grid(row=1, column=0, pady=10)

root.mainloop()
