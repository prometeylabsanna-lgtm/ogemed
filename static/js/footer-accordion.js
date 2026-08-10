(function () {
  "use strict";

  var root = document.querySelector("[data-footer-acc]");
  if (!root) return;

  var toggles = root.querySelectorAll("[data-footer-acc-toggle]");
  var panel = root.querySelector("[data-footer-acc-panel]");
  if (!toggles.length || !panel) return;

  function setOpen(open) {
    root.classList.toggle("is-open", open);
    toggles.forEach(function (toggle) {
      toggle.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  toggles.forEach(function (toggle) {
    toggle.addEventListener("click", function () {
      setOpen(!root.classList.contains("is-open"));
    });
  });

  setOpen(false);
})();
