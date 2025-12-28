import json
import os
import sys
from datetime import datetime

class IAGuardia:
    def __init__(self, archivo_har):
        self.archivo_har = archivo_har
        self.alertas = []
        self.datos = self._cargar_har()

    def _cargar_har(self):
        try:
            with open(self.archivo_har, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error al cargar el archivo: {e}")
            sys.exit(1)

    def sensor_latencia_selectiva(self):
        """Sensor 4: Detecta si las acciones críticas son ralentizadas artificialmente"""
        latencias_criticas = []
        latencias_normales = []
        
        for entry in self.datos['log']['entries']:
            url = entry['request']['url'].lower()
            tiempo = entry.get('time', 0)
            
            # URLs de transacciones
            if any(x in url for x in ["withdraw", "retiro", "payout", "balance", "user", "account"]):
                latencias_criticas.append(tiempo)
            else:
                latencias_normales.append(tiempo)
        
        if latencias_criticas and latencias_normales:
            media_critica = sum(latencias_criticas) / len(latencias_criticas)
            media_normal = sum(latencias_normales) / len(latencias_normales)
            
            if media_critica > media_normal * 2.5:
                self.alertas.append({
                    "nivel": "PELIGRO",
                    "sensor": "THROTTLING_SELECTIVO",
                    "mensaje": f"Retraso forzado: Acciones de cuenta tardan {media_critica:.0f}ms vs {media_normal:.0f}ms promedio."
                })

    def sensor_verdad_oculta(self):
        """Sensor 2: Busca mensajes de error camuflados en respuestas exitosas"""
        palabras_trampa = [
            "error", "denied", "rejected", "failed", "invalid", "bloqueado", 
            "limite", "restringido", "suspicious", "insufficient", "revisión", "recha"
        ]
        
        for entry in self.datos['log']['entries']:
            status = entry['response']['status']
            url = entry['request']['url']
            content_obj = entry['response'].get('content', {})
            text = content_obj.get('text', "")
            
            if text:
                text_lower = text.lower()
                for palabra in palabras_trampa:
                    if palabra in text_lower:
                        nivel = "CRÍTICO" if status == 200 else "INFO"
                        self.alertas.append({
                            "nivel": nivel,
                            "sensor": "VERDAD_OCULTA",
                            "mensaje": f"Palabra '{palabra}' hallada en respuesta (Status: {status}) de: {url[:50]}..."
                        })
                        break

    def sensor_limpieza_evidencia(self):
        """Sensor 3: Detecta órdenes del servidor para purgar rastros locales"""
        for entry in self.datos['log']['entries']:
            headers = entry['response'].get('headers', [])
            for h in headers:
                if h['name'].lower() == 'clear-site-data':
                    self.alertas.append({
                        "nivel": "CUIDADO",
                        "sensor": "LIMPIEZA_EVIDENCIA",
                        "mensaje": f"Intento de purga de rastro en: {entry['request']['url'][:50]}"
                    })

    def generar_dictamen(self):
        print("-" * 65)
        print(f"🛡️  IA-SOBERANA v0.2 - ANALIZANDO: {self.archivo_har}")
        print(f"📅 Fecha de peritaje: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 65)
        
        self.sensor_latencia_selectiva()
        self.sensor_verdad_oculta()
        self.sensor_limpieza_evidencia()
        
        if not self.alertas:
            print("\n✅ RESULTADO: No se detectaron anomalías en el tráfico de red.")
            print("💡 CONCLUSIÓN DEL AUDITOR: El servidor se comporta 'técnicamente' bien.")
            print("   El fraude es visual (Sensor de Interfaz) o lógico de negocio.")
        else:
            print(f"\n🚨 SE DETECTARON {len(self.alertas)} ANOMALÍAS ANALIZANDO EL PAYLOAD:\n")
            for alerta in self.alertas:
                icono = "🔴" if alerta['nivel'] == "CRÍTICO" else "⚠️" if alerta['nivel'] == "PELIGRO" else "ℹ️"
                print(f"{icono} [{alerta['nivel']}] {alerta['sensor']}: {alerta['mensaje']}")
        
        dictamen_path = "dictamen_ia_guardia.json"
        with open(dictamen_path, "w", encoding='utf-8') as f:
            json.dump({
                "analisis": self.archivo_har,
                "timestamp": str(datetime.now()),
                "hallazgos": self.alertas
            }, f, indent=4, ensure_ascii=False)
        
        print(f"\n📄 Dictamen guardado en: {dictamen_path}")
        print("-" * 65)

if __name__ == "__main__":
    # Usamos el archivo capturado por el usuario
    archivo = "evidencia_fallo_retiro.har"
    if os.path.exists(archivo):
        guardia = IAGuardia(archivo)
        guardia.generar_dictamen()
    else:
        print(f"❌ Error: No se encuentra '{archivo}' en la carpeta actual.")