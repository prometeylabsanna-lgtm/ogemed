/* Збільшення фото товару: лупа в межах колонки на десктопі
   і повноекранний перегляд із пінчем на тач-екранах. */
(() => {
  const HOVER_SCALE = 2.2;
  const MAX_SCALE = 4;
  const TAP_SCALE = 2.5;
  const SWIPE_MIN = 60;
  const DOUBLE_TAP_MS = 350;

  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

  // Вище 1:1 пікселів файлу збільшувати нема сенсу — буде лише розмите мило
  const nativeLimit = (img, ceiling) => {
    const shown = img.offsetWidth || img.clientWidth;
    if (!img.naturalWidth || !shown) return ceiling;
    return clamp(img.naturalWidth / shown, 1.4, ceiling);
  };

  /* ---------- лупа в рамці галереї ---------- */

  const initHoverZoom = (stage) => {
    if (!stage || stage.dataset.hoverZoom === "1") return;
    stage.dataset.hoverZoom = "1";

    const track = (event) => {
      if (!finePointer.matches || event.pointerType === "touch") return;
      const rect = stage.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * 100;
      const y = ((event.clientY - rect.top) / rect.height) * 100;
      stage.style.setProperty("--zoom-x", `${clamp(x, 0, 100)}%`);
      stage.style.setProperty("--zoom-y", `${clamp(y, 0, 100)}%`);
    };

    const stop = () => {
      stage.classList.remove("is-zoomed");
      stage.style.removeProperty("--zoom-x");
      stage.style.removeProperty("--zoom-y");
    };

    stage.addEventListener("pointerenter", (event) => {
      if (!finePointer.matches || event.pointerType === "touch") return;
      const img = stage.querySelector(".pdp-gallery__slide.is-active img");
      if (img) stage.style.setProperty("--zoom-scale", nativeLimit(img, HOVER_SCALE));
      track(event);
      stage.classList.add("is-zoomed");
    });
    stage.addEventListener("pointermove", track);
    stage.addEventListener("pointerleave", stop);
    stage.addEventListener("pointercancel", stop);
  };

  /* ---------- повноекранний перегляд ---------- */

  let viewer = null;
  const view = { images: [], index: 0, scale: 1, x: 0, y: 0, origin: null, trigger: null };
  const pointers = new Map();
  let pinch = null;
  let drag = null;
  let lastTap = 0;
  let scrollLock = "";

  const build = (closeLabel) => {
    if (viewer) return viewer;
    const label = closeLabel || "Закрити";
    viewer = document.createElement("div");
    viewer.className = "pdp-zoom";
    viewer.setAttribute("data-pdp-zoom", "");
    viewer.setAttribute("role", "dialog");
    viewer.setAttribute("aria-modal", "true");
    viewer.hidden = true;
    viewer.innerHTML = `
      <button type="button" class="pdp-zoom__close" data-zoom-close aria-label="${label}">&times;</button>
      <p class="pdp-zoom__counter" data-zoom-counter></p>
      <div class="pdp-zoom__canvas" data-zoom-canvas><img alt="" data-zoom-img></div>`;
    document.body.appendChild(viewer);

    viewer.querySelector("[data-zoom-close]").addEventListener("click", close);
    viewer.addEventListener("click", (event) => {
      if (event.target === viewer) close();
    });
    bindGestures(viewer.querySelector("[data-zoom-canvas]"));
    return viewer;
  };

  const el = (name) => viewer.querySelector(`[data-zoom-${name}]`);

  const apply = (eased) => {
    const img = el("img");
    img.classList.toggle("is-eased", Boolean(eased));
    img.style.transform = `translate3d(${view.x}px, ${view.y}px, 0) scale(${view.scale})`;
    el("canvas").classList.toggle("is-zoomed", view.scale > 1);
  };

  const clampOffsets = () => {
    const canvas = el("canvas");
    const img = el("img");
    const maxX = Math.max(0, (img.offsetWidth * view.scale - canvas.clientWidth) / 2);
    const maxY = Math.max(0, (img.offsetHeight * view.scale - canvas.clientHeight) / 2);
    view.x = clamp(view.x, -maxX, maxX);
    view.y = clamp(view.y, -maxY, maxY);
  };

  // Тримає точку під пальцем/курсором на місці при зміні масштабу
  const zoomAt = (clientX, clientY, nextScale, eased) => {
    const img = el("img");
    const next = clamp(nextScale, 1, nativeLimit(img, MAX_SCALE));
    const rect = img.getBoundingClientRect();
    const ratio = next / view.scale;
    view.x -= (clientX - (rect.left + rect.width / 2)) * (ratio - 1);
    view.y -= (clientY - (rect.top + rect.height / 2)) * (ratio - 1);
    view.scale = next;
    if (next === 1) {
      view.x = 0;
      view.y = 0;
    } else {
      clampOffsets();
    }
    apply(eased);
  };

  const show = (index) => {
    const total = view.images.length;
    if (!total) return;
    view.index = (index + total) % total;
    const item = view.images[view.index];
    const img = el("img");
    img.src = item.src;
    img.alt = item.alt;
    view.scale = 1;
    view.x = 0;
    view.y = 0;
    apply(false);
    const counter = el("counter");
    counter.textContent = total > 1 ? `${view.index + 1} / ${total}` : "";
  };

  const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  const midpoint = (a, b) => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 });

  const bindGestures = (canvas) => {
    canvas.addEventListener("pointerdown", (event) => {
      // capture лишаємо лише для миші: на синтетичних touch-подіях
      // і в частини Safari capture зриває подальший pointerup
      if (event.pointerType === "mouse") {
        try {
          canvas.setPointerCapture(event.pointerId);
        } catch {
          /* ignore */
        }
      }
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });

      if (pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        pinch = { distance: distance(a, b), scale: view.scale };
        drag = null;
        return;
      }
      drag = {
        id: event.pointerId,
        x: event.clientX,
        y: event.clientY,
        moved: 0,
      };
    });

    canvas.addEventListener("pointermove", (event) => {
      if (!pointers.has(event.pointerId)) return;
      const previous = pointers.get(event.pointerId);
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });

      if (pinch && pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        const center = midpoint(a, b);
        zoomAt(center.x, center.y, (pinch.scale * distance(a, b)) / pinch.distance, false);
        return;
      }
      if (!drag || drag.id !== event.pointerId) return;

      const dx = event.clientX - previous.x;
      const dy = event.clientY - previous.y;
      drag.moved += Math.abs(dx) + Math.abs(dy);
      if (view.scale > 1) {
        view.x += dx;
        view.y += dy;
        clampOffsets();
        apply(false);
      }
    });

    const endPointer = (event, cancelled) => {
      pointers.delete(event.pointerId);
      if (pointers.size < 2) pinch = null;

      const active = drag && drag.id === event.pointerId ? drag : null;
      if (active) drag = null;
      if (!active || cancelled) return;

      const dx = event.clientX - active.x;
      if (view.scale === 1 && Math.abs(dx) > SWIPE_MIN) {
        lastTap = 0;
        show(view.index + (dx < 0 ? 1 : -1));
        return;
      }
      // подвійний тап: touch і pen; на мишці — dblclick
      if (event.pointerType === "mouse" || active.moved > 12) return;

      const now = Date.now();
      if (now - lastTap > 0 && now - lastTap < DOUBLE_TAP_MS) {
        lastTap = 0;
        zoomAt(event.clientX, event.clientY, view.scale > 1 ? 1 : TAP_SCALE, true);
      } else {
        lastTap = now;
      }
    };

    canvas.addEventListener("pointerup", (event) => endPointer(event, false));
    canvas.addEventListener("pointercancel", (event) => endPointer(event, true));

    canvas.addEventListener("dblclick", (event) => {
      event.preventDefault();
      zoomAt(event.clientX, event.clientY, view.scale > 1 ? 1 : TAP_SCALE, true);
    });

    canvas.addEventListener(
      "wheel",
      (event) => {
        event.preventDefault();
        const step = event.deltaY < 0 ? 1.18 : 1 / 1.18;
        zoomAt(event.clientX, event.clientY, view.scale * step, false);
      },
      { passive: false }
    );
  };

  const open = (gallery, index) => {
    const slides = [...gallery.querySelectorAll(".pdp-gallery__slide img")];
    if (!slides.length) return;
    view.images = slides.map((img) => ({
      src: img.getAttribute("data-zoom-src") || img.src,
      alt: img.alt || "",
    }));
    view.origin = gallery;
    view.trigger = document.activeElement;

    build(gallery.getAttribute("data-close-label") || "Закрити");
    viewer.hidden = false;
    scrollLock = document.documentElement.style.overflow;
    document.documentElement.style.overflow = "hidden";
    show(index);
    el("close").focus({ preventScroll: true });
  };

  function close() {
    if (!viewer || viewer.hidden) return;
    viewer.hidden = true;
    document.documentElement.style.overflow = scrollLock;
    pointers.clear();
    pinch = null;
    drag = null;

    // Галерея на сторінці лишається на тому фото, яким закрили перегляд
    const dot =
      view.origin && view.origin.querySelector(`[data-gallery-dot="${view.index}"]`);
    if (dot) dot.click();

    if (view.trigger && document.contains(view.trigger)) {
      view.trigger.focus({ preventScroll: true });
    }
  }

  document.addEventListener("keydown", (event) => {
    if (!viewer || viewer.hidden) return;
    if (event.key === "Escape") close();
    if (event.key === "ArrowRight") show(view.index + 1);
    if (event.key === "ArrowLeft") show(view.index - 1);
  });

  document.body.addEventListener("click", (event) => {
    const img = event.target.closest(".pdp-gallery__slide img");
    if (!img) return;
    const gallery = img.closest("[data-pdp-gallery]");
    // свайп по галереї не має відкривати перегляд
    if (!gallery || gallery.dataset.swiped === "1") return;
    const slides = [...gallery.querySelectorAll(".pdp-gallery__slide img")];
    open(gallery, Math.max(0, slides.indexOf(img)));
  });

  const initAll = () => {
    document
      .querySelectorAll("[data-pdp-gallery] .pdp-gallery__stage")
      .forEach(initHoverZoom);
  };

  initAll();
  document.body.addEventListener("htmx:afterSwap", initAll);
})();
