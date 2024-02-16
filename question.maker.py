# Prompt for category name
category_name = input("Please enter the category name for your questions: ")
# File name based on category
file_name = f"{category_name}.txt"
# Questions points
points = [100, 200, 300, 400, 500]
# Open a text file to write
with open(file_name, 'w') as file:
    
    # Loop through each point value to ask questions and answers
    for point in points:
        question = input(f"Enter the question for {point} points: ")
        answer = input(f"Enter the answer for {point} points: ")
        # Format and write the question and answer to the text file
        file.write(f'{point},"{question}","{answer}"\n')

print(f"Questions and answers have been saved in '{file_name}'.")
