#!/usr/bin/env python3

# Standard Library
import os
import random
import sys
import time
import argparse

#==============
def load_single_question_from_file(file_path: str) -> tuple:
	"""
	Load a single random question from a text file.

	Args:
		file_path (str): Path to the file containing questions.

	Returns:
		tuple: A tuple containing the question text and a list of answer-choice tuples.
	"""
	with open(file_path, 'r') as file:
		lines = file.readlines()

	# Pick a random line from the file
	line = random.choice(lines).strip()
	parts = line.split('\t')

	# Validate the format of the line
	if parts[0] != "MC" or len(parts) < 4 or (len(parts) - 2) % 2 != 0:
		raise ValueError("Invalid question format in the file.")

	# Extract question text
	question_text = parts[1]

	# Extract answer choices as a list of tuples (answer_text, is_correct)
	choices_list_of_tuples = [
		(parts[i], parts[i + 1].lower() == "correct") for i in range(2, len(parts), 2)
	]

	return question_text, choices_list_of_tuples

#==============
def generate_html(question_text, choices_list_of_tuples):
	"""
	Generate an HTML file for a single multiple-choice question.

	Args:
		question (dict): A dictionary containing question text and options.
		output_file (str): Path to save the generated HTML file.
	"""
	html_content = ""
	# Add DOCTYPE and opening HTML tag
	html_content += "<!DOCTYPE html>\n"
	html_content += "<html lang=\"en\">\n"
	# Add head section with metadata and title
	html_content += "<head>\n"
	html_content += "<meta charset=\"UTF-8\">\n"
	html_content += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
	html_content += "<title>MC Question</title>\n"
	# Add JavaScript function
	html_content += generate_javascript()
	html_content += "</head>\n"
	# Open body section
	html_content += "<body>\n"
	# Add question header
	html_content += "<h1>Multiple Choice Question</h1>\n"
	# Add question text
	html_content += f"<p>{question_text}</p>\n"
	# Open form tag
	html_content += "<form>\n"

	# Add options dynamically
	for idx, option_tuple in enumerate(choices_list_of_tuples):
		choice_text, correct_bool = option_tuple
		html_content += f"<div>\n"
		html_content += f"<input type=\"radio\" id=\"option{idx}\" name=\"answer\" data-correct=\"{str(correct_bool).lower()}\">\n"
		html_content += f"<label for=\"option{idx}\">{choice_text}</label>\n"
		html_content += "</div>\n"

	# Add check button
	html_content += "<button type=\"button\" onclick=\"checkAnswer()\">Check</button>\n"
	# Close form tag
	html_content += "</form>\n"
	# Add result div
	html_content += "<div id=\"result\"></div>\n"
	# Close body and HTML tags
	html_content += "</body>\n"
	html_content += "</html>\n"

	return html_content

#==============
def generate_javascript() -> str:
	"""
	Generate the JavaScript code for the HTML file.

	Returns:
		str: JavaScript code as a string.
	"""
	javascript_html = "<script>\n"
	# Open the function
	javascript_html += "function checkAnswer() {\n"
	# Set options constant to get all options from the form
	javascript_html += "const options = document.getElementsByName('answer');\n"
	# Initialize correctOption variable to null
	javascript_html += "let correctOption = null;\n"

	# Loop through options to find the correct one
	javascript_html += "for (let i = 0; i < options.length; i++) {\n"
	javascript_html += "if (options[i].dataset.correct === 'true') {\n"
	javascript_html += "correctOption = options[i];\n"
	javascript_html += "}\n"  # Close if statement
	javascript_html += "}\n"  # Close for loop

	# Get the selected option
	javascript_html += "const selected = Array.from(options).find(option => option.checked);\n"
	# Get the result div to display feedback
	javascript_html += "const resultDiv = document.getElementById('result');\n"

	# Check if a selection is made
	javascript_html += "if (selected) {\n"
	# If the selection is correct
	javascript_html += "if (selected === correctOption) {\n"
	javascript_html += "resultDiv.style.color = 'green';\n"
	javascript_html += "resultDiv.textContent = 'CORRECT';\n"
	javascript_html += "} else {\n"  # If the selection is incorrect
	javascript_html += "resultDiv.style.color = 'red';\n"
	javascript_html += "resultDiv.textContent = 'incorrect';\n"
	javascript_html += "}\n"  # Close else
	javascript_html += "} else {\n"  # If no selection is made
	javascript_html += "resultDiv.style.color = 'black';\n"
	javascript_html += "resultDiv.textContent = 'Please select an answer.';\n"
	javascript_html += "}\n"  # Close else

	# Close the function
	javascript_html += "}\n"
	javascript_html += "</script>\n"

	return javascript_html

#==============
def get_parser() -> argparse.Namespace:
	"""
	Set up argument parser for command-line inputs.

	Returns:
		argparse.Namespace: Parsed command-line arguments.
	"""
	parser = argparse.ArgumentParser(description="Generate an HTML MC question from a text file.")
	parser.add_argument('-f', '--file', dest='file_path', required=True, help='Path to the questions text file.')
	parser.add_argument('-o', '--output', dest='output_file', default='mc_question.html', help='Output HTML file name.')
	args = parser.parse_args()
	return args

#==============
def main() -> None:
	"""
	Main function to execute the program.
	Handles argument parsing, question loading, and HTML generation.
	"""
	args = get_parser()

	file_path = args.file_path

	if not os.path.exists(file_path):
		print(f"Error: File {file_path} not found.")
		sys.exit(1)

	question_text, choices_list_of_tuples = load_single_question_from_file(file_path)

	# Generate the HTML file
	html_content = generate_html(question_text, choices_list_of_tuples)

	# Write the constructed HTML to the output file
	with open(args.output_file, 'w') as file:
		file.write(html_content)

	print(f"HTML file generated: {args.output_file}")

#==============
if __name__ == "__main__":
	main()
