// ========================================
// MOBILE MENU TOGGLE
// ========================================

document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menuToggle")
  const mainNav = document.getElementById("mainNav")

  if (menuToggle && mainNav) {
    menuToggle.addEventListener("click", () => {
      menuToggle.classList.toggle("active")
      mainNav.classList.toggle("active")
    })

    // Close menu when clicking outside
    document.addEventListener("click", (event) => {
      const isClickInsideNav = mainNav.contains(event.target)
      const isClickOnToggle = menuToggle.contains(event.target)

      if (!isClickInsideNav && !isClickOnToggle && mainNav.classList.contains("active")) {
        menuToggle.classList.remove("active")
        mainNav.classList.remove("active")
      }
    })

    // Close menu when clicking on a link
    const navLinks = mainNav.querySelectorAll(".nav-link")
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        menuToggle.classList.remove("active")
        mainNav.classList.remove("active")
      })
    })
  }

  // ========================================
  // ACCORDION FUNCTIONALITY
  // ========================================

  const accordionHeaders = document.querySelectorAll(".accordion-header")

  accordionHeaders.forEach((header) => {
    header.addEventListener("click", function () {
      const accordionItem = this.parentElement
      const isActive = accordionItem.classList.contains("active")

      // Close all accordion items
      document.querySelectorAll(".accordion-item").forEach((item) => {
        item.classList.remove("active")
      })

      // Open clicked item if it wasn't active
      if (!isActive) {
        accordionItem.classList.add("active")
      }
    })
  })

  // ========================================
  // SMOOTH SCROLL FOR ANCHOR LINKS
  // ========================================

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href")

      // Skip if it's just "#"
      if (href === "#") {
        e.preventDefault()
        return
      }

      const target = document.querySelector(href)

      if (target) {
        e.preventDefault()
        const headerOffset = 100
        const elementPosition = target.getBoundingClientRect().top
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset

        window.scrollTo({
          top: offsetPosition,
          behavior: "smooth",
        })
      }
    })
  })

  // ========================================
  // FORM VALIDATION (LOGIN)
  // ========================================

  const loginForm = document.getElementById("loginForm")

  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault()

      const email = document.getElementById("email").value
      const password = document.getElementById("password").value

      // Basic validation
      if (!email || !password) {
        alert("Por favor, preencha todos os campos.")
        return
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(email)) {
        alert("Por favor, insira um e-mail válido.")
        return
      }

      // Here you would typically send the data to your backend
      console.log("Login attempt:", { email, password })
      alert("Funcionalidade de login será implementada no backend.")
    })
  }

  // ========================================
  // FADE IN ANIMATION ON SCROLL
  // ========================================

  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1"
        entry.target.style.transform = "translateY(0)"
      }
    })
  }, observerOptions)

  // Observe course and category cards
  document.querySelectorAll(".course-card, .category-card").forEach((card) => {
    card.style.opacity = "0"
    card.style.transform = "translateY(20px)"
    card.style.transition = "opacity 0.5s ease, transform 0.5s ease"
    observer.observe(card)
  })

  // ========================================
  // HEADER SHADOW ON SCROLL
  // ========================================

  const header = document.querySelector(".header")

  window.addEventListener("scroll", () => {
    if (window.scrollY > 10) {
      header.style.boxShadow = "0 4px 6px rgba(0, 0, 0, 0.1)"
    } else {
      header.style.boxShadow = "0 1px 3px rgba(0, 0, 0, 0.1)"
    }
  })
})
