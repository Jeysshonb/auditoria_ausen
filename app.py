import pandas as pd
import numpy as np
import warnings
import os
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN DE RUTAS (Se pueden sobrescribir desde la app)
# ============================================================================
ruta_relacion_laboral = None
ruta_reporte_45_excel = None
ruta_cie10 = None
directorio_salida = None
ruta_completa_salida = None
ruta_alertas = None

# ============================================================================
# FUNCIÓN AUXILIAR: PARSEO DE FECHAS ROBUSTO
# ============================================================================
def parsear_fecha_flexible(fecha_str):
    """
    Intenta parsear una fecha en múltiples formatos comunes.
    Retorna un objeto datetime o NaT si falla.
    """
    if pd.isna(fecha_str) or fecha_str == '':
        return pd.NaT
    
    fecha_str = str(fecha_str).strip()
    
    # Lista de formatos a probar
    formatos = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M:%S',
        '%d-%m-%Y %H:%M:%S',
        '%Y-%m-%d %H:%M:%S'
    ]
    
    for formato in formatos:
        try:
            return pd.to_datetime(fecha_str, format=formato)
        except:
            continue
    
    # Si ningún formato funciona, intentar parseo automático
    try:
        fecha_parseada = pd.to_datetime(fecha_str, dayfirst=False, errors='coerce')
        return fecha_parseada
    except:
        return pd.NaT

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def procesar_todo():
    """
    Procesa todo el flujo del Paso 3:
    1. Carga datos del Paso 2
    2. Filtra subtipos específicos
    3. Merge con Reporte 45
    4. Valida diagnósticos
    5. Enriquece con CIE-10
    6. Genera archivos de salida
    """
    
    # ========================================================================
    # 1. VALIDAR RUTAS
    # ========================================================================
    if not all([ruta_relacion_laboral, ruta_reporte_45_excel, ruta_cie10, directorio_salida]):
        print("❌ ERROR: Faltan rutas de configuración")
        return None
    
    # Crear directorio de salida si no existe
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Configurar rutas de archivos de salida
    global ruta_completa_salida, ruta_alertas
    if ruta_completa_salida is None:
        ruta_completa_salida = os.path.join(directorio_salida, "ausentismos_completo_con_cie10.csv")
    if ruta_alertas is None:
        ruta_alertas = os.path.join(directorio_salida, "ALERTA_DIAGNOSTICO.xlsx")
    
    print("\n" + "="*70)
    print("🏥 PASO 3: MERGE CON REPORTE 45 Y CIE-10")
    print("="*70)
    
    # ========================================================================
    # 2. CARGAR DATOS DEL PASO 2
    # ========================================================================
    print("\n📂 Cargando archivo del Paso 2...")
    try:
        df = pd.read_csv(ruta_relacion_laboral, encoding='utf-8-sig')
        print(f"✅ Cargado: {len(df):,} registros, {len(df.columns)} columnas")
    except Exception as e:
        print(f"❌ Error al cargar CSV del Paso 2: {e}")
        return None
    
    # ========================================================================
    # 3. FILTRAR SUBTIPOS ESPECÍFICOS
    # ========================================================================
    print("\n🔍 Filtrando 17 subtipos específicos...")
    
    subtipos_validos = [
        'Incapacidad enfermedad general',
        'Prorroga Inca/Enfer Gene',
        'Enf Gral SOAT',
        'Inc. Accidente de Trabajo',
        'Prorroga Inc. Accid. Trab',
        'Incapacidad gral SENA',
        'Licencia Maternidad',
        'Licencia de Maternidad SENA',
        'Licencia Paternidad',
        'Calamidad domestica',
        'Ley de luto',
        'Otros permisos',
        'Día de la familia',
        'Susp. Contrato de Trabajo',
        'Suspensión contrato SENA',
        'Incapa.fuera de turno',
        'Inca. Enfer Gral Integral'
    ]
    
    df_filtrado = df[df['external_name_label'].isin(subtipos_validos)].copy()
    print(f"✅ Registros después del filtro: {len(df_filtrado):,}")
    print(f"   Registros eliminados: {len(df) - len(df_filtrado):,}")
    
    if len(df_filtrado) == 0:
        print("⚠️ WARNING: No quedan registros después del filtro")
        return None
    
    # ========================================================================
    # 4. CARGAR Y PROCESAR REPORTE 45
    # ========================================================================
    print("\n📂 Cargando Reporte 45 desde Excel...")
    try:
        df_r45 = pd.read_excel(ruta_reporte_45_excel)
        print(f"✅ Cargado: {len(df_r45):,} registros")
    except Exception as e:
        print(f"❌ Error al cargar Reporte 45: {e}")
        return None
    
    # Limpiar nombres de columnas
    df_r45.columns = df_r45.columns.str.strip()
    
    print("\n🔧 Preparando Reporte 45 para merge...")
    
    # Identificar columnas necesarias
    col_fecha_inicio = next((col for col in df_r45.columns if 'inicio' in col.lower() and 'fecha' in col.lower()), None)
    col_fecha_fin = next((col for col in df_r45.columns if 'fin' in col.lower() and 'fecha' in col.lower()), None)
    col_diagnostico = next((col for col in df_r45.columns if 'diagn' in col.lower()), None)
    col_empleado = next((col for col in df_r45.columns if 'empl' in col.lower() or 'pers' in col.lower()), None)
    
    print(f"   Columna Fecha Inicio: {col_fecha_inicio}")
    print(f"   Columna Fecha Fin: {col_fecha_fin}")
    print(f"   Columna Diagnóstico: {col_diagnostico}")
    print(f"   Columna Empleado: {col_empleado}")
    
    if not all([col_fecha_inicio, col_fecha_fin, col_diagnostico, col_empleado]):
        print("⚠️ WARNING: No se encontraron todas las columnas necesarias en Reporte 45")
        print("   Columnas disponibles:", df_r45.columns.tolist())
        return None
    
    # Renombrar columnas estándar
    df_r45 = df_r45.rename(columns={
        col_fecha_inicio: 'fecha_inicio_r45',
        col_fecha_fin: 'fecha_fin_r45',
        col_diagnostico: 'diagnostico',
        col_empleado: 'empleado_num'
    })
    
    # Convertir empleado a string
    df_r45['empleado_num'] = df_r45['empleado_num'].astype(str).str.strip()
    
    # Parsear fechas usando función robusta
    print("   Parseando fechas...")
    df_r45['fecha_inicio_r45'] = df_r45['fecha_inicio_r45'].apply(parsear_fecha_flexible)
    df_r45['fecha_fin_r45'] = df_r45['fecha_fin_r45'].apply(parsear_fecha_flexible)
    
    # Crear llave de merge
    df_r45['llave_merge'] = (
        df_r45['empleado_num'].astype(str) + '_' +
        df_r45['fecha_inicio_r45'].dt.strftime('%Y-%m-%d') + '_' +
        df_r45['fecha_fin_r45'].dt.strftime('%Y-%m-%d')
    )
    
    print(f"✅ Reporte 45 preparado con {len(df_r45):,} registros")
    
    # ========================================================================
    # 5. PREPARAR DF_FILTRADO PARA MERGE
    # ========================================================================
    print("\n🔧 Preparando datos filtrados para merge...")
    
    # Convertir fechas si no están ya en formato datetime
    if 'fecha_inicio' not in df_filtrado.columns or 'fecha_fin' not in df_filtrado.columns:
        print("⚠️ WARNING: No se encuentran columnas fecha_inicio/fecha_fin")
        return None
    
    df_filtrado['fecha_inicio'] = pd.to_datetime(df_filtrado['fecha_inicio'], errors='coerce')
    df_filtrado['fecha_fin'] = pd.to_datetime(df_filtrado['fecha_fin'], errors='coerce')
    
    # Convertir id_personal a string
    df_filtrado['id_personal'] = df_filtrado['id_personal'].astype(str).str.strip()
    
    # Crear llave de merge
    df_filtrado['llave_merge'] = (
        df_filtrado['id_personal'].astype(str) + '_' +
        df_filtrado['fecha_inicio'].dt.strftime('%Y-%m-%d') + '_' +
        df_filtrado['fecha_fin'].dt.strftime('%Y-%m-%d')
    )
    
    print(f"✅ Datos preparados: {len(df_filtrado):,} registros con llave de merge")
    
    # ========================================================================
    # 6. MERGE CON REPORTE 45
    # ========================================================================
    print("\n🔗 Realizando merge con Reporte 45...")
    
    # Seleccionar solo columnas necesarias de R45
    df_r45_mini = df_r45[['llave_merge', 'diagnostico']].copy()
    
    # Merge
    df_merged = pd.merge(
        df_filtrado,
        df_r45_mini,
        on='llave_merge',
        how='left'
    )
    
    print(f"✅ Merge completado: {len(df_merged):,} registros")
    
    # ========================================================================
    # 7. VALIDAR DIAGNÓSTICOS REQUERIDOS
    # ========================================================================
    print("\n🩺 Validando diagnósticos requeridos...")
    
    conceptos_requieren_diagnostico = [
        'Incapacidad enfermedad general',
        'Prorroga Inca/Enfer Gene',
        'Enf Gral SOAT',
        'Inc. Accidente de Trabajo',
        'Prorroga Inc. Accid. Trab',
        'Incapacidad gral SENA',
        'Licencia Maternidad',
        'Licencia de Maternidad SENA',
        'Licencia Paternidad',
        'Incapa.fuera de turno',
        'Inca. Enfer Gral Integral'
    ]
    
    # Crear columna de alerta
    df_merged['alerta_diagnostico'] = df_merged.apply(
        lambda row: 'ALERTA DIAGNOSTICO' 
        if row['external_name_label'] in conceptos_requieren_diagnostico and pd.isna(row['diagnostico'])
        else 'OK',
        axis=1
    )
    
    alertas_count = (df_merged['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum()
    print(f"⚠️ Registros con alerta de diagnóstico: {alertas_count:,}")
    
    # ========================================================================
    # 8. CARGAR Y PROCESAR CIE-10
    # ========================================================================
    print("\n📂 Cargando tabla CIE-10...")
    try:
        df_cie10 = pd.read_excel(ruta_cie10)
        print(f"✅ Cargado: {len(df_cie10):,} códigos CIE-10")
    except Exception as e:
        print(f"❌ Error al cargar CIE-10: {e}")
        return None
    
    # Limpiar columnas
    df_cie10.columns = df_cie10.columns.str.strip()
    
    # Identificar columna de código
    col_codigo = next((col for col in df_cie10.columns if 'cod' in col.lower() or 'clave' in col.lower()), None)
    
    if col_codigo is None:
        print("⚠️ WARNING: No se encontró columna de código en CIE-10")
        print("   Columnas disponibles:", df_cie10.columns.tolist())
        col_codigo = df_cie10.columns[0]
        print(f"   Usando primera columna: {col_codigo}")
    
    df_cie10 = df_cie10.rename(columns={col_codigo: 'cie10_codigo'})
    
    # Limpiar código
    df_cie10['cie10_codigo'] = df_cie10['cie10_codigo'].astype(str).str.strip().str.upper()
    df_merged['diagnostico'] = df_merged['diagnostico'].astype(str).str.strip().str.upper()
    
    print(f"✅ CIE-10 preparado con columna: {col_codigo}")
    
    # ========================================================================
    # 9. MERGE CON CIE-10
    # ========================================================================
    print("\n🔗 Enriqueciendo con información CIE-10...")
    
    df_final = pd.merge(
        df_merged,
        df_cie10,
        left_on='diagnostico',
        right_on='cie10_codigo',
        how='left'
    )
    
    registros_con_cie10 = df_final['cie10_codigo'].notna().sum()
    print(f"✅ Registros enriquecidos con CIE-10: {registros_con_cie10:,}")
    print(f"   Registros sin match CIE-10: {len(df_final) - registros_con_cie10:,}")
    
    # ========================================================================
    # 10. GUARDAR ARCHIVO PRINCIPAL
    # ========================================================================
    print("\n💾 Guardando archivo principal...")
    try:
        df_final.to_csv(ruta_completa_salida, index=False, encoding='utf-8-sig', quoting=1, lineterminator='\n')
        print(f"✅ Guardado: {os.path.basename(ruta_completa_salida)}")
        print(f"   Ruta: {ruta_completa_salida}")
    except Exception as e:
        print(f"❌ Error al guardar archivo principal: {e}")
        return None
    
    # ========================================================================
    # 11. GENERAR ARCHIVO DE ALERTAS
    # ========================================================================
    print("\n📊 Generando archivo de alertas...")
    
    df_alertas = df_final[df_final['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO'].copy()
    
    if len(df_alertas) > 0:
        try:
            df_alertas.to_excel(ruta_alertas, index=False)
            print(f"✅ Guardado: {os.path.basename(ruta_alertas)}")
            print(f"   Alertas generadas: {len(df_alertas):,}")
        except Exception as e:
            print(f"⚠️ Error al guardar alertas: {e}")
    else:
        print("✅ No hay alertas de diagnóstico para generar archivo")
    
    # ========================================================================
    # 12. RESUMEN FINAL
    # ========================================================================
    print("\n" + "="*70)
    print("📊 RESUMEN FINAL - PASO 3")
    print("="*70)
    print(f"✅ Total registros procesados: {len(df_final):,}")
    print(f"✅ Registros con CIE-10: {registros_con_cie10:,}")
    print(f"⚠️ Alertas de diagnóstico: {alertas_count:,}")
    print(f"✅ Columnas totales: {len(df_final.columns)}")
    print(f"✅ Archivo principal: {os.path.basename(ruta_completa_salida)}")
    if len(df_alertas) > 0:
        print(f"✅ Archivo alertas: {os.path.basename(ruta_alertas)}")
    print("="*70)
    
    return df_final

# ============================================================================
# EJECUCIÓN DIRECTA (PARA TESTING)
# ============================================================================
if __name__ == "__main__":
    print("⚠️ Este script debe ser ejecutado desde la aplicación Streamlit")
    print("   O configura las rutas manualmente antes de ejecutar")
