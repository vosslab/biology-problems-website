#!/usr/bin/env python3

# Import modules from the standard library
# Allows interaction with the operating system and file system
import os
# Provides regular expression support for string manipulation
import re
# Allows interaction with the Python runtime environment
import sys
# Provides functionality for random number generation
import random
# Provides tools for parsing command-line arguments
import argparse

# Import modules from external libraries
# Provides tools to parse and manipulate HTML
from lxml import html, etree

#==============
# This function formats an HTML string to be more readable.
def format_html(html_string):
	"""
	Format an HTML string to be more readable by removing excess whitespace and adding proper indentation.

	Args:
		html_string (str): The HTML content to be formatted.

	Returns:
		str: The formatted HTML string.
	"""
	# Call the helper function to handle HTML formatting using the lxml library
	return format_html_lxml(html_string)

#==============
# This function formats HTML content using the lxml library.
def format_html_lxml(html_string):
	"""
	Format an HTML string using lxml library for cleaner output.

	Args:
		html_string (str): The HTML content to be formatted.

	Returns:
		str: The formatted HTML string.
	"""
	# Create an HTML parser that removes blank text nodes
	parser = html.HTMLParser(remove_blank_text=True)

	# Parse the input HTML string into an HTML tree
	tree = html.fromstring(html_string, parser=parser)

	# Convert the parsed HTML tree to a formatted string with indentation and line breaks
	formatted_html = etree.tostring(tree, pretty_print=True, encoding="unicode").strip()
	# Ensure the string is formatted for HTML output
	formatted_html = etree.tostring(tree, pretty_print=True, encoding="unicode", method="html").strip()
	formatted_html = formatted_html.replace("&amp;", "&")
	# Return the formatted HTML string
	return formatted_html

#==============
def add_mathml_javascript():
	javascript_text = ""
	javascript_text += "<script type='text/javascript' async "
	javascript_text += "src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'>"
	javascript_text += "</script>"
	return javascript_text

#==============
# This function loads a random multiple-choice question from a file.
def load_single_question_from_file(file_path: str) -> tuple:
	"""
	Load a single random multiple-choice question from a file.

	Args:
		file_path (str): Path to the file containing questions.

	Returns:
		tuple: A tuple containing the hex value, question text, and a list of answer-choice tuples.
	"""
	# Open the file at the given path and read all lines
	with open(file_path, 'r') as file:
		lines = file.readlines()

	# Select a random line from the list of lines
	line = random.choice(lines).strip()

	# Split the line by tab characters into parts
	parts = line.split('\t')

	# Check if the question format is valid based on specific criteria
	if parts[0] != "MC" or len(parts) < 4 or (len(parts) - 2) % 2 != 0:
		raise ValueError("Invalid question format in the file.")

	# Extract the question text from the parts
	question_text = parts[1]

	# Extract a 4-character hex value from the question text
	hex_value = question_text[3:7]

	# Validate that the extracted hex value matches a valid hexadecimal pattern
	if not re.match(r'^[0-9a-fA-F]{4}$', hex_value):
		raise ValueError(f"Invalid hex value: {hex_value}")

	# Remove unnecessary text from the question text
	question_text = question_text[11:].strip()

	if '<math xmlns=' in line:
		question_text = add_mathml_javascript() + question_text

	# Debug output to display the validated hex value (optional)
	print("  Validated Hex Value:", hex_value)

	# Extract the answer choices and whether each is correct or not
	choices_list_of_tuples = [
		(parts[i], parts[i + 1].lower() == "correct") for i in range(2, len(parts), 2)
	]

	# Return the hex value, cleaned question text, and the list of answer-choice tuples
	return hex_value, question_text, choices_list_of_tuples

#==============
# This function generates HTML for a multiple-choice question.
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
	# Start the HTML content with a div containing a unique ID for the question
	html_content = f"<div id=\"question_html_{hex_value}\">\n"

	# Replace adjacent paragraph tags with a line break for cleaner formatting
	question_text = re.sub(r'</p>\s*<p>', '<br/>', question_text)

	# Add the question text inside another uniquely identified div
	html_content += f"<div id=\"statement_text_{hex_value}\">{question_text}</div>\n"

	# Begin the form for the multiple-choice options
	html_content += "<form>\n"

	# Add an unordered list to contain the choices, identified by a unique ID
	html_content += f"<ul id=\"choices_{hex_value}\">\n"

	# Loop through each answer choice
	for idx, option_tuple in enumerate(choices_list_of_tuples):
		# Extract the choice text and whether it is the correct answer
		choice_text, correct_bool = option_tuple

		# Add a list item to contain the radio button and label
		html_content += "  <li>\n"

		# Add an input element of type "radio"
		html_content += f"    <input type=\"radio\" id=\"option{idx}\" "

		# Set the name attribute to group radio buttons together under the question's hex value
		html_content += f" name=\"answer_{hex_value}\" "

		# Store whether the choice is correct as a custom data attribute
		html_content += f" data-correct=\"{str(correct_bool).lower()}\">\n"

		# Add a label for the radio button, associated by its ID
		html_content += f"    <label for=\"option{idx}\">{choice_text}</label>\n"

		# Close the list item
		html_content += "  </li>\n"

	# Close the unordered list of choices
	html_content += "</ul>\n"

	# Add a div to display the result message, styled with inline CSS
	style = 'style="display: block; margin: 0; padding: 0; font-size: large; font-weight: bold; font-family: monospace;"'
	html_content += f"<div id=\"result_{hex_value}\" {style}>&nbsp;</div>\n"

	# Add a button for submitting the answer
	# Set the button type to "button" to prevent form submission
	html_content += "<button type=\"button\" "

	# Set the class of the button to match the material design theme of the website
	html_content += "class=\"md-button md-button--secondary\" "

	# Add an onclick event to call the answer-checking function for this question
	html_content += f"onclick=\"checkAnswer_{hex_value}()\">"

	# Set the button's visible text
	html_content += "Check Answer"

	# Close the button element
	html_content += "</button>\n"

	# Close the form element
	html_content += "</form>\n"

	# Close the question div element
	html_content += "</div>"

	# Return the complete HTML content
	return html_content

#==============

# This function generates JavaScript to check the answer for a multiple-choice question.
def generate_javascript(hex_value) -> str:
	"""
	Generate JavaScript code for validating the answer to a multiple-choice question.

	Args:
		hex_value (str): Unique identifier for the question.

	Returns:
		str: JavaScript code as a string.
	"""
	# Begin the JavaScript with a script tag
	javascript_html = "<script>\n"

	# Define a function to check the selected answer, using the unique hex value
	javascript_html += f"function checkAnswer_{hex_value}() {{\n"

	# Get all radio button options for this question
	javascript_html += f" const options = document.getElementsByName('answer_{hex_value}');\n"

	# Find the correct option by checking the custom data attribute
	javascript_html += " const correctOption = Array.from(options).reduce(function(acc, option) {\n"
	javascript_html += "   return acc || (option.dataset.correct === 'true' ? option : null);\n"
	javascript_html += " }, null);\n"

	# Find the selected option by checking which radio button is checked
	javascript_html += " const selectedOption = Array.from(options).reduce(function(acc, option) {\n"
	javascript_html += "   return acc || (option.checked ? option : null);\n"
	javascript_html += " }, null);\n"

	# Get the result display element by its unique ID
	javascript_html += f" const resultDiv = document.getElementById('result_{hex_value}');\n"

	# Check if the user selected an option
	javascript_html += " if (selectedOption) {\n"

	# If the selected option is correct, display a "CORRECT" message in green
	javascript_html += "  if (selectedOption === correctOption) {\n"
	javascript_html += "   resultDiv.style.color = 'green';\n"
	javascript_html += "   resultDiv.textContent = 'CORRECT';\n"

	# If the selected option is incorrect, display an "incorrect" message in red
	javascript_html += "  } else {\n"
	javascript_html += "   resultDiv.style.color = 'red';\n"
	javascript_html += "   resultDiv.textContent = 'incorrect';\n"
	javascript_html += "  }\n"

	# If no option was selected, prompt the user to select an answer
	javascript_html += " } else {\n"
	javascript_html += "  resultDiv.style.color = 'black';\n"
	javascript_html += "  resultDiv.textContent = 'Please select an answer.';\n"
	javascript_html += " }\n"

	# Close the function definition
	javascript_html += "}\n"

	# Close the script tag
	javascript_html += "</script>\n"

	# Return the complete JavaScript code
	return javascript_html

#==============
# This function generates the output HTML filename from the input file path.
def get_output_filename(file_path):
	"""
	Generate the output HTML filename from the input text file name.

	Args:
		file_path (str): Path to the input file.

	Returns:
		str: The generated output file name.
	"""
	# Extract the base name of the file (without directory path)
	basename = os.path.basename(file_path)

	# Check if the file name starts with 'bbq-' and matches the expected pattern
	if basename.startswith('bbq-'):
		# Use a regular expression to extract the unique part of the file name
		match = re.search(r'bbq-(.*?)-questions\.txt', basename)

		# If the pattern doesn't match, raise an error
		if not match:
			raise ValueError(f"Invalid filename format: {basename}")

		# Extract the unique part of the file name from the regex match
		unique_part = match.group(1)

		# Create the output file name by appending '.html' to the unique part
		output_file = unique_part + ".html"

	# Return the generated output file name
	return output_file

#==============

# This function converts a text file with questions into an HTML file.
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
		# Print an error message if the file is not found
		print(f"Error: File {file_path} not found.")

		# Exit the program with a non-zero status to indicate an error
		sys.exit(1)

	# If no output file is provided, generate a name based on the input file
	if output_file is None:
		output_file = get_output_filename(file_path)

	# Load a random question from the input file
	hex_value, question_text, choices_list_of_tuples = load_single_question_from_file(file_path)

	# Generate the HTML content for the question
	html_content = generate_html(hex_value, question_text, choices_list_of_tuples)

	# Format the generated HTML for better readability
	html_content = format_html(html_content)

	# Append the generated JavaScript to the HTML content
	html_content += generate_javascript(hex_value)

	# Open the output file in write mode
	with open(output_file, 'w') as file:
		# Write the generated HTML content to the file
		file.write(html_content)

	# Return the output file path
	return output_file

#==============
# This function sets up the command-line argument parser.
def get_parser() -> argparse.Namespace:
	"""
	Set up argument parser for command-line inputs.

	Returns:
		argparse.Namespace: Parsed command-line arguments.
	"""
	# Create a parser with a description of the program's purpose
	parser = argparse.ArgumentParser(description="Generate an HTML MC question from a text file.")

	# Add a required argument for the input file path
	parser.add_argument('-f', '--file', dest='file_path',
		required=True, help='Path to the questions text file.')

	# Add an optional argument for the output file path
	parser.add_argument('-o', '--output', dest='output_file', help='Output HTML file name.')

	# Parse the command-line arguments
	args = parser.parse_args()

	# Return the parsed arguments
	return args

#==============
# This is the main function that orchestrates the entire program flow.
def main() -> None:
	"""
	Main function to execute the program.
	Handles argument parsing, question loading, and HTML generation.
	"""
	# Parse command-line arguments
	args = get_parser()

	# Retrieve the input file path from the parsed arguments
	file_path = args.file_path

	# Convert the input text file into an HTML file
	output_file = convert_text_to_html(file_path, args.output_file)

	# Print a success message with the output file path
	print(f"HTML file generated: {output_file}")

#==============

# This ensures that the main function is only called when the script is executed directly.
if __name__ == "__main__":
	# Run the main function
	main()
