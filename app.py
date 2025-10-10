import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import os
import subprocess
import tempfile

st.set_page_config(page_title="Auditoría Ausentismos", page_icon="📊", layout="wide")

if 'paso_actual' not in st.session_state:
    st.session_state.paso_actual = 1

def crear_zip_desde_archivos(archivos_paths):
    """Crea ZIP desde rutas de archivos existentes"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for ruta in archivos_paths:
            if os.path.exists(ruta):
                zip_file.write(ruta, os.path.basename(ruta))
    return zip_buffer.getvalue()

# ============================================================================
# PASO 1: EJECUTA auditoria_ausentismos_part1.py
# ============================================================================
def paso1():
    st.title("📄 PASO 1: Procesamiento Inicial")
    st.info("Sube CSV + Excel Reporte 45 → Ejecuta part1.py")
    
    col1, col2 = st.columns(2)
    with col1:
        csv_file = st.file_uploader("CSV Ausentismos", type=['csv'], key="csv1")
    with col2:
        excel_file = st.file_uploader("Excel Reporte 45", type=['xlsx', 'xls'], key="excel1")
    
    if csv_file and excel_file:
        try:
            with st.spinner('⏳ Ejecutando part1.py...'):
                # Crear carpeta temporal
                temp_dir = tempfile.mkdtemp()
                
                # Guardar archivos subidos
                csv_path = os.path.join(temp_dir, "input.csv")
                excel_path = os.path.join(temp_dir, "reporte45.xlsx")
                
                with open(csv_path, "wb") as f:
                    f.write(csv_file.getbuffer())
                with open(excel_path, "wb") as f:
                    f.write(excel_file.getbuffer())
                
                # Modificar rutas en part1.py y ejecutar
                import auditoria_ausentismos_part1 as part1
                part1.ruta_entrada_csv = csv_path
                part1.ruta_entrada_excel = excel_path
                part1.directorio_salida = temp_dir
                
                # EJECUTAR
                df_resultado = part1.procesar_archivo_ausentismos()
                
                if df_resultado is not None:
                    st.success(f"✅ Completado: {len(df_resultado):,} registros")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Registros", f"{len(df_resultado):,}")
                    with col2:
                        st.metric("🔑 Llaves", df_resultado['llave'].nunique())
                    with col3:
                        st.metric("📋 Columnas", len(df_resultado.columns))
                    
                    st.dataframe(df_resultado.head(10), use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Buscar archivo generado
                    archivo_salida = os.path.join(temp_dir, "ausentismo_procesado_completo_v2.csv")
                    
                    if os.path.exists(archivo_salida):
                        zip_data = crear_zip_desde_archivos([archivo_salida])
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.download_button(
                                "📥 DESCARGAR ZIP - PASO 1",
                                zip_data,
                                "PASO_1_Procesado.zip",
                                "application/zip",
                                use_container_width=True
                            )
                        with col2:
                            if st.button("▶️ Paso 2", use_container_width=True):
                                st.session_state.paso_actual = 2
                                st.rerun()
                    else:
                        st.warning("⚠️ Archivo no encontrado, pero proceso completado")
                else:
                    st.error("❌ Error en el procesamiento")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver error completo"):
                import traceback
                st.code(traceback.format_exc())

# ============================================================================
# PASO 2: EJECUTA auditoria_ausentismos_part2.py
# ============================================================================
def paso2():
    st.title("🔗 PASO 2: Validaciones y Merge")
    st.info("Sube CSV Paso 1 + Excel Personal → Ejecuta part2.py")
    
    col1, col2 = st.columns(2)
    with col1:
        csv_paso1 = st.file_uploader("CSV del Paso 1", type=['csv'], key="csv2")
    with col2:
        excel_personal = st.file_uploader("Excel Personal (MD_*.xlsx)", type=['xlsx', 'xls'], key="excel2")
    
    if csv_paso1 and excel_personal:
        try:
            with st.spinner('⏳ Ejecutando part2.py...'):
                temp_dir = tempfile.mkdtemp()
                
                # Guardar archivos
                csv_path = os.path.join(temp_dir, "ausentismo_procesado_completo_v2.csv")
                excel_path = os.path.join(temp_dir, "MD_personal.xlsx")
                
                with open(csv_path, "wb") as f:
                    f.write(csv_paso1.getbuffer())
                with open(excel_path, "wb") as f:
                    f.write(excel_personal.getbuffer())
                
                # Ejecutar lógica de part2 directamente
                # (Copiar y pegar código de part2 COMPLETO aquí o importarlo)
                
                # Por ahora, leer y procesar manualmente
                df_ausentismo = pd.read_csv(csv_path, encoding='utf-8-sig')
                df_personal = pd.read_excel(excel_path)
                
                st.info(f"CSV: {len(df_ausentismo):,} | Excel: {len(df_personal):,}")
                
                # Buscar columnas
                col_num_pers = None
                for col in df_personal.columns:
                    if 'pers' in col.lower() or 'personal' in col.lower():
                        col_num_pers = col
                        break
                
                col_relacion = None
                for col in df_personal.columns:
                    if 'relaci' in col.lower() and 'labor' in col.lower():
                        col_relacion = col
                        break
                
                if not col_num_pers or not col_relacion:
                    st.error("❌ Columnas no encontradas")
                    st.stop()
                
                # Merge
                df_ausentismo['id_personal'] = df_ausentismo['id_personal'].astype(str).str.strip()
                df_personal[col_num_pers] = df_personal[col_num_pers].astype(str).str.strip()
                
                df = pd.merge(
                    df_ausentismo,
                    df_personal[[col_num_pers, col_relacion]],
                    left_on='id_personal',
                    right_on=col_num_pers,
                    how='left'
                )
                
                if col_relacion != 'Relación laboral':
                    df.rename(columns={col_relacion: 'Relación laboral'}, inplace=True)
                
                if col_num_pers != 'id_personal' and col_num_pers in df.columns:
                    df.drop(columns=[col_num_pers], inplace=True)
                
                df = df[df['Relación laboral'].notna()]
                
                # Validaciones SENA
                df_aprendizaje = df[df['Relación laboral'].str.contains('Aprendizaje', case=False, na=False)].copy()
                conceptos_validos = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA']
                df_errores_sena = df_aprendizaje[~df_aprendizaje['external_name_label'].isin(conceptos_validos)].copy()
                
                # Validaciones Ley 50
                df_ley50 = df[df['Relación laboral'].str.contains('Ley 50', case=False, na=False)].copy()
                prohibidos = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA',
                             'Inca. Enfer Gral Integral', 'Prorr Inc/Enf Gral ntegra']
                df_errores_ley50 = df_ley50[df_ley50['external_name_label'].isin(prohibidos)].copy()
                
                # Columnas de validación (las 6)
                df['licencia_paternidad'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia Paternidad" and r['calendar_days'] == '14' 
                    else "Concepto No Aplica", axis=1)
                
                df['licencia_maternidad'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia Maternidad" and r['calendar_days'] == '126' 
                    else "Concepto No Aplica", axis=1)
                
                df['ley_de_luto'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Ley de luto" and r['quantity_in_days'] == '5' 
                    else "Concepto No Aplica", axis=1)
                
                df['incap_fuera_de_turno'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Incapa.fuera de turno" and 
                    pd.to_numeric(r['calendar_days'], errors='coerce') <= 1 else "Concepto No Aplica", axis=1)
                
                df['lic_maternidad_sena'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia de Maternidad SENA" and r['calendar_days'] == '126' 
                    else "Concepto No Aplica", axis=1)
                
                df['lic_jurado_votacion'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Lic Jurado Votación" and 
                    pd.to_numeric(r['calendar_days'], errors='coerce') <= 1 else "Concepto No Aplica", axis=1)
                
                # Guardar archivo principal
                archivo_principal = os.path.join(temp_dir, "relacion_laboral_con_validaciones.csv")
                df.to_csv(archivo_principal, index=False, encoding='utf-8-sig')
                
                # Guardar excels de errores
                archivos_generados = [archivo_principal]
                
                if len(df_errores_sena) > 0:
                    path_sena = os.path.join(temp_dir, "Sena_error_validar.xlsx")
                    df_errores_sena.to_excel(path_sena, index=False)
                    archivos_generados.append(path_sena)
                
                if len(df_errores_ley50) > 0:
                    path_ley50 = os.path.join(temp_dir, "Ley_50_error_validar.xlsx")
                    df_errores_ley50.to_excel(path_ley50, index=False)
                    archivos_generados.append(path_ley50)
                
                # Alertas adicionales
                df_alert_pat = df[(df['licencia_paternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Paternidad')]
                if len(df_alert_pat) > 0:
                    path = os.path.join(temp_dir, "alerta_licencia_paternidad.xlsx")
                    df_alert_pat.to_excel(path, index=False)
                    archivos_generados.append(path)
                
                # Incapacidades > 30 días
                conceptos_incap = ['Incapacidad enfermedad general', 'Prorroga Inca/Enfer Gene', 'Enf Gral SOAT', 
                                  'Inc. Accidente de Trabajo', 'Prorroga Inc. Accid. Trab']
                df_incap30 = df[(df['external_name_label'].isin(conceptos_incap)) & 
                               (pd.to_numeric(df['calendar_days'], errors='coerce') > 30)]
                if len(df_incap30) > 0:
                    path = os.path.join(temp_dir, "incp_mayor_30_dias.xlsx")
                    df_incap30.to_excel(path, index=False)
                    archivos_generados.append(path)
                
                st.success(f"✅ Procesado: {len(df):,} registros")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Registros", f"{len(df):,}")
                with col2:
                    st.metric("🚨 Errores SENA", len(df_errores_sena))
                with col3:
                    st.metric("🚨 Errores Ley 50", len(df_errores_ley50))
                
                st.dataframe(df.head(10), use_container_width=True)
                
                st.markdown("---")
                st.success(f"📦 {len(archivos_generados)} archivo(s) generado(s)")
                
                zip_data = crear_zip_desde_archivos(archivos_generados)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.download_button(
                        f"📥 DESCARGAR ZIP - PASO 2 ({len(archivos_generados)} archivos)",
                        zip_data,
                        "PASO_2_Validaciones.zip",
                        "application/zip",
                        use_container_width=True
                    )
                with col2:
                    if st.button("▶️ Paso 3", use_container_width=True):
                        st.session_state.paso_actual = 3
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver error completo"):
                import traceback
                st.code(traceback.format_exc())

# ============================================================================
# PASO 3: EJECUTA auditoria_ausentismos_part3.py  
# ============================================================================
def paso3():
    st.title("🏥 PASO 3: Reporte 45 y CIE-10")
    st.info("Sube CSV Paso 2 + Reporte 45 + CIE-10 → Ejecuta part3.py")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        csv_paso2 = st.file_uploader("CSV Paso 2", type=['csv'], key="csv3")
    with col2:
        excel_r45 = st.file_uploader("Reporte 45 (Excel)", type=['xlsx', 'xls'], key="excel3")
    with col3:
        excel_cie10 = st.file_uploader("CIE-10 (Excel)", type=['xlsx', 'xls'], key="excel4")
    
    if csv_paso2 and excel_r45 and excel_cie10:
        try:
            with st.spinner('⏳ Ejecutando part3.py...'):
                temp_dir = tempfile.mkdtemp()
                
                # Guardar archivos
                csv_path = os.path.join(temp_dir, "relacion_laboral_con_validaciones.csv")
                r45_path = os.path.join(temp_dir, "Reporte45.xlsx")
                cie10_path = os.path.join(temp_dir, "CIE10.xlsx")
                
                with open(csv_path, "wb") as f:
                    f.write(csv_paso2.getbuffer())
                with open(r45_path, "wb") as f:
                    f.write(excel_r45.getbuffer())
                with open(cie10_path, "wb") as f:
                    f.write(excel_cie10.getbuffer())
                
                # Modificar rutas en part3 y ejecutar
                import auditoria_ausentismos_part3 as part3
                part3.ruta_relacion_laboral = csv_path
                part3.ruta_reporte_45_excel = r45_path
                part3.ruta_cie10 = cie10_path
                part3.directorio_salida = temp_dir
                
                # EJECUTAR
                df_resultado = part3.procesar_todo()
                
                if df_resultado is not None:
                    st.success(f"✅ Completado: {len(df_resultado):,} registros")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Registros", f"{len(df_resultado):,}")
                    with col2:
                        alertas = (df_resultado['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum() if 'alerta_diagnostico' in df_resultado.columns else 0
                        st.metric("🚨 Alertas Diag", alertas)
                    with col3:
                        con_cie = df_resultado['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_resultado.columns else 0
                        st.metric("🏥 Con CIE-10", con_cie)
                    
                    st.dataframe(df_resultado.head(10), use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Buscar archivos generados
                    archivo_final = os.path.join(temp_dir, "ausentismos_completo_con_cie10.csv")
                    archivo_alertas = os.path.join(temp_dir, "ALERTA_DIAGNOSTICO.xlsx")
                    
                    archivos = [archivo_final]
                    if os.path.exists(archivo_alertas):
                        archivos.append(archivo_alertas)
                    
                    zip_data = crear_zip_desde_archivos(archivos)
                    
                    st.download_button(
                        f"📥 DESCARGAR ZIP - PASO 3 ({len(archivos)} archivos)",
                        zip_data,
                        "PASO_3_CIE10.zip",
                        "application/zip",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Error en el procesamiento")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver error completo"):
                import traceback
                st.code(traceback.format_exc())

# ============================================================================
# SIDEBAR Y MAIN
# ============================================================================
with st.sidebar:
    st.title("🧭 Navegación")
    st.markdown("---")
    
    progreso = (st.session_state.paso_actual - 1) / 2 * 100
    st.progress(progreso / 100)
    st.markdown(f"**Progreso:** {progreso:.0f}%")
    
    st.markdown("---")
    
    if st.button("1️⃣ Paso 1", use_container_width=True):
        st.session_state.paso_actual = 1
        st.rerun()
    
    if st.button("2️⃣ Paso 2", use_container_width=True):
        st.session_state.paso_actual = 2
        st.rerun()
    
    if st.button("3️⃣ Paso 3", use_container_width=True):
        st.session_state.paso_actual = 3
        st.rerun()

# MAIN
if st.session_state.paso_actual == 1:
    paso1()
elif st.session_state.paso_actual == 2:
    paso2()
elif st.session_state.paso_actual == 3:
    paso3()
