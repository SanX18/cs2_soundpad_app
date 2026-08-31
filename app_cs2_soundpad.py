import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import os
import sys
import subprocess
from flask import Flask, request
import logging
from datetime import datetime

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

servidor_flask = Flask(__name__)
app_instance = None

kills_anteriores = -1
kills_objetivo = 1
indice_audio = 1
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

def reproducir_sonido():
    try:
        comando = f'"{ruta_soundpad}" -rc "DoPlaySound({indice_audio})"'
        log_msg(f"Ejecutando Soundpad: Audio #{indice_audio}")
        subprocess.Popen(comando, shell=True)
        log_msg("✅ Audio enviado a Soundpad exitosamente.")
    except Exception as e:
        log_msg(f"❌ Error al reproducir en Soundpad: {e}")

@servidor_flask.route('/', methods=['POST'])
def recibir_datos():
    global kills_anteriores, kills_objetivo
    data = request.get_json()
    
    if data:
        if 'player' in data and 'match_stats' in data['player']:
            kills_actuales = data['player']['match_stats'].get('kills', 0)
            
            if kills_anteriores == -1:
                kills_anteriores = kills_actuales
                log_msg(f"📡 Conectado con CS2. Kills iniciales en la partida: {kills_actuales}")
                
            if kills_actuales > kills_anteriores:
                log_msg(f"💥 ¡Baja detectada! Kills totales: {kills_actuales}")
                if kills_actuales % kills_objetivo == 0:
                    log_msg(f"🎯 Meta de {kills_objetivo} kills alcanzada.")
                    reproducir_sonido()
                kills_anteriores = kills_actuales
    return 'OK', 200

def ejecutar_servidor():
    log_msg("✅ Servidor escuchando al CS2 en puerto 3000.")
    servidor_flask.run(port=3000)

class Aplicacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        global app_instance
        app_instance = self
        
        self.title("CS2 Soundpad Auto-Caster")
        self.geometry("450x650")
        self.resizable(False, False)
        
        try:
            self.iconbitmap(resource_path("app_icon.ico"))
        except Exception:
            pass
        
        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(15, 5))
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="CS2 Soundpad Caster", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_title.pack()
        
        # --- SETTINGS FRAME ---
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=20, fill="both")
        
        self.lbl_kills = ctk.CTkLabel(self.settings_frame, text="🎯 ¿Cada cuántas Kills suena el audio?", font=ctk.CTkFont(weight="bold"))
        self.lbl_kills.pack(pady=(10, 0))
        self.entry_kills = ctk.CTkEntry(self.settings_frame, justify="center", width=80)
        self.entry_kills.insert(0, "1")
        self.entry_kills.pack(pady=(0, 10))
        
        self.lbl_audio = ctk.CTkLabel(self.settings_frame, text="🎵 Número de Audio en Soundpad:", font=ctk.CTkFont(weight="bold"))
        self.lbl_audio.pack()
        self.entry_audio = ctk.CTkEntry(self.settings_frame, justify="center", width=80)
        self.entry_audio.insert(0, "1")
        self.entry_audio.pack(pady=(0, 10))
        
        self.lbl_ruta = ctk.CTkLabel(self.settings_frame, text="📂 Ruta de Soundpad.exe:", font=ctk.CTkFont(weight="bold"))
        self.lbl_ruta.pack()
        self.ruta_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.ruta_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.entry_ruta = ctk.CTkEntry(self.ruta_frame, justify="left")
        self.entry_ruta.insert(0, ruta_soundpad)
        self.entry_ruta.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_buscar = ctk.CTkButton(self.ruta_frame, text="📁", width=40, command=self.buscar_soundpad)
        self.btn_buscar.pack(side="right")

        # --- ACTIONS ---
        self.btn_cfg = ctk.CTkButton(self, text="⚙️ 1. Instalar CFG en CS2", fg_color="#d35400", hover_color="#e67e22", command=self.instalar_cfg)
        self.btn_cfg.pack(pady=(5, 5), padx=40, fill="x")
        
        self.btn_iniciar = ctk.CTkButton(self, text="🚀 2. INICIAR APP", fg_color="#27ae60", hover_color="#2ecc71", font=ctk.CTkFont(size=14, weight="bold"), command=self.iniciar_app)
        self.btn_iniciar.pack(pady=5, padx=40, fill="x")
        
        # --- LOGS BOX ---
        self.log_box = ctk.CTkTextbox(self, height=140, state="disabled", font=ctk.CTkFont(size=11, family="Consolas"))
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)
        self.escribir_log("Aplicación lista. Esperando configuración...")
        
        self.servidor_iniciado = False

    def escribir_log(self, mensaje):
        hora = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{hora}] {mensaje}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

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
            self.escribir_log("✅ CFG instalado con éxito en la carpeta seleccionada.")
        except Exception as e:
            self.escribir_log(f"❌ Error instalando CFG: {e}")

    def iniciar_app(self):
        global kills_objetivo, indice_audio, ruta_soundpad
        try:
            kills_objetivo = int(self.entry_kills.get())
            indice_audio = int(self.entry_audio.get())
            ruta_soundpad = self.entry_ruta.get()
        except ValueError:
            self.escribir_log("❌ Error: Kills y Audio deben ser números.")
            return

        if not self.servidor_iniciado:
            hilo = threading.Thread(target=ejecutar_servidor, daemon=True)
            hilo.start()
            self.servidor_iniciado = True
            self.escribir_log("⏳ ESCUCHANDO PARTIDA...")
            self.btn_iniciar.configure(text="🔄 ACTUALIZAR AJUSTES")
        else:
            self.escribir_log("✅ Configuración actualizada.")

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
