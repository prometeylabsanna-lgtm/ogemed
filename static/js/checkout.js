(() => {
  const select = document.querySelector("#id_delivery_type");
  if (!select) return;

  const sync = () => {
    const value = select.value;
    document.querySelectorAll("[data-delivery-block]").forEach((block) => {
      const match = block.getAttribute("data-delivery-block") === value;
      block.hidden = !match;
    });
  };

  select.addEventListener("change", sync);
  sync();

  const attachAutocomplete = ({
    input,
    listEl,
    refInput,
    buildUrl,
    onSelect,
    emptyLabel,
    minChars = 2,
  }) => {
    if (!input || !listEl) return;

    let timer = null;
    let items = [];
    let active = -1;
    let abortCtrl = null;

    const hide = () => {
      listEl.hidden = true;
      listEl.innerHTML = "";
      items = [];
      active = -1;
      input.setAttribute("aria-expanded", "false");
    };

    const render = () => {
      listEl.innerHTML = "";
      if (!items.length) {
        const li = document.createElement("li");
        li.className = "np-autocomplete__empty";
        li.setAttribute("role", "option");
        li.textContent = emptyLabel;
        listEl.appendChild(li);
        listEl.hidden = false;
        input.setAttribute("aria-expanded", "true");
        return;
      }
      items.forEach((item, idx) => {
        const li = document.createElement("li");
        li.className = "np-autocomplete__option";
        li.setAttribute("role", "option");
        li.id = `${input.id}-opt-${idx}`;
        li.setAttribute("aria-selected", idx === active ? "true" : "false");
        if (idx === active) li.classList.add("is-active");
        li.textContent = item.name || "";
        li.addEventListener("mousedown", (event) => {
          event.preventDefault();
          choose(item);
        });
        listEl.appendChild(li);
      });
      listEl.hidden = false;
      input.setAttribute("aria-expanded", "true");
    };

    const choose = (item) => {
      input.value = item.name || "";
      if (refInput) refInput.value = item.ref || "manual";
      if (typeof onSelect === "function") onSelect(item);
      hide();
    };

    const fetchItems = async (q) => {
      if (abortCtrl) abortCtrl.abort();
      abortCtrl = new AbortController();
      try {
        const resp = await fetch(buildUrl(q), { signal: abortCtrl.signal });
        const data = await resp.json();
        items = data.results || [];
        active = items.length ? 0 : -1;
        render();
      } catch (err) {
        if (err && err.name === "AbortError") return;
        items = [];
        render();
      }
    };

    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-expanded", "false");
    input.setAttribute("aria-controls", listEl.id);
    input.setAttribute("autocomplete", "off");

    input.addEventListener("input", () => {
      if (refInput) refInput.value = "";
      clearTimeout(timer);
      const q = input.value.trim();
      if (q.length < minChars) {
        hide();
        return;
      }
      timer = setTimeout(() => fetchItems(q), 350);
    });

    input.addEventListener("keydown", (event) => {
      if (listEl.hidden) return;
      if (event.key === "ArrowDown") {
        event.preventDefault();
        if (!items.length) return;
        active = (active + 1) % items.length;
        render();
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        if (!items.length) return;
        active = (active - 1 + items.length) % items.length;
        render();
      } else if (event.key === "Enter") {
        if (active >= 0 && items[active]) {
          event.preventDefault();
          choose(items[active]);
        }
      } else if (event.key === "Escape") {
        hide();
      }
    });

    input.addEventListener("blur", () => {
      setTimeout(hide, 150);
    });
  };

  const cityInput = document.querySelector("#id_np_city_name");
  const cityRef = document.querySelector("#id_np_city_ref");
  const cityList = document.querySelector("#np-city-list");
  const whInput = document.querySelector("#id_np_warehouse_name");
  const whRef = document.querySelector("#id_np_warehouse_ref");
  const whList = document.querySelector("#np-warehouse-list");
  const pointType = document.querySelector("#id_np_point_type");

  const syncWarehouseEnabled = () => {
    if (!whInput) return;
    const enabled = Boolean(cityRef && cityRef.value && cityRef.value !== "manual");
    whInput.disabled = !enabled;
    if (!enabled) {
      whInput.value = "";
      if (whRef) whRef.value = "";
    }
  };

  attachAutocomplete({
    input: cityInput,
    listEl: cityList,
    refInput: cityRef,
    emptyLabel: (cityList && cityList.dataset.emptyLabel) || "Нічого не знайдено",
    buildUrl: (q) => `/api/np/cities/?q=${encodeURIComponent(q)}`,
    onSelect: () => {
      syncWarehouseEnabled();
      if (whInput) whInput.focus();
    },
  });

  attachAutocomplete({
    input: whInput,
    listEl: whList,
    refInput: whRef,
    emptyLabel: (whList && whList.dataset.emptyLabel) || "Нічого не знайдено",
    minChars: 0,
    buildUrl: (q) => {
      const ref = cityRef ? cityRef.value : "";
      return `/api/np/warehouses/?city_ref=${encodeURIComponent(ref)}&q=${encodeURIComponent(q)}`;
    },
    onSelect: (item) => {
      if (pointType && item.point_type) pointType.value = item.point_type;
    },
  });

  if (whInput) {
    whInput.addEventListener("focus", () => {
      if (whInput.disabled) return;
      if (!whInput.value.trim()) {
        whInput.dispatchEvent(new Event("input", { bubbles: true }));
      }
    });
  }

  if (cityInput) {
    cityInput.addEventListener("input", syncWarehouseEnabled);
  }
  syncWarehouseEnabled();
})();

(() => {
  const paySelect = document.querySelector("#id_payment_type");
  if (!paySelect) return;
  const hints = document.querySelectorAll("[data-payment-hint]");
  const syncPayHint = () => {
    const value = paySelect.value;
    hints.forEach((el) => {
      el.hidden = el.getAttribute("data-payment-hint") !== value;
    });
  };
  paySelect.addEventListener("change", syncPayHint);
  syncPayHint();
})();

(() => {
  const form = document.querySelector("[data-checkout-form]");
  if (!form) return;

  const openAcc = (acc) => {
    if (acc && !acc.open) acc.open = true;
  };

  form.querySelectorAll(".field-error, .form-errors").forEach((el) => {
    openAcc(el.closest("details.checkout-acc"));
  });

  if (form.querySelector(".form-errors")) {
    openAcc(form.querySelector('[data-checkout-acc="delivery"]'));
  }

  const firstError = form.querySelector(".field-error, .form-errors");
  if (firstError) {
    const target = firstError.closest("details.checkout-acc") || firstError;
    if (typeof target.scrollIntoView === "function") {
      window.requestAnimationFrame(() => {
        target.scrollIntoView({ block: "nearest", behavior: "smooth" });
      });
    }
  }

  // C2: block double-submit (button outside form via form="checkout-form")
  let submitting = false;
  const submitControls = () =>
    Array.from(
      document.querySelectorAll(
        'button[type="submit"][form="checkout-form"], #checkout-form button[type="submit"]'
      )
    );

  form.addEventListener("submit", (event) => {
    if (submitting) {
      event.preventDefault();
      return;
    }
    submitting = true;
    submitControls().forEach((btn) => {
      btn.disabled = true;
      btn.setAttribute("aria-busy", "true");
    });
  });
})();
