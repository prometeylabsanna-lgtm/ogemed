(function () {
  "use strict";

  var root = document.querySelector("[data-history-stack]");
  if (!root) return;

  var stack = root.querySelector("[data-paper-stack]");
  if (!stack) return;

  var dots = Array.prototype.slice.call(
    root.querySelectorAll("[data-paper-dots] .about-paper__dot")
  );
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var drag = null;
  var busy = false;
  var EXIT_MS = 820;
  var SETTLE_MS = 780;
  var ROTS = [-1.6, 2.4, -2.8, 1.8];

  function cards() {
    return Array.prototype.slice.call(stack.querySelectorAll("[data-paper-card]"));
  }

  function clearInlineMotion(card) {
    card.style.transform = "";
    card.style.opacity = "";
    card.style.transition = "";
  }

  function layout() {
    var list = cards();
    list.forEach(function (card, index) {
      card.style.setProperty("--paper-depth", String(index));
      card.style.setProperty(
        "--paper-base-rot",
        ROTS[index % ROTS.length] + "deg"
      );
      card.classList.toggle("is-front", index === 0);
      card.tabIndex = index === 0 ? 0 : -1;
      if (
        !card.classList.contains("is-dragging") &&
        !card.classList.contains("is-exit") &&
        !card.classList.contains("is-settle")
      ) {
        clearInlineMotion(card);
      }
    });
    var front = list[0];
    var active = front ? Number(front.getAttribute("data-paper-index") || 0) : 0;
    dots.forEach(function (dot, i) {
      dot.classList.toggle("is-active", i === active);
    });
  }

  function advance() {
    var list = cards();
    if (list.length < 2) return;
    stack.appendChild(list[0]);
    layout();
  }

  function retreat() {
    var list = cards();
    if (list.length < 2) return;
    stack.insertBefore(list[list.length - 1], list[0]);
    layout();
  }

  function bringToFront(card) {
    if (!card || card === cards()[0] || busy) return;
    stack.insertBefore(card, stack.firstChild);
    layout();
  }

  function settleBack(card) {
    card.classList.remove("is-dragging");
    card.classList.add("is-settle");
    void card.offsetWidth;
    clearInlineMotion(card);
    window.setTimeout(function () {
      card.classList.remove("is-settle");
      layout();
    }, SETTLE_MS);
  }

  function flingCard(card, dir) {
    busy = true;
    card.classList.remove("is-dragging");
    card.classList.add("is-exit");
    void card.offsetWidth;
    var distance = Math.max(window.innerWidth * 0.55, 320);
    card.style.transform =
      "translateX(" +
      dir * distance +
      "px) translateY(" +
      dir * 28 +
      "px) rotate(" +
      dir * 14 +
      "deg)";
    card.style.opacity = "0";
    window.setTimeout(function () {
      card.classList.remove("is-exit");
      clearInlineMotion(card);
      if (dir < 0) advance();
      else retreat();
      busy = false;
    }, EXIT_MS);
  }

  function swipeThreshold(card) {
    var w = card.offsetWidth || 280;
    return Math.max(72, Math.min(w * 0.35, 160));
  }

  function onPointerDown(event) {
    if (busy) return;
    var card = event.target.closest("[data-paper-card]");
    if (!card || !stack.contains(card)) return;
    if (event.button != null && event.button !== 0) return;

    if (!card.classList.contains("is-front")) {
      bringToFront(card);
      return;
    }

    drag = {
      card: card,
      startX: event.clientX,
      startY: event.clientY,
      dx: 0,
      active: false,
      pointerId: event.pointerId,
      raf: 0,
    };
    try {
      card.setPointerCapture(event.pointerId);
    } catch (err) {
      /* ignore */
    }
    card.classList.add("is-dragging");
  }

  function applyDragFrame() {
    if (!drag) return;
    drag.raf = 0;
    var dx = drag.dx;
    var rot = dx * 0.028;
    var fade = Math.max(0.58, 1 - Math.abs(dx) / 620);
    drag.card.style.transform =
      "translateX(" + dx + "px) rotate(" + rot + "deg)";
    drag.card.style.opacity = String(fade);
  }

  function onPointerMove(event) {
    if (!drag || drag.pointerId !== event.pointerId) return;
    drag.dx = event.clientX - drag.startX;
    var dy = event.clientY - drag.startY;
    if (!drag.active && Math.abs(drag.dx) < 6 && Math.abs(dy) < 6) return;
    if (!drag.active && Math.abs(dy) > Math.abs(drag.dx) * 1.35) {
      endDrag(false);
      return;
    }
    drag.active = true;
    event.preventDefault();
    if (!drag.raf) {
      drag.raf = window.requestAnimationFrame(applyDragFrame);
    }
  }

  function endDrag(commit) {
    if (!drag) return;
    var card = drag.card;
    var dx = drag.dx;
    var active = drag.active;
    if (drag.raf) {
      window.cancelAnimationFrame(drag.raf);
      drag.raf = 0;
    }
    try {
      card.releasePointerCapture(drag.pointerId);
    } catch (err) {
      /* ignore */
    }
    drag = null;

    if (!commit || !active) {
      settleBack(card);
      return;
    }

    if (Math.abs(dx) < swipeThreshold(card)) {
      settleBack(card);
      return;
    }

    if (reduceMotion) {
      card.classList.remove("is-dragging");
      clearInlineMotion(card);
      if (dx < 0) advance();
      else retreat();
      return;
    }

    flingCard(card, dx < 0 ? -1 : 1);
  }

  function onPointerUp(event) {
    if (!drag || drag.pointerId !== event.pointerId) return;
    endDrag(true);
  }

  function onPointerCancel(event) {
    if (!drag || drag.pointerId !== event.pointerId) return;
    endDrag(false);
  }

  function onKeyDown(event) {
    if (busy) return;
    var front = stack.querySelector(".about-paper__card.is-front");
    if (!front || document.activeElement !== front) return;
    if (event.key === "ArrowLeft" || event.key === "ArrowDown") {
      event.preventDefault();
      if (reduceMotion) {
        advance();
      } else {
        flingCard(front, -1);
      }
      window.setTimeout(function () {
        var next = stack.querySelector(".about-paper__card.is-front");
        if (next) next.focus();
      }, EXIT_MS + 20);
    } else if (event.key === "ArrowRight" || event.key === "ArrowUp") {
      event.preventDefault();
      if (reduceMotion) {
        retreat();
      } else {
        flingCard(front, 1);
      }
      window.setTimeout(function () {
        var next = stack.querySelector(".about-paper__card.is-front");
        if (next) next.focus();
      }, EXIT_MS + 20);
    }
  }

  stack.addEventListener("pointerdown", onPointerDown);
  stack.addEventListener("pointermove", onPointerMove);
  stack.addEventListener("pointerup", onPointerUp);
  stack.addEventListener("pointercancel", onPointerCancel);
  root.addEventListener("keydown", onKeyDown);

  layout();
})();
