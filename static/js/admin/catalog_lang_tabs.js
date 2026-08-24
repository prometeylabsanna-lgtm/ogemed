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
    applyDefaultLocks(root, lang);
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

  function wrapSharedFields(root) {
    root.querySelectorAll("fieldset.product-shared-fields").forEach(function (fs) {
      if (fs.closest(".inline-group")) return;
      fs.querySelectorAll(
        "input:not([type=hidden]):not([type=file]):not([data-default-lock]), select, textarea"
      ).forEach(function (input) {
        if (input.closest("[data-default-wrap]")) return;
        if (input.closest(".inline-group")) return;
        var row =
          input.closest(".form-row") ||
          input.closest("[class*='field-']") ||
          input.parentElement;
        if (!row || row.getAttribute("data-default-wrap")) return;

        var wrap = document.createElement("label");
        wrap.className = "product-default-lock";
        wrap.setAttribute("data-default-wrap", "1");
        var cb = document.createElement("input");
        cb.type = "checkbox";
        cb.checked = true;
        cb.className = "product-default-lock__cb";
        cb.setAttribute("data-default-lock", "1");
        var text = document.createElement("span");
        text.textContent = "Дефолтне значення";
        wrap.appendChild(cb);
        wrap.appendChild(text);

        var anchor =
          row.querySelector("label") ||
          row.querySelector(".flex") ||
          row.firstElementChild;
        if (anchor && anchor.parentNode) {
          anchor.parentNode.insertBefore(wrap, anchor.nextSibling);
        } else {
          row.appendChild(wrap);
        }

        cb.addEventListener("change", function () {
          var lang = root.classList.contains("cms-lang-mode-ru") ? "ru" : "uk";
          applyDefaultLocks(root, lang);
        });
      });
    });
  }

  function controlsInSharedFieldsets(root) {
    var list = [];
    root.querySelectorAll("fieldset.product-shared-fields").forEach(function (fs) {
      if (fs.closest(".inline-group")) return;
      fs.querySelectorAll(
        "input:not([type=hidden]):not([data-default-lock]), select, textarea"
      ).forEach(function (el) {
        if (el.type === "file") return;
        if (el.classList.contains("product-default-lock__cb")) return;
        if (el.closest(".inline-group")) return;
        list.push(el);
      });
    });
    return list;
  }

  function applyDefaultLocks(root, lang) {
    var lockRu = lang === "ru";
    controlsInSharedFieldsets(root).forEach(function (el) {
      var row =
        el.closest(".form-row") ||
        el.closest("[class*='field-']") ||
        el.parentElement;
      var cb = row ? row.querySelector("[data-default-lock]") : null;
      var useDefault = !cb || cb.checked;
      var disable = lockRu && useDefault;
      el.disabled = disable;
      el.readOnly = disable;
      if (disable) {
        el.setAttribute("data-locked-by-default", "1");
      } else {
        el.removeAttribute("data-locked-by-default");
      }
    });
  }

  function markI18nRows(root) {
    // Лише основна форма — не чіпаємо tabular inline (Значення атрибутів тощо)
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

  function unlockOnSubmit(root) {
    var form = root.closest("form");
    if (!form || form.getAttribute("data-i18n-unlock-bound")) return;
    form.setAttribute("data-i18n-unlock-bound", "1");
    form.addEventListener("submit", function () {
      controlsInSharedFieldsets(root).forEach(function (el) {
        el.disabled = false;
        el.readOnly = false;
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector("[data-catalog-lang-root]");
    if (!root) return;
    markI18nRows(root);
    wrapSharedFields(root);
    unlockOnSubmit(root);
    setLang(root, "uk");
    root.querySelectorAll("[data-cms-lang]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setLang(root, btn.getAttribute("data-cms-lang") || "uk");
      });
    });
  });
})();
