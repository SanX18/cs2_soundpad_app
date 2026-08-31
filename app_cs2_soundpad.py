import tkinter as tk
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
        print("Sonido reproducido en Soundpad.")
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

# --- LÓGICA DE LA INTERFAZ GRÁFICA (GUI) ---
class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("CS2 Soundpad Auto-Caster")
        self.root.geometry("350x450")
        self.root.resizable(False, False)
        
        tk.Label(root, text="CS2 Soundpad Integración", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(root, text="¿Cada cuántas Kills suena el audio?").pack(pady=5)
        self.entry_kills = tk.Entry(root, justify="center")
        self.entry_kills.insert(0, "2")
        self.entry_kills.pack()
        
        tk.Label(root, text="Número de Audio en Soundpad:").pack(pady=5)
        self.entry_audio = tk.Entry(root, justify="center")
        self.entry_audio.insert(0, "1")
        self.entry_audio.pack()
        
        tk.Label(root, text="Ruta de Soundpad.exe:").pack(pady=5)
        self.entry_ruta = tk.Entry(root, width=40, justify="center")
        self.entry_ruta.insert(0, ruta_soundpad)
        self.entry_ruta.pack()
        tk.Button(root, text="Buscar Soundpad", command=self.buscar_soundpad).pack(pady=5)
        
        self.btn_cfg = tk.Button(root, text="1. Instalar CFG en CS2", bg="lightblue", command=self.instalar_cfg)
        self.btn_cfg.pack(pady=15, fill="x", padx=40)
        
        self.btn_iniciar = tk.Button(root, text="2. INICIAR APP", bg="lightgreen", font=("Arial", 12, "bold"), command=self.iniciar_app)
        self.btn_iniciar.pack(pady=5, fill="x", padx=40)
        
        self.lbl_estado = tk.Label(root, text="Estado: Detenido", fg="red")
        self.lbl_estado.pack(pady=10)
        
        self.servidor_iniciado = False

    def buscar_soundpad(self):
        ruta = filedialog.askopenfilename(title="Selecciona Soundpad.exe", filetypes=[("Ejecutables", "*.exe")])
        if ruta:
            self.entry_ruta.delete(0, tk.END)
            self.entry_ruta.insert(0, ruta)

    def instalar_cfg(self):
        ruta_cs2 = filedialog.askdirectory(title="Selecciona la carpeta 'cfg' de CS2 (csgo/cfg)")
        if not ruta_cs2:
            return
            
        contenido_cfg = """"Soundpad App"
{
    "uri" "http://localhost:3000"
    "timeout" "5.0"
    "buffer"  "0.1"
    "throttle" "0.1"
    "heartbeat" "10.0"
    "data"
    {
        "provider"            "1"
        "player_match_stats"  "1"
    }
}"""
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
            
        self.lbl_estado.config(text="Estado: ESCUCHANDO PARTIDA...", fg="green")
        self.btn_iniciar.config(text="ACTUALIZAR CONFIGURACIÓN")

if __name__ == "__main__":
    ventana = tk.Tk()
    app = Aplicacion(ventana)
    ventana.mainloop()
