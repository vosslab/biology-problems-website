# 13: Bioinformatics

Students analyze GAPDH DNA and protein sequences using BLAST, interpret alignment scores, and use bioinformatics databases to compare sequences across species.

<details class="bloom-scales"><summary>Bloom's scales</summary>
<p>Two dimensions describe the assessed task. Numbers identify categories, not difficulty ratings.</p><div class="bloom-scales-grid">
<section><h3>Cognitive Process Dimension</h3><dl>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-cognitive" data-bloom="Remember" title="Retrieve relevant knowledge from memory by recognizing or recalling.">Remember <span class="bloom-level">&#10112;</span></span></span></dt><dd>Retrieve relevant knowledge from memory by recognizing or recalling.</dd>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-cognitive" data-bloom="Understand" title="Construct meaning by interpreting, classifying, summarizing, comparing, or explaining.">Understand <span class="bloom-level">&#10113;</span></span></span></dt><dd>Construct meaning by interpreting, classifying, summarizing, comparing, or explaining.</dd>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-cognitive" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply <span class="bloom-level">&#10114;</span></span></span></dt><dd>Carry out or use a procedure in a given situation.</dd>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-cognitive" data-bloom="Analyze" title="Separate material into parts and identify their relationships and overall structure.">Analyze <span class="bloom-level">&#10115;</span></span></span></dt><dd>Separate material into parts and identify their relationships and overall structure.</dd>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-cognitive" data-bloom="Evaluate" title="Make judgments using criteria and standards through checking or critique.">Evaluate <span class="bloom-level">&#10116;</span></span></span></dt><dd>Make judgments using criteria and standards through checking or critique.</dd>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-cognitive" data-bloom="Create" title="Combine elements into a coherent new whole through generating, planning, or producing.">Create <span class="bloom-level">&#10117;</span></span></span></dt><dd>Combine elements into a coherent new whole through generating, planning, or producing.</dd>
</dl></section>
<section><h3>Knowledge Dimension</h3><dl>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-knowledge" data-bloom="Factual" title="Knowledge of basic elements, terminology, and specific details.">Factual <span class="bloom-level">&#10112;</span></span></span></dt><dd>Knowledge of basic elements, terminology, and specific details.</dd>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-knowledge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual <span class="bloom-level">&#10113;</span></span></span></dt><dd>Knowledge of categories, principles, theories, models, and how they relate.</dd>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-knowledge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural <span class="bloom-level">&#10114;</span></span></span></dt><dd>Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.</dd>
<dt><span class="bloom-ribbon bloom-solo"><span class="bloom-badge bloom-knowledge" data-bloom="Metacognitive" title="Knowledge of learning strategies, thinking tasks, and one&#x27;s own strengths and limitations.">Metacognitive <span class="bloom-level">&#10115;</span></span></span></dt><dd>Knowledge of learning strategies, thinking tasks, and one&#x27;s own strengths and limitations.</dd>
</dl></section>
</div><p>Based on Anderson and Krathwohl (2001), chapters 4-5. <a href="https://celt.iastate.edu/prepare-and-teach/design-your-course/blooms-taxonomy/">Iowa State Bloom's taxonomy guide</a>.</p></details>

## Degenerate Primer Codes from Sequence Alignments

<div id="consensus_sequence_FIB-arbitrary_code-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-consensus_sequence_FIB-arbitrary_code-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-consensus_sequence_FIB-arbitrary_code-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-consensus_sequence_FIB-arbitrary_code.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-consensus_sequence_FIB-arbitrary_code-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-consensus_sequence_FIB-arbitrary_code.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-consensus_sequence_FIB-arbitrary_code-questions.txt" data-format="human_readable" data-filename="human_readable-consensus_sequence_FIB-arbitrary_code.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-consensus_sequence_FIB-arbitrary_code-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-fib" title="Fill in the Blank">FiB</abbr></span>
<span class="bloom-classification bloom-ribbon" aria-label="Estimated Bloom labels for this bank"><span class="bloom-badge bloom-cognitive" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply <span class="bloom-level">&#10114;</span></span><span class="bloom-badge bloom-knowledge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural <span class="bloom-level">&#10114;</span></span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Consensus Sequences from Alignments (Easy)

<div id="consensus_sequence_FIB-easy-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-consensus_sequence_FIB-easy-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-consensus_sequence_FIB-easy-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-consensus_sequence_FIB-easy.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-consensus_sequence_FIB-easy-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-consensus_sequence_FIB-easy.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-consensus_sequence_FIB-easy-questions.txt" data-format="human_readable" data-filename="human_readable-consensus_sequence_FIB-easy.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-consensus_sequence_FIB-easy-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-fib" title="Fill in the Blank">FiB</abbr></span>
<span class="bloom-classification bloom-ribbon" aria-label="Estimated Bloom labels for this bank"><span class="bloom-badge bloom-cognitive" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply <span class="bloom-level">&#10114;</span></span><span class="bloom-badge bloom-knowledge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural <span class="bloom-level">&#10114;</span></span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Consensus Sequences from Alignments (Hard)

<div id="consensus_sequence_FIB-hard-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-consensus_sequence_FIB-hard-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-consensus_sequence_FIB-hard-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-consensus_sequence_FIB-hard.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-consensus_sequence_FIB-hard-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-consensus_sequence_FIB-hard.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-consensus_sequence_FIB-hard-questions.txt" data-format="human_readable" data-filename="human_readable-consensus_sequence_FIB-hard.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-consensus_sequence_FIB-hard-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-fib" title="Fill in the Blank">FiB</abbr></span>
<span class="bloom-classification bloom-ribbon" aria-label="Estimated Bloom labels for this bank"><span class="bloom-badge bloom-cognitive" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply <span class="bloom-level">&#10114;</span></span><span class="bloom-badge bloom-knowledge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural <span class="bloom-level">&#10114;</span></span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Consensus Sequences from Alignments

<div id="consensus_sequence_MC-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-consensus_sequence_MC-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-consensus_sequence_MC-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-consensus_sequence_MC.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-consensus_sequence_MC-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-consensus_sequence_MC.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-consensus_sequence_MC-questions.txt" data-format="human_readable" data-filename="human_readable-consensus_sequence_MC.html" aria-label="Generate Human-Readable">Human-Readable</button>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-consensus_sequence_MC-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification bloom-ribbon" aria-label="Estimated Bloom labels for this bank"><span class="bloom-badge bloom-cognitive" data-bloom="Apply" title="Carry out or use a procedure in a given situation.">Apply <span class="bloom-level">&#10114;</span></span><span class="bloom-badge bloom-knowledge" data-bloom="Procedural" title="Knowledge of subject-specific skills, algorithms, techniques, methods, and when to use them.">Procedural <span class="bloom-level">&#10114;</span></span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


