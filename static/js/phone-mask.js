(() => {
  const formatUaPhone = (raw) => {
    let digits = String(raw || "").replace(/\D/g, "");
    if (digits.startsWith("380")) {
      digits = digits.slice(0, 12);
    } else if (digits.startsWith("0")) {
      digits = ("380" + digits.slice(1)).slice(0, 12);
    } else if (digits.length && !digits.startsWith("380")) {
      digits = ("380" + digits).slice(0, 12);
    } else {
      digits = digits.slice(0, 12);
    }

    const rest = digits.slice(3);
    let out = "+380";
    if (rest.length > 0) out += " " + rest.slice(0, 2);
    if (rest.length > 2) out += " " + rest.slice(2, 5);
    if (rest.length > 5) out += " " + rest.slice(5, 7);
    if (rest.length > 7) out += " " + rest.slice(7, 9);
    return out;
  };

  const bind = (input) => {
    if (!input || input.dataset.phoneMaskBound === "1") return;
    input.dataset.phoneMaskBound = "1";
    input.setAttribute("inputmode", "tel");
    input.setAttribute("autocomplete", "tel");
    input.setAttribute("maxlength", "17");

    const apply = () => {
      const next = formatUaPhone(input.value);
      if (input.value !== next) input.value = next;
    };

    input.addEventListener("focus", () => {
      if (!input.value.trim()) input.value = "+380 ";
    });
    input.addEventListener("input", apply);
    input.addEventListener("blur", () => {
      if (input.value.replace(/\D/g, "") === "380") input.value = "";
      else apply();
    });
    if (input.value.trim()) apply();
  };

  const scan = (root) => {
    (root || document).querySelectorAll("input[data-phone-mask]").forEach(bind);
  };

  scan(document);
  document.body.addEventListener("htmx:afterSwap", (event) => {
    scan(event.target);
  });
})();
