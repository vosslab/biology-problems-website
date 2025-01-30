#!/usr/bin/env python

import os
import re
import time
import random
import argparse

#pip
from ollama import chat, ChatResponse
from bs4 import BeautifulSoup

# Configure Ollama model
#MODEL_NAME = "phi4"
#MODEL_NAME = "llama3.2:3b"
#MODEL_NAME = "llama3.2:1b"
MODEL_NAME = "llama3.2:3b-instruct-q4_K_M"

#==============

def generate_title_prompt(file_path: str, problem_statements: list) -> str:
	"""Generate a prompt for summarizing homework problems by generating a concise section title.

	Args:
		problem_statements (list[str]): List of problem statements.

	Returns:
		str: The formatted prompt for generating a title.
	"""

	# Construct the prompt
	prompt = (
		"You are summarizing a group of homework problems using markdown. "
		"Your task is to generate a descriptive section heading that classifies these types of problems so you can present the problem itself under this heading. "
		"The section heading should be concise and informative, indicating the primary topic or concepts tested (e.g., acid-base buffering, equilibrium constants, protonation states).\n\n"

		"Instructions:\n"
		"- The content provided below are a few problem statements. Assume the problem specifics may vary, but the conceptual type should remain clear.\n"
		"- Analyze the problem statements to identify the main concept or question type (e.g., buffering range, pKa values, protonation state).\n"
		"- Avoid analysis, reasoning, or explanation of the problem. Simply generate a **concise title** that clearly and accurately reflects the problem's focus.\n"
		"- Use simple, accessible language (no complex scientific terms unless necessary).\n"
		"- Return only the title in **bold markdown format**: ### <Title>\n"
		"- Titles should be brief and easy to understand for both students and educators.\n"
		"- Do not include any restated problem details, commentary, or additional thoughts.\n"
		"- Keep the word choices and language accessible to both students and educators.\n\n"

		"<sample>\n"
		"### Identify the Optimal Buffering Range Based on pKa Values\n\n"
		"Phosphoric acid has pKa values of 2.16, 7.21, and 12.32.\n"
		"Which one of the following pH values falls outside the optimal buffering range?\n"
		"</sample>\n\n"

	)

	if file_path is not None:
		match = re.search(r'bbq-(.*?)-questions\.txt', file_path)
		if not match:
			raise ValueError(f"Invalid filename format: {file_path}")
		unique_part = match.group(1)
		prompt += "The filename may offer some insight into the question type.\n "
		prompt += "For example, if the filename contains a number such as '2_protons' "
		prompt += "that implies something special about these problems"
		prompt += "filename root is:\n"
		prompt += f"{unique_part}\n\n"

	prompt += "Now the following are the problem examples that you are to provide a single title for:\n\n"

	for i, problem in enumerate(problem_statements, start=1):
		prompt += f"<problem {i}>\n{problem.strip()}\n</problem {i}>\n\n"

	return prompt


#==============

def strip_html_tags(html_string):
    """
    Removes all HTML tags from the input string and returns the plain text.

    Parameters:
    - html_string (str): The HTML string to process.

    Returns:
    - str: The plain text with HTML tags removed.
    """
    # Use BeautifulSoup to parse and extract the text
    soup = BeautifulSoup(html_string, 'html.parser')
    return soup.get_text()

#==============

def read_file_content(file_path: str) -> str:
	"""Read the content of a text file.	"""
	with open(file_path, "r") as file:
		content = file.read()
	return content

#==============

def run_ollama(prompt: str, model: str = MODEL_NAME) -> str:
	"""Generate a response using the Ollama model.

	Args:
		prompt (str): The prompt to send to the model.
		model (str): The name of the Ollama model to use. Defaults to 'phi4'.
		max_tokens (int): Maximum number of tokens in the response. Defaults to 50.
		temperature (float): Sampling temperature for response generation. Defaults to 0.5.
	"""
	t0 = time.time()
	# Send the prompt to the Ollama model
	response: ChatResponse = chat(
		model=model,
		messages=[{'role': 'user', 'content': prompt}],
	)

	# Extract the response content using the ChatResponse object
	response_content = response.message.content.strip()
	print(f"Ollama completed in {time.time()-t0:.2f} seconds")

	return response_content

#==============

def get_problem_title_from_response(response_content: str) -> str:
	"""Extract and return the problem title from the response content.

	Args:
		response_content (str): The response content from the Ollama model.

	Returns:
		str: The extracted problem title.
	"""
	# Handle multi-line content by splitting and searching for '###'
	line_content = response_content.strip()
	if '\n' in response_content:
		lines = response_content.split('\n')
		for line in lines:
			sline = line.strip()
			if '###' in sline:
				line_content = sline
				break  # Stop after finding the first valid title

	# Extract the title using regex
	title = re.sub(r'^.*###*', '', line_content).strip()
	return title


#==============
def load_problem_statements_from_file(file_path: str) -> tuple:
	"""
	Load a random question from a text file.
	"""
	with open(file_path, 'r') as file:
		lines = file.readlines()

	problem_statements = []

	total_length = 0
	for _ in range(4):

		# Pick a random line from the file
		line = random.choice(lines).strip()
		parts = line.split('\t')

		# Validate the format of the line
		if parts[0] != "MC" or len(parts) < 4 or (len(parts) - 2) % 2 != 0:
			raise ValueError("Invalid question format in the file.")

		# Extract question text
		question_text = parts[1].strip()
		stripped_problem = strip_html_tags(question_text)


		problem_statements.append(stripped_problem)
		total_length += len(stripped_problem)
		if total_length > 1000:
			break

	problem_statements = list(set(problem_statements))
	return problem_statements

#==============
def get_parser() -> argparse.Namespace:
	"""
	Set up argument parser for command-line inputs.

	Returns:
		argparse.Namespace: Parsed command-line arguments.
	"""
	parser = argparse.ArgumentParser(description="Generate a Markdown MC question with HTML from a text file.")
	parser.add_argument('-f', '--file', dest='file_path', required=True, help='Path to the questions text file.')

	args = parser.parse_args()
	return args

#==============
def get_problem_title_from_file(file_path):
	if not os.path.exists(file_path):
		print(f"Error: File {file_path} not found.")
		raise IOError

	problem_statements = load_problem_statements_from_file(file_path)

	# Generate and print the prompt
	prompt = generate_title_prompt(file_path, problem_statements)

	response_content = run_ollama(prompt)
	problem_title = get_problem_title_from_response(response_content)
	leading_words = ['Determine', 'Identify', 'Identifying']
	for word in leading_words:
		if problem_title.startswith(f'{word} '):
			problem_title = problem_title[len(word)+1:].strip()
	if problem_title.startswith('the '):
		problem_title = problem_title[len('the')+1:].strip()
	return problem_title

#==============
def main():
	"""
	Main function to execute the program.
	Handles argument parsing, question loading, and Markdown generation.
	"""
	args = get_parser()
	file_path = args.file_path
	problem_title = get_problem_title_from_file(file_path)
	print(f"Generated Title:\"{problem_title}\"")



#==============

if __name__ == "__main__":
	main()
