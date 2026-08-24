(function () {
  "use strict";

  function isMainInput(el) {
    if (!el || el.type !== "checkbox") return false;
    var name = el.getAttribute("name") || "";
    return name === "is_main" || /-is_main$/.test(name);
  }

  document.addEventListener(
    "change",
    function (event) {
      var target = event.target;
      if (!isMainInput(target) || !target.checked) return;
      var form = target.closest("form") || document;
      form.querySelectorAll('input[type="checkbox"]').forEach(function (el) {
        if (el === target || !isMainInput(el) || !el.checked) return;
        el.checked = false;
        el.dispatchEvent(new Event("input", { bubbles: true }));
      });
    },
    true
  );
})();
