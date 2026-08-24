(function () {
  "use strict";

  var I18N_UK = [
    "name_uk",
    "short_description_uk",
    "description_uk",
    "tagline_uk",
    "seo_title_uk",
    "seo_description_uk",
    "title_uk",
  ];
  var I18N_RU = [
    "name_ru",
    "short_description_ru",
    "description_ru",
    "tagline_ru",
    "seo_title_ru",
    "seo_description_ru",
    "title_ru",
  ];

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

  function i18nScope(root) {
    return root.querySelector("fieldset.product-i18n-fields") || root;
  }

  function fieldRow(scope, name) {
    return (
      scope.querySelector(".field-" + name) ||
      scope.querySelector("[class*='field-" + name + "']")
    );
  }

  function markI18nRows(root) {
    var scope = i18nScope(root);
    I18N_UK.forEach(function (name) {
      var row = fieldRow(scope, name);
      if (row && !row.closest(".inline-group")) {
        row.classList.add("cms-lang-uk");
      }
    });
    I18N_RU.forEach(function (name) {
      var row = fieldRow(scope, name);
      if (row && !row.closest(".inline-group")) {
        row.classList.add("cms-lang-ru");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector(
      "[data-catalog-lang-root], [data-product-lang-root], [data-i18n-lang-root]"
    );
    if (!root) return;
    markI18nRows(root);
    setLang(root, "uk");
    root.querySelectorAll("[data-cms-lang]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setLang(root, btn.getAttribute("data-cms-lang") || "uk");
      });
    });
  });
})();
