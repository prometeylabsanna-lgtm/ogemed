(() => {
  const MIN = 2;
  const DEBOUNCE_MS = 220;

  const forms = document.querySelectorAll("[data-search-suggest]");
  if (!forms.length) return;

  const escapeHtml = (value) =>
    String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  const initForm = (form) => {
    const input = form.querySelector("[data-search-input]");
    const list = form.querySelector("[data-search-list]");
    const endpoint = form.getAttribute("data-suggest-url");
    if (!input || !list || !endpoint) return;

    let timer = null;
    let controller = null;
    let activeIndex = -1;
    let items = [];

    const setOpen = (open) => {
      list.hidden = !open;
      input.setAttribute("aria-expanded", open ? "true" : "false");
      if (!open) {
        activeIndex = -1;
        items.forEach((el) => el.classList.remove("is-active"));
      }
    };

    const render = (payload) => {
      const q = payload.q || "";
      const results = payload.results || [];
      if (!results.length) {
        list.innerHTML = `<li class="search-suggest__empty" role="option">${escapeHtml(
          list.dataset.emptyText || "Нічого не знайдено"
        )}</li>`;
        setOpen(true);
        items = [];
        return;
      }

      const rows = results
        .map((item, index) => {
          const thumb = item.image
            ? `<img class="search-suggest__thumb" src="${escapeHtml(item.image)}" alt="" width="44" height="44" loading="lazy">`
            : `<span class="search-suggest__thumb search-suggest__thumb--empty" aria-hidden="true"></span>`;
          const brand = item.brand
            ? `<span class="search-suggest__brand">${escapeHtml(item.brand)}${
                item.sku ? ` · ${escapeHtml(item.sku)}` : ""
              }</span>`
            : item.sku
              ? `<span class="search-suggest__brand">${escapeHtml(item.sku)}</span>`
              : "";
          const price = item.price
            ? `<span class="search-suggest__price">${escapeHtml(item.price)} ₴</span>`
            : "";
          return `<li class="search-suggest__item" role="option" id="suggest-opt-${index}">
            <a class="search-suggest__link" href="${escapeHtml(item.url)}" data-suggest-link>
              ${thumb}
              <span class="search-suggest__meta">
                <span class="search-suggest__name">${escapeHtml(item.name)}</span>
                ${brand}
              </span>
              ${price}
            </a>
          </li>`;
        })
        .join("");

      const more = `<li class="search-suggest__more">
        <a href="${escapeHtml(form.action)}?q=${encodeURIComponent(q)}">${escapeHtml(
          list.dataset.moreText || "Усі результати"
        )}</a>
      </li>`;

      list.innerHTML = rows + more;
      items = Array.from(list.querySelectorAll("[data-suggest-link]"));
      setOpen(true);
    };

    const fetchSuggest = (q) => {
      if (controller) controller.abort();
      controller = new AbortController();
      const url = `${endpoint}?q=${encodeURIComponent(q)}`;
      fetch(url, {
        headers: { Accept: "application/json" },
        signal: controller.signal,
        credentials: "same-origin",
      })
        .then((res) => (res.ok ? res.json() : Promise.reject()))
        .then(render)
        .catch((err) => {
          if (err && err.name === "AbortError") return;
          setOpen(false);
        });
    };

    input.addEventListener("input", () => {
      const q = input.value.trim();
      window.clearTimeout(timer);
      if (q.length < MIN) {
        setOpen(false);
        list.innerHTML = "";
        return;
      }
      timer = window.setTimeout(() => fetchSuggest(q), DEBOUNCE_MS);
    });

    input.addEventListener("keydown", (event) => {
      if (list.hidden || !items.length) return;
      if (event.key === "ArrowDown") {
        event.preventDefault();
        activeIndex = (activeIndex + 1) % items.length;
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        activeIndex = (activeIndex - 1 + items.length) % items.length;
      } else if (event.key === "Enter" && activeIndex >= 0) {
        event.preventDefault();
        items[activeIndex].click();
        return;
      } else if (event.key === "Escape") {
        setOpen(false);
        return;
      } else {
        return;
      }
      items.forEach((el, i) => el.classList.toggle("is-active", i === activeIndex));
      const active = items[activeIndex];
      if (active) {
        input.setAttribute("aria-activedescendant", active.parentElement.id);
        active.scrollIntoView({ block: "nearest" });
      }
    });

    input.addEventListener("blur", () => {
      window.setTimeout(() => setOpen(false), 150);
    });

    document.addEventListener("click", (event) => {
      if (!form.contains(event.target)) setOpen(false);
    });
  };

  forms.forEach(initForm);
})();
