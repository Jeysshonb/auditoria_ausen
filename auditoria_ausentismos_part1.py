# Auditoría Ausentismos - Con Columna Nombre Validador
import pandas as pd
import os

# Rutas de archivos
ruta_entrada = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_planos\AusentismoCOL-ApprovedPayrollIndicarfecha-Componente1.csv"
directorio_salida = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida"
archivo_salida = "ausentismo_procesado_especifico.csv"
ruta_completa_salida = os.path.join(directorio_salida, archivo_salida)

# Columnas que necesitas (22 columnas específicas)
columnas_requeridas = [
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

# Mapeo a snake_case (ahora incluye nombre_validador, sub_tipo y fse)
mapeo_columnas = {
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

# Tabla de homologación SSF vs SAP - COMPLETA
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
    'CO_VacationsFDS': '100'
}

# NUEVA TABLA: Mapeo de códigos de aprobador a nombres
tabla_validadores = {
    '80002749': 'Diana Paola Martinez Diaz',
    '62208433': 'Nini Johanna Neira',
    '62208420': 'Maria Lorena Ospina',
    '62208383': 'Juan Sebastian Sanabria Cabezas',
    '62208367': 'Yeimy Velasco',
    '60005132': 'Angie Paola Muñoz',
    '80025780': 'Buitrago Baron Deisy Marley',
    '80005980': 'Caro Salamanca Wilson Alfredo',
    '80003719': 'Carreño Diaz Natalia Andrea',
    '60005117': 'Daniela Maria Herrera',
    '80022209': 'Guerra Cabrera Carolina',
    '80025779': 'Huerfano Davila Edgar Andres',
    '60005052': 'Jose Esteban Vargas',
    '60006940': 'Juan Esteban Sanabria',
    '60005371': 'Lenin Karina Triana',
    '60005046': 'Luis Armando Chacon',
    '60005129': 'Luz Liliana Rodriguez',
    '60006593': 'Luz Liliana Rodriguez',
    '60006112': 'Mancera Reinosa Diana Maria',
    '60006909': 'Maria Jose Alfonso',
    '60005057': 'Maria Lorena Ospina',
    '80000523': 'Rodriguez Gutierrez Paula Marcela',
    '80025781': 'Yaima Motta Alejandra Lorena',
    '60006707': 'Yeimy Velasco',
    '62212713': 'Andres Castaño',
    '62212735': 'Diana Shirley Quiroga Cubillos',
    '62214358': 'Paula Estefania Cardenas Diaz',
    '62214530': 'Ana Milena Moyano Beltran',
    '62212720': 'Lenin Karina Triana',
    '62215253': 'Angie Marcela Carranza Arbelaez',
    '62219343': 'Johan Esteven Bernal Diaz',
    '62219327': 'Karen Ximena Castañeda Cristancho',
    '62220971': 'Paula Estefania Cardenas Diaz',
    '62222408': 'Julieth Lorena Pacheco Vargas',
    '62214888': 'Liliana Espitia',
    '62222738': 'Diana Shirley Quiroga Cubillos',
    '62231004': 'Dayana Ramirez',
    '62230354': 'Karen Ximena Castañeda Cristancho',
    '62237396': 'Johan Esteven Bernal Diaz',
    '62237293': 'Douglas Enrique Mora',
    '62243896': 'Maria Alejandra Preciado',
    '62246490': 'Norberto Alvarez',
    '62252653': 'Hasbleidy Vanessa Rodriguez Beltran',
    '62256597': 'Wilson Arley Perez',
    '62259813': 'Ramiro Augusto Chavez',
    '80024790': 'Heidy Maiyeth Alvarez',
    '62256596': 'Alexander Parga',
    '62261836': 'Sandra Milena Pinzon',
    '62261839': 'Andrea Gissette Turizo',
    '62266296': 'Nicol Estefani Porras',
    '62273220': 'Erika Daniela Amaya Varela',
    '62274136': 'Yuri Viviana Torres Garcia',
    '62274134': 'Yeraldin Iveth Correa Mateus',
    '62278611': 'Cesar Augusto Pinzon Calderon',
    '62277236': 'Cristian Alexander Rodriguez Contreras',
    '62274138': 'Angie Lureidy Avila Rodriguez',
    '62287385': 'Luisa Fernanda Ardila Parra',
    '62293397': 'Jenny Andrea Ramirez',
    '62295420': 'Ana Maria Moreno Chavez',
    '62295400': 'Nelson Javier Borrego Hernandez',
    '62295415': 'Diana Marcela Castro Cardenas',
    '62295417': 'Ruben Dario Villamizar Rojas',
    '62295374': 'Diana Caterin Rojas Rivera'
}

# NUEVA TABLA: Mapeo de código homologación a Sub_tipo y FSE
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
    '301': {'sub_tipo': 'Licencia Maternidad Integ', 'fse': 'No Aplica'}
}

def limpiar_fecha_para_llave(fecha_str):
    """
    Función que REALMENTE limpia las fechas para la llave - quita TODO lo que no sea número
    """
    if pd.isna(fecha_str) or fecha_str == '' or str(fecha_str).lower() in ['nan', 'none', 'nat']:
        return ''
    
    # Convertir a string y quitar TODO lo que no sea dígito
    fecha_limpia = ''.join(c for c in str(fecha_str) if c.isdigit())
    return fecha_limpia

def procesar_archivo_ausentismos():
    """
    Función principal que procesa el archivo de ausentismos
    """
    print("=== PROCESAMIENTO DE AUSENTISMOS ===")
    
    try:
        # PASO 1: Leer el archivo usando los headers que ya tiene
        print("1. Leyendo archivo CSV...")
        
        df = pd.read_csv(ruta_entrada, skiprows=2, encoding='utf-8', dtype=str)
        
        print(f"   ✓ Archivo leído: {df.shape[0]} filas, {df.shape[1]} columnas")
        print(f"   ✓ Primeras columnas: {list(df.columns[:5])}")
        
        # PASO 2: Verificar que tenemos las columnas que necesitamos
        print("\n2. Verificando columnas requeridas...")
        
        columnas_encontradas = []
        columnas_faltantes = []
        
        for col in columnas_requeridas:
            if col in df.columns:
                columnas_encontradas.append(col)
            else:
                columnas_faltantes.append(col)
        
        print(f"   ✓ Columnas encontradas: {len(columnas_encontradas)}/22")
        if columnas_faltantes:
            print(f"   ⚠ Columnas faltantes: {columnas_faltantes}")
        
        # PASO 3: Extraer solo las columnas que necesitamos
        print("\n3. Extrayendo columnas específicas...")
        df_especifico = df[columnas_encontradas].copy()
        
        print(f"   ✓ DataFrame específico: {df_especifico.shape}")
        
        # PASO 4: Verificar los datos
        print("\n4. Verificando primeros datos...")
        print(f"   ID personal: {df_especifico['ID personal'].iloc[0]}")
        print(f"   Nombre: {df_especifico['Nombre completo'].iloc[0]}")
        print(f"   Fecha inicio: {df_especifico['startDate'].iloc[0]}")
        
        # PASO 5: Aplicar mapeo de nombres y agregar columna de homologación
        print("\n5. Aplicando mapeo de columnas y agregando homologación...")
        
        # Crear la columna de homologación ANTES del mapeo de nombres
        if 'externalCode' in df_especifico.columns:
            print("   🔧 Creando columna de homologación SSF vs SAP...")
            
            df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'] = df_especifico['externalCode'].map(tabla_homologacion)
            
            valores_encontrados = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].notna().sum()
            valores_totales = len(df_especifico)
            valores_no_encontrados = valores_totales - valores_encontrados
            
            print(f"   ✓ Homologación aplicada: {valores_encontrados}/{valores_totales} códigos encontrados")
            if valores_no_encontrados > 0:
                codigos_faltantes = df_especifico[df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].isna()]['externalCode'].unique()
                print(f"   ⚠ Códigos no encontrados en tabla de homologación: {list(codigos_faltantes)}")
            
            print("   📋 Ejemplos de homologación:")
            for i in range(min(5, len(df_especifico))):
                codigo = df_especifico['externalCode'].iloc[i]
                homolog = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].iloc[i]
                print(f"      {codigo} → {homolog}")
        
        # PASO 5.5: CREAR COLUMNA NOMBRE_VALIDADOR
        print("\n5.5 Creando columna NOMBRE_VALIDADOR...")
        
        if 'lastModifiedBy' in df_especifico.columns:
            print("   🔧 Mapeando códigos de aprobador a nombres...")
            
            df_especifico['lastModifiedBy_limpio'] = df_especifico['lastModifiedBy'].astype(str).str.strip()
            
            # Aplicar el mapeo y poner "ALERTA VALIDADOR NO ENCONTRADO" cuando no hay match
            df_especifico['nombre_validador'] = df_especifico['lastModifiedBy_limpio'].map(tabla_validadores).fillna('ALERTA VALIDADOR NO ENCONTRADO')
            
            validadores_encontrados = (df_especifico['nombre_validador'] != 'ALERTA VALIDADOR NO ENCONTRADO').sum()
            validadores_totales = len(df_especifico)
            validadores_no_encontrados = validadores_totales - validadores_encontrados
            
            print(f"   ✓ Nombres de validadores mapeados: {validadores_encontrados}/{validadores_totales}")
            
            if validadores_no_encontrados > 0:
                codigos_validadores_faltantes = df_especifico[df_especifico['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO']['lastModifiedBy_limpio'].unique()
                print(f"   ⚠ ALERTA: {validadores_no_encontrados} registros con validador no encontrado")
                print(f"   ⚠ Códigos de validadores no encontrados: {list(codigos_validadores_faltantes)[:10]}")
            
            print("   📋 Ejemplos de mapeo de validadores:")
            for i in range(min(5, len(df_especifico))):
                codigo_val = df_especifico['lastModifiedBy_limpio'].iloc[i]
                nombre_val = df_especifico['nombre_validador'].iloc[i]
                print(f"      {codigo_val} → {nombre_val}")
            
            df_especifico = df_especifico.drop(['lastModifiedBy_limpio'], axis=1)
        else:
            print("   ❌ No se encontró la columna 'lastModifiedBy'")
        
        # PASO 5.55: CREAR COLUMNAS SUB_TIPO Y FSE
        print("\n5.55 Creando columnas SUB_TIPO y FSE...")
        
        if 'Homologacion_clase_de_ausentismo_SSF_vs_SAP' in df_especifico.columns:
            print("   🔧 Mapeando códigos de homologación a Sub_tipo y FSE...")
            
            # Crear las columnas usando el mapeo
            df_especifico['Sub_tipo'] = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                lambda x: tabla_sub_tipo_fse.get(str(x), {}).get('sub_tipo', 'ALERTA SUB_TIPO NO ENCONTRADO') if pd.notna(x) else 'ALERTA SUB_TIPO NO ENCONTRADO'
            )
            
            df_especifico['FSE'] = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].map(
                lambda x: tabla_sub_tipo_fse.get(str(x), {}).get('fse', 'No Aplica') if pd.notna(x) else 'No Aplica'
            )
            
            # Contar valores encontrados
            sub_tipo_encontrados = (df_especifico['Sub_tipo'] != 'ALERTA SUB_TIPO NO ENCONTRADO').sum()
            fse_aplicables = (df_especifico['FSE'] == 'Si Aplica').sum()
            fse_no_aplicables = (df_especifico['FSE'] == 'No Aplica').sum()
            totales = len(df_especifico)
            
            print(f"   ✓ Sub_tipo mapeados: {sub_tipo_encontrados}/{totales}")
            print(f"   ✓ FSE - Si Aplica: {fse_aplicables}")
            print(f"   ✓ FSE - No Aplica: {fse_no_aplicables}")
            
            # Mostrar códigos no encontrados
            codigos_no_encontrados = df_especifico[df_especifico['Sub_tipo'] == 'ALERTA SUB_TIPO NO ENCONTRADO']['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].unique()
            codigos_no_encontrados = [c for c in codigos_no_encontrados if pd.notna(c) and c != '']
            if codigos_no_encontrados:
                print(f"   ⚠ ALERTA: Códigos sin Sub_tipo: {list(codigos_no_encontrados)}")
            
            # Mostrar ejemplos
            print("   📋 Ejemplos de mapeo Sub_tipo y FSE:")
            for i in range(min(5, len(df_especifico))):
                codigo_homolog = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].iloc[i]
                sub_tipo_val = df_especifico['Sub_tipo'].iloc[i]
                fse_val = df_especifico['FSE'].iloc[i]
                print(f"      Código {codigo_homolog} → Sub_tipo: '{sub_tipo_val}', FSE: '{fse_val}'")
        else:
            print("   ❌ No se encontró la columna 'Homologacion_clase_de_ausentismo_SSF_vs_SAP'")
        
        # PASO 5.6: CREAR COLUMNA LLAVE
        print("\n5.6 Creando columna LLAVE (SIN barras en fechas)...")
        
        columnas_llave_originales = ['ID personal', 'startDate', 'endDate', 'Homologacion_clase_de_ausentismo_SSF_vs_SAP']
        columnas_disponibles = all(col in df_especifico.columns for col in columnas_llave_originales)
        
        if columnas_disponibles:
            print("   🔧 Limpiando fechas y creando llave SOLO CON NÚMEROS...")
            
            print("   📋 Ejemplos de fechas ANTES de limpiar:")
            for i in range(min(3, len(df_especifico))):
                start_orig = df_especifico['startDate'].iloc[i]
                end_orig = df_especifico['endDate'].iloc[i]
                print(f"      Fila {i+1}: start='{start_orig}', end='{end_orig}'")
            
            df_especifico['startDate_limpia'] = df_especifico['startDate'].apply(limpiar_fecha_para_llave)
            df_especifico['endDate_limpia'] = df_especifico['endDate'].apply(limpiar_fecha_para_llave)
            
            print("   📋 Ejemplos de fechas DESPUÉS de limpiar:")
            for i in range(min(3, len(df_especifico))):
                start_limpia = df_especifico['startDate_limpia'].iloc[i]
                end_limpia = df_especifico['endDate_limpia'].iloc[i]
                print(f"      Fila {i+1}: start='{start_limpia}', end='{end_limpia}'")
            
            df_especifico['llave'] = (
                df_especifico['ID personal'].astype(str).fillna('') +
                df_especifico['startDate_limpia'] +
                df_especifico['endDate_limpia'] +
                df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].astype(str).fillna('')
            )
            
            print(f"   ✓ Columna llave creada con {len(df_especifico)} registros")
            
            print("   📋 Ejemplos de llaves generadas (FINAL):")
            for i in range(min(5, len(df_especifico))):
                id_pers = df_especifico['ID personal'].iloc[i]
                start_limpia = df_especifico['startDate_limpia'].iloc[i]
                end_limpia = df_especifico['endDate_limpia'].iloc[i]
                homolog = df_especifico['Homologacion_clase_de_ausentismo_SSF_vs_SAP'].iloc[i]
                llave = df_especifico['llave'].iloc[i]
                print(f"      {id_pers} + {start_limpia} + {end_limpia} + {homolog} = {llave}")
            
            df_especifico = df_especifico.drop(['startDate_limpia', 'endDate_limpia'], axis=1)
            
            duplicados = df_especifico['llave'].duplicated().sum()
            if duplicados > 0:
                print(f"   ⚠ Se encontraron {duplicados} llaves duplicadas")
            else:
                print(f"   ✅ Todas las llaves son únicas")
                
        else:
            print("   ❌ No se pueden crear las llaves - faltan columnas requeridas")
            columnas_faltantes_llave = [col for col in columnas_llave_originales if col not in df_especifico.columns]
            print(f"   ❌ Columnas faltantes: {columnas_faltantes_llave}")
        
        mapeo_actual = {col: mapeo_columnas[col] for col in df_especifico.columns if col in mapeo_columnas}
        df_final = df_especifico.rename(columns=mapeo_actual)
        
        print(f"   ✓ Columnas renombradas: {len(mapeo_actual)}")
        print(f"   ✓ Columnas finales: {len(df_final.columns)} (incluyendo homologación, llave, nombre_validador, sub_tipo y fse)")
        
        # PASO 6: Limpiar y guardar
        print("\n6. Limpiando datos y guardando archivo...")
        
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
        
        if 'tipo_documento_identidad' in df_final.columns:
            df_final['tipo_documento_identidad'] = df_final['tipo_documento_identidad'].fillna('')
        
        if 'numero_documento_identidad' in df_final.columns:
            print("   🔧 Corrigiendo numero_documento_identidad...")
            df_final['numero_documento_identidad'] = df_final['numero_documento_identidad'].astype(str).replace('nan', '')
            df_final['numero_documento_identidad'] = '"' + df_final['numero_documento_identidad'] + '"'
            print(f"   ✓ Ejemplos corregidos: {df_final['numero_documento_identidad'].head(3).tolist()}")
        
        if 'llave' in df_final.columns:
            print("   🔧 Agregando prefijo a la llave para evitar notación científica...")
            df_final['llave'] = 'K' + df_final['llave'].astype(str)
            print(f"   ✓ Ejemplos de llaves con prefijo: {df_final['llave'].head(3).tolist()}")
        
        df_final.to_csv(ruta_completa_salida, index=False, encoding='utf-8', quoting=2)
        
        print(f"   ✓ Archivo guardado: {ruta_completa_salida}")
        print(f"   ✓ Registros procesados: {len(df_final)}")
        print(f"   ✓ Columna nombre_validador agregada exitosamente")
        print(f"   ✓ Columnas sub_tipo y fse agregadas exitosamente")
        
        # PASO 7: Mostrar resumen final
        print("\n=== RESUMEN FINAL ===")
        print(f"Columnas procesadas: {len(df_final.columns)}")
        for i, col in enumerate(df_final.columns, 1):
            print(f"{i:2d}. {col}")
        
        print(f"\nPrimera fila de ejemplo:")
        primera_fila = df_final.iloc[0]
        for col in list(df_final.columns)[:12]:
            print(f"  {col}: {primera_fila[col]}")
        
        if 'homologacion_clase_de_ausentismo_ssf_vs_sap' in df_final.columns:
            print(f"\n📊 ESTADÍSTICAS DE HOMOLOGACIÓN:")
            homolog_stats = df_final['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts()
            print(f"   Total de códigos únicos homologados: {len(homolog_stats)}")
            print(f"   Códigos más frecuentes:")
            for codigo, freq in homolog_stats.head(5).items():
                print(f"     {codigo}: {freq} registros")
        
        if 'sub_tipo' in df_final.columns and 'fse' in df_final.columns:
            print(f"\n📋 ESTADÍSTICAS DE SUB_TIPO Y FSE:")
            
            # Contar Sub_tipos con alerta
            sub_tipo_alertas = (df_final['sub_tipo'] == 'ALERTA SUB_TIPO NO ENCONTRADO').sum()
            sub_tipo_ok = (df_final['sub_tipo'] != 'ALERTA SUB_TIPO NO ENCONTRADO').sum()
            
            print(f"   Total de registros con Sub_tipo: {sub_tipo_ok}")
            if sub_tipo_alertas > 0:
                print(f"   🚨 Registros con ALERTA SUB_TIPO NO ENCONTRADO: {sub_tipo_alertas}")
            
            # Contar por tipo de FSE
            fse_stats = df_final['fse'].value_counts()
            print(f"   Distribución FSE:")
            for fse_val, freq in fse_stats.items():
                porcentaje = (freq / len(df_final)) * 100
                print(f"     {fse_val}: {freq} registros ({porcentaje:.1f}%)")
            
            # Mostrar algunos Sub_tipos más comunes (excluyendo alertas)
            print(f"   Sub_tipos más frecuentes:")
            sub_tipo_stats = df_final[df_final['sub_tipo'] != 'ALERTA SUB_TIPO NO ENCONTRADO']['sub_tipo'].value_counts().head(5)
            for sub_tipo_val, freq in sub_tipo_stats.items():
                print(f"     {sub_tipo_val}: {freq} registros")
        
        if 'nombre_validador' in df_final.columns:
            print(f"\n👤 ESTADÍSTICAS DE VALIDADORES:")
            validadores_stats = df_final['nombre_validador'].value_counts()
            print(f"   Total de validadores únicos: {len(validadores_stats)}")
            print(f"   Validadores más frecuentes:")
            
            # Contar los que tienen alerta
            alertas_count = (df_final['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
            
            # Mostrar top 5 (excluyendo las alertas para el top)
            top_validadores = df_final[df_final['nombre_validador'] != 'ALERTA VALIDADOR NO ENCONTRADO']['nombre_validador'].value_counts().head(5)
            for nombre, freq in top_validadores.items():
                print(f"     {nombre}: {freq} registros")
            
            if alertas_count > 0:
                print(f"\n   🚨 ALERTAS:")
                print(f"     Registros con 'ALERTA VALIDADOR NO ENCONTRADO': {alertas_count}")
                porcentaje_alerta = (alertas_count / len(df_final)) * 100
                print(f"     Porcentaje de alertas: {porcentaje_alerta:.2f}%")
        
        if 'llave' in df_final.columns:
            print(f"\n🔑 ESTADÍSTICAS DE LLAVES:")
            llaves_unicas = df_final['llave'].nunique()
            total_registros = len(df_final)
            print(f"   Total de llaves únicas: {llaves_unicas}")
            print(f"   Total de registros: {total_registros}")
            if llaves_unicas == total_registros:
                print(f"   ✅ Todas las llaves son únicas")
            else:
                print(f"   ⚠ Hay {total_registros - llaves_unicas} llaves duplicadas")
        
        print(f"\n✅ PROCESO COMPLETADO EXITOSAMENTE")
        print(f"   📁 Archivo guardado con {len(df_final.columns)} columnas")
        print(f"   📊 {len(df_final)} registros procesados")
        print(f"   🔑 Columna llave creada exitosamente (SIN barras, CON prefijo K)")
        print(f"   👤 Columna nombre_validador agregada exitosamente")
        print(f"   📋 Columnas sub_tipo y fse agregadas exitosamente")
        return df_final
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def diagnostico_archivo():
    """
    Función de diagnóstico para entender la estructura del archivo
    """
    print("=== DIAGNÓSTICO DEL ARCHIVO ===")
    
    with open(ruta_entrada, 'r', encoding='utf-8') as file:
        for i in range(5):
            linea = file.readline().strip()
            print(f"Línea {i}: {linea[:100]}...")
    
    print("\nProbando diferentes configuraciones:")
    
    configs = [
        {"skiprows": 0, "desc": "Sin skiprows"},
        {"skiprows": 1, "desc": "Skiprows=1"},
        {"skiprows": 2, "desc": "Skiprows=2"},
    ]
    
    for config in configs:
        try:
            df_test = pd.read_csv(ruta_entrada, nrows=2, encoding='utf-8', **{k:v for k,v in config.items() if k != 'desc'})
            print(f"{config['desc']}: {df_test.shape[1]} columnas, primera columna: {df_test.columns[0]}")
        except Exception as e:
            print(f"{config['desc']}: Error - {e}")

if __name__ == "__main__":
    diagnostico_archivo()
    
    print("\n" + "="*50)
    
    resultado = procesar_archivo_ausentismos()
    
    if resultado is not None and 'nombre_validador' in resultado.columns:
        print("\n" + "="*50)
        print("=== ANÁLISIS DETALLADO DE NOMBRE_VALIDADOR ===")
        print(f"\nTotal de registros: {len(resultado)}")
        
        registros_con_validador = (resultado['nombre_validador'] != 'ALERTA VALIDADOR NO ENCONTRADO').sum()
        registros_sin_validador = (resultado['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
        
        print(f"Registros con validador identificado: {registros_con_validador}")
        print(f"Registros con ALERTA: {registros_sin_validador}")
        print(f"Porcentaje con validador: {(registros_con_validador / len(resultado) * 100):.2f}%")
        
        if registros_sin_validador > 0:
            print(f"\n🚨 ATENCIÓN: {registros_sin_validador} registros tienen 'ALERTA VALIDADOR NO ENCONTRADO'")
            print("   Estos registros requieren revisión manual.")
        
        print("\n📋 Top 10 validadores por frecuencia:")
        top_validadores = resultado[resultado['nombre_validador'] != 'ALERTA VALIDADOR NO ENCONTRADO']['nombre_validador'].value_counts().head(10)
        for i, (nombre, cantidad) in enumerate(top_validadores.items(), 1):
            porcentaje = (cantidad / len(resultado)) * 100
            print(f"   {i:2d}. {nombre}: {cantidad} registros ({porcentaje:.1f}%)")
        
        print("\n✅ Proceso completado. Revisa el archivo de salida para ver todos los datos.")
