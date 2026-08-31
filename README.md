# CS2 Soundpad Auto-Caster

¡Automatiza sonidos de Soundpad basados en tus estadísticas de Counter-Strike 2!

Esta aplicación de escritorio conecta Counter-Strike 2 con Soundpad mediante la integración oficial de Valve (Game State Integration). Te permite reproducir automáticamente sonidos configurados en tu Soundpad cada vez que alcanzas una cierta cantidad de bajas (kills) en el juego.

## 🛡️ 100% VAC Safe (Libre de Baneos)

Este proyecto es **completamente seguro y legal**. NO produce baneos por VAC (Valve Anti-Cheat) por las siguientes razones:

1. **Usa GSI (Game State Integration):** No lee la memoria del juego ni inyecta código (DLLs). Utiliza un sistema oficial creado por la propia Valve para que los desarrolladores puedan extraer estadísticas en vivo (usado en torneos, teclados RGB y aplicaciones de estadísticas).
2. **Interacción con Soundpad segura:** Soundpad funciona a nivel de los drivers de audio de Windows. Nunca interactúa ni modifica el proceso de `cs2.exe`.

## 🚀 Características
* Interfaz gráfica fácil de usar.
* Auto-instalación del archivo GSI `.cfg` en tu carpeta de CS2.
* No requiere modificar archivos del juego manualmente.
* Se ejecuta en segundo plano consumiendo muy pocos recursos.

## ⚙️ Cómo usarlo
1. Ejecuta `app_cs2_soundpad.py` o el ejecutable compilado.
2. Haz clic en **"1. Instalar CFG en CS2"** e indica la carpeta `cfg` de tu CS2 (normalmente `steamapps/common/Counter-Strike Global Offensive/game/csgo/cfg`).
3. Configura cada cuántas Kills quieres que suene el audio.
4. Indica el índice del sonido de Soundpad (el número a la izquierda en tu lista de Soundpad).
5. Configura Soundpad: Activa las **Teclas Automáticas** (Auto Keys) en Preferencias para que pulse tu botón de chat de voz del CS2.
6. Dale a **INICIAR APP**.

## 🛠️ Requisitos para código fuente
* Python 3.x
* Flask (`pip install flask`)
* Soundpad instalado y configurado
