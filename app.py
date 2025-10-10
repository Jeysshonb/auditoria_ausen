import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
from datetime import datetime

st.set_page_config(page_title="Auditoría Ausentismos", page_icon="📊", layout="wide")

# ============================================================================
# ESTILOS CSS
# ============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }
    .main-header h1 { 
        color: white; 
        margin: 0; 
        font-size: 2.8rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p { 
        color: #e0e7ff; 
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
    }
    
    .step-card {
        background: linear-gradient(to right, #f8f9fa, #ffffff);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #667eea;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #667eea;
    }
    
    .success-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .info-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stProgress > div > div {
        background-color: #667eea;
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
def header():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Auditoría de Ausentismos</h1>
        <p>Sistema Integrado de Procesamiento y Validación</p>
    </div>
    """, unsafe_allow_html=True)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
    return output.getvalue()

def to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

def crear_zip(archivos_dict):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for nombre, data in archivos_dict.items():
            zip_file.writestr(nombre, data)
    return zip_buffer.getvalue()

def mostrar_metricas(col_configs):
    cols = st.columns(len(col_configs))
    for col, config in zip(cols, col_configs):
        with col:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(config['label'], config['value'], delta=config.get('delta'))
            st.markdown('</div>', unsafe_allow_html=True)

def convertir_fecha_a_excel(fecha_str):
    """Convierte fechas de formato YYYY-MM-DD HH:MM:SS a DD/MM/YYYY"""
    if pd.isna(fecha_str) or fecha_str == '' or str(fecha_str).lower() in ['nan', 'none', 'nat']:
        return ''
    
    try:
        if '/' in str(fecha_str):
            return str(fecha_str).split()[0]
        
        fecha_str_limpia = str(fecha_str).split()[0]
        
        if '-' in fecha_str_limpia:
            partes = fecha_str_limpia.split('-')
            if len(partes) == 3:
                año, mes, dia = partes
                return f"{dia.zfill(2)}/{mes.zfill(2)}/{año}"
        
        return fecha_str_limpia
    except:
        return str(fecha_str)

def limpiar_fecha_para_llave(fecha_str):
    """Limpia fechas para la llave - quita TODO lo que no sea número"""
    if pd.isna(fecha_str) or fecha_str == '' or str(fecha_str).lower() in ['nan', 'none', 'nat']:
        return ''
    fecha_limpia = ''.join(c for c in str(fecha_str) if c.isdigit())
    return fecha_limpia

def convertir_codigo_sap_a_ssf(codigo_sap, tabla_homologacion_inversa):
    """Convierte un código SAP (ej: '205') a código SSF (ej: 'CO_FAMILY')"""
    if pd.isna(codigo_sap) or codigo_sap == '':
        return ''
    codigo_limpio = str(codigo_sap).strip()
    return tabla_homologacion_inversa.get(codigo_limpio, codigo_limpio)

# ============================================================================
# PASO 1: PROCESAMIENTO INICIAL (CSV + EXCEL REPORTE 45)
# ============================================================================
def paso1():
    header()
    
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown("### 📄 Paso 1: Procesamiento Inicial - CONCAT CSV + Excel")
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📥 Entradas:**")
            st.markdown("• CSV de ausentismos (Success Factors)")
            st.markdown("• Excel Reporte 45 (SAP)")
        with col2:
            st.markdown("**📤 Salida:**")
            st.markdown("• ausentismo_procesado_especifico.csv")
        
        st.markdown("**🔧 Procesos:**")
        st.markdown("• CONCAT de CSV + Excel\n• Homologación SSF vs SAP\n• Validadores\n• Sub-tipos y FSE\n• Generación de llaves\n• Eliminación de duplicados")
    
    st.markdown('<div class="info-box">🔴 <b>Este paso requiere 2 archivos</b></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📤 1. CSV de Ausentismos**")
        archivo_csv = st.file_uploader("AusentismoCOL-*.csv", type=['csv'], key="csv1",
                                        help="Archivo exportado de Success Factors")
    
    with col2:
        st.markdown("**📤 2. Excel Reporte 45**")
        archivo_excel = st.file_uploader("Reporte 45_*.XLSX", type=['xlsx', 'xls'], key="excel1",
                                          help="Reporte 45 de SAP")
    
    if archivo_csv and archivo_excel:
        try:
            with st.spinner('⏳ Procesando CSV y Excel (CONCAT)...'):
                from auditoria_ausentismos_part1 import (
                    tabla_homologacion,
                    tabla_validadores, 
                    tabla_sub_tipo_fse
                )
                
                # TABLA INVERSA
                tabla_homologacion_inversa = {v: k for k, v in tabla_homologacion.items()}
                
                # ========================================
                # LEER CSV
                # ========================================
                df_csv = pd.read_csv(archivo_csv, skiprows=2, encoding='utf-8', dtype=str)
                st.info(f"✅ CSV leído: {len(df_csv):,} registros")
                
                columnas_csv = [
                    'ID personal', 'Nombre completo', 'Cod Función (externalCode)', 'Cod Función (Label)',
                    'Tipo de Documento de Identidad', 'Número de Documento de Identidad',
                    'Estado de empleado (Picklist Label)', 'externalCode', 'externalName (Label)',
                    'startDate', 'endDate', 'quantityInDays', 'Calendar Days',
                    'Descripción General (External Code)', 'Descripción General (Picklist Label)',
                    'Fecha de inicio de ausentismo', 'Agregador global de ausencias (Picklist Label)',
                    'lastModifiedBy', 'Last Approval Status Date', 'HR Personnel Subarea',
                    'HR Personnel Subarea Name', 'approvalStatus'
                ]
                
                columnas_csv_encontradas = [col for col in columnas_csv if col in df_csv.columns]
                df_csv_filtrado = df_csv[columnas_csv_encontradas].copy()
                
                if 'lastModifiedBy' in df_csv_filtrado.columns:
                    df_csv_filtrado['lastModifiedBy'] = df_csv_filtrado['lastModifiedBy'].astype(str)
                
                # ========================================
                # LEER EXCEL REPORTE 45
                # ========================================
                df_excel = pd.read_excel(archivo_excel, dtype=str)
                st.info(f"✅ Excel leído: {len(df_excel):,} registros")
                
                # Mapeo de columnas del Excel
                mapeo_excel = {
                    'Número de personal': 'ID personal',
                    'Nombre empl./cand.': 'Nombre completo',
                    'Txt.cl.pres./ab.': 'externalName (Label)',
                    'Inicio de validez': 'startDate',
                    'Fin de validez': 'endDate',
                    'Días presenc./abs.': 'quantityInDays',
                    'Días naturales': 'Calendar Days',
                    'Descripc.enfermedad': 'Descripción General (Picklist Label)',
                    'Modificado por': 'lastModifiedBy',
                    'Final': 'Last Approval Status Date',
                    'Clase absent./pres.': 'codigo_sap_original'
                }
                
                df_excel_renamed = df_excel.rename(columns=mapeo_excel)
                
                if 'lastModifiedBy' in df_excel_renamed.columns:
                    df_excel_renamed['lastModifiedBy'] = df_excel_renamed['lastModifiedBy'].astype(str)
                
                # Convertir códigos SAP a SSF
                if 'codigo_sap_original' in df_excel_renamed.columns:
                    df_excel_renamed['externalCode'] = df_excel_renamed['codigo_sap_original'].apply(
                        lambda x: convertir_codigo_sap_a_ssf(x, tabla_homologacion_inversa)
                    )
                    df_excel_renamed = df_excel_renamed.drop(['codigo_sap_original'], axis=1)
                
                # ========================================
                # CONCAT CSV + EXCEL
                # ========================================
                df_combinado = pd.concat([df_csv_filtrado, df_excel_renamed], ignore_index=True, sort=False)
                st.success(f"✅ CONCAT completado: {len(df_combinado):,} registros totales")
                
                # ========================================
                # CONVERTIR FECHAS A DD/MM/YYYY
                # ========================================
                columnas_fecha = ['startDate', 'endDate', 'Last Approval Status Date']
                for col in columnas_fecha:
                    if col in df_combinado.columns:
                        df_combinado[col] = df_combinado[col].apply(convertir_fecha_a_excel)
                
                # ========================================
                # HOMOLOGACIÓN
                # ========================================
                if 'externalCode' in df_combinado.columns:
                    df_combinado['Homologacion_clase_de_ausentismo_SSF_vs_SAP'] = \
                        df_combinado['externalCode'].map(tabla_homologacion)
                
                # ========================================
                # CREAR LLAVE (ANTES DE ELIMINAR DUPLICADOS)
                # ========================================
                df_combinado['startDate_limpia'] = df_combinado['startDate'].apply(limpiar_fecha_para_llave)
                df_combinado['endDate_limpia'] = df_combinado['endDate'].apply(limpiar_fecha_para_llave)
                
                df_combinado['llave'] = (
                    df_combinado['ID personal'].astype(str).fillna('') +
                    df_combinado['startDate_limpia'] +
                    df_combinado['endDate_limpia'] +
                    df_combinado['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].astype(str).fillna('')
                )
                
                df_combinado['llave'] = 'K' + df_combinado['llave'].astype(str)
                df_combinado = df_combinado.drop(['startDate_limpia', 'endDate_limpia'], axis=1)
                
                # ========================================
                # ELIMINAR DUPLICADOS POR LLAVE
                # ========================================
                registros_antes = len(df_combinado)
                duplicados_encontrados = df_combinado['llave'].duplicated().sum()
                
                if duplicados_encontrados > 0:
                    df_combinado = df_combinado.drop_duplicates(subset=['llave'], keep='first')
                    registros_despues = len(df_combinado)
                    st.warning(f"⚠️ Duplicados eliminados: {registros_antes - registros_despues}")
                
                # ========================================
                # VALIDADORES
                # ========================================
                if 'lastModifiedBy' in df_combinado.columns:
                    df_combinado['lastModifiedBy_limpio'] = df_combinado['lastModifiedBy'].astype(str).str.strip()
                    df_combinado['nombre_validador'] = df_combinado['lastModifiedBy_limpio'].map(tabla_validadores)\
                        .fillna('ALERTA VALIDADOR NO ENCONTRADO')
                    df_combinado = df_combinado.drop(['lastModifiedBy_limpio'], axis=1)
                
                # ========================================
                # SUB-TIPO Y FSE
                # ========================================
                df_combinado['Sub_tipo'] = df_combinado['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                    lambda x: tabla_sub_tipo_fse.get(str(x), {}).get('sub_tipo', 'ALERTA SUB_TIPO NO ENCONTRADO') 
                    if pd.notna(x) else 'ALERTA SUB_TIPO NO ENCONTRADO'
                )
                df_combinado['FSE'] = df_combinado['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                    lambda x: tabla_sub_tipo_fse.get(str(x), {}).get('fse', 'No Aplica') 
                    if pd.notna(x) else 'No Aplica'
                )
                
                # ========================================
                # MAPEO DE COLUMNAS
                # ========================================
                mapeo_columnas_final = {
                    'ID personal': 'id_personal',
                    'Nombre completo': 'nombre_completo',
                    'Cod Función (externalCode)': 'cod_funcion_external_code',
                    'Cod Función (Label)': 'cod_funcion_label',
                    'Tipo de Documento de Identidad': 'tipo_documento_identidad',
                    'Número de Documento de Identidad': 'numero_documento_identidad',
                    'Estado de empleado (Picklist Label)': 'estado_empleado_picklist_label',
                    'externalCode': 'external_code',
                    'externalName (Label)': 'external_name_label',
                    'startDate': 'start_date',
                    'endDate': 'end_date',
                    'quantityInDays': 'quantity_in_days',
                    'Calendar Days': 'calendar_days',
                    'Descripción General (External Code)': 'descripcion_general_external_code',
                    'Descripción General (Picklist Label)': 'descripcion_general_picklist_label',
                    'Fecha de inicio de ausentismo': 'fecha_inicio_ausentismo',
                    'Agregador global de ausencias (Picklist Label)': 'agregador_global_ausencias_picklist_label',
                    'lastModifiedBy': 'last_modified_by',
                    'Last Approval Status Date': 'last_approval_status_date',
                    'HR Personnel Subarea': 'hr_personnel_subarea',
                    'HR Personnel Subarea Name': 'hr_personnel_subarea_name',
                    'approvalStatus': 'approval_status',
                    'Homologacion_clase_de_ausentismo_SSF_vs_SAP': 'homologacion_clase_de_ausentismo_ssf_vs_sap',
                    'llave': 'llave',
                    'nombre_validador': 'nombre_validador',
                    'Sub_tipo': 'sub_tipo',
                    'FSE': 'fse'
                }
                
                mapeo_aplicable = {k: v for k, v in mapeo_columnas_final.items() if k in df_combinado.columns}
                df_final = df_combinado.rename(columns=mapeo_aplicable)
                
                # ========================================
                # LIMPIEZA FINAL
                # ========================================
                if 'last_modified_by' in df_final.columns:
                    df_final['last_modified_by'] = df_final['last_modified_by'].astype(str)
                    df_final['last_modified_by'] = '"' + df_final['last_modified_by'] + '"'
                
                if 'numero_documento_identidad' in df_final.columns:
                    df_final['numero_documento_identidad'] = df_final['numero_documento_identidad'].astype(str).replace('nan', '')
                    df_final['numero_documento_identidad'] = '"' + df_final['numero_documento_identidad'] + '"'
            
            st.markdown('<div class="success-box">✅ Procesamiento completado exitosamente</div>', unsafe_allow_html=True)
            
            # Métricas
            alertas = (df_final['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
            fse_aplica = (df_final['fse'] == 'Si Aplica').sum()
            llaves_unicas = df_final['llave'].nunique()
            
            mostrar_metricas([
                {'label': '📊 Total Registros', 'value': f"{len(df_final):,}"},
                {'label': '🔑 Llaves Únicas', 'value': f"{llaves_unicas:,}"},
                {'label': '⚠️ Alertas', 'value': alertas},
                {'label': '✅ FSE Si Aplica', 'value': fse_aplica}
            ])
            
            st.markdown("---")
            st.markdown("### 👀 Vista Previa de Datos")
            st.dataframe(df.head(10), use_container_width=True, height=350)
            
            st.markdown("---")
            st.markdown("### 📦 Generar Paquete de Resultados")
            
            # Preparar archivos para ZIP
            archivos_zip = {'relacion_laboral_con_validaciones.csv': to_csv(df)}
            
            if len(df_errores_sena) > 0:
                archivos_zip['Sena_error_validar.xlsx'] = to_excel(df_errores_sena)
            if len(df_errores_ley50) > 0:
                archivos_zip['Ley_50_error_validar.xlsx'] = to_excel(df_errores_ley50)
            
            # Alertas individuales
            df_alert_pat = df[(df['licencia_paternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Paternidad')]
            if len(df_alert_pat) > 0:
                archivos_zip['alerta_licencia_paternidad.xlsx'] = to_excel(df_alert_pat)
            
            df_alert_mat = df[(df['licencia_maternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Maternidad')]
            if len(df_alert_mat) > 0:
                archivos_zip['alerta_licencia_maternidad.xlsx'] = to_excel(df_alert_mat)
            
            df_alert_luto = df[(df['ley_de_luto'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Ley de luto')]
            if len(df_alert_luto) > 0:
                archivos_zip['alerta_ley_de_luto.xlsx'] = to_excel(df_alert_luto)
            
            # Incapacidades mayores a 30 días
            conceptos_incap = ['Incapacidad enfermedad general', 'Prorroga Inca/Enfer Gene',
                               'Enf Gral SOAT', 'Inc. Accidente de Trabajo', 'Prorroga Inc. Accid. Trab']
            df_incap30 = df[(df['external_name_label'].isin(conceptos_incap)) & 
                            (pd.to_numeric(df['calendar_days'], errors='coerce') > 30)]
            if len(df_incap30) > 0:
                archivos_zip['incp_mayor_30_dias.xlsx'] = to_excel(df_incap30)
            
            # Ausentismos sin pago mayores a 10 días
            conceptos_sin_pago = ['Aus Reg sin Soporte', 'Suspensión']
            df_sin_pago_mayor_10 = df[(df['external_name_label'].isin(conceptos_sin_pago)) & 
                                       (pd.to_numeric(df['calendar_days'], errors='coerce') > 10)]
            if len(df_sin_pago_mayor_10) > 0:
                archivos_zip['Validacion_ausentismos_sin_pago_mayor_10_dias.xlsx'] = to_excel(df_sin_pago_mayor_10)
            
            # Día de la familia mayor de 1 día
            df_dia_fam = df[(df['external_name_label'] == 'Día de la familia') & 
                            (pd.to_numeric(df['calendar_days'], errors='coerce') > 1)]
            if len(df_dia_fam) > 0:
                archivos_zip['dia_de_la_familia.xlsx'] = to_excel(df_dia_fam)
            
            # Mostrar contenido del ZIP
            st.success(f"📦 El ZIP contendrá {len(archivos_zip)} archivo(s):")
            
            col1, col2 = st.columns(2)
            for idx, nombre in enumerate(archivos_zip.keys()):
                with col1 if idx % 2 == 0 else col2:
                    st.markdown(f"• ✅ {nombre}")
            
            zip_data = crear_zip(archivos_zip)
            
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.download_button(
                    label=f"📥 DESCARGAR ZIP - PASO 2 ({len(archivos_zip)} archivos)",
                    data=zip_data,
                    file_name="PASO_2_Validaciones.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                if st.button("▶️ Ir al Paso 3", use_container_width=True, type="secondary"):
                    st.session_state.paso_actual = 3
                    st.rerun()
            with col3:
                if st.button("✅ Finalizar", use_container_width=True):
                    st.session_state.paso_actual = 4
                    st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error en el procesamiento")
            with st.expander("Ver detalles del error"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())

# ============================================================================
# PASO 3: MERGE CON REPORTE 45 Y CIE-10
# ============================================================================
def paso3():
    header()
    
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown("### 🏥 Paso 3: Merge con Reporte 45 y CIE-10")
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📥 Entradas:**")
            st.markdown("• CSV del Paso 2\n• Reporte 45 (Excel) - FILTRADO\n• Tabla CIE-10 (Excel)")
        with col2:
            st.markdown("**📤 Salidas:**")
            st.markdown("• CSV con diagnósticos\n• ALERTA_DIAGNOSTICO.xlsx")
        
        st.markdown("**🔧 Procesos:**")
        st.markdown("• Filtro de 17 subtipos específicos\n• Merge con Reporte 45 por llave\n• Validación de diagnósticos\n• Enriquecimiento con CIE-10")
    
    st.markdown('<div class="info-box">🔴 <b>Este paso requiere 3 archivos</b></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📤 1. CSV Paso 2**")
        csv_paso2 = st.file_uploader(
            "relacion_laboral_con_validaciones.csv",
            type=['csv'],
            key="csv_p2",
            help="Archivo generado en el Paso 2"
        )
    
    with col2:
        st.markdown("**📤 2. Reporte 45**")
        excel_reporte45 = st.file_uploader(
            "Reporte 45_*.XLSX",
            type=['xlsx', 'xls'],
            key="excel_r45",
            help="Reporte 45 de SAP (DIFERENTE al del Paso 1)"
        )
    
    with col3:
        st.markdown("**📤 3. Tabla CIE-10**")
        excel_cie10 = st.file_uploader(
            "CIE 10 - AJUSTADO.xlsx",
            type=['xlsx', 'xls'],
            key="excel_cie10",
            help="Tabla maestra CIE-10"
        )
    
    if csv_paso2 and excel_reporte45 and excel_cie10:
        try:
            with st.spinner('⏳ Procesando merge con Reporte 45 y CIE-10...'):
                # FILTRO DE 17 SUBTIPOS
                SUBTIPOS_FILTRO = [
                    'Enf Gral Int SOAT', 'Enf Gral SOAT', 'Inc. Acci Trabajo Integra',
                    'Inc. Accidente de Trabajo', 'Inc. Enfer. General Hospi', 'Inc. Enfermed Profesional',
                    'Inca. Enfer Gral Integral', 'Inca. Enfermedad  General', 'Incap  mayor 180 dias',
                    'Incap  mayor 540 dias', 'Incapa.fuera de turno', 'Prorr Enf Gral Int SOAT',
                    'Prorr Inc.Accid. Tr Integ', 'Prorr Inc/Enf Gral ntegra', 'Prorroga Enf Gral SOAT',
                    'Prorroga Inc. Accid. Trab', 'Prorroga Inca/Enfer Gene'
                ]
                
                # Leer CSV del paso 2
                df_base = pd.read_csv(csv_paso2, encoding='utf-8-sig', dtype=str)
                st.info(f"✅ CSV Paso 2: {len(df_base):,} registros")
                
                # Filtrar por subtipos
                if 'external_name_label' in df_base.columns:
                    antes = len(df_base)
                    df_base_filtrado = df_base[df_base['external_name_label'].isin(SUBTIPOS_FILTRO)].copy()
                    despues = len(df_base_filtrado)
                    st.info(f"✅ CSV filtrado: {despues:,} registros (descartados: {antes - despues:,})")
                else:
                    df_base_filtrado = df_base.copy()
                
                # Leer Reporte 45
                df_reporte45 = pd.read_excel(excel_reporte45, dtype=str)
                st.info(f"✅ Reporte 45: {len(df_reporte45):,} registros")
                
                # Filtrar Reporte 45
                col_txt_clase = None
                for col in df_reporte45.columns:
                    if 'txt' in col.lower() and ('pres' in col.lower() or 'clase' in col.lower()):
                        col_txt_clase = col
                        break
                
                valores_filtro_r45 = [
                    'Enf Gral SOAT', 'Inc. Accidente de Trabajo', 'Inca. Enfer Gral Integral',
                    'Inca. Enfermedad  General', 'Prorroga Enf Gral SOAT', 'Prorroga Inc. Accid. Trab',
                    'Prorroga Inca/Enfer Gene', 'Incapa.fuera de turno'
                ]
                
                if col_txt_clase:
                    df_reporte45_filtrado = df_reporte45[df_reporte45[col_txt_clase].isin(valores_filtro_r45)].copy()
                    st.info(f"✅ Reporte 45 filtrado: {len(df_reporte45_filtrado):,} registros")
                else:
                    df_reporte45_filtrado = df_reporte45.copy()
                
                # Buscar columnas para merge en Reporte 45
                col_num_pers_r45 = None
                for col in df_reporte45_filtrado.columns:
                    if 'número' in col.lower() and 'personal' in col.lower():
                        col_num_pers_r45 = col
                        break
                
                col_inicio_r45 = None
                for col in df_reporte45_filtrado.columns:
                    if 'inicio' in col.lower() and 'valid' in col.lower():
                        col_inicio_r45 = col
                        break
                
                col_fin_r45 = None
                for col in df_reporte45_filtrado.columns:
                    if 'fin' in col.lower() and 'valid' in col.lower():
                        col_fin_r45 = col
                        break
                
                col_clase_r45 = None
                for col in df_reporte45_filtrado.columns:
                    if 'clase' in col.lower() and 'absent' in col.lower():
                        col_clase_r45 = col
                        break
                
                if not all([col_num_pers_r45, col_inicio_r45, col_fin_r45, col_clase_r45]):
                    st.error("❌ No se encontraron todas las columnas necesarias en Reporte 45")
                    st.info("Columnas disponibles:")
                    st.write(list(df_reporte45_filtrado.columns))
                    st.stop()
                
                # Crear llave en Reporte 45
                df_reporte45_filtrado['inicio_limpio'] = pd.to_datetime(df_reporte45_filtrado[col_inicio_r45], errors='coerce').dt.strftime('%d%m%Y')
                df_reporte45_filtrado['fin_limpio'] = pd.to_datetime(df_reporte45_filtrado[col_fin_r45], errors='coerce').dt.strftime('%d%m%Y')
                
                df_reporte45_filtrado['llave_report_45'] = (
                    'K' +
                    df_reporte45_filtrado[col_num_pers_r45].astype(str).str.strip() +
                    df_reporte45_filtrado['inicio_limpio'].fillna('') +
                    df_reporte45_filtrado['fin_limpio'].fillna('') +
                    df_reporte45_filtrado[col_clase_r45].astype(str).str.strip()
                )
                
                # Merge INNER con Reporte 45
                df_merged = pd.merge(
                    df_base_filtrado,
                    df_reporte45_filtrado,
                    left_on='llave',
                    right_on='llave_report_45',
                    how='inner',
                    suffixes=('', '_r45')
                )
                
                st.success(f"✅ Merge con Reporte 45: {len(df_merged):,} registros con match")
                
                # VALIDACIÓN DE DIAGNÓSTICO
                valores_requieren_diagnostico = [
                    'Inca. Enfermedad  General', 'Prorroga Inca/Enfer Gene', 'Inc. Accidente de Trabajo',
                    'Enf Gral SOAT', 'Prorroga Enf Gral SOAT', 'Licencia Paternidad', 'Prorroga Inc. Accid. Trab',
                    'Incapacidad gral SENA', 'Inca. Enfer Gral Integral', 'Licencia Paternidad Inegr',
                    'Licencia Maternidad', 'Incap  mayor 180 dias', 'Incap  mayor 540 dias',
                    'Lic Mater Interrumpida', 'Licencia Mater especial', 'Enf Gral Int SOAT',
                    'Inc. Enfer. General Hospi', 'Prorr Inc/Enf Gral ntegra', 'Incapacidad ARL SENA',
                    'Licencia Maternidad Integ'
                ]
                
                col_diagnostico = None
                for col in df_merged.columns:
                    if 'descripc' in col.lower() and 'enfermedad' in col.lower():
                        col_diagnostico = col
                        break
                
                df_alerta_diagnostico = pd.DataFrame()
                if col_diagnostico and 'external_name_label' in df_merged.columns:
                    df_merged['alerta_diagnostico'] = df_merged.apply(
                        lambda row: 'ALERTA DIAGNOSTICO' 
                        if row['external_name_label'] in valores_requieren_diagnostico and 
                           (pd.isna(row[col_diagnostico]) or str(row[col_diagnostico]).strip() in ['', 'nan', 'None'])
                        else '', 
                        axis=1
                    )
                    
                    alertas_diag = (df_merged['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum()
                    df_alerta_diagnostico = df_merged[df_merged['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO'].copy()
                else:
                    df_merged['alerta_diagnostico'] = ''
                
                # MERGE CON CIE-10
                df_cie10 = pd.read_excel(excel_cie10, dtype=str)
                st.info(f"✅ CIE-10: {len(df_cie10):,} códigos")
                
                col_codigo_cie = None
                for col in df_cie10.columns:
                    if col.lower() in ['código', 'codigo', 'code']:
                        col_codigo_cie = col
                        break
                
                if col_codigo_cie and 'descripcion_general_external_code' in df_merged.columns:
                    df_merged['codigo_limpio'] = df_merged['descripcion_general_external_code'].str.strip().str.upper().str.replace('*', '', regex=False)
                    df_cie10['codigo_limpio'] = df_cie10[col_codigo_cie].str.strip().str.upper().str.replace('*', '', regex=False)
                    
                    cols_cie10 = [col_codigo_cie]
                    if 'Descripción' in df_cie10.columns:
                        cols_cie10.append('Descripción')
                    if 'TIPO' in df_cie10.columns:
                        cols_cie10.append('TIPO')
                    if 'Clasificación Sistemas JMC' in df_cie10.columns:
                        cols_cie10.append('Clasificación Sistemas JMC')
                    
                    cols_cie10.append('codigo_limpio')
                    df_cie10_subset = df_cie10[cols_cie10].copy()
                    
                    df_final = pd.merge(
                        df_merged,
                        df_cie10_subset,
                        on='codigo_limpio',
                        how='left',
                        suffixes=('', '_cie10')
                    )
                    
                    renombrar = {}
                    if col_codigo_cie in df_final.columns and col_codigo_cie != 'codigo_limpio':
                        renombrar[col_codigo_cie] = 'cie10_codigo'
                    if 'Descripción' in df_final.columns:
                        renombrar['Descripción'] = 'cie10_descripcion'
                    if 'TIPO' in df_final.columns:
                        renombrar['TIPO'] = 'cie10_tipo'
                    if 'Clasificación Sistemas JMC' in df_final.columns:
                        renombrar['Clasificación Sistemas JMC'] = 'cie10_clasificacion_sistemas_jmc'
                    
                    df_final = df_final.rename(columns=renombrar)
                    
                    if 'codigo_limpio' in df_final.columns:
                        df_final = df_final.drop(['codigo_limpio'], axis=1)
                    
                    con_cie10 = df_final['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_final.columns else 0
                    st.success(f"✅ Merge CIE-10: {con_cie10:,} registros con información")
                else:
                    df_final = df_merged.copy()
                    con_cie10 = 0
            
            st.markdown('<div class="success-box">✅ Proceso completado exitosamente</div>', unsafe_allow_html=True)
            
            # Métricas finales
            alertas = (df_final['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum() if 'alerta_diagnostico' in df_final.columns else 0
            
            mostrar_metricas([
                {'label': '📊 Total Registros', 'value': f"{len(df_final):,}"},
                {'label': '🚨 Alertas Diagnóstico', 'value': alertas},
                {'label': '🏥 Con CIE-10', 'value': con_cie10},
                {'label': '📋 Columnas', 'value': len(df_final.columns)}
            ])
            
            st.markdown("---")
            st.markdown("### 👀 Vista Previa de Datos")
            st.dataframe(df_final.head(10), use_container_width=True, height=350)
            
            st.markdown("---")
            st.markdown("### 📦 Generar Paquete de Resultados")
            
            archivos_zip = {
                'ausentismos_con_cie10.csv': to_csv(df_final)
            }
            
            if len(df_alerta_diagnostico) > 0:
                archivos_zip['ALERTA_DIAGNOSTICO.xlsx'] = to_excel(df_alerta_diagnostico)
            
            st.success(f"📦 El ZIP contendrá {len(archivos_zip)} archivo(s):")
            
            for nombre in archivos_zip.keys():
                st.markdown(f"• ✅ {nombre}")
            
            zip_data = crear_zip(archivos_zip)
            
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.download_button(
                    label=f"📥 DESCARGAR ZIP - PASO 3 ({len(archivos_zip)} archivos)",
                    data=zip_data,
                    file_name="PASO_3_CIE10_y_Diagnosticos.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                if st.button("✅ Finalizar", use_container_width=True, type="secondary"):
                    st.session_state.paso_actual = 4
                    st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error en el procesamiento")
            with st.expander("Ver detalles del error"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())
    
    else:
        st.markdown('<div class="info-box">📤 Por favor sube los 3 archivos requeridos para continuar</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Volver al Paso 2", use_container_width=True):
                st.session_state.paso_actual = 2
                st.rerun()
        with col2:
            if st.button("⭐ Ir al Resumen", use_container_width=True):
                st.session_state.paso_actual = 4
                st.rerun()

# ============================================================================
# PASO 4: RESUMEN FINAL
# ============================================================================
def paso4():
    header()
    
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown("### 🎉 Proceso Completado")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.balloons()
    
    st.markdown('<div class="success-box">✅ Has completado exitosamente el proceso de auditoría de ausentismos</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Paso 1")
        st.markdown("**Procesamiento Inicial**")
        st.markdown("✅ CONCAT CSV + Excel")
        st.markdown("✅ Homologación SSF vs SAP")
        st.markdown("✅ Validadores identificados")
        st.markdown("✅ Sub-tipos y FSE")
        st.markdown("✅ Generación de llaves")
        st.markdown("✅ Eliminación duplicados")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔗 Paso 2")
        st.markdown("**Validaciones y Merge**")
        st.markdown("✅ Merge con Personal")
        st.markdown("✅ Validaciones SENA")
        st.markdown("✅ Validaciones Ley 50")
        st.markdown("✅ Validaciones de licencias")
        st.markdown("✅ Alertas de incapacidades")
        st.markdown("✅ Alertas ausentismos")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🏥 Paso 3")
        st.markdown("**Reporte 45 y CIE-10**")
        st.markdown("✅ Filtro 17 subtipos")
        st.markdown("✅ Merge con Reporte 45")
        st.markdown("✅ Validación diagnósticos")
        st.markdown("✅ Enriquecimiento CIE-10")
        st.markdown("✅ Alertas generadas")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📦 Archivos Generados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📁 Paso 1:**")
        st.markdown("• ausentismo_procesado_especifico.csv")
        st.markdown("• *Incluye CONCAT de CSV + Excel Reporte 45*")
        
        st.markdown("**📁 Paso 2:**")
        st.markdown("• relacion_laboral_con_validaciones.csv")
        st.markdown("• Sena_error_validar.xlsx")
        st.markdown("• Ley_50_error_validar.xlsx")
        st.markdown("• alerta_licencia_paternidad.xlsx")
        st.markdown("• alerta_licencia_maternidad.xlsx")
        st.markdown("• alerta_ley_de_luto.xlsx")
    
    with col2:
        st.markdown("**📁 Paso 2 (cont):**")
        st.markdown("• incp_mayor_30_dias.xlsx")
        st.markdown("• Validacion_ausentismos_sin_pago_mayor_10_dias.xlsx")
        st.markdown("• dia_de_la_familia.xlsx")
        
        st.markdown("**📁 Paso 3:**")
        st.markdown("• ausentismos_con_cie10.csv")
        st.markdown("• ALERTA_DIAGNOSTICO.xlsx")
        
        st.markdown("**📊 Total:**")
        st.markdown("• **12+ archivos generados**")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mostrar_metricas([{'label': '✅ Pasos', 'value': '3/3'}])
    
    with col2:
        mostrar_metricas([{'label': '📁 Archivos', 'value': '12+'}])
    
    with col3:
        mostrar_metricas([{'label': '🎯 Estado', 'value': 'Completo'}])
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔄 Iniciar Nuevo Proceso", use_container_width=True, type="primary"):
            st.session_state.paso_actual = 1
            st.rerun()

# ============================================================================
# SIDEBAR DE NAVEGACIÓN
# ============================================================================
def sidebar():
    with st.sidebar:
        st.markdown("# 🧭 Navegación")
        st.markdown("---")
        
        progreso = (st.session_state.paso_actual - 1) / 3 * 100
        st.progress(progreso / 100)
        st.markdown(f"**Progreso:** {progreso:.0f}%")
        
        st.markdown("---")
        
        pasos = [
            ("1️⃣", "CSV + Excel", 1, "📄"),
            ("2️⃣", "Validaciones", 2, "🔗"),
            ("3️⃣", "Reporte 45 + CIE-10", 3, "🏥"),
            ("4️⃣", "Resumen", 4, "🎉")
        ]
        
        for emoji, nombre, num, icono in pasos:
            if st.session_state.paso_actual == num:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;
                            font-weight: 600; text-align: center;'>
                    {emoji} {nombre} ◄
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(f"{emoji} {nombre}", key=f"nav_{num}", use_container_width=True):
                    st.session_state.paso_actual = num
                    st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📋 Flujo del Proceso")
        st.markdown("""
        **Paso 1:** CONCAT CSV + Excel
        - Sube CSV de ausentismos
        - Sube Excel Reporte 45
        - Descarga ZIP con procesado
        
        **Paso 2:** Validaciones
        - Sube CSV del Paso 1
        - Sube Excel de Personal
        - Descarga ZIP con validaciones
        
        **Paso 3:** Reporte 45 + CIE-10
        - Sube CSV del Paso 2
        - Sube OTRO Excel Reporte 45
        - Sube Excel CIE-10
        - Descarga ZIP con análisis final
        
        **Paso 4:** Resumen completo
        """)
        
        st.markdown("---")
        
        st.markdown("### 💡 Información")
        st.info("Esta aplicación procesa ausentismos en 3 pasos secuenciales, generando archivos validados en cada etapa.")
        
        st.markdown("---")
        st.markdown("### ⚠️ IMPORTANTE")
        st.warning("En **Paso 1** y **Paso 3** se usan DIFERENTES archivos Reporte 45. Uno para CONCAT y otro para merge.")
        
        st.markdown("---")
        st.markdown("**📧 Soporte:**")
        st.markdown("Grupo Jerónimo Martins")

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def main():
    sidebar()
    
    if st.session_state.paso_actual == 1:
        paso1()
    elif st.session_state.paso_actual == 2:
        paso2()
    elif st.session_state.paso_actual == 3:
        paso3()
    elif st.session_state.paso_actual == 4:
        paso4()

if __name__ == "__main__":
    main()
            st.dataframe(df_final.head(10), use_container_width=True, height=350)
            
            st.markdown("---")
            st.markdown("### 📦 Descarga de Resultados")
            
            archivos_zip = {'ausentismo_procesado_especifico.csv': to_csv(df_final)}
            zip_data = crear_zip(archivos_zip)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.download_button(
                    label="📥 DESCARGAR ZIP - PASO 1",
                    data=zip_data,
                    file_name="PASO_1_Procesado.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                if st.button("▶️ Siguiente", use_container_width=True, type="secondary"):
                    st.session_state.paso_actual = 2
                    st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error en el procesamiento")
            with st.expander("Ver detalles del error"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())

# ============================================================================
# PASO 2: VALIDACIONES Y MERGE CON PERSONAL
# ============================================================================
def paso2():
    header()
    
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown("### 🔗 Paso 2: Validaciones y Merge con Personal")
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📥 Entradas:**")
            st.markdown("• CSV del Paso 1\n• Excel de Personal (MD_*.xlsx)")
        with col2:
            st.markdown("**📤 Salidas:**")
            st.markdown("• CSV con validaciones\n• Excels de alertas")
        
        st.markdown("**🔧 Procesos:**")
        st.markdown("• Merge por ID Personal\n• Validaciones SENA\n• Validaciones Ley 50\n• Validaciones de licencias\n• Alertas de incapacidades y ausentismos")
    
    st.markdown('<div class="info-box">🔴 <b>Este paso requiere 2 archivos</b></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📤 1. CSV del Paso 1**")
        csv_paso1 = st.file_uploader("ausentismo_procesado_especifico.csv", 
                                      type=['csv'], key="csv_p1",
                                      help="Archivo generado en el Paso 1")
    
    with col2:
        st.markdown("**📤 2. Excel de Personal**")
        excel_personal = st.file_uploader("MD_*.XLSX", 
                                           type=['xlsx', 'xls'], key="excel_pers",
                                           help="Maestro de datos de personal")
    
    if csv_paso1 and excel_personal:
        try:
            with st.spinner('⏳ Procesando validaciones...'):
                # Leer archivos
                df_ausentismo = pd.read_csv(csv_paso1, encoding='utf-8-sig')
                df_personal = pd.read_excel(excel_personal)
                
                st.info(f"✅ CSV: {len(df_ausentismo):,} registros | Excel: {len(df_personal):,} registros")
                
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
                    st.error("❌ No se encontraron columnas necesarias en el archivo de personal")
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
                
                # Validación SENA
                df_aprendizaje = df[df['Relación laboral'].str.contains('Aprendizaje', case=False, na=False)].copy()
                conceptos_validos_sena = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA']
                df_errores_sena = df_aprendizaje[~df_aprendizaje['external_name_label'].isin(conceptos_validos_sena)].copy()
                
                # Validación Ley 50
                df_ley50 = df[df['Relación laboral'].str.contains('Ley 50', case=False, na=False)].copy()
                conceptos_prohibidos = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA',
                                        'Inca. Enfer Gral Integral', 'Prorr Inc/Enf Gral ntegra']
                df_errores_ley50 = df_ley50[df_ley50['external_name_label'].isin(conceptos_prohibidos)].copy()
                
                # Crear columnas de validación
                df['licencia_paternidad'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia Paternidad" and r['calendar_days'] == '14' else "Concepto No Aplica", axis=1)
                df['licencia_maternidad'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia Maternidad" and r['calendar_days'] == '126' else "Concepto No Aplica", axis=1)
                df['ley_de_luto'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Ley de luto" and r['quantity_in_days'] == '5' else "Concepto No Aplica", axis=1)
                df['incap_fuera_de_turno'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Incapa.fuera de turno" and pd.to_numeric(r['calendar_days'], errors='coerce') <= 1 else "Concepto No Aplica", axis=1)
                df['lic_maternidad_sena'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia de Maternidad SENA" and r['calendar_days'] == '126' else "Concepto No Aplica", axis=1)
                df['lic_jurado_votacion'] = df.apply(
                    lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Lic Jurado Votación" and pd.to_numeric(r['calendar_days'], errors='coerce') <= 1 else "Concepto No Aplica", axis=1)
            
            st.markdown('<div class="success-box">✅ Validaciones completadas exitosamente</div>', unsafe_allow_html=True)
            
            # Métricas
            mostrar_metricas([
                {'label': '📊 Total Registros', 'value': f"{len(df):,}"},
                {'label': '🚨 Errores SENA', 'value': len(df_errores_sena)},
                {'label': '🚨 Errores Ley 50', 'value': len(df_errores_ley50)},
                {'label': '✅ Validaciones', 'value': '6 columnas'}
            ])
            
            st.markdown("---")
            st.markdown("### 👀 Vista Previa de Datos")
