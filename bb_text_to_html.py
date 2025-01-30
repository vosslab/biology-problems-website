#!/usr/bin/env python3

# Standard Library
import os
import re
import sys
import random
import argparse

from lxml import html, etree

def format_html(html_string):
	return format_html_lxml(html_string)

def format_html_lxml(html_string):
	parser = html.HTMLParser(remove_blank_text=True)  # Prevent excessive spacing
	tree = html.fromstring(html_string, parser=parser)
	formatted_html = etree.tostring(tree, pretty_print=True, encoding="unicode").strip()
	formatted_html = etree.tostring(tree, pretty_print=True, encoding="unicode", method="html").strip()
	return formatted_html

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

	# Extract the hex value
	hex_value = question_text[3:7]

	# Validate the hex value
	if not re.match(r'^[0-9a-fA-F]{4}$', hex_value):
		raise ValueError(f"Invalid hex value: {hex_value}")

	# Remove those characters from the string and strip any leading/trailing whitespace
	question_text = question_text[11:].strip()

	# Output for validation (optional)
	print("  Validated Hex Value:", hex_value)
	#print("Remaining Question Text:", question_text[:40])

	# Extract answer choices as a list of tuples (answer_text, is_correct)
	choices_list_of_tuples = [
		(parts[i], parts[i + 1].lower() == "correct") for i in range(2, len(parts), 2)
	]

	return hex_value, question_text, choices_list_of_tuples

#==============
def generate_html(hex_value, question_text, choices_list_of_tuples):
	"""
	Generate an HTML file for a single multiple-choice question.

	Args:
		question (dict): A dictionary containing question text and options.
		output_file (str): Path to save the generated HTML file.
	"""
	html_content = f"<div id=\"question_html_{hex_value}\">\n"
	# Add JavaScript function
	# Add question text
	#style = 'style="display: block; margin: 0; padding: 0;"'
	question_text = re.sub(r'</p>\s*<p>', '<br/>', question_text)
	html_content += f"<div id=\"statement_text_{hex_value}\">{question_text}</div>\n"
	# Open form tag
	html_content += "<form>\n"

	html_content += f"<ul id=\"choices_{hex_value}\">\n"
	for idx, option_tuple in enumerate(choices_list_of_tuples):
		choice_text, correct_bool = option_tuple
		html_content += "  <li>\n"
		html_content += f"    <input type=\"radio\" id=\"option{idx}\" "
		html_content += f" name=\"answer_{hex_value}\" "
		html_content += f" data-correct=\"{str(correct_bool).lower()}\">\n"
		html_content += f"    <label for=\"option{idx}\">{choice_text}</label>\n"
		html_content += "  </li>\n"
	html_content += "</ul>\n"
	style = 'style="display: block; margin: 0; padding: 0; font-size: large; font-weight: bold; font-family: monospace;"'
	html_content += f"<div id=\"result_{hex_value}\" {style}>&nbsp;</div>\n"

	# Add check button
	html_content += "<button type=\"button\" "
	html_content += "class=\"md-button md-button--secondary\" "
	html_content += f"onclick=\"checkAnswer_{hex_value}()\">"
	html_content += "Check Answer"
	html_content += "</button>\n"

	# close the form
	html_content += "</form>\n"
	# Add result div
	html_content += "</div>" # close question
	return html_content

#==============
def generate_javascript(hex_value) -> str:
	"""
	Generate the JavaScript code for the HTML file.

	Returns:
		str: JavaScript code as a string.
	"""

	javascript_html = "<script>\n"
	# Open the function
	javascript_html +=f"function checkAnswer_{hex_value}() "
	javascript_html += "{\n"
	# Set options constant to get all options from the form
	javascript_html +=f" const options = document.getElementsByName('answer_{hex_value}');\n"

	#  Get the correct option
	javascript_html += " const correctOption = Array.from(options).reduce(function(acc, option) {\n"
	javascript_html += "   return acc || (option.dataset.correct === 'true' ? option : null);\n"
	javascript_html += " }, null);\n"

	# Get the selected option
	javascript_html += " const selectedOption = Array.from(options).reduce(function(acc, option) {\n"
	javascript_html += "   return acc || (option.checked ? option : null);\n"
	javascript_html += " }, null);\n"

	# Get the result div to display feedback
	javascript_html +=f" const resultDiv = document.getElementById('result_{hex_value}');\n"

	# Check if a selection is made
	javascript_html += " if (selectedOption) {\n"
	# If the selection is correct
	javascript_html += "  if (selectedOption === correctOption) {\n"
	javascript_html += "   resultDiv.style.color = 'green';\n"
	javascript_html += "   resultDiv.textContent = 'CORRECT';\n"
	javascript_html += "  } else {\n"  # If the selection is incorrect
	javascript_html += "   resultDiv.style.color = 'red';\n"
	javascript_html += "   resultDiv.textContent = 'incorrect';\n"
	javascript_html += "  }\n"  # Close else
	javascript_html += " } else {\n"  # If no selection is made
	javascript_html += "  resultDiv.style.color = 'black';\n"
	javascript_html += "  resultDiv.textContent = 'Please select an answer.';\n"
	javascript_html += " }\n"  # Close else

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
	parser.add_argument('-o', '--output', dest='output_file', help='Output HTML file name.')
	args = parser.parse_args()
	return args

#==============
def get_output_filename(file_path):
	basename = os.path.basename(file_path)
	if basename.startswith('bbq-'):
		match = re.search(r'bbq-(.*?)-questions\.txt', basename)
		if not match:
			raise ValueError(f"Invalid filename format: {basename}")
		unique_part = match.group(1)
		output_file = unique_part + ".html"
	return output_file

#==============
def convert_text_to_html(file_path, output_file=None):

	if not os.path.exists(file_path):
		print(f"Error: File {file_path} not found.")
		sys.exit(1)

	if output_file is None:
		output_file = get_output_filename(file_path)

	hex_value, question_text, choices_list_of_tuples = load_single_question_from_file(file_path)

	# Generate the HTML file
	html_content = generate_html(hex_value, question_text, choices_list_of_tuples)
	#print(f"Original HTML Text (Length = {len(html_content)}):", html_content[:40])
	html_content = format_html(html_content)
	#print(f"Cleaned  HTML Text (Length = {len(html_content)}):", html_content[:40])
	html_content += generate_javascript(hex_value)

	# Write the constructed HTML to the output file
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

	file_path = args.file_path

	output_file = convert_text_to_html(file_path, args.output_file)

	print(f"HTML file generated: {output_file}")

#==============
if __name__ == "__main__":
	main()
