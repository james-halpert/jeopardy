# Prompt for category name
category_name = input("Please enter the category name for your questions: ")
# File name based on category
file_name = f"{category_name}.txt"
# Questions points
points = [100, 200, 300, 400, 500]
# Open a text file to write
with open(file_name, 'w', newline='') as file:
    # Loop through each point value to ask questions, answers, and optionally media filenames
    for point in points:
        question = input(f"Enter the question for {point} points: ")
        answer = input(f"Enter the answer for {point} points: ")
        # New - Prompt for an optional media filename
        media_filename = input(f"Enter the media filename for {point} points (leave blank if none): ")
        # Ensure the media filename is properly formatted or left out if blank
        media_entry = f',"{media_filename}"' if media_filename else ''
        # Format and write the question, answer, and optional media filename to the text file
        file.write(f'{point},"{question}","{answer}"{media_entry}\n')

print(f"Questions and answers have been saved in '{file_name}'.")
