(function () {
  "use strict";

  var modal = document.querySelector("[data-value-modal]");
  if (!modal) return;

  var panel = modal.querySelector(".about-value-modal__panel");
  var titleEl = modal.querySelector("[data-value-modal-title]");
  var textEl = modal.querySelector("[data-value-modal-text]");
  var triggers = document.querySelectorAll("[data-value-trigger]");
  var lastFocus = null;

  function coverSize(markRect) {
    // Компактне коло навколо іконки (не всієї кнопки з підписом)
    var base = Math.max(markRect.width, markRect.height);
    var size = Math.ceil(base * 1.42);
    var maxSize = Math.min(window.innerWidth - 24, window.innerHeight - 24, 168);
    var minSize = 120;
    return Math.max(minSize, Math.min(size, maxSize));
  }

  function positionPanel(trigger) {
    if (!panel || !trigger) return;
    var mark = trigger.querySelector(".about-value__mark");
    var markRect = (mark || trigger).getBoundingClientRect();
    var size = coverSize(markRect);
    panel.style.width = size + "px";
    panel.style.height = size + "px";
    panel.style.maxHeight = size + "px";

    var cx = markRect.left + markRect.width / 2;
    var cy = markRect.top + markRect.height / 2;
    var pad = 10;
    var left = cx - size / 2;
    var top = cy - size / 2;
    left = Math.max(pad, Math.min(left, window.innerWidth - size - pad));
    top = Math.max(pad, Math.min(top, window.innerHeight - size - pad));

    panel.style.left = Math.round(left) + "px";
    panel.style.top = Math.round(top) + "px";
  }

  function openModal(trigger) {
    var title = trigger.getAttribute("data-value-title") || "";
    var text = trigger.getAttribute("data-value-text") || "";
    if (!title && !text) return;

    lastFocus = trigger;
    if (titleEl) titleEl.textContent = title;
    if (textEl) {
      textEl.textContent = text;
      textEl.hidden = !text;
    }
    modal.hidden = false;
    document.documentElement.classList.add("is-value-modal-open");
    positionPanel(trigger);
    window.requestAnimationFrame(function () {
      positionPanel(trigger);
    });
    var closeBtn = modal.querySelector(".about-value-modal__close");
    if (closeBtn) closeBtn.focus();
  }

  function closeModal() {
    if (modal.hidden) return;
    modal.hidden = true;
    document.documentElement.classList.remove("is-value-modal-open");
    if (panel) {
      panel.style.left = "";
      panel.style.top = "";
      panel.style.width = "";
      panel.style.height = "";
      panel.style.maxHeight = "";
    }
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
    lastFocus = null;
  }

  triggers.forEach(function (btn) {
    btn.addEventListener("click", function () {
      openModal(btn);
    });
  });

  modal.querySelectorAll("[data-value-close]").forEach(function (el) {
    el.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !modal.hidden) {
      event.preventDefault();
      closeModal();
    }
  });

  window.addEventListener(
    "resize",
    function () {
      if (!modal.hidden && lastFocus) positionPanel(lastFocus);
    },
    { passive: true }
  );

  window.addEventListener(
    "scroll",
    function () {
      if (!modal.hidden && lastFocus) positionPanel(lastFocus);
    },
    { passive: true, capture: true }
  );
})();
