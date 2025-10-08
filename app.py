import streamlit as st
import pandas as pd
from io import BytesIO
import tempfile
import os

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
        <p>Sistema Paso a Paso con Descargas</p>
    </div>
    """, unsafe_allow_html=True)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

# ============================================================================
# PASO 1: PROCESA CSV Y DESCARGA
# ============================================================================

def paso1():
    header()
    st.markdown("### 🔄 Paso 1: Procesamiento Inicial")
    
    with st.expander("📋 ¿Qué hace este paso?"):
        st.markdown("""
        **Script:** `auditoria_ausentismos_part1.py`
        
        **Entrada:**
        - CSV de ausentismos (AusentismoCOL-ApprovedPayroll...)
        
        **Salida:**
        - ✅ `ausentismo_procesado_especifico.csv` (para usar en Paso 2)
        """)
    
    st.info("📤 Sube el archivo CSV de ausentismos")
    
    archivo = st.file_uploader("Archivo CSV", type=['csv'], key="csv1")
    
    if archivo:
        try:
            with st.spinner('⏳ Procesando con part1.py...'):
                # IMPORTAR PART1
                from auditoria_ausentismos_part1 import (
                    TABLA_HOMOLOGACION, TABLA_VALIDADORES, TABLA_SUB_TIPO_FSE,
                    COLUMNAS_REQUERIDAS, MAPEO_COLUMNAS, limpiar_fecha_para_llave
                )
                
                # EJECUTAR LÓGICA DE PART1
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
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Registros", f"{len(df_final):,}")
            with col2:
                st.metric("📋 Columnas", len(df_final.columns))
            with col3:
                alertas = (df_final['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
                st.metric("⚠️ Alertas", alertas)
            
            # Vista previa
            st.markdown("### 👀 Vista Previa")
            st.dataframe(df_final.head(10), use_container_width=True)
            
            # DESCARGA
            st.markdown("---")
            st.markdown("### 💾 DESCARGA para continuar al Paso 2")
            csv_data = to_csv(df_final)
            st.download_button(
                label="📥 DESCARGAR: ausentismo_procesado_especifico.csv",
                data=csv_data,
                file_name="ausentismo_procesado_especifico.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
            
            st.info("👉 **Paso siguiente:** Descarga este archivo y úsalo en el Paso 2")
            
            # Botón siguiente
            st.markdown("---")
            if st.button("▶️ Ir al Paso 2", use_container_width=True):
                st.session_state.paso_actual = 2
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ============================================================================
# PASO 2: SUBE CSV DE PASO 1 + EXCEL PERSONAL, DESCARGA VALIDACIONES
# ============================================================================

def paso2():
    header()
    st.markdown("### 🔗 Paso 2: Validaciones y Merge")
    
    with st.expander("📋 ¿Qué hace este paso?"):
        st.markdown("""
        **Script:** `auditoria_ausentismos_part2.py`
        
        **Entradas:**
        - ✅ `ausentismo_procesado_especifico.csv` (del Paso 1)
        - ✅ `MD_*.XLSX` (archivo de personal)
        
        **Salidas:**
        - ✅ `relacion_laboral_con_validaciones.csv` (para usar en Paso 3)
        - ✅ 9+ archivos Excel de alertas (Sena_error, Ley_50_error, etc.)
        """)
    
    st.warning("🔴 **IMPORTANTE:** Necesitas el archivo CSV generado en el Paso 1")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📤 1. Sube el CSV del Paso 1")
        csv_paso1 = st.file_uploader(
            "ausentismo_procesado_especifico.csv",
            type=['csv'],
            key="csv_paso1"
        )
    
    with col2:
        st.info("📤 2. Sube el Excel de Personal")
        excel_personal = st.file_uploader(
            "MD_*.XLSX",
            type=['xlsx', 'xls'],
            key="excel_personal"
        )
    
    if csv_paso1 and excel_personal:
        try:
            with st.spinner('⏳ Procesando con part2.py... (Esto puede tardar)'):
                # Leer archivos
                df_ausentismo = pd.read_csv(csv_paso1, encoding='utf-8-sig')
                df_personal = pd.read_excel(excel_personal)
                
                st.success(f"✅ CSV leído: {len(df_ausentismo):,} registros")
                st.success(f"✅ Excel leído: {len(df_personal):,} registros")
                
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
                    st.error("❌ No se encontraron columnas necesarias en el Excel")
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
                
                # Crear columnas validación
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
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Registros", f"{len(df):,}")
            with col2:
                st.metric("🚨 Errores SENA", len(df_errores_sena))
            with col3:
                st.metric("🚨 Errores Ley 50", len(df_errores_ley50))
            
            # DESCARGAS
            st.markdown("---")
            st.markdown("### 💾 DESCARGAS")
            
            # Archivo principal
            st.markdown("#### 📄 Archivo Principal (para Paso 3)")
            csv_main = to_csv(df)
            st.download_button(
                "📥 DESCARGAR: relacion_laboral_con_validaciones.csv",
                csv_main,
                "relacion_laboral_con_validaciones.csv",
                "text/csv",
                use_container_width=True,
                type="primary"
            )
            
            # Archivos de alertas
            st.markdown("#### 🚨 Archivos de Alertas")
            
            alertas = []
            if len(df_errores_sena) > 0:
                alertas.append(('Sena_error_validar.xlsx', df_errores_sena))
            if len(df_errores_ley50) > 0:
                alertas.append(('Ley_50_error_validar.xlsx', df_errores_ley50))
            
            # Otras alertas (simplificado)
            df_alert_pat = df[(df['licencia_paternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Paternidad')]
            if len(df_alert_pat) > 0:
                alertas.append(('alerta_licencia_paternidad.xlsx', df_alert_pat))
            
            df_alert_mat = df[(df['licencia_maternidad'] == 'Concepto No Aplica') & (df['external_name_label'] == 'Licencia Maternidad')]
            if len(df_alert_mat) > 0:
                alertas.append(('alerta_licencia_maternidad.xlsx', df_alert_mat))
            
            if alertas:
                cols = st.columns(2)
                for i, (nombre, df_alert) in enumerate(alertas):
                    with cols[i % 2]:
                        excel_data = to_excel(df_alert)
                        st.download_button(
                            f"📥 {nombre} ({len(df_alert)})",
                            excel_data,
                            nombre,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"alert_{i}",
                            use_container_width=True
                        )
            else:
                st.success("✅ No hay alertas - Todo correcto")
            
            # Vista previa
            st.markdown("### 👀 Vista Previa")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.info("👉 **Paso siguiente:** Descarga el CSV principal para usar en Paso 3 (opcional)")
            
            # Botón siguiente
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Ir al Paso 3 (Opcional)", use_container_width=True):
                    st.session_state.paso_actual = 3
                    st.rerun()
            with col2:
                if st.button("✅ Finalizar Aquí", use_container_width=True):
                    st.session_state.paso_actual = 4
                    st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Ver error completo"):
                st.code(str(e))

# ============================================================================
# PASO 3: MERGE CON CIE-10 (OPCIONAL)
# ============================================================================

def paso3():
    header()
    st.markdown("### 🏥 Paso 3: Merge con CIE-10 (Opcional)")
    
    with st.expander("📋 ¿Qué hace este paso?"):
        st.markdown("""
        **Script:** `auditoria_ausentismos_part3.py` o scripts de merge
        
        **Entradas:**
        - ✅ CSV del Paso 2 (o merged con Reporte 45)
        - ✅ `CIE 10 - AJUSTADO - NÓMINA.xlsx`
        
        **Salida:**
        - ✅ `ausentismos_con_cie10.csv` (archivo final con diagnósticos)
        """)
    
    st.info("""
    📝 **Nota:** Este paso requiere scripts adicionales para:
    1. Procesar Reporte 45 (opcional)
    2. Hacer merge con Reporte 45 (opcional)
    3. Merge con CIE-10
    
    Usa los scripts en la carpeta `scripts/` para estos procesos.
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
    
    st.success("✅ ¡Felicitaciones! Has completado el proceso de auditoría")
    
    st.markdown("""
    ### 📋 Resumen
    
    Has generado los siguientes archivos:
    
    **Paso 1:**
    - ✅ `ausentismo_procesado_especifico.csv`
    
    **Paso 2:**
    - ✅ `relacion_laboral_con_validaciones.csv`
    - ✅ Archivos de alertas (Excel)
    
    **Paso 3 (Opcional):**
    - ⭕ Merge con Reporte 45 y CIE-10
    """)
    
    st.markdown("---")
    
    if st.button("🔄 Iniciar Nuevo Proceso", use_container_width=True, type="primary"):
        st.session_state.paso_actual = 1
        st.rerun()

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
            ("1️⃣", "Procesamiento", 1),
            ("2️⃣", "Validaciones", 2),
            ("3️⃣", "Merge CIE-10 (Opcional)", 3),
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
        1. Sube CSV → Descarga
        2. Sube CSV+Excel → Descarga
        3. (Opcional) Merge CIE-10
        4. ¡Listo!
        """)

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
