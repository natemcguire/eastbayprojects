const menuButton = document.querySelector(".menu-toggle");
const mobileNav = document.querySelector("#mobile-nav");
if (menuButton && mobileNav) {
  const closeMenu = () => {
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.textContent = "Menu +";
    mobileNav.hidden = true;
  };
  menuButton.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") !== "true";
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.textContent = open ? "Close −" : "Menu +";
    mobileNav.hidden = !open;
  });
  mobileNav
    .querySelectorAll("a")
    .forEach((link) => link.addEventListener("click", closeMenu));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !mobileNav.hidden) {
      closeMenu();
      menuButton.focus();
    }
  });
  matchMedia("(min-width: 601px)").addEventListener("change", (event) => {
    if (event.matches) closeMenu();
  });
}

const filters = document.querySelector("[data-work-filters]");
if (filters) {
  filters.hidden = false;
  const projects = [...document.querySelectorAll("[data-project-category]")];
  filters.querySelectorAll("button").forEach((button) =>
    button.addEventListener("click", () => {
      filters
        .querySelectorAll("button")
        .forEach((item) =>
          item.setAttribute("aria-pressed", String(item === button)),
        );
      const category = button.dataset.filter;
      projects.forEach((project) => {
        project.hidden =
          category !== "all" && project.dataset.projectCategory !== category;
      });
      const additionalWork = document.querySelector("[data-additional-work]");
      if (additionalWork)
        additionalWork.hidden = category !== "all" && category !== "websites";
      const count = projects.filter((project) => !project.hidden).length;
      document.querySelector("[data-work-count]").textContent =
        `${count} ${count === 1 ? "project" : "projects"}`;
    }),
  );
}
