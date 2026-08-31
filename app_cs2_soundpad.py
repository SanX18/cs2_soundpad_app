import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import os
import subprocess
from flask import Flask, request
import logging

# Ocultar los mensajes de la consola de Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

servidor_flask = Flask(__name__)

# --- VARIABLES GLOBALES ---
kills_anteriores = 0
kills_objetivo = 1
indice_audio = 1
ruta_soundpad = r"C:\Program Files (x86)\Steam\steamapps\common\Soundpad\Soundpad.exe"

def reproducir_sonido():
    try:
        comando = f'"{ruta_soundpad}" -rc "DoPlaySound({indice_audio})"'
        subprocess.Popen(comando, shell=True)
    except Exception as e:
        print(f"Error al reproducir: {e}")

@servidor_flask.route('/', methods=['POST'])
def recibir_datos():
    global kills_anteriores, kills_objetivo
    data = request.get_json()
    
    if data and 'player' in data and 'match_stats' in data['player']:
        kills_actuales = data['player']['match_stats'].get('kills', 0)
        
        if kills_actuales > kills_anteriores:
            if kills_actuales % kills_objetivo == 0 and kills_actuales != 0:
                reproducir_sonido()
            kills_anteriores = kills_actuales
            
    return 'OK', 200

def ejecutar_servidor():
    servidor_flask.run(port=3000)

# --- CONFIGURACIÓN UI MODERNA ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Aplicacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CS2 Soundpad Auto-Caster")
        self.geometry("400x550")
        self.resizable(False, False)
        
        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(20, 10))
        
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="CS2 Soundpad Caster", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_title.pack()
        
        self.lbl_subtitle = ctk.CTkLabel(self.header_frame, text="Automatiza tus clips de audio al hacer bajas", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_subtitle.pack()

        # --- SETTINGS FRAME ---
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Kills
        self.lbl_kills = ctk.CTkLabel(self.settings_frame, text="🎯 ¿Cada cuántas Kills suena el audio?", font=ctk.CTkFont(weight="bold"))
        self.lbl_kills.pack(pady=(15, 5))
        self.entry_kills = ctk.CTkEntry(self.settings_frame, justify="center", width=80)
        self.entry_kills.insert(0, "2")
        self.entry_kills.pack()
        
        # Audio Index
        self.lbl_audio = ctk.CTkLabel(self.settings_frame, text="🎵 Número de Audio en Soundpad:", font=ctk.CTkFont(weight="bold"))
        self.lbl_audio.pack(pady=(15, 5))
        self.entry_audio = ctk.CTkEntry(self.settings_frame, justify="center", width=80)
        self.entry_audio.insert(0, "1")
        self.entry_audio.pack()
        
        # Ruta Soundpad
        self.lbl_ruta = ctk.CTkLabel(self.settings_frame, text="📂 Ruta de Soundpad.exe:", font=ctk.CTkFont(weight="bold"))
        self.lbl_ruta.pack(pady=(15, 5))
        
        self.ruta_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.ruta_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.entry_ruta = ctk.CTkEntry(self.ruta_frame, justify="left")
        self.entry_ruta.insert(0, ruta_soundpad)
        self.entry_ruta.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_buscar = ctk.CTkButton(self.ruta_frame, text="📁", width=40, command=self.buscar_soundpad)
        self.btn_buscar.pack(side="right")

        # --- ACTIONS ---
        self.btn_cfg = ctk.CTkButton(self, text="⚙️ 1. Instalar CFG en CS2", fg_color="#d35400", hover_color="#e67e22", command=self.instalar_cfg)
        self.btn_cfg.pack(pady=(10, 5), padx=40, fill="x")
        
        self.btn_iniciar = ctk.CTkButton(self, text="🚀 2. INICIAR APP", fg_color="#27ae60", hover_color="#2ecc71", font=ctk.CTkFont(size=14, weight="bold"), command=self.iniciar_app)
        self.btn_iniciar.pack(pady=5, padx=40, fill="x", ipady=5)
        
        self.lbl_estado = ctk.CTkLabel(self, text="Estado: DETENIDO", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
        self.lbl_estado.pack(pady=(10, 20))
        
        self.servidor_iniciado = False

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
            messagebox.showinfo("Éxito", f"Archivo instalado correctamente en:\n{ruta_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el archivo:\n{e}")

    def iniciar_app(self):
        global kills_objetivo, indice_audio, ruta_soundpad
        
        try:
            kills_objetivo = int(self.entry_kills.get())
            indice_audio = int(self.entry_audio.get())
            ruta_soundpad = self.entry_ruta.get()
        except ValueError:
            messagebox.showerror("Error", "Los valores de Kills y Audio deben ser números enteros.")
            return

        if not self.servidor_iniciado:
            hilo = threading.Thread(target=ejecutar_servidor, daemon=True)
            hilo.start()
            self.servidor_iniciado = True
            
        self.lbl_estado.configure(text="Estado: ESCUCHANDO PARTIDA...", text_color="#2ecc71")
        self.btn_iniciar.configure(text="🔄 ACTUALIZAR CONFIGURACIÓN")

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
