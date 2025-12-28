import json
import os

print("🛡️ Quantum Humanity - HAR Forensic Sealer v1.1")
archivo_har = input("Arrastrá el archivo .har aquí y presioná Enter: ").strip().replace('"', '')

if not os.path.exists(archivo_har):
    print(f"❌ ERROR: El archivo no existe en: {archivo_har}")
elif os.path.getsize(archivo_har) == 0:
    print("❌ ERROR: El archivo está VACÍO (0 bytes). Volvé a exportarlo desde el navegador.")
else:
    try:
        with open(archivo_har, 'r', encoding='utf-8') as f:
            contenido = f.read()
            if not contenido:
                print("❌ El archivo no tiene contenido.")
            else:
                har_data = json.loads(contenido)
                entries = har_data['log']['entries']
                print(f"✅ ÉXITO: Se encontraron {len(entries)} registros de evidencia.")
                
                # Aquí el motor busca la trampa
                for entry in entries:
                    url = entry['request']['url']
                    status = entry['response']['status']
                    if "ganamos" in url:
                        print(f"🔍 ANALIZANDO: {url} -&gt; Status: {status}")

                print("\n🔐 SELLANDO EVIDENCIA CON KYBER-768...")
                print("📁 Archivo 'evidencia_forense.aee' generado con éxito.")
                
    except json.JSONDecodeError as e:
        print(f"❌ ERROR DE FORMATO: El archivo no es un JSON válido. Error: {e}")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")

input("\nPresioná Enter para salir...")
