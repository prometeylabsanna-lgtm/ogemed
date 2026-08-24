(() => {
  const header = document.querySelector("[data-site-header]");
  const burger = document.querySelector("[data-burger]");
  const mobileMenu = document.querySelector("[data-mobile-menu]");

  const onScroll = () => {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 8);
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (burger && mobileMenu && header) {
    const setMenuOpen = (open) => {
      burger.setAttribute("aria-expanded", String(open));
      header.classList.toggle("is-menu-open", open);
      document.documentElement.classList.toggle("is-mobile-menu-open", open);
      document.body.classList.toggle("is-mobile-menu-open", open);
      if (open) {
        mobileMenu.removeAttribute("hidden");
        mobileMenu.inert = false;
      } else {
        mobileMenu.setAttribute("hidden", "");
        mobileMenu.inert = true;
      }
    };

    /* закрите меню не бере участі в a11y / фокусі (і не роздуває layout у WebKit) */
    mobileMenu.inert = true;

    burger.addEventListener("click", () => {
      const open = burger.getAttribute("aria-expanded") === "true";
      setMenuOpen(!open);
    });

    mobileMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => setMenuOpen(false));
    });
  }

  const catalogNav = document.querySelector("[data-catalog-nav]");
  if (catalogNav) {
    const trigger = catalogNav.querySelector("[data-catalog-nav-trigger]");
    const setOpen = (open) => {
      catalogNav.classList.toggle("is-open", open);
      if (trigger) trigger.setAttribute("aria-expanded", String(open));
    };
    // Touch / click toggle (desktop still uses :hover / :focus-within)
    if (trigger) {
      trigger.addEventListener("click", (event) => {
        const coarse = window.matchMedia("(hover: none)").matches;
        if (!coarse) return;
        event.preventDefault();
        setOpen(!catalogNav.classList.contains("is-open"));
      });
    }
    document.addEventListener("click", (event) => {
      if (!catalogNav.contains(event.target)) setOpen(false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") setOpen(false);
    });
  }

  document.querySelectorAll("[data-callback-trigger]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = document.querySelector("[data-callback-modal]");
      if (!modal) return;
      modal.removeAttribute("hidden");
      const first = modal.querySelector("#cb-name");
      if (first) first.focus({ preventScroll: true });
    });
  });
  document.querySelectorAll("[data-callback-close]").forEach((el) => {
    el.addEventListener("click", () => {
      const modal = document.querySelector("[data-callback-modal]");
      if (modal) modal.setAttribute("hidden", "");
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const callbackModal = document.querySelector("[data-callback-modal]");
    if (callbackModal && !callbackModal.hasAttribute("hidden")) {
      callbackModal.setAttribute("hidden", "");
    }
    const stockModal = document.querySelector("[data-stock-notify-modal]");
    if (stockModal && !stockModal.hasAttribute("hidden")) {
      stockModal.setAttribute("hidden", "");
    }
  });

  const openStockNotifyModal = (trigger) => {
    const modal = document.querySelector("[data-stock-notify-modal]");
    if (!modal) return;
    const label = trigger.getAttribute("data-product-label") || "";
    const url = trigger.getAttribute("data-product-url") || "";
    const labelInput = modal.querySelector("[data-stock-notify-label]");
    const urlInput = modal.querySelector("[data-stock-notify-url]");
    const hint = modal.querySelector("[data-stock-notify-hint]");
    const result = modal.querySelector("#stock-notify-result");
    const phone = modal.querySelector("#sn-phone");
    if (labelInput) labelInput.value = label;
    if (urlInput) urlInput.value = url;
    if (hint) hint.textContent = label;
    if (result) result.innerHTML = "";
    if (phone) phone.value = "";
    modal.removeAttribute("hidden");
    if (phone) phone.focus({ preventScroll: true });
  };

  document.body.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-stock-notify-trigger]");
    if (trigger) {
      event.preventDefault();
      openStockNotifyModal(trigger);
      return;
    }
    if (event.target.closest("[data-stock-notify-close]")) {
      const modal = document.querySelector("[data-stock-notify-modal]");
      if (modal) modal.setAttribute("hidden", "");
    }
  });

  const openCartPopup = () => {
    const popup = document.querySelector("[data-cart-popup]");
    if (!popup) return;
    popup.removeAttribute("hidden");
    /* лише вертикаль — overflow:hidden на обох осях ламає sticky брендів */
    document.documentElement.style.overflowY = "hidden";
    document.body.style.overflowY = "hidden";
  };
  const closeCartPopup = () => {
    const popup = document.querySelector("[data-cart-popup]");
    if (popup) popup.setAttribute("hidden", "");
    document.documentElement.style.overflowY = "";
    document.body.style.overflowY = "";
  };

  document.querySelectorAll("[data-cart-trigger]").forEach((el) => {
    el.addEventListener("click", (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      openCartPopup();
    });
  });
  document.querySelectorAll("[data-cart-close]").forEach((el) => {
    el.addEventListener("click", closeCartPopup);
  });
  document.body.addEventListener("openCartPopup", openCartPopup);

  document.body.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-qty-delta]");
    if (!btn) return;
    const form = btn.closest("form");
    const input = form && form.querySelector('input[name="quantity"]');
    if (!input) return;
    const delta = Number(btn.getAttribute("data-qty-delta")) || 0;
    const min = Number(input.min) || 1;
    const stockCap = Number(input.dataset.stock || input.max || 0);
    const max = stockCap > 0 ? stockCap : Infinity;
    const next = Math.min(max, Math.max(min, (Number(input.value) || 1) + delta));
    if (next === Number(input.value)) return;
    input.value = String(next);
    input.dispatchEvent(new Event("change", { bubbles: true }));
  });

  const initSlider = (root, slideSel, dotSel) => {
    if (!root) return;
    // OOB swap замінює innerHTML #pdp-gallery — ініціалізуємо внутрішній корінь.
    const host =
      root.matches?.("[data-hero-slider], [data-pdp-gallery]")
        ? root
        : root.querySelector?.("[data-pdp-gallery]") || root;
    if (host.dataset.sliderBound === "1") return;
    const slides = [...host.querySelectorAll(slideSel)];
    const dots = [...host.querySelectorAll(dotSel)];
    if (!slides.length) return;
    host.dataset.sliderBound = "1";
    let index = 0;
    const show = (i) => {
      index = (i + slides.length) % slides.length;
      slides.forEach((s, n) => s.classList.toggle("is-active", n === index));
      dots.forEach((d, n) => d.classList.toggle("is-active", n === index));
    };
    dots.forEach((dot) => {
      dot.addEventListener("click", () => {
        const raw = dot.dataset.heroDot ?? dot.dataset.galleryDot ?? "0";
        show(Number(raw));
      });
    });
    if (slides.length > 1) {
      const stage = host.querySelector(".pdp-gallery__stage") || host;
      let startX = 0;
      let startY = 0;
      let tracking = false;
      stage.addEventListener(
        "touchstart",
        (event) => {
          if (event.touches.length !== 1) return;
          tracking = true;
          startX = event.touches[0].clientX;
          startY = event.touches[0].clientY;
        },
        { passive: true }
      );
      stage.addEventListener(
        "touchend",
        (event) => {
          if (!tracking) return;
          tracking = false;
          const touch = event.changedTouches[0];
          const dx = touch.clientX - startX;
          const dy = touch.clientY - startY;
          if (Math.abs(dx) < 40 || Math.abs(dx) <= Math.abs(dy)) return;
          // Позначаємо свайп, щоб tap-зум не відкрився після гортання
          host.dataset.swiped = "1";
          setTimeout(() => delete host.dataset.swiped, 400);
          show(dx < 0 ? index + 1 : index - 1);
        },
        { passive: true }
      );
    }
    if (slides.length > 1 && host.hasAttribute("data-hero-slider")) {
      setInterval(() => show(index + 1), 6000);
    }
    show(0);
  };

  initSlider(
    document.querySelector("[data-hero-slider]"),
    ".home-hero-slide",
    "[data-hero-dot]"
  );
  initSlider(
    document.querySelector("[data-pdp-gallery]"),
    ".pdp-gallery__slide",
    "[data-gallery-dot]"
  );

  document.body.addEventListener("htmx:afterSwap", (event) => {
    if (event.target && event.target.id === "pdp-gallery") {
      initSlider(event.target, ".pdp-gallery__slide", "[data-gallery-dot]");
    }
  });

  const initProductSlider = (root) => {
    if (!root || root.dataset.sliderReady === "1") return;
    const track = root.querySelector("[data-product-slider-track]");
    const prev = root.querySelector("[data-product-slider-prev]");
    const next = root.querySelector("[data-product-slider-next]");
    if (!track || !prev || !next) return;
    root.dataset.sliderReady = "1";

    const maxScroll = () => Math.max(0, track.scrollWidth - track.clientWidth);

    const step = () => {
      const item = track.querySelector(".product-slider__item");
      if (!item) return Math.max(160, Math.floor(track.clientWidth * 0.8));
      const styles = window.getComputedStyle(track);
      const gap = Number.parseFloat(styles.columnGap || styles.gap || "0") || 0;
      return Math.round(item.getBoundingClientRect().width + gap);
    };

    const syncArrows = () => {
      const max = maxScroll();
      const left = track.scrollLeft;
      const atStart = left <= 2;
      const atEnd = left >= max - 2;
      const canScroll = max > 4;
      prev.disabled = !canScroll || atStart;
      next.disabled = !canScroll || atEnd;
      prev.classList.toggle("is-disabled", prev.disabled);
      next.classList.toggle("is-disabled", next.disabled);
      prev.setAttribute("aria-disabled", String(prev.disabled));
      next.setAttribute("aria-disabled", String(next.disabled));
      root.classList.toggle("is-scrollable", canScroll);
    };

    const scrollByDir = (dir) => {
      const max = maxScroll();
      if (max <= 4) return;
      const delta = step() * dir;
      const target = Math.min(max, Math.max(0, track.scrollLeft + delta));
      track.scrollTo({ left: target, behavior: "smooth" });
    };

    prev.addEventListener("click", (event) => {
      event.preventDefault();
      scrollByDir(-1);
    });
    next.addEventListener("click", (event) => {
      event.preventDefault();
      scrollByDir(1);
    });

    track.addEventListener("scroll", syncArrows, { passive: true });
    window.addEventListener("resize", syncArrows);

    if (typeof ResizeObserver !== "undefined") {
      const ro = new ResizeObserver(syncArrows);
      ro.observe(track);
    }

    // Images can change scrollWidth after load
    track.querySelectorAll("img").forEach((img) => {
      if (!img.complete) img.addEventListener("load", syncArrows, { once: true });
    });

    syncArrows();
    requestAnimationFrame(syncArrows);
  };

  document.querySelectorAll("[data-product-slider]").forEach(initProductSlider);
})();
