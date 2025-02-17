import argparse
import os
import random  # Required for selecting random questions

# Function to parse command-line arguments
def get_parser():
    parser = argparse.ArgumentParser(description="Process matching questions into HTML.")
    parser.add_argument('-f', '--file', dest='file_path', required=True, help='Path to the input question file')
    return parser.parse_args()

# Function to parse the input question file
def parse_question_file(file_path):
    questions = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) < 2:  # Skip lines that don't have the expected format
                continue
            question_text = parts[1]
            answers_and_matches = [(parts[i], parts[i + 1]) for i in range(2, len(parts), 2)]
            questions.append((question_text, answers_and_matches))
    
    print("Parsed questions:")
    print(questions)  # Debugging: print the structure of the questions
    return questions

# Function to generate HTML for each question
def generate_matching_html(question_text, answers_and_matches):
    html_content = f"""
    <div>
        <p style="font-family: Arial, sans-serif; margin: 20px;">
            {question_text}
        </p>

        <!-- Wrapper table to hold the two tables side-by-side -->
        <table style="border-collapse: collapse;">
            <tr>
                <!-- Left table: Numbered matching questions -->
                <td style="vertical-align: top; padding: 10px;">
                    <table style="border: 1px solid #999; border-collapse: collapse; font-family: Arial, sans-serif;">
                        <thead>
                            <tr>
                                <th style="border: 1px solid #999; padding: 10px; background-color: #eee;">Numbered Term</th>
                                <th style="border: 1px solid #999; padding: 10px; background-color: #eee;">Your Answer</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    # Dynamically create rows for terms
    for idx, (answer, match) in enumerate(answers_and_matches, start=1):
        html_content += f"""
            <tr>
                <td style="border: 1px solid #999; padding: 10px;">{idx}. {answer}</td>
                <td style="border: 1px solid #999; padding: 5px;">
                    <select id="answer_{idx}">
                        <option value="">--Select--</option>
        """
        # Add dynamic options based on the number of matches
        options = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:len(answers_and_matches)]
        for option in options:
            html_content += f'<option value="{option}">{option}</option>'
        
        html_content += f"""
                    </select>
                </td>
            </tr>
        """
    
    html_content += """
                        </tbody>
                    </table>
                </td>

                <!-- Right table: Lettered answer choices -->
                <td style="vertical-align: top; padding: 10px;">
                    <table style="border: 1px solid #999; border-collapse: collapse; font-family: Arial, sans-serif;">
                        <thead>
                            <tr>
                                <th style="border: 1px solid #999; padding: 10px; background-color: #eee;">Letter</th>
                                <th style="border: 1px solid #999; padding: 10px; background-color: #eee;">Definition</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # Dynamically create rows for the answers
    for idx, (answer, match) in enumerate(answers_and_matches, start=1):
        letter = chr(65 + idx - 1)  # 'A', 'B', 'C', etc.
        html_content += f"""
            <tr>
                <td style="border: 1px solid #999; padding: 10px;" align="center">{letter}</td>
                <td style="border: 1px solid #999; padding: 10px;">{match}</td>
            </tr>
        """
    
    html_content += """
                        </tbody>
                    </table>
                </td>
            </tr>
        </table>

        <p style="font-family: Arial, sans-serif; margin: 20px;">
            <button onclick="checkAnswers()" style="padding: 10px 20px;" class='md-button md-button--secondary'>Check Answers</button>
        </p>

        <div id="feedback" style="font-family: monospace; font-weight: bold; margin-top: 20px;"></div>

        <script>
        function checkAnswers() {
            var score = 0;
            var feedbackText = "";
    """
    
    for idx in range(1, len(answers_and_matches) + 1):
        html_content += f"""
            var answer_{idx} = document.getElementById('answer_{idx}').value;
            var correct_answer_{idx} = '{chr(65 + idx - 1)}';  // Replace with actual correct answer if available
            if (answer_{idx} === correct_answer_{idx}) {{
                score++;
                feedbackText += '{idx}. Correct!<br>';
            }} else {{
                feedbackText += '{idx}. Incorrect. Correct answer is ' + correct_answer_{idx} + '<br>';
            }}
        """
    
    html_content += """
            document.getElementById('feedback').innerHTML = 'Your score: ' + score;
        }
        </script>
    </div>
    """
    
    return html_content

# Function to get a random question from a file
def get_random_question(questions):
    return random.choice(questions)

# Main function to handle the full process
def main():
    args = get_parser()
    file_path = args.file_path

    # Parse the questions from the file
    questions = parse_question_file(file_path)

    # Pick a random question
    random_question = get_random_question(questions)
    question_text, answers_and_matches = random_question
    
    # Generate the HTML for this question
    final_html = generate_matching_html(question_text, answers_and_matches)
    
    # Generate output file name based on input file name and hex part of the question
    file_name = os.path.basename(file_path).split('-')[1]  # Get the hex value from the file name
    output_file = f"output_{file_name}.html"  # Prepend 'output_' and use hex value
    
    # Output HTML to the file
    with open(output_file, "w") as file:
        file.write(final_html)
    
    print(f"Output saved to {output_file}")

# Run the script
if __name__ == "__main__":
    main()
