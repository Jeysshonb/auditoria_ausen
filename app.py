import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile

st.set_page_config(page_title="Auditoría Ausentismos", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 { color: white; margin: 0; font-size: 2.5rem; }
    .main-header p { color: #e8f5e9; margin: 0.5rem 0 0 0; }
</style>
""", unsafe_allow_html=True)

if 'paso_actual' not in st.session_state:
    st.session_state.paso_actual = 1

def header():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Auditoría de Ausentismos</h1>
        <p>Sistema Paso a Paso con Descargas ZIP</p>
    </div>
    """, unsafe_allow_html=True)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

def crear_zip(archivos_dict):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for nombre, data in archivos_dict.items():
            zip_file.writestr(nombre, data)
    return zip_buffer.getvalue()

def paso1():
    header()
    st.markdown("### 🔄 Paso 1: Procesamiento Inicial")
    
    with st.expander("📋 ¿Qué hace este paso?", expanded=False):
        st.markdown("**Entrada:** CSV de ausentismos")
        st.markdown("**Proceso:** Homologación, validadores, llaves")
        st.markdown("**Salida:** ausentismo_procesado_especifico.csv")
    
    st.info("📤 Sube el archivo CSV de ausentismos")
    archivo = st.file_uploader("Archivo CSV", type=['csv'], key="csv1")
    
    if archivo:
        try:
            with st.spinner('⏳ Procesando...'):
                from auditoria_ausentismos_part1 import (
                    tabla_homologacion,
                    tabla_validadores, 
                    tabla_sub_tipo_fse,
                    columnas_requeridas,
                    mapeo_columnas,
                    limpiar_fecha_para_llave
                )
                
                df = pd.read_csv(archivo, skiprows=2, encoding='utf-8', dtype=str)
                columnas_encontradas = [col for col in columnas_requeridas if col in df.columns]
                df_especifico = df[columnas_encontradas].copy()
                
                df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'] = \
                    df_especifico['externalCode'].map(tabla_homologacion)
                
                df_especifico['lastModifiedBy_limpio'] = df_especifico['lastModifiedBy'].astype(str).str.strip()
                df_especifico['nombre_validador'] = df_especifico['lastModifiedBy_limpio'].map(tabla_validadores)\
                    .fillna('ALERTA VALIDADOR NO ENCONTRADO')
                df_especifico = df_especifico.drop(['lastModifiedBy_limpio'], axis=1)
                
                df_especifico['Sub_tipo'] = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                    lambda x: tabla_sub_tipo_fse.get(str(x), {}).get('sub_tipo', 'ALERTA SUB_TIPO NO ENCONTRADO') 
                    if pd.notna(x) else 'ALERTA SUB_TIPO NO ENCONTRADO'
                )
                df_especifico['FSE'] = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                    lambda x: tabla_sub_tipo_fse.get(str(x), {}).get('fse', 'No Aplica') 
                    if pd.notna(x) else 'No Aplica'
                )
                
                df_especifico['startDate_limpia'] = df_especifico['startDate'].apply(limpiar_fecha_para_llave)
                df_especifico['endDate_limpia'] = df_especifico['endDate'].apply(limpiar_fecha_para_llave)
                df_especifico['llave'] = (
                    df_especifico['ID personal'].astype(str).fillna('') +
                    df_especifico['startDate_limpia'] +
                    df_especifico['endDate_limpia'] +
                    df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].astype(str).fillna('')
                )
                df_especifico = df_especifico.drop(['startDate_limpia', 'endDate_limpia'], axis=1)
                
                mapeo_actual = {col: mapeo_columnas[col] for col in df_especifico.columns if col in mapeo_columnas}
                df_final = df_especifico.rename(columns=mapeo_actual)
                
                if 'numero_documento_identidad' in df_final.columns:
                    df_final['numero_documento_identidad'] = df_final['numero_documento_identidad'].astype(str).replace('nan', '')
                    df_final['numero_documento_identidad'] = '"' + df_final['numero_documento_identidad'] + '"'
                
                if 'llave' in df_final.columns:
                    df_final['llave'] = 'K' + df_final['llave'].astype(str)
            
            st.success("✅ Procesamiento completado!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Registros", f"{len(df_final):,}")
            with col2:
                st.metric("📋 Columnas", len(df_final.columns))
            with col3:
                alertas = (df_final['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
                st.metric("⚠️ Alertas", alertas)
            
            st.markdown("### 👀 Vista Previa")
            st.dataframe(df_final.head(10), use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 📦 DESCARGA ZIP")
            
            archivos_zip = {'ausentismo_procesado_especifico.csv': to_csv(df_final)}
            zip_data = crear_zip(archivos_zip)
            
            st.download_button(
                label="📥 DESCARGAR ZIP - PASO 1",
                data=zip_data,
                file_name="PASO_1_Procesado.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
            
            st.info("👉 Descarga el ZIP y usa el CSV en el Paso 2")
            
            st.markdown("---")
            if st.button("▶️ Ir al Paso 2", use_container_width=True):
                st.session_state.paso_actual = 2
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def paso2():
    header()
    st.markdown("### 🔗 Paso 2: Validaciones y Merge")
    
    with st.expander("📋 ¿Qué hace este paso?", expanded=False):
        st.markdown("**Entradas:** CSV Paso 1 + Excel Personal")
        st.markdown("**Proceso:** Merge, validaciones SENA y Ley 50")
        st.markdown("**Salidas:** CSV principal + alertas Excel")
    
    st.warning("🔴 Necesitas 2 archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📤 1. CSV del Paso 1")
        csv_paso1 = st.file_uploader("ausentismo_procesado_especifico.csv", type=['csv'], key="csv_p1")
    
    with col2:
        st.info("📤 2. Excel de Personal")
        excel_personal = st.file_uploader("MD_*.XLSX", type=['xlsx', 'xls'], key="excel_pers")
    
    if csv_paso1 and excel_personal:
        try:
            with st.spinner('⏳ Procesando validaciones...'):
                df_ausentismo = pd.read_csv(csv_paso1, encoding='utf-8-sig')
                df_personal = pd.read_excel(excel_personal)
                
                st.info(f"✅ CSV: {len(df_ausentismo):,} | Excel: {len(df_personal):,}")
                
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
                    st.error("❌ No se encontraron columnas necesarias")
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
                
                if col_num_pers != 'id_personal' and col_num_pers in df.columns:
                    df.drop(columns=[col_num_pers], inplace=True)
                
                df = df[df['Relación laboral'].notna()]
                
                df_aprendizaje = df[df['Relación laboral'].str.contains('Aprendizaje', case=False, na=False)].copy()
                conceptos_validos_sena = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA']
                df_errores_sena = df_aprendizaje[~df_aprendizaje['external_name_label'].isin(conceptos_validos_sena)].copy()
                
                df_ley50 = df[df['Relación laboral'].str.contains('Ley 50', case=False, na=False)].copy()
                conceptos_prohibidos = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA',
                                        'Inca. Enfer Gral Integral', 'Prorr Inc/Enf Gral ntegra']
                df_errores_ley50 = df_ley50[df_ley50['external_name_label'].isin(conceptos_prohibidos)].copy()
                
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
            
            st.success("✅ Validaciones completadas!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Registros", f"{len(df):,}")
            with col2:
                st.metric("🚨 Errores SENA", len(df_errores_sena))
            with col3:
                st.metric("🚨 Errores Ley 50", len(df_errores_ley50))
            
            st.markdown("### 👀 Vista Previa")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 📦 GENERAR ZIP CON TODO")
            
            archivos_zip = {'relacion_laboral_con_validaciones.csv': to_csv(df)}
            
            if len(df_errores_sena) > 0:
                archivos_zip['Sena_error_validar.xlsx'] = to_excel(df_errores_sena)
            if len(df_errores_ley50) > 0:
                archivos_zip['Ley_50_error_validar.xlsx'] = to_excel(df_errores_ley50)
            
            df_alert_pat = df[(df['licencia_paternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Paternidad')]
            if len(df_alert_pat) > 0:
                archivos_zip['alerta_licencia_paternidad.xlsx'] = to_excel(df_alert_pat)
            
            df_alert_mat = df[(df['licencia_maternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Maternidad')]
            if len(df_alert_mat) > 0:
                archivos_zip['alerta_licencia_maternidad.xlsx'] = to_excel(df_alert_mat)
            
            df_alert_luto = df[(df['ley_de_luto'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Ley de luto')]
            if len(df_alert_luto) > 0:
                archivos_zip['alerta_ley_de_luto.xlsx'] = to_excel(df_alert_luto)
            
            conceptos_incap = ['Incapacidad enfermedad general', 'Prorroga Inca/Enfer Gene',
                               'Enf Gral SOAT', 'Inc. Accidente de Trabajo', 'Prorroga Inc. Accid. Trab']
            df_incap30 = df[(df['external_name_label'].isin(conceptos_incap)) & 
                            (pd.to_numeric(df['calendar_days'], errors='coerce') > 30)]
            if len(df_incap30) > 0:
                archivos_zip['incp_mayor_30_dias.xlsx'] = to_excel(df_incap30)
            
            df_dia_fam = df[(df['external_name_label'] == 'Día de la familia') & 
                            (pd.to_numeric(df['calendar_days'], errors='coerce') > 1)]
            if len(df_dia_fam) > 0:
                archivos_zip['dia_de_la_familia.xlsx'] = to_excel(df_dia_fam)
            
            st.success(f"📦 ZIP contendrá {len(archivos_zip)} archivo(s)")
            
            for nombre in archivos_zip.keys():
                st.markdown(f"- ✅ {nombre}")
            
            zip_data = crear_zip(archivos_zip)
            
            st.download_button(
                label=f"📥 DESCARGAR ZIP - PASO 2 ({len(archivos_zip)} archivos)",
                data=zip_data,
                file_name="PASO_2_Validaciones.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Ir al Paso 3", use_container_width=True):
                    st.session_state.paso_actual = 3
                    st.rerun()
            with col2:
                if st.button("✅ Finalizar", use_container_width=True):
                    st.session_state.paso_actual = 4
                    st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def paso3():
    header()
    st.markdown("### 🏥 Paso 3: Merge con Reporte 45 y CIE-10")
    
    with st.expander("📋 ¿Qué hace este paso?", expanded=False):
        st.markdown("**Entradas:** CSV Paso 2 + Reporte 45 (XLSX) + CIE-10 (XLSX)")
        st.markdown("**Proceso:** Merge con Reporte 45 y tabla CIE-10")
        st.markdown("**Salidas:** CSV con diagnósticos + ALERTA_DIAGNOSTICO.xlsx")
    
    st.warning("🔴 Necesitas 3 archivos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📤 1. CSV del Paso 2")
        csv_paso2 = st.file_uploader(
            "relacion_laboral_con_validaciones.csv",
            type=['csv'],
            key="csv_p2"
        )
    
    with col2:
        st.info("📤 2. Reporte 45 (Excel)")
        excel_reporte45 = st.file_uploader(
            "Reporte 45_*.XLSX",
            type=['xlsx', 'xls'],
            key="excel_r45"
        )
    
    with col3:
        st.info("📤 3. CIE-10 (Excel)")
        excel_cie10 = st.file_uploader(
            "CIE 10 - AJUSTADO.xlsx",
            type=['xlsx', 'xls'],
            key="excel_cie10"
        )
    
    if csv_paso2 and excel_reporte45 and excel_cie10:
        try:
            with st.spinner('⏳ Procesando merge con Reporte 45 y CIE-10...'):
                # Leer CSV del paso 2
                df_base = pd.read_csv(csv_paso2, encoding='utf-8-sig', dtype=str)
                st.info(f"✅ CSV Paso 2: {len(df_base):,} registros")
                
                # Leer Reporte 45
                df_reporte45 = pd.read_excel(excel_reporte45, dtype=str)
                st.info(f"✅ Reporte 45: {len(df_reporte45):,} registros")
                
                # Filtrar Reporte 45 por tipos específicos
                valores_filtro = [
                    'Enf Gral SOAT', 'Inc. Accidente de Trabajo',
                    'Inca. Enfer Gral Integral', 'Inca. Enfermedad  General',
                    'Prorroga Enf Gral SOAT', 'Prorroga Inc. Accid. Trab',
                    'Prorroga Inca/Enfer Gene', 'Incapa.fuera de turno'
                ]
                
                # Buscar columna de texto de clase
                col_txt_clase = None
                for col in df_reporte45.columns:
                    if 'txt' in col.lower() and 'pres' in col.lower():
                        col_txt_clase = col
                        break
                
                if col_txt_clase:
                    df_reporte45_filtrado = df_reporte45[df_reporte45[col_txt_clase].isin(valores_filtro)].copy()
                    st.info(f"✅ Reporte 45 filtrado: {len(df_reporte45_filtrado):,} registros")
                else:
                    df_reporte45_filtrado = df_reporte45.copy()
                
                # Filtrar CSV base también
                if 'external_name_label' in df_base.columns:
                    df_base_filtrado = df_base[df_base['external_name_label'].isin(valores_filtro)].copy()
                    st.info(f"✅ CSV base filtrado: {len(df_base_filtrado):,} registros")
                else:
                    df_base_filtrado = df_base.copy()
                
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
                    st.info(f"Columnas disponibles: {list(df_reporte45.columns)}")
                else:
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
                    st.markdown("### 🩺 Validando Diagnósticos")
                    
                    valores_requieren_diagnostico = [
                        'Inca. Enfermedad  General', 'Prorroga Inca/Enfer Gene',
                        'Inc. Accidente de Trabajo', 'Enf Gral SOAT', 'Prorroga Enf Gral SOAT',
                        'Licencia Paternidad', 'Prorroga Inc. Accid. Trab', 'Incapacidad gral SENA',
                        'Inca. Enfer Gral Integral', 'Licencia Paternidad Inegr', 'Licencia Maternidad',
                        'Incap  mayor 180 dias', 'Incap  mayor 540 dias', 'Lic Mater Interrumpida',
                        'Licencia Mater especial', 'Enf Gral Int SOAT', 'Inc. Enfer. General Hospi',
                        'Prorr Inc/Enf Gral ntegra', 'Incapacidad ARL SENA', 'Licencia Maternidad Integ'
                    ]
                    
                    # Buscar columna de diagnóstico en Reporte 45
                    col_diagnostico = None
                    for col in df_merged.columns:
                        if 'descripc' in col.lower() and 'enfermedad' in col.lower():
                            col_diagnostico = col
                            break
                    
                    if col_diagnostico and 'external_name_label' in df_merged.columns:
                        df_merged['alerta_diagnostico'] = df_merged.apply(
                            lambda row: 'ALERTA DIAGNOSTICO' 
                            if row['external_name_label'] in valores_requieren_diagnostico and 
                               (pd.isna(row[col_diagnostico]) or str(row[col_diagnostico]).strip() in ['', 'nan', 'None'])
                            else '', 
                            axis=1
                        )
                        
                        alertas_diag = (df_merged['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum()
                        st.metric("🚨 Alertas de Diagnóstico", alertas_diag)
                        
                        df_alerta_diagnostico = df_merged[df_merged['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO'].copy()
                    else:
                        st.warning("⚠️ No se pudo validar diagnósticos")
                        df_alerta_diagnostico = pd.DataFrame()
                    
                    # MERGE CON CIE-10
                    st.markdown("### 🏥 Agregando información CIE-10")
                    
                    df_cie10 = pd.read_excel(excel_cie10, dtype=str)
                    st.info(f"✅ CIE-10: {len(df_cie10):,} códigos")
                    
                    # Buscar columnas en CIE-10
                    col_codigo_cie = None
                    for col in df_cie10.columns:
                        if col.lower() in ['código', 'codigo', 'code']:
                            col_codigo_cie = col
                            break
                    
                    if col_codigo_cie and 'descripcion_general_external_code' in df_merged.columns:
                        # Limpiar códigos
                        df_merged['codigo_limpio'] = df_merged['descripcion_general_external_code'].str.strip().str.upper()
                        df_cie10['codigo_limpio'] = df_cie10[col_codigo_cie].str.strip().str.upper()
                        
                        # Seleccionar columnas de CIE-10 a agregar
                        cols_cie10 = [col_codigo_cie]
                        if 'Descripción' in df_cie10.columns:
                            cols_cie10.append('Descripción')
                        if 'TIPO' in df_cie10.columns:
                            cols_cie10.append('TIPO')
                        
                        cols_cie10.append('codigo_limpio')
                        df_cie10_subset = df_cie10[cols_cie10].copy()
                        
                        # Merge con CIE-10
                        df_final = pd.merge(
                            df_merged,
                            df_cie10_subset,
                            on='codigo_limpio',
                            how='left',
                            suffixes=('', '_cie10')
                        )
                        
                        # Renombrar columnas CIE-10
                        renombrar = {}
                        if col_codigo_cie in df_final.columns and col_codigo_cie != 'codigo_limpio':
                            renombrar[col_codigo_cie] = 'cie10_codigo'
                        if 'Descripción' in df_final.columns:
                            renombrar['Descripción'] = 'cie10_descripcion'
                        if 'TIPO' in df_final.columns:
                            renombrar['TIPO'] = 'cie10_tipo'
                        
                        df_final = df_final.rename(columns=renombrar)
                        
                        # Eliminar columna temporal
                        if 'codigo_limpio' in df_final.columns:
                            df_final = df_final.drop(['codigo_limpio'], axis=1)
                        
                        con_cie10 = df_final['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_final.columns else 0
                        st.success(f"✅ Merge CIE-10: {con_cie10:,} registros con información")
                    else:
                        df_final = df_merged.copy()
                        st.warning("⚠️ No se pudo hacer merge con CIE-10")
            
            st.success("✅ Proceso completado!")
            
            # Métricas finales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Registros", f"{len(df_final):,}")
            with col2:
                alertas = (df_final['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum() if 'alerta_diagnostico' in df_final.columns else 0
                st.metric("🚨 Alertas Diag", alertas)
            with col3:
                con_cie = df_final['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_final.columns else 0
                st.metric("🏥 Con CIE-10", con_cie)
            with col4:
                st.metric("📋 Columnas", len(df_final.columns))
            
            # Vista previa
            st.markdown("### 👀 Vista Previa")
            st.dataframe(df_final.head(10), use_container_width=True)
            
            # GENERAR ZIP
            st.markdown("---")
            st.markdown("### 📦 GENERAR ZIP CON TODO")
            
            archivos_zip = {
                'ausentismos_con_cie10.csv': to_csv(df_final)
            }
            
            # Agregar archivo de alertas de diagnóstico si hay
            if len(df_alerta_diagnostico) > 0:
                archivos_zip['ALERTA_DIAGNOSTICO.xlsx'] = to_excel(df_alerta_diagnostico)
            
            st.success(f"📦 ZIP contendrá {len(archivos_zip)} archivo(s)")
            
            for nombre in archivos_zip.keys():
                st.markdown(f"- ✅ {nombre}")
            
            zip_data = crear_zip(archivos_zip)
            
            st.download_button(
                label=f"📥 DESCARGAR ZIP - PASO 3 ({len(archivos_zip)} archivos)",
                data=zip_data,
                file_name="PASO_3_CIE10_y_Diagnosticos.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
            
            st.markdown("---")
            if st.button("✅ Finalizar Proceso", use_container_width=True, type="primary"):
                st.session_state.paso_actual = 4
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver error completo"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())
    
    else:
        st.info("📤 Por favor sube los 3 archivos requeridos para continuar")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Volver al Paso 2", use_container_width=True):
                st.session_state.paso_actual = 2
                st.rerun()
        with col2:
            if st.button("⏭️ Saltar al Resumen", use_container_width=True):
                st.session_state.paso_actual = 4
                st.rerun()

def paso4():
    header()
    st.markdown("### 🎉 Proceso Completado")
    
    st.balloons()
    st.success("✅ Has completado el proceso de auditoría!")
    
    st.markdown("""
    ### 📋 Archivos Generados
    
    **Paso 1:**
    - ausentismo_procesado_especifico.csv
    
    **Paso 2:**
    - relacion_laboral_con_validaciones.csv
    - Archivos Excel de alertas
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pasos", "2/3")
    with col2:
        st.metric("Archivos", "10+")
    with col3:
        st.metric("Estado", "Completo ✅")
    
    st.markdown("---")
    if st.button("🔄 Nuevo Proceso", use_container_width=True, type="primary"):
        st.session_state.paso_actual = 1
        st.rerun()

def sidebar():
    with st.sidebar:
        st.markdown("# 🧭 Navegación")
        st.markdown("---")
        
        progreso = (st.session_state.paso_actual - 1) / 3 * 100
        st.progress(progreso / 100)
        st.markdown(f"**Progreso:** {progreso:.0f}%")
        
        st.markdown("---")
        
        pasos = [
            ("1️⃣", "Procesamiento", 1),
            ("2️⃣", "Validaciones", 2),
            ("3️⃣", "Scripts Adicionales", 3),
            ("4️⃣", "Resumen", 4)
        ]
        
        for emoji, nombre, num in pasos:
            if st.session_state.paso_actual == num:
                st.markdown(f"**{emoji} {nombre}** ◄")
            else:
                if st.button(f"{emoji} {nombre}", key=f"nav_{num}", use_container_width=True):
                    st.session_state.paso_actual = num
                    st.rerun()
        
        st.markdown("---")
        st.markdown("""
        ### 📝 Flujo
        1. Sube CSV → Descarga ZIP
        2. Sube CSV+Excel → Descarga ZIP
        3. Scripts opcionales
        4. Resumen
        """)

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
