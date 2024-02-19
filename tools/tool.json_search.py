import tkinter as tk
from tkinter import filedialog, scrolledtext, simpledialog
import json

class JSONSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Search Tool")
        self.json_data = None

        # Frame for Load Button
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Load Button
        load_button = tk.Button(frame, text="Load JSON File", command=self.load_json_file)
        load_button.pack(side=tk.LEFT, padx=5)

        # Display Keys
        self.keys_text = tk.Text(frame, height=10, width=50)
        self.keys_text.pack(side=tk.LEFT, padx=5)

        # Search Term Entry
        self.search_entry = tk.Entry(frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Search Button
        search_button = tk.Button(frame, text="Search", command=self.search_json)
        search_button.pack(side=tk.LEFT, padx=5)

        # Results Display
        self.results_text = scrolledtext.ScrolledText(self.root, height=15, width=100)
        self.results_text.pack(pady=10)

    def load_json_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                self.json_data = json.load(file)
                self.display_keys()

    def display_keys(self):
        if self.json_data:
            keys = self.extract_keys(self.json_data)
            self.keys_text.delete('1.0', tk.END)
            self.keys_text.insert(tk.END, "\n".join(keys))

    def extract_keys(self, obj, prefix=''):
        keys = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                keys.extend(self.extract_keys(v, prefix + k + '.'))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                keys.extend(self.extract_keys(v, prefix + str(i) + '.'))
        else:
            keys.append(prefix.rstrip('.'))
        return keys

    def search_json(self):
        search_term = self.search_entry.get()
        if self.json_data and search_term:
            self.results_text.delete('1.0', tk.END)
            results = []
            self.find_in_json(self.json_data, search_term, results)
            if results:
                formatted_results = "\n\n".join([json.dumps(result, indent=4, ensure_ascii=False) for result in results])
            else:
                formatted_results = "No results found."
            self.results_text.insert(tk.END, formatted_results)

    def find_in_json(self, data, search_term, results):
        if isinstance(data, dict):
            if search_term.lower() in json.dumps(data, ensure_ascii=False).lower():
                results.append(data)
            else:
                for value in data.values():
                    self.find_in_json(value, search_term, results)
        elif isinstance(data, list):
            for item in data:
                self.find_in_json(item, search_term, results)

root = tk.Tk()
app = JSONSearchGUI(root)
root.mainloop()
