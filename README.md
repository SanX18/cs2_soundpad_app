# CS2 Soundpad Auto-Caster 🎮🔊

Automate Soundpad audio playback based on your Counter-Strike 2 in-game stats! 

This desktop application connects Counter-Strike 2 with Soundpad using Valve's official Game State Integration (GSI). It allows you to automatically play sounds from your Soundpad library every time you reach a specific kill count in a match, broadcasting it directly to your teammates via the in-game voice chat.

## 🛡️ 100% VACNET & Steam Ban Safe

This project is **completely safe, legal, and will NOT cause VAC or VACNet bans**. 
* **Official GSI:** It does NOT read game memory or inject any code/DLLs into `cs2.exe`. It strictly uses Valve's official Game State Integration system, which is explicitly provided by Valve for developers (used by tournament HUDs, Razer/SteelSeries RGB software, etc.).
* **Audio Routing:** It triggers Soundpad, which operates entirely at the Windows audio driver level.

## ⚠️ Requirements
* **Counter-Strike 2**
* **Soundpad** (You **MUST** have the Soundpad application installed, available on Steam or their official website).

## 🚀 Features
* Easy-to-use graphical interface.
* 1-Click auto-installation of the GSI `.cfg` file into your CS2 folder.
* Runs lightweight in the background.

## ⚙️ How to Use (For Users)
1. Go to the **Releases** tab on the right side of this repository and download `app_cs2_soundpad.exe`.
2. Open the application.
3. Click **"1. Instalar CFG en CS2"** and select your CS2 `cfg` folder (usually located at `C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg`).
4. Set the number of kills required to trigger the sound.
5. Set the **Sound Index** (the number displayed next to your sound in the Soundpad list).
6. **Crucial Soundpad Setup:** In Soundpad, go to *Preferences > Hotkeys > Auto Keys*. Add the exact same key you use for voice chat in CS2 (e.g., 'K' or 'V'). This makes Soundpad press your Push-To-Talk button automatically!
7. Click **"2. INICIAR APP"** and launch CS2.

## 🛠️ For Developers (Source Code)
If you want to run the python script yourself:
```bash
pip install flask
python app_cs2_soundpad.py
```
To compile it into an executable:
```bash
pyinstaller --noconsole --onefile app_cs2_soundpad.py
```
