(function () {
  "use strict";

  function nextFormIndex(totalInput) {
    var n = parseInt(totalInput.value || "0", 10);
    if (isNaN(n) || n < 0) n = 0;
    totalInput.value = String(n + 1);
    return n;
  }

  function cloneEmpty(template, index) {
    var html = template.innerHTML.replace(/__prefix__/g, String(index));
    var wrap = document.createElement("div");
    wrap.innerHTML = html.trim();
    return wrap.firstElementChild;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector("[data-legal-sections]");
    if (!root) return;
    var list = root.querySelector("[data-legal-sections-list]");
    var template = root.querySelector("[data-legal-sections-empty]");
    var addBtn = root.querySelector("[data-legal-sections-add]");
    var total = root.querySelector('input[name$="-TOTAL_FORMS"]');
    if (!list || !template || !addBtn || !total) return;

    addBtn.addEventListener("click", function () {
      var idx = nextFormIndex(total);
      var row = cloneEmpty(template, idx);
      if (!row) return;
      list.appendChild(row);
    });
  });
})();
