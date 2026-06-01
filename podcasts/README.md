# Podcasts del temario

Audios MP3/M4A generados a partir de los apuntes en `temario/`, leídos en español de España con voz neutra. Pensados para repasar mientras vas al trabajo, paseas o haces deporte.

## Voz y velocidad
- **Voz:** Mónica (es_ES) — voz nativa de macOS, femenina neutra.
- **Velocidad:** 200 palabras por minuto (ritmo de estudio cómodo).
- **Formato:** MP3 (compatible con cualquier reproductor/coche/móvil).

## Duraciones

| Tema | Duración | Tamaño |
|---|---|---|
| `tema-00-overview.mp3` | 8 min | 2 MB |
| `tema-01-actividad-comercial.mp3` | 41 min | 10 MB |
| `tema-02-plan-igualdad.mp3` | 29 min | 7 MB |
| `tema-03-cultura-seguridad.mp3` | 17 min | 4 MB |
| `tema-04-experiencia-cliente.mp3` | 26 min | 6 MB |
| `tema-05-conocimientos-ferroviarios.mp3` | 44 min | 11 MB |
| **Total** | **~2 h 45 min** | **~40 MB** |

## Cómo regenerarlos

Si modificas un tema en `temario/` y quieres regenerar el audio:

```bash
cd podcasts
python3 generate_podcasts.py
```

Esto vuelve a procesar todos los `.md` de `temario/`, limpia el markdown (quita `#`, `*`, `|`, etc.), expande siglas (AVE → "A V E", FIP → "F I P", etc.) para que la voz las pronuncie bien, y genera los `.mp3`.

## Cómo escucharlos en el móvil

- **iPhone:** arrastra los `.mp3` a Apple Music o a la app Archivos. También puedes subirlos a Drive/Dropbox y escucharlos desde allí.
- **Android:** los `.mp3` se reproducen nativamente con la app de música/podcasts.
- **Como podcast propio:** súbelos a una app tipo AntennaPod, Podcast Addict o Pocket Casts apuntando a la URL raw de GitHub.

## Notas

- Las **siglas y acrónimos** se han transformado para que Mónica los pronuncie deletreados (`AVE` → "A V E", `ETCS` → "E T C S", `RFIG` → "Red Ferroviaria de Interés General", etc.). Esto hace el audio mucho más natural y entendible.
- Las **tablas** se leen fila por fila como prosa.
- Los **emojis y símbolos** (📸, ⭐, →, ≥, etc.) se eliminan o sustituyen por palabras.
