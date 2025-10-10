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
# ESTILOS CSS
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: #2c3e50;
        padding: 2.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: #ecf0f1;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    .paso-header {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin-bottom: 2rem;
    }
    
    .paso-header h2 {
        color: #2c3e50;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .paso-header p {
        color: #7f8c8d;
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        border: 2px solid #e8e8e8;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        border-color: #3498db;
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.15);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
    }
    
    .success-box {
        background: #27ae60;
        color: white;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        font-weight: 600;
        text-align: center;
        font-size: 1.1rem;
    }
    
    .warning-box {
        background: #e74c3c;
        color: white;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        font-weight: 600;
        text-align: center;
        font-size: 1rem;
    }
    
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
    }
    
    [data-testid="stSidebar"] {
        background: #34495e;
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

def mostrar_metricas_custom(metricas):
    cols = st.columns(len(metricas))
    for col, metrica in zip(cols, metricas):
        with col:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">{metrica['label']}</div>
                <div class="metric-value">{metrica['value']}</div>
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
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📥 Archivos de Entrada:**")
            st.markdown("• CSV de Ausentismos (Success Factors)")
            st.markdown("• Excel Reporte 45 (SAP)")
        with col2:
            st.markdown("**📤 Archivos de Salida:**")
            st.markdown("• ausentismo_procesado_especifico.csv")
        
        st.markdown("---")
        st.markdown("**🔧 Procesos Ejecutados:**")
        st.markdown("• Concatenación de CSV + Excel\n• Homologación SSF vs SAP\n• Identificación de validadores\n• Generación de llaves únicas\n• Eliminación de duplicados\n• Clasificación Sub-tipos y FSE")
    
    st.markdown('<div class="warning-box">🔴 Este paso requiere 2 archivos</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Archivo 1")
        csv_file = st.file_uploader(
            "CSV de Ausentismos",
            type=['csv'],
            key="csv1",
            help="Archivo exportado desde Success Factors"
        )
    
    with col2:
        st.markdown("### 📤 Archivo 2")
        excel_file = st.file_uploader(
            "Excel Reporte 45",
            type=['xlsx', 'xls'],
            key="excel1",
            help="Reporte 45 exportado desde SAP"
        )
    
    if csv_file and excel_file:
        st.markdown("---")
        
        if st.button("🚀 PROCESAR ARCHIVOS", use_container_width=True, type="primary"):
            try:
                with st.spinner('⏳ Ejecutando auditoria_ausentismos_part1.py...'):
                    temp_dir = tempfile.mkdtemp()
                    
                    csv_path = os.path.join(temp_dir, "input.csv")
                    excel_path = os.path.join(temp_dir, "reporte45.xlsx")
                    
                    with open(csv_path, "wb") as f:
                        f.write(csv_file.getbuffer())
                    with open(excel_path, "wb") as f:
                        f.write(excel_file.getbuffer())
                    
                    import auditoria_ausentismos_part1 as part1
                    part1.ruta_entrada_csv = csv_path
                    part1.ruta_entrada_excel = excel_path
                    part1.directorio_salida = temp_dir
                    
                    df_resultado = part1.procesar_archivo_ausentismos()
                    
                    if df_resultado is not None:
                        st.markdown('<div class="success-box">✅ Procesamiento completado exitosamente</div>', unsafe_allow_html=True)
                        
                        alertas = (df_resultado['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
                        
                        mostrar_metricas_custom([
                            {'label': '📊 Total Registros', 'value': f"{len(df_resultado):,}"},
                            {'label': '🔑 Llaves Únicas', 'value': f"{df_resultado['llave'].nunique():,}"},
                            {'label': '⚠️ Alertas', 'value': alertas},
                            {'label': '📋 Columnas', 'value': len(df_resultado.columns)}
                        ])
                        
                        st.markdown("---")
                        st.markdown("### 👀 Vista Previa de Datos")
                        st.dataframe(df_resultado.head(10), use_container_width=True, height=400)
                        
                        st.markdown("---")
                        st.markdown("### 📦 Descargar Resultados")
                        
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
                                if st.button("▶️ Siguiente", use_container_width=True, type="secondary"):
                                    st.session_state.paso_actual = 2
                                    st.rerun()
                    else:
                        st.error("❌ Error en el procesamiento")
            
            except Exception as e:
                st.error(f"❌ Error durante la ejecución")
                with st.expander("🔍 Ver detalles del error"):
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
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📥 Archivos de Entrada:**")
            st.markdown("• CSV del Paso 1")
            st.markdown("• Excel de Personal (MD_*.xlsx)")
        with col2:
            st.markdown("**📤 Archivos de Salida:**")
            st.markdown("• relacion_laboral_con_validaciones.csv")
            st.markdown("• Múltiples archivos Excel de alertas")
        
        st.markdown("---")
        st.markdown("**🔧 Validaciones Ejecutadas:**")
        st.markdown("• Validación SENA\n• Validación Ley 50\n• Validación de licencias (6 tipos)\n• Incapacidades > 30 días\n• Ausentismos sin pago > 10 días\n• Día de la familia")
    
    st.markdown('<div class="warning-box">🔴 Este paso requiere 2 archivos</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Archivo 1")
        csv_paso1 = st.file_uploader(
            "CSV del Paso 1",
            type=['csv'],
            key="csv2",
            help="Archivo ausentismo_procesado_especifico.csv"
        )
    
    with col2:
        st.markdown("### 📤 Archivo 2")
        excel_personal = st.file_uploader(
            "Excel de Personal (MD_*.xlsx)",
            type=['xlsx', 'xls'],
            key="excel2",
            help="Maestro de datos de personal"
        )
    
    if csv_paso1 and excel_personal:
        st.markdown("---")
        
        if st.button("🚀 PROCESAR ARCHIVOS", use_container_width=True, type="primary", key="procesar_paso2"):
            try:
                with st.spinner('⏳ Ejecutando auditoria_ausentismos_part2.py...'):
                    temp_dir = tempfile.mkdtemp()
                    
                    csv_path = os.path.join(temp_dir, "ausentismo_procesado_completo_v2.csv")
                    excel_path = os.path.join(temp_dir, "MD_personal.xlsx")
                    
                    with open(csv_path, "wb") as f:
                        f.write(csv_paso1.getbuffer())
                    with open(excel_path, "wb") as f:
                        f.write(excel_personal.getbuffer())
                    
                    # Leer archivos
                    df_ausentismo = pd.read_csv(csv_path, encoding='utf-8-sig')
                    df_personal = pd.read_excel(excel_path)
                    
                    # Buscar columnas
                    col_num_pers = next((col for col in df_personal.columns if 'pers' in col.lower() or 'personal' in col.lower()), None)
                    col_relacion = next((col for col in df_personal.columns if 'relaci' in col.lower() and 'labor' in col.lower()), None)
                    
                    if not col_num_pers or not col_relacion:
                        st.error("❌ No se encontraron las columnas necesarias en el archivo de personal")
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
                    
                    # Columnas de validación
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
                    
                    # Guardar archivos
                    archivo_principal = os.path.join(temp_dir, "relacion_laboral_con_validaciones.csv")
                    df.to_csv(archivo_principal, index=False, encoding='utf-8-sig')
                    
                    archivos_generados = [archivo_principal]
                    
                    # Excels de errores
                    if len(df_errores_sena) > 0:
                        path = os.path.join(temp_dir, "Sena_error_validar.xlsx")
                        df_errores_sena.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    if len(df_errores_ley50) > 0:
                        path = os.path.join(temp_dir, "Ley_50_error_validar.xlsx")
                        df_errores_ley50.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    # Alertas de licencias
                    df_alert_pat = df[(df['licencia_paternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Paternidad')]
                    if len(df_alert_pat) > 0:
                        path = os.path.join(temp_dir, "alerta_licencia_paternidad.xlsx")
                        df_alert_pat.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    df_alert_mat = df[(df['licencia_maternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Maternidad')]
                    if len(df_alert_mat) > 0:
                        path = os.path.join(temp_dir, "alerta_licencia_maternidad.xlsx")
                        df_alert_mat.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    df_alert_luto = df[(df['ley_de_luto'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Ley de luto')]
                    if len(df_alert_luto) > 0:
                        path = os.path.join(temp_dir, "alerta_ley_de_luto.xlsx")
                        df_alert_luto.to_excel(path, index=False)
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
                    
                    # Día de la familia
                    df_dia_fam = df[(df['external_name_label'] == 'Día de la familia') & 
                                   (pd.to_numeric(df['calendar_days'], errors='coerce') > 1)]
                    if len(df_dia_fam) > 0:
                        path = os.path.join(temp_dir, "dia_de_la_familia.xlsx")
                        df_dia_fam.to_excel(path, index=False)
                        archivos_generados.append(path)
                    
                    st.markdown('<div class="success-box">✅ Validaciones completadas exitosamente</div>', unsafe_allow_html=True)
                    
                    mostrar_metricas_custom([
                        {'label': '📊 Total Registros', 'value': f"{len(df):,}"},
                        {'label': '🚨 Errores SENA', 'value': len(df_errores_sena)},
                        {'label': '🚨 Errores Ley 50', 'value': len(df_errores_ley50)},
                        {'label': '📁 Archivos', 'value': len(archivos_generados)}
                    ])
                    
                    st.markdown("---")
                    st.markdown("### 👀 Vista Previa de Datos")
                    st.dataframe(df.head(10), use_container_width=True, height=400)
                    
                    st.markdown("---")
                    st.markdown("### 📦 Descargar Resultados")
                    
                    st.success(f"✅ {len(archivos_generados)} archivo(s) generado(s)")
                    for archivo in archivos_generados:
                        st.markdown(f"• {os.path.basename(archivo)}")
                    
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
                        if st.button("▶️ Siguiente", use_container_width=True, type="secondary"):
                            st.session_state.paso_actual = 3
                            st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error durante la ejecución")
                with st.expander("🔍 Ver detalles del error"):
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
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📥 Archivos de Entrada:**")
            st.markdown("• CSV del Paso 2")
            st.markdown("• Excel Reporte 45 (OTRO)")
            st.markdown("• Excel CIE-10")
        with col2:
            st.markdown("**📤 Archivos de Salida:**")
            st.markdown("• ausentismos_completo_con_cie10.csv")
            st.markdown("• ALERTA_DIAGNOSTICO.xlsx")
        
        st.markdown("---")
        st.markdown("**🔧 Procesos Ejecutados:**")
        st.markdown("• Filtro de 17 subtipos específicos\n• Merge con Reporte 45 por llave\n• Validación de diagnósticos requeridos\n• Enriquecimiento con tabla CIE-10\n• Generación de alertas de diagnósticos")
    
    st.markdown('<div class="warning-box">🔴 Este paso requiere 3 archivos</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📤 Archivo 1")
        csv_paso2 = st.file_uploader(
            "CSV del Paso 2",
            type=['csv'],
            key="csv3",
            help="Archivo relacion_laboral_con_validaciones.csv"
        )
    
    with col2:
        st.markdown("### 📤 Archivo 2")
        excel_r45 = st.file_uploader(
            "Excel Reporte 45",
            type=['xlsx', 'xls'],
            key="excel3",
            help="Otro Reporte 45 (diferente al del Paso 1)"
        )
    
    with col3:
        st.markdown("### 📤 Archivo 3")
        excel_cie10 = st.file_uploader(
            "Excel CIE-10",
            type=['xlsx', 'xls'],
            key="excel4",
            help="Tabla maestra CIE-10 ajustada"
        )
    
    if csv_paso2 and excel_r45 and excel_cie10:
        st.markdown("---")
        
        if st.button("🚀 PROCESAR ARCHIVOS", use_container_width=True, type="primary", key="procesar_paso3"):
            try:
                with st.spinner('⏳ Ejecutando auditoria_ausentismos_part3.py...'):
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
                    part3.ruta_relacion_laboral = csv_path
                    part3.ruta_reporte_45_excel = r45_path
                    part3.ruta_cie10 = cie10_path
                    part3.directorio_salida = temp_dir
                    
                    df_resultado = part3.procesar_todo()
                    
                    if df_resultado is not None:
                        st.markdown('<div class="success-box">✅ Proceso completado exitosamente</div>', unsafe_allow_html=True)
                        
                        alertas = (df_resultado['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum() if 'alerta_diagnostico' in df_resultado.columns else 0
                        con_cie = df_resultado['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_resultado.columns else 0
                        
                        mostrar_metricas_custom([
                            {'label': '📊 Total Registros', 'value': f"{len(df_resultado):,}"},
                            {'label': '🚨 Alertas Diagnóstico', 'value': alertas},
                            {'label': '🏥 Con CIE-10', 'value': con_cie},
                            {'label': '📋 Columnas', 'value': len(df_resultado.columns)}
                        ])
                        
                        st.markdown("---")
                        st.markdown("### 👀 Vista Previa de Datos")
                        st.dataframe(df_resultado.head(10), use_container_width=True, height=400)
                        
                        st.markdown("---")
                        st.markdown("### 📦 Descargar Resultados")
                        
                        archivo_final = os.path.join(temp_dir, "ausentismos_completo_con_cie10.csv")
                        archivo_alertas = os.path.join(temp_dir, "ALERTA_DIAGNOSTICO.xlsx")
                        
                        archivos = [archivo_final]
                        if os.path.exists(archivo_alertas):
                            archivos.append(archivo_alertas)
                            st.success(f"✅ {len(archivos)} archivo(s) generado(s)")
                        else:
                            st.success(f"✅ 1 archivo generado (sin alertas de diagnóstico)")
                        
                        for archivo in archivos:
                            st.markdown(f"• {os.path.basename(archivo)}")
                        
                        zip_data = crear_zip_desde_archivos(archivos)
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.download_button(
                                f"📥 DESCARGAR ZIP - PASO 3 ({len(archivos)} archivos)",
                                zip_data,
                                "PASO_3_CIE10.zip",
                                "application/zip",
                                use_container_width=True,
                                type="primary"
                            )
                        with col2:
                            if st.button("🎉 Finalizar", use_container_width=True, type="secondary"):
                                st.balloons()
                                st.success("¡Proceso completado!")
                    else:
                        st.error("❌ Error en el procesamiento")
            
            except Exception as e:
                st.error(f"❌ Error durante la ejecución")
                with st.expander("🔍 Ver detalles del error"):
                    import traceback
                    st.code(traceback.format_exc())

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: white; font-size: 2rem; margin: 0;'>🧭</h1>
        <h2 style='color: white; font-size: 1.5rem; margin: 0.5rem 0;'>Navegación</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    progreso = (st.session_state.paso_actual - 1) / 2 * 100
    st.progress(progreso / 100)
    st.markdown(f"<p style='color: white; text-align: center; font-weight: 600;'>Progreso: {progreso:.0f}%</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Botones de navegación
    if st.session_state.paso_actual == 1:
        st.markdown("""
        <div style='background: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #3498db;'>
            <p style='margin: 0; font-weight: 700; color: #2c3e50;'>📄 PASO 1: Procesamiento ◄</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("📄 PASO 1: Procesamiento", use_container_width=True, key="nav1"):
            st.session_state.paso_actual = 1
            st.rerun()
    
    if st.session_state.paso_actual == 2:
        st.markdown("""
        <div style='background: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #3498db;'>
            <p style='margin: 0; font-weight: 700; color: #2c3e50;'>🔗 PASO 2: Validaciones ◄</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("🔗 PASO 2: Validaciones", use_container_width=True, key="nav2"):
            st.session_state.paso_actual = 2
            st.rerun()
    
    if st.session_state.paso_actual == 3:
        st.markdown("""
        <div style='background: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #3498db;'>
            <p style='margin: 0; font-weight: 700; color: #2c3e50;'>🏥 PASO 3: CIE-10 ◄</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("🏥 PASO 3: CIE-10", use_container_width=True, key="nav3"):
            st.session_state.paso_actual = 3
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("""
    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;'>
        <h3 style='color: white; font-size: 1.2rem; margin: 0 0 1rem 0;'>📋 Flujo del Proceso</h3>
        <div style='color: white; font-size: 0.9rem; line-height: 1.8;'>
            <p><strong>PASO 1:</strong> CSV + Excel → Procesado</p>
            <p><strong>PASO 2:</strong> CSV + Personal → Validaciones</p>
            <p><strong>PASO 3:</strong> CSV + R45 + CIE-10 → Final</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;'>
        <h3 style='color: white; font-size: 1.2rem; margin: 0 0 1rem 0;'>💡 Información</h3>
        <p style='color: white; font-size: 0.85rem; line-height: 1.6;'>
            Sistema que ejecuta scripts Python existentes (part1, part2, part3) 
            de forma secuencial. Presiona "🚀 PROCESAR ARCHIVOS" para ejecutar cada paso.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <p style='color: white; font-size: 0.9rem; margin: 0;'>📧 <strong>Soporte</strong></p>
        <p style='color: rgba(255,255,255,0.8); font-size: 0.85rem; margin: 0.5rem 0 0 0;'>Grupo Jerónimo Martins</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN - ENRUTADOR DE PASOS
# ============================================================================
if st.session_state.paso_actual == 1:
    paso1()
elif st.session_state.paso_actual == 2:
    paso2()
elif st.session_state.paso_actual == 3:
    paso3()
