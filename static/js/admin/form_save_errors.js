(function () {
  "use strict";

  if (window.__ogemedAdminFormErrors) return;
  window.__ogemedAdminFormErrors = true;

  var BANNER_ID = "ogemed-admin-error-banner";

  function fieldLabel(el) {
    if (!el) return "Поле";
    var fromData = el.getAttribute("data-field-label");
    if (fromData) return fromData;
    var id = el.getAttribute("id");
    if (id) {
      var lab = document.querySelector('label[for="' + id + '"]');
      if (lab) {
        var t = (lab.textContent || "").replace(/\s+/g, " ").trim();
        if (t) return t;
      }
    }
    var wrap = el.closest(".form-row, .field-box, .flex, .cms-field-wrap, td, .hero-slides-admin__fields");
    if (wrap) {
      var lbl = wrap.querySelector("label");
      if (lbl) {
        var text = (lbl.textContent || "").replace(/\s+/g, " ").trim();
        if (text) return text;
      }
    }
    return el.getAttribute("name") || "Поле";
  }

  function unique(list) {
    var seen = {};
    var out = [];
    list.forEach(function (item) {
      if (!item || seen[item]) return;
      seen[item] = true;
      out.push(item);
    });
    return out;
  }

  function collectServerErrors(root) {
    var labels = [];
    // Не чіпати .text-red-* — у Unfold так стилізовані зірочки required (*)
    root.querySelectorAll(".errorlist, ul.errorlist").forEach(function (list) {
      var host =
        list.closest(".form-row, .field-box, .flex, .cms-field-wrap, td, [class*='field-']") ||
        list.parentElement;
      if (!host) return;
      var lab = host.querySelector("label");
      if (lab) {
        var t = (lab.textContent || "").replace(/\s+/g, " ").trim();
        if (t) labels.push(t);
      }
      list.querySelectorAll("li").forEach(function (li) {
        var msg = (li.textContent || "").trim();
        if (msg) labels.push(msg);
      });
    });
    root.querySelectorAll(".is-invalid").forEach(function (row) {
      var lab = row.querySelector("label");
      if (lab) {
        var t = (lab.textContent || "").replace(/\s+/g, " ").trim();
        if (t) labels.push(t);
      }
    });
    return unique(labels);
  }

  function isEffectivelyHidden(el) {
    if (!el || el.disabled || el.type === "hidden") return true;
    if (el.getAttribute("aria-hidden") === "true") return true;
    if (el.closest("[hidden], .cms-lang-ru, .cms-lang-uk")) {
      var modeRoot = el.closest(".cms-lang-mode-uk, .cms-lang-mode-ru, .product-admin-editor, .site-content-editor");
      if (modeRoot) {
        var isRu = el.closest(".cms-lang-ru");
        var isUk = el.closest(".cms-lang-uk");
        if (modeRoot.classList.contains("cms-lang-mode-uk") && isRu) return true;
        if (modeRoot.classList.contains("cms-lang-mode-ru") && isUk) return true;
      }
    }
    var style = window.getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden") return true;
    var parent = el.closest(".cms-lang-ru, .cms-lang-uk");
    if (parent) {
      var ps = window.getComputedStyle(parent);
      if (ps.display === "none" || ps.visibility === "hidden") return true;
    }
    return false;
  }

  function collectSoftLimitIssues(form) {
    var issues = [];
    form.querySelectorAll("[data-recommend-max]").forEach(function (el) {
      if (isEffectivelyHidden(el)) return;
      var max = parseInt(el.getAttribute("data-recommend-max") || "0", 10);
      if (!max) return;
      var value = (el.value || "").trim();
      if (value.length <= max) return;
      issues.push(
        fieldLabel(el) +
          " — " +
          value.length +
          " символів (рекомендовано до " +
          max +
          ")"
      );
    });
    return issues;
  }

  function collectInvalidFields(form) {
    var issues = [];
    if (typeof form.checkValidity !== "function") return issues;
    var controls = form.querySelectorAll("input, select, textarea");
    controls.forEach(function (el) {
      if (isEffectivelyHidden(el) || el.type === "submit") return;
      if (typeof el.checkValidity === "function" && !el.checkValidity()) {
        issues.push(fieldLabel(el));
      }
    });
    return unique(issues);
  }

  function removeBanner() {
    var old = document.getElementById(BANNER_ID);
    if (old) old.remove();
  }

  function showBanner(title, items, form) {
    removeBanner();
    var banner = document.createElement("div");
    banner.id = BANNER_ID;
    banner.className = "ogemed-admin-error-banner";
    banner.setAttribute("role", "alert");

    var head = document.createElement("p");
    head.className = "ogemed-admin-error-banner__title";
    head.textContent = title;
    banner.appendChild(head);

    if (items.length) {
      var ul = document.createElement("ul");
      ul.className = "ogemed-admin-error-banner__list";
      items.slice(0, 12).forEach(function (item) {
        var li = document.createElement("li");
        li.textContent = item;
        ul.appendChild(li);
      });
      banner.appendChild(ul);
    }

    var hint = document.createElement("p");
    hint.className = "ogemed-admin-error-banner__hint";
    hint.textContent =
      "Прокрутіть до червоних підказок біля полів або виправте пункти вище, потім збережіть знову.";
    banner.appendChild(hint);

    var mount =
      (form && form.querySelector(".ogemed-admin-error-mount")) ||
      (form && form.parentElement) ||
      document.querySelector("#content-main") ||
      document.querySelector("#content") ||
      document.body;
    if (form && form.parentElement === mount) {
      mount.insertBefore(banner, form);
    } else if (form) {
      form.insertBefore(banner, form.firstChild);
    } else {
      mount.insertBefore(banner, mount.firstChild);
    }

    try {
      banner.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      banner.scrollIntoView(true);
    }
  }

  function scrollToFirstError(root) {
    var first =
      root.querySelector(".errorlist, ul.errorlist, .is-invalid, .ogemed-admin-error-banner") ||
      root.querySelector(":invalid");
    if (!first) return;
    try {
      first.scrollIntoView({ behavior: "smooth", block: "center" });
    } catch (err) {
      first.scrollIntoView(true);
    }
  }

  function onPageErrors() {
    var forms = document.querySelectorAll(
      "form[method='post'], form[data-cms-content-form], #product_form, #changelist-form"
    );
    forms.forEach(function (form) {
      var errors = collectServerErrors(form);
      if (!errors.length) {
        // Unfold інколи кладе errornote поза формою
        var note = document.querySelector(".errornote, [data-errornote]");
        if (!note) return;
        errors = [(note.textContent || "").replace(/\s+/g, " ").trim()].filter(Boolean);
      }
      if (!errors.length) return;
      showBanner("Не збережено — є помилки", errors, form);
      scrollToFirstError(form);
    });
  }

  document.addEventListener(
    "submit",
    function (event) {
      var form = event.target;
      if (!form || form.tagName !== "FORM") return;
      if (form.method && form.method.toLowerCase() !== "post") return;
      if (form.dataset.errorWarnOk === "1") {
        delete form.dataset.errorWarnOk;
        return;
      }

      var invalid = collectInvalidFields(form);
      var soft = collectSoftLimitIssues(form);
      if (!invalid.length && !soft.length) return;

      event.preventDefault();
      event.stopPropagation();

      var items = invalid
        .map(function (l) {
          return l + " — обовʼязкове або некоректне";
        })
        .concat(soft);

      showBanner("Перед збереженням перевірте поля", items, form);

      var firstInvalid = form.querySelector(":invalid, [data-recommend-max]");
      if (soft.length) {
        form.querySelectorAll("[data-recommend-max]").forEach(function (el) {
          var max = parseInt(el.getAttribute("data-recommend-max") || "0", 10);
          if (max && (el.value || "").trim().length > max) {
            firstInvalid = el;
          }
        });
      }
      if (firstInvalid) {
        try {
          firstInvalid.focus({ preventScroll: true });
        } catch (err) {
          try {
            firstInvalid.focus();
          } catch (e2) {}
        }
        try {
          firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
        } catch (err) {
          firstInvalid.scrollIntoView(true);
        }
      }

      if (!invalid.length && soft.length) {
        var ok = window.confirm(
          "Деякі тексти довші за рекомендовані для верстки:\n\n• " +
            soft.slice(0, 6).join("\n• ") +
            "\n\nЗберегти все одно?"
        );
        if (!ok) return;
        form.dataset.errorWarnOk = "1";
        window.setTimeout(function () {
          if (typeof form.requestSubmit === "function") {
            try {
              form.requestSubmit();
              return;
            } catch (err) {
              form.submit();
            }
          } else {
            form.submit();
          }
        }, 0);
      }
    },
    true
  );

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onPageErrors);
  } else {
    onPageErrors();
  }
})();
