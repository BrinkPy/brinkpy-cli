// Mark wide tables that have columns hidden to the left or right, so the CSS
// in extra.css can show a shadow on that edge. Material wraps every table in
// .md-typeset__scrollwrap, which is the element that scrolls sideways.
function updateScrollShadows(wrap) {
  const hiddenLeft = wrap.scrollLeft > 1;
  const hiddenRight = wrap.scrollLeft + wrap.clientWidth < wrap.scrollWidth - 1;
  wrap.classList.toggle("scroll-left", hiddenLeft);
  wrap.classList.toggle("scroll-right", hiddenRight);
}

function initScrollShadows() {
  const wraps = document.querySelectorAll(".md-typeset__scrollwrap");
  wraps.forEach((wrap) => {
    updateScrollShadows(wrap);
    wrap.addEventListener("scroll", () => updateScrollShadows(wrap), { passive: true });
  });
  window.addEventListener("resize", () => wraps.forEach(updateScrollShadows));
}

// document$ is Material's page-load observable, which also fires after instant
// navigation. Fall back to DOMContentLoaded if it is not available.
if (typeof document$ !== "undefined") {
  document$.subscribe(initScrollShadows);
} else {
  document.addEventListener("DOMContentLoaded", initScrollShadows);
}
