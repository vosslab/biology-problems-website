#!/usr/bin/env python3

# Standard Library
import os
import re
import sys
import random
import argparse

# External Library for HTML manipulation
from lxml import html, etree

#==============
def format_html(html_string):
	"""
	Format an HTML string to be more readable by removing excess whitespace and adding proper indentation.

	Args:
		html_string (str): The HTML content to be formatted.

	Returns:
		str: The formatted HTML string.
	"""
	return format_html_lxml(html_string)

#==============
def format_html_lxml(html_string):
	"""
	Format an HTML string using lxml library for cleaner output.

	Args:
		html_string (str): The HTML content to be formatted.

	Returns:
		str: The formatted HTML string.
	"""
	# Initialize HTML parser to remove blank text nodes
	parser = html.HTMLParser(remove_blank_text=True)
	tree = html.fromstring(html_string, parser=parser)

	# Convert the parsed HTML tree to a formatted string
	formatted_html = etree.tostring(tree, pretty_print=True, encoding="unicode").strip()
	formatted_html = etree.tostring(tree, pretty_print=True, encoding="unicode", method="html").strip()
	return formatted_html

#==============
def load_single_question_from_file(file_path: str) -> tuple:
	"""
	Load a single random multiple-choice question from a file.

	Args:
		file_path (str): Path to the file containing questions.

	Returns:
		tuple: A tuple containing the hex value, question text, and a list of answer-choice tuples.
	"""
	with open(file_path, 'r') as file:
		lines = file.readlines()

	# Select a random line from the file
	line = random.choice(lines).strip()
	parts = line.split('\t')

	# Check if the question format is valid
	if parts[0] != "MC" or len(parts) < 4 or (len(parts) - 2) % 2 != 0:
		raise ValueError("Invalid question format in the file.")

	# Extract and validate the question text and hex value
	question_text = parts[1]
	hex_value = question_text[3:7]
	if not re.match(r'^[0-9a-fA-F]{4}$', hex_value):
		raise ValueError(f"Invalid hex value: {hex_value}")

	# Clean up the question text
	question_text = question_text[11:].strip()

	# Debugging output (optional)
	print("  Validated Hex Value:", hex_value)
	# print("Remaining Question Text:", question_text[:40])

	# Extract answer choices and correct status
	choices_list_of_tuples = [
		(parts[i], parts[i + 1].lower() == "correct") for i in range(2, len(parts), 2)
	]

	return hex_value, question_text, choices_list_of_tuples

#==============
def generate_html(hex_value, question_text, choices_list_of_tuples):
	"""
	Generate the HTML structure for a multiple-choice question.

	Args:
		hex_value (str): Unique identifier for the question.
		question_text (str): The question text to display.
		choices_list_of_tuples (list): List of answer-choice tuples.

	Returns:
		str: The generated HTML content as a string.
	"""
	html_content = f"<div id=\"question_html_{hex_value}\">\n"

	# Format and add the question text
	question_text = re.sub(r'</p>\s*<p>', '<br/>', question_text)
	html_content += f"<div id=\"statement_text_{hex_value}\">{question_text}</div>\n"

	# Add a form element for answer choices
	html_content += "<form>\n"
	html_content += f"<ul id=\"choices_{hex_value}\">\n"

	# Add each choice to the form
	for idx, option_tuple in enumerate(choices_list_of_tuples):
		choice_text, correct_bool = option_tuple
		html_content += "  <li>\n"
		html_content += f"    <input type=\"radio\" id=\"option{idx}\" "
		html_content += f" name=\"answer_{hex_value}\" "
		html_content += f" data-correct=\"{str(correct_bool).lower()}\">\n"
		html_content += f"    <label for=\"option{idx}\">{choice_text}</label>\n"
		html_content += "  </li>\n"

	html_content += "</ul>\n"

	# Add result display area
	style = 'style="display: block; margin: 0; padding: 0; font-size: large; font-weight: bold; font-family: monospace;"'
	html_content += f"<div id=\"result_{hex_value}\" {style}>&nbsp;</div>\n"

	# Add check button
	html_content += "<button type=\"button\" "
	html_content += "class=\"md-button md-button--secondary\" "
	html_content += f"onclick=\"checkAnswer_{hex_value}()\">"
	html_content += "Check Answer"
	html_content += "</button>\n"

	# Close form and div
	html_content += "</form>\n"
	html_content += "</div>"  # Close question div

	return html_content

#==============
def generate_javascript(hex_value) -> str:
	"""
	Generate JavaScript code for validating the answer to a multiple-choice question.

	Args:
		hex_value (str): Unique identifier for the question.

	Returns:
		str: JavaScript code as a string.
	"""
	javascript_html = "<script>\n"

	# Define a function to check the selected answer
	javascript_html += f"function checkAnswer_{hex_value}() {{\n"

	# Retrieve all answer options from the form
	javascript_html += f" const options = document.getElementsByName('answer_{hex_value}');\n"

	# Find the correct option
	javascript_html += " const correctOption = Array.from(options).reduce(function(acc, option) {\n"
	javascript_html += "   return acc || (option.dataset.correct === 'true' ? option : null);\n"
	javascript_html += " }, null);\n"

	# Find the selected option
	javascript_html += " const selectedOption = Array.from(options).reduce(function(acc, option) {\n"
	javascript_html += "   return acc || (option.checked ? option : null);\n"
	javascript_html += " }, null);\n"

	# Get the result display element
	javascript_html += f" const resultDiv = document.getElementById('result_{hex_value}');\n"

	# Update the result based on the selection
	javascript_html += " if (selectedOption) {\n"
	javascript_html += "  if (selectedOption === correctOption) {\n"
	javascript_html += "   resultDiv.style.color = 'green';\n"
	javascript_html += "   resultDiv.textContent = 'CORRECT';\n"
	javascript_html += "  } else {\n"
	javascript_html += "   resultDiv.style.color = 'red';\n"
	javascript_html += "   resultDiv.textContent = 'incorrect';\n"
	javascript_html += "  }\n"
	javascript_html += " } else {\n"
	javascript_html += "  resultDiv.style.color = 'black';\n"
	javascript_html += "  resultDiv.textContent = 'Please select an answer.';\n"
	javascript_html += " }\n"

	# Close function and script
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
	parser.add_argument('-o', '--output', dest='output_file', help='Output HTML file name.')
	args = parser.parse_args()
	return args

#==============
def get_output_filename(file_path):
	"""
	Generate the output HTML filename from the input text file name.

	Args:
		file_path (str): Path to the input file.

	Returns:
		str: The generated output file name.
	"""
	basename = os.path.basename(file_path)

	# Check if the file name starts with 'bbq-' and matches the expected pattern
	if basename.startswith('bbq-'):
		match = re.search(r'bbq-(.*?)-questions\.txt', basename)
		if not match:
			raise ValueError(f"Invalid filename format: {basename}")
		unique_part = match.group(1)
		output_file = unique_part + ".html"
	return output_file

#==============
def convert_text_to_html(file_path, output_file=None):
	"""
	Main conversion function to generate HTML and JavaScript from a text file.

	Args:
		file_path (str): Path to the input file.
		output_file (str, optional): Path to the output file. Defaults to None.

	Returns:
		str: The path to the generated output file.
	"""
	# Check if the input file exists
	if not os.path.exists(file_path):
		print(f"Error: File {file_path} not found.")
		sys.exit(1)

	# Determine the output file name if not provided
	if output_file is None:
		output_file = get_output_filename(file_path)

	# Load question data from the file
	hex_value, question_text, choices_list_of_tuples = load_single_question_from_file(file_path)

	# Generate and format the HTML content
	html_content = generate_html(hex_value, question_text, choices_list_of_tuples)
	html_content = format_html(html_content)
	html_content += generate_javascript(hex_value)

	# Write the output HTML file
	with open(output_file, 'w') as file:
		file.write(html_content)

	return output_file

#==============
def main() -> None:
	"""
	Main function to execute the program.
	Handles argument parsing, question loading, and HTML generation.
	"""
	args = get_parser()

	# Retrieve the file path from command-line arguments
	file_path = args.file_path

	# Convert the text file to an HTML file
	output_file = convert_text_to_html(file_path, args.output_file)

	# Print success message
	print(f"HTML file generated: {output_file}")

#==============
if __name__ == "__main__":
	main()
