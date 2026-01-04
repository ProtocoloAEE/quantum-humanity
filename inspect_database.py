#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspector de base de datos SQLite para AEE Bot v3.0
Muestra estructura, registros y estadísticas
"""

import sqlite3
import os
import sys
from datetime import datetime
from tabulate import tabulate

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

DB_PATH = "aee_preservations.db"

def inspect_database():
    """Inspecciona completamente la BD SQLite."""
    
    print("\n" + "="*80)
    print("INSPECTOR DE BASE DE DATOS - AEE Bot v3.0")
    print("="*80 + "\n")
    
    # Verificar que la BD existe
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Base de datos no encontrada: {DB_PATH}")
        return
    
    file_size = os.path.getsize(DB_PATH)
    print(f"Archivo: {DB_PATH}")
    print(f"Tamano: {file_size} bytes ({file_size/1024:.2f} KB)\n")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # ============================================================================
        # 1. ESQUEMA DE TABLAS
        # ============================================================================
        print("\n" + "-"*80)
        print("ESQUEMA DE TABLAS")
        print("-"*80)
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name;
        """)
        
        tables = cursor.fetchall()
        
        if not tables:
            print("No hay tablas en la BD")
            return
        
        for table in tables:
            table_name = table[0]
            print(f"\nTabla: {table_name}")
            
            # Obtener esquema de la tabla
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("\n  Columnas:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                nullable = "NOT NULL" if not_null else "NULL"
                pk_marker = " [PRIMARY KEY]" if pk else ""
                print(f"    • {col_name}: {col_type} {nullable}{pk_marker}")
        
        # ============================================================================
        # 2. ESTADÍSTICAS
        # ============================================================================
        print("\n\n" + "-"*80)
        print("ESTADISTICAS")
        print("-"*80)
        
        cursor.execute("SELECT COUNT(*) as total FROM preservations;")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(file_size) as total_size FROM preservations;")
        total_size = cursor.fetchone()[0] or 0
        
        print(f"\n  Total de registros: {total_records}")
        print(f"  Tamaño total de archivos: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
        
        if total_records > 0:
            cursor.execute("SELECT COUNT(DISTINCT user_id) as users FROM preservations;")
            unique_users = cursor.fetchone()[0]
            print(f"  Usuarios únicos: {unique_users}")
        
        # ============================================================================
        # 3. REGISTROS
        # ============================================================================
        if total_records == 0:
            print("\n\n" + "-"*80)
            print("NO HAY REGISTROS EN LA BD")
            print("-"*80)
            print("\nPróximos pasos:")
            print("  1. Envía una foto/documento al bot en Telegram")
            print("  2. El bot calculará el hash SHA-256")
            print("  3. Se registrará automáticamente en esta BD")
            print("  4. Ejecuta este script nuevamente para ver los registros")
        else:
            print("\n\n" + "-"*80)
            print(f"REGISTROS ({total_records} preservaciones)")
            print("-"*80 + "\n")
            
            cursor.execute("""
                SELECT 
                    id,
                    file_hash,
                    file_name,
                    mime_type,
                    file_size,
                    user_id,
                    timestamp_utc,
                    cryptographic_signature
                FROM preservations
                ORDER BY timestamp_utc DESC
            """)
            
            records = cursor.fetchall()
            
            for i, record in enumerate(records, 1):
                record_id = record[0]
                file_hash = record[1]
                file_name = record[2] or "N/A"
                mime_type = record[3] or "N/A"
                file_size = record[4]
                user_id = record[5]
                timestamp = record[6]
                cryptographic_sig = record[7]
                
                print(f"\n  [{i}] ID: {record_id}")
                print(f"      Archivo: {file_name}")
                print(f"      Tipo MIME: {mime_type}")
                print(f"      Tamaño: {file_size:,} bytes ({file_size/1024:.2f} KB)")
                print(f"      Usuario (Telegram ID): {user_id}")
                print(f"      Timestamp UTC: {timestamp}")
                print(f"      Hash SHA-256: {file_hash}")
                
                if cryptographic_sig:
                    print(f"      Firma Criptográfica: {cryptographic_sig[:50]}...")
                else:
                    print(f"      Firma Criptográfica: [Pendiente de implementación]")
                
                print()
        
        # ============================================================================
        # 4. VERIFICACIONES DE INTEGRIDAD
        # ============================================================================
        print("\n" + "-"*80)
        print("VERIFICACIONES DE INTEGRIDAD")
        print("-"*80)
        
        # Verificar hashes únicos
        cursor.execute("""
            SELECT COUNT(*) as total, COUNT(DISTINCT file_hash) as unique_hashes
            FROM preservations
        """)
        total, unique = cursor.fetchone()
        
        if total == unique:
            print(f"\n  Todos los hashes son únicos ({unique})")
        else:
            print(f"\n  Se encontraron hashes duplicados:")
            cursor.execute("""
                SELECT file_hash, COUNT(*) as count
                FROM preservations
                GROUP BY file_hash
                HAVING count > 1
            """)
            duplicates = cursor.fetchall()
            for dup in duplicates:
                print(f"     • Hash {dup[0]}: {dup[1]} registros")
        
        # Verificar timestamps válidos
        cursor.execute("""
            SELECT COUNT(*) as invalid
            FROM preservations
            WHERE timestamp_utc IS NULL
        """)
        invalid = cursor.fetchone()[0]
        
        if invalid == 0:
            print(f"  Todos los timestamps son válidos")
        else:
            print(f"  {invalid} registros sin timestamp")
        
        # Verificar user_ids
        cursor.execute("""
            SELECT COUNT(*) as no_user
            FROM preservations
            WHERE user_id IS NULL OR user_id = ''
        """)
        no_user = cursor.fetchone()[0]
        
        if no_user == 0:
            print(f"  Todos los registros tienen user_id")
        else:
            print(f"  {no_user} registros sin user_id")
        
        # ============================================================================
        # 5. ÍNDICES
        # ============================================================================
        print("\n\n" + "-"*80)
        print("INDICES (Optimización)")
        print("-"*80 + "\n")
        
        cursor.execute("""
            SELECT name, tbl_name, sql
            FROM sqlite_master
            WHERE type='index' AND tbl_name='preservations'
        """)
        
        indexes = cursor.fetchall()
        
        if indexes:
            for idx in indexes:
                idx_name = idx[0]
                if not idx_name.startswith('sqlite_'):
                    print(f"  • {idx_name}")
        else:
            print("  No hay índices personalizados")
        
        # ============================================================================
        # RESUMEN FINAL
        # ============================================================================
        print("\n\n" + "="*80)
        print("INSPECCION COMPLETADA")
        print("="*80 + "\n")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"ERROR de base de datos: {e}")
    except Exception as e:
        print(f"ERROR inesperado: {e}")


if __name__ == '__main__':
    inspect_database()
