"""Generate concise problem-set titles from BBQ question files via an LLM."""

# Standard Library
import os
import re
import random

# PIP3 modules
import bs4
import local_llm_wrapper.llm as llm

#==============
# This function generates a descriptive prompt for summarizing problem statements.
def generate_title_prompt(file_path: str, problem_statements: list) -> str:
	"""
	Generate a prompt for an instructor-facing problem-set catalog title.

	Args:
		file_path (str): Path to the input file.
		problem_statements (list[str]): List of problem statements.

	Returns:
		str: The formatted prompt for generating a title.
	"""
	# Define the prompt template that guides the model to generate a title
	prompt = (
		"You curate a catalog of biology problem sets for instructors browsing the corpus "
		"and considering material for their courses. "
		"Write a concise title that helps an instructor recognize the topic, assessed skill, "
		"and meaningful differences from related sets.\n\n"
	)

	prompt += (
		# Provide instructions for how the title should be created
		# Canonical format labels: docs/PROBLEM_TITLE_ABBREVIATIONS.md.
		"Instructions:\n"
		"- Lead with the biological concept and use the scientific terms instructors search for.\n"
		"- Name the assessed task or input when useful, such as structure identification, pedigree interpretation, or calculations from data.\n"
		"- Describe the scope across the sample questions. Include a particular organism, disorder, or value only when it defines the set.\n"
		"- Use the same base wording for versions of the same content; put format and meaningful variant details in parentheses at the end.\n"
		"- MATCH- and WOMC- files are versions of a matching bank. Use the same content title with a final Matching or WOMC label, respectively. WOMC means Which One Multiple Choice, drawn from matching content.\n"
		"- Use (TFMS) for TFMS- filenames. It identifies that MC generator family even when the stem asks for an example or sequence. The website displays it as T/F Statements (MC); describe the actual assessed task in the base title.\n"
		"- End every title with its question type. Distinguish MC, WOMC, TFMS, MA, NUM, FiB, MULTI_FIB, Matching, and ORD. Use MULTI_FIB when the BBQ record type is FIB_PLUS. The website displays the type as a badge.\n"
		"- Include distinctions that help course selection, such as representation, scope, number of taxa, or label type.\n"
		"- Replace opaque generator labels and local course codes with content distinctions when supported by the examples or filename.\n"
		"- State difficulty and prerequisites only when the supplied material supports them.\n"
		"- Use FiB (Fill in the Blank), MC (Multiple Choice), WOMC (Which One Multiple Choice), TFMS (True/False Multiple-Choice Statements), MA (Multiple Answer), NUM (Numeric), and ORD (Ordering). Preserve this capitalization.\n"
		"- Use Easy, Medium, and Hard capitalization for supported difficulty qualifiers.\n"
		"- Return only <title>Your Title Here</title>, with no Markdown, commentary, or trailing punctuation in the title.\n\n"
	)

	# get topics using this command
	# egrep '^bbq' problem_set_titles.yml | cut -d':' -f2- | sort
	prompt += (
		# Provide a list of sample titles to guide the model
		"<list of unrelated sample titles>\n"
		"Allosteric Enzymes in Metabolic Pathways (MC)\n"
		"Amino Acids from Chemical Structures (7 Choices, MC)\n"
		"Cell Disruption Techniques (Matching)\n"
		"pH Using the Henderson-Hasselbalch Equation (NUM)\n"
		"Dipeptide Sequences from Structures (FiB)\n"
		"Dipeptide Sequences from Structures (MC)\n"
		"Protein Net Charge at a Given pH (MC)\n"
		"Protein Molecular Weight from SDS-PAGE Migration (MC)\n"
		"Inhibition Type from Enzyme Activity Data (MC)\n"
		"Michaelis-Menten Constant (Km) from Enzyme Activity Data (MC)\n"
		"Optimal Buffering Range from pKa (MC)\n"
		"Chemical Reactions (TFMS)\n"
		"Enzyme Kinetics (TFMS)\n"
		"Michaelis-Menten Kinetics (TFMS)\n"
		"Column Chromatography Methods (Matching)\n"
		"Column Chromatography Methods (WOMC)\n"
		"Offspring HLA Genotypes (2 Markers, Color, MC)\n"
		"Phylogenetic Trees from Distance Matrices (5 Taxa, MC)\n"
		"RFLP Suspect Identification from DNA Profiles (Easy, 4 Suspects, MC)\n"
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

	# Return the generated prompt
	return prompt

#==============

# This function removes all HTML tags from a string.
def strip_html_tags(html_string: str) -> str:
	"""
	Removes all HTML tags from the input string and returns the plain text.

	Args:
		html_string (str): The HTML string to process.

	Returns:
		str: The plain text with HTML tags removed.
	"""
	# Use BeautifulSoup to parse the HTML and extract only the text content
	soup = bs4.BeautifulSoup(html_string, 'html.parser')
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

# This function sends a prompt to the selected LLM backend and retrieves the response.
def run_llm(client: llm.LLMClient, prompt: str) -> str:
	"""
	Generate a response from a pre-built LLMClient.

	Args:
		client (llm.LLMClient): Pre-built client (one per page CLI run).
		prompt (str): The prompt to send to the model.

	Returns:
		str: The response content generated by the model.
	"""
	# max_tokens=200 is an intentional cap suitable for short titles.
	response = client.generate(prompt, max_tokens=200)
	return response

#==============

# This function extracts the problem title from the model's response.
def get_problem_title_from_response(response_content: str) -> str:
	"""
	Extract and return the problem title from the response content.

	Args:
		response_content (str): The response content from the selected LLM backend.

	Returns:
		str: The extracted problem title.
	"""
	# Try XML tag extraction first (preferred format)
	title = llm.extract_xml_tag_content(response_content, "title")

	# Fall back to legacy ### markdown parsing for backward compatibility
	if not title:
		line_content = response_content.strip()
		if '\n' in response_content:
			lines = response_content.split('\n')
			for line in lines:
				sline = line.strip()
				if '###' in sline:
					line_content = sline
					break
		# Remove any characters before the '###' marker
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
def get_problem_title_from_file(client: llm.LLMClient, file_path: str) -> str:
	"""
	Generate a problem title from a file containing problem statements.

	Args:
		client (llm.LLMClient): Pre-built client (one per page CLI run).
		file_path (str): Path to the file containing problem statements.

	Returns:
		str: The generated problem title.
	"""
	# Check if the input file exists
	if not os.path.exists(file_path):
		raise IOError(f"Input file not found: {file_path}")

	# Load problem statements from the file
	problem_statements = load_problem_statements_from_file(file_path)

	# Generate a prompt using the loaded problem statements
	prompt = generate_title_prompt(file_path, problem_statements)

	# Run the selected LLM backend to generate a response for the prompt
	response_content = run_llm(client, prompt)

	# Extract the problem title from the model's response
	problem_title = get_problem_title_from_response(response_content)

	# Define a list of leading words that should be removed from the title
	leading_words = [
		'Calculate',
		'Calculating',
		'Determine',
		'Determining',
		'Identify',
		'Identifying',
	]

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
