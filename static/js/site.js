(() => {
  const button = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".main-navigation");
  if (!button || !nav) return;
  const closeMenu = () => {
    button.setAttribute("aria-expanded", "false");
    nav.classList.remove("is-open");
  };
  button.addEventListener("click", () => {
    const open = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("is-open", open);
  });
  nav.addEventListener("click", event => {
    if (event.target.closest("a")) closeMenu();
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape") closeMenu();
  });
  document.addEventListener("click", event => {
    if (!nav.contains(event.target) && !button.contains(event.target)) closeMenu();
  });
})();
