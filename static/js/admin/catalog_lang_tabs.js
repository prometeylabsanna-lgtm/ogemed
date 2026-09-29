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

  function markI18nRows(root) {
    root.querySelectorAll("[class*='field-']").forEach(function (row) {
      var match = String(row.className).match(/(?:^|\s)field-([\w-]+?)_(uk|ru)(?:\s|$)/);
      if (!match) return;
      row.classList.add("cms-lang-" + match[2]);
    });
  }

  function ensureLangSwitch(root) {
    if (root.querySelector("[data-cms-lang-switch]")) return;
    var bar = document.createElement("div");
    bar.className =
      "product-admin-editor__langbar product-admin-editor__langbar--inline";
    bar.setAttribute("data-cms-lang-switch", "");
    bar.setAttribute("role", "group");
    bar.setAttribute("aria-label", "Мова контенту");
    bar.innerHTML =
      '<button type="button" class="cms-lang-switch__btn is-active" data-cms-lang="uk">UA</button>' +
      '<button type="button" class="cms-lang-switch__btn" data-cms-lang="ru">RU</button>' +
      '<p class="product-admin-editor__langhint">' +
      "Перемикач показує текстові поля українською або російською." +
      "</p>";
    root.insertBefore(bar, root.firstChild);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector(
      "[data-catalog-lang-root], [data-product-lang-root], [data-i18n-lang-root], .product-admin-editor, .site-content-editor"
    );
    if (!root) return;
    ensureLangSwitch(root);
    markI18nRows(root);
    setLang(root, "uk");
    root.querySelectorAll("[data-cms-lang]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setLang(root, btn.getAttribute("data-cms-lang") || "uk");
      });
    });
  });
})();
