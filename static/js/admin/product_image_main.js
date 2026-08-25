(function () {
  "use strict";

  // Синхронно з apps.catalog.forms.MIN_IMAGE_SIDE
  var MIN_IMAGE_SIDE = 1600;
  var WARN_CLASS = "product-image-size-warn";

  function isMainInput(el) {
    if (!el || el.type !== "checkbox") return false;
    var name = el.getAttribute("name") || "";
    return name === "is_main" || /-is_main$/.test(name);
  }

  function isProductImageFileInput(el) {
    if (!el || el.type !== "file") return false;
    var name = el.getAttribute("name") || "";
    return name === "image" || /-image$/.test(name);
  }

  function warnHost(input) {
    var cell = input.closest("td, .form-row, .field-image, .flex") || input.parentElement;
    if (!cell) return null;
    var existing = cell.querySelector("." + WARN_CLASS);
    if (existing) return existing;
    var el = document.createElement("p");
    el.className = WARN_CLASS;
    el.setAttribute("role", "status");
    cell.appendChild(el);
    return el;
  }

  function clearWarn(input) {
    var cell = input.closest("td, .form-row, .field-image, .flex") || input.parentElement;
    if (!cell) return;
    var existing = cell.querySelector("." + WARN_CLASS);
    if (existing) existing.remove();
  }

  function setWarn(input, width, height) {
    var host = warnHost(input);
    if (!host) return;
    host.textContent =
      "Рекомендовано від " +
      MIN_IMAGE_SIDE +
      "px по довгій стороні (зараз " +
      width +
      "×" +
      height +
      "px), інакше збільшення на сторінці товару буде розмитим. Можна зберегти й так.";
  }

  function readDimensions(file) {
    return new Promise(function (resolve, reject) {
      if (!file || !file.type || file.type.indexOf("image/") !== 0) {
        reject(new Error("not-image"));
        return;
      }
      var url = URL.createObjectURL(file);
      var img = new Image();
      img.onload = function () {
        var size = { width: img.naturalWidth, height: img.naturalHeight };
        URL.revokeObjectURL(url);
        resolve(size);
      };
      img.onerror = function () {
        URL.revokeObjectURL(url);
        reject(new Error("decode"));
      };
      img.src = url;
    });
  }

  function checkInput(input) {
    var file = input.files && input.files[0];
    if (!file) {
      clearWarn(input);
      return Promise.resolve(null);
    }
    return readDimensions(file).then(function (size) {
      if (Math.max(size.width, size.height) < MIN_IMAGE_SIDE) {
        setWarn(input, size.width, size.height);
        return size;
      }
      clearWarn(input);
      return null;
    }).catch(function () {
      clearWarn(input);
      return null;
    });
  }

  function collectSmallUploads(form) {
    var inputs = Array.prototype.slice.call(
      form.querySelectorAll('input[type="file"]')
    ).filter(isProductImageFileInput);
    return Promise.all(inputs.map(checkInput)).then(function (results) {
      return results.filter(Boolean);
    });
  }

  document.addEventListener(
    "change",
    function (event) {
      var target = event.target;
      if (isMainInput(target) && target.checked) {
        var form = target.closest("form") || document;
        form.querySelectorAll('input[type="checkbox"]').forEach(function (el) {
          if (el === target || !isMainInput(el) || !el.checked) return;
          el.checked = false;
          el.dispatchEvent(new Event("input", { bubbles: true }));
        });
        return;
      }
      if (isProductImageFileInput(target)) {
        checkInput(target);
      }
    },
    true
  );

  document.addEventListener(
    "submit",
    function (event) {
      var form = event.target;
      if (!form || form.tagName !== "FORM") return;
      if (form.dataset.imageSizeWarnOk === "1") {
        delete form.dataset.imageSizeWarnOk;
        return;
      }
      if (!form.querySelector('input[type="file"]')) return;

      var hasNew = Array.prototype.some.call(
        form.querySelectorAll('input[type="file"]'),
        function (input) {
          return isProductImageFileInput(input) && input.files && input.files.length;
        }
      );
      if (!hasNew) return;

      event.preventDefault();
      event.stopPropagation();

      collectSmallUploads(form).then(function (small) {
        if (small.length) {
          var first = small[0];
          var ok = window.confirm(
            "Рекомендовано зображення від " +
              MIN_IMAGE_SIDE +
              "px по довгій стороні (зараз " +
              first.width +
              "×" +
              first.height +
              "px), інакше збільшення на сторінці товару буде розмитим.\n\n" +
              "Зберегти все одно?"
          );
          if (!ok) return;
        }
        form.dataset.imageSizeWarnOk = "1";
        if (typeof form.requestSubmit === "function") {
          form.requestSubmit();
        } else {
          form.submit();
        }
      });
    },
    true
  );
})();
