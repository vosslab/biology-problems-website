#!/usr/bin/env python3

import os
import yaml

def extract_topic_title(md_file):
	"""Extract the first heading from a Markdown file."""
	with open(md_file, "r") as file:
		for line in file:
			if line.startswith("# "):  # Look for a top-level heading
				return line[2:].strip()  # Remove "# " and any surrounding whitespace
	return None  # Return None if no heading is found

def generate_mkdocs_yml(root_dir="docs", output_file="mkdocs.yml"):
	site_name = "Biology Problems OER"
	theme = {"name": "material"}
	nav = []

	# Add Home page
	nav.append({"Home": "index.md"})

	# Walk through directories in root_dir
	for subject in sorted(os.listdir(root_dir)):
		subject_path = os.path.join(root_dir, subject)
		if os.path.isdir(subject_path):
			subject_nav = []
			# Add list of topics for the subject
			subject_nav.append({"List of Topics": f"{subject}/index.md"})
			# Add each topic in the subject
			for topic in sorted(os.listdir(subject_path)):
				topic_path = os.path.join(subject_path, topic)
				topic_index = os.path.join(topic_path, "index.md")
				if os.path.isdir(topic_path) and os.path.exists(topic_index):
					# Extract topic title from index.md
					topic_title = extract_topic_title(topic_index)
					if not topic_title:
						topic_title = topic.replace("topic", "Topic ")  # Fallback title
					subject_nav.append({topic_title: f"{subject}/{topic}/index.md"})
			nav.append({subject.capitalize(): subject_nav})

	# Create the mkdocs.yml structure
	mkdocs_config = {
		"site_name": site_name,
		"theme": theme,
		"nav": nav
	}

	# Write to mkdocs.yml
	with open(output_file, "w") as file:
		yaml.dump(mkdocs_config, file, sort_keys=False)
	print(f"Generated {output_file} successfully!")

# Run the function
generate_mkdocs_yml()
