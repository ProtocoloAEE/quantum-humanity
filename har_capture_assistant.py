import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURACIÓN ---
CARPETA_A_MONITOREAR = "." 
SCRIPT_SEALER = "har_sealer_real.py"

class HarHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        # Detecta tanto .har como .har.txt
        if event.src_path.lower().endswith(".har") or event.src_path.lower().endswith(".har.txt"):
            nombre_archivo = os.path.basename(event.src_path)
            print(f"\n🚀 ¡NUEVO ARCHIVO DETECTADO!: {nombre_archivo}")
            print(f"🛡️ Sellando evidencia automáticamente...")
            
            try:
                # Ejecutamos el sealer enviándole la ruta del archivo
                proceso = subprocess.Popen(['python', SCRIPT_SEALER], 
                                         stdin=subprocess.PIPE, 
                                         text=True)
                # Le enviamos la ruta del archivo al sealer como si la escribieras vos
                proceso.communicate(input=event.src_path)
                print(f"✅ {nombre_archivo} SELLADO Y ASEGURADO.")
                print("-" * 50)
            except Exception as e:
                print(f"❌ Error al sellar: {e}")

if __name__ == "__main__":
    print("🛡️ ASISTENTE DE CAPTURA FORENSE - ACTIVO")
    print(f"📂 Monitoreando: {os.path.abspath(CARPETA_A_MONITOREAR)}")
    print("✨ Instrucción: Solo guarda tus archivos HAR en esta carpeta y yo los sello.")
    print("Presioná Ctrl+C para detener.")
    
    event_handler = HarHandler()
    observer = Observer()
    observer.schedule(event_handler, CARPETA_A_MONITOREAR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()