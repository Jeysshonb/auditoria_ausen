# Auditoría Ausentismos - Versión Completa con CONCAT y Validaciones Mejoradas
import pandas as pd
import os

# ============================================================================
# RUTAS DE ARCHIVOS
# ============================================================================
ruta_entrada_csv = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_planos\AusentismoCOL-ApprovedPayrollIndicarfecha-Componente1.csv"
ruta_entrada_excel = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_planos\Reporte 45_012025_082025_26082025.XLSX"
directorio_salida = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida"
archivo_salida = "ausentismo_procesado_completo_v2.csv"
ruta_completa_salida = os.path.join(directorio_salida, archivo_salida)

# ============================================================================
# COLUMNAS REQUERIDAS DEL CSV
# ============================================================================
columnas_csv = [
    'ID personal',
    'Nombre completo',
    'Cod Función (externalCode)',
    'Cod Función (Label)',
    'Tipo de Documento de Identidad',
    'Número de Documento de Identidad',
    'Estado de empleado (Picklist Label)',
    'externalCode',
    'externalName (Label)',
    'startDate',
    'endDate',
    'quantityInDays',
    'Calendar Days',
    'Descripción General (External Code)',
    'Descripción General (Picklist Label)',
    'Fecha de inicio de ausentismo',
    'Agregador global de ausencias (Picklist Label)',
    'lastModifiedBy',
    'Last Approval Status Date',
    'HR Personnel Subarea',
    'HR Personnel Subarea Name',
    'approvalStatus'
]

# ============================================================================
# TABLA DE HOMOLOGACIÓN SSF vs SAP (MAPEO DIRECTO)
# ============================================================================
tabla_homologacion = {
    'CO_vacatio': '100',
    'CO_SICK180': '188',
    'CO_EXPSUSP': '189',
    'CO_PAID': '190',
    'CO_UNPAID': '191',
    'CO_CTR_SEN': '198',
    'CO_SICK': '200',
    'CO_SICKINT': '201',
    'CO_SICKSOA': '202',
    'CO_PR_QRT': '204',
    'CO_FAMILY': '205',
    'CO_WORKACC': '215',
    'CO_ILL': '230',
    'CO_ILL_EXT': '231',
    'CO_ILLSEXT': '232',
    'CO_SICK540': '235',
    'CO_WRKACXT': '250',
    'CO_SICKSEN': '280',
    'CO_MAT': '300',
    'CO_MAT_SPE': '302',
    'CO_MAT_ITR': '305',
    'CO_PAT': '310',
    'CO_PAT_INT': '311',
    'CO_DOM_CAL': '330',
    'CO_MOURN': '340',
    'CO_UNJ': '380',
    'CO_SUS': '381',
    'CO_SHFT_SK': '383',
    'CO_REG_WOS': '397',
    'CO_MAT_INT': '301',
    'CO_SICKARL': '187',
    'CO_UNJ_INT': '197',
    'CO_SCIT_SO': '203',
    'CO_MOURN_I': '341',
    'CO_WKACSEN': '281',
    'CO_MAT_SEN': '398',
    'CO_WRKACIT': '216',
    'CO_INT_SUS': '195',
    'CO_NONWORK': '192',
    'CO_DELICAT': '206',
    'CO_PR_QRTI': '334',
    'CO_ILLSEIN': '233',
    'CO_DM_CALI': '331',
    'CO_VOTING': '345',
    'CO_INT_UNP': '196',
    'CO_FAM_FDS': '205',
    'CO_VacationsFDS': '100',
    'Aus.Sin Soporte Rech Docs': '399'
    

}

# TABLA INVERSA: De código SAP (205) a código SSF (CO_FAMILY)
tabla_homologacion_inversa = {v: k for k, v in tabla_homologacion.items()}

# ============================================================================
# TABLA DE VALIDADORES ACTUALIZADA (CON AMBAS COLUMNAS)
# Incluye mapeo INVERSO por nombre de usuario también
# ============================================================================
tabla_validadores = {
    '80002749': {'nombre': 'Diana Paola Martinez Diaz', 'usuario': 'DMARTINEZ'},
    '62208433': {'nombre': 'Nini Johanna Neira', 'usuario': 'NNEIRA'},
    '62208420': {'nombre': 'Maria Lorena Ospina', 'usuario': 'MOSPINA'},
    '62208383': {'nombre': 'Juan Sebastian Sanabria Cabezas', 'usuario': 'JSSANABRIA'},
    '62208367': {'nombre': 'Yeimy Velasco', 'usuario': 'YEIVELASCO'},
    '60005132': {'nombre': 'Angie Paola Muñoz', 'usuario': 'ADE-AMUNOZ'},
    '80025780': {'nombre': 'Buitrago Baron Deisy Marley', 'usuario': 'DMBUITRAGO'},
    '80005980': {'nombre': 'Caro Salamanca Wilson Alfredo', 'usuario': 'WCARO'},
    '80003719': {'nombre': 'Carreño Diaz Natalia Andrea', 'usuario': 'NCARRENO'},
    '60005117': {'nombre': 'Daniela Maria Herrera', 'usuario': 'ADE-DMHERRER'},
    '80022209': {'nombre': 'Guerra Cabrera Carolina', 'usuario': 'CGUERRA'},
    '80025779': {'nombre': 'Huerfano Davila Edgar Andres', 'usuario': 'EHUERFANO'},
    '60005052': {'nombre': 'Jose Esteban Vargas', 'usuario': 'ADE-JVARGAS'},
    '60006940': {'nombre': 'Juan Esteban Sanabria', 'usuario': 'ADE-JSANABRI'},
    '60005371': {'nombre': 'Lenin Karina Triana', 'usuario': 'ADE-KTRIANA'},
    '60005046': {'nombre': 'Luis Armando Chacon', 'usuario': 'ADE-ACHACON'},
    '60005129': {'nombre': 'Luz Liliana Rodriguez', 'usuario': 'ADE-LRODRIGU'},
    '60006593': {'nombre': 'Luz Liliana Rodriguez', 'usuario': 'LULRODRIGUEZ'},
    '60006112': {'nombre': 'Mancera Reinosa Diana Maria', 'usuario': 'DMANCERA'},
    '60006909': {'nombre': 'Maria Jose Alfonso', 'usuario': 'ADE-MALFONSO'},
    '60005057': {'nombre': 'Maria Lorena Ospina', 'usuario': 'ADE-LOSPINA'},
    '80000523': {'nombre': 'Rodriguez Gutierrez Paula Marcela', 'usuario': 'PRODRIGUEZ'},
    '80025781': {'nombre': 'Yaima Motta Alejandra Lorena', 'usuario': 'AYAIMA'},
    '60006707': {'nombre': 'Yeimy Velasco', 'usuario': 'ADE-YVELASCO'},
    '62212713': {'nombre': 'Andres Castaño', 'usuario': 'ACASTANO'},
    '62212735': {'nombre': 'Diana Shirley Quiroga Cubillos', 'usuario': 'ADE-DQUIROGA'},
    '62214358': {'nombre': 'Paula Estefania Cardenas Diaz', 'usuario': 'ADE-PCARDENA'},
    '62214530': {'nombre': 'Ana Milena Moyano Beltran', 'usuario': 'AMOYANO'},
    '62212720': {'nombre': 'Lenin Karina Triana', 'usuario': 'LKTRIANA'},
    '62215253': {'nombre': 'Angie Marcela Carranza Arbelaez', 'usuario': 'AMCARRANZA'},
    '62219343': {'nombre': 'Johan Esteven Bernal Diaz', 'usuario': 'ADE-JBERNAL'},
    '62219327': {'nombre': 'Karen Ximena Castañeda Cristancho', 'usuario': 'KXCASTANEDA'},
    '62220971': {'nombre': 'Paula Estefania Cardenas Diaz', 'usuario': 'PCARDENAS'},
    '62222408': {'nombre': 'Julieth Lorena Pacheco Vargas', 'usuario': 'ADE-JPACHECO'},
    '62214888': {'nombre': 'Liliana Espitia', 'usuario': 'LESPITIA'},
    '62222738': {'nombre': 'Diana Shirley Quiroga Cubillos', 'usuario': 'DSQUIROGA'},
    '62231004': {'nombre': 'Dayana Ramirez', 'usuario': 'ANGDRAMIREZ'},
    '62230354': {'nombre': 'Karen Ximena Castañeda Cristancho', 'usuario': 'KXCASTANEDA'},
    '62237396': {'nombre': 'Johan Esteven Bernal Diaz', 'usuario': 'JOEBERNAL'},
    '62237293': {'nombre': 'Douglas Enrique Mora', 'usuario': 'DEMORA'},
    '62243896': {'nombre': 'Maria Alejandra Preciado', 'usuario': 'MAPRECIADO'},
    '62246490': {'nombre': 'Norberto Alvarez', 'usuario': 'NOALVAREZ'},
    '62252653': {'nombre': 'Hasbleidy Vanessa Rodriguez Beltran', 'usuario': 'HRODRIGUEZ'},
    '62256597': {'nombre': 'Wilson Arley Perez', 'usuario': 'WIAPEREZ'},
    '62259813': {'nombre': 'Ramiro Augusto Chavez', 'usuario': 'RCHAVEZ'},
    '80024790': {'nombre': 'Heidy Maiyeth Alvarez', 'usuario': 'HALVAREZ'},
    '62256596': {'nombre': 'Alexander Parga', 'usuario': 'APARGA'},
    '62261836': {'nombre': 'Sandra Milena Pinzon', 'usuario': 'SMPINZON'},
    '62261839': {'nombre': 'Andrea Gissette Turizo', 'usuario': 'AGTURIZO'},
    '62266296': {'nombre': 'Nicol Estefani Porras', 'usuario': 'NPORRAS'},
    '62273220': {'nombre': 'Erika Daniela Amaya Varela', 'usuario': 'EAMAYA'},
    '62274136': {'nombre': 'Yuri Viviana Torres Garcia', 'usuario': 'YUVTORRES'},
    '62274134': {'nombre': 'Yeraldin Iveth Correa Mateus', 'usuario': 'YICORREA'},
    '62278611': {'nombre': 'Cesar Augusto Pinzon Calderon', 'usuario': 'CAPINZON'},
    '62277236': {'nombre': 'Cristian Alexander Rodriguez Contreras', 'usuario': 'CRIARODRIGUE'},
    '62274138': {'nombre': 'Angie Lureidy Avila Rodriguez', 'usuario': 'ANLAVILA'},
    '62287385': {'nombre': 'Luisa Fernanda Ardila Parra', 'usuario': 'LUARDILA'},
    '62293397': {'nombre': 'Jenny Andrea Ramirez', 'usuario': 'JENARAMIREZ'},
    '62295420': {'nombre': 'Ana Maria Moreno Chavez', 'usuario': 'ANMMORENO'},
    '62295400': {'nombre': 'Nelson Javier Borrego Hernandez', 'usuario': 'NBORREGO'},
    '62295415': {'nombre': 'Diana Marcela Castro Cardenas', 'usuario': 'DIAMCASTRO'},
    '62295417': {'nombre': 'Ruben Dario Villamizar Rojas', 'usuario': 'RVILLAMIZAR'},
    '62295374': {'nombre': 'Diana Caterin Rojas Rivera', 'usuario': 'DIACROJAS'},
    '62305995': {'nombre': 'Paola Andrea Pinilla Torres', 'usuario': 'PAPINILLA'}
}

# Crear mapeo INVERSO por nombre de usuario
tabla_validadores_por_usuario = {}
for codigo, data in tabla_validadores.items():
    usuario = data['usuario']
    tabla_validadores_por_usuario[usuario] = {
        'codigo': codigo,
        'nombre': data['nombre']
    }

def obtener_info_validador(valor):
    """
    Obtiene información del validador ya sea por código numérico o por nombre de usuario
    Retorna: (nombre_completo, usuario, codigo)
    """
    if pd.isna(valor) or valor == '':
        return ('ALERTA VALIDADOR NO ENCONTRADO', 'ALERTA USUARIO NO ENCONTRADO', '')
    
    valor_limpio = str(valor).strip()
    
    # Intentar buscar por código numérico primero
    if valor_limpio in tabla_validadores:
        info = tabla_validadores[valor_limpio]
        return (info['nombre'], info['usuario'], valor_limpio)
    
    # Si no, intentar buscar por nombre de usuario
    if valor_limpio in tabla_validadores_por_usuario:
        info = tabla_validadores_por_usuario[valor_limpio]
        return (info['nombre'], valor_limpio, info['codigo'])
    
    # Si no se encuentra ni por código ni por usuario
    return ('ALERTA VALIDADOR NO ENCONTRADO', 'ALERTA USUARIO NO ENCONTRADO', valor_limpio)

# ============================================================================
# TABLA SUB_TIPO Y FSE
# ============================================================================
tabla_sub_tipo_fse = {
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
    '301': {'sub_tipo': 'Licencia Maternidad Integ', 'fse': 'No Aplica'},
    '100': {'sub_tipo': 'Vacaciones', 'fse': 'No Aplica'},
    '189': {'sub_tipo': 'Suspension Explicita', 'fse': 'No Aplica'},
    '190': {'sub_tipo': 'Permiso Remunerado', 'fse': 'No Aplica'},
    '191': {'sub_tipo': 'Permiso No Remunerado', 'fse': 'No Aplica'},
    '198': {'sub_tipo': 'Contrato Suspension', 'fse': 'No Aplica'},
    '204': {'sub_tipo': 'Prorroga Quarentena', 'fse': 'No Aplica'},
    '205': {'sub_tipo': 'Calamidad Familiar', 'fse': 'No Aplica'},
    '330': {'sub_tipo': 'Calamidad Domestica', 'fse': 'No Aplica'},
    '340': {'sub_tipo': 'Luto', 'fse': 'No Aplica'},
    '380': {'sub_tipo': 'Licencia No Justificada', 'fse': 'No Aplica'},
    '381': {'sub_tipo': 'Suspension', 'fse': 'No Aplica'},
    '397': {'sub_tipo': 'Registro Sin Jornada', 'fse': 'No Aplica'},
    '187': {'sub_tipo': 'Incapacidad ARL', 'fse': 'No Aplica'},
    '197': {'sub_tipo': 'Licencia Injustificada Int', 'fse': 'No Aplica'},
    '341': {'sub_tipo': 'Luto Integral', 'fse': 'No Aplica'},
    '216': {'sub_tipo': 'Inc. Accidente Trabajo Int', 'fse': 'No Aplica'},
    '195': {'sub_tipo': 'Suspension Integral', 'fse': 'No Aplica'},
    '192': {'sub_tipo': 'No Laboral', 'fse': 'No Aplica'},
    '206': {'sub_tipo': 'Delicadeza', 'fse': 'No Aplica'},
    '334': {'sub_tipo': 'Prorroga Cuarentena Int', 'fse': 'No Aplica'},
    '233': {'sub_tipo': 'Prorroga Enfermedad Int', 'fse': 'Si Aplica'},
    '331': {'sub_tipo': 'Calamidad Domestica Int', 'fse': 'No Aplica'},
    '345': {'sub_tipo': 'Votacion', 'fse': 'No Aplica'},
    '196': {'sub_tipo': 'Permiso No Remun Integral', 'fse': 'No Aplica'},
    '398': {'sub_tipo': 'Maternidad SENA', 'fse': 'No Aplica'},
    '399': {'sub_tipo': 'Aus.Sin Soporte Rech Docs', 'fse': 'No Aplica'},

    
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def convertir_fecha_a_excel(fecha_str):
    """
    Convierte fechas de formato YYYY-MM-DD HH:MM:SS a DD/MM/YYYY para Excel
    """
    if pd.isna(fecha_str) or fecha_str == '' or str(fecha_str).lower() in ['nan', 'none', 'nat']:
        return ''
    
    try:
        # Si ya es formato DD/MM/YYYY, dejarlo como está
        if '/' in str(fecha_str):
            return str(fecha_str).split()[0]  # Quitar hora si existe
        
        # Si es formato YYYY-MM-DD o similar
        fecha_str_limpia = str(fecha_str).split()[0]  # Quitar la hora
        
        # Intentar parsear la fecha
        if '-' in fecha_str_limpia:
            partes = fecha_str_limpia.split('-')
            if len(partes) == 3:
                año, mes, dia = partes
                # Convertir a DD/MM/YYYY
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

def convertir_codigo_sap_a_ssf(codigo_sap):
    """
    Convierte un código SAP (ej: '205') a código SSF (ej: 'CO_FAMILY')
    Usa la tabla inversa de homologación
    """
    if pd.isna(codigo_sap) or codigo_sap == '':
        return ''
    codigo_limpio = str(codigo_sap).strip()
    return tabla_homologacion_inversa.get(codigo_limpio, codigo_limpio)

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def procesar_archivo_ausentismos():
    """
    Función principal que procesa ambos archivos y genera el CSV final
    """
    print("="*80)
    print("=== PROCESAMIENTO DE AUSENTISMOS - VERSIÓN COMPLETA ===")
    print("="*80)
    
    try:
        # ====================================================================
        # PASO 1: LEER ARCHIVO CSV
        # ====================================================================
        print("\n[PASO 1] Leyendo archivo CSV principal...")
        df_csv = pd.read_csv(ruta_entrada_csv, skiprows=2, encoding='utf-8', dtype=str)
        print(f"   ✓ CSV leído: {df_csv.shape[0]} filas, {df_csv.shape[1]} columnas")
        
        # Seleccionar columnas del CSV
        columnas_csv_encontradas = [col for col in columnas_csv if col in df_csv.columns]
        df_csv_filtrado = df_csv[columnas_csv_encontradas].copy()
        
        # CRÍTICO: Asegurar que lastModifiedBy del CSV también sea STRING
        if 'lastModifiedBy' in df_csv_filtrado.columns:
            df_csv_filtrado['lastModifiedBy'] = df_csv_filtrado['lastModifiedBy'].astype(str)
        
        print(f"   ✓ Columnas filtradas del CSV: {len(columnas_csv_encontradas)}")
        
        # ====================================================================
        # PASO 2: LEER ARCHIVO EXCEL
        # ====================================================================
        print("\n[PASO 2] Leyendo archivo Excel para CONCAT...")
        df_excel = pd.read_excel(ruta_entrada_excel, dtype=str)
        print(f"   ✓ Excel leído: {df_excel.shape[0]} filas, {df_excel.shape[1]} columnas")
        print(f"   ✓ Columnas Excel: {list(df_excel.columns[:10])}")
        
        # Renombrar columnas del Excel para que coincidan
        mapeo_excel = {
            'Número de personal': 'ID personal',
            'Nombre empl./cand.': 'Nombre completo',
            'Txt.cl.pres./ab.': 'externalName (Label)',
            'Inicio de validez': 'startDate',
            'Fin de validez': 'endDate',
            'Días presenc./abs.': 'quantityInDays',
            'Días naturales': 'Calendar Days',
            'Descripc.enfermedad': 'Descripción General (Picklist Label)',
            'Modificado por': 'lastModifiedBy',  # MANTENER COMO STRING
            'Final': 'Last Approval Status Date',
            'Clase absent./pres.': 'codigo_sap_original'  # Columna especial
        }
        
        # Aplicar mapeo
        df_excel_renamed = df_excel.rename(columns=mapeo_excel)
        
        # CRÍTICO: Asegurar que lastModifiedBy sea STRING
        if 'lastModifiedBy' in df_excel_renamed.columns:
            df_excel_renamed['lastModifiedBy'] = df_excel_renamed['lastModifiedBy'].astype(str)
            print(f"   ✓ lastModifiedBy convertido a STRING")
            print(f"   📋 Ejemplos de valores: {df_excel_renamed['lastModifiedBy'].head(5).tolist()}")
        
        print(f"   ✓ Columnas renombradas en Excel")
        
        # ====================================================================
        # PASO 2.5: CONVERTIR CÓDIGOS SAP A SSF EN EXCEL
        # ====================================================================
        print("\n[PASO 2.5] Convirtiendo códigos SAP a SSF en archivo Excel...")
        if 'codigo_sap_original' in df_excel_renamed.columns:
            df_excel_renamed['externalCode'] = df_excel_renamed['codigo_sap_original'].apply(convertir_codigo_sap_a_ssf)
            
            ejemplos_conversion = df_excel_renamed[['codigo_sap_original', 'externalCode']].head(5)
            print("   📋 Ejemplos de conversión SAP → SSF:")
            for idx, row in ejemplos_conversion.iterrows():
                print(f"      {row['codigo_sap_original']} → {row['externalCode']}")
            
            # Eliminar columna temporal
            df_excel_renamed = df_excel_renamed.drop(['codigo_sap_original'], axis=1)
        
        # ====================================================================
        # PASO 3: CONCATENAR CSV + EXCEL
        # ====================================================================
        print("\n[PASO 3] Concatenando CSV y Excel...")
        df_combinado = pd.concat([df_csv_filtrado, df_excel_renamed], ignore_index=True, sort=False)
        print(f"   ✓ Datos combinados: {df_combinado.shape[0]} filas totales")
        print(f"   ✓ CSV: {df_csv_filtrado.shape[0]} filas")
        print(f"   ✓ Excel: {df_excel_renamed.shape[0]} filas")
        
        # ====================================================================
        # PASO 3.5: CONVERTIR FECHAS A FORMATO DD/MM/YYYY
        # ====================================================================
        print("\n[PASO 3.5] Convirtiendo fechas a formato DD/MM/YYYY...")
        
        columnas_fecha = ['startDate', 'endDate', 'Last Approval Status Date']
        
        for col in columnas_fecha:
            if col in df_combinado.columns:
                print(f"   🔧 Convirtiendo columna: {col}")
                print(f"      Ejemplo ANTES: {df_combinado[col].iloc[0]}")
                
                df_combinado[col] = df_combinado[col].apply(convertir_fecha_a_excel)
                
                print(f"      Ejemplo DESPUÉS: {df_combinado[col].iloc[0]}")
        
        print(f"   ✓ Fechas convertidas a formato DD/MM/YYYY")
        
        # ====================================================================
        # PASO 4: CREAR COLUMNA DE HOMOLOGACIÓN (SSF → SAP)
        # ====================================================================
        print("\n[PASO 4] Creando columna de homologación SSF vs SAP...")
        if 'externalCode' in df_combinado.columns:
            df_combinado['Homologacion_clase_de_ausentismo_SSF_vs_SAP'] = df_combinado['externalCode'].map(tabla_homologacion)
            
            valores_encontrados = df_combinado['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].notna().sum()
            print(f"   ✓ Homologación aplicada: {valores_encontrados}/{len(df_combinado)} códigos")
        
        # ====================================================================
        # PASO 5: CREAR LLAVE (ANTES DE ELIMINAR DUPLICADOS)
        # ====================================================================
        print("\n[PASO 5] Creando columna LLAVE...")
        df_combinado['startDate_limpia'] = df_combinado['startDate'].apply(limpiar_fecha_para_llave)
        df_combinado['endDate_limpia'] = df_combinado['endDate'].apply(limpiar_fecha_para_llave)
        
        df_combinado['llave'] = (
            df_combinado['ID personal'].astype(str).fillna('') +
            df_combinado['startDate_limpia'] +
            df_combinado['endDate_limpia'] +
            df_combinado['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].astype(str).fillna('')
        )
        
        # Agregar prefijo K
        df_combinado['llave'] = 'K' + df_combinado['llave'].astype(str)
        
        print(f"   ✓ Llaves creadas: {len(df_combinado)}")
        print(f"   📋 Ejemplos de llaves:")
        for llave in df_combinado['llave'].head(3):
            print(f"      {llave}")
        
        # Limpiar columnas temporales
        df_combinado = df_combinado.drop(['startDate_limpia', 'endDate_limpia'], axis=1)
        
        # ====================================================================
        # PASO 6: ELIMINAR DUPLICADOS POR LLAVE
        # ====================================================================
        print("\n[PASO 6] Eliminando duplicados por llave...")
        registros_antes = len(df_combinado)
        duplicados_encontrados = df_combinado['llave'].duplicated().sum()
        
        print(f"   ⚠ Duplicados encontrados: {duplicados_encontrados}")
        
        if duplicados_encontrados > 0:
            # Mantener el primer registro de cada llave
            df_combinado = df_combinado.drop_duplicates(subset=['llave'], keep='first')
            registros_despues = len(df_combinado)
            eliminados = registros_antes - registros_despues
            
            print(f"   ✓ Registros eliminados: {eliminados}")
            print(f"   ✓ Registros finales: {registros_despues}")
        else:
            print(f"   ✅ No hay duplicados - todas las llaves son únicas")
        
        # ====================================================================
        # PASO 7: CREAR COLUMNAS DE VALIDADOR (NOMBRE Y USUARIO)
        # ====================================================================
        print("\n[PASO 7] Creando columnas de validador (maneja códigos Y usuarios)...")
        if 'lastModifiedBy' in df_combinado.columns:
            print("   🔧 Procesando lastModifiedBy (puede contener códigos o usuarios)...")
            
            # Aplicar la función que maneja ambos casos
            validador_info = df_combinado['lastModifiedBy'].apply(obtener_info_validador)
            
            # Separar en 3 columnas
            df_combinado['nombre_validador'] = validador_info.apply(lambda x: x[0])
            df_combinado['usuario_validador'] = validador_info.apply(lambda x: x[1])
            df_combinado['codigo_validador'] = validador_info.apply(lambda x: x[2])
            
            validadores_ok = (df_combinado['nombre_validador'] != 'ALERTA VALIDADOR NO ENCONTRADO').sum()
            print(f"   ✓ Validadores mapeados: {validadores_ok}/{len(df_combinado)}")
            
            # Mostrar ejemplos
            print(f"\n   📋 Ejemplos de conversión (primeros 5):")
            for i in range(min(5, len(df_combinado))):
                original = df_combinado['lastModifiedBy'].iloc[i]
                nombre = df_combinado['nombre_validador'].iloc[i]
                usuario = df_combinado['usuario_validador'].iloc[i]
                codigo = df_combinado['codigo_validador'].iloc[i]
                print(f"      '{original}' → Nombre: {nombre}, Usuario: {usuario}, Código: {codigo}")
        
        # ====================================================================
        # PASO 8: CREAR COLUMNAS SUB_TIPO Y FSE
        # ====================================================================
        print("\n[PASO 8] Creando columnas Sub_tipo y FSE...")
        if 'Homologacion_clase_de_ausentismo_SSF_vs_SAP' in df_combinado.columns:
            df_combinado['Sub_tipo'] = df_combinado['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].apply(
                lambda x: tabla_sub_tipo_fse.get(str(x), {}).get('sub_tipo', 'ALERTA SUB_TIPO NO ENCONTRADO') if pd.notna(x) else 'ALERTA SUB_TIPO NO ENCONTRADO'
            )
            
            df_combinado['FSE'] = df_combinado['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].apply(
                lambda x: tabla_sub_tipo_fse.get(str(x), {}).get('fse', 'No Aplica') if pd.notna(x) else 'No Aplica'
            )
            
            sub_tipo_ok = (df_combinado['Sub_tipo'] != 'ALERTA SUB_TIPO NO ENCONTRADO').sum()
            fse_si = (df_combinado['FSE'] == 'Si Aplica').sum()
            fse_no = (df_combinado['FSE'] == 'No Aplica').sum()
            
            print(f"   ✓ Sub_tipo mapeados: {sub_tipo_ok}/{len(df_combinado)}")
            print(f"   ✓ FSE - Si Aplica: {fse_si}")
            print(f"   ✓ FSE - No Aplica: {fse_no}")
        
        # ====================================================================
        # PASO 9: MAPEO FINAL DE NOMBRES DE COLUMNAS
        # ====================================================================
        print("\n[PASO 9] Aplicando mapeo de nombres de columnas...")
        
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
            'usuario_validador': 'usuario_validador',
            'codigo_validador': 'codigo_validador',
            'Sub_tipo': 'sub_tipo',
            'FSE': 'fse'
        }
        
        # Aplicar solo las columnas que existen
        mapeo_aplicable = {k: v for k, v in mapeo_columnas_final.items() if k in df_combinado.columns}
        df_final = df_combinado.rename(columns=mapeo_aplicable)
        
        print(f"   ✓ Columnas renombradas: {len(mapeo_aplicable)}")
        print(f"   ✓ Total columnas finales: {len(df_final.columns)}")
        
        # ====================================================================
        # PASO 10: LIMPIEZA FINAL Y GUARDADO
        # ====================================================================
        print("\n[PASO 10] Limpieza final y guardado...")
        
        # Crear directorio si no existe
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
        
        # CRÍTICO: Asegurar que last_modified_by sea STRING en salida final
        if 'last_modified_by' in df_final.columns:
            print("   🔧 Forzando last_modified_by como STRING...")
            df_final['last_modified_by'] = df_final['last_modified_by'].astype(str)
            # Agregar comillas para forzar que Excel lo lea como texto
            df_final['last_modified_by'] = '"' + df_final['last_modified_by'] + '"'
            print(f"   ✓ Ejemplos de last_modified_by: {df_final['last_modified_by'].head(3).tolist()}")
        
        # Limpiar número de documento
        if 'numero_documento_identidad' in df_final.columns:
            df_final['numero_documento_identidad'] = df_final['numero_documento_identidad'].astype(str).replace('nan', '')
            df_final['numero_documento_identidad'] = '"' + df_final['numero_documento_identidad'] + '"'
        
        # Guardar archivo
        df_final.to_csv(ruta_completa_salida, index=False, encoding='utf-8', quoting=2)
        
        print(f"   ✓ Archivo guardado: {ruta_completa_salida}")
        print(f"   ✓ Registros procesados: {len(df_final)}")
        
        # ====================================================================
        # RESUMEN FINAL
        # ====================================================================
        print("\n" + "="*80)
        print("=== RESUMEN FINAL DEL PROCESAMIENTO ===")
        print("="*80)
        
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"   Total de registros: {len(df_final)}")
        print(f"   Total de columnas: {len(df_final.columns)}")
        print(f"   Registros únicos por llave: {df_final['llave'].nunique()}")
        
        if 'homologacion_clase_de_ausentismo_ssf_vs_sap' in df_final.columns:
            print(f"\n📋 HOMOLOGACIÓN SSF vs SAP:")
            homolog_stats = df_final['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts().head(10)
            print(f"   Códigos SAP más frecuentes:")
            for codigo, freq in homolog_stats.items():
                porcentaje = (freq / len(df_final)) * 100
                print(f"      {codigo}: {freq} registros ({porcentaje:.1f}%)")
        
        if 'sub_tipo' in df_final.columns and 'fse' in df_final.columns:
            print(f"\n🏥 SUB_TIPO Y FSE:")
            
            sub_tipo_alertas = (df_final['sub_tipo'] == 'ALERTA SUB_TIPO NO ENCONTRADO').sum()
            if sub_tipo_alertas > 0:
                print(f"   🚨 Alertas de Sub_tipo: {sub_tipo_alertas} registros")
            
            print(f"\n   Top 5 Sub_tipos:")
            sub_tipo_top = df_final[df_final['sub_tipo'] != 'ALERTA SUB_TIPO NO ENCONTRADO']['sub_tipo'].value_counts().head(5)
            for sub_tipo, freq in sub_tipo_top.items():
                porcentaje = (freq / len(df_final)) * 100
                print(f"      {sub_tipo}: {freq} ({porcentaje:.1f}%)")
            
            print(f"\n   Distribución FSE:")
            fse_stats = df_final['fse'].value_counts()
            for fse_val, freq in fse_stats.items():
                porcentaje = (freq / len(df_final)) * 100
                print(f"      {fse_val}: {freq} registros ({porcentaje:.1f}%)")
        
        if 'nombre_validador' in df_final.columns:
            print(f"\n👤 VALIDADORES:")
            
            validador_alertas = (df_final['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
            if validador_alertas > 0:
                print(f"   🚨 Alertas de validadores: {validador_alertas} registros ({(validador_alertas/len(df_final)*100):.1f}%)")
            
            print(f"\n   Top 10 Validadores:")
            validadores_top = df_final[df_final['nombre_validador'] != 'ALERTA VALIDADOR NO ENCONTRADO']['nombre_validador'].value_counts().head(10)
            for i, (nombre, freq) in enumerate(validadores_top.items(), 1):
                porcentaje = (freq / len(df_final)) * 100
                usuario = df_final[df_final['nombre_validador'] == nombre]['usuario_validador'].iloc[0]
                print(f"      {i:2d}. {nombre} ({usuario}): {freq} ({porcentaje:.1f}%)")
        
        print(f"\n🔑 COLUMNAS FINALES ({len(df_final.columns)}):")
        for i, col in enumerate(df_final.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n✅ PROCESO COMPLETADO EXITOSAMENTE")
        print(f"   📁 Archivo: {archivo_salida}")
        print(f"   📊 Registros: {len(df_final)}")
        print(f"   🔑 Llaves únicas: {df_final['llave'].nunique()}")
        print(f"   👤 Validadores identificados: {(df_final['nombre_validador'] != 'ALERTA VALIDADOR NO ENCONTRADO').sum()}")
        print(f"   📋 Sub_tipos identificados: {(df_final['sub_tipo'] != 'ALERTA SUB_TIPO NO ENCONTRADO').sum()}")
        
        return df_final
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# FUNCIÓN DE DIAGNÓSTICO
# ============================================================================
def diagnostico_archivos():
    """Función de diagnóstico para entender la estructura de ambos archivos"""
    print("="*80)
    print("=== DIAGNÓSTICO DE ARCHIVOS ===")
    print("="*80)
    
    print("\n[1] DIAGNÓSTICO CSV:")
    try:
        with open(ruta_entrada_csv, 'r', encoding='utf-8') as file:
            for i in range(5):
                linea = file.readline().strip()
                print(f"   Línea {i}: {linea[:100]}...")
    except Exception as e:
        print(f"   ❌ Error leyendo CSV: {e}")
    
    print("\n[2] DIAGNÓSTICO EXCEL:")
    try:
        df_excel_test = pd.read_excel(ruta_entrada_excel, nrows=3, dtype=str)
        print(f"   ✓ Shape: {df_excel_test.shape}")
        print(f"   ✓ Columnas: {list(df_excel_test.columns)}")
        print(f"\n   Primeras 3 filas:")
        print(df_excel_test.to_string(index=False))
    except Exception as e:
        print(f"   ❌ Error leyendo Excel: {e}")

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================
if __name__ == "__main__":
    # Ejecutar diagnóstico primero (opcional)
    diagnostico_archivos()
    
    print("\n" + "="*80)
    print("INICIANDO PROCESAMIENTO PRINCIPAL...")
    print("="*80 + "\n")
    
    # Ejecutar proceso principal
    resultado = procesar_archivo_ausentismos()
    
    if resultado is not None:
        print("\n" + "="*80)
        print("🎉 ¡PROCESO COMPLETADO CON ÉXITO, PARCERO! 🎉")
        print("="*80)
        print(f"\n📁 Revisa tu archivo en:")
        print(f"   {ruta_completa_salida}")
        print(f"\n📊 Estadísticas rápidas:")
        print(f"   • Registros totales: {len(resultado)}")
        print(f"   • Llaves únicas: {resultado['llave'].nunique()}")
        print(f"   • Columnas: {len(resultado.columns)}")
    else:
        print("\n❌ El proceso falló. Revisa los errores arriba.")
