/* Instructor metadata search. DataTables and ColumnControl are page-scoped CDN libraries. */
(function () {
  "use strict";

  const root = document.getElementById("question-finder-app");
  if (!root) return;
  const status = document.getElementById("finder-status");
  const content = document.getElementById("finder-content");
  const retry = document.getElementById("finder-retry");
  const search = document.getElementById("finder-search");
  const filters = document.getElementById("finder-filters");
  const columns = ["name", "subject", "topic", "type"];
  const labels = ["Name", "Subject", "Topic", "Question type"];

  // ASVS 1.2.1: display catalog text using DOM text, never interpolated HTML.
  function renderName(value, mode, row) {
    if (mode !== "display") return value;
    const link = document.createElement("a");
    link.textContent = value;
    link.href = row.url;
    return link;
  }

  function renderType(value, mode, row) {
    if (mode !== "display") return value;
    const wrapper = document.createElement("span");
    wrapper.className = "question-type-badges";
    const badge = document.createElement("abbr");
    badge.className = "question-type question-type-" + row.type_code.toLowerCase().replaceAll("_", "-");
    badge.title = row.type_description;
    badge.textContent = value;
    wrapper.append(badge);
    return wrapper;
  }

  function validateCatalog(rows) {
    const fields = ["id", "name", "subject", "topic", "type", "type_code", "type_description", "url"];
    if (!Array.isArray(rows)) throw new Error("Invalid catalog: expected rows");
    const identities = new Set();
    for (const row of rows) {
      if (!row || fields.some((field) => typeof row[field] !== "string")) {
        throw new Error("Invalid catalog row");
      }
      // Only generated, same-site topic routes may become links.
      if (!/^\.\.\/[a-z0-9_-]+\/[a-z0-9_-]+\/$/.test(row.url) || identities.has(row.id)) {
        throw new Error("Invalid catalog identity or topic route");
      }
      identities.add(row.id);
    }
    return rows;
  }

  function filterControl(index) {
    const control = index === 0
      ? { extend: "searchText" }
      : { extend: "searchList", search: true, select: true, ajaxOnly: false, orthogonal: "filter" };
    return [{
      extend: "dropdown", text: "Filter " + labels[index], icon: "search",
      dropdownClass: "finder-filter-" + columns[index], content: [control],
    }];
  }

  // ColumnControl exposes native dialogs and focus handling, but list inputs and
  // selection buttons need labels and announced state. Observe only this page.
  function accessibleFilters() {
    for (let index = 0; index < columns.length; index += 1) {
      const dialog = root.querySelector(".finder-filter-" + columns[index]);
      if (!dialog) continue;
      for (const input of dialog.querySelectorAll("input")) {
        const label = index === 0 ? "Filter Name" : "Search " + labels[index] + " options";
        if (input.getAttribute("aria-label") !== label) input.setAttribute("aria-label", label);
      }
      for (const select of dialog.querySelectorAll("select")) {
        select.setAttribute("aria-label", labels[index] + " match condition");
      }
      for (const button of dialog.querySelectorAll(".dtcc-list-buttons button")) {
        const pressed = String(button.classList.contains("dtcc-button_active"));
        if (button.getAttribute("aria-pressed") !== pressed) button.setAttribute("aria-pressed", pressed);
      }
    }
  }

  function setupTable(rows) {
    const table = new DataTable("#finder-table", {
      data: rows,
      columns: columns.map((name, index) => ({
        data: name, name, type: "string", columnControl: filterControl(index),
        render: index === 0 ? renderName : index === 3 ? renderType : DataTable.render.text(),
      })),
      order: [], pageLength: 50, lengthMenu: [25, 50, 100], deferRender: true,
      stateSave: true, stateDuration: -1,
      layout: { topStart: "pageLength", topEnd: "info", bottomStart: null, bottomEnd: "paging" },
      language: {
        lengthMenu: "Show _MENU_ question sets per page",
        info: "_TOTAL_ matching question sets; showing _START_ to _END_",
        infoFiltered: "(of _MAX_ total)", infoEmpty: "0 matching question sets",
        zeroRecords: "No question sets match. Clear filters or try a different search.",
        emptyTable: "No question sets are available yet.",
      },
    });

    // Scroll only the table. Counts, paging, and dropdowns stay in the visible
    // container rather than shifting offscreen with wide columns.
    const scroll = root.querySelector(".finder-scroll");
    scroll.replaceWith(table.table().container());
    table.table().node().before(scroll);
    scroll.append(table.table().node());

    function addFilter(text, remove) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = text + " \u00d7";
      button.setAttribute("aria-label", "Remove " + text + " filter");
      button.addEventListener("click", function () {
        remove();
        search.focus();
      });
      filters.append(button);
    }

    function refreshSummary() {
      filters.replaceChildren();
      search.value = table.search();
      if (table.search()) addFilter("Search: " + table.search(), () => table.search("").draw());
      const state = table.state();
      for (let index = 0; index < columns.length; index += 1) {
        const name = columns[index];
        const saved = state.columnControl[name];
        if (index === 0) {
          if (saved.searchInput.value) {
            addFilter("Name: " + saved.searchInput.value, function () {
              table.column(index).columnControl.searchClear();
              table.draw();
            });
          }
        } else {
          for (const value of saved.searchList || []) {
            addFilter(labels[index] + ": " + value, function () {
              const updated = table.state();
              updated.columnControl[name].searchList = saved.searchList.filter((item) => item !== value);
              updated.start = 0;
              table.state(updated).draw(false);
            });
          }
        }
      }
      accessibleFilters();
    }

    search.addEventListener("input", () => table.search(search.value).draw());
    document.getElementById("finder-clear").addEventListener("click", function () {
      table.search("").columns().search("");
      table.columns().columnControl.searchClear();
      table.draw();
      search.focus();
    });
    table.on("draw", refreshSummary);
    refreshSummary();
    const observer = new MutationObserver(accessibleFilters);
    observer.observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ["class"] });
  }

  async function load() {
    retry.hidden = true;
    status.textContent = "Loading question sets...";
    if (typeof DataTable === "undefined" || !DataTable.ColumnControl) {
      status.textContent = "The table controls could not load. Retry or browse the sitemap above.";
      retry.hidden = false;
      return;
    }
    // Catch at the page boundary so fetch, JSON, and initialization errors have a
    // useful fallback; never silently substitute an empty dataset.
    try {
      const response = await fetch(root.dataset.catalog);
      if (!response.ok) throw new Error("Catalog response " + response.status);
      const rows = validateCatalog(await response.json());
      content.hidden = false;
      setupTable(rows);
      status.hidden = true;
    } catch (error) {
      console.error("Question Finder initialization failed", error);
      content.hidden = true;
      status.textContent = "Question sets could not load. Retry or browse the sitemap above.";
      retry.hidden = false;
    }
  }

  retry.addEventListener("click", function () {
    if (typeof DataTable === "undefined" || !DataTable.ColumnControl || DataTable.isDataTable("#finder-table")) {
      window.location.reload();
    } else {
      load();
    }
  });
  load();
})();
