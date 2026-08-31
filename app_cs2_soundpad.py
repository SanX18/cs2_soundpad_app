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
            
        if kills_actuales > kills_anteriores:
            log_msg(f"💥 ¡Baja detectada! Kills totales: {kills_actuales}")
            
            for regla in reglas_activas:
                if kills_actuales % regla['kills'] == 0:
                    log_msg(f"🎯 Regla de {regla['kills']} kills activada.")
                    reproducir_sonido(regla['folder'], regla['audio'])
                    break
                    
            kills_anteriores = kills_actuales
    return 'OK', 200

def ejecutar_servidor():
    log_msg("✅ Servidor escuchando en puerto 3000.")
    servidor_flask.run(port=3000)

class Aplicacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        global app_instance
        app_instance = self
        
        self.title("CS2 Soundpad Auto-Caster")
        self.geometry("450x680")
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
        self.settings_frame.pack(pady=10, padx=20, fill="both")
        
        # --- TABLA DE REGLAS ---
        self.rows_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.rows_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(self.rows_frame, text="Cada X Kills", width=90, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(self.rows_frame, text="Nº Carpeta", width=90, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(self.rows_frame, text="Nº Audio", width=90, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)
        
        self.rule_entries = []
        for i in range(4):
            ek = ctk.CTkEntry(self.rows_frame, width=90, justify="center", placeholder_text="-")
            ek.grid(row=i+1, column=0, padx=5, pady=3)
            
            ec = ctk.CTkEntry(self.rows_frame, width=90, justify="center", placeholder_text="(Opcional)")
            ec.grid(row=i+1, column=1, padx=5, pady=3)
            
            ea = ctk.CTkEntry(self.rows_frame, width=90, justify="center", placeholder_text="-")
            ea.grid(row=i+1, column=2, padx=5, pady=3)
            
            self.rule_entries.append((ek, ec, ea))
            
        self.rule_entries[0][0].insert(0, "2")
        self.rule_entries[0][2].insert(0, "1")
        
        # --- RUTA SOUNDPAD ---
        self.lbl_ruta = ctk.CTkLabel(self.settings_frame, text="📂 Ruta de Soundpad.exe:", font=ctk.CTkFont(weight="bold"))
        self.lbl_ruta.pack()
        self.ruta_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.ruta_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.entry_ruta = ctk.CTkEntry(self.ruta_frame, justify="left")
        self.entry_ruta.insert(0, ruta_soundpad)
        self.entry_ruta.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_buscar = ctk.CTkButton(self.ruta_frame, text="📁", width=40, command=self.buscar_soundpad)
        self.btn_buscar.pack(side="right")

        # --- ACTIONS ---
        self.btn_cfg = ctk.CTkButton(self, text="⚙️ 1. Instalar CFG en CS2", fg_color="#d35400", hover_color="#e67e22", command=self.instalar_cfg)
        self.btn_cfg.pack(pady=(5, 5), padx=40, fill="x")
        
        self.btn_iniciar = ctk.CTkButton(self, text="🚀 2. INICIAR / ACTUALIZAR", fg_color="#27ae60", hover_color="#2ecc71", font=ctk.CTkFont(size=14, weight="bold"), command=self.iniciar_app)
        self.btn_iniciar.pack(pady=5, padx=40, fill="x")
        
        # --- LOGS BOX ---
        self.log_box = ctk.CTkTextbox(self, height=130, state="disabled", font=ctk.CTkFont(size=11, family="Consolas"))
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)
        self.escribir_log("Aplicación v1.4 lista.")
        
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
            
        # Ordenar reglas de mayor a menor kills para la prioridad del módulo (%)
        nuevas_reglas.sort(key=lambda x: x['kills'], reverse=True)
        reglas_activas = nuevas_reglas
        
        self.escribir_log(f"✅ {len(reglas_activas)} reglas cargadas.")

        if not self.servidor_iniciado:
            hilo = threading.Thread(target=ejecutar_servidor, daemon=True)
            hilo.start()
            self.servidor_iniciado = True
            self.escribir_log("⏳ ESCUCHANDO PARTIDA...")

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
