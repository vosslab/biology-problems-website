/* Progressive decoration of ordinary HTML labels, shared by static pages and Finder. */
(function () {
  "use strict";

  const observed = new WeakSet();
  const outlines = new ResizeObserver(function (entries) {
    for (const { target: badge } of entries) {
      const svg = badge.querySelector(".bloom-outline");
      const path = svg.firstElementChild;
      const { width, height } = svg.getBoundingClientRect();
      // Closed scale guides and detached Finder rows are measured when shown.
      if (!width || !height) continue;
      const style = getComputedStyle(badge);
      const chevron = parseFloat(style.getPropertyValue("--bloom-chevron-depth")) * parseFloat(style.fontSize);
      const inset = parseFloat(getComputedStyle(path).strokeWidth) / 2;
      const points = badge.classList.contains("bloom-cognitive")
        ? [[inset, inset], [width - chevron, inset], [width - inset, height / 2],
          [width - chevron, height - inset], [inset, height - inset]]
        : [[inset, inset], [width - inset, inset], [width - inset, height - inset],
          [inset, height - inset], [chevron, height / 2]];
      svg.setAttribute("viewBox", "0 0 " + width + " " + height);
      path.setAttribute("d", "M" + points.map(point => point.join(",")).join(" L") + " Z");
    }
  });

  function enhance(root) {
    for (const badge of root.querySelectorAll(".bloom-badge")) {
      if (observed.has(badge)) continue;
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.classList.add("bloom-outline");
      svg.setAttribute("aria-hidden", "true");
      svg.setAttribute("focusable", "false");
      svg.append(document.createElementNS(svg.namespaceURI, "path"));
      badge.prepend(svg);
      observed.add(badge);
      outlines.observe(badge);
    }
  }

  window.BloomDisplay = { enhance };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => enhance(document), { once: true });
  } else {
    enhance(document);
  }
})();
