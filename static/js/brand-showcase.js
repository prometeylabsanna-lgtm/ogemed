(() => {
  "use strict";

  const root = document.querySelector("[data-brand-showcase]");
  if (!root) return;

  const scrollEl = root.querySelector("[data-brand-scroll]");
  const stickyEl = root.querySelector(".brand-showcase__sticky");
  const panels = Array.prototype.slice.call(
    root.querySelectorAll("[data-brand-panel]")
  );
  const dots = Array.prototype.slice.call(
    root.querySelectorAll("[data-brand-dot]")
  );
  if (!scrollEl || !stickyEl || panels.length < 1) return;

  const reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;
  const count = panels.length;
  let activeIndex = 0;
  let ticking = false;

  root.style.setProperty("--brand-steps", String(Math.max(count, 1)));
  root.classList.add("is-morph");

  function clamp(v, min, max) {
    return Math.max(min, Math.min(max, v));
  }

  function smoothstep(t) {
    const x = clamp(t, 0, 1);
    return x * x * (3 - 2 * x);
  }

  function headerOffset() {
    const top = parseFloat(getComputedStyle(stickyEl).top);
    if (Number.isFinite(top)) return top;
    return (
      parseFloat(
        getComputedStyle(document.documentElement).getPropertyValue(
          "--header-height"
        )
      ) || 64
    );
  }

  function setActiveMeta(index) {
    if (index === activeIndex) return;
    activeIndex = index;
    panels.forEach((panel, i) => {
      panel.setAttribute("aria-hidden", i === index ? "false" : "true");
    });
    dots.forEach((dot, i) => {
      const on = i === index;
      dot.classList.toggle("is-active", on);
      dot.setAttribute("aria-selected", on ? "true" : "false");
    });
  }

  function paint(progress) {
    const pos = progress * Math.max(count - 1, 0);
    let best = 0;
    let bestW = -1;

    panels.forEach((panel, i) => {
      const dist = Math.abs(pos - i);
      let weight = 0;
      if (dist < 1) {
        weight = reduceMotion ? (dist < 0.5 ? 1 : 0) : smoothstep(1 - dist);
      }
      const visible = weight > 0.02;
      panel.classList.toggle("is-visible", visible);
      panel.style.opacity = visible ? weight.toFixed(4) : "0";
      panel.style.zIndex = String(visible ? Math.round(weight * 100) : 0);
      const scale = 0.94 + 0.06 * weight;
      panel.style.setProperty("--brand-media-scale", scale.toFixed(4));
      if (weight > bestW) {
        bestW = weight;
        best = i;
      }
    });

    setActiveMeta(best);
  }

  function readProgress() {
    const stickyTop = headerOffset();
    const rect = scrollEl.getBoundingClientRect();
    const range = Math.max(scrollEl.offsetHeight - stickyEl.offsetHeight, 1);
    const scrolled = clamp(stickyTop - rect.top, 0, range);
    return scrolled / range;
  }

  function update() {
    paint(readProgress());
    ticking = false;
  }

  function requestUpdate() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  }

  function scrollToIndex(index) {
    const i = clamp(index, 0, count - 1);
    const rect = scrollEl.getBoundingClientRect();
    const pageY = window.pageYOffset || document.documentElement.scrollTop;
    const top = rect.top + pageY;
    const stickyTop = headerOffset();
    const range = Math.max(scrollEl.offsetHeight - stickyEl.offsetHeight, 1);
    const target =
      top - stickyTop + (count <= 1 ? 0 : (i / (count - 1)) * range);
    window.scrollTo({
      top: target,
      behavior: reduceMotion ? "auto" : "smooth",
    });
  }

  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      const i = Number(dot.getAttribute("data-brand-dot"));
      if (Number.isFinite(i)) scrollToIndex(i);
    });
  });

  window.addEventListener("scroll", requestUpdate, { passive: true });
  window.addEventListener("resize", requestUpdate, { passive: true });
  update();
})();
