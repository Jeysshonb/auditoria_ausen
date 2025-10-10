import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import os
import tempfile

st.set_page_config(
    page_title="Auditoría Ausentismos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS CSS - CORREGIDOS
# ============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        color: white;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    .paso-header {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 2rem;
    }
    
    .paso-header h2 {
        color: #2c3e50;
        margin: 0;
        font-size: 1.8rem;
    }
    
    .paso-header p {
        color: #7f8c8d;
        margin: 0.5rem 0 0 0;
    }
    
    .success-box {
        background: #27ae60;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .warning-box {
        background: #e74c3c;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .info-box {
        background: #3498db;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INICIALIZACIÓN
# ============================================================================
if 'paso_actual' not in st.session_state:
    st.session_state.paso_actual = 1

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def crear_zip_desde_archivos(archivos_paths):
    """Crea ZIP desde rutas de archivos existentes"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for ruta in archivos_paths:
            if os.path.exists(ruta):
                zip_file.write(ruta, os.path.basename(ruta))
    return zip_buffer.getvalue()

def mostrar_header_principal():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Auditoría de Ausentismos</h1>
        <p>Sistema Integrado de Gestión y Validación</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PASO 1: PROCESAMIENTO INICIAL
# ============================================================================
def paso1():
    mostrar_header_principal()
    
    st.markdown("""
    <div class="paso-header">
        <h2>📄 PASO 1: Procesamiento Inicial</h2>
        <p>CONCAT de CSV + Excel Reporte 45 con homologación y validaciones</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        st.write("**📥 Archivos de Entrada:**")
        st.write("• CSV de Ausentismos (Success Factors)")
        st.write("• Excel Reporte 45 (SAP)")
        
        st.write("**📤 Archivos de Salida:**")
        st.write("• ausentismo_procesado_completo_v2.csv")
        
        st.write("**🔧 Procesos Ejecutados:**")
        st.write("• Concatenación de CSV + Excel")
        st.write("• Homologación SSF vs SAP")
        st.write("• Identificación de validadores")
        st.write("• Generación de llaves únicas")
    
    st.warning("🔴 Este paso requiere 2 archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Archivo 1")
        csv_file = st.file_uploader(
            "CSV de Ausentismos",
            type=['csv'],
            key="csv1",
            help="Archivo exportado desde Success Factors"
        )
    
    with col2:
        st.subheader("📤 Archivo 2")
        excel_file = st.file_uploader(
            "Excel Reporte 45",
            type=['xlsx', 'xls'],
            key="excel1",
            help="Reporte 45 exportado desde SAP"
        )
    
    if csv_file and excel_file:
        st.divider()
        
        if st.button("🚀 PROCESAR ARCHIVOS", use_container_width=True, type="primary"):
            try:
                with st.spinner('⏳ Procesando archivos...'):
                    temp_dir = tempfile.mkdtemp()
                    
                    csv_path = os.path.join(temp_dir, "input.csv")
                    excel_path = os.path.join(temp_dir, "reporte45.xlsx")
                    
                    with open(csv_path, "wb") as f:
                        f.write(csv_file.getbuffer())
                    with open(excel_path, "wb") as f:
                        f.write(excel_file.getbuffer())
                    
                    import auditoria_ausentismos_part1 as part1
                    import importlib
                    importlib.reload(part1)
                    
                    part1.ruta_entrada_csv = csv_path
                    part1.ruta_entrada_excel = excel_path
                    part1.directorio_salida = temp_dir
                    part1.archivo_salida = "ausentismo_procesado_completo_v2.csv"
                    part1.ruta_completa_salida = os.path.join(temp_dir, "ausentismo_procesado_completo_v2.csv")
                    
                    df_resultado = part1.procesar_archivo_ausentismos()
                    
                    if df_resultado is not None:
                        st.success("✅ Procesamiento completado exitosamente")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Total Registros", f"{len(df_resultado):,}")
                        with col2:
                            st.metric("🔑 Llaves Únicas", f"{df_resultado['llave'].nunique():,}")
                        with col3:
                            alertas = (df_resultado['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
                            st.metric("⚠️ Alertas", alertas)
                        with col4:
                            st.metric("📋 Columnas", len(df_resultado.columns))
                        
                        st.divider()
                        st.subheader("👀 Vista Previa de Datos")
                        st.dataframe(df_resultado.head(10), use_container_width=True)
                        
                        st.divider()
                        st.subheader("📦 Descargar Resultados")
                        
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
                                    use_container_width=True,
                                    type="primary"
                                )
                            with col2:
                                if st.button("▶️ Siguiente", use_container_width=True):
                                    st.session_state.paso_actual = 2
                                    st.rerun()
                    else:
                        st.error("❌ Error en el procesamiento")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("🔍 Ver detalles"):
                    import traceback
                    st.code(traceback.format_exc())

# ============================================================================
# PASO 2: VALIDACIONES
# ============================================================================
def paso2():
    mostrar_header_principal()
    
    st.markdown("""
    <div class="paso-header">
        <h2>🔗 PASO 2: Validaciones y Merge con Personal</h2>
        <p>Cruza con datos de personal y ejecuta múltiples validaciones</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        st.write("**📥 Archivos de Entrada:**")
        st.write("• CSV del Paso 1")
        st.write("• Excel de Personal (MD_*.xlsx)")
        
        st.write("**📤 Archivos de Salida:**")
        st.write("• relacion_laboral_con_validaciones.csv")
        st.write("• Múltiples archivos Excel de alertas")
        
        st.write("**🔧 Validaciones:**")
        st.write("• Validación SENA")
        st.write("• Validación Ley 50")
        st.write("• Validación de licencias (6 tipos)")
    
    st.warning("🔴 Este paso requiere 2 archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Archivo 1")
        csv_paso1 = st.file_uploader(
            "CSV del Paso 1",
            type=['csv'],
            key="csv2"
        )
    
    with col2:
        st.subheader("📤 Archivo 2")
        excel_personal = st.file_uploader(
            "Excel de Personal",
            type=['xlsx', 'xls'],
            key="excel2"
        )
    
    if csv_paso1 and excel_personal:
        st.divider()
        
        if st.button("🚀 PROCESAR ARCHIVOS", use_container_width=True, type="primary"):
            try:
                with st.spinner('⏳ Procesando validaciones...'):
                    temp_dir = tempfile.mkdtemp()
                    
                    csv_path = os.path.join(temp_dir, "ausentismo_procesado_completo_v2.csv")
                    excel_path = os.path.join(temp_dir, "MD_personal.xlsx")
                    
                    with open(csv_path, "wb") as f:
                        f.write(csv_paso1.getbuffer())
                    with open(excel_path, "wb") as f:
                        f.write(excel_personal.getbuffer())
                    
                    df_ausentismo = pd.read_csv(csv_path, encoding='utf-8-sig')
                    df_personal = pd.read_excel(excel_path)
                    
                    st.info(f"📊 CSV: {len(df_ausentismo):,} | Excel: {len(df_personal):,}")
                    
                    col_num_pers = next((col for col in df_personal.columns if 'pers' in col.lower()), None)
                    col_relacion = next((col for col in df_personal.columns if 'relaci' in col.lower() and 'labor' in col.lower()), None)
                    
                    if not col_num_pers or not col_relacion:
                        st.error("❌ No se encontraron las columnas necesarias")
                        st.stop()
                    
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
                    
                    # Convertir calendar_days y quantity_in_days a numérico
                    df['calendar_days'] = pd.to_numeric(df['calendar_days'], errors='coerce')
                    df['quantity_in_days'] = pd.to_numeric(df['quantity_in_days'], errors='coerce')
                    
                    # Columnas de validación
                    df['licencia_paternidad'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia Paternidad" and r['calendar_days'] == 14 
                        else "Concepto No Aplica", axis=1)
                    
                    df['licencia_maternidad'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia Maternidad" and r['calendar_days'] == 126 
                        else "Concepto No Aplica", axis=1)
                    
                    df['ley_de_luto'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Ley de luto" and r['quantity_in_days'] == 5 
                        else "Concepto No Aplica", axis=1)
                    
                    df['incap_fuera_de_turno'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Incapa.fuera de turno" and r['calendar_days'] <= 1 
                        else "Concepto No Aplica", axis=1)
                    
                    df['lic_maternidad_sena'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia de Maternidad SENA" and r['calendar_days'] == 126 
                        else "Concepto No Aplica", axis=1)
                    
                    df['lic_jurado_votacion'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Lic Jurado Votación" and r['calendar_days'] <= 1 
                        else "Concepto No Aplica", axis=1)
                    
                    # Guardar archivo principal
                    archivo_principal = os.path.join(temp_dir, "relacion_laboral_con_validaciones.csv")
                    df.to_csv(archivo_principal, index=False, encoding='utf-8-sig')
                    
                    archivos_generados = [archivo_principal]
                    
                    # Errores SENA
                    if len(df_errores_sena) > 0:
                        path = os.path.join(temp_dir, "Sena_error_validar.xlsx")
                        df_errores_sena.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # Errores Ley 50
                    if len(df_errores_ley50) > 0:
                        path = os.path.join(temp_dir, "Ley_50_error_validar.xlsx")
                        df_errores_ley50.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # ===== ALERTAS POR COLUMNA =====
                    
                    # 1. Alerta licencia_paternidad
                    df_alert_pat = df[(df['licencia_paternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Paternidad')]
                    if len(df_alert_pat) > 0:
                        path = os.path.join(temp_dir, "alerta_licencia_paternidad.xlsx")
                        df_alert_pat.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # 2. Alerta licencia_maternidad
                    df_alert_mat = df[(df['licencia_maternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Maternidad')]
                    if len(df_alert_mat) > 0:
                        path = os.path.join(temp_dir, "alerta_licencia_maternidad.xlsx")
                        df_alert_mat.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # 3. Alerta ley_de_luto
                    df_alert_luto = df[(df['ley_de_luto'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Ley de luto')]
                    if len(df_alert_luto) > 0:
                        path = os.path.join(temp_dir, "alerta_ley_de_luto.xlsx")
                        df_alert_luto.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # 4. Alerta incap_fuera_de_turno
                    df_alert_incap = df[(df['incap_fuera_de_turno'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Incapa.fuera de turno')]
                    if len(df_alert_incap) > 0:
                        path = os.path.join(temp_dir, "alerta_incap_fuera_de_turno.xlsx")
                        df_alert_incap.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # 5. Alerta lic_maternidad_sena
                    df_alert_mat_sena = df[(df['lic_maternidad_sena'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia de Maternidad SENA')]
                    if len(df_alert_mat_sena) > 0:
                        path = os.path.join(temp_dir, "alerta_lic_maternidad_sena.xlsx")
                        df_alert_mat_sena.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # 6. Alerta lic_jurado_votacion
                    df_alert_jurado = df[(df['lic_jurado_votacion'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Lic Jurado Votación')]
                    if len(df_alert_jurado) > 0:
                        path = os.path.join(temp_dir, "alerta_lic_jurado_votacion.xlsx")
                        df_alert_jurado.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # 7. Incapacidades > 30 días
                    conceptos_incap = ['Incapacidad enfermedad general', 'Prorroga Inca/Enfer Gene', 'Enf Gral SOAT', 
                                      'Inc. Accidente de Trabajo', 'Prorroga Inc. Accid. Trab']
                    df_incap30 = df[(df['external_name_label'].isin(conceptos_incap)) & (df['calendar_days'] > 30)]
                    if len(df_incap30) > 0:
                        path = os.path.join(temp_dir, "incp_mayor_30_dias.xlsx")
                        df_incap30.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # 8. Ausentismos sin pago > 10 días
                    conceptos_sin_pago = ['Aus Reg sin Soporte', 'Suspensión']
                    df_sin_pago = df[(df['external_name_label'].isin(conceptos_sin_pago)) & (df['calendar_days'] > 10)]
                    if len(df_sin_pago) > 0:
                        path = os.path.join(temp_dir, "Validacion_ausentismos_sin_pago_mayor_10_dias.xlsx")
                        df_sin_pago.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # 9. Día de la familia > 1 día
                    df_dia_fam = df[(df['external_name_label'] == 'Día de la familia') & (df['calendar_days'] > 1)]
                    if len(df_dia_fam) > 0:
                        path = os.path.join(temp_dir, "dia_de_la_familia.xlsx")
                        df_dia_fam.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    st.success("✅ Validaciones completadas")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Total", f"{len(df):,}")
                    with col2:
                        st.metric("🚨 Errores SENA", len(df_errores_sena))
                    with col3:
                        st.metric("🚨 Errores Ley 50", len(df_errores_ley50))
                    with col4:
                        st.metric("📁 Archivos", len(archivos_generados))
                    
                    st.divider()
                    st.subheader("👀 Vista Previa")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    st.divider()
                    
                    zip_data = crear_zip_desde_archivos(archivos_generados)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.download_button(
                            f"📥 DESCARGAR ZIP - PASO 2 ({len(archivos_generados)} archivos)",
                            zip_data,
                            "PASO_2_Validaciones.zip",
                            "application/zip",
                            use_container_width=True,
                            type="primary"
                        )
                    with col2:
                        if st.button("▶️ Siguiente", use_container_width=True):
                            st.session_state.paso_actual = 3
                            st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("🔍 Ver detalles"):
                    import traceback
                    st.code(traceback.format_exc())

# ============================================================================
# PASO 3: REPORTE 45 Y CIE-10
# ============================================================================
def paso3():
    mostrar_header_principal()
    
    st.markdown("""
    <div class="paso-header">
        <h2>🏥 PASO 3: Merge con Reporte 45 y CIE-10</h2>
        <p>Enriquecimiento con diagnósticos y clasificación CIE-10</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        st.write("**📥 Archivos de Entrada:**")
        st.write("• CSV del Paso 2")
        st.write("• Excel Reporte 45")
        st.write("• Excel CIE-10")
        
        st.write("**📤 Archivos de Salida:**")
        st.write("• ausentismos_completo_con_cie10.csv")
        st.write("• ALERTA_DIAGNOSTICO.xlsx")
    
    st.warning("🔴 Este paso requiere 3 archivos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📤 Archivo 1")
        csv_paso2 = st.file_uploader("CSV del Paso 2", type=['csv'], key="csv3")
    
    with col2:
        st.subheader("📤 Archivo 2")
        excel_r45 = st.file_uploader("Excel Reporte 45", type=['xlsx', 'xls'], key="excel3")
    
    with col3:
        st.subheader("📤 Archivo 3")
        excel_cie10 = st.file_uploader("Excel CIE-10", type=['xlsx', 'xls'], key="excel4")
    
    if csv_paso2 and excel_r45 and excel_cie10:
        st.divider()
        st.success("✅ Los 3 archivos están listos")
        
        if st.button("🚀 PROCESAR ARCHIVOS", use_container_width=True, type="primary"):
            try:
                with st.spinner('⏳ Procesando...'):
                    temp_dir = tempfile.mkdtemp()
                    
                    csv_path = os.path.join(temp_dir, "relacion_laboral_con_validaciones.csv")
                    r45_path = os.path.join(temp_dir, "Reporte45.xlsx")
                    cie10_path = os.path.join(temp_dir, "CIE10.xlsx")
                    
                    with open(csv_path, "wb") as f:
                        f.write(csv_paso2.getbuffer())
                    with open(r45_path, "wb") as f:
                        f.write(excel_r45.getbuffer())
                    with open(cie10_path, "wb") as f:
                        f.write(excel_cie10.getbuffer())
                    
                    import auditoria_ausentismos_part3 as part3
                    import importlib
                    importlib.reload(part3)
                    
                    part3.ruta_relacion_laboral = csv_path
                    part3.ruta_reporte_45_excel = r45_path
                    part3.ruta_cie10 = cie10_path
                    part3.directorio_salida = temp_dir
                    part3.ruta_completa_salida = os.path.join(temp_dir, "ausentismos_completo_con_cie10.csv")
                    part3.ruta_alertas = os.path.join(temp_dir, "ALERTA_DIAGNOSTICO.xlsx")
                    
                    df_resultado = part3.procesar_todo()
                    
                    if df_resultado is not None:
                        st.success("✅ Proceso completado")
                        
                        alertas = (df_resultado['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum() if 'alerta_diagnostico' in df_resultado.columns else 0
                        con_cie = df_resultado['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_resultado.columns else 0
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Total", f"{len(df_resultado):,}")
                        with col2:
                            st.metric("🚨 Alertas", alertas)
                        with col3:
                            st.metric("🏥 Con CIE-10", con_cie)
                        with col4:
                            st.metric("📋 Columnas", len(df_resultado.columns))
                        
                        st.divider()
                        st.subheader("👀 Vista Previa")
                        st.dataframe(df_resultado.head(10), use_container_width=True)
                        
                        st.divider()
                        
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
                            use_container_width=True,
                            type="primary"
                        )
                        
                        st.balloons()
                    else:
                        st.error("❌ Error en el procesamiento")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("🔍 Ver detalles"):
                    import traceback
                    st.code(traceback.format_exc())

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.title("🧭 Navegación")
    
    st.divider()
    
    progreso = (st.session_state.paso_actual - 1) / 2 * 100
    st.progress(progreso / 100)
    st.write(f"**Progreso: {progreso:.0f}%**")
    
    st.divider()
    
    if st.button("📄 PASO 1: Procesamiento", use_container_width=True, 
                 disabled=(st.session_state.paso_actual == 1)):
        st.session_state.paso_actual = 1
        st.rerun()
    
    if st.button("🔗 PASO 2: Validaciones", use_container_width=True,
                 disabled=(st.session_state.paso_actual == 2)):
        st.session_state.paso_actual = 2
        st.rerun()
    
    if st.button("🏥 PASO 3: CIE-10", use_container_width=True,
                 disabled=(st.session_state.paso_actual == 3)):
        st.session_state.paso_actual = 3
        st.rerun()
    
    st.divider()
    
    st.info("""
    **📋 Flujo del Proceso**
    
    **PASO 1:** CSV + Excel → Procesado
    
    **PASO 2:** CSV + Personal → Validaciones
    
    **PASO 3:** CSV + R45 + CIE-10 → Final
    """)
    
    st.divider()
    
    st.caption("📧 **Soporte**")
    st.caption("Grupo Jerónimo Martins")

# ============================================================================
# MAIN
# ============================================================================
if st.session_state.paso_actual == 1:
    paso1()
elif st.session_state.paso_actual == 2:
    paso2()
elif st.session_state.paso_actual == 3:
    paso3()
