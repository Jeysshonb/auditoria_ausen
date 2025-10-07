import streamlit as st
import pandas as pd
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Auditoría Ausentismos",
    page_icon="📊",
    layout="wide"
)

# Inicializar session_state
if 'paso_actual' not in st.session_state:
    st.session_state.paso_actual = 1
if 'df_parte1' not in st.session_state:
    st.session_state.df_parte1 = None
if 'df_parte2' not in st.session_state:
    st.session_state.df_parte2 = None
if 'archivos_generados' not in st.session_state:
    st.session_state.archivos_generados = {}

# ============================================================================
# TABLAS DE CONFIGURACIÓN
# ============================================================================

TABLA_HOMOLOGACION = {
    'CO_vacatio': '100', 'CO_SICK180': '188', 'CO_EXPSUSP': '189', 'CO_PAID': '190',
    'CO_UNPAID': '191', 'CO_CTR_SEN': '198', 'CO_SICK': '200', 'CO_SICKINT': '201',
    'CO_SICKSOA': '202', 'CO_PR_QRT': '204', 'CO_FAMILY': '205', 'CO_WORKACC': '215',
    'CO_ILL': '230', 'CO_ILL_EXT': '231', 'CO_ILLSEXT': '232', 'CO_SICK540': '235',
    'CO_WRKACXT': '250', 'CO_SICKSEN': '280', 'CO_MAT': '300', 'CO_MAT_SPE': '302',
    'CO_MAT_ITR': '305', 'CO_PAT': '310', 'CO_PAT_INT': '311', 'CO_DOM_CAL': '330',
    'CO_MOURN': '340', 'CO_UNJ': '380', 'CO_SUS': '381', 'CO_SHFT_SK': '383',
    'CO_REG_WOS': '397', 'CO_MAT_INT': '301', 'CO_SICKARL': '187', 'CO_UNJ_INT': '197',
    'CO_SCIT_SO': '203', 'CO_MOURN_I': '341', 'CO_WKACSEN': '281', 'CO_MAT_SEN': '398',
    'CO_WRKACIT': '216', 'CO_INT_SUS': '195', 'CO_NONWORK': '192', 'CO_DELICAT': '206',
    'CO_PR_QRTI': '334', 'CO_ILLSEIN': '233', 'CO_DM_CALI': '331', 'CO_VOTING': '345',
    'CO_INT_UNP': '196', 'CO_FAM_FDS': '205', 'CO_VacationsFDS': '100'
}

TABLA_VALIDADORES = {
    '80002749': 'Diana Paola Martinez Diaz', '62208433': 'Nini Johanna Neira',
    '62208420': 'Maria Lorena Ospina', '62208383': 'Juan Sebastian Sanabria Cabezas',
    '62208367': 'Yeimy Velasco', '60005132': 'Angie Paola Muñoz',
    '80025780': 'Buitrago Baron Deisy Marley', '80005980': 'Caro Salamanca Wilson Alfredo',
    '80003719': 'Carreño Diaz Natalia Andrea', '60005117': 'Daniela Maria Herrera',
    '80022209': 'Guerra Cabrera Carolina', '80025779': 'Huerfano Davila Edgar Andres',
    '60005052': 'Jose Esteban Vargas', '60006940': 'Juan Esteban Sanabria',
    '60005371': 'Lenin Karina Triana', '60005046': 'Luis Armando Chacon',
    '60005129': 'Luz Liliana Rodriguez', '60006593': 'Luz Liliana Rodriguez',
    '60006112': 'Mancera Reinosa Diana Maria', '60006909': 'Maria Jose Alfonso',
    '60005057': 'Maria Lorena Ospina', '80000523': 'Rodriguez Gutierrez Paula Marcela',
    '80025781': 'Yaima Motta Alejandra Lorena', '60006707': 'Yeimy Velasco',
    '62212713': 'Andres Castaño', '62212735': 'Diana Shirley Quiroga Cubillos',
    '62214358': 'Paula Estefania Cardenas Diaz', '62214530': 'Ana Milena Moyano Beltran',
    '62212720': 'Lenin Karina Triana', '62215253': 'Angie Marcela Carranza Arbelaez',
    '62219343': 'Johan Esteven Bernal Diaz', '62219327': 'Karen Ximena Castañeda Cristancho',
    '62220971': 'Paula Estefania Cardenas Diaz', '62222408': 'Julieth Lorena Pacheco Vargas',
    '62214888': 'Liliana Espitia', '62222738': 'Diana Shirley Quiroga Cubillos',
    '62231004': 'Dayana Ramirez', '62230354': 'Karen Ximena Castañeda Cristancho',
    '62237396': 'Johan Esteven Bernal Diaz', '62237293': 'Douglas Enrique Mora',
    '62243896': 'Maria Alejandra Preciado', '62246490': 'Norberto Alvarez',
    '62252653': 'Hasbleidy Vanessa Rodriguez Beltran', '62256597': 'Wilson Arley Perez',
    '62259813': 'Ramiro Augusto Chavez', '80024790': 'Heidy Maiyeth Alvarez',
    '62256596': 'Alexander Parga', '62261836': 'Sandra Milena Pinzon',
    '62261839': 'Andrea Gissette Turizo', '62266296': 'Nicol Estefani Porras',
    '62273220': 'Erika Daniela Amaya Varela', '62274136': 'Yuri Viviana Torres Garcia',
    '62274134': 'Yeraldin Iveth Correa Mateus', '62278611': 'Cesar Augusto Pinzon Calderon',
    '62277236': 'Cristian Alexander Rodriguez Contreras', '62274138': 'Angie Lureidy Avila Rodriguez',
    '62287385': 'Luisa Fernanda Ardila Parra', '62293397': 'Jenny Andrea Ramirez',
    '62295420': 'Ana Maria Moreno Chavez', '62295400': 'Nelson Javier Borrego Hernandez',
    '62295415': 'Diana Marcela Castro Cardenas', '62295417': 'Ruben Dario Villamizar Rojas',
    '62295374': 'Diana Caterin Rojas Rivera'
}

TABLA_SUB_TIPO_FSE = {
    '200': {'sub_tipo': 'Inca. Enfermedad  General', 'fse': 'No Aplica'},
    '230': {'sub_tipo': 'Prorroga Inca/Enfer Gene', 'fse': 'Si Aplica'},
    '383': {'sub_tipo': 'Incapa.fuera de turno', 'fse': 'No Aplica'},
    '215': {'sub_tipo': 'Inc. Accidente de Trabajo', 'fse': 'No Aplica'},
    '202': {'sub_tipo': 'Enf Gral SOAT', 'fse': 'No Aplica'},
    '232': {'sub_tipo': 'Prorroga Enf Gral SOAT', 'fse': 'Si Aplica'},
    '310': {'sub_tipo': 'Licencia Paternidad', 'fse': 'No Aplica'},
    '250': {'sub_tipo': 'Prorroga Inc. Accid. Trab', 'fse': 'Si Aplica'},
    '280': {'sub_tipo': 'Incapacidad gral SENA', 'fse': 'No Aplica'},
    '201': {'sub_tipo': 'Inca. Enfer Gral Integral', 'fse': 'No Aplica'},
    '311': {'sub_tipo': 'Licencia Paternidad Inegr', 'fse': 'No Aplica'},
    '300': {'sub_tipo': 'Licencia Maternidad', 'fse': 'No Aplica'},
    '188': {'sub_tipo': 'Incap  mayor 180 dias', 'fse': 'No Aplica'},
    '235': {'sub_tipo': 'Incap  mayor 540 dias', 'fse': 'No Aplica'},
    '305': {'sub_tipo': 'Lic Mater Interrumpida', 'fse': 'No Aplica'},
    '302': {'sub_tipo': 'Licencia Mater especial', 'fse': 'No Aplica'},
    '203': {'sub_tipo': 'Enf Gral Int SOAT', 'fse': 'No Aplica'},
    '210': {'sub_tipo': 'Inc. Enfer. General Hospi', 'fse': 'No Aplica'},
    '231': {'sub_tipo': 'Prorr Inc/Enf Gral ntegra', 'fse': 'Si Aplica'},
    '281': {'sub_tipo': 'Incapacidad ARL SENA', 'fse': 'No Aplica'},
    '301': {'sub_tipo': 'Licencia Maternidad Integ', 'fse': 'No Aplica'}
}

COLUMNAS_REQUERIDAS = [
    'ID personal', 'Nombre completo', 'Cod Función (externalCode)', 'Cod Función (Label)',
    'Tipo de Documento de Identidad', 'Número de Documento de Identidad',
    'Estado de empleado (Picklist Label)', 'externalCode', 'externalName (Label)',
    'startDate', 'endDate', 'quantityInDays', 'Calendar Days',
    'Descripción General (External Code)', 'Descripción General (Picklist Label)',
    'Fecha de inicio de ausentismo', 'Agregador global de ausencias (Picklist Label)',
    'lastModifiedBy', 'Last Approval Status Date', 'HR Personnel Subarea',
    'HR Personnel Subarea Name', 'approvalStatus'
]

MAPEO_COLUMNAS = {
    'ID personal': 'id_personal', 'Nombre completo': 'nombre_completo',
    'Cod Función (externalCode)': 'cod_funcion_external_code',
    'Cod Función (Label)': 'cod_funcion_label',
    'Tipo de Documento de Identidad': 'tipo_documento_identidad',
    'Número de Documento de Identidad': 'numero_documento_identidad',
    'Estado de empleado (Picklist Label)': 'estado_empleado_picklist_label',
    'externalCode': 'external_code', 'externalName (Label)': 'external_name_label',
    'startDate': 'start_date', 'endDate': 'end_date',
    'quantityInDays': 'quantity_in_days', 'Calendar Days': 'calendar_days',
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
    'llave': 'llave', 'nombre_validador': 'nombre_validador',
    'Sub_tipo': 'sub_tipo', 'FSE': 'fse'
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def limpiar_fecha_para_llave(fecha_str):
    """Limpia fechas para crear la llave - solo números"""
    if pd.isna(fecha_str) or fecha_str == '' or str(fecha_str).lower() in ['nan', 'none', 'nat']:
        return ''
    return ''.join(c for c in str(fecha_str) if c.isdigit())

def convertir_df_a_excel(df):
    """Convierte DataFrame a Excel en memoria"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def convertir_df_a_csv(df):
    """Convierte DataFrame a CSV en memoria"""
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

# ============================================================================
# PASO 1: PROCESAMIENTO INICIAL
# ============================================================================

def paso1_procesamiento_inicial():
    st.title("📊 Paso 1: Procesamiento de Archivo de Ausentismos")
    st.markdown("---")
    
    st.info("📁 Sube el archivo CSV de ausentismos (AusentismoCOL-ApprovedPayrollIndicarfecha-Componente1.csv)")
    
    archivo_csv = st.file_uploader("Selecciona el archivo CSV", type=['csv'], key="archivo_paso1")
    
    if archivo_csv:
        try:
            with st.spinner('🔄 Procesando archivo...'):
                # Leer CSV
                df = pd.read_csv(archivo_csv, skiprows=2, encoding='utf-8', dtype=str)
                
                st.success(f"✅ Archivo leído: {df.shape[0]:,} registros, {df.shape[1]} columnas")
                
                # Verificar columnas
                columnas_encontradas = [col for col in COLUMNAS_REQUERIDAS if col in df.columns]
                
                if len(columnas_encontradas) < len(COLUMNAS_REQUERIDAS):
                    st.warning(f"⚠️ Encontradas {len(columnas_encontradas)}/{len(COLUMNAS_REQUERIDAS)} columnas")
                
                # Extraer columnas específicas
                df_especifico = df[columnas_encontradas].copy()
                
                # HOMOLOGACIÓN
                st.write("### 🔄 Aplicando Homologación SSF vs SAP...")
                df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'] = \
                    df_especifico['externalCode'].map(TABLA_HOMOLOGACION)
                
                valores_encontrados = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].notna().sum()
                st.write(f"✅ Homologación aplicada: {valores_encontrados:,}/{len(df_especifico):,} códigos")
                
                # NOMBRE VALIDADOR
                st.write("### 👤 Mapeando Validadores...")
                df_especifico['lastModifiedBy_limpio'] = df_especifico['lastModifiedBy'].astype(str).str.strip()
                df_especifico['nombre_validador'] = df_especifico['lastModifiedBy_limpio'].map(TABLA_VALIDADORES)\
                    .fillna('ALERTA VALIDADOR NO ENCONTRADO')
                
                validadores_ok = (df_especifico['nombre_validador'] != 'ALERTA VALIDADOR NO ENCONTRADO').sum()
                st.write(f"✅ Validadores identificados: {validadores_ok:,}/{len(df_especifico):,}")
                
                df_especifico = df_especifico.drop(['lastModifiedBy_limpio'], axis=1)
                
                # SUB_TIPO Y FSE
                st.write("### 📋 Creando Sub_tipo y FSE...")
                df_especifico['Sub_tipo'] = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                    lambda x: TABLA_SUB_TIPO_FSE.get(str(x), {}).get('sub_tipo', 'ALERTA SUB_TIPO NO ENCONTRADO') 
                    if pd.notna(x) else 'ALERTA SUB_TIPO NO ENCONTRADO'
                )
                
                df_especifico['FSE'] = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                    lambda x: TABLA_SUB_TIPO_FSE.get(str(x), {}).get('fse', 'No Aplica') 
                    if pd.notna(x) else 'No Aplica'
                )
                
                sub_tipo_ok = (df_especifico['Sub_tipo'] != 'ALERTA SUB_TIPO NO ENCONTRADO').sum()
                st.write(f"✅ Sub_tipos asignados: {sub_tipo_ok:,}/{len(df_especifico):,}")
                
                # LLAVE
                st.write("### 🔑 Creando columna LLAVE...")
                df_especifico['startDate_limpia'] = df_especifico['startDate'].apply(limpiar_fecha_para_llave)
                df_especifico['endDate_limpia'] = df_especifico['endDate'].apply(limpiar_fecha_para_llave)
                
                df_especifico['llave'] = (
                    df_especifico['ID personal'].astype(str).fillna('') +
                    df_especifico['startDate_limpia'] +
                    df_especifico['endDate_limpia'] +
                    df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].astype(str).fillna('')
                )
                
                df_especifico = df_especifico.drop(['startDate_limpia', 'endDate_limpia'], axis=1)
                
                duplicados = df_especifico['llave'].duplicated().sum()
                if duplicados > 0:
                    st.warning(f"⚠️ Se encontraron {duplicados} llaves duplicadas")
                else:
                    st.success("✅ Todas las llaves son únicas")
                
                # Renombrar columnas
                mapeo_actual = {col: MAPEO_COLUMNAS[col] for col in df_especifico.columns if col in MAPEO_COLUMNAS}
                df_final = df_especifico.rename(columns=mapeo_actual)
                
                # Limpiar datos
                if 'numero_documento_identidad' in df_final.columns:
                    df_final['numero_documento_identidad'] = df_final['numero_documento_identidad'].astype(str).replace('nan', '')
                    df_final['numero_documento_identidad'] = '"' + df_final['numero_documento_identidad'] + '"'
                
                if 'llave' in df_final.columns:
                    df_final['llave'] = 'K' + df_final['llave'].astype(str)
                
                # Guardar en session_state
                st.session_state.df_parte1 = df_final
                
                # Mostrar resumen
                st.markdown("---")
                st.write("### 📊 Resumen del Procesamiento")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Registros", f"{len(df_final):,}")
                with col2:
                    st.metric("Total Columnas", len(df_final.columns))
                with col3:
                    validadores_alertas = (df_final['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
                    st.metric("Alertas Validadores", validadores_alertas)
                
                # Mostrar preview
                st.write("### 👀 Vista Previa (primeras 10 filas)")
                st.dataframe(df_final.head(10), use_container_width=True)
                
                # Botón de descarga
                csv_data = convertir_df_a_csv(df_final)
                st.download_button(
                    label="📥 Descargar CSV Procesado",
                    data=csv_data,
                    file_name="ausentismo_procesado_especifico.csv",
                    mime="text/csv"
                )
                
                # Botón para continuar
                st.markdown("---")
                if st.button("▶️ Continuar al Paso 2", type="primary", use_container_width=True):
                    st.session_state.paso_actual = 2
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")
            st.exception(e)

# ============================================================================
# PASO 2: VALIDACIONES Y MERGE
# ============================================================================

def paso2_validaciones_merge():
    st.title("📊 Paso 2: Validaciones y Merge con Relación Laboral")
    st.markdown("---")
    
    if st.session_state.df_parte1 is None:
        st.warning("⚠️ Debes completar el Paso 1 primero")
        if st.button("⬅️ Volver al Paso 1"):
            st.session_state.paso_actual = 1
            st.rerun()
        return
    
    st.success(f"✅ Datos del Paso 1 cargados: {len(st.session_state.df_parte1):,} registros")
    
    st.info("📁 Sube el archivo Excel de personal (MD_26082025.XLSX)")
    
    archivo_excel = st.file_uploader("Selecciona el archivo Excel de personal", type=['xlsx', 'xls'], key="archivo_paso2")
    
    if archivo_excel:
        try:
            with st.spinner('🔄 Procesando merge...'):
                # Leer archivo de personal
                df_personal = pd.read_excel(archivo_excel)
                st.success(f"✅ Archivo de personal leído: {len(df_personal):,} registros")
                
                # Buscar columna de personal
                col_num_pers = None
                for col in df_personal.columns:
                    if 'pers' in col.lower() or 'personal' in col.lower():
                        col_num_pers = col
                        break
                
                # Buscar columna de relación laboral
                col_relacion = None
                for col in df_personal.columns:
                    if 'relaci' in col.lower() and 'labor' in col.lower():
                        col_relacion = col
                        break
                
                if col_num_pers is None or col_relacion is None:
                    st.error("❌ No se encontraron las columnas necesarias en el Excel")
                    st.write("Columnas disponibles:", df_personal.columns.tolist())
                    return
                
                st.write(f"✅ Columna Personal: **{col_num_pers}**")
                st.write(f"✅ Columna Relación Laboral: **{col_relacion}**")
                
                # Preparar merge
                df_ausentismo = st.session_state.df_parte1.copy()
                df_ausentismo['id_personal'] = df_ausentismo['id_personal'].astype(str).str.strip()
                df_personal[col_num_pers] = df_personal[col_num_pers].astype(str).str.strip()
                
                df_personal_reducido = df_personal[[col_num_pers, col_relacion]].copy()
                
                # Realizar merge
                df_resultado = df_ausentismo.merge(
                    df_personal_reducido,
                    left_on='id_personal',
                    right_on=col_num_pers,
                    how='left'
                )
                
                if col_relacion != 'Relación laboral':
                    df_resultado.rename(columns={col_relacion: 'Relación laboral'}, inplace=True)
                
                if col_num_pers in df_resultado.columns and col_num_pers != 'id_personal':
                    df_resultado.drop(columns=[col_num_pers], inplace=True)
                
                con_relacion = df_resultado['Relación laboral'].notna().sum()
                sin_relacion = df_resultado['Relación laboral'].isna().sum()
                
                st.write("### 📊 Resultados del Merge")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Registros", f"{len(df_resultado):,}")
                with col2:
                    st.metric("Con Relación Laboral", f"{con_relacion:,}")
                with col3:
                    st.metric("Sin Relación Laboral", f"{sin_relacion:,}")
                
                # Eliminar registros sin relación laboral
                df_resultado = df_resultado[df_resultado['Relación laboral'].notna()]
                st.info(f"ℹ️ Registros finales (solo con relación laboral): {len(df_resultado):,}")
                
                # VALIDACIONES SENA Y LEY 50
                st.markdown("---")
                st.write("## 🔍 Validaciones SENA y Ley 50")
                
                # Validación SENA
                st.write("### 🎓 Validación SENA")
                df_aprendizaje = df_resultado[df_resultado['Relación laboral'].str.contains('Aprendizaje', case=False, na=False)].copy()
                st.write(f"📊 Registros con Aprendizaje: {len(df_aprendizaje):,}")
                
                conceptos_validos_sena = [
                    'Incapacidad gral SENA',
                    'Licencia de Maternidad SENA',
                    'Suspensión contrato SENA'
                ]
                
                df_errores_sena = df_aprendizaje[~df_aprendizaje['external_name_label'].isin(conceptos_validos_sena)].copy()
                st.write(f"❌ Errores encontrados: {len(df_errores_sena):,}")
                
                if len(df_errores_sena) > 0:
                    st.dataframe(df_errores_sena[['id_personal', 'nombre_completo', 'Relación laboral', 'external_name_label']].head(10))
                    excel_sena = convertir_df_a_excel(df_errores_sena)
                    st.download_button(
                        "📥 Descargar Errores SENA (Excel)",
                        data=excel_sena,
                        file_name="Sena_error_validar.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # Validación LEY 50
                st.write("### 📜 Validación Ley 50")
                df_ley50 = df_resultado[df_resultado['Relación laboral'].str.contains('Ley 50', case=False, na=False)].copy()
                st.write(f"📊 Registros con Ley 50: {len(df_ley50):,}")
                
                conceptos_prohibidos_ley50 = [
                    'Incapacidad gral SENA',
                    'Licencia de Maternidad SENA',
                    'Suspensión contrato SENA',
                    'Inca. Enfer Gral Integral',
                    'Prorr Inc/Enf Gral ntegra'
                ]
                
                df_errores_ley50 = df_ley50[df_ley50['external_name_label'].isin(conceptos_prohibidos_ley50)].copy()
                st.write(f"❌ Errores encontrados: {len(df_errores_ley50):,}")
                
                if len(df_errores_ley50) > 0:
                    st.dataframe(df_errores_ley50[['id_personal', 'nombre_completo', 'Relación laboral', 'external_name_label']].head(10))
                    excel_ley50 = convertir_df_a_excel(df_errores_ley50)
                    st.download_button(
                        "📥 Descargar Errores Ley 50 (Excel)",
                        data=excel_ley50,
                        file_name="Ley_50_error_validar.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # CREAR COLUMNAS DE VALIDACIÓN
                st.markdown("---")
                st.write("## ✅ Creando Columnas de Validación")
                
                # 1. licencia_paternidad
                df_resultado['licencia_paternidad'] = df_resultado.apply(
                    lambda row: "Concepto Si Aplica" 
                    if row['external_name_label'] == "Licencia Paternidad" and row['calendar_days'] == '14' 
                    else "Concepto No Aplica",
                    axis=1
                )
                
                # 2. licencia_maternidad
                df_resultado['licencia_maternidad'] = df_resultado.apply(
                    lambda row: "Concepto Si Aplica" 
                    if row['external_name_label'] == "Licencia Maternidad" and row['calendar_days'] == '126' 
                    else "Concepto No Aplica",
                    axis=1
                )
                
                # 3. ley_de_luto
                df_resultado['ley_de_luto'] = df_resultado.apply(
                    lambda row: "Concepto Si Aplica" 
                    if row['external_name_label'] == "Ley de luto" and row['quantity_in_days'] == '5' 
                    else "Concepto No Aplica",
                    axis=1
                )
                
                # 4. incap_fuera_de_turno
                df_resultado['incap_fuera_de_turno'] = df_resultado.apply(
                    lambda row: "Concepto Si Aplica" 
                    if row['external_name_label'] == "Incapa.fuera de turno" and pd.to_numeric(row['calendar_days'], errors='coerce') <= 1 
                    else "Concepto No Aplica",
                    axis=1
                )
                
                # 5. lic_maternidad_sena
                df_resultado['lic_maternidad_sena'] = df_resultado.apply(
                    lambda row: "Concepto Si Aplica" 
                    if row['external_name_label'] == "Licencia de Maternidad SENA" and row['calendar_days'] == '126' 
                    else "Concepto No Aplica",
                    axis=1
                )
                
                # 6. lic_jurado_votacion
                df_resultado['lic_jurado_votacion'] = df_resultado.apply(
                    lambda row: "Concepto Si Aplica" 
                    if row['external_name_label'] == "Lic Jurado Votación" and pd.to_numeric(row['calendar_days'], errors='coerce') <= 1 
                    else "Concepto No Aplica",
                    axis=1
                )
                
                st.success("✅ 6 columnas de validación creadas exitosamente")
                
                # Guardar resultado
                st.session_state.df_parte2 = df_resultado
                
                # Mostrar resumen
                st.write("### 📊 Resumen de Columnas de Validación")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Licencia Paternidad:**")
                    st.write(f"✅ Si Aplica: {(df_resultado['licencia_paternidad'] == 'Concepto Si Aplica').sum()}")
                    st.write(f"❌ No Aplica: {(df_resultado['licencia_paternidad'] == 'Concepto No Aplica').sum()}")
                
                with col2:
                    st.write("**Licencia Maternidad:**")
                    st.write(f"✅ Si Aplica: {(df_resultado['licencia_maternidad'] == 'Concepto Si Aplica').sum()}")
                    st.write(f"❌ No Aplica: {(df_resultado['licencia_maternidad'] == 'Concepto No Aplica').sum()}")
                
                # Generar alertas
                st.markdown("---")
                st.write("## 🚨 Generando Archivos de Alertas")
                
                alertas_generadas = []
                
                # Alerta 1: licencia_paternidad
                df_alert_paternidad = df_resultado[(df_resultado['licencia_paternidad'] == 'Concepto No Aplica') & 
                                                   (df_resultado['external_name_label'] == 'Licencia Paternidad')].copy()
                if len(df_alert_paternidad) > 0:
                    alertas_generadas.append(('alerta_licencia_paternidad.xlsx', df_alert_paternidad, len(df_alert_paternidad)))
                
                # Alerta 2: licencia_maternidad
                df_alert_maternidad = df_resultado[(df_resultado['licencia_maternidad'] == 'Concepto No Aplica') & 
                                                   (df_resultado['external_name_label'] == 'Licencia Maternidad')].copy()
                if len(df_alert_maternidad) > 0:
                    alertas_generadas.append(('alerta_licencia_maternidad.xlsx', df_alert_maternidad, len(df_alert_maternidad)))
                
                # Alerta 3: ley_de_luto
                df_alert_luto = df_resultado[(df_resultado['ley_de_luto'] == 'Concepto No Aplica') & 
                                             (df_resultado['external_name_label'] == 'Ley de luto')].copy()
                if len(df_alert_luto) > 0:
                    alertas_generadas.append(('alerta_ley_de_luto.xlsx', df_alert_luto, len(df_alert_luto)))
                
                # Alerta 4: incap_fuera_de_turno
                df_alert_incap = df_resultado[(df_resultado['incap_fuera_de_turno'] == 'Concepto No Aplica') & 
                                              (df_resultado['external_name_label'] == 'Incapa.fuera de turno')].copy()
                if len(df_alert_incap) > 0:
                    alertas_generadas.append(('alerta_incap_fuera_de_turno.xlsx', df_alert_incap, len(df_alert_incap)))
                
                # Alerta 5: lic_maternidad_sena
                df_alert_mat_sena = df_resultado[(df_resultado['lic_maternidad_sena'] == 'Concepto No Aplica') & 
                                                 (df_resultado['external_name_label'] == 'Licencia de Maternidad SENA')].copy()
                if len(df_alert_mat_sena) > 0:
                    alertas_generadas.append(('alerta_lic_maternidad_sena.xlsx', df_alert_mat_sena, len(df_alert_mat_sena)))
                
                # Alerta 6: lic_jurado_votacion
                df_alert_jurado = df_resultado[(df_resultado['lic_jurado_votacion'] == 'Concepto No Aplica') & 
                                               (df_resultado['external_name_label'] == 'Lic Jurado Votación')].copy()
                if len(df_alert_jurado) > 0:
                    alertas_generadas.append(('alerta_lic_jurado_votacion.xlsx', df_alert_jurado, len(df_alert_jurado)))
                
                # Alerta 7: Incapacidades mayores a 30 días
                conceptos_incapacidad = [
                    'Incapacidad enfermedad general', 'Prorroga Inca/Enfer Gene',
                    'Enf Gral SOAT', 'Inc. Accidente de Trabajo', 'Prorroga Inc. Accid. Trab'
                ]
                df_incap_mayor_30 = df_resultado[
                    (df_resultado['external_name_label'].isin(conceptos_incapacidad)) & 
                    (pd.to_numeric(df_resultado['calendar_days'], errors='coerce') > 30)
                ].copy()
                if len(df_incap_mayor_30) > 0:
                    alertas_generadas.append(('incp_mayor_30_dias.xlsx', df_incap_mayor_30, len(df_incap_mayor_30)))
                
                # Alerta 8: Ausentismos sin pago mayores a 10 días
                conceptos_sin_pago = ['Aus Reg sin Soporte', 'Suspensión']
                df_sin_pago_mayor_10 = df_resultado[
                    (df_resultado['external_name_label'].isin(conceptos_sin_pago)) & 
                    (pd.to_numeric(df_resultado['calendar_days'], errors='coerce') > 10)
                ].copy()
                if len(df_sin_pago_mayor_10) > 0:
                    alertas_generadas.append(('Validacion_ausentismos_sin_pago_mayor_10_dias.xlsx', df_sin_pago_mayor_10, len(df_sin_pago_mayor_10)))
                
                # Alerta 9: Día de la familia mayor de 1 día
                df_dia_familia = df_resultado[
                    (df_resultado['external_name_label'] == 'Día de la familia') & 
                    (pd.to_numeric(df_resultado['calendar_days'], errors='coerce') > 1)
                ].copy()
                if len(df_dia_familia) > 0:
                    alertas_generadas.append(('dia_de_la_familia.xlsx', df_dia_familia, len(df_dia_familia)))
                
                # Mostrar alertas
                if alertas_generadas:
                    st.write(f"📋 Se generaron **{len(alertas_generadas)}** archivos de alerta:")
                    for nombre, df_alert, cantidad in alertas_generadas:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"• {nombre}")
                        with col2:
                            excel_alert = convertir_df_a_excel(df_alert)
                            st.download_button(
                                f"📥 Descargar ({cantidad})",
                                data=excel_alert,
                                file_name=nombre,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"alert_{nombre}"
                            )
                else:
                    st.success("✅ No se encontraron alertas")
                
                # Descargar archivo con validaciones
                st.markdown("---")
                st.write("### 💾 Descargar Archivo Completo con Validaciones")
                csv_validaciones = convertir_df_a_csv(df_resultado)
                st.download_button(
                    "📥 Descargar CSV Completo con Validaciones",
                    data=csv_validaciones,
                    file_name="relacion_laboral_con_validaciones.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
                
                # Vista previa
                st.write("### 👀 Vista Previa del Resultado")
                st.dataframe(df_resultado.head(10), use_container_width=True)
                
                # Botón para continuar
                st.markdown("---")
                if st.button("▶️ Continuar al Paso 3 (Opcional)", type="primary", use_container_width=True):
                    st.session_state.paso_actual = 3
                    st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error en el procesamiento: {str(e)}")
            st.exception(e)

# ============================================================================
# PASO 3: MERGE ADICIONAL CON REPORTE 45 (OPCIONAL)
# ============================================================================

def paso3_merge_adicional():
    st.title("📊 Paso 3: Merge con Reporte 45 (Opcional)")
    st.markdown("---")
    
    if st.session_state.df_parte2 is None:
        st.warning("⚠️ Debes completar el Paso 2 primero")
        if st.button("⬅️ Volver al Paso 2"):
            st.session_state.paso_actual = 2
            st.rerun()
        return
    
    st.success(f"✅ Datos del Paso 2 cargados: {len(st.session_state.df_parte2):,} registros")
    
    st.info("""
    📁 Este paso es **OPCIONAL**. Si tienes el archivo Reporte 45 de ausentismo, 
    puedes hacer un merge adicional para agregar la columna 'Descripc.enfermedad'.
    
    Si no lo tienes, puedes **Finalizar el Proceso** directamente.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⏭️ Omitir este paso y Finalizar", use_container_width=True):
            st.session_state.paso_actual = 4
            st.rerun()
    
    with col2:
        st.write("")  # Espacio
    
    st.markdown("---")
    st.write("### 📤 O sube el archivo Reporte 45 para hacer el merge:")
    
    archivo_reporte45 = st.file_uploader(
        "Selecciona el archivo Reporte 45 (Excel)", 
        type=['xlsx', 'xls'], 
        key="archivo_paso3"
    )
    
    if archivo_reporte45:
        try:
            with st.spinner('🔄 Procesando merge con Reporte 45...'):
                # Leer Excel
                df_excel = pd.read_excel(archivo_reporte45)
                st.success(f"✅ Reporte 45 leído: {len(df_excel):,} registros")
                
                # Filtrar por valores específicos
                valores_filtro = [
                    'Enf Gral SOAT', 'Inc. Accidente de Trabajo',
                    'Inca. Enfer Gral Integral', 'Inca. Enfermedad  General',
                    'Prorroga Enf Gral SOAT', 'Prorroga Inc. Accid. Trab',
                    'Prorroga Inca/Enfer Gene', 'Incapa.fuera de turno'
                ]
                
                if 'Txt.cl.pres./ab.' in df_excel.columns:
                    df_excel_filtrado = df_excel[df_excel['Txt.cl.pres./ab.'].isin(valores_filtro)].copy()
                    st.write(f"📊 Registros después del filtro: {len(df_excel_filtrado):,}")
                    
                    # Preparar para merge
                    df_csv = st.session_state.df_parte2.copy()
                    
                    if 'Número de personal' in df_excel_filtrado.columns:
                        df_excel_filtrado['Número de personal'] = df_excel_filtrado['Número de personal'].astype(str).str.strip()
                        df_csv['id_personal'] = df_csv['id_personal'].astype(str).str.strip()
                        
                        # Opción 1: Merge simple por ID
                        st.write("### 🔀 Tipo de Merge")
                        tipo_merge = st.radio(
                            "Selecciona el tipo de merge:",
                            ["Merge Simple (solo por ID personal)", 
                             "Merge Completo (ID + fechas de inicio y fin)"],
                            key="tipo_merge"
                        )
                        
                        if tipo_merge == "Merge Simple (solo por ID personal)":
                            # Merge simple
                            if 'Descripc.enfermedad' in df_excel_filtrado.columns:
                                df_merged = pd.merge(
                                    df_csv,
                                    df_excel_filtrado[['Número de personal', 'Descripc.enfermedad']],
                                    left_on='id_personal',
                                    right_on='Número de personal',
                                    how='left'
                                )
                                
                                if 'Número de personal' in df_merged.columns:
                                    df_merged = df_merged.drop(columns=['Número de personal'])
                                
                                df_merged = df_merged.dropna(how='all')
                                
                                st.success(f"✅ Merge completado: {len(df_merged):,} registros")
                                
                                # Mostrar estadísticas
                                con_descripcion = df_merged['Descripc.enfermedad'].notna().sum()
                                sin_descripcion = df_merged['Descripc.enfermedad'].isna().sum()
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total", f"{len(df_merged):,}")
                                with col2:
                                    st.metric("Con Descripción", f"{con_descripcion:,}")
                                with col3:
                                    st.metric("Sin Descripción", f"{sin_descripcion:,}")
                                
                                # Guardar resultado
                                st.session_state.df_parte2 = df_merged
                                
                                # Descargar
                                csv_merged = convertir_df_a_csv(df_merged)
                                st.download_button(
                                    "📥 Descargar Merge Simple",
                                    data=csv_merged,
                                    file_name="merge_ausentismos_filtrado.csv",
                                    mime="text/csv",
                                    type="primary",
                                    use_container_width=True
                                )
                                
                                # Vista previa
                                st.write("### 👀 Vista Previa")
                                st.dataframe(df_merged[['id_personal', 'nombre_completo', 'external_name_label', 'Descripc.enfermedad']].head(10))
                            
                        else:
                            # Merge completo con fechas
                            if all(col in df_excel_filtrado.columns for col in ['Inicio de validez', 'Fin de validez', 'Descripc.enfermedad']):
                                # Convertir fechas
                                df_excel_filtrado['Inicio de validez'] = pd.to_datetime(df_excel_filtrado['Inicio de validez'], errors='coerce')
                                df_excel_filtrado['Fin de validez'] = pd.to_datetime(df_excel_filtrado['Fin de validez'], errors='coerce')
                                df_csv['start_date'] = pd.to_datetime(df_csv['start_date'], errors='coerce')
                                df_csv['end_date'] = pd.to_datetime(df_csv['end_date'], errors='coerce')
                                
                                # Merge con 3 columnas
                                df_merged = pd.merge(
                                    df_csv,
                                    df_excel_filtrado,
                                    left_on=['id_personal', 'start_date', 'end_date'],
                                    right_on=['Número de personal', 'Inicio de validez', 'Fin de validez'],
                                    how='inner'
                                )
                                
                                # Limpiar columnas duplicadas
                                columnas_duplicadas = ['Número de personal', 'Inicio de validez', 'Fin de validez']
                                for col in columnas_duplicadas:
                                    if col in df_merged.columns:
                                        df_merged = df_merged.drop(columns=[col])
                                
                                st.success(f"✅ Super Merge completado: {len(df_merged):,} registros con match exacto")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Registros CSV", f"{len(df_csv):,}")
                                with col2:
                                    st.metric("Registros Excel", f"{len(df_excel_filtrado):,}")
                                with col3:
                                    st.metric("Matches", f"{len(df_merged):,}")
                                
                                # Guardar resultado
                                st.session_state.df_parte2 = df_merged
                                
                                # Descargar
                                csv_super_merged = convertir_df_a_csv(df_merged)
                                st.download_button(
                                    "📥 Descargar Super Merge",
                                    data=csv_super_merged,
                                    file_name="super_merge_ausentismos.csv",
                                    mime="text/csv",
                                    type="primary",
                                    use_container_width=True
                                )
                                
                                # Vista previa
                                st.write("### 👀 Vista Previa")
                                st.dataframe(df_merged.head(10), use_container_width=True)
                            else:
                                st.error("❌ No se encontraron las columnas de fecha necesarias")
                    else:
                        st.error("❌ No se encontró la columna 'Número de personal'")
                else:
                    st.error("❌ No se encontró la columna 'Txt.cl.pres./ab.'")
                
                # Botón para finalizar
                st.markdown("---")
                if st.button("✅ Finalizar Proceso", type="primary", use_container_width=True):
                    st.session_state.paso_actual = 4
                    st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error en el merge: {str(e)}")
            st.exception(e)

# ============================================================================
# PASO 4: RESUMEN FINAL
# ============================================================================

def paso4_resumen_final():
    st.title("🎉 Proceso Completado")
    st.markdown("---")
    
    st.success("✅ Todos los pasos han sido completados exitosamente")
    
    st.write("### 📊 Resumen del Proceso")
    
    if st.session_state.df_parte1 is not None:
        st.write(f"✅ **Paso 1:** Procesados {len(st.session_state.df_parte1):,} registros")
    
    if st.session_state.df_parte2 is not None:
        st.write(f"✅ **Paso 2:** Generado archivo con {len(st.session_state.df_parte2):,} registros y validaciones")
    
    st.markdown("---")
    st.write("### 💾 Descarga Final")
    
    if st.session_state.df_parte2 is not None:
        csv_final = convertir_df_a_csv(st.session_state.df_parte2)
        st.download_button(
            "📥 Descargar Archivo Final Completo (CSV)",
            data=csv_final,
            file_name="auditoria_ausentismos_final.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
        
        excel_final = convertir_df_a_excel(st.session_state.df_parte2)
        st.download_button(
            "📥 Descargar Archivo Final Completo (Excel)",
            data=excel_final,
            file_name="auditoria_ausentismos_final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.markdown("---")
    
    if st.button("🔄 Comenzar Nuevo Proceso", use_container_width=True):
        # Limpiar session state
        st.session_state.paso_actual = 1
        st.session_state.df_parte1 = None
        st.session_state.df_parte2 = None
        st.session_state.archivos_generados = {}
        st.rerun()

# ============================================================================
# NAVEGACIÓN PRINCIPAL
# ============================================================================

def main():
    # Sidebar con navegación
    with st.sidebar:
        st.title("🧭 Navegación")
        st.markdown("---")
        
        # Indicadores de progreso
        pasos = [
            ("1️⃣", "Procesamiento Inicial", 1),
            ("2️⃣", "Validaciones y Merge", 2),
            ("3️⃣", "Merge Adicional (Opcional)", 3),
            ("4️⃣", "Resumen Final", 4)
        ]
        
        for emoji, nombre, numero in pasos:
            if st.session_state.paso_actual == numero:
                st.markdown(f"**{emoji} {nombre}** ◀️")
            else:
                if st.button(f"{emoji} {nombre}", key=f"nav_{numero}", use_container_width=True):
                    # Solo permitir navegar a pasos completados o el siguiente
                    if numero == 1 or \
                       (numero == 2 and st.session_state.df_parte1 is not None) or \
                       (numero == 3 and st.session_state.df_parte2 is not None) or \
                       (numero == 4 and st.session_state.df_parte2 is not None):
                        st.session_state.paso_actual = numero
                        st.rerun()
        
        st.markdown("---")
        st.info("""
        **ℹ️ Instrucciones:**
        1. Procesa el CSV de ausentismos
        2. Agrega relación laboral (Excel)
        3. (Opcional) Merge con Reporte 45
        4. Descarga resultados
        """)
    
    # Renderizar paso actual
    if st.session_state.paso_actual == 1:
        paso1_procesamiento_inicial()
    elif st.session_state.paso_actual == 2:
        paso2_validaciones_merge()
    elif st.session_state.paso_actual == 3:
        paso3_merge_adicional()
    elif st.session_state.paso_actual == 4:
        paso4_resumen_final()

if __name__ == "__main__":
    main()
