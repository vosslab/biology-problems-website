# 7: Z-Tests, T-Tests, F-Tests, and ANOVA

Students analyze biological datasets using one-sample z-tests and t-tests, two-sample t-tests, F-tests for comparing variances, and ANOVA for comparing group means.

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

## One-Sample t-Test p-Values from Birth Weight Data (One-Tailed)

<div id="babies_one_sample_t_test-tails1-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-babies_one_sample_t_test-tails1-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-babies_one_sample_t_test-tails1-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-babies_one_sample_t_test-tails1.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-babies_one_sample_t_test-tails1-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-babies_one_sample_t_test-tails1.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-babies_one_sample_t_test-tails1-questions.txt" data-format="human_readable" data-filename="human_readable-babies_one_sample_t_test-tails1.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-babies_one_sample_t_test-tails1-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-num" title="Numeric">NUM</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## One-Sample z-Test p-Values from Birth Weight Data (One-Tailed)

<div id="babies_one_sample_z_test-ztest-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-babies_one_sample_z_test-ztest-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-babies_one_sample_z_test-ztest-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-babies_one_sample_z_test-ztest.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-babies_one_sample_z_test-ztest-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-babies_one_sample_z_test-ztest.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-babies_one_sample_z_test-ztest-questions.txt" data-format="human_readable" data-filename="human_readable-babies_one_sample_z_test-ztest.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-babies_one_sample_z_test-ztest-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-num" title="Numeric">NUM</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Two-Sample t-Test p-Values from Birth Weight Data (One-Tailed)

<div id="babies_two_sample_t_test-tails1-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-babies_two_sample_t_test-tails1-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-babies_two_sample_t_test-tails1-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-babies_two_sample_t_test-tails1.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-babies_two_sample_t_test-tails1-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-babies_two_sample_t_test-tails1.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-babies_two_sample_t_test-tails1-questions.txt" data-format="human_readable" data-filename="human_readable-babies_two_sample_t_test-tails1.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-babies_two_sample_t_test-tails1-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-num" title="Numeric">NUM</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## One-Way ANOVA p-Values from Shannon Diversity Data (5 Years)

<div id="busse_woods_anova-anova-5year-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-busse_woods_anova-anova-5year-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-busse_woods_anova-anova-5year-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-busse_woods_anova-anova-5year.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-busse_woods_anova-anova-5year-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-busse_woods_anova-anova-5year.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-busse_woods_anova-anova-5year-questions.txt" data-format="human_readable" data-filename="human_readable-busse_woods_anova-anova-5year.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-busse_woods_anova-anova-5year-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-num" title="Numeric">NUM</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## One-Sample z-Test p-Values from Shannon Diversity Data

<div id="busse_woods_one_sample_tests-ztest-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-busse_woods_one_sample_tests-ztest-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-busse_woods_one_sample_tests-ztest-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-busse_woods_one_sample_tests-ztest.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-busse_woods_one_sample_tests-ztest-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-busse_woods_one_sample_tests-ztest.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-busse_woods_one_sample_tests-ztest-questions.txt" data-format="human_readable" data-filename="human_readable-busse_woods_one_sample_tests-ztest.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-busse_woods_one_sample_tests-ztest-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-num" title="Numeric">NUM</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Two-Sample F-Test p-Values from Shannon Diversity Data (One-Tailed)

<div id="busse_woods_two_sample_f_test-tails1-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-busse_woods_two_sample_f_test-tails1-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-busse_woods_two_sample_f_test-tails1-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-busse_woods_two_sample_f_test-tails1.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-busse_woods_two_sample_f_test-tails1-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-busse_woods_two_sample_f_test-tails1.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-busse_woods_two_sample_f_test-tails1-questions.txt" data-format="human_readable" data-filename="human_readable-busse_woods_two_sample_f_test-tails1.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-busse_woods_two_sample_f_test-tails1-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-num" title="Numeric">NUM</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Two-Sample t-Test p-Values from Shannon Diversity Data (One-Tailed)

<div id="busse_woods_two_sample_t_test-tails1-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-busse_woods_two_sample_t_test-tails1-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-busse_woods_two_sample_t_test-tails1-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-busse_woods_two_sample_t_test-tails1.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-busse_woods_two_sample_t_test-tails1-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-busse_woods_two_sample_t_test-tails1.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-busse_woods_two_sample_t_test-tails1-questions.txt" data-format="human_readable" data-filename="human_readable-busse_woods_two_sample_t_test-tails1.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-busse_woods_two_sample_t_test-tails1-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-num" title="Numeric">NUM</abbr></span>
<span class="bloom-classification" aria-label="Estimated Bloom labels for this bank" title="Estimated Bloom labels for this question bank"><span class="bloom-badge" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply (3)</span> <span class="bloom-badge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural (3)</span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


