# PrediBol

Prototipo web móvil de PrediBol: trivia boliviana, pulso de hinchadas y secciones de actualidad.

## Estado actual

Esta entrega es una **demo web/PWA**, no una aplicación Android publicada ni un APK/AAB listo para Play Store.

- Trivia de demostración con banco de 60 preguntas incluidas en el código.
- Cada ronda intenta usar tres categorías diferentes, alterna la dificultad y mezcla las alternativas manteniendo correcta la respuesta.
- Evita las últimas 9 preguntas seleccionadas en este teléfono (la selección local cuenta al generar una ronda).
- Votos SÍ/NO por equipo guardados localmente en el teléfono.
- Puntos y estadísticas locales; no se sincronizan entre usuarios.
- Actualidad se alimenta mediante un flujo RSS programado (GitHub Actions), actualmente con EL DEBER y BBC Mundo. El resumen se refresca cada 30 minutos con EL DEBER y BBC Mundo; titulares de deportes se clasifican por palabras clave. Si las fuentes fallan, se conserva el archivo anterior. La automatización necesita que GitHub Actions esté habilitado y que su primera ejecución termine correctamente.
- Los datos del partido y las cifras de ejemplo no son resultados oficiales ni encuestas reales.
- No hay cuentas, servidor, ranking nacional ni moderación central.

## Probar localmente

Abrir `index.html` en un navegador. Algunas funciones PWA, como el service worker, requieren servir la carpeta mediante HTTPS o localhost.

## Publicar como sitio

El repositorio incluye un flujo de GitHub Pages. En GitHub, abrir **Settings → Pages** y seleccionar **GitHub Actions** como fuente. Cuando el flujo termine, GitHub mostrará la dirección del sitio.

## Próximos pasos antes de Google Play

1. Crear un backend seguro para cuentas, votos, puntos y ranking compartido.
2. Conectar fuentes verificables y actualizar automáticamente noticias y preguntas, con validación y control de repeticiones.
3. Crear el envoltorio Android (por ejemplo, Capacitor), definir el identificador de paquete y probar en varios teléfonos.
4. Preparar y firmar el Android App Bundle (.aab), completar la ficha de Play Console y cumplir sus políticas.
5. Probar privacidad, seguridad, accesibilidad y funcionamiento sin conexión.

**No subir esta demo a Play Store como si ya tuviera funciones en vivo o multijugador.**