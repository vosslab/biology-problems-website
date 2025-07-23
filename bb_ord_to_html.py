import argparse
import os
import random  # Required for selecting random questions

# Function to parse command-line arguments
def get_parser():
    parser = argparse.ArgumentParser(description="Process ordering questions into HTML.")
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
            answers = parts[2:]  # All the remaining parts are the answers
            questions.append((question_text, answers))
    
    print("Parsed questions:")
    print(questions)  # Debugging: print the structure of the questions
    return questions

# Function to generate HTML for each ordering question
def generate_ordering_html(question_text, answers):
    # Randomize answers for drag-and-drop functionality
    random.shuffle(answers)

    # Prepare the correct order to be injected into JavaScript
    correct_order_str = '", "'.join(answers)  # Turn the answers list into a string

    # HTML content
    html_content = f"""
    <div>
        <p style="font-family: Arial, sans-serif; margin: 20px;">
            {question_text}
        </p>

        <!-- List to hold answers for drag-and-drop -->
        <ul id="answerList" style="list-style-type: none; padding: 0;">
    """
    
    # Dynamically create list items for answers
    for idx, answer in enumerate(answers, start=1):
        html_content += f"""
            <li id="answer_{idx}" draggable="true" style="padding: 10px; border: 1px solid #999; margin-bottom: 5px; background-color: #f4f4f4;">
                {answer}
            </li>
        """
    
    html_content += """
        </ul>

        <p style="font-family: Arial, sans-serif; margin: 20px;">
            <button onclick="checkAnswers()" style="padding: 10px 20px;" class='md-button md-button--secondary'>Check Answers</button>
        </p>

        <div id="feedback" style="font-family: monospace; font-weight: bold; margin-top: 20px;"></div>

        <script>
        // Enable drag-and-drop functionality
        const answerList = document.getElementById('answerList');
        let draggedItem = null;

        answerList.addEventListener('dragstart', function(e) {
            draggedItem = e.target;
            e.target.style.opacity = '0.5';
        });

        answerList.addEventListener('dragend', function(e) {
            e.target.style.opacity = '1';
        });

        answerList.addEventListener('dragover', function(e) {
            e.preventDefault();
            const draggedOverItem = e.target;
            if (draggedItem !== draggedOverItem && draggedOverItem.nodeName === 'LI') {
                const allItems = [...answerList.querySelectorAll('li')];
                const draggedIndex = allItems.indexOf(draggedItem);
                const overIndex = allItems.indexOf(draggedOverItem);
                if (draggedIndex < overIndex) {
                    answerList.insertBefore(draggedItem, draggedOverItem.nextSibling);
                } else {
                    answerList.insertBefore(draggedItem, draggedOverItem);
                }
            }
        });

        // Check the answer order when the button is clicked
        function checkAnswers() {
            const listItems = document.querySelectorAll('#answerList li');
            let score = 0;
            let feedbackText = "";

            // Define the correct answer order dynamically
            const correctOrder = ["{correct_order_str}"];

            listItems.forEach((item, index) => {
                if (item.innerHTML === correctOrder[index]) {
                    score++;
                    feedbackText += `Answer ${index + 1}: Correct!<br>`;
                } else {
                    feedbackText += `Answer ${index + 1}: Incorrect. Correct answer is "${correctOrder[index]}"<br>`;
                }
            });
            
            document.getElementById('feedback').innerHTML = 'Your score: ' + score + '<br>' + feedbackText;
        }
        </script>
    </div>
    """
    
    return html_content

# Function to get a random question from a list of questions
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
    question_text, answers = random_question
    
    # Generate the HTML for this question
    final_html = generate_ordering_html(question_text, answers)
    
    # Generate output file name based on input file name and hex part of the question
    file_name = os.path.basename(file_path).split('.')[0]  # Get the hex value from the file name
    output_file = f"output_{file_name}.html"  # Prepend 'output_' and use hex value
    
    # Output HTML to the file
    with open(output_file, "w") as file:
        file.write(final_html)
    
    print(f"Output saved to {output_file}")

# Run the script
if __name__ == "__main__":
    main()
