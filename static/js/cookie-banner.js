(function () {
  "use strict";

  var KEY = "ogemed_cookie_consent";
  var YEAR_MS = 365 * 24 * 60 * 60 * 1000;
  var banner = document.querySelector("[data-cookie-banner]");
  if (!banner) return;

  function readConsent() {
    try {
      var raw = window.localStorage.getItem(KEY);
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (!data || data.v !== 1 || !data.ts) return null;
      if (Date.now() - Number(data.ts) > YEAR_MS) return null;
      return data;
    } catch (err) {
      return null;
    }
  }

  function saveConsent() {
    try {
      window.localStorage.setItem(
        KEY,
        JSON.stringify({ v: 1, ts: Date.now(), accepted: true })
      );
    } catch (err) {
      /* ignore quota / private mode */
    }
  }

  function hide() {
    banner.hidden = true;
    document.documentElement.classList.remove("has-cookie-banner");
  }

  function show() {
    banner.hidden = false;
    document.documentElement.classList.add("has-cookie-banner");
  }

  if (readConsent()) {
    hide();
    return;
  }

  show();

  var acceptBtn = banner.querySelector("[data-cookie-accept]");
  if (acceptBtn) {
    acceptBtn.addEventListener("click", function () {
      saveConsent();
      hide();
    });
  }
})();
