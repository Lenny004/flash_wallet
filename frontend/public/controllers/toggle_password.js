/**
 * Toggle mostrar/ocultar contraseña (script clásico, sin módulos).
 * Uso: data-toggle-password="#idDelInput" en el botón.
 */
(function () {
  function alternar(boton) {
    var selector = boton.getAttribute('data-toggle-password');
    var campo = selector ? document.querySelector(selector) : null;
    var icono = boton.querySelector('img');
    if (!campo) return;

    var mostrar = campo.type === 'password';
    campo.type = mostrar ? 'text' : 'password';

    if (icono) {
      icono.src = mostrar ? '/resources/icons/ver.png' : '/resources/icons/ocultar.png';
    }

    boton.setAttribute('aria-pressed', mostrar ? 'true' : 'false');
    boton.setAttribute('aria-label', mostrar ? 'Ocultar contraseña' : 'Mostrar contraseña');
  }

  function enlazar() {
    document.querySelectorAll('[data-toggle-password]').forEach(function (boton) {
      boton.addEventListener('click', function (evento) {
        evento.preventDefault();
        evento.stopPropagation();
        alternar(boton);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enlazar);
  } else {
    enlazar();
  }
})();
