import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import os
import sys
import subprocess
import requests
import json
import tempfile
import time
from flask import Flask, request
import logging
from datetime import datetime

CURRENT_VERSION = "v1.6.4"
REPO = "SanX18/cs2_soundpad_app"

appdata = os.environ.get('APPDATA')
if not appdata:
    appdata = os.path.expanduser('~')
APP_DATA_DIR = os.path.join(appdata, 'CS2SoundpadCaster')
CONFIG_FILE = os.path.join(APP_DATA_DIR, 'config.json')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

servidor_flask = Flask(__name__)
app_instance = None

kills_anteriores = -1
reglas_activas = []
ruta_soundpad = r"C:\Program Files (x86)\Steam\steamapps\common\Soundpad\Soundpad.exe"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def log_msg(mensaje):
    if app_instance:
        app_instance.escribir_log(mensaje)

def reproducir_sonido(carpeta, audio):
    try:
        if carpeta > 0:
            comando = f'"{ruta_soundpad}" -rc "DoPlaySoundFromCategory({carpeta}, {audio})"'
            log_msg(f"▶️ Soundpad: Carpeta {carpeta}, Audio #{audio}")
        else:
            comando = f'"{ruta_soundpad}" -rc "DoPlaySound({audio})"'
            log_msg(f"▶️ Soundpad: Audio Global #{audio}")
            
        subprocess.Popen(comando, shell=True)
    except Exception as e:
        log_msg(f"❌ Error al reproducir en Soundpad: {e}")

@servidor_flask.route('/', methods=['POST'])
def recibir_datos():
    global kills_anteriores
    data = request.get_json()
    
    if data and 'player' in data and 'match_stats' in data['player']:
        kills_actuales = data['player']['match_stats'].get('kills', 0)
        
        if kills_anteriores == -1:
            kills_anteriores = kills_actuales
            log_msg(f"📡 Conectado con CS2. Kills actuales: {kills_actuales}")
            
        # FIX: Detectar si el usuario reinicia el mapa o la partida (los kills bajan a 0)
        if kills_actuales < kills_anteriores:
            log_msg(f"🔄 Reinicio de mapa detectado. Reseteando contador a {kills_actuales} kills.")
            kills_anteriores = kills_actuales
            
        elif kills_actuales > kills_anteriores:
            log_msg(f"💥 ¡Baja detectada! Kills totales: {kills_actuales}")
            
            if reglas_activas:
                max_kills_ciclo = max(r['kills'] for r in reglas_activas)
                kill_en_ciclo = ((kills_actuales - 1) % max_kills_ciclo) + 1
                
                log_msg(f"🔄 Posición en el ciclo de rachas (1-{max_kills_ciclo}): Baja nº {kill_en_ciclo}")
                
                for regla in reglas_activas:
                    if kill_en_ciclo == regla['kills']:
                        log_msg(f"🎯 Activando sonido para la baja {regla['kills']}.")
                        reproducir_sonido(regla['folder'], regla['audio'])
                        break
                        
            kills_anteriores = kills_actuales
    return 'OK', 200

def ejecutar_servidor():
    log_msg("✅ Servidor escuchando en puerto 3000.")
    servidor_flask.run(port=3000)

def comprobar_actualizaciones():
    try:
        log_msg("🔍 Comprobando si hay actualizaciones...")
        response = requests.get(f"https://api.github.com/repos/{REPO}/releases/latest", timeout=5)
        response.raise_for_status()
        data = response.json()
        latest_version = data.get("tag_name")
        
        if latest_version and latest_version != CURRENT_VERSION:
            if latest_version > CURRENT_VERSION:
                log_msg(f"✨ ¡Nueva versión encontrada! ({latest_version})")
                app_instance.after(1000, lambda: app_instance.preguntar_actualizacion(data))
            else:
                log_msg("✅ Tienes la última versión.")
        else:
            log_msg("✅ Tienes la última versión.")
    except Exception as e:
        log_msg(f"⚠️ No se pudo comprobar actualizaciones: {e}")

class Aplicacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        global app_instance
        app_instance = self
        
        self.title(f"CS2 Soundpad Auto-Caster {CURRENT_VERSION}")
        self.geometry("460x720")
        self.resizable(False, False)
        
        try:
            self.iconbitmap(resource_path("app_icon.ico"))
        except Exception:
            pass
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(15, 5))
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="CS2 Soundpad Caster", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_title.pack()
        self.lbl_subtitle = ctk.CTkLabel(self.header_frame, text="Configura múltiples audios según tus kills", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_subtitle.pack()
        
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=15, fill="both")
        
        self.rows_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.rows_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(self.rows_frame, text="Cada X Kills", width=90, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(self.rows_frame, text="Nº Carpeta", width=90, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(self.rows_frame, text="Nº Audio", width=90, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)
        
        self.rule_entries = []
        for i in range(5):
            ek = ctk.CTkEntry(self.rows_frame, width=90, justify="center", placeholder_text="-")
            ek.grid(row=i+1, column=0, padx=5, pady=3)
            ek.insert(0, str(i+1))
            
            ec = ctk.CTkEntry(self.rows_frame, width=90, justify="center", placeholder_text="(Opcional)")
            ec.grid(row=i+1, column=1, padx=5, pady=3)
            
            ea = ctk.CTkEntry(self.rows_frame, width=90, justify="center", placeholder_text="-")
            ea.grid(row=i+1, column=2, padx=5, pady=3)
            
            self.rule_entries.append((ek, ec, ea))
        
        self.lbl_ruta = ctk.CTkLabel(self.settings_frame, text="📂 Ruta de Soundpad.exe:", font=ctk.CTkFont(weight="bold"))
        self.lbl_ruta.pack()
        self.ruta_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.ruta_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.entry_ruta = ctk.CTkEntry(self.ruta_frame, justify="left")
        self.entry_ruta.insert(0, ruta_soundpad)
        self.entry_ruta.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_buscar = ctk.CTkButton(self.ruta_frame, text="📁", width=40, command=self.buscar_soundpad)
        self.btn_buscar.pack(side="right")

        self.btn_cfg = ctk.CTkButton(self, text="⚙️ 1. Instalar CFG en CS2", fg_color="#d35400", hover_color="#e67e22", command=self.instalar_cfg)
        self.btn_cfg.pack(pady=(5, 5), padx=40, fill="x")
        
        self.btn_iniciar = ctk.CTkButton(self, text="🚀 2. INICIAR / GUARDAR", fg_color="#27ae60", hover_color="#2ecc71", font=ctk.CTkFont(size=14, weight="bold"), command=self.iniciar_app)
        self.btn_iniciar.pack(pady=5, padx=40, fill="x")
        
        self.log_box = ctk.CTkTextbox(self, height=120, state="disabled", font=ctk.CTkFont(size=11, family="Consolas"))
        self.log_box.pack(pady=10, padx=15, fill="both", expand=True)
        self.escribir_log(f"Aplicación {CURRENT_VERSION} lista.")
        
        self.servidor_iniciado = False
        
        self.cargar_config()
        
        threading.Thread(target=comprobar_actualizaciones, daemon=True).start()

    def escribir_log(self, mensaje):
        hora = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{hora}] {mensaje}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def cargar_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "ruta_soundpad" in data:
                    self.entry_ruta.delete(0, ctk.END)
                    self.entry_ruta.insert(0, data["ruta_soundpad"])
                    
                reglas_guardadas = data.get("reglas", [])
                for i in range(min(5, len(reglas_guardadas))):
                    r = reglas_guardadas[i]
                    
                    self.rule_entries[i][0].delete(0, ctk.END)
                    if r.get("kills"): self.rule_entries[i][0].insert(0, r["kills"])
                    
                    self.rule_entries[i][1].delete(0, ctk.END)
                    if r.get("folder"): self.rule_entries[i][1].insert(0, r["folder"])
                    
                    self.rule_entries[i][2].delete(0, ctk.END)
                    if r.get("audio"): self.rule_entries[i][2].insert(0, r["audio"])
                    
                self.escribir_log("📂 Configuración anterior cargada.")
            except Exception as e:
                self.escribir_log(f"⚠️ No se pudo cargar config: {e}")

    def guardar_config(self):
        try:
            if not os.path.exists(APP_DATA_DIR):
                os.makedirs(APP_DATA_DIR)
                
            data = {
                "ruta_soundpad": self.entry_ruta.get(),
                "reglas": []
            }
            
            for ek, ec, ea in self.rule_entries:
                data["reglas"].append({
                    "kills": ek.get().strip(),
                    "folder": ec.get().strip(),
                    "audio": ea.get().strip()
                })
                
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                
            self.escribir_log("💾 Configuración guardada correctamente.")
        except Exception as e:
            self.escribir_log(f"⚠️ Error guardando config: {e}")

    def preguntar_actualizacion(self, release_data):
        latest_version = release_data.get("tag_name")
        assets = release_data.get("assets", [])
        download_url = None
        for asset in assets:
            if asset["name"].endswith(".exe"):
                download_url = asset["browser_download_url"]
                break
                
        if not download_url:
            return
            
        respuesta = messagebox.askyesno("¡Nueva Actualización!", f"Se ha encontrado la versión {latest_version}.\n\n¿Quieres descargarla e instalarla automáticamente ahora?")
        if respuesta:
            threading.Thread(target=self.realizar_actualizacion, args=(download_url,), daemon=True).start()

    def realizar_actualizacion(self, download_url):
        try:
            self.escribir_log("⬇️ Iniciando descarga de la actualización...")
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            temp_dir = tempfile.gettempdir()
            temp_exe = os.path.join(temp_dir, f"cs2_update_{int(time.time())}.exe")
            bat_path = os.path.join(temp_dir, "updater_cs2.bat")
            
            self.escribir_log(f"📂 Guardando archivo temporal...")
            with open(temp_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.escribir_log("✅ Descarga completada. Preparando instalación...")
            
            if not getattr(sys, 'frozen', False):
                self.escribir_log("⚠️ Modo desarrollador: Cancelando (solo funciona en .exe).")
                return

            my_exe = sys.executable
            
            bat_content = f"""@echo off\ntimeout /t 2 /nobreak > NUL\ndel "{my_exe}"\ncopy /y "{temp_exe}" "{my_exe}"\nexplorer "{my_exe}"\ndel "%~f0"\n"""
            with open(bat_path, "w") as f:
                f.write(bat_content)
                
            self.escribir_log("🚀 Ejecutando instalador y cerrando app vieja...")
            subprocess.Popen(bat_path, shell=True)
            sys.exit(0)
            
        except Exception as e:
            self.escribir_log(f"❌ Error al actualizar: {e}")

    def buscar_soundpad(self):
        ruta = filedialog.askopenfilename(title="Selecciona Soundpad.exe", filetypes=[("Ejecutables", "*.exe")])
        if ruta:
            self.entry_ruta.delete(0, ctk.END)
            self.entry_ruta.insert(0, ruta)

    def instalar_cfg(self):
        ruta_cs2 = filedialog.askdirectory(title="Selecciona la carpeta 'cfg' de CS2 (csgo/cfg)")
        if not ruta_cs2:
            return
        contenido_cfg = """"Soundpad App"\n{\n    "uri" "http://localhost:3000"\n    "timeout" "5.0"\n    "buffer"  "0.1"\n    "throttle" "0.1"\n    "heartbeat" "10.0"\n    "data"\n    {\n        "provider"            "1"\n        "player_match_stats"  "1"\n    }\n}"""
        try:
            ruta_archivo = os.path.join(ruta_cs2, "gamestate_integration_soundpad.cfg")
            with open(ruta_archivo, "w") as f:
                f.write(contenido_cfg)
            self.escribir_log("✅ CFG instalado con éxito.")
        except Exception as e:
            self.escribir_log(f"❌ Error instalando CFG: {e}")

    def iniciar_app(self):
        global reglas_activas, ruta_soundpad
        
        ruta_soundpad = self.entry_ruta.get()
        nuevas_reglas = []
        
        for ek, ec, ea in self.rule_entries:
            v_k = ek.get().strip()
            v_a = ea.get().strip()
            v_c = ec.get().strip()
            
            if v_k and v_a:
                try:
                    rk = int(v_k)
                    ra = int(v_a)
                    rc = int(v_c) if v_c else 0
                    nuevas_reglas.append({'kills': rk, 'folder': rc, 'audio': ra})
                except ValueError:
                    self.escribir_log("❌ Error: Kills y Audio deben ser números enteros.")
                    return
                    
        if not nuevas_reglas:
            self.escribir_log("❌ Error: Tienes que rellenar al menos una regla válida.")
            return
            
        nuevas_reglas.sort(key=lambda x: x['kills'], reverse=True)
        reglas_activas = nuevas_reglas
        
        self.guardar_config()
        
        self.escribir_log(f"✅ {len(reglas_activas)} reglas cargadas.")

        if not self.servidor_iniciado:
            hilo = threading.Thread(target=ejecutar_servidor, daemon=True)
            hilo.start()
            self.servidor_iniciado = True
            self.escribir_log("⏳ ESCUCHANDO PARTIDA...")

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
