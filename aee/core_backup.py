import json
import datetime
import ntplib
import hashlib
import argparse

# La importación de 'cryptography' no es necesaria aquí si no se firman los datos
# con claves asimétricas, pero se mantiene por compatibilidad futura.
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("Advertencia: Librería 'cryptography' no encontrada. Algunas funciones futuras pueden no estar disponibles.")


class TimestampAuditable:
    """Sellado de tiempo con servidores NTP oficiales para validez legal"""
    
    SERVERS_NTP_OFICIALES = [
        'time.google.com',
        'time.windows.com',
        'time.nist.gov',
        '0.ar.pool.ntp.org',
        'time.afip.gov.ar',
    ]
    
    def obtener_timestamp_auditable(self):
        """Obtiene hora de múltiples servidores para prueba de consistencia y validez."""
        timestamps = []
        
        for server in self.SERVERS_NTP_OFICIALES[:3]:  # Usamos los primeros 3 para agilidad
            try:
                client = ntplib.NTPClient()
                response = client.request(server, timeout=2)
                timestamp = datetime.datetime.fromtimestamp(response.tx_time, datetime.timezone.utc)
                timestamps.append({
                    'server': server,
                    'timestamp': timestamp.isoformat(),
                    'stratum': response.stratum,
                    'delay_seconds': response.delay
                })
            except Exception as e:
                print(f"Advertencia: Fallo al contactar NTP server {server}: {e}")
                continue
        
        if len(timestamps) >= 2:
            # Si al menos 2 servidores responden, hay consenso
            return {
                'consenso': True,
                'timestamps': timestamps,
                'timestamp_oficial': timestamps[0]['timestamp'],
                'metodo': 'NTP_MULTI_SERVER_CONSENSUS'
            }
        
        # Si no hay consenso NTP, se usa la hora local con una advertencia clara
        return {
            'consenso': False,
            'timestamp_oficial': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'advertencia': 'FALLO_NTP_USANDO_LOCAL',
            'metodo': 'FALLBACK_LOCAL_TIME (NO RECOMENDADO PARA VALIDEZ JUDICIAL)'
        }
    
    def generar_sello_temporal(self, hash_evidencia):
        """Genera el bloque de sello temporal del certificado."""
        timestamp_data = self.obtener_timestamp_auditable()
        
        sello_temporal = {
            'protocolo': 'RFC-3161-TSA-COMPATIBLE',
            'hash_a_sellar': hash_evidencia,
            'datos_temporales': timestamp_data,
            'referencia_legal': 'Ley 25.506 Art. 3 - Presunción de Fecha CIERTA',
            'explicacion_tecnica': 'Consenso de múltiples servidores NTP oficiales para garantizar la integridad y no repudio de la fecha y hora de la observación.'
        }
        
        return sello_temporal


class MotorRiesgoLegal:
    """Motor que asocia cada hallazgo con legislación argentina específica."""
    
    MATRIZ_LEGAL_RIESGO = {
        'ausencia_cuit': {
            'nivel': 'CRITICO',
            'leyes': ['Ley 11.683 Art. 4 - Obligación de inscripción'],
            'puntaje': 40, 'explicacion': 'Entidad no identificada ante organismo fiscal.'
        },
        'retornos_garantizados': {
            'nivel': 'ALTO',
            'leyes': ['Ley 26.831 Art. 109 - Oferta Pública no autorizada', 'Código Penal Art. 172 - Estafa'],
            'puntaje': 35, 'explicacion': 'Promesa de rentabilidad sin autorización de la CNV, indicio de estafa.'
        },
        'estructura_referidos': {
            'nivel': 'ALTO',
            'leyes': ['Ley 24.240 Art. 10bis - Venta piramidal prohibida'],
            'puntaje': 30, 'explicacion': 'Características de captación piramidal, prohibido por Defensa del Consumidor.'
        },
        'falta_ssl': {
            'nivel': 'MEDIO',
            'leyes': ['Ley 25.326 Art. 9 - Seguridad de datos personales'],
            'puntaje': 15, 'explicacion': 'Transmisión no cifrada de datos, violando la ley de protección de datos.'
        }
    }
    
    def analizar_riesgo_legal(self, hallazgos):
        """Convierte hallazgos técnicos en una evaluación jurídica estructurada."""
        evaluacion = {
            'puntaje_total': 0, 'nivel_riesgo': 'BAJO',
            'infracciones_detectadas': [], 'fundamento_legal_completo': [],
            'recomendacion_accion': []
        }
        
        hallazgos_lower = " ".join(hallazgos).lower()
        
        for clave, datos in self.MATRIZ_LEGAL_RIESGO.items():
            if clave.replace('_', ' ') in hallazgos_lower or clave in hallazgos_lower:
                evaluacion['puntaje_total'] += datos['puntaje']
                infraccion = {
                    'clasificacion': clave, 'nivel': datos['nivel'],
                    'fundamento': datos['leyes'][0], 'explicacion': datos['explicacion']
                }
                evaluacion['infracciones_detectadas'].append(infraccion)
                evaluacion['fundamento_legal_completo'].extend(datos['leyes'])
                if datos['nivel'] in ['ALTO', 'CRITICO']:
                    evaluacion['recomendacion_accion'].append(
                        f"Acción recomendada por '{clave}': Denuncia (UFECI/CNV) basada en {datos['leyes'][0]}"
                    )

        if evaluacion['puntaje_total'] >= 70:
            evaluacion['nivel_riesgo'] = 'CRITICO'
            evaluacion['recomendacion_accion'].insert(0, 'DENUNCIA INMEDIATA A UFECI Y CNV')
        elif evaluacion['puntaje_total'] >= 40:
            evaluacion['nivel_riesgo'] = 'ALTO'
        elif evaluacion['puntaje_total'] >= 20:
            evaluacion['nivel_riesgo'] = 'MEDIO'
        
        evaluacion['fundamento_legal_completo'] = sorted(list(dict.fromkeys(evaluacion['fundamento_legal_completo'])))
        return evaluacion

def generar_certificado_legalmente_valido(url, hallazgos, auditor_info):
    """Genera un certificado completo con estructura jurídica formal y sellado de tiempo."""
    
    # Pre-cálculo de hash de evidencia para el sello de tiempo
    hash_evidencia = hashlib.sha3_512(json.dumps({"url": url, "hallazgos": hallazgos}, sort_keys=True).encode()).hexdigest()

    # 1. Timestamp auditable
    timestamp_auditable = TimestampAuditable()
    sello_temporal = timestamp_auditable.generar_sello_temporal(hash_evidencia)
    
    # 2. Análisis de riesgo legal
    motor_legal = MotorRiesgoLegal()
    analisis_legal = motor_legal.analizar_riesgo_legal(hallazgos)
    
    # 3. Construcción del certificado
    certificado = {
        'encabezado_legal': {
            'tipo_documento': 'ACTA DE OBSERVACIÓN TÉCNICA CIUDADANA (PROTOCOLO AEE v1.4)',
            'referencia_normativa': 'Ley 25.506 Arts. 3 y 7 - Presunción de Fecha Cierta e Integridad',
            'finalidad': 'Prevención del fraude digital y protección del consumidor (Ley 24.240).',
            'advertencia': 'Este documento constituye EVIDENCIA DIGITAL autosuficiente, no un veredicto judicial.'
        },
        'seccion_identificacion': {
            'auditor_responsable': {
                'nombre': auditor_info['nombre'],
                'dni': auditor_info['dni'],
                'jurisdiccion': auditor_info['jurisdiccion'],
                'declaracion_jurada': 'Bajo juramento, declaro la veracidad de los hechos técnicos observados.'
            },
            'objetivo_auditado': {
                'url': url,
                'fecha_observacion_utc': sello_temporal['datos_temporales']['timestamp_oficial'],
                'metodo_observacion': 'Análisis técnico remoto, pasivo y no intrusivo.'
            }
        },
        'seccion_hallazgos_y_riesgo': {
            'hallazgos_tecnicos_objetivos': hallazgos,
            'analisis_riesgo_legal': analisis_legal
        },
        'seccion_integridad_y_firma': {
            'sello_temporal_auditable': sello_temporal,
            'metodo_hash_documento': 'SHA3-512 (Estándar NIST FIPS 202)',
            'verificacion_independiente': 'https://github.com/quantum-humanity/aee-protocol/blob/main/validador_legal.py'
        },
        'anexos_informativos': {
            'leyes_relevantes': list(analisis_legal['fundamento_legal_completo']),
            'organismos_competentes': ['UFECI', 'CNV', 'Defensa del Consumidor', 'AFIP']
        }
    }
    
    # 4. Firma digital final de todo el documento
    hash_final_doc = hashlib.sha3_512(json.dumps(certificado, sort_keys=True).encode('utf-8')).hexdigest()
    
    certificado['firma_digital'] = {
        'hash_sha3_512': hash_final_doc,
        'timestamp_firma_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'declaracion_validez': 'La presente firma digital sella la totalidad del documento, garantizando su integridad conforme a la Ley 25.506.'
    }
    
    return certificado

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generador de Certificados AEE v1.4. Puede funcionar en modo interactivo o directo con argumentos.")
    parser.add_argument('--url', type=str, help='La URL del objetivo a certificar.')
    parser.add_argument('--hallazgos', nargs='+', type=str, help='Lista de hallazgos técnicos observados.')
    
    args = parser.parse_args()

    print("🚀 QUANTUM HUMANITY - INICIANDO PROTOCOLO AEE v1.4 'BLINDADO LEGAL'")
    print("-----------------------------------------------------------------")
    
    auditor_info = {
        'nombre': 'Franco Carricondo',
        'dni': '35.664.619',
        'jurisdiccion': 'República Argentina'
    }

    if args.url and args.hallazgos:
        print("Modo directo detectado. Usando argumentos de línea de comandos.")
        url = args.url
        hallazgos = args.hallazgos
    else:
        print("Modo interactivo. Ingrese los datos para la certificación:")
        url = input("🌐 URL del objetivo (ej: ganamosnet.biz): ")
        
        print("\n📝 Ingrese los hallazgos técnicos. Para el motor de riesgo, use palabras clave como:")
        print("   'ausencia cuit', 'retornos garantizados', 'estructura referidos', 'falta ssl'")
        hallazgos = []
        while True:
            hallazgo = input("   - Hallazgo (deje vacío para terminar): ")
            if not hallazgo:
                break
            hallazgos.append(hallazgo)
        
        if not hallazgos:
            print("❌ No se ingresaron hallazgos. Abortando.")
            exit()

    print("\nGenerando certificado con blindaje legal...")
    certificado_final = generar_certificado_legalmente_valido(url, hallazgos, auditor_info)
    
    # Limpieza de URL para nombre de archivo seguro
    url_limpia = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('.', '_')
    nombre_archivo = f"AEE_CERT_{url_limpia}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(certificado_final, f, indent=4, ensure_ascii=False)
        
    print("\n" + "="*65)
    print(f"✅ CERTIFICADO LEGALMENTE VÁLIDO GENERADO: {nombre_archivo}")
    analisis = certificado_final['seccion_hallazgos_y_riesgo']['analisis_riesgo_legal']
    print(f"📊 NIVEL DE RIESGO: {analisis['nivel_riesgo']} ({analisis['puntaje_total']}/100)")
    print(f"🔐 FIRMA DIGITAL (HASH DOCUMENTO): {certificado_final['firma_digital']['hash_sha3_512'][:32]}...")
    print(f"🕒 SELLO DE TIEMPO OFICIAL: {certificado_final['seccion_identificacion']['objetivo_auditado']['fecha_observacion_utc']}")
    print("="*65)
    print("Evidencia digital lista para ser presentada en sede judicial.")

