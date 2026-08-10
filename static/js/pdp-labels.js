/* Підписи міток товару показуються як підказка: hover/фокус на десктопі,
   тап або затискання на тач-екранах. Делегування — переживає htmx-свопи. */
(() => {
  const LONG_PRESS_MS = 400;

  let openItem = null;
  let holdTimer = null;
  let openedByHold = false;

  const setState = (item, isOpen) => {
    item.classList.toggle("is-open", isOpen);
    const trigger = item.querySelector(".pdp-label__trigger");
    if (trigger) trigger.setAttribute("aria-expanded", isOpen ? "true" : "false");
  };

  const close = () => {
    if (!openItem) return;
    setState(openItem, false);
    openItem = null;
  };

  const open = (item) => {
    if (openItem === item) return;
    close();
    setState(item, true);
    openItem = item;
  };

  const clearHold = () => {
    if (holdTimer === null) return;
    clearTimeout(holdTimer);
    holdTimer = null;
  };

  const itemFrom = (target) => {
    const trigger = target.closest?.(".pdp-label__trigger");
    return trigger ? trigger.closest(".pdp-label") : null;
  };

  document.addEventListener("pointerdown", (event) => {
    const item = itemFrom(event.target);
    if (!item) {
      close();
      return;
    }
    if (event.pointerType === "mouse") return;
    openedByHold = false;
    holdTimer = window.setTimeout(() => {
      holdTimer = null;
      openedByHold = true;
      open(item);
    }, LONG_PRESS_MS);
  });

  document.addEventListener("pointerup", clearHold);
  document.addEventListener("pointercancel", clearHold);

  document.addEventListener("click", (event) => {
    const item = itemFrom(event.target);
    if (!item) return;
    // тап, що вже відкрив підказку затисканням, не має її одразу згортати
    if (openedByHold) {
      openedByHold = false;
      return;
    }
    if (openItem === item) close();
    else open(item);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close();
  });

  window.addEventListener("scroll", close, { passive: true });
})();
