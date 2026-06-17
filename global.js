document.addEventListener("DOMContentLoaded", () => {
    // 1. Mobile Menu Toggle
    const mobileMenuButton = document.getElementById("mobile-menu-button");
    const mobileMenu = document.getElementById("mobile-menu");

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener("click", (e) => {
            e.stopPropagation();
            mobileMenu.classList.toggle("hidden");
            
            // Toggle hamburger icon animation/state if needed
            const svgPath = mobileMenuButton.querySelector("svg path");
            if (svgPath) {
                if (mobileMenu.classList.contains("hidden")) {
                    svgPath.setAttribute("d", "M4 6h16M4 12h16M4 18h16");
                } else {
                    svgPath.setAttribute("d", "M6 18L18 6M6 6l12 12");
                }
            }
        });

        // Close mobile menu when clicking outside
        document.addEventListener("click", (e) => {
            if (!mobileMenu.classList.contains("hidden") && !mobileMenu.contains(e.target) && e.target !== mobileMenuButton) {
                mobileMenu.classList.add("hidden");
                const svgPath = mobileMenuButton.querySelector("svg path");
                if (svgPath) {
                    svgPath.setAttribute("d", "M4 6h16M4 12h16M4 18h16");
                }
            }
        });
    }

    // 2. Navigation Active Link Detection
    const currentPath = window.location.pathname;
    const pageName = currentPath.substring(currentPath.lastIndexOf('/') + 1) || "index.html";
    
    const navLinks = document.querySelectorAll("nav a");
    navLinks.forEach(link => {
        const linkHref = link.getAttribute("href");
        if (linkHref === pageName) {
            link.classList.add("nav-active");
        } else {
            link.classList.remove("nav-active");
        }
    });

    // 3. Page Reveal Transition
    document.body.style.opacity = "0";
    document.body.style.transition = "opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1)";
    requestAnimationFrame(() => {
        document.body.style.opacity = "1";
    });

    // 4. Scroll Reveal Animations (Intersection Observer)
    const fadeElements = document.querySelectorAll(".fade-in-scroll");
    
    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                
                // If it's a progress bar, animate its width
                const progressBar = entry.target.querySelector(".skill-progress-bar");
                if (progressBar) {
                    const targetWidth = progressBar.getAttribute("data-width") || "0%";
                    progressBar.style.width = targetWidth;
                }
                
                // Unobserve after showing
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    });

    fadeElements.forEach(el => {
        revealObserver.observe(el);
    });

    // 5. ESC Key to Close Modals
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            const openModals = document.querySelectorAll(".modal-open");
            openModals.forEach(modal => {
                const modalId = modal.id;
                const numericId = modalId.replace("projectDetail", "");
                if (typeof closeProject === "function") {
                    closeProject(numericId);
                }
            });
            
            // Close contact modal if open
            const contactModal = document.getElementById("successModal");
            if (contactModal && !contactModal.classList.contains("hidden")) {
                contactModal.classList.add("hidden");
            }
        }
    });
});
