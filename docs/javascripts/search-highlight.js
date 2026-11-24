// After a search result is clicked, Material opens the page with the search
// term in the address (?h=term) and highlights its matches in yellow, but the
// search box on the new page is empty. This puts the term back in the box, so
// its clear button (x) can be used. Clearing the box, with the button or by
// deleting the text, removes the highlights and the term from the address.
function initSearchHighlight() {
  const input = document.querySelector(".md-search__input");
  if (!input) return;

  const term = new URL(window.location.href).searchParams.get("h");
  if (term && !input.value) input.value = term;

  function clearHighlights() {
    document.querySelectorAll("mark[data-md-highlight]").forEach((mark) => {
      const parent = mark.parentNode;
      mark.replaceWith(...mark.childNodes);
      parent.normalize();
    });
    const url = new URL(window.location.href);
    if (url.searchParams.has("h")) {
      url.searchParams.delete("h");
      history.replaceState(history.state, "", url.pathname + url.search + url.hash);
    }
  }

  if (input.form) input.form.addEventListener("reset", clearHighlights);
  input.addEventListener("input", () => {
    if (!input.value.trim()) clearHighlights();
  });
}

// document$ is Material's page-load observable. Fall back to DOMContentLoaded
// if it is not available.
if (typeof document$ !== "undefined") {
  document$.subscribe(initSearchHighlight);
} else {
  document.addEventListener("DOMContentLoaded", initSearchHighlight);
}
