# 9: Enzyme Allostery

Students analyze allosteric regulation, cooperativity, and sigmoidal binding curves, calculate Hill coefficients from hemoglobin oxygen binding data, and trace end-product feedback control through metabolic pathway diagrams.

**LibreTexts reference:** [Unit 2, Chapter 4: Enzyme Allostery](https://bio.libretexts.org/Courses/Roosevelt_University/BCHM_355_455_Biochemistry_(Roosevelt_University)/02%3A_Unit_2_-_Enzymes/2.04%3A_Enzyme_Allostery) <a href="https://bio.libretexts.org/Courses/Roosevelt_University/BCHM_355_455_Biochemistry_(Roosevelt_University)/02%3A_Unit_2_-_Enzymes/2.04%3A_Enzyme_Allostery" target="_blank" rel="noopener" aria-label="LibreTexts Unit 2, Chapter 4" title="Open LibreTexts chapter"><img src="/assets/images/libretexts.png" alt="LibreTexts" class="lt-icon"></a>

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

## Allosteric Enzyme Models from Conformational Descriptions

<div id="allosteric_enzyme_models-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-allosteric_enzyme_models-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-allosteric_enzyme_models-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-allosteric_enzyme_models.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-allosteric_enzyme_models-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-allosteric_enzyme_models.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-allosteric_enzyme_models-questions.txt" data-format="human_readable" data-filename="human_readable-allosteric_enzyme_models.html" aria-label="Generate Human-Readable">Human-Readable</button>
<a class="md-button custom-button webwork_pgml" href="downloads/allosteric_enzyme_models.pgml" download aria-label="Download WeBWorK PGML">WeBWorK PGML</a>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-allosteric_enzyme_models-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification bloom-ribbon" aria-label="Estimated Bloom labels for this bank"><span class="bloom-badge bloom-cognitive" data-bloom="Remember" title="Retrieve relevant knowledge from memory by recognizing or recalling.">Remember <span class="bloom-level">&#10112;</span></span><span class="bloom-badge bloom-knowledge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual <span class="bloom-level">&#10113;</span></span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Metabolic Regulation in Converging Pathways

<div id="feedback_merging_pathway-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-feedback_merging_pathway-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-feedback_merging_pathway-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-feedback_merging_pathway.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-feedback_merging_pathway-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-feedback_merging_pathway.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-feedback_merging_pathway-questions.txt" data-format="human_readable" data-filename="human_readable-feedback_merging_pathway.html" aria-label="Generate Human-Readable">Human-Readable</button>
<a class="md-button custom-button webwork_pgml" href="downloads/feedback_merging_pathway.pgml" download aria-label="Download WeBWorK PGML">WeBWorK PGML</a>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-feedback_merging_pathway-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification bloom-ribbon" aria-label="Estimated Bloom labels for this bank"><span class="bloom-badge bloom-cognitive" data-bloom="Analyze" title="Separate material into parts and identify their relationships and overall structure.">Analyze <span class="bloom-level">&#10115;</span></span><span class="bloom-badge bloom-knowledge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual <span class="bloom-level">&#10113;</span></span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Metabolic Regulation in Diverging Pathways

<div id="feedback_splitting_pathway-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-feedback_splitting_pathway-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-feedback_splitting_pathway-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-feedback_splitting_pathway.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-feedback_splitting_pathway-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-feedback_splitting_pathway.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-feedback_splitting_pathway-questions.txt" data-format="human_readable" data-filename="human_readable-feedback_splitting_pathway.html" aria-label="Generate Human-Readable">Human-Readable</button>
<a class="md-button custom-button webwork_pgml" href="downloads/feedback_splitting_pathway.pgml" download aria-label="Download WeBWorK PGML">WeBWorK PGML</a>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-feedback_splitting_pathway-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification bloom-ribbon" aria-label="Estimated Bloom labels for this bank"><span class="bloom-badge bloom-cognitive" data-bloom="Analyze" title="Separate material into parts and identify their relationships and overall structure.">Analyze <span class="bloom-level">&#10115;</span></span><span class="bloom-badge bloom-knowledge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual <span class="bloom-level">&#10113;</span></span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Hemoglobin Oxygen Affinity Under Different Conditions

<div id="hemoglobin_oxygen_affinity-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-hemoglobin_oxygen_affinity-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-hemoglobin_oxygen_affinity-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-hemoglobin_oxygen_affinity.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-hemoglobin_oxygen_affinity-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-hemoglobin_oxygen_affinity.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-hemoglobin_oxygen_affinity-questions.txt" data-format="human_readable" data-filename="human_readable-hemoglobin_oxygen_affinity.html" aria-label="Generate Human-Readable">Human-Readable</button>
<a class="md-button custom-button webwork_pgml" href="downloads/hemoglobin_oxygen_affinity.pgml" download aria-label="Download WeBWorK PGML">WeBWorK PGML</a>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-hemoglobin_oxygen_affinity-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification bloom-ribbon" aria-label="Estimated Bloom labels for this bank"><span class="bloom-badge bloom-cognitive" data-bloom="Remember" title="Retrieve relevant knowledge from memory by recognizing or recalling.">Remember <span class="bloom-level">&#10112;</span></span><span class="bloom-badge bloom-knowledge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual <span class="bloom-level">&#10113;</span></span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


## Allosteric Enzymes in Metabolic Pathways

<div id="metabolic_pathway_allosteric-button-container" class="button-container">
<a class="md-button custom-button bb_text" href="bbq-metabolic_pathway_allosteric-questions.txt" download aria-label="Download BBQ Text">BBQ Text</a>
<button type="button" class="md-button custom-button bb_export qpm-package-download" data-bbq="bbq-metabolic_pathway_allosteric-questions.txt" data-format="blackboard_export_zip" data-filename="blackboard_export_zip-metabolic_pathway_allosteric.zip" aria-label="Generate Blackboard Ultra pool-export ZIP">Blackboard Ultra ZIP</button>
<button type="button" class="md-button custom-button canvas_qti qpm-package-download" data-bbq="bbq-metabolic_pathway_allosteric-questions.txt" data-format="canvas_qti_v1_2" data-filename="canvas_qti_v1_2-metabolic_pathway_allosteric.zip" aria-label="Generate Canvas/ADAPT QTI v1.2">Canvas/ADAPT QTI v1.2</button>
<button type="button" class="md-button custom-button human_read qpm-package-download" data-bbq="bbq-metabolic_pathway_allosteric-questions.txt" data-format="human_readable" data-filename="human_readable-metabolic_pathway_allosteric.html" aria-label="Generate Human-Readable">Human-Readable</button>
<a class="md-button custom-button webwork_pgml" href="downloads/metabolic_pathway_allosteric.pgml" download aria-label="Download WeBWorK PGML">WeBWorK PGML</a>
<span class="qpm-package-status" role="status" aria-live="polite"></span>
<progress class="qpm-package-progress" max="1" value="0" hidden aria-label="Package generation progress"></progress>
</div><div class="qpm-selftest" data-bbq="bbq-metabolic_pathway_allosteric-questions.txt">
<div class="selftest-question-header selftest-question-placeholder">
<span class="question-type-badges"><abbr class="question-type question-type-mc" title="Multiple Choice">MC</abbr></span>
<span class="bloom-classification bloom-ribbon" aria-label="Estimated Bloom labels for this bank"><span class="bloom-badge bloom-cognitive" data-bloom="Understand" title="Construct meaning by interpreting, classifying, summarizing, comparing, or explaining.">Understand <span class="bloom-level">&#10113;</span></span><span class="bloom-badge bloom-knowledge" data-bloom="Conceptual" title="Knowledge of categories, principles, theories, models, and how they relate.">Conceptual <span class="bloom-level">&#10113;</span></span></span>
</div>
  <div class="selftest-reroll-content"></div>
</div>


