(() => {
  const root = document.querySelector("[data-info-steps]");
  if (!root) return;

  const reveal = () => {
    requestAnimationFrame(() => {
      root.classList.add("is-inview");
    });
  };

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    reveal();
    return;
  }

  if (!("IntersectionObserver" in window)) {
    reveal();
    return;
  }

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        reveal();
        io.disconnect();
      });
    },
    { threshold: 0.2, rootMargin: "0px 0px -4% 0px" }
  );

  io.observe(root);
})();
