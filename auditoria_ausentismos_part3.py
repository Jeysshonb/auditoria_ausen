import pandas as pd
import os
from datetime import datetime

# ===== CONFIGURACIÓN DE RUTAS =====
# Archivos de entrada
ruta_reporte_45_excel = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_planos\Reporte 45_012025_082025_26082025.XLSX"
ruta_relacion_laboral = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida\relacion_laboral_con_validaciones.csv"
ruta_cie10 = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_planos\CIE 10 - AJUSTADO - NÓMINA.xlsx"

# Directorio de salida
directorio_salida = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida"
archivo_final = "ausentismos_completo_con_cie10.csv"
ruta_completa_salida = os.path.join(directorio_salida, archivo_final)

# ===== FILTRO DE 17 SUBTIPOS =====
SUBTIPOS_FILTRO = [
    'Enf Gral Int SOAT',
    'Enf Gral SOAT',
    'Inc. Acci Trabajo Integra',
    'Inc. Accidente de Trabajo',
    'Inc. Enfer. General Hospi',
    'Inc. Enfermed Profesional',
    'Inca. Enfer Gral Integral',
    'Inca. Enfermedad  General',
    'Incap  mayor 180 dias',
    'Incap  mayor 540 dias',
    'Incapa.fuera de turno',
    'Prorr Enf Gral Int SOAT',
    'Prorr Inc.Accid. Tr Integ',
    'Prorr Inc/Enf Gral ntegra',
    'Prorroga Enf Gral SOAT',
    'Prorroga Inc. Accid. Trab',
    'Prorroga Inca/Enfer Gene'
]


def limpiar_fecha_para_llave(fecha):
    """Convierte fecha a formato DDMMYYYY para la llave"""
    if pd.isna(fecha) or fecha == '' or str(fecha).lower() in ['nan', 'none', 'nat']:
        return ''
    
    try:
        if isinstance(fecha, (pd.Timestamp, datetime)):
            return fecha.strftime('%d%m%Y')
        
        fecha_str = str(fecha).strip()
        fecha_parseada = pd.to_datetime(fecha_str, dayfirst=True, errors='coerce')
        
        if pd.notna(fecha_parseada):
            return fecha_parseada.strftime('%d%m%Y')
        
        fecha_limpia = ''.join(c for c in fecha_str if c.isdigit())
        if len(fecha_limpia) == 8:
            return fecha_limpia
        
        return fecha_limpia
        
    except:
        return ''


def procesar_todo():
    """Función principal que ejecuta todo el proceso"""
    
    print("=" * 80)
    print("PROCESO COMPLETO: AUDITORÍA AUSENTISMOS")
    print("=" * 80)
    
    try:
        # ============================================
        # PARTE 1: PROCESAR REPORTE 45 Y CREAR LLAVE
        # ============================================
        print("\n[PARTE 1/3] PROCESANDO REPORTE 45")
        print("-" * 80)
        
        print("\n[1.1] Leyendo Excel Reporte 45...")
        df_reporte45 = pd.read_excel(ruta_reporte_45_excel, dtype=str)
        print(f"      Registros: {len(df_reporte45)}")
        
        # Verificar columnas necesarias
        columnas_necesarias = ['Número de personal', 'Clase absent./pres.', 'Inicio de validez', 'Fin de validez']
        faltantes = [col for col in columnas_necesarias if col not in df_reporte45.columns]
        if faltantes:
            print(f"      ❌ Faltan columnas: {faltantes}")
            return None
        
        print("\n[1.2] Creando llave_report_45...")
        df_reporte45['inicio_limpio'] = df_reporte45['Inicio de validez'].apply(limpiar_fecha_para_llave)
        df_reporte45['fin_limpio'] = df_reporte45['Fin de validez'].apply(limpiar_fecha_para_llave)
        
        # Limpiar formato de fechas (quitar hora 0:00)
        for col in ['Inicio de validez', 'Fin de validez', 'Modificado el', 'Final Salario enfer.']:
            if col in df_reporte45.columns:
                df_reporte45[col] = pd.to_datetime(df_reporte45[col], errors='coerce').dt.strftime('%d/%m/%Y')
        
        df_reporte45['llave_report_45'] = (
            'K' +
            df_reporte45['Número de personal'].astype(str).fillna('') +
            df_reporte45['inicio_limpio'] +
            df_reporte45['fin_limpio'] +
            df_reporte45['Clase absent./pres.'].astype(str).fillna('')
        )
        
        df_reporte45 = df_reporte45.drop(['inicio_limpio', 'fin_limpio'], axis=1)
        print(f"      ✅ Llave creada. Ejemplo: {df_reporte45['llave_report_45'].iloc[0]}")
        
        # ============================================
        # PARTE 2: MERGE CON RELACIÓN LABORAL
        # ============================================
        print("\n[PARTE 2/3] MERGE CON RELACIÓN LABORAL")
        print("-" * 80)
        
        print("\n[2.1] Leyendo Relación Laboral...")
        df_relacion = pd.read_csv(ruta_relacion_laboral, encoding='utf-8-sig', dtype=str)
        print(f"      Registros: {len(df_relacion)}")
        
        print(f"\n[2.2] Aplicando filtro de {len(SUBTIPOS_FILTRO)} subtipos...")
        if 'external_name_label' in df_relacion.columns:
            antes = len(df_relacion)
            df_relacion = df_relacion[df_relacion['external_name_label'].isin(SUBTIPOS_FILTRO)]
            despues = len(df_relacion)
            print(f"      Antes: {antes} | Después: {despues} | Descartados: {antes - despues}")
            
            if despues == 0:
                print("      ❌ No quedaron registros después del filtro")
                return None
        else:
            print("      ⚠️  Columna 'external_name_label' no encontrada")
        
        # Verificar llaves
        if 'llave' not in df_relacion.columns:
            print("      ❌ Falta columna 'llave' en Relación Laboral")
            return None
        
        print("\n[2.3] Realizando merge INNER por llave...")
        llaves_relacion = set(df_relacion['llave'].dropna())
        llaves_reporte = set(df_reporte45['llave_report_45'].dropna())
        coincidencias = llaves_relacion.intersection(llaves_reporte)
        
        print(f"      Coincidencias: {len(coincidencias)}/{len(llaves_relacion)} ({(len(coincidencias)/len(llaves_relacion)*100):.1f}%)")
        
        df_merged = pd.merge(
            df_relacion,
            df_reporte45,
            left_on='llave',
            right_on='llave_report_45',
            how='inner',
            suffixes=('_relacion', '_reporte45')
        )
        print(f"      ✅ Registros con match: {len(df_merged)}")
        
        # Crear columna ALERTA_DIAGNOSTICO
        print("\n[2.4] Creando columna ALERTA_DIAGNOSTICO...")
        valores_requieren_diagnostico = [
            'Inca. Enfermedad  General', 'Prorroga Inca/Enfer Gene', 'Inc. Accidente de Trabajo',
            'Enf Gral SOAT', 'Prorroga Enf Gral SOAT', 'Licencia Paternidad', 'Prorroga Inc. Accid. Trab',
            'Incapacidad gral SENA', 'Inca. Enfer Gral Integral', 'Licencia Paternidad Inegr',
            'Licencia Maternidad', 'Incap  mayor 180 dias', 'Incap  mayor 540 dias',
            'Lic Mater Interrumpida', 'Licencia Mater especial', 'Enf Gral Int SOAT',
            'Inc. Enfer. General Hospi', 'Prorr Inc/Enf Gral ntegra', 'Incapacidad ARL SENA',
            'Licencia Maternidad Integ'
        ]
        
        columnas_diagnostico = ['Descripc.enfermedad.1', 'descripcion_enfermedad', 
                               'Descripc.enfermedad.1_reporte45', 'descripcion_enfermedad_reporte45']
        
        col_diag = None
        for col in columnas_diagnostico:
            if col in df_merged.columns:
                col_diag = col
                break
        
        if 'external_name_label' in df_merged.columns and col_diag:
            def validar_diagnostico(row):
                tipo = str(row['external_name_label']).strip()
                diagnostico = str(row[col_diag]).strip()
                if tipo in valores_requieren_diagnostico and (diagnostico == '' or diagnostico.lower() in ['nan', 'none', 'nat']):
                    return 'ALERTA DIAGNOSTICO'
                return ''
            
            df_merged['alerta_diagnostico'] = df_merged.apply(validar_diagnostico, axis=1)
            alertas = (df_merged['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum()
            print(f"      ✅ Alertas: {alertas} ({(alertas/len(df_merged)*100):.1f}%)")
        else:
            df_merged['alerta_diagnostico'] = ''
            print("      ⚠️  No se pudo crear columna de alertas")
        
        # ============================================
        # PARTE 3: MERGE CON CIE 10
        # ============================================
        print("\n[PARTE 3/3] MERGE CON CIE 10")
        print("-" * 80)
        
        print("\n[3.1] Leyendo tabla CIE 10...")
        df_cie10 = pd.read_excel(ruta_cie10, dtype=str)
        print(f"      Registros: {len(df_cie10)}")
        
        # Verificar columnas CIE 10
        if 'Código' not in df_cie10.columns:
            print("      ❌ Falta columna 'Código' en CIE 10")
            return None
        
        columnas_cie10 = ['Código', 'Descripción', 'TIPO', 'Clasificación Sistemas JMC']
        df_cie10_subset = df_cie10[[col for col in columnas_cie10 if col in df_cie10.columns]].copy()
        
        # Verificar columna de merge en df_merged
        if 'descripcion_general_external_code' not in df_merged.columns:
            print("      ❌ Falta columna 'descripcion_general_external_code'")
            return None
        
        print("\n[3.2] Realizando merge LEFT con CIE 10...")
        # Limpiar código: quitar asteriscos, espacios y convertir a mayúsculas
        df_merged['codigo_clean'] = df_merged['descripcion_general_external_code'].str.strip().str.replace('*', '', regex=False).str.upper()
        df_cie10_subset['Código_clean'] = df_cie10_subset['Código'].str.strip().str.replace('*', '', regex=False).str.upper()
        
        codigos_base = set(df_merged['codigo_clean'].dropna())
        codigos_cie10 = set(df_cie10_subset['Código_clean'].dropna())
        coincidencias_cie = codigos_base.intersection(codigos_cie10)
        
        print(f"      Coincidencias: {len(coincidencias_cie)}/{len(codigos_base)} ({(len(coincidencias_cie)/len(codigos_base)*100):.1f}%)")
        
        df_final = pd.merge(
            df_merged,
            df_cie10_subset,
            left_on='codigo_clean',
            right_on='Código_clean',
            how='left',
            suffixes=('', '_cie10')
        )
        
        # Renombrar columnas CIE 10
        renombrado = {
            'Código': 'cie10_codigo', 
            'Descripción': 'cie10_descripcion', 
            'TIPO': 'cie10_tipo',
            'Clasificación Sistemas JMC': 'cie10_clasificacion_sistemas_jmc'
        }
        df_final = df_final.rename(columns={col: renombrado.get(col, col) for col in df_final.columns if col in renombrado})
        
        # Limpiar columnas temporales
        df_final = df_final.drop(['codigo_clean'], axis=1)
        if 'Código_clean' in df_final.columns:
            df_final = df_final.drop(['Código_clean'], axis=1)
        
        registros_con_cie10 = df_final['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_final.columns else 0
        print(f"      ✅ Registros con CIE 10: {registros_con_cie10} ({(registros_con_cie10/len(df_final)*100):.1f}%)")
        
        # ============================================
        # GENERAR EXCEL DE ALERTA DIAGNOSTICO
        # ============================================
        print("\n[3.3] Generando Excel de ALERTA_DIAGNOSTICO...")
        
        if 'alerta_diagnostico' in df_final.columns:
            df_alertas = df_final[df_final['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO'].copy()
            
            if len(df_alertas) > 0:
                archivo_alertas = os.path.join(directorio_salida, "ALERTA_DIAGNOSTICO.xlsx")
                df_alertas.to_excel(archivo_alertas, index=False, engine='openpyxl')
                print(f"      ✅ Excel generado: {len(df_alertas)} registros con alerta")
                print(f"      📁 {archivo_alertas}")
            else:
                print(f"      ℹ️  No hay registros con ALERTA DIAGNOSTICO")
        else:
            print(f"      ⚠️  Columna 'alerta_diagnostico' no existe")
        
        # ============================================
        # GUARDAR ARCHIVO FINAL
        # ============================================
        print("\n[GUARDANDO ARCHIVO FINAL]")
        print("-" * 80)
        
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
        
        df_final.to_csv(ruta_completa_salida, index=False, encoding='utf-8-sig', quoting=1, lineterminator='\n')
        
        print("\n" + "=" * 80)
        print("✅ PROCESO COMPLETADO")
        print("=" * 80)
        print(f"Registros finales: {len(df_final)}")
        print(f"Columnas totales: {len(df_final.columns)}")
        print(f"Con CIE 10: {registros_con_cie10}")
        print(f"Archivo: {ruta_completa_salida}")
        print("=" * 80)
        
        return df_final
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: Archivo no encontrado")
        print(f"   {str(e)}")
        return None
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\nVerificando archivos de entrada...")
    archivos = {
        "Reporte 45 Excel": ruta_reporte_45_excel,
        "Relación Laboral": ruta_relacion_laboral,
        "CIE 10": ruta_cie10
    }
    
    todos_ok = True
    for nombre, ruta in archivos.items():
        if os.path.exists(ruta):
            print(f"   ✅ {nombre}")
        else:
            print(f"   ❌ {nombre}: NO ENCONTRADO")
            todos_ok = False
    
    if todos_ok:
        print("\n¡Todos los archivos encontrados! Iniciando proceso...\n")
        resultado = procesar_todo()
        if resultado is None:
            print("\n❌ El proceso falló.")
    else:
        print("\n❌ Verifica las rutas de los archivos.")
