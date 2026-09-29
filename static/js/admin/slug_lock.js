(function () {
  "use strict";

  function sync(input, unlock) {
    if (!input || !unlock) return;
    var allow = !!unlock.checked;
    if (allow) {
      input.removeAttribute("readonly");
      input.classList.remove("is-slug-locked");
    } else {
      input.setAttribute("readonly", "readonly");
      input.classList.add("is-slug-locked");
    }
  }

  function bind(root) {
    var input = root.querySelector("[data-slug-lock-input]");
    if (!input) return;
    var unlock =
      root.querySelector('input[name="slug_unlock"]') ||
      document.querySelector('input[name="slug_unlock"]');
    if (!unlock) {
      // поле поруч у тому ж fieldset
      var wrap = input.closest(".form-row, .field-box, [class*='field-slug']");
      var section = wrap && wrap.parentElement;
      if (section) {
        unlock = section.querySelector('input[name="slug_unlock"]');
      }
    }
    if (!unlock) return;
    sync(input, unlock);
    unlock.addEventListener("change", function () {
      sync(input, unlock);
    });
  }

  function init() {
    document.querySelectorAll("[data-slug-lock-input]").forEach(function (input) {
      var root =
        input.closest("fieldset, .site-content-fieldset, form") || document;
      bind(root);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
