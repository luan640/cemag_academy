(() => {
  "use strict";

  // Year in footer
  const yearEl = document.querySelectorAll("#year");
  const now = new Date();
  yearEl.forEach((el) => (el.textContent = String(now.getFullYear())));

  // Smooth scroll for internal anchors (ex: #sobre)
  document.addEventListener("click", (e) => {
    const a = e.target.closest("a[href^='#']");
    if (!a) return;

    const href = a.getAttribute("href");
    if (!href || href === "#") return;

    const target = document.querySelector(href);
    if (!target) return;

    e.preventDefault();
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  // Reveal on scroll (fade/slide)
  const revealEls = Array.from(document.querySelectorAll(".reveal"));
  if (revealEls.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add("is-visible");
        });
      },
      { threshold: 0.12 }
    );
    revealEls.forEach((el) => io.observe(el));
  }

  // Cursos: busca + filtros (apenas front)
  const grid = document.getElementById("coursesGrid");
  const emptyState = document.getElementById("emptyState");

  const searchInput = document.getElementById("courseSearch");
  const btnClearSearch = document.getElementById("btnClearSearch");

  const filterCategory = document.getElementById("filterCategory");
  const filterDuration = document.getElementById("filterDuration");
  const filterInstructor = document.getElementById("filterInstructor");

  function applyFilters() {
    if (!grid) return;

    const q = (searchInput?.value || "").trim().toLowerCase();
    const c = (filterCategory?.value || "").trim();
    const d = (filterDuration?.value || "").trim();
    const i = (filterInstructor?.value || "").trim();

    const items = Array.from(grid.querySelectorAll(".course-item"));
    let visibleCount = 0;

    items.forEach((item) => {
      const title = (item.dataset.title || "").toLowerCase();
      const cat = item.dataset.category || "";
      const dur = item.dataset.duration || "";
      const ins = item.dataset.instructor || "";

      const matchQ = !q || title.includes(q);
      const matchC = !c || cat === c;
      const matchD = !d || dur === d;
      const matchI = !i || ins === i;

      const show = matchQ && matchC && matchD && matchI;
      item.classList.toggle("d-none", !show);
      if (show) visibleCount += 1;
    });

    if (emptyState) {
      emptyState.classList.toggle("d-none", visibleCount !== 0);
    }
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }
  if (btnClearSearch) {
    btnClearSearch.addEventListener("click", () => {
      if (searchInput) searchInput.value = "";
      if (filterCategory) filterCategory.value = "";
      if (filterDuration) filterDuration.value = "";
      if (filterInstructor) filterInstructor.value = "";
      applyFilters();
    });
  }
  if (filterCategory) filterCategory.addEventListener("change", applyFilters);
  if (filterDuration) filterDuration.addEventListener("change", applyFilters);
  if (filterInstructor) filterInstructor.addEventListener("change", applyFilters);

  // Curso detalhes: expandir tudo (accordion)
  const btnExpandAll = document.getElementById("btnExpandAll");
  const lessonsAccordion = document.getElementById("lessonsAccordion");

  if (btnExpandAll && lessonsAccordion) {
    btnExpandAll.addEventListener("click", () => {
      const collapses = lessonsAccordion.querySelectorAll(".accordion-collapse");
      const allOpen = Array.from(collapses).every((c) => c.classList.contains("show"));

      collapses.forEach((c) => {
        // Bootstrap Collapse API (já no bundle)
        const instance = bootstrap.Collapse.getOrCreateInstance(c, { toggle: false });
        allOpen ? instance.hide() : instance.show();
      });

      btnExpandAll.textContent = allOpen ? "Expandir tudo" : "Recolher tudo";
    });
  }

  // Login: validação visual minimalista
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const email = document.getElementById("email");
      const password = document.getElementById("password");

      let ok = true;

      if (!email || !email.value || !/^\S+@\S+\.\S+$/.test(email.value)) {
        email?.classList.add("is-invalid");
        ok = false;
      } else {
        email.classList.remove("is-invalid");
      }

      if (!password || !password.value || password.value.length < 6) {
        password?.classList.add("is-invalid");
        ok = false;
      } else {
        password.classList.remove("is-invalid");
      }

      if (ok) {
        // Template: apenas demonstração (sem backend)
        window.location.href = "cursos.html";
      }
    });
  }
})();
