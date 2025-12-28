#!/usr/bin/env python3
"""
QUANTUM HUMANITY - CERTIFICADOR AEE v1.3
Interfaz de línea de comandos para certificación forense soberana
Autor: Franco Luciano Carricondo (DNI 35664619)
Licencia: AGPLv3
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

# Importar motor AEE
from kyber_engine import QuantumSovereignEngine, certificar_evidencia_completa

class QHCertificadorCLI:
    """Interfaz de línea de comandos para Quantum Humanity"""
    
    VERSION = "QH-Certificador-AEE-v1.3"
    BANNER = f"""
    {'='*70}
    🔐 QUANTUM HUMANITY - CERTIFICADOR SOBERANO
    {'='*70}
    Versión: {VERSION}
    Protocolo: AEE v1.3 (Auditoría Ética y Evidencia)
    Autor: Franco Luciano Carricondo (DNI 35664619)
    Licencia: AGPLv3
    Repositorio: https://github.com/quantum-humanity/aee-protocol
    {'='*70}
    "
    
    def __init__(self, config_path: str = "qh_config.json"):
        self.config_path = config_path
        self.config = self._cargar_configuracion()
        
    def _cargar_configuracion(self) -> Dict[str, Any]:
        """Carga o crea configuración del auditor"""
        
        config_default = {
            "auditor": {
                "nombre": "Franco Luciano Carricondo",
                "dni": "35664619",
                "pais": "AR",
                "jurisdiccion": "Buenos Aires, Argentina",
                "contacto": "protocolo@quantum-humanity.org",
                "declaracion_etica": "Certifico bajo mi responsabilidad la veracidad de las observaciones técnicas documentadas mediante el Protocolo AEE."
            },
            "protocolo": {
                "version": "AEE-v1.3",
                "algoritmo_hash": "SHA3-512",
                "validez_estandar_dias": 365,
                "repositorio_oficial": "https://github.com/quantum-humanity/aee-protocol",
                "documentacion": "https://quantum-humanity.org/docs/aee-protocol"
            },
            "legal": {
                "leyes_aplicables": [
                    "Ley 25.506 - Firma Digital (Argentina)",
                    "Ley 25.326 - Protección de Datos Personales",
                    "Ley 27.099 - Defensa del Consumidor",
                    "Código Penal Argentino - Art. 172 bis (Estafas Informáticas)"
                ],
                "advertencia": "Este certificado constituye evidencia técnica preliminar. Requiere validación por autoridades competentes para uso judicial formal.",
                "responsabilidad": "El auditor asume responsabilidad personal por la veracidad de la información certificada.",
                "uso_etico": "Este sistema debe usarse exclusivamente para auditoría ética y protección del consumidor."
            },
            "contacto": {
                "organizacion": "Quantum Humanity",
                "proposito": "Soberanía Digital Ciudadana",
                "email": "contacto@quantum-humanity.org",
                "web": "https://quantum-humanity.org",
                "github": "https://github.com/quantum-humanity",
                "reportes": "reportes@quantum-humanity.org"
            }
        }
        
        # Intentar cargar configuración existente
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_existente = json.load(f)
                    # Merge con defaults para nuevas claves
                    self._merge_configs(config_default, config_existente)
            except json.JSONDecodeError:
                print(f"⚠️  Configuración inválida, usando valores por defecto")
            except Exception as e:
                print(f"⚠️  Error cargando configuración: {e}")
        
        # Guardar configuración
        self._guardar_configuracion(config_default)
        
        return config_default
    
    def _merge_configs(self, default: Dict, existente: Dict) -> None:
        """Fusiona configuraciones manteniendo valores por defecto"""
        for key, value in default.items():
            if key not in existente:
                existente[key] = value
            elif isinstance(value, dict) and isinstance(existente[key], dict):
                self._merge_configs(value, existente[key])
    
    def _guardar_configuracion(self, config: Dict) -> None:
        """Guarda configuración a archivo"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error guardando configuración: {e}")
    
    def mostrar_banner(self) -> None:
        """Muestra banner informativo"""
        print(self.BANNER)
        
    def modo_interactivo(self) -> Optional[Dict[str, Any]]:
        """Modo interactivo paso a paso para creación de evidencia"""
        
        print("\n📝 MODO INTERACTIVO - CREACIÓN DE EVIDENCIA")
        print("-" * 50)
        
        try:
            # 1. URL a certificar
            print("\n🌐 INFORMACIÓN DEL SITIO AUDITADO")
            print("  " + "-" * 40)
            url = input("  URL completa (con https://): ").strip()
            
            if not url:
                print("  ❌ URL es obligatoria")
                return None
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                print(f"  ℹ️  URL ajustada a: {url}")
            
            # 2. Descripción breve
            print("\n📋 DESCRIPCIÓN DE LA OBSERVACIÓN")
            print("  " + "-" * 40)
            descripcion = input("  Descripción breve (qué observaste): ").strip()
            
            if not descripcion:
                descripcion = "Observación técnica documentada mediante Protocolo AEE"
                print(f"  ℹ️  Usando descripción por defecto")
            
            # 3. Hallazgos técnicos
            print("\n🔍 HALLAZGOS TÉCNICOS ENCONTRADOS")
            print("  " + "-" * 40)
            print("  Ingresa cada hallazgo en una línea separada.")
            print("  Presiona Enter dos veces para finalizar.")
            print()
            
            hallazgos = []
            contador = 1
            
            while True:
                try:
                    prompt = f"  Hallazgo #{contador}: "
                    if sys.stdin.isatty():
                        hallazgo = input(prompt).strip()
                    else:
                        # Para entornos no interactivos
                        print(prompt, end='', flush=True)
                        hallazgo = sys.stdin.readline().strip()
                    
                    if not hallazgo:
                        # Verificar si es segundo Enter consecutivo
                        if not sys.stdin.isatty():
                            break
                        if len(hallazgos) > 0:
                            # Preguntar si terminar
                            terminar = input("  ¿Terminar? (s/n): ").strip().lower()
                            if terminar == 's':
                                break
                        continue
                    
                    hallazgos.append(hallazgo)
                    contador += 1
                    
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrumpido por usuario")
                    return None
            
            if not hallazgos:
                hallazgos = ["Sin hallazgos técnicos específicos documentados"]
                print("  ℹ️  Usando valor por defecto para hallazgos")
            
            # 4. Puntuación de riesgo
            print("\n⚠️  EVALUACIÓN DE RIESGO")
            print("  " + "-" * 40)
            print("  0-20: Riesgo bajo (sitio mal configurado)")
            print("  21-50: Riesgo medio (comportamiento sospechoso)")
            print("  51-75: Riesgo alto (posible fraude)")
            print("  76-100: Riesgo crítico (fraude confirmado)")
            print()
            
            while True:
                try:
                    riesgo_input = input("  Puntuación de riesgo (0-100): ").strip()
                    
                    if not riesgo_input:
                        riesgo = 50
                        print(f"  ℹ️  Usando valor por defecto: {riesgo}")
                        break
                    
                    riesgo = int(riesgo_input)
                    
                    if 0 <= riesgo <= 100:
                        break
                    else:
                        print("  ❌ El valor debe estar entre 0 y 100")
                        
                except ValueError:
                    print("  ❌ Ingresa un número válido")
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrumpido por usuario")
                    return None
            
            # 5. Observaciones adicionales
            print("\n📝 OBSERVACIONES ADICIONALES")
            print("  " + "-" * 40)
            print("  Detalles adicionales, contexto, o información relevante.")
            print("  (Opcional - presiona Enter para omitir)")
            print()
            
            observaciones = input("  Observaciones: ").strip()
            
            # 6. Archivos adjuntos
            print("\n📎 ARCHIVOS ADJUNTOS")
            print("  " + "-" * 40)
            print("  Puedes adjuntar screenshots, logs, o archivos de evidencia.")
            print("  Ingresa rutas completas (una por línea).")
            print("  Presiona Enter para omitir o finalizar.")
            print()
            
            archivos = []
            while True:
                try:
                    archivo = input("  Ruta del archivo: ").strip()
                    
                    if not archivo:
                        break
                    
                    if os.path.exists(archivo):
                        archivos.append(archivo)
                        print(f"  ✅ Archivo encontrado: {os.path.basename(archivo)}")
                    else:
                        print(f"  ❌ Archivo no encontrado: {archivo}")
                        
                except KeyboardInterrupt:
                    break
            
            # 7. Método de observación
            print("\n🔬 MÉTODO DE OBSERVACIÓN")
            print("  " + "-" * 40)
            print("  Describe cómo realizaste la observación.")
            print()
            
            metodos = [
                "Observación directa del sitio web",
                "Análisis técnico de código fuente",
                "Pruebas de funcionalidad",
                "Monitoreo de red/trafico",
                "Revisión de términos y condiciones",
                "Otra metodología técnica"
            ]
            
            for i, metodo in enumerate(metodos, 1):
                print(f"  {i}. {metodo}")
            
            print()
            metodo_input = input("  Selecciona método(s) separados por comas (1-6): ").strip()
            
            if metodo_input:
                try:
                    indices = [int(idx.strip()) for idx in metodo_input.split(',')]
                    metodos_seleccionados = [metodos[i-1] for i in indices if 1 <= i <= 6]
                except:
                    metodos_seleccionados = ["Observación técnica no especificada"]
            else:
                metodos_seleccionados = ["Observación técnica no especificada"]
            
            # Construir estructura de evidencia
            evidencia = {
                "metadata": {
                    "timestamp_observacion": datetime.now(timezone.utc).isoformat(),
                    "metodo_observacion": metodos_seleccionados,
                    "herramientas_utilizadas": [
                        "Protocolo AEE v1.3 - Quantum Humanity",
                        "Motor de certificación soberana"
                    ],
                    "modo_captura": "Interactivo - Auditoría ciudadana"
                },
                "contenido": {
                    "url_observada": url,
                    "descripcion_observacion": descripcion,
                    "hallazgos_tecnicos": hallazgos,
                    "puntuacion_riesgo": riesgo,
                    "observaciones_adicionales": observaciones if observaciones else None,
                    "archivos_adjuntos": archivos if archivos else None
                },
                "contexto": {
                    "tipo_auditoria": "Auditoría técnica ciudadana",
                    "motivo_observacion": "Protección del consumidor y prevención del fraude digital",
                    "marco_legal": self.config["legal"]["leyes_aplicables"],
                    "etica_profesional": self.config["legal"]["uso_etico"]
                }
            }
            
            # Remover valores None para limpieza
            self._limpiar_nones(evidencia)
            
            print(f"\n{'='*50}")
            print("✅ EVIDENCIA PREPARADA EXITOSAMENTE")
            print('='*50)
            print(f"  URL: {url}")
            print(f"  Hallazgos: {len(hallazgos)}")
            print(f"  Riesgo: {riesgo}/100")
            print(f"  Método: {', '.join(metodos_seleccionados[:2])}")
            
            return evidencia
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Proceso interrumpido por el usuario")
            return None
        except Exception as e:
            print(f"\n❌ Error en modo interactivo: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _limpiar_nones(self, value):
        """Elimina valores None recursivamente de diccionarios"""
        if isinstance(value, dict):
            for key, val in list(value.items()):
                if val is None:
                    del value[key]
                else:
                    self._limpiar_nones(val)
        elif isinstance(value, list):
            for i in reversed(range(len(value))):
                if value[i] is None:
                    del value[i]
                else:
                    self._limpiar_nones(value[i])
    
    def modo_archivo(self, ruta_archivo: str) -> Optional[Dict[str, Any]]:
        """Carga evidencia desde archivo JSON existente"""
        
        if not os.path.exists(ruta_archivo):
            print(f"❌ Archivo no encontrado: {ruta_archivo}")
            return None
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                evidencia = json.load(f)
            
            # Validar estructura básica
            if not isinstance(evidencia, dict):
                print("❌ Error: El archivo debe contener un objeto JSON")
                return None
            
            print(f"✅ Archivo cargado exitosamente: {ruta_archivo}")
            print(f"   Tamaño: {os.path.getsize(ruta_archivo):,} bytes")
            
            # Mostrar resumen
            url = evidencia.get('contenido', {}).get('url_observada', 
                   evidencia.get('url', 'No especificada'))
            hallazgos = evidencia.get('contenido', {}).get('hallazgos_tecnicos', [])
            
            print(f"   URL: {url[:50]}..." if len(url) > 50 else f"   URL: {url}")
            print(f"   Hallazgos: {len(hallazgos)}")
            
            return evidencia
            
        except json.JSONDecodeError as e:
            print(f"❌ Error: Archivo JSON inválido - {e}")
            return None
        except Exception as e:
            print(f"❌ Error cargando archivo: {e}")
            return None
    
    def ejecutar_certificacion(self, 
                               evidencia: Dict[str, Any], 
                               modo: str = "interactivo") -> Dict[str, Any]:
        """Ejecuta proceso completo de certificación soberana"""
        
        print("\n" + "="*70)
        print("🔨 INICIANDO CERTIFICACIÓN SOBERANA")
        print("="*70)
        
        try:
            # Extraer información necesaria
            url = evidencia.get("contenido", {}).get("url_observada", 
                   evidencia.get("url", "URL_NO_ESPECIFICADA"))
            
            # Obtener datos del auditor desde configuración
            auditor = self.config["auditor"]
            
            print(f"\n👤 AUDITOR SOBERANO:")
            print(f"  Nombre: {auditor['nombre']}")
            print(f"  DNI: {auditor['dni']}")
            print(f"  Jurisdicción: {auditor['jurisdiccion']}")
            
            print(f"\n🎯 OBJETIVO DE CERTIFICACIÓN:")
            print(f"  URL: {url[:80]}..." if len(url) > 80 else f"  URL: {url}")
            
            # Ejecutar certificación completa
            print(f"\n🔐 EJECUTANDO CERTIFICACIÓN...")
            
            resultado = certificar_evidencia_completa(
                evidencia_dict=evidencia,
                url_objetivo=url,
                dni_auditor=auditor["dni"],
                nombre_auditor=auditor["nombre"],
                pais=auditor["pais"]
            )
            
            if resultado["success"]:
                # Mostrar resultados
                self.mostrar_resultados(resultado, modo)
                
                # Preguntar si guardar evidencia original
                self._guardar_evidencia_original(evidencia, resultado)
                
                return resultado
            else:
                print(f"\n❌ ERROR EN CERTIFICACIÓN")
                if "error" in resultado:
                    print(f"   Detalle: {resultado['error']}")
                return resultado
                
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO EN CERTIFICACIÓN: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def mostrar_resultados(self, resultado: Dict[str, Any], modo: str) -> None:
        """Muestra resultados detallados de la certificación"""
        
        exportacion = resultado["exportacion"]
        certificado = resultado["certificado"]
        
        print("\n" + "="*70)
        print("✅ CERTIFICACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        
        # Información del archivo
        print(f"\n📄 ARCHIVO CERTIFICADO GENERADO:")
        print(f"   Nombre: {exportacion['archivo']}")
        print(f"   Tamaño: {exportacion['tamano_bytes']:,} bytes")
        print(f"   Hash SHA3-512: {exportacion['hash_archivo'][:32]}...")
        print(f"   Ruta completa: {exportacion.get('ruta_absoluta', 'No disponible')}")
        
        # Información del certificado
        contexto = certificado["contexto_soberano"]
        sellos = certificado["sellos_integridad"]
        
        print(f"\n🔐 SELLOS DE INTEGRIDAD:")
        print(f"   Sello Soberano: {sellos['sello_soberano'][:24]}...")
        print(f"   Sello Evidencia: {sellos['sello_evidencia'][:24]}...")
        print(f"   Algoritmo: {sellos['algoritmo']}")
        print(f"   Timestamp: {sellos['timestamp_sellado'][:19]}")
        
        # Hallazgos documentados
        evidencia_original = certificado.get("evidencia_original", {})
        hallazgos = evidencia_original.get("contenido", {}).get("hallazgos_tecnicos", [])
        
        if hallazgos:
            print(f"\n🔍 HALLAZGOS DOCUMENTADOS ({len(hallazgos)}):")
            for i, hallazgo in enumerate(hallazgos[:3], 1):
                print(f"   {i}. {hallazgo[:60]}..." if len(hallazgo) > 60 else f"   {i}. {hallazgo}")
            if len(hallazgos) > 3:
                print(f"   ... y {len(hallazgos) - 3} hallazgos más")
        
        # Riesgo evaluado
        riesgo = evidencia_original.get("contenido", {}).get("puntuacion_riesgo", 0)
        nivel_riesgo = self._clasificar_riesgo(riesgo)
        
        print(f"\n⚠️  EVALUACIÓN DE RIESGO:")
        print(f"   Puntuación: {riesgo}/100")
        print(f"   Nivel: {nivel_riesgo}")
        
        # Mostrar resumen ejecutivo
        if "resumen_ejecutivo" in resultado:
            print("\n" + "="*70)
            print("📋 RESUMEN EJECUTIVO")
            print("="*70)
            print(resultado["resumen_ejecutivo"])
        
        print("\n" + "="*70)
        print("⚖️  VALOR LEGAL Y USO")
        print("="*70)
        print("ESTE CERTIFICADO ES:")
        print("• Acta de observación técnica ciudadana")
        print("• Evidencia digital con integridad criptográfica verificable")
        print("• Documento vinculado a identidad soberana del auditor")
        print("• Herramienta para protección del consumidor y prevención de fraude")
        print()
        print("NO ES:")
        print("• Prueba legal concluyente (requiere validación judicial)")
        print("• Análisis forense profesional certificado")
        print("• Acusación formal o veredicto")
        print()
        print("🛡️  Quantum Humanity - Protocolo AEE v1.3")
        print("   Soberanía Digital Ciudadana Verificable")
    
    def _clasificar_riesgo(self, puntuacion: int) -> str:
        """Clasifica nivel de riesgo basado en puntuación"""
        if puntuacion >= 76:
            return "CRÍTICO (Posible fraude organizado)"
        elif puntuacion >= 51:
            return "ALTO (Posible fraude)"
        elif puntuacion >= 21:
            return "MEDIO (Comportamiento sospechoso)"
        else:
            return "BAJO (Sitio mal configurado)"
    
    def _guardar_evidencia_original(self, 
                                   evidencia: Dict[str, Any], 
                                   resultado: Dict[str, Any]) -> None:
        """Guarda evidencia original junto al certificado"""
        
        archivo_certificado = resultado["exportacion"]["archivo"]
        nombre_base = os.path.splitext(archivo_certificado)[0]
        archivo_evidencia = f"{nombre_base}_evidencia_original.json"
        
        try:
            with open(archivo_evidencia, 'w', encoding='utf-8') as f:
                json.dump(evidencia, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 EVIDENCIA ORIGINAL GUARDADA:")
            print(f"   Archivo: {archivo_evidencia}")
            
        except Exception as e:
            print(f"\n⚠️  No se pudo guardar evidencia original: {e}")
    
    def modo_configuracion(self) -> None:
        """Muestra y permite editar configuración"""
        
        print("\n⚙️  CONFIGURACIÓN ACTUAL DEL PROTOCOLO AEE")
        print("="*50)
        
        # Mostrar configuración actual
        print(json.dumps(self.config, indent=2, ensure_ascii=False))
        
        print("\n¿Deseas editar la configuración?")
        print("1. Editar datos del auditor")
        print("2. Restaurar configuración por defecto")
        print("3. Volver al menú principal")
        
        try:
            opcion = input("\nSelección: ").strip()
            
            if opcion == "1":
                self._editar_configuracion()
            elif opcion == "2":
                self._restaurar_configuracion()
            elif opcion == "3":
                return
            else:
                print("❌ Opción no válida")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Operación cancelada")
    
    def _editar_configuracion(self) -> None:
        """Interfaz para editar configuración"""
        print("\n✏️  EDITAR CONFIGURACIÓN")
        print("-" * 40)
        
        # Esta función se puede expandir para edición interactiva
        print("Para editar la configuración, modifica directamente el archivo:")
        print(f"  {os.path.abspath(self.config_path)}")
        print("\nLuego reinicia el certificador para cargar los cambios.")
        
        input("\nPresiona Enter para continuar...")
    
    def _restaurar_configuracion(self) -> None:
        """Restaura configuración por defecto"""
        print("\n⚠️  RESTAURAR CONFIGURACIÓN POR DEFECTO")
        print("-" * 40)
        
        confirmar = input("¿Estás seguro? Esto sobrescribirá tu configuración actual. (s/n): ")
        
        if confirmar.lower() == 's':
            # Eliminar archivo de configuración
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            
            # Recargar configuración (creará nueva por defecto)
            self.config = self._cargar_configuracion()
            
            print("✅ Configuración restaurada a valores por defecto")
        else:
            print("❌ Operación cancelada")
    
    def ejecutar_desde_args(self, args):
        """Ejecuta certificación basada en argumentos de línea de comandos"""
        
        if args.modo == "interactivo":
            evidencia = self.modo_interactivo()
            if evidencia:
                self.ejecutar_certificacion(evidencia, "interactivo")
                
        elif args.modo == "archivo":
            if not args.archivo:
                print("❌ Error: Se requiere ruta de archivo con --archivo")
                return
            
            evidencia = self.modo_archivo(args.archivo)
            if evidencia:
                self.ejecutar_certificacion(evidencia, "archivo")
                
        elif args.modo == "config":
            self.modo_configuracion()
            
        elif args.modo == "version":
            self.mostrar_banner()
            
        elif args.modo == "ejemplo":
            self.generar_ejemplo()
    
    def generar_ejemplo(self) -> None:
        """Genera un ejemplo de certificación"""
        
        print("\n📚 GENERANDO EJEMPLO DE CERTIFICACIÓN")
        print("-" * 40)
        
        evidencia_ejemplo = {
            "metadata": {
                "timestamp_observacion": datetime.now(timezone.utc).isoformat(),
                "metodo_observacion": ["Ejemplo de certificación"],
                "herramientas_utilizadas": ["Protocolo AEE v1.3 - Ejemplo"],
                "modo_captura": "Ejemplo demostrativo"
            },
            "contenido": {
                "url_observada": "https://ejemplo.quantum-humanity.org",
                "descripcion_observacion": "Este es un ejemplo de certificación generado automáticamente.",
                "hallazgos_tecnicos": [
                    "Ejemplo de hallazgo técnico #1",
                    "Ejemplo de hallazgo técnico #2",
                    "Patrón de ejemplo detectado"
                ],
                "puntuacion_riesgo": 35,
                "observaciones_adicionales": "Ejemplo generado para demostración del Protocolo AEE.",
                "archivos_adjuntos": []
            },
            "contexto": {
                "tipo_auditoria": "Ejemplo demostrativo",
                "motivo_observacion": "Demostración de funcionalidad del Protocolo AEE",
                "marco_legal": self.config["legal"]["leyes_aplicables"],
                "etica_profesional": self.config["legal"]["uso_etico"]
            }
        }
        
        resultado = self.ejecutar_certificacion(evidencia_ejemplo, "ejemplo")
        
        if resultado.get("success"):
            print("\n✅ EJEMPLO GENERADO EXITOSAMENTE")
            print(f"   Archivo: {resultado['exportacion']['archivo']}")
            print(f"   Este archivo puede usarse como referencia y prueba del sistema.")
    
    def ejecutar(self):
        """Punto de entrada principal con interfaz de menú"""
        
        self.mostrar_banner()
        
        while True:
            print("\n📂 MENÚ PRINCIPAL - PROTOCOLO AEE v1.3")
            print("-" * 40)
            print("1. Modo interactivo (crear nueva evidencia)")
            print("2. Certificar archivo JSON existente")
            print("3. Ver/editar configuración")
            print("4. Generar ejemplo demostrativo")
            print("5. Mostrar información de versión")
            print("6. Salir")
            print("-" * 40)
            
            try:
                opcion = input("\nSeleccione opción (1-6): ").strip()
                
                if opcion == "1":
                    evidencia = self.modo_interactivo()
                    if evidencia:
                        self.ejecutar_certificacion(evidencia, "interactivo")
                        
                elif opcion == "2":
                    ruta = input("\n📁 Ruta del archivo JSON: ").strip()
                    if ruta:
                        evidencia = self.modo_archivo(ruta)
                        if evidencia:
                            self.ejecutar_certificacion(evidencia, "archivo")
                    else:
                        print("❌ Debes especificar una ruta de archivo")
                        
                elif opcion == "3":
                    self.modo_configuracion()
                    
                elif opcion == "4":
                    self.generar_ejemplo()
                    
                elif opcion == "5":
                    self.mostrar_banner()
                    
                elif opcion == "6":
                    print("\n👋 ¡Hasta luego! Recuerda: La soberanía digital se ejerce, no se delega.")
                    print("   Protocolo AEE v1.3 - Quantum Humanity 🇦🇷")
                    break
                    
                else:
                    print("❌ Opción no válida. Por favor, selecciona 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrumpido por usuario")
                confirmar = input("¿Deseas salir? (s/n): ").strip().lower()
                if confirmar == 's':
                    print("\n👋 ¡Hasta luego! La soberanía continua...")
                    break
                    
            except EOFError:
                print("\n\n👋 ¡Hasta luego! EOF detectado.")
                break
                
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                import traceback
                traceback.print_exc()
                input("\nPresiona Enter para continuar...")

def main():
    """Función principal con manejo de argumentos y errores"""
    
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description="Quantum Humanity - Certificador AEE v1.3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s                       # Modo interactivo con menú
  %(prog)s --modo interactivo    # Modo interactivo directo
  %(prog)s --modo archivo --archivo evidencia.json
  %(prog)s --modo ejemplo        # Generar ejemplo demostrativo
  %(prog)s --modo config         # Configurar sistema
  %(prog)s --modo version        # Mostrar información de versión
        """
    )
    
    parser.add_argument(
        "--modo",
        choices=["interactivo", "archivo", "config", "version", "ejemplo"],
        default=None,
        help="Modo de operación (por defecto: menú interactivo)"
    )
    
    parser.add_argument(
        "--archivo",
        type=str,
        help="Ruta al archivo JSON con evidencia (requerido para modo 'archivo')"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="qh_config.json",
        help="Ruta al archivo de configuración (por defecto: qh_config.json)"
    )
    
    # Parsear argumentos
    args = parser.parse_args()
    
    try:
        # Crear certificador
        certificador = QHCertificadorCLI(config_path=args.config)
        
        # Ejecutar según modo
        if args.modo:
            certificador.ejecutar_desde_args(args)
        else:
            # Modo menú interactivo
            certificador.ejecutar()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
