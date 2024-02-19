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

def sort_items(items):
    # Sort items by their original dollar value
    return sorted(items, key=lambda x: int(x['value']))

def process_data(split_into_years, stats_label):
    filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not filename:
        messagebox.showinfo("Info", "No file selected.")
        return

    with open(filename, 'r') as file:
        data = json.load(file)

    processed_questions = 0
    categories = {}

    for item in data:
        if 'value' in item and 'category' in item and 'air_date' in item and item.get('value') not in (None, "None", "") and 'round' in item:
            try:
                item['value'] = int(item['value'].replace('$', '').replace(',', ''))
                item['question'] = clean_html(item['question'])
                item['question'] = adjust_quotes(item['question'])
                item['answer'] = adjust_quotes(item['answer'])
                round_type = item['round']

                category = item['category']
                year = item['air_date'][:4] if split_into_years else "all"
                key = (category, year, round_type)

                if key not in categories:
                    categories[key] = []
                categories[key].append(item)
            except ValueError:
                continue

    # Process each category
    for (category, year, round_type), items in categories.items():
        sorted_items = sort_items(items)  # Sort items before chunking

        chunk_size = 5
        standard_seq = [100, 200, 300, 400, 500]  # Standard sequence for Jeopardy!
        double_seq = [200, 400, 600, 800, 1000]  # Standard sequence for Double Jeopardy!

        for i, start in enumerate(range(0, len(sorted_items), chunk_size), start=0):
            chunked_items = sorted_items[start:start + chunk_size]

            # Determine the sequence to use based on the round type
            sequence_to_use = double_seq if round_type == "Double Jeopardy!" else standard_seq

            # Reassign values for the chunk based on the appropriate sequence
            for j, item in enumerate(chunked_items):
                item['value'] = sequence_to_use[j]

            category_suffix = f" -{i}" if i > 0 else ""  # Append suffix if it's a subsequent chunk
            category_name = f"{category}{category_suffix}"

            processed_questions += len(chunked_items)
            base_dir = 'JeopardyQuestions'
            question_type_dir = os.path.join(base_dir, round_type.replace(" ", ""))
            os.makedirs(question_type_dir, exist_ok=True)
            file_path = os.path.join(question_type_dir, f"{sanitize_filename(category_name)}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in chunked_items:
                    f.write(f'"{item["value"]}","{item["question"]}","{item["answer"]}"\n')

    # Update statistics
    total_questions = sum(len(items) for items in categories.values())
    stats_text = f"Total questions processed: {total_questions}\nProcessed categories: {len(categories)}"
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
