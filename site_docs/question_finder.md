# Question Finder

Find problem sets by name, subject, topic, and question type. Open a name to visit
its topic page and download the questions. This table searches problem-set metadata.

Prefer browsing? [Browse All Questions in the sitemap](sitemap.md).

<link rel="stylesheet" href="https://cdn.datatables.net/3.1.2/css/dataTables.dataTables.min.css" integrity="sha384-IkYzSBi8dm4Cg6IWFobByqhtleZ+PI1q8HYZXz9QgfRw+9LiJ3uVKcGDIWZFa+0k" crossorigin="anonymous">
<link rel="stylesheet" href="https://cdn.datatables.net/columncontrol/2.1.2/css/columnControl.dataTables.min.css" integrity="sha384-6J0Yn5VflAFZlwwk6LE8FtuppORLtNUl3VhRACLvSgnqT8GA0XA2VTIgkIyf/piJ" crossorigin="anonymous">
<link rel="stylesheet" href="../assets/stylesheets/question_finder.css">

<div id="question-finder-app" class="question-finder" data-catalog="../assets/data/question_finder.json">
  <p id="finder-status" role="status">Loading question sets. You can also use the sitemap above.</p>
  <button id="finder-retry" type="button" hidden>Retry loading</button>
  <noscript><p>Enable JavaScript to filter this table, or use the sitemap above.</p></noscript>
  <div id="finder-content" hidden>
    <div class="finder-toolbar">
      <label for="finder-search">Search questions</label>
      <input id="finder-search" type="search" placeholder="Search names, subjects, topics, or types">
      <button id="finder-clear" type="button">Clear all filters</button>
    </div>
    <p class="finder-help">Use the filter button in each column heading. Select several values to
      include any of them; filters in different columns narrow the results together.</p>
    <div id="finder-filters" aria-label="Active filters" role="group"></div>
    <div class="finder-scroll" tabindex="0" role="region" aria-label="Question sets table, scroll horizontally on narrow screens">
      <table id="finder-table">
        <caption>Question sets by subject, topic, and question type</caption>
        <thead><tr><th scope="col">Name</th><th scope="col">Subject</th><th scope="col">Topic</th><th scope="col">Question type</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
</div>

<script defer src="https://cdn.datatables.net/3.1.2/js/dataTables.min.js" integrity="sha384-cfmaUdZ8w93sHP/kwwcXXwphNEZNejRNqnytms+mOdggtuHvRys4cswJ3s3CbX33" crossorigin="anonymous"></script>
<script defer src="https://cdn.datatables.net/columncontrol/2.1.2/js/dataTables.columnControl.min.js" integrity="sha384-w4xGD4Wd38z0wwe63unidRa52DFkhBipcbjO1jHzLA5naorG/T97Xh9ffmEBwlWw" crossorigin="anonymous"></script>
<script defer src="../assets/scripts/question_finder.js"></script>
