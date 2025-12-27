#!/usr/bin/env python

#!/usr/bin/env python

# Import modules from the standard library
# Provides functions to interact with the operating system and file system
import os
# Provides tools for regular expression matching and string manipulation
import re
# Provides functions for working with time and timing operations
import time
# Provides tools for generating random numbers and selections
import random
# Provides tools to parse and handle command-line arguments
import argparse
import subprocess

# Import external libraries
# Provides functions to interact with the Ollama chat model API
from ollama import chat, ChatResponse
# Provides tools to parse and manipulate HTML content
from bs4 import BeautifulSoup

#==============
# Function to detect VRAM or Unified Memory size in GB
def get_vram_size_in_gb():
	try:
		# Detect system architecture
		architecture = subprocess.check_output(["uname", "-m"], text=True).strip()
		is_apple_silicon = architecture.startswith("arm64")

		if is_apple_silicon:
			# Apple Silicon (M1/M2): Unified memory
			hardware_info = subprocess.check_output(["system_profiler", "SPHardwareDataType"], text=True)
			memory_match = re.search(r"Memory:\s(\d+)\s?GB", hardware_info)
			if memory_match:
				return int(memory_match.group(1))
		else:
			# Intel Macs: Dedicated VRAM
			display_info = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True)
			vram_match = re.search(r"VRAM.*?: (\d+)\s?MB", display_info)
			if vram_match:
				vram_in_mb = int(vram_match.group(1))
				return vram_in_mb // 1024  # Convert MB to GB

	except subprocess.SubprocessError as e:
		print(f"Error getting memory info: {e}")
	except Exception as e:
		print(f"Unexpected error: {e}")

	return None

vram_size_gb = get_vram_size_in_gb()
if vram_size_gb is not None:
	print(f"VRAM size: {vram_size_gb} GB")
else:
	print("Could not determine VRAM size.")

# Configure the Ollama model by setting the model name
# Uncomment one of these lines to change the model
# see https://ollama.com/library for models
# check size of models 'du -sh .ollama/models/blobs/'
# to avoid filling hard drive space
# run 'ollama list' also helps
# best for 32GB VRAM machines
#default
MODEL_NAME = "llama3.2:1b-instruct-q4_K_M"
if vram_size_gb is not None:
	if vram_size_gb > 30:
		#MODEL_NAME = "phi4:14b-q8_0"
		#MODEL_NAME = "llama3.2:3b-instruct-fp16"
		MODEL_NAME = "gpt-oss:20b"
	elif vram_size_gb > 14:
		MODEL_NAME = "phi4:14b-q4_K_M"
	elif vram_size_gb > 4:
		# best for 8GB VRAM machines
		#MODEL_NAME = "llama3.2:3b-instruct-q4_K_M"
		MODEL_NAME = "llama3.2:3b-instruct-q5_K_M"
print(f"Selected ollama model: {MODEL_NAME}")

#==============

# This function generates a descriptive prompt for summarizing problem statements.
def generate_title_prompt(file_path: str, problem_statements: list, save_prompt: bool = False) -> str:
	"""
	Generate a prompt for summarizing homework problems by generating a concise section title.

	Args:
		file_path (str): Path to the input file.
		problem_statements (list[str]): List of problem statements.
		save_prompt (bool): Whether to save the generated prompt to a file.

	Returns:
		str: The formatted prompt for generating a title.
	"""
	# Define the prompt template that guides the model to generate a title
	prompt = (
		"You are summarizing a group of homework problems using markdown. "
		"Your task is to generate a descriptive section heading that classifies these types of problems so you can present the problem itself under this heading. "
		"The section heading should be concise and informative, indicating the primary topic or concepts tested (e.g., acid-base buffering, equilibrium constants, protonation states).\n\n"
	)

	prompt += (
		# Provide instructions for how the title should be created
		"Instructions:\n"
		"- The content provided below are a few problem statements. Assume the problem specifics may vary, but the conceptual type should remain clear.\n"
		"- Analyze the problem statements to identify the main concept or question type (e.g., buffering range, pKa values, protonation state).\n"
		"- Avoid analysis, reasoning, or explanation of the problem. Simply generate a **concise title** that clearly and accurately reflects the problem's focus.\n"
		"- Use simple, accessible language (no complex scientific terms unless necessary).\n"
		"- Return only the title in **bold markdown format**: ### <Title>\n"
		"- Titles should be brief and easy to understand for both students and educators.\n"
		"- Do not include any restated problem details, commentary, or additional thoughts.\n"
		"- Keep the word choices and language accessible to both students and educators.\n\n"
	)

	# get topics using this command
	# egrep '^bbq' site_docs/*/topic*/problem_set_titles.yml | cut -d':' -f3- | gsed 's/^\s*/\"### /' | gsed 's/\s*$/\\n\",/' | sort
	prompt += (
		# Provide a list of sample titles to guide the model
		"<list of unrelated sample titles>\n"
		"### Allosteric Enzymes in Metabolic Pathways\n"
		"### Amino Acids from Chemical Structures\n"
		"### Cell Disruption Techniques Identification\n"
		"### Correct Form of the Henderson-Hasselbalch\n"
		"### Determining Dipeptide Sequence\n"
		"### Determining Net Charge of Proteins at Given\n"
		"### Energy Terms and Their Categories\n"
		"### Enzyme Catalysis Terminology\n"
		"### Enzyme Inhibition and Activation\n"
		"### Estimating Protein Molecular Weight from\n"
		"### Hydrogen Bonding in Alpha-Helix Structures\n"
		"### Hydrophobic Compounds from Molecular Formulas\n"
		"### Identification of Amino Acids by Structural and\n"
		"### Identification of Macromolecules in Gel Electrophoresis\n"
		"### Inhibition Type Determination from Enzyme Activity Data\n"
		"### Ionic Bond Formation in Amino Acid Side\n"
		"### Levels of Protein Structure\n"
		"### Macromolecule Types Based on Chemical Structures\n"
		"### Michaelis-Menten Constant\n"
		"### Most Abundant Diprotic State at pH using\n"
		"### Most Abundant Tetraprotic State at pH\n"
		"### Most Abundant Triprotic State at pH\n"
		"### Optimal Buffering Range using pKa\n"
		"### Protein Migration Direction Based on Isoelectric\n"
		"### The Seven Biochemical Functional Groups\n"
		"### True/False Statements on Chemical Reactions\n"
		"### True/False Statements on Enzyme Kinetics\n"
		"### True/False Statements on Gibbs Free Energy (&Delta;G = &Delta;H - T &Delta;S)\n"
		"### True/False Statements on Michaelis-Menten Kinetics\n"
		"### True/False Statements on Thermodynamics vs. Kinetics\n"
		"### Types and Descriptions of Column Chromatography\n"
		"### Types of Chemical Bonds\n"
		"### Types of Column Chromatography\n"
		"### Types of Macromolecules\n"
		"### Which Molecule Cannot be an Enzyme Cofactors\n"
		"### Which Molecule Could be an Enzyme\n"
		"</list of unrelated sample titles>\n\n"
	)

	# Check if the file path was provided
	if file_path is not None:
		# Use regular expressions to extract information from the filename
		match = re.search(r'bbq-(.*?)-questions\.txt', file_path)
		# If the filename does not match the expected pattern, raise an error
		if not match:
			raise ValueError(f"Invalid filename format: {file_path}")

		# Extract the unique part of the filename
		unique_part = match.group(1)

		# Add additional information to the prompt based on the filename
		prompt += "The filename may offer some insight into the question type.\n "
		prompt += "For example, if the filename contains a number such as '2_protons' "
		prompt += "that implies something special about these problems."
		prompt += " Filename root is:\n"
		prompt += f"{unique_part}\n\n"

	# Add the problem statements to the prompt
	prompt += "Now the following are the problem examples that you are to provide a single title for:\n\n"
	for i, problem in enumerate(problem_statements, start=1):
		# Add each problem statement, numbered, to the prompt
		prompt += f"<problem {i}>\n{problem.strip()}\n</problem {i}>\n\n"

	# If the save_prompt flag is True, save the generated prompt to a file
	if save_prompt is True:
		with open('prompt.txt', 'w') as prompt_file:
			prompt_file.write(prompt)

	# Return the generated prompt
	return prompt

#==============

# This function removes all HTML tags from a string.
def strip_html_tags(html_string):
	"""
	Removes all HTML tags from the input string and returns the plain text.

	Args:
		html_string (str): The HTML string to process.

	Returns:
		str: The plain text with HTML tags removed.
	"""
	# Use BeautifulSoup to parse the HTML and extract only the text content
	soup = BeautifulSoup(html_string, 'html.parser')
	return soup.get_text()

#==============

# This function reads the contents of a text file.
def read_file_content(file_path: str) -> str:
	"""
	Read the content of a text file.

	Args:
		file_path (str): The path to the file.

	Returns:
		str: The content of the file as a string.
	"""
	# Open the file in read mode and read its contents
	with open(file_path, "r") as file:
		content = file.read()

	# Return the file content
	return content

#==============

# This function sends a prompt to the Ollama model and retrieves the response.
def run_ollama(prompt: str, model: str = MODEL_NAME) -> str:
	"""
	Generate a response using the Ollama model.

	Args:
		prompt (str): The prompt to send to the model.
		model (str): The name of the Ollama model to use. Defaults to 'MODEL_NAME'.

	Returns:
		str: The response content generated by the model.
	"""
	# Record the start time to measure execution time
	t0 = time.time()

	# Send the prompt to the Ollama chat model and store the response
	response: ChatResponse = chat(
		model=model,  # Use the specified model for response generation
		messages=[{'role': 'user', 'content': prompt}]  # Send the prompt as a user message
	)

	# Extract the message content from the response and remove leading/trailing whitespace
	response_content = response.message.content.strip()

	# Print the time taken to complete the response
	print(f"Ollama completed in {time.time()-t0:.2f} seconds")

	# Return the cleaned response content
	return response_content

#==============

# This function extracts the problem title from the model's response.
def get_problem_title_from_response(response_content: str) -> str:
	"""
	Extract and return the problem title from the response content.

	Args:
		response_content (str): The response content from the Ollama model.

	Returns:
		str: The extracted problem title.
	"""
	# Remove leading and trailing whitespace from the response
	line_content = response_content.strip()

	# Check if the response contains multiple lines
	if '\n' in response_content:
		# Split the response into lines
		lines = response_content.split('\n')

		# Iterate through each line to find the one containing the '###' title marker
		for line in lines:
			sline = line.strip()  # Remove extra whitespace from the line
			if '###' in sline:
				# Set the line content to the one containing the title and stop searching
				line_content = sline
				break

	# Use a regular expression to remove any characters before the '###' marker
	title = re.sub(r'^.*###*', '', line_content).strip()

	# Return the extracted title
	return title

#==============

# This function loads problem statements from a file and returns a list of unique problems.
def load_problem_statements_from_file(file_path: str) -> tuple:
	"""
	Load a random question from a text file.

	Args:
		file_path (str): Path to the file containing questions.

	Returns:
		list: A list of unique problem statements.
	"""
	# Open the file in read mode and read all lines
	with open(file_path, 'r') as file:
		lines = file.readlines()

	# Initialize an empty list to store problem statements
	problem_statements = []

	# Initialize a counter for the total length of all problems
	total_length = 0

	# Loop up to 4 times to select random problem statements
	for _ in range(6):
		# Pick a random line from the file and remove any extra whitespace
		line = random.choice(lines).strip()
		while len(line) < 10:
			line = random.choice(lines).strip()

		# Split the line by tab characters
		parts = line.split('\t')

		# Extract the question text from the second element of the parts
		question_text = parts[1].strip()

		# Remove any HTML tags from the question text
		stripped_problem = strip_html_tags(question_text)

		# Add the cleaned problem statement to the list
		problem_statements.append(stripped_problem)

		# Increment the total length of all problem statements
		total_length += len(stripped_problem)

		# Stop adding problems if the total length exceeds 1000 characters
		if total_length > 1000:
			break

	# Remove duplicate problem statements by converting the list to a set and back to a list
	problem_statements = list(set(problem_statements))

	# Return the list of unique problem statements
	return problem_statements

#==============

# This function orchestrates the process of generating a problem title from a file.
def get_problem_title_from_file(file_path, save_prompt=False):
	"""
	Generate a problem title from a file containing problem statements.

	Args:
		file_path (str): Path to the file containing problem statements.
		save_prompt (bool): Whether to save the generated prompt to a file.

	Returns:
		str: The generated problem title.
	"""
	# Check if the input file exists
	if not os.path.exists(file_path):
		# Print an error message if the file is not found
		print(f"Error: File {file_path} not found.")

		# Raise an IOError to indicate the issue
		raise IOError

	# Load problem statements from the file
	problem_statements = load_problem_statements_from_file(file_path)

	# Generate a prompt using the loaded problem statements
	prompt = generate_title_prompt(file_path, problem_statements, save_prompt)

	# Run the Ollama model to generate a response for the prompt
	response_content = run_ollama(prompt)

	# Extract the problem title from the model's response
	problem_title = get_problem_title_from_response(response_content)

	# Define a list of leading words that should be removed from the title
	leading_words = ['Determine', 'Identify', 'Identifying']

	# Loop through each leading word and check if the title starts with it
	for word in leading_words:
		if problem_title.startswith(f'{word} '):
			# Remove the leading word and the following space from the title
			problem_title = problem_title[len(word) + 1:].strip()

	# Remove "the " if the title starts with it
	if problem_title.startswith('the '):
		problem_title = problem_title[len('the') + 1:].strip()

	# Return the cleaned problem title
	return problem_title

#==============

# This function sets up and returns a parser for command-line arguments.
def get_parser() -> argparse.Namespace:
	"""
	Set up argument parser for command-line inputs.

	Returns:
		argparse.Namespace: Parsed command-line arguments.
	"""
	# Create an argument parser with a description of the program's purpose
	parser = argparse.ArgumentParser(
		description="Generate a Markdown MC question with HTML from a text file."
	)

	# Add a required argument for the input file path
	parser.add_argument(
		'-f', '--file', dest='file_path',
		required=True, help='Path to the questions text file.'
	)

	# Add a flag to determine whether to save the prompt
	parser.add_argument(
		'-s', '--save-prompt', dest='save_prompt',
		default=False, action='store_true',
		help='Save prompt (default is False).'
	)

	# Parse the command-line arguments and return them
	args = parser.parse_args()
	return args

#==============

# This is the main function that executes the entire program.
def main():
	"""
	Main function to execute the program.
	Handles argument parsing, question loading, and Markdown generation.
	"""
	# Parse command-line arguments
	args = get_parser()

	# Generate the problem title from the input file
	problem_title = get_problem_title_from_file(args.file_path, args.save_prompt)

	# Print the generated title to the console
	print(f"Generated Title: \"{problem_title}\"")

#==============

# This block ensures that the main function is called when the script is executed directly.
if __name__ == "__main__":
	# Run the main function
	main()
