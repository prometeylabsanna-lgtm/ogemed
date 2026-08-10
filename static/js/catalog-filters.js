(() => {
  const OPEN_CLASS = "is-open";
  const VIEW_STORAGE_KEY = "catalog-view";
  const VIEW_VALUES = new Set(["grid", "list"]);
  const FILTER_KEYS = [
    "brand",
    "price_min",
    "price_max",
    "attr",
    "availability",
    "label",
    "skin_type",
  ];

  const currentFilters = () => {
    const params = new URLSearchParams(window.location.search);
    params.delete("page");
    return params;
  };

  const readStoredView = () => {
    try {
      const stored = window.localStorage.getItem(VIEW_STORAGE_KEY);
      if (VIEW_VALUES.has(stored)) return stored;
    } catch (_err) {
      /* private mode / blocked storage */
    }
    return null;
  };

  const writeStoredView = (view) => {
    try {
      window.localStorage.setItem(VIEW_STORAGE_KEY, view);
    } catch (_err) {
      /* ignore */
    }
  };

  const resolveView = () => {
    const fromUrl = new URLSearchParams(window.location.search).get("view");
    if (VIEW_VALUES.has(fromUrl)) return fromUrl;
    return readStoredView() || "grid";
  };

  const syncViewUrl = (view) => {
    const url = new URL(window.location.href);
    if (view === "grid") {
      url.searchParams.delete("view");
    } else {
      url.searchParams.set("view", view);
    }
    const next = url.pathname + url.search + url.hash;
    const current = window.location.pathname + window.location.search + window.location.hash;
    if (next !== current) {
      window.history.replaceState(window.history.state, "", next);
    }
  };

  const applyView = (view, { syncUrl = true } = {}) => {
    const next = VIEW_VALUES.has(view) ? view : "grid";
    document.querySelectorAll("[data-product-grid]").forEach((grid) => {
      grid.setAttribute("data-view", next);
    });
    document.querySelectorAll("[data-catalog-view] input[name='catalog_view']").forEach((input) => {
      input.checked = input.value === next;
    });
    writeStoredView(next);
    if (syncUrl) syncViewUrl(next);
  };

  const initCatalogView = (root) => {
    if (!root || root.dataset.viewReady === "1") return;
    root.dataset.viewReady = "1";
    root.addEventListener("change", (event) => {
      const input = event.target.closest("input[name='catalog_view']");
      if (!input || !VIEW_VALUES.has(input.value)) return;
      applyView(input.value);
    });
  };

  // htmx only swaps the grid, so category links keep the querystring rendered on
  // the initial load — rebuild them from the live URL at click time.
  const carryFiltersOver = (link) => {
    const url = new URL(link.getAttribute("href"), window.location.href);
    const params = currentFilters();
    const query = params.toString();
    link.setAttribute("href", url.pathname + (query ? `?${query}` : ""));
  };

  const syncReset = () => {
    const link = document.querySelector("[data-filter-reset]");
    if (!link) return;
    const params = currentFilters();
    const active = FILTER_KEYS.some((key) => {
      const values = params.getAll(key).filter((value) => value !== "");
      if (key === "skin_type") {
        return values.some((value) => value !== "select");
      }
      return values.length > 0;
    });
    link.toggleAttribute("hidden", !active);
  };

  const panelOf = (dd) => dd.querySelector("[data-dropdown-panel]");
  const toggleOf = (dd) => dd.querySelector("[data-dropdown-toggle]");

  const setOpen = (dd, open) => {
    const panel = panelOf(dd);
    const toggle = toggleOf(dd);
    if (!panel || !toggle) return;
    dd.classList.toggle(OPEN_CLASS, open);
    toggle.setAttribute("aria-expanded", String(open));
    if (open) {
      panel.removeAttribute("hidden");
    } else {
      panel.setAttribute("hidden", "");
    }
  };

  const closeAll = (except) => {
    document.querySelectorAll(`[data-dropdown].${OPEN_CLASS}`).forEach((dd) => {
      if (dd !== except) setOpen(dd, false);
    });
  };

  const priceLabel = (out, min, max) => {
    if (min && max) return `${min} — ${max}`;
    if (min) return `${out.dataset.priceFrom || ""} ${min}`.trim();
    if (max) return `${out.dataset.priceTo || ""} ${max}`.trim();
    return "";
  };

  const syncValue = (dd) => {
    const out = dd.querySelector("[data-dropdown-value]");
    if (!out) return;
    const empty = out.dataset.empty || "";

    const checked = Array.from(
      dd.querySelectorAll('input[type="checkbox"]:checked, input[type="radio"]:checked')
    );
    if (checked.length) {
      out.textContent = checked.map((el) => el.dataset.label || el.value).join(", ");
      return;
    }

    const min = dd.querySelector('input[name="price_min"]');
    const max = dd.querySelector('input[name="price_max"]');
    if (min || max) {
      const label = priceLabel(out, min ? min.value.trim() : "", max ? max.value.trim() : "");
      out.textContent = label || empty;
      return;
    }

    out.textContent = empty;
  };

  const init = (dd) => {
    if (dd.dataset.dropdownReady === "1") return;
    const panel = panelOf(dd);
    const toggle = toggleOf(dd);
    if (!panel || !toggle) return;
    dd.dataset.dropdownReady = "1";

    setOpen(dd, false);
    syncValue(dd);

    toggle.addEventListener("click", (event) => {
      event.preventDefault();
      const willOpen = !dd.classList.contains(OPEN_CLASS);
      closeAll(dd);
      setOpen(dd, willOpen);
    });

    panel.addEventListener("change", () => syncValue(dd));
    panel.addEventListener("input", () => syncValue(dd));
    panel.addEventListener("click", (event) => {
      const link = event.target.closest("a");
      if (link) carryFiltersOver(link);
      if (link || event.target.closest('button[type="submit"]')) setOpen(dd, false);
    });
  };

  // Радіо саме по собі не знімається, тому повторний клік по вибраній картці
  // бренду обробляємо вручну: скасовуємо активацію і чистимо фільтр.
  const initBrandToggle = (card) => {
    if (card.dataset.brandToggleReady === "1") return;
    const input = card.querySelector(".brand-card__input");
    if (!input) return;
    card.dataset.brandToggleReady = "1";

    card.addEventListener("click", (event) => {
      // клік по самому input (пробіл із клавіатури) лишаємо штатним
      if (event.target === input || !input.checked) return;
      event.preventDefault();
      input.checked = false;
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
  };

  const openSkinTypeSelect = () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("skin_type") !== "select") return;
    const dd = document.querySelector("[data-skin-type-filter]");
    if (!dd) return;
    closeAll(dd);
    setOpen(dd, true);
    const toggle = toggleOf(dd);
    if (toggle) {
      try {
        toggle.focus({ preventScroll: true });
      } catch (_err) {
        toggle.focus();
      }
    }
  };

  const initAll = () => {
    document.querySelectorAll("[data-dropdown]").forEach(init);
    document.querySelectorAll(".brand-card").forEach(initBrandToggle);
    document.querySelectorAll("[data-catalog-view]").forEach(initCatalogView);
    applyView(resolveView(), { syncUrl: true });
    syncReset();
    openSkinTypeSelect();
  };

  // Empty inputs are still serialised by FormData; drop them so the pushed URL stays clean.
  document.addEventListener("htmx:configRequest", (event) => {
    const elt = event.detail.elt;
    if (!elt || !elt.closest || !elt.closest("#catalog-filters, #catalog-sort")) return;
    const params = event.detail.parameters;
    if (!params || typeof params.getAll !== "function") return;
    const keys = new Set();
    params.forEach((value, key) => keys.add(key));
    keys.forEach((key) => {
      const kept = params.getAll(key).filter((value) => String(value).trim() !== "");
      params.delete(key);
      kept.forEach((value) => params.append(key, value));
    });
    // Зберігаємо поточний вигляд у запиті сортування/фільтрів (без окремого reload від радіо).
    const view = resolveView();
    if (view && view !== "grid") {
      params.set("view", view);
    } else {
      params.delete("view");
    }
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest("[data-dropdown]")) closeAll(null);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const open = document.querySelector(`[data-dropdown].${OPEN_CLASS}`);
    if (!open) return;
    setOpen(open, false);
    const toggle = toggleOf(open);
    if (toggle) toggle.focus();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }
  document.addEventListener("htmx:afterSwap", () => {
    initAll();
  });
  document.addEventListener("htmx:pushedIntoHistory", syncReset);
})();
