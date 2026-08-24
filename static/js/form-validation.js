(() => {
  const NAME_MIN = 2;
  const NAME_MAX = 50;
  const MESSAGE_MIN = 15;
  const MESSAGE_MAX = 2000;
  const PASSWORD_MIN = 8;

  const NAME_RE = /^[A-Za-zА-Яа-яЁёІіЇїЄєҐґʼ'`’\- ]+$/u;
  const URLISH_RE = /(https?:\/\/|www\.|[a-z0-9-]+\.[a-z]{2,})/i;
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const HTML_TAG_RE = /<[^>]*>/g;

  const I18N = {
    uk: {
      nameEmpty: "Будь ласка, вкажіть ваше імʼя.",
      nameShort: "Імʼя надто коротке. Введіть щонайменше 2 літери.",
      nameLong: `Імʼя занадто довге (максимум ${NAME_MAX} символів).`,
      nameChars:
        "Імʼя не може містити цифри та спецсимволи. Використовуйте лише літери.",
      phoneEmpty: "Введіть номер телефону.",
      phoneIncomplete:
        "Введіть повний номер телефону: +380 XX XXX XX XX (не вистачає цифр).",
      phoneInvalid:
        "Невірний формат номера. Перевірте правильність введених цифр.",
      emailEmpty: "Електронна пошта обовʼязкова для заповнення.",
      emailInvalid:
        "Введіть коректну email-адресу (наприклад: name@domain.com).",
      messageEmpty: "Напишіть текст вашого повідомлення.",
      messageShort: (left) =>
        `Повідомлення занадто коротке. Опишіть детальніше (мінімум 15 символів). Залишилось ввести ще ${left} симв.`,
      messageLong: "Перевищено максимальний ліміт у 2000 символів.",
      passwordEmpty: "Обовʼязкове поле",
      passwordShort: `Пароль має містити щонайменше ${PASSWORD_MIN} символів`,
      passwordDigits: "Пароль не може складатися лише з цифр",
      passwordMismatch:
        "Введені паролі не збігаються. Перевірте правильність повторного вводу.",
      formCheck: "Перевірте поля форми",
    },
    ru: {
      nameEmpty: "Пожалуйста, укажите ваше имя.",
      nameShort: "Имя слишком короткое. Введите не менее 2 букв.",
      nameLong: `Имя слишком длинное (максимум ${NAME_MAX} символов).`,
      nameChars:
        "Имя не может содержать цифры и спецсимволы. Используйте только буквы.",
      phoneEmpty: "Введите номер телефона.",
      phoneIncomplete:
        "Введите полный номер телефона: +380 XX XXX XX XX (не хватает цифр).",
      phoneInvalid:
        "Неверный формат номера. Проверьте правильность введённых цифр.",
      emailEmpty: "Электронная почта обязательна для заполнения.",
      emailInvalid:
        "Введите корректный email-адрес (например: name@domain.com).",
      messageEmpty: "Напишите текст вашего сообщения.",
      messageShort: (left) =>
        `Сообщение слишком короткое. Опишите подробнее (минимум 15 символов). Осталось ввести ещё ${left} симв.`,
      messageLong: "Превышен максимальный лимит в 2000 символов.",
      passwordEmpty: "Обязательное поле",
      passwordShort: `Пароль должен содержать не менее ${PASSWORD_MIN} символов`,
      passwordDigits: "Пароль не может состоять только из цифр",
      passwordMismatch:
        "Введённые пароли не совпадают. Проверьте повторный ввод.",
      formCheck: "Проверьте поля формы",
    },
  };

  const currentLang = () => {
    const raw = (
      document.documentElement.lang ||
      document.documentElement.getAttribute("lang") ||
      "uk"
    )
      .toLowerCase()
      .slice(0, 2);
    return raw === "ru" ? "ru" : "uk";
  };

  const t = () => I18N[currentLang()] || I18N.uk;

  const normalizeName = (value) => String(value || "").trim().replace(/\s+/g, " ");

  const normalizePhoneDigits = (value) => {
    let digits = String(value || "").replace(/\D/g, "");
    if (digits.startsWith("0") && digits.length === 10) {
      digits = "380" + digits.slice(1);
    }
    return digits;
  };

  const normalizeEmail = (value) => String(value || "").trim().toLowerCase();

  const sanitizeMessage = (value) =>
    String(value || "").replace(HTML_TAG_RE, "").replace(/\u0000/g, "").trim();

  const validateName = (value, required) => {
    const msg = t();
    const name = normalizeName(value);
    if (!name) return required ? msg.nameEmpty : "";
    if (name.length < NAME_MIN) return msg.nameShort;
    if (name.length > NAME_MAX) return msg.nameLong;
    if (URLISH_RE.test(name) || !NAME_RE.test(name)) return msg.nameChars;
    if (![...name].some((ch) => /\p{L}/u.test(ch))) return msg.nameChars;
    return "";
  };

  const validatePhone = (value, required) => {
    const msg = t();
    const raw = String(value || "").trim();
    if (!raw) return required ? msg.phoneEmpty : "";
    const digits = normalizePhoneDigits(raw);
    if (!digits || digits === "380") return required ? msg.phoneEmpty : "";
    if (digits.startsWith("380") && digits.length < 12) return msg.phoneIncomplete;
    if (!/^380\d{9}$/.test(digits)) return msg.phoneInvalid;
    return "";
  };

  const validateEmail = (value, required) => {
    const msg = t();
    const email = normalizeEmail(value);
    if (!email) return required ? msg.emailEmpty : "";
    if (!EMAIL_RE.test(email)) return msg.emailInvalid;
    return "";
  };

  const validateMessage = (value, required) => {
    const msg = t();
    const text = sanitizeMessage(value);
    if (!text) return required ? msg.messageEmpty : "";
    if (text.length < MESSAGE_MIN) {
      return msg.messageShort(MESSAGE_MIN - text.length);
    }
    if (text.length > MESSAGE_MAX) return msg.messageLong;
    return "";
  };

  const validatePassword = (value, required) => {
    const msg = t();
    const password = String(value || "");
    if (!password) return required ? msg.passwordEmpty : "";
    if (password.length < PASSWORD_MIN) return msg.passwordShort;
    if (/^\d+$/.test(password)) return msg.passwordDigits;
    return "";
  };

  const validatePasswordLogin = (value) => {
    return String(value || "") ? "" : t().passwordEmpty;
  };

  const resolveRule = (input) => {
    const explicit = (input.getAttribute("data-validate") || "").trim();
    if (explicit) return explicit;
    const name = (input.name || "").toLowerCase();
    if (
      name === "name" ||
      name === "full_name" ||
      name === "customer_name" ||
      name === "first_name" ||
      name === "last_name"
    ) {
      return "name";
    }
    if (name === "phone" || name === "customer_phone") return "phone";
    if (name === "email" || name === "customer_email" || name === "username") {
      return name === "customer_email" ? "email_optional" : "email";
    }
    if (name === "message" || name === "comment" || name === "courier_comment") {
      return "message_optional";
    }
    if (name === "password1" || name === "password") return "password";
    if (name === "password2" || name === "password_confirmation") {
      return "password_confirm";
    }
    return "";
  };

  const fieldError = (input, rule) => {
    const value = input.value;
    switch (rule) {
      case "name":
        return validateName(value, true);
      case "name_optional":
        return validateName(value, false);
      case "phone":
        return validatePhone(value, true);
      case "phone_optional":
        return validatePhone(value, false);
      case "email":
        return validateEmail(value, true);
      case "email_optional":
        return validateEmail(value, false);
      case "message":
        return validateMessage(value, true);
      case "message_optional":
        return validateMessage(value, false);
      case "password":
        return validatePassword(value, true);
      case "password_login":
        return validatePasswordLogin(value);
      case "password_confirm": {
        const matchName =
          input.getAttribute("data-validate-match") || "password1";
        const form = input.closest("form");
        const other = form && form.querySelector(`[name="${matchName}"]`);
        if (!String(value || "")) return t().passwordEmpty;
        if (other && value !== other.value) return t().passwordMismatch;
        return "";
      }
      default:
        return "";
    }
  };

  const fieldWrap = (input) =>
    input.closest(
      ".form-field, .callback-modal__field, .form-group, .field-wrapper"
    ) || input.parentElement;

  const ensureErrorEl = (input) => {
    const wrap = fieldWrap(input);
    if (!wrap) return null;
    let el =
      wrap.querySelector("[data-field-error]") ||
      wrap.querySelector(".field-error-message") ||
      wrap.querySelector(".field-error");
    if (!el) {
      el = document.createElement("span");
      el.setAttribute("role", "alert");
      wrap.appendChild(el);
    }
    el.classList.add("field-error-message", "field-error");
    el.setAttribute("data-field-error", "");
    return el;
  };

  const setError = (input, message) => {
    const wrap = fieldWrap(input);
    const el = ensureErrorEl(input);
    const has = Boolean(message);
    if (wrap) {
      wrap.classList.toggle("form-field--error", has);
      wrap.classList.toggle("is-invalid", has);
    }
    input.classList.toggle("is-invalid", has);
    input.setAttribute("aria-invalid", has ? "true" : "false");
    if (el) {
      el.textContent = message || "";
      el.hidden = !has;
    }
  };

  const validateInput = (input) => {
    if (!input || input.disabled || input.type === "hidden") return true;
    if (input.classList.contains("hp-field") || input.name === "website") return true;
    const rule = resolveRule(input);
    if (!rule) return true;
    const message = fieldError(input, rule);
    setError(input, message);
    return !message;
  };

  const allValidatedInputs = (form) =>
    Array.from(form.querySelectorAll("input, textarea, select")).filter((el) => {
      if (el.type === "hidden" || el.disabled) return false;
      if (el.classList.contains("hp-field") || el.name === "website") return false;
      return Boolean(resolveRule(el));
    });

  const visibleInputs = (form) =>
    allValidatedInputs(form).filter((el) => {
      const block = el.closest("[data-delivery-block]");
      if (block && block.hidden) return false;
      if (el.closest("[hidden]")) return false;
      return true;
    });

  const focusFirstInvalid = (input) => {
    if (!input) return;
    const acc = input.closest("details.checkout-acc");
    if (acc && !acc.open) acc.open = true;
    if (typeof input.scrollIntoView === "function") {
      input.scrollIntoView({ block: "center", behavior: "smooth" });
    }
    window.requestAnimationFrame(() => {
      if (typeof input.focus === "function") {
        input.focus({ preventScroll: true });
      }
    });
  };

  const validateForm = (form) => {
    let ok = true;
    let firstInvalid = null;
    visibleInputs(form).forEach((input) => {
      const valid = validateInput(input);
      if (!valid) {
        ok = false;
        if (!firstInvalid) firstInvalid = input;
      }
    });
    if (firstInvalid) focusFirstInvalid(firstInvalid);
    return ok;
  };

  const applyServerErrors = (form, html) => {
    if (!html || !form) return;
    let doc;
    try {
      doc = new DOMParser().parseFromString(html, "text/html");
    } catch (_err) {
      return;
    }
    const nodes = doc.querySelectorAll("[data-field-error-for]");
    if (!nodes.length) return;
    let first = null;
    nodes.forEach((node) => {
      const name = node.getAttribute("data-field-error-for");
      const text = (node.textContent || "").trim();
      if (!name || !text) return;
      const input = form.querySelector(`[name="${CSS.escape(name)}"]`);
      if (!input) return;
      setError(input, text);
      if (!first) first = input;
    });
    if (first) focusFirstInvalid(first);
  };

  const setSubmitting = (form, on) => {
    form.classList.toggle("is-submitting", on);
    const buttons = Array.from(
      form.querySelectorAll('button[type="submit"]')
    ).concat(
      Array.from(
        document.querySelectorAll(
          `button[type="submit"][form="${form.id || "__none__"}"]`
        )
      )
    );
    buttons.forEach((btn) => {
      btn.disabled = on;
      btn.classList.toggle("is-loading", on);
      if (on) {
        if (!btn.dataset.labelBackup) btn.dataset.labelBackup = btn.innerHTML;
        if (!btn.querySelector(".btn-spinner")) {
          const spin = document.createElement("span");
          spin.className = "btn-spinner";
          spin.setAttribute("aria-hidden", "true");
          btn.prepend(spin);
        }
      } else if (btn.dataset.labelBackup) {
        btn.innerHTML = btn.dataset.labelBackup;
        delete btn.dataset.labelBackup;
      }
    });
  };

  const bindCharCount = (input) => {
    if (!input.hasAttribute("data-char-count")) return;
    const wrap = fieldWrap(input);
    if (!wrap) return;
    let counter = wrap.querySelector("[data-char-count-el]");
    if (!counter) {
      counter = document.createElement("div");
      counter.className = "field-char-count";
      counter.setAttribute("data-char-count-el", "");
      wrap.appendChild(counter);
    }
    const max = Number(input.getAttribute("maxlength") || MESSAGE_MAX);
    const sync = () => {
      const len = sanitizeMessage(input.value).length;
      counter.textContent = `${len} / ${max}`;
    };
    input.addEventListener("input", sync);
    sync();
  };

  const bindForm = (form) => {
    if (!form || form.dataset.validateBound === "1") return;
    form.dataset.validateBound = "1";

    form.querySelectorAll("[data-char-count]").forEach(bindCharCount);

    allValidatedInputs(form).forEach((input) => {
      input.addEventListener("blur", () => {
        const filled = String(input.value || "").trim().length > 0;
        if (!filled) {
          if (input.classList.contains("is-invalid")) setError(input, "");
          return;
        }
        validateInput(input);
      });
      input.addEventListener("input", () => {
        if (!input.classList.contains("is-invalid")) return;
        validateInput(input);
      });
      input.addEventListener("change", () => {
        if (input.classList.contains("is-invalid")) validateInput(input);
      });
    });

    form.addEventListener(
      "submit",
      (event) => {
        if (!validateForm(form)) {
          event.preventDefault();
          event.stopImmediatePropagation();
          return;
        }
        if (!form.hasAttribute("hx-post") && !form.hasAttribute("hx-get")) {
          setSubmitting(form, true);
        }
      },
      true
    );

    form.addEventListener("htmx:beforeRequest", (event) => {
      if (!validateForm(form)) {
        event.preventDefault();
        return;
      }
      setSubmitting(form, true);
    });

    form.addEventListener("htmx:beforeSwap", (event) => {
      const xhr = event.detail && event.detail.xhr;
      if (!xhr) return;
      const status = xhr.status;
      if (status === 422 || status === 400) {
        event.detail.shouldSwap = true;
        event.detail.isError = false;
        applyServerErrors(form, xhr.responseText);
      }
    });

    form.addEventListener("htmx:afterRequest", (event) => {
      setSubmitting(form, false);
      const xhr = event.detail && event.detail.xhr;
      if (xhr && (xhr.status === 422 || xhr.status === 400)) {
        applyServerErrors(form, xhr.responseText);
      }
    });
    form.addEventListener("htmx:responseError", (event) => {
      setSubmitting(form, false);
      const xhr = event.detail && event.detail.xhr;
      if (xhr) applyServerErrors(form, xhr.responseText);
    });
    form.addEventListener("htmx:sendError", () => setSubmitting(form, false));
  };

  const scan = (root) => {
    (root || document)
      .querySelectorAll("form[data-validate-form]")
      .forEach(bindForm);
  };

  scan(document);
  document.body.addEventListener("htmx:afterSwap", (event) => {
    scan(event.target);
  });
})();
