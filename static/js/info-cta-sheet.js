(function () {
  "use strict";

  var sheet = document.querySelector("[data-info-cta-sheet]");
  if (!sheet) return;

  var dismissBtn = sheet.querySelector("[data-info-cta-dismiss]");
  var reopenBtn = document.querySelector("[data-info-cta-reopen]");
  var mq = window.matchMedia("(max-width: 767px)");
  var storageKey = "info-cta-sheet-dismissed:" + location.pathname;

  function isMobile() {
    return mq.matches;
  }

  function setDismissed(dismissed) {
    sheet.classList.toggle("is-dismissed", dismissed);
    sheet.setAttribute("aria-hidden", dismissed ? "true" : "false");
    if (reopenBtn) {
      reopenBtn.hidden = !dismissed || !isMobile();
      reopenBtn.classList.toggle("is-visible", dismissed && isMobile());
    }
    try {
      if (dismissed) sessionStorage.setItem(storageKey, "1");
      else sessionStorage.removeItem(storageKey);
    } catch (err) {
      /* ignore */
    }
  }

  function sync() {
    if (!isMobile()) {
      sheet.classList.remove("is-dismissed");
      sheet.setAttribute("aria-hidden", "false");
      if (reopenBtn) {
        reopenBtn.hidden = true;
        reopenBtn.classList.remove("is-visible");
      }
      return;
    }
    var stored = false;
    try {
      stored = sessionStorage.getItem(storageKey) === "1";
    } catch (err) {
      stored = false;
    }
    setDismissed(stored);
  }

  if (dismissBtn) {
    dismissBtn.addEventListener("click", function () {
      if (!isMobile()) return;
      setDismissed(true);
    });
  }

  if (reopenBtn) {
    reopenBtn.addEventListener("click", function () {
      setDismissed(false);
    });
  }

  if (typeof mq.addEventListener === "function") {
    mq.addEventListener("change", sync);
  } else if (typeof mq.addListener === "function") {
    mq.addListener(sync);
  }

  sync();
})();
