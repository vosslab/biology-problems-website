# Multiple Choice Question

<p>Based on only their molecular formula, which one of the following compounds is most likely a lipid?</p>
<form>
<div>
<input type="radio" id="option0" name="answer" data-correct="false">
<label for="option0">C<sub>11</sub>H<sub>15</sub>N<sub>5</sub>O<sub>11</sub></label>
</div>
<div>
<input type="radio" id="option1" name="answer" data-correct="false">
<label for="option1">C<sub>14</sub>H<sub>17</sub>N<sub>8</sub>O<sub>7</sub>P</label>
</div>
<div>
<input type="radio" id="option2" name="answer" data-correct="false">
<label for="option2">C<sub>14</sub>H<sub>17</sub>N<sub>8</sub>O<sub>8</sub>P</label>
</div>
<div>
<input type="radio" id="option3" name="answer" data-correct="false">
<label for="option3">C<sub>10</sub>H<sub>13</sub>O<sub>4</sub>N<sub>5</sub></label>
</div>
<div>
<input type="radio" id="option4" name="answer" data-correct="true">
<label for="option4">C<sub>40</sub>H<sub>58</sub>O<sub>3</sub></label>
</div>
<button type="button" onclick="checkAnswer()">Check</button>
</form>
<div id="result"></div>

<script>
function checkAnswer() {
    const options = document.getElementsByName('answer');
    let correctOption = null;
    for (let i = 0; i < options.length; i++) {
        if (options[i].dataset.correct === 'true') {
            correctOption = options[i];
        }
    }
    const selected = Array.from(options).find(option => option.checked);
    const resultDiv = document.getElementById('result');
    if (selected) {
        if (selected === correctOption) {
            resultDiv.style.color = 'green';
            resultDiv.textContent = 'CORRECT';
        } else {
            resultDiv.style.color = 'red';
            resultDiv.textContent = 'incorrect';
        }
    } else {
        resultDiv.style.color = 'black';
        resultDiv.textContent = 'Please select an answer.';
    }
}
</script>
