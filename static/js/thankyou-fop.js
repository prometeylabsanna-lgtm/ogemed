(() => {
  const root = document.querySelector("[data-fop-requisites]");
  if (!root) return;

  const btn = root.querySelector("[data-fop-copy]");
  const src = root.querySelector(".fop-req__src");
  if (!btn || !src) return;

  const original = btn.textContent;
  const copied = btn.getAttribute("data-copied-label") || "Скопійовано";

  const fallbackCopy = (text) => {
    src.hidden = false;
    src.focus();
    src.select();
    src.setSelectionRange(0, text.length);
    let ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (_err) {
      ok = false;
    }
    src.hidden = true;
    return ok;
  };

  btn.addEventListener("click", async () => {
    const text = src.value || "";
    let ok = false;
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        ok = true;
      } catch (_err) {
        ok = fallbackCopy(text);
      }
    } else {
      ok = fallbackCopy(text);
    }
    if (!ok) return;
    btn.textContent = copied;
    window.setTimeout(() => {
      btn.textContent = original;
    }, 2000);
  });
})();
