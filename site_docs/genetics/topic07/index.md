# 7: Chi Square Analysis

Students calculate offspring probabilities from visible outcomes and small families, then use expected counts, hypotheses, and chi-square results to evaluate Mendelian predictions.

**LibreTexts reference:** [Chapter 7: Chi Square Analysis](https://bio.libretexts.org/Courses/Roosevelt_University/Advanced_Genetics:_Mechanisms_of_Inheritance_and_Analysis/07:_Chi_Square_Analysis) <a href="https://bio.libretexts.org/Courses/Roosevelt_University/Advanced_Genetics:_Mechanisms_of_Inheritance_and_Analysis/07:_Chi_Square_Analysis" target="_blank" rel="noopener" aria-label="LibreTexts Chapter 7" title="Open LibreTexts chapter"><img src="/assets/images/libretexts.png" alt="LibreTexts" class="lt-icon"></a>

<details class="bloom-scales"><summary>Bloom's scales</summary>
<p>Two dimensions describe the assessed task. Numbers identify categories, not difficulty ratings.</p><div class="bloom-scales-grid">
<section><h3>Cognitive Process Dimension</h3><dl>
<dt><span class="bloom-badge" data-bloom="Remember" title="Retrieve relevant knowledge from memory by recognizing or recalling.">Remember (1)</span></dt><dd>Retrieve relevant knowledge from memory by recognizing or recalling.</dd>
<dt><span class="bloom-badge" data-bloom="Understand" title="Construct meaning by interpreting, classifying, summarizing, comparing, or explaining.">Understand (2)</span></dt><dd>Construct meaning by interpreting, classifying, summarizing, comparing, or explaining.</dd>
<dt><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span></dt><dd>Carry out or use a procedure in a given situation.</dd>
<dt><span class="bloom-badge" data-bloom="Analyze" title="Separate material into parts and identify their relationships and overall structure.">Analyze (4)</span></dt><dd>Separate material into parts and identify their relationships and overall structure.</dd>
<dt><span class="bloom-badge" data-bloom="Evaluate" title="Make judgments using criteria and standards through checking or critique.">Evaluate (5)</span></dt><dd>Make judgments using criteria and standards through checking or critique.</dd>
<dt><span class="bloom-badge" data-bloom="Create" title="Combine elements into a coherent new whole through generating, planning, or producing.">Create (6)</span></dt><dd>Combine elements into a coherent new whole through generating, planning, or producing.</dd>
</dl></section>
<section><h3>Knowledge Dimension</h3><dl>
<dt><span class="bloom-badge" data-bloom="Factual" title="Knowledge of basic elements, terminology, and specific details.">Factual (1)</span></dt><dd>Knowledge of basic elements, terminology, and specific details.</dd>
<dt><span class="bloom-badge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual (2)</span></dt><dd>Knowledge of categories, principles, theories, models, and how they relate.</dd>
<dt><span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></dt><dd>Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.</dd>
<dt><span class="bloom-badge" data-bloom="Metacognitive" title="Knowledge of learning strategies, thinking tasks, and one&#x27;s own strengths and limitations.">Metacognitive (4)</span></dt><dd>Knowledge of learning strategies, thinking tasks, and one&#x27;s own strengths and limitations.</dd>
</dl></section>
</div><p>Based on Anderson and Krathwohl (2001), chapters 4-5. <a href="https://celt.iastate.edu/prepare-and-teach/design-your-course/blooms-taxonomy/">Iowa State Bloom's taxonomy guide</a>.</p></details>

## Chi-Square Terms from Definitions

<div id="MATCH-chi-square_terms-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-MATCH-chi-square_terms-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-MATCH-chi-square_terms-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-MATCH-chi-square_terms.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-MATCH-chi-square_terms-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-MATCH-chi-square_terms.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-MATCH-chi-square_terms-questions.txt" data-format="human_readable" data-filename="human_readable-MATCH-chi-square_terms.html" aria-label="Generate Human-Readable">Human-Readable</button>
<a class="md-button custom-button webwork_pgml" href="downloads/chi-square_terms-matching.pgml" download aria-label="Download WeBWorK PGML">WeBWorK PGML</a>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-MATCH-chi-square_terms-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-matching" title="Matching">Matching</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Remember" title="Retrieve relevant knowledge from memory by recognizing or recalling.">Remember (1)</span> <span class="bloom-badge" data-bloom="Factual" title="Knowledge of basic elements, terminology, and specific details.">Factual (1)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Chi-Square Tests

<div id="TFMS-chi-square-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-TFMS-chi-square-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-TFMS-chi-square-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-TFMS-chi-square.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-TFMS-chi-square-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-TFMS-chi-square.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-TFMS-chi-square-questions.txt" data-format="human_readable" data-filename="human_readable-TFMS-chi-square.html" aria-label="Generate Human-Readable">Human-Readable</button>
<a class="md-button custom-button webwork_pgml" href="downloads/chi-square.pg" download aria-label="Download WeBWorK PGML">WeBWorK PGML</a>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-TFMS-chi-square-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-tfms" title="True/False Statements (Multiple Choice)">T/F Statements (MC)</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Remember" title="Retrieve relevant knowledge from memory by recognizing or recalling.">Remember (1)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Chi-Square Terms from Definitions

<div id="WOMC-chi-square_terms-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-WOMC-chi-square_terms-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-WOMC-chi-square_terms-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-WOMC-chi-square_terms.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-WOMC-chi-square_terms-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-WOMC-chi-square_terms.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-WOMC-chi-square_terms-questions.txt" data-format="human_readable" data-filename="human_readable-WOMC-chi-square_terms.html" aria-label="Generate Human-Readable">Human-Readable</button>
<a class="md-button custom-button webwork_pgml" href="downloads/chi-square_terms-which_one.pgml" download aria-label="Download WeBWorK PGML">WeBWorK PGML</a>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-WOMC-chi-square_terms-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-womc" title="Which One Multiple Choice (from matching content)">WOMC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Remember" title="Retrieve relevant knowledge from memory by recognizing or recalling.">Remember (1)</span> <span class="bloom-badge" data-bloom="Factual" title="Knowledge of basic elements, terminology, and specific details.">Factual (1)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Chi-Square Values for Phenotypic Ratios

<div id="chi_square_calculated-ACCEPT-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_calculated-ACCEPT-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_calculated-ACCEPT-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_calculated-ACCEPT.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_calculated-ACCEPT-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_calculated-ACCEPT.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_calculated-ACCEPT-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_calculated-ACCEPT.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_calculated-ACCEPT-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-num" title="Numeric">NUM</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Hypothesis Decisions from Chi-Square Tests

<div id="chi_square_choices-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_choices-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_choices-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_choices.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_choices-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_choices.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_choices-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_choices.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_choices-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Completing a Dice Chi-Square Calculation

<div id="chi_square_dice-calculate-MC-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_dice-calculate-MC-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_dice-calculate-MC-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_dice-calculate-MC.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_dice-calculate-MC-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_dice-calculate-MC.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_dice-calculate-MC-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_dice-calculate-MC.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_dice-calculate-MC-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Evaluating a Dice Chi-Square Test

<div id="chi_square_dice-conclusions-MA-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_dice-conclusions-MA-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_dice-conclusions-MA-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_dice-conclusions-MA.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_dice-conclusions-MA-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_dice-conclusions-MA.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_dice-conclusions-MA-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_dice-conclusions-MA.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_dice-conclusions-MA-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-ma" title="Multiple Answer">MA</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Counts and Degrees of Freedom in a Dice Experiment

<div id="chi_square_dice-connect-MATCH-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_dice-connect-MATCH-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_dice-connect-MATCH-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_dice-connect-MATCH.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_dice-connect-MATCH-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_dice-connect-MATCH.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_dice-connect-MATCH-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_dice-connect-MATCH.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_dice-connect-MATCH-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-matching" title="Matching">Matching</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Degrees of Freedom for Six-Sided Dice

<div id="chi_square_dice-df-MC-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_dice-df-MC-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_dice-df-MC-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_dice-df-MC.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_dice-df-MC-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_dice-df-MC.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_dice-df-MC-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_dice-df-MC.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_dice-df-MC-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Expected Counts for Six-Sided Dice

<div id="chi_square_dice-expected-MC-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_dice-expected-MC-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_dice-expected-MC-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_dice-expected-MC.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_dice-expected-MC-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_dice-expected-MC.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_dice-expected-MC-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_dice-expected-MC.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_dice-expected-MC-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Interpreting Dice Chi-Square Results

<div id="chi_square_dice-interpret-MC-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_dice-interpret-MC-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_dice-interpret-MC-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_dice-interpret-MC.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_dice-interpret-MC-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_dice-interpret-MC.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_dice-interpret-MC-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_dice-interpret-MC.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_dice-interpret-MC-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Evaluate" title="Make judgments using criteria and standards through checking or critique.">Evaluate (5)</span> <span class="bloom-badge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual (2)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Errors in Chi-Square Calculations and Hypothesis Decisions

<div id="chi_square_errors-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_errors-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_errors-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_errors.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_errors-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_errors.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_errors-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_errors.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_errors-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Evaluate" title="Make judgments using criteria and standards through checking or critique.">Evaluate (5)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Chi-Square Tests for Hardy-Weinberg Equilibrium

<div id="chi_square_hardy_weinberg-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_hardy_weinberg-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_hardy_weinberg-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_hardy_weinberg.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_hardy_weinberg-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_hardy_weinberg.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_hardy_weinberg-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_hardy_weinberg.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_hardy_weinberg-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Evaluate" title="Make judgments using criteria and standards through checking or critique.">Evaluate (5)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Choosing the Alternative Hypothesis for a Genetic Cross

<div id="chi_square_hypotheses-alt-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_hypotheses-alt-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_hypotheses-alt-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_hypotheses-alt.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_hypotheses-alt-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_hypotheses-alt.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_hypotheses-alt-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_hypotheses-alt.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_hypotheses-alt-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Understand" title="Construct meaning by interpreting, classifying, summarizing, comparing, or explaining.">Understand (2)</span> <span class="bloom-badge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual (2)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Choosing the Null Hypothesis for a Genetic Cross

<div id="chi_square_hypotheses-null-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_hypotheses-null-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_hypotheses-null-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_hypotheses-null.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_hypotheses-null-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_hypotheses-null.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_hypotheses-null-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_hypotheses-null.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_hypotheses-null-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Understand" title="Construct meaning by interpreting, classifying, summarizing, comparing, or explaining.">Understand (2)</span> <span class="bloom-badge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual (2)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Reviewing a Lab Partner&#x27;s Chi-Square Hypotheses

<div id="chi_square_hypotheses_lab_partner-hypotheses_partner-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-chi_square_hypotheses_lab_partner-hypotheses_partner-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-chi_square_hypotheses_lab_partner-hypotheses_partner-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-chi_square_hypotheses_lab_partner-hypotheses_partner.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-chi_square_hypotheses_lab_partner-hypotheses_partner-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-chi_square_hypotheses_lab_partner-hypotheses_partner.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-chi_square_hypotheses_lab_partner-hypotheses_partner-questions.txt" data-format="human_readable" data-filename="human_readable-chi_square_hypotheses_lab_partner-hypotheses_partner.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-chi_square_hypotheses_lab_partner-hypotheses_partner-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Evaluate" title="Make judgments using criteria and standards through checking or critique.">Evaluate (5)</span> <span class="bloom-badge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual (2)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Offspring Sex Distribution Using the Binomial Model

<div id="probabiliy_of_progeny-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-probabiliy_of_progeny-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-probabiliy_of_progeny-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-probabiliy_of_progeny.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-probabiliy_of_progeny-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-probabiliy_of_progeny.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-probabiliy_of_progeny-questions.txt" data-format="human_readable" data-filename="human_readable-probabiliy_of_progeny.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-probabiliy_of_progeny-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Probabilities for Two to Four Offspring

<div id="progeny_probability_practice-calculate-MC-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-progeny_probability_practice-calculate-MC-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-progeny_probability_practice-calculate-MC-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-progeny_probability_practice-calculate-MC.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-progeny_probability_practice-calculate-MC-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-progeny_probability_practice-calculate-MC.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-progeny_probability_practice-calculate-MC-questions.txt" data-format="human_readable" data-filename="human_readable-progeny_probability_practice-calculate-MC.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-progeny_probability_practice-calculate-MC-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Offspring Probability and Independence

<div id="progeny_probability_practice-independence-MC-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-progeny_probability_practice-independence-MC-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-progeny_probability_practice-independence-MC-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-progeny_probability_practice-independence-MC.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-progeny_probability_practice-independence-MC-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-progeny_probability_practice-independence-MC.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-progeny_probability_practice-independence-MC-questions.txt" data-format="human_readable" data-filename="human_readable-progeny_probability_practice-independence-MC.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-progeny_probability_practice-independence-MC-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual (2)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Exactly and At Least in Offspring Outcomes

<div id="progeny_probability_practice-outcomes-MA-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-progeny_probability_practice-outcomes-MA-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-progeny_probability_practice-outcomes-MA-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-progeny_probability_practice-outcomes-MA.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-progeny_probability_practice-outcomes-MA-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-progeny_probability_practice-outcomes-MA.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-progeny_probability_practice-outcomes-MA-questions.txt" data-format="human_readable" data-filename="human_readable-progeny_probability_practice-outcomes-MA.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-progeny_probability_practice-outcomes-MA-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-ma" title="Multiple Answer">MA</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Offspring Probabilities from Tables

<div id="progeny_probability_practice-tables-MATCH-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-progeny_probability_practice-tables-MATCH-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-progeny_probability_practice-tables-MATCH-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-progeny_probability_practice-tables-MATCH.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-progeny_probability_practice-tables-MATCH-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-progeny_probability_practice-tables-MATCH.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-progeny_probability_practice-tables-MATCH-questions.txt" data-format="human_readable" data-filename="human_readable-progeny_probability_practice-tables-MATCH.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-progeny_probability_practice-tables-MATCH-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-matching" title="Matching">Matching</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


