#!/usr/bin/env python3
"""
QUANTUM HUMANITY - MOTOR AEE v1.3 (PRODUCCIÓN)
Motor de identidad soberana y certificación post-cuántica
Autor: Franco Luciano Carricondo (DNI 35664619)
Licencia: AGPLv3
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional

class QuantumSovereignEngine:
    """Motor de soberanía digital para certificación ciudadana"""
    
    VERSION = "AEE-v1.3"
    ALGORITHM = "SHA3-512-Deterministic"
    
    def __init__(self, auditor_dni: str, auditor_nombre: str, pais: str = "AR"):
        """
        Inicializa motor con identidad soberana
        
        Args:
            auditor_dni: Documento Nacional de Identidad (Argentina)
            auditor_nombre: Nombre completo del auditor
            pais: Código ISO 3166-1 alpha-2 (AR, ES, MX, etc.)
        """
        self.auditor_dni = str(auditor_dni).strip()
        self.auditor_nombre = auditor_nombre.strip()
        self.pais = pais.upper()
        
        # Validaciones de identidad
        self._validar_identidad()
        
        # Generar identidad soberana
        self.clave_publica = self._generar_clave_publica()
        self.identificador_soberano = self._generar_identificador()
        
    def _validar_identidad(self) -> None:
        """Valida datos de identidad"""
        if not self.auditor_dni:
            raise ValueError("DNI es obligatorio")
        if not self.auditor_nombre:
            raise ValueError("Nombre es obligatorio")
        if len(self.pais) != 2:
            raise ValueError("País debe ser código de 2 letras (ISO 3166-1)")
        
    def _generar_clave_publica(self) -> str:
        """Genera clave pública determinista desde identidad física"""
        
        # 1. Construir semilla soberana única
        semilla_base = (
            f"QH-SOBERANO-{self.pais}-"
            f"{self.auditor_dni}-"
            f"{self.auditor_nombre}-"
            f"PROTOCOLO-AEE-v1.3"
        )
        
        # 2. Hash seguro de la semilla
        semilla_hash = hashlib.sha3_256(semilla_base.encode()).digest()
        
        # 3. Derivar clave pública (determinista)
        clave_raw = hashlib.sha3_256(b"PK-SOBERANO-AEE" + semilla_hash).hexdigest()
        
        # 4. Formato estándar verificable
        return f"QH-PK-{self.pais}-{self.auditor_dni[:2]}-{clave_raw[:32]}"
    
    def _generar_identificador(self) -> str:
        """Genera identificador único soberano"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        hash_base = hashlib.sha3_256(
            f"{self.clave_publica}-{timestamp}-AEE-SOBERANO".encode()
        ).hexdigest()
        
        return f"QH-ID-{self.pais}-{hash_base[:12]}"
    
    def sellar_evidencia(self, 
                         evidencia_dict: Dict[str, Any], 
                         url_objetivo: str, 
                         timestamp_utc: Optional[str] = None) -> Dict[str, Any]:
        """
        Sella evidencia con contexto completo y sellos criptográficos
        
        Args:
            evidencia_dict: Diccionario con evidencia técnica
            url_objetivo: URL auditada (máx 500 caracteres)
            timestamp_utc: Timestamp UTC ISO 8601 (opcional)
            
        Returns:
            Dict: Estructura sellada completa lista para certificación
        """
        
        # Validar entrada
        if not url_objetivo or len(url_objetivo) > 500:
            raise ValueError("URL objetivo inválida (vacía o >500 caracteres)")
        
        # Timestamp preciso UTC
        if timestamp_utc is None:
            timestamp_utc = datetime.now(timezone.utc).isoformat()
        
        # 1. Preparar evidencia para hashing consistente
        evidencia_ordenada = self._ordenar_para_hashing(evidencia_dict)
        evidencia_hash = self._calcular_hash_evidencia(evidencia_ordenada)
        
        # 2. Construir contexto soberano completo
        contexto = {
            "protocolo": self.VERSION,
            "algoritmo": self.ALGORITHM,
            "auditor": {
                "nombre": self.auditor_nombre,
                "dni": self.auditor_dni,
                "pais": self.pais,
                "clave_publica": self.clave_publica,
                "identificador": self.identificador_soberano,
                "declaracion": "Certifico bajo mi responsabilidad la veracidad técnica"
            },
            "objetivo": {
                "url": url_objetivo[:200],  # Limitar para consistencia
                "timestamp_auditoria": timestamp_utc,
                "dominio": self._extraer_dominio(url_objetivo)
            },
            "hash_evidencia": evidencia_hash,
            "metadatos_tecnicos": {
                "python_version": sys.version,
                "sistema_operativo": sys.platform,
                "timestamp_procesamiento": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # 3. Calcular sellos de integridad múltiples
        sellos = self._calcular_sellos_integridad(contexto)
        
        # 4. Estructura final del certificado
        certificado = {
            "encabezado": {
                "titulo": "CERTIFICADO SOBERANO QUANTUM HUMANITY",
                "subtitulo": "Evidencia Digital Sellada - Protocolo AEE v1.3",
                "version": self.VERSION,
                "fecha_generacion": datetime.now(timezone.utc).isoformat(),
                "advertencia": "DOCUMENTO DE EVIDENCIA TÉCNICA - VALOR PROBATORIO"
            },
            "contexto_soberano": contexto,
            "evidencia_original": evidencia_dict,
            "sellos_integridad": sellos,
            "instrucciones_verificacion": self._instrucciones_verificacion(),
            "marco_legal": {
                "referencia": "Ley 25.506 - Firma Digital (Argentina)",
                "tipo_documento": "Acta de Observación Técnica Ciudadana",
                "finalidad": "Protección del consumidor y prevención del fraude digital"
            }
        }
        
        return certificado
    
    def _ordenar_para_hashing(self, data: Any) -> Any:
        """Ordena recursivamente estructuras para hashing consistente"""
        if isinstance(data, dict):
            return {k: self._ordenar_para_hashing(v) 
                   for k, v in sorted(data.items())}
        elif isinstance(data, list):
            # Ordenar listas si todos los elementos son comparables
            try:
                return sorted(self._ordenar_para_hashing(item) for item in data)
            except TypeError:
                return [self._ordenar_para_hashing(item) for item in data]
        else:
            return data
    
    def _calcular_hash_evidencia(self, evidencia_ordenada: Dict) -> str:
        """Calcula hash SHA3-512 de evidencia"""
        evidencia_str = json.dumps(
            evidencia_ordenada, 
            sort_keys=True, 
            separators=(',', ':'),
            ensure_ascii=False
        )
        
        return hashlib.sha3_512(evidencia_str.encode('utf-8')).hexdigest()
    
    def _extraer_dominio(self, url: str) -> str:
        """Extrae dominio de URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc or url.split('//')[-1].split('/')[0]
        except:
            return url.split('//')[-1].split('/')[0].split('?')[0]
    
    def _calcular_sellos_integridad(self, contexto: Dict) -> Dict[str, Any]:
        """Calcula múltiples sellos de integridad"""
        
        # 1. Preparar datos para sellado
        datos_sello = {
            "clave_publica": self.clave_publica,
            "hash_evidencia": contexto["hash_evidencia"],
            "url": contexto["objetivo"]["url"],
            "timestamp": contexto["objetivo"]["timestamp_auditoria"],
            "auditor_dni": self.auditor_dni,
            "protocolo_version": self.VERSION
        }
        
        datos_str = json.dumps(
            datos_sello,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=False
        )
        
        # 2. Capas de hash para robustez
        capa1 = hashlib.sha3_512(datos_str.encode()).hexdigest()
        capa2 = hashlib.sha3_512(f"AEE-SELLO-{capa1}".encode()).hexdigest()
        capa3 = hashlib.sha3_512(f"QH-SOBERANO-{capa2}".encode()).hexdigest()
        
        # 3. Sello final
        sello_final = capa3
        
        return {
            "sello_soberano": f"QH-SELLO-{sello_final[:64]}",
            "sello_evidencia": contexto["hash_evidencia"],
            "algoritmo": self.ALGORITHM,
            "timestamp_sellado": datetime.now(timezone.utc).isoformat(),
            "capas_hash": 3,
            "verificacion_rapida": sello_final[:16]  # Para verificación rápida
        }
    
    def _instrucciones_verificacion(self) -> Dict[str, Any]:
        """Instrucciones completas para verificación independiente"""
        return {
            "paso_1": "Obtener clave pública del auditor desde el certificado",
            "paso_2": "Recalcular hash SHA3-512 de 'evidencia_original'",
            "paso_3": "Comparar con 'sello_evidencia' en 'sellos_integridad'",
            "paso_4": "Validar que 'sello_soberano' coincida con recalculo",
            "paso_5": "Validar timestamp dentro de periodo razonable",
            "herramientas": "Cualquier implementación SHA3-512 (OpenSSL, Python, etc.)",
            "codigo_verificacion": "Disponible en https://github.com/quantum-humanity/aee-protocol",
            "contacto_verificacion": "verificacion@quantum-humanity.org"
        }
    
    def exportar_certificado(self, 
                            certificado: Dict[str, Any], 
                            nombre_base: Optional[str] = None) -> Dict[str, Any]:
        """
        Exporta certificado a archivo JSON con metadatos
        
        Args:
            certificado: Certificado generado por sellar_evidencia
            nombre_base: Nombre base personalizado (opcional)
            
        Returns:
            Dict: Información del archivo generado y metadatos
        """
        
        # Generar nombre de archivo único
        if nombre_base is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            dominio = certificado["contexto_soberano"]["objetivo"]["dominio"]
            dominio_limpio = "".join(c for c in dominio if c.isalnum() or c in '.-')
            nombre_base = f"QH-CERT-{dominio_limpio}-{timestamp}"
        
        nombre_archivo = f"{nombre_base}.json"
        
        try:
            # Escribir archivo con encoding UTF-8
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                json.dump(certificado, f, indent=2, ensure_ascii=False)
            
            # Calcular hash del archivo para verificación posterior
            with open(nombre_archivo, 'rb') as f:
                contenido = f.read()
                hash_archivo = hashlib.sha3_512(contenido).hexdigest()
            
            # Metadatos del archivo
            tamano_bytes = os.path.getsize(nombre_archivo)
            
            return {
                "success": True,
                "archivo": nombre_archivo,
                "hash_archivo": hash_archivo,
                "tamano_bytes": tamano_bytes,
                "timestamp_exportacion": datetime.now(timezone.utc).isoformat(),
                "ruta_absoluta": os.path.abspath(nombre_archivo)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "archivo": nombre_archivo
            }
    
    def generar_resumen_ejecutivo(self, certificado: Dict[str, Any]) -> str:
        """Genera resumen ejecutivo legible del certificado"""
        
        contexto = certificado["contexto_soberano"]
        sellos = certificado["sellos_integridad"]
        
        resumen = f"""
{'='*70}
CERTIFICADO SOBERANO QUANTUM HUMANITY - PROTOCOLO AEE v1.3
{'='*70}

AUDITOR SOBERANO:
  Nombre: {contexto['auditor']['nombre']}
  DNI: {contexto['auditor']['dni']}
  País: {contexto['auditor']['pais']}
  Clave Pública: {contexto['auditor']['clave_publica']}
  Identificador: {contexto['auditor']['identificador']}

OBJETIVO CERTIFICADO:
  URL: {contexto['objetivo']['url']}
  Dominio: {contexto['objetivo']['dominio']}
  Fecha Auditoría: {contexto['objetivo']['timestamp_auditoria']}

SELLOS DE INTEGRIDAD:
  Sello Soberano: {sellos['sello_soberano'][:32]}...
  Sello Evidencia: {sellos['sello_evidencia'][:32]}...
  Algoritmo: {sellos['algoritmo']}
  Timestamp: {sellos['timestamp_sellado']}
  Capas Hash: {sellos['capas_hash']}
  Verificación Rápida: {sellos['verificacion_rapida']}

INFORMACIÓN TÉCNICA:
  Protocolo: {certificado['encabezado']['version']}
  Fecha Generación: {certificado['encabezado']['fecha_generacion']}
  Python: {contexto['metadatos_tecnicos']['python_version']}
  Sistema: {contexto['metadatos_tecnicos']['sistema_operativo']}

MARCO LEGAL:
  Referencia: {certificado['marco_legal']['referencia']}
  Tipo Documento: {certificado['marco_legal']['tipo_documento']}
  Finalidad: {certificado['marco_legal']['finalidad']}

{'='*70}
INSTRUCCIONES DE VERIFICACIÓN:
{'='*70}
{certificado['instrucciones_verificacion']['paso_1']}
{certificado['instrucciones_verificacion']['paso_2']}
{certificado['instrucciones_verificacion']['paso_3']}
{certificado['instrucciones_verificacion']['paso_4']}
{certificado['instrucciones_verificacion']['paso_5']}

Herramientas: {certificado['instrucciones_verificacion']['herramientas']}
Código: {certificado['instrucciones_verificacion']['codigo_verificacion']}
Contacto: {certificado['instrucciones_verificacion']['contacto_verificacion']}

{'='*70}
        """.strip()
        
        return resumen

# ============================================================================
# FUNCIONES DE CONVENIENCIA PARA USO DIRECTO
# ============================================================================

def crear_motor_soberano(dni: str, nombre: str, pais: str = "AR") -> QuantumSovereignEngine:
    """
    Crea motor soberano con validaciones integradas
    
    Args:
        dni: Documento Nacional de Identidad
        nombre: Nombre completo del auditor
        pais: Código país ISO 3166-1
        
    Returns:
        QuantumSovereignEngine: Instancia configurada del motor
    """
    return QuantumSovereignEngine(dni, nombre, pais)

def certificar_evidencia_completa(evidencia_dict: Dict[str, Any], 
                                  url_objetivo: str, 
                                  dni_auditor: str, 
                                  nombre_auditor: str,
                                  pais: str = "AR") -> Dict[str, Any]:
    """
    Función completa para certificación en un solo paso
    
    Args:
        evidencia_dict: Evidencia técnica a certificar
        url_objetivo: URL del sitio auditado
        dni_auditor: DNI del auditor
        nombre_auditor: Nombre del auditor
        pais: Código país
        
    Returns:
        Dict: Resultado completo de la certificación
    """
    
    # 1. Crear motor soberano
    motor = crear_motor_soberano(dni_auditor, nombre_auditor, pais)
    
    # 2. Sellar evidencia
    certificado = motor.sellar_evidencia(evidencia_dict, url_objetivo)
    
    # 3. Exportar certificado
    resultado_export = motor.exportar_certificado(certificado)
    
    # 4. Generar resumen
    resumen = motor.generar_resumen_ejecutivo(certificado)
    
    return {
        "success": resultado_export["success"],
        "motor": motor,
        "certificado": certificado,
        "exportacion": resultado_export,
        "resumen_ejecutivo": resumen
    }

if __name__ == "__main__":
    """Ejecución directa - modo demostración y pruebas"""
    
    print("\n" + "="*70)
    print("🔐 QUANTUM HUMANITY - MOTOR AEE v1.3")
    print("="*70)
    
    # Datos de demostración
    DEMO_DNI = "35664619"
    DEMO_NOMBRE = "Franco Luciano Carricondo"
    DEMO_PAIS = "AR"
    
    # Evidencia de demostración
    evidencia_demo = {
        "metadata": {
            "tipo_observacion": "Demostración técnica",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "herramienta": "Protocolo AEE v1.3"
        },
        "contenido": {
            "url_observada": "https://ejemplo-demo.quantum-humanity.org",
            "hallazgos": [
                "Este es un certificado de demostración",
                "Muestra el funcionamiento del Protocolo AEE",
                "Hash SHA3-512 garantiza integridad"
            ],
            "puntuacion_riesgo": 25,
            "observaciones": "Certificado generado para fines de demostración y validación técnica."
        }
    }
    
    try:
        print(f"\n👤 CONFIGURANDO AUDITOR SOBERANO:")
        print(f"  Nombre: {DEMO_NOMBRE}")
        print(f"  DNI: {DEMO_DNI}")
        print(f"  País: {DEMO_PAIS}")
        
        # Crear motor
        motor = crear_motor_soberano(DEMO_DNI, DEMO_NOMBRE, DEMO_PAIS)
        
        print(f"\n🔑 IDENTIDAD SOBERANA GENERADA:")
        print(f"  Clave Pública: {motor.clave_publica}")
        print(f"  Identificador: {motor.identificador_soberano}")
        
        # Sellar evidencia
        print(f"\n🔨 SELLANDO EVIDENCIA DE DEMOSTRACIÓN...")
        certificado = motor.sellar_evidencia(
            evidencia_demo,
            "https://ejemplo-demo.quantum-humanity.org"
        )
        
        # Exportar
        print(f"\n💾 EXPORTANDO CERTIFICADO...")
        resultado = motor.exportar_certificado(certificado)
        
        if resultado["success"]:
            print(f"\n{'='*70}")
            print("✅ DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
            print('='*70)
            print(f"📄 Archivo: {resultado['archivo']}")
            print(f"🔐 Hash archivo: {resultado['hash_archivo'][:32]}...")
            print(f"📊 Tamaño: {resultado['tamano_bytes']:,} bytes")
            print(f"📍 Ruta: {resultado['ruta_absoluta']}")
            
            # Mostrar resumen
            print(motor.generar_resumen_ejecutivo(certificado))
            
        else:
            print(f"\n❌ ERROR EN EXPORTACIÓN: {resultado['error']}")
            
    except Exception as e:
        print(f"\n❌ ERROR EN DEMOSTRACIÓN: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
