// --- UNIFICACIÓN DE SCROLL (NAVBAR + PARALLAX + WHATSAPP) ---
window.addEventListener("scroll", function() {
    const navbar = document.querySelector(".navbar");
    const hero = document.querySelector(".hero");
    const waButton = document.getElementById("wha-button"); // Variable corregida
    let offset = window.scrollY;

    // 1. Control de Navbar
    if (navbar) {
        navbar.classList.toggle("scrolled", offset > 50);
    }

    // 2. Parallax en Hero
    if (hero) {
        hero.style.backgroundPositionY = (offset * 0.5) + "px";
    }

    // 3. Botón WhatsApp Minimalista
    if (waButton) {
        if (offset > 300) {
            waButton.classList.add("show");
        } else {
            waButton.classList.remove("show");
        }
    }
});

// --- MENÚ MÓVIL ---
const toggle = document.getElementById("menu-toggle");
const navLinks = document.getElementById("nav-links");

if (toggle && navLinks) {
    toggle.addEventListener("click", () => {
        navLinks.classList.toggle("active");
    });
}

// --- ANIMACIÓN DE ELEMENTOS (REVEAL) ---
const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("active"); // Activa la animación
        }
    });
}, { threshold: 0.1 });

// Aplicar a todo lo que tenga clase 'reveal'
document.querySelectorAll(".reveal").forEach(el => observer.observe(el));

function actualizarEstadoHorario() {
    const elemento = document.getElementById("estado-horario");
    if (!elemento) return; 

    const ahora = new Date();
    const dia = ahora.getDay(); 
    const horaActual = ahora.getHours() + (ahora.getMinutes() / 60);
    
    let abierto = false;

    // Lunes(1) y Martes(2) cierran a las 10 PM (22)
    // Miércoles(3) a Domingo(0) cierran a las 11 PM (23)
    if (dia === 1 || dia === 2) {
        if (horaActual >= 8.5 && horaActual < 22) abierto = true;
    } else {
        if (horaActual >= 8.5 && horaActual < 23) abierto = true;
    }

    if (abierto) {
        elemento.innerHTML = "<span style='color: #25d366;'>🟢 ¡ESTAMOS ABIERTOS! Pasa por tu café</span>";
    } else {
        elemento.innerHTML = "<span style='color: #ff4d4d;'>🔴 CERRADO POR AHORA. Te esperamos mañana</span>";
    }
}

// Ejecutar al cargar la página
document.addEventListener("DOMContentLoaded", actualizarEstadoHorario);
// Ejecutar de nuevo a los 500ms por si el HTML tardó en renderizar
setTimeout(actualizarEstadoHorario, 500);

const mobileMenu = document.getElementById('mobile-menu');

mobileMenu.addEventListener('click', () => {
    // Esta línea quita o pone la clase 'active' cada vez que haces clic
    navLinks.classList.toggle('active');
});