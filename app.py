### 🎯 Próximos Pasos Recomendados:
    
    1. **Revisa los archivos de alertas** - Corrige los errores identificados
    2. **Documenta los resultados** - Mantén un registro de las auditorías
    3. **Archiva los archivos** - Guarda los ZIPs para referencia futura
    4. **Comunica hallazgos** - Comparte las alertas con los equipos correspondientes
    
    ---
    
    ### 📊 Estadísticas de tu Proceso:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Pasos Completados", "2 de 3", delta="Paso 3 opcional")
    
    with col2:
        st.metric("Archivos Generados", "10+", delta="CSV y Excel")
    
    with col3:
        st.metric("Estado", "Completo ✅")
    
    st.markdown("---")
    
    with st.expander("📚 Documentación y Soporte"):
        st.markdown("""
        **📖 Recursos disponibles:**
        - README.md - Documentación completa
        - GUIA_RAPIDA.md - Guía de inicio rápido
        - Scripts en carpeta `scripts/` - Para procesos adicionales
        
        **🐛 Reportar problemas:**
        - GitHub Issues: [Reportar bug](https://github.com/TU_USUARIO/auditoria-ausentismos/issues)
        
        **💬 Contacto:**
        - Email: tu_email@ejemplo.com
        """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Iniciar Nuevo Proceso", use_container_width=True, type="primary"):
            st.session_state.paso_actual = 1
            st.rerun()
    
    with col2:
        if st.button("📊 Ver Estadísticas Detalladas", use_container_width=True):
            st.info("Esta funcionalidad estará disponible próximamente")

# ============================================================================
# SIDEBAR
# ============================================================================

def sidebar():
    with st.sidebar:
        st.markdown("# 🧭 Navegación")
        st.markdown("---")
        
        # Progreso
        progreso = (st.session_state.paso_actual - 1) / 3 * 100
        st.progress(progreso / 100)
        st.markdown(f"**Progreso:** {progreso:.0f}%")
        
        st.markdown("---")
        
        # Pasos
        pasos = [
            ("1️⃣", "Procesamiento", 1, "✅"),
            ("2️⃣", "Validaciones", 2, "✅"),
            ("3️⃣", "Merge CIE-10", 3, "⭕"),
            ("4️⃣", "Resumen", 4, "🎉")
        ]
        
        for emoji, nombre, num, status in pasos:
            if st.session_state.paso_actual == num:
                st.markdown(f"**{emoji} {nombre}** ◄")
            else:
                if st.button(f"{emoji} {nombre}", key=f"nav_{num}", use_container_width=True):
                    st.session_state.paso_actual = num
                    st.rerun()
            
            # Mostrar estado
            if num < st.session_state.paso_actual:
                st.markdown(f"<small style='color: green;'>{status} Completado</small>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📝 Flujo del Proceso")
        st.markdown("""
        **Paso 1:**
        - Sube CSV
        - 📥 Descarga ZIP
        
        **Paso 2:**
        - Sube CSV (Paso 1)
        - Sube Excel (Personal)
        - 📥 Descarga ZIP
        
        **Paso 3:**
        - Opcional (scripts)
        
        **Paso 4:**
        - ¡Listo! 🎉
        """)
        
        st.markdown("---")
        
        # Info del sistema
        st.markdown("### ℹ️ Sistema")
        st.markdown("""
        **Archivos temporales:** ❌ No  
        **Almacenamiento:** ❌ No  
        **Descargas:** ✅ ZIP  
        
        Tus archivos **NO** se guardan en el servidor. 
        Todo se procesa en memoria y se descarga directamente.
        """)
        
        st.markdown("---")
        
        # Versión
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            <p><strong>Auditoría Ausentismos</strong></p>
            <p>v1.0.0</p>
            <p>Juan José Bustos</p>
            <p>Grupo Jerónimo Martins</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# MAIN
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
import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="Auditoría Ausentismos",
    page_icon="📊",
    layout="wide"
)

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
    .big-download {
        background: #4CAF50;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 2rem 0;
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
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
        <p>Sistema Paso a Paso - Descarga → Sube → Descarga</p>
    </div>
    """, unsafe_allow_html=True)

def to_excel(df):
    """Convierte DataFrame a Excel en memoria"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def to_csv(df):
    """Convierte DataFrame a CSV en memoria"""
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

def crear_zip(archivos_dict):
    """
    Crea un ZIP en memoria con múltiples archivos
    archivos_dict = {'nombre_archivo.csv': bytes_data, ...}
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for nombre, data in archivos_dict.items():
            zip_file.writestr(nombre, data)
    return zip_buffer.getvalue()

# ============================================================================
# PASO 1: PROCESA CSV Y GENERA ZIP
# ============================================================================

def paso1():
    header()
    st.markdown("### 🔄 Paso 1: Procesamiento Inicial")
    
    with st.expander("📋 ¿Qué hace este paso?", expanded=False):
        st.markdown("""
        **Entrada:**
        - CSV de ausentismos (AusentismoCOL-ApprovedPayroll...)
        
        **Proceso:**
        - Ejecuta lógica de `auditoria_ausentismos_part1.py`
        - Homologación SSF vs SAP
        - Mapea validadores
        - Crea llaves únicas
        
        **Salida (ZIP):**
        - ✅ `ausentismo_procesado_especifico.csv` → **Úsalo en Paso 2**
        """)
    
    st.info("📤 Sube el archivo CSV de ausentismos")
    
    archivo = st.file_uploader("Archivo CSV", type=['csv'], key="csv1")
    
    if archivo:
        try:
            with st.spinner('⏳ Procesando archivo...'):
                # IMPORTAR LÓGICA DE PART1
                from auditoria_ausentismos_part1 import (
                    TABLA_HOMOLOGACION, TABLA_VALIDADORES, TABLA_SUB_TIPO_FSE,
                    COLUMNAS_REQUERIDAS, MAPEO_COLUMNAS, limpiar_fecha_para_llave
                )
                
                # EJECUTAR PROCESAMIENTO
                df = pd.read_csv(archivo, skiprows=2, encoding='utf-8', dtype=str)
                
                columnas_encontradas = [col for col in COLUMNAS_REQUERIDAS if col in df.columns]
                df_especifico = df[columnas_encontradas].copy()
                
                # Homologación
                df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'] = \
                    df_especifico['externalCode'].map(TABLA_HOMOLOGACION)
                
                # Validadores
                df_especifico['lastModifiedBy_limpio'] = df_especifico['lastModifiedBy'].astype(str).str.strip()
                df_especifico['nombre_validador'] = df_especifico['lastModifiedBy_limpio'].map(TABLA_VALIDADORES)\
                    .fillna('ALERTA VALIDADOR NO ENCONTRADO')
                df_especifico = df_especifico.drop(['lastModifiedBy_limpio'], axis=1)
                
                # Sub_tipo y FSE
                df_especifico['Sub_tipo'] = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                    lambda x: TABLA_SUB_TIPO_FSE.get(str(x), {}).get('sub_tipo', 'ALERTA SUB_TIPO NO ENCONTRADO') 
                    if pd.notna(x) else 'ALERTA SUB_TIPO NO ENCONTRADO'
                )
                df_especifico['FSE'] = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                    lambda x: TABLA_SUB_TIPO_FSE.get(str(x), {}).get('fse', 'No Aplica') 
                    if pd.notna(x) else 'No Aplica'
                )
                
                # Llave
                df_especifico['startDate_limpia'] = df_especifico['startDate'].apply(limpiar_fecha_para_llave)
                df_especifico['endDate_limpia'] = df_especifico['endDate'].apply(limpiar_fecha_para_llave)
                df_especifico['llave'] = (
                    df_especifico['ID personal'].astype(str).fillna('') +
                    df_especifico['startDate_limpia'] +
                    df_especifico['endDate_limpia'] +
                    df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].astype(str).fillna('')
                )
                df_especifico = df_especifico.drop(['startDate_limpia', 'endDate_limpia'], axis=1)
                
                # Renombrar
                mapeo_actual = {col: MAPEO_COLUMNAS[col] for col in df_especifico.columns if col in MAPEO_COLUMNAS}
                df_final = df_especifico.rename(columns=mapeo_actual)
                
                # Limpiar
                if 'numero_documento_identidad' in df_final.columns:
                    df_final['numero_documento_identidad'] = df_final['numero_documento_identidad'].astype(str).replace('nan', '')
                    df_final['numero_documento_identidad'] = '"' + df_final['numero_documento_identidad'] + '"'
                
                if 'llave' in df_final.columns:
                    df_final['llave'] = 'K' + df_final['llave'].astype(str)
            
            st.success("✅ Procesamiento completado!")
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Registros", f"{len(df_final):,}")
            with col2:
                st.metric("📋 Columnas", len(df_final.columns))
            with col3:
                alertas = (df_final['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
                st.metric("⚠️ Alertas", alertas)
            with col4:
                st.metric("🔑 Llaves Únicas", df_final['llave'].nunique())
            
            # Vista previa
            st.markdown("### 👀 Vista Previa")
            st.dataframe(df_final.head(10), use_container_width=True, height=300)
            
            # GENERAR ZIP
            st.markdown("---")
            st.markdown('<div class="big-download">📦 DESCARGA TODO EN UN ZIP</div>', unsafe_allow_html=True)
            
            # Preparar archivos para ZIP
            archivos_zip = {
                'ausentismo_procesado_especifico.csv': to_csv(df_final)
            }
            
            zip_data = crear_zip(archivos_zip)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.download_button(
                    label="📥 DESCARGAR ZIP - PASO 1 (ausentismo_procesado_especifico.csv)",
                    data=zip_data,
                    file_name="PASO_1_Archivos_Procesados.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
            
            with col2:
                # También opción individual
                st.download_button(
                    label="📄 Solo CSV",
                    data=to_csv(df_final),
                    file_name="ausentismo_procesado_especifico.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.success("👉 **Siguiente:** Descarga el ZIP, extrae el CSV y úsalo en el Paso 2")
            
            # Botón siguiente
            st.markdown("---")
            if st.button("▶️ Ir al Paso 2", use_container_width=True):
                st.session_state.paso_actual = 2
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver error completo"):
                st.code(str(e))

# ============================================================================
# PASO 2: SUBE CSV PASO 1 + EXCEL, GENERA ZIP CON TODO
# ============================================================================

def paso2():
    header()
    st.markdown("### 🔗 Paso 2: Validaciones y Merge")
    
    with st.expander("📋 ¿Qué hace este paso?", expanded=False):
        st.markdown("""
        **Entradas:**
        - ✅ `ausentismo_procesado_especifico.csv` (del Paso 1)
        - ✅ `MD_*.XLSX` (archivo de personal/relación laboral)
        
        **Proceso:**
        - Ejecuta lógica de `auditoria_ausentismos_part2.py`
        - Merge con relación laboral
        - Validaciones SENA y Ley 50
        - Genera 6 columnas de validación
        - Crea archivos de alertas
        
        **Salida (ZIP):**
        - ✅ `relacion_laboral_con_validaciones.csv` → **Úsalo en Paso 3**
        - ✅ 9+ archivos Excel de alertas (Sena_error, Ley_50_error, etc.)
        """)
    
    st.warning("🔴 **IMPORTANTE:** Necesitas 2 archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📤 1. CSV del Paso 1")
        csv_paso1 = st.file_uploader(
            "ausentismo_procesado_especifico.csv",
            type=['csv'],
            key="csv_p1",
            help="El archivo que descargaste en el Paso 1"
        )
    
    with col2:
        st.info("📤 2. Excel de Personal")
        excel_personal = st.file_uploader(
            "MD_*.XLSX",
            type=['xlsx', 'xls'],
            key="excel_pers",
            help="Archivo maestro de datos de personal"
        )
    
    if csv_paso1 and excel_personal:
        try:
            with st.spinner('⏳ Procesando validaciones... (puede tardar unos minutos)'):
                # Leer archivos
                df_ausentismo = pd.read_csv(csv_paso1, encoding='utf-8-sig')
                df_personal = pd.read_excel(excel_personal)
                
                st.info(f"✅ CSV: {len(df_ausentismo):,} registros | Excel: {len(df_personal):,} registros")
                
                # Buscar columnas de personal
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
                    st.error("❌ No se encontraron columnas necesarias en el Excel")
                    st.info(f"Columnas disponibles: {list(df_personal.columns)}")
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
                conceptos_validos_sena = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA']
                df_errores_sena = df_aprendizaje[~df_aprendizaje['external_name_label'].isin(conceptos_validos_sena)].copy()
                
                # Validaciones Ley 50
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
            
            st.success("✅ Validaciones completadas!")
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Registros", f"{len(df):,}")
            with col2:
                st.metric("🚨 Errores SENA", len(df_errores_sena))
            with col3:
                st.metric("🚨 Errores Ley 50", len(df_errores_ley50))
            with col4:
                total_alertas = len(df_errores_sena) + len(df_errores_ley50)
                st.metric("📋 Total Alertas", total_alertas)
            
            # Vista previa
            st.markdown("### 👀 Vista Previa del Resultado")
            st.dataframe(df.head(10), use_container_width=True, height=300)
            
            # PREPARAR ARCHIVOS PARA ZIP
            st.markdown("---")
            st.markdown('<div class="big-download">📦 DESCARGA TODO EN UN ZIP</div>', unsafe_allow_html=True)
            
            archivos_zip = {
                'relacion_laboral_con_validaciones.csv': to_csv(df)
            }
            
            # Agregar archivos de alertas al ZIP
            alertas_generadas = []
            
            if len(df_errores_sena) > 0:
                archivos_zip['Sena_error_validar.xlsx'] = to_excel(df_errores_sena)
                alertas_generadas.append(('Sena_error_validar.xlsx', len(df_errores_sena)))
            
            if len(df_errores_ley50) > 0:
                archivos_zip['Ley_50_error_validar.xlsx'] = to_excel(df_errores_ley50)
                alertas_generadas.append(('Ley_50_error_validar.xlsx', len(df_errores_ley50)))
            
            # Otras alertas
            df_alert_pat = df[(df['licencia_paternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Paternidad')]
            if len(df_alert_pat) > 0:
                archivos_zip['alerta_licencia_paternidad.xlsx'] = to_excel(df_alert_pat)
                alertas_generadas.append(('alerta_licencia_paternidad.xlsx', len(df_alert_pat)))
            
            df_alert_mat = df[(df['licencia_maternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Maternidad')]
            if len(df_alert_mat) > 0:
                archivos_zip['alerta_licencia_maternidad.xlsx'] = to_excel(df_alert_mat)
                alertas_generadas.append(('alerta_licencia_maternidad.xlsx', len(df_alert_mat)))
            
            df_alert_luto = df[(df['ley_de_luto'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Ley de luto')]
            if len(df_alert_luto) > 0:
                archivos_zip['alerta_ley_de_luto.xlsx'] = to_excel(df_alert_luto)
                alertas_generadas.append(('alerta_ley_de_luto.xlsx', len(df_alert_luto)))
            
            df_alert_incap = df[(df['incap_fuera_de_turno'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Incapa.fuera de turno')]
            if len(df_alert_incap) > 0:
                archivos_zip['alerta_incap_fuera_de_turno.xlsx'] = to_excel(df_alert_incap)
                alertas_generadas.append(('alerta_incap_fuera_de_turno.xlsx', len(df_alert_incap)))
            
            # Incapacidades > 30 días
            conceptos_incap = ['Incapacidad enfermedad general', 'Prorroga Inca/Enfer Gene',
                               'Enf Gral SOAT', 'Inc. Accidente de Trabajo', 'Prorroga Inc. Accid. Trab']
            df_incap30 = df[(df['external_name_label'].isin(conceptos_incap)) & 
                            (pd.to_numeric(df['calendar_days'], errors='coerce') > 30)]
            if len(df_incap30) > 0:
                archivos_zip['incp_mayor_30_dias.xlsx'] = to_excel(df_incap30)
                alertas_generadas.append(('incp_mayor_30_dias.xlsx', len(df_incap30)))
            
            # Día de familia > 1
            df_dia_fam = df[(df['external_name_label'] == 'Día de la familia') & 
                            (pd.to_numeric(df['calendar_days'], errors='coerce') > 1)]
            if len(df_dia_fam) > 0:
                archivos_zip['dia_de_la_familia.xlsx'] = to_excel(df_dia_fam)
                alertas_generadas.append(('dia_de_la_familia.xlsx', len(df_dia_fam)))
            
            # Ausentismos sin pago > 10 días
            conceptos_sin_pago = ['Aus Reg sin Soporte', 'Suspensión']
            df_sin_pago = df[(df['external_name_label'].isin(conceptos_sin_pago)) & 
                             (pd.to_numeric(df['calendar_days'], errors='coerce') > 10)]
            if len(df_sin_pago) > 0:
                archivos_zip['Validacion_ausentismos_sin_pago_mayor_10_dias.xlsx'] = to_excel(df_sin_pago)
                alertas_generadas.append(('Validacion_ausentismos_sin_pago_mayor_10_dias.xlsx', len(df_sin_pago)))
            
            # Mostrar archivos que se incluirán
            st.success(f"📦 El ZIP contiene **{len(archivos_zip)} archivo(s)**:")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("**Archivo principal:**")
                st.markdown("- ✅ `relacion_laboral_con_validaciones.csv`")
                
                if alertas_generadas:
                    st.markdown(f"\n**Archivos de alertas ({len(alertas_generadas)}):**")
                    for nombre, cantidad in alertas_generadas:
                        st.markdown(f"- 🚨 `{nombre}` ({cantidad} registros)")
                else:
                    st.success("- ✅ No hay alertas")
            
            with col2:
                st.metric("Total archivos", len(archivos_zip))
            
            # GENERAR Y DESCARGAR ZIP
            zip_data = crear_zip(archivos_zip)
            
            st.download_button(
                label=f"📥 DESCARGAR ZIP - PASO 2 ({len(archivos_zip)} archivos)",
                data=zip_data,
                file_name="PASO_2_Validaciones_y_Alertas.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
            
            st.success("👉 **Siguiente:** Si necesitas merge con Reporte 45 o CIE-10, ve al Paso 3. Sino, ¡ya terminaste!")
            
            # Botones navegación
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Ir al Paso 3 (Opcional)", use_container_width=True):
                    st.session_state.paso_actual = 3
                    st.rerun()
            with col2:
                if st.button("✅ Finalizar Aquí", use_container_width=True, type="primary"):
                    st.session_state.paso_actual = 4
                    st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver error completo"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())

# ============================================================================
# PASO 3: INFO PARA SCRIPTS ADICIONALES
# ============================================================================

def paso3():
    header()
    st.markdown("### 🏥 Paso 3: Merge con Reporte 45 y CIE-10 (Opcional)")
    
    st.info("""
    📝 **Este paso requiere usar scripts adicionales por separado:**
    
    Los archivos `part3.py` y scripts de merge están diseñados para ejecutarse 
    desde línea de comandos con rutas fijas.
    
    **Para completar este paso:**
    
    1. Usa el script `procesar_reporte_45.py` para procesar el Reporte 45
    2. Usa el script `merge_ausentismos.py` para hacer merge
    3. Usa el script `merge_cie10.py` para agregar información CIE-10
    
    **Consulta la documentación en README.md para más detalles.**
    """)
    
    with st.expander("📚 Ver rutas de los scripts"):
        st.code("""
# Scripts disponibles en la carpeta scripts/:

scripts/
├── procesar_reporte_45.py    # Procesa Reporte 45 de SAP
├── merge_ausentismos.py       # Merge con Reporte 45
└── merge_cie10.py             # Agrega información CIE-10

# Ejecutar desde terminal:
python scripts/procesar_reporte_45.py
python scripts/merge_ausentismos.py
python scripts/merge_cie10.py
        """)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Volver al Paso 2", use_container_width=True):
            st.session_state.paso_actual = 2
            st.rerun()
    with col2:
        if st.button("✅ Finalizar", use_container_width=True, type="primary"):
            st.session_state.paso_actual = 4
            st.rerun()

# ============================================================================
# PASO 4: RESUMEN FINAL
# ============================================================================

def paso4():
    header()
    st.markdown("### 🎉 Proceso Completado")
    
    st.balloons()
    
    st.success("✅ ¡Felicitaciones! Has completado el proceso de auditoría de ausentismos")
    
    st.markdown("""
    ### 📋 Resumen de Archivos Generados
    
    **📦 Paso 1:**
    - ✅ `ausentismo_procesado_especifico.csv`
    
    **📦 Paso 2:**
    - ✅ `relacion_laboral_con_validaciones.csv`
    - ✅ Archivos Excel de alertas (Sena_error, Ley_50_error, etc.)
    
    **📦 Paso 3 (Opcional):**
    - ⭕ Merge con Reporte 45
    - ⭕ Información CIE-10
    
    ---
    
    ### 🎯 Próximos Pasos Recomendados:
    
    1. **Revisa los archivos de alertas** - Corrige los errores identificados
    2. **Documenta los resultados** - Mantén un registro de las au
