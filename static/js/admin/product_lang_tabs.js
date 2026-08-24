(function () {
  "use strict";

  function setLang(root, lang) {
    root.classList.remove("cms-lang-mode-uk", "cms-lang-mode-ru");
    root.classList.add("cms-lang-mode-" + lang);
    root.querySelectorAll("[data-cms-lang]").forEach(function (btn) {
      btn.classList.toggle(
        "is-active",
        btn.getAttribute("data-cms-lang") === lang
      );
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector("[data-product-lang-root]");
    if (!root) return;
    setLang(root, "uk");
    root.querySelectorAll("[data-cms-lang]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setLang(root, btn.getAttribute("data-cms-lang") || "uk");
      });
    });
  });
})();
