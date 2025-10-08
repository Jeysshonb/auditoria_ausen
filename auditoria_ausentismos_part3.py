import pandas as pd
import os

# ===== CONFIGURACIÓN DE RUTAS =====
ruta_archivo_base = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida\ausentismos_merged_completo.csv"
ruta_cie10 = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_planos\CIE 10 - AJUSTADO - NÓMINA.xlsx"
directorio_salida = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida"
archivo_salida = "ausentismos_con_cie10.csv"
ruta_completa_salida = os.path.join(directorio_salida, archivo_salida)


def merge_cie10():
    """
    Función principal que hace el merge con la tabla CIE 10
    """
    print("=" * 80)
    print("=== MERGE CON CIE 10 ===")
    print("=== Agregando información de diagnósticos ===")
    print("=" * 80)
    
    try:
        # PASO 1: Leer archivo base (ausentismos_merged_completo)
        print("\n📂 PASO 1: Leyendo archivo base de ausentismos...")
        print(f"   Ruta: {ruta_archivo_base}")
        
        df_base = pd.read_csv(ruta_archivo_base, encoding='utf-8-sig', dtype=str)
        
        print(f"   ✅ Archivo leído exitosamente")
        print(f"   📊 Dimensiones: {df_base.shape[0]} filas × {df_base.shape[1]} columnas")
        
        # Verificar que existe la columna de merge
        if 'descripcion_general_external_code' not in df_base.columns:
            print(f"\n   ❌ ERROR: No se encontró la columna 'descripcion_general_external_code'")
            print(f"   💡 Columnas disponibles: {list(df_base.columns)[:10]}...")
            return None
        
        print(f"   🔑 Columna de merge encontrada: descripcion_general_external_code")
        print(f"   📋 Códigos únicos: {df_base['descripcion_general_external_code'].nunique()}")
        print(f"   📋 Ejemplo de código: {df_base['descripcion_general_external_code'].iloc[0]}")
        
        # PASO 2: Leer archivo CIE 10
        print("\n📂 PASO 2: Leyendo tabla CIE 10...")
        print(f"   Ruta: {ruta_cie10}")
        
        df_cie10 = pd.read_excel(ruta_cie10, dtype=str)
        
        print(f"   ✅ Archivo leído exitosamente")
        print(f"   📊 Dimensiones: {df_cie10.shape[0]} filas × {df_cie10.shape[1]} columnas")
        print(f"   📋 Columnas encontradas: {list(df_cie10.columns)}")
        
        # Verificar columnas necesarias
        columnas_requeridas = ['Código', 'Descripción', 'TIPO']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df_cie10.columns]
        
        if columnas_faltantes:
            print(f"\n   ⚠️  ADVERTENCIA: Faltan columnas en CIE 10:")
            for col in columnas_faltantes:
                print(f"      • {col}")
            print(f"   💡 Se intentará continuar con las columnas disponibles")
        else:
            print(f"   ✅ Todas las columnas requeridas están presentes")
        
        # Mostrar información de la columna Código
        if 'Código' in df_cie10.columns:
            print(f"\n   📋 Información de códigos CIE 10:")
            print(f"      • Total de códigos: {len(df_cie10)}")
            print(f"      • Códigos únicos: {df_cie10['Código'].nunique()}")
            print(f"      • Ejemplo de código: {df_cie10['Código'].iloc[0]}")
        
        # Seleccionar solo las columnas que necesitamos del CIE 10
        columnas_a_agregar = [col for col in columnas_requeridas if col in df_cie10.columns]
        if 'Código' in df_cie10.columns:
            columnas_cie10_merge = ['Código'] + [col for col in columnas_a_agregar if col != 'Código']
        else:
            print(f"\n   ❌ ERROR: No se encontró la columna 'Código' en CIE 10")
            return None
        
        df_cie10_subset = df_cie10[columnas_cie10_merge].copy()
        
        print(f"\n   📋 Columnas que se agregarán desde CIE 10:")
        for col in columnas_cie10_merge:
            print(f"      • {col}")
        
        # PASO 3: Analizar coincidencias antes del merge
        print("\n🔍 PASO 3: Analizando coincidencias antes del merge...")
        
        # Limpiar espacios en blanco de los códigos
        print(f"   🧹 Limpiando espacios en blanco de los códigos...")
        df_base['descripcion_general_external_code_clean'] = df_base['descripcion_general_external_code'].str.strip().str.upper()
        df_cie10_subset['Código_clean'] = df_cie10_subset['Código'].str.strip().str.upper()
        
        codigos_base = set(df_base['descripcion_general_external_code_clean'].dropna())
        codigos_cie10 = set(df_cie10_subset['Código_clean'].dropna())
        
        coincidencias = codigos_base.intersection(codigos_cie10)
        solo_base = codigos_base - codigos_cie10
        solo_cie10 = codigos_cie10 - codigos_base
        
        print(f"\n   📊 Estadísticas de códigos:")
        print(f"   • Códigos únicos en archivo base: {len(codigos_base)}")
        print(f"   • Códigos únicos en CIE 10: {len(codigos_cie10)}")
        print(f"   • Códigos que coinciden: {len(coincidencias)}")
        print(f"   • Solo en archivo base: {len(solo_base)}")
        print(f"   • Solo en CIE 10: {len(solo_cie10)}")
        
        if len(coincidencias) > 0:
            porcentaje_match = (len(coincidencias) / len(codigos_base)) * 100
            print(f"\n   📈 Porcentaje de coincidencia: {porcentaje_match:.1f}%")
        
        # Mostrar códigos que no coinciden
        if len(solo_base) > 0:
            print(f"\n   ⚠️  Códigos en archivo base SIN coincidencia en CIE 10 (primeros 10):")
            for i, codigo in enumerate(list(solo_base)[:10], 1):
                # Contar cuántos registros tienen ese código
                count = (df_base['descripcion_general_external_code_clean'] == codigo).sum()
                print(f"      {i:2d}. {codigo} ({count} registros)")
        
        # PASO 4: Realizar el merge
        print("\n🔗 PASO 4: Realizando merge con CIE 10...")
        print("   📌 Tipo de merge: LEFT (mantiene todos los registros del archivo base)")
        print("   📌 Columnas de merge: descripcion_general_external_code ← → Código")
        
        df_merged = pd.merge(
            df_base,
            df_cie10_subset,
            left_on='descripcion_general_external_code_clean',
            right_on='Código_clean',
            how='left',
            suffixes=('', '_cie10')
        )
        
        # Renombrar columnas para que sean más claras
        renombrado = {
            'Código': 'cie10_codigo',
            'Descripción': 'cie10_descripcion',
            'TIPO': 'cie10_tipo'
        }
        
        columnas_renombrar = {col: renombrado.get(col, col) for col in df_merged.columns if col in renombrado}
        df_merged = df_merged.rename(columns=columnas_renombrar)
        
        # Eliminar columnas temporales de limpieza
        df_merged = df_merged.drop(['descripcion_general_external_code_clean'], axis=1)
        if 'Código_clean' in df_merged.columns:
            df_merged = df_merged.drop(['Código_clean'], axis=1)
        
        print(f"   ✅ Merge completado")
        print(f"   📊 Dimensiones del resultado: {df_merged.shape[0]} filas × {df_merged.shape[1]} columnas")
        
        # PASO 5: Analizar resultados del merge
        print("\n📈 PASO 5: Analizando resultados del merge...")
        
        # Contar registros con y sin información de CIE 10
        if 'cie10_codigo' in df_merged.columns:
            registros_con_cie10 = df_merged['cie10_codigo'].notna().sum()
            registros_sin_cie10 = df_merged['cie10_codigo'].isna().sum()
            
            print(f"\n   📊 Resultados del merge:")
            print(f"   • Total de registros: {len(df_merged)}")
            print(f"   • Registros con información CIE 10: {registros_con_cie10}")
            print(f"   • Registros sin información CIE 10: {registros_sin_cie10}")
            
            if len(df_merged) > 0:
                porcentaje_con_cie10 = (registros_con_cie10 / len(df_merged)) * 100
                print(f"   • Porcentaje con CIE 10: {porcentaje_con_cie10:.1f}%")
            
            # Mostrar distribución de TIPO si existe
            if 'cie10_tipo' in df_merged.columns:
                print(f"\n   📊 Distribución por TIPO (CIE 10):")
                tipo_stats = df_merged['cie10_tipo'].value_counts().head(10)
                for tipo, count in tipo_stats.items():
                    if pd.notna(tipo):
                        porcentaje = (count / len(df_merged)) * 100
                        print(f"      • {tipo}: {count} registros ({porcentaje:.1f}%)")
        
        # PASO 6: Guardar archivo
        print("\n💾 PASO 6: Guardando archivo con CIE 10...")
        
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
            print(f"   📁 Directorio creado: {directorio_salida}")
        
        df_merged.to_csv(
            ruta_completa_salida,
            index=False,
            encoding='utf-8-sig',
            quoting=1,
            lineterminator='\n'
        )
        
        print(f"   ✅ Archivo guardado exitosamente")
        print(f"   📁 Ubicación: {ruta_completa_salida}")
        print(f"   📊 Registros guardados: {len(df_merged)}")
        
        # PASO 7: Resumen final
        print("\n" + "=" * 80)
        print("=== RESUMEN FINAL ===")
        print("=" * 80)
        
        print(f"\n📊 Estadísticas generales:")
        print(f"   • Total de registros: {len(df_merged)}")
        print(f"   • Total de columnas: {len(df_merged.columns)}")
        
        if 'cie10_codigo' in df_merged.columns:
            registros_con_cie10 = df_merged['cie10_codigo'].notna().sum()
            print(f"   • Registros con información CIE 10: {registros_con_cie10}")
        
        print(f"\n📋 Nuevas columnas agregadas desde CIE 10:")
        columnas_nuevas = [col for col in df_merged.columns if col.startswith('cie10_')]
        for i, col in enumerate(columnas_nuevas, 1):
            print(f"   {i}. {col}")
        
        print(f"\n📌 Vista previa del primer registro:")
        primera_fila = df_merged.iloc[0]
        
        # Mostrar columnas relevantes
        columnas_mostrar = [
            'id_personal',
            'nombre_completo',
            'descripcion_general_external_code',
            'cie10_codigo',
            'cie10_descripcion',
            'cie10_tipo'
        ]
        
        for col in columnas_mostrar:
            if col in df_merged.columns:
                valor = primera_fila[col]
                if pd.isna(valor):
                    valor = "[VACÍO]"
                elif isinstance(valor, str) and len(valor) > 60:
                    valor = valor[:60] + "..."
                print(f"   • {col}: {valor}")
        
        print("\n" + "=" * 80)
        print("✅ MERGE CON CIE 10 COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print(f"\n📁 Archivo disponible en: {ruta_completa_salida}")
        
        return df_merged
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: No se encontró uno de los archivos")
        print(f"   Verifica que los archivos existen:")
        print(f"   • {ruta_archivo_base}")
        print(f"   • {ruta_cie10}")
        return None
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def verificar_archivos():
    """
    Función para verificar que los archivos existen antes del merge
    """
    print("\n" + "=" * 80)
    print("=== VERIFICACIÓN DE ARCHIVOS ===")
    print("=" * 80)
    
    archivos = {
        "Archivo base (ausentismos)": ruta_archivo_base,
        "Tabla CIE 10": ruta_cie10
    }
    
    todos_existen = True
    
    for nombre, ruta in archivos.items():
        print(f"\n📂 Verificando {nombre}...")
        print(f"   Ruta: {ruta}")
        
        if os.path.exists(ruta):
            tamanio = os.path.getsize(ruta) / 1024  # Tamaño en KB
            print(f"   ✅ Archivo encontrado ({tamanio:.1f} KB)")
        else:
            print(f"   ❌ Archivo NO encontrado")
            todos_existen = False
    
    return todos_existen


if __name__ == "__main__":
    # Verificar que los archivos existen
    if verificar_archivos():
        # Ejecutar el merge directamente
        resultado = merge_cie10()
        
        if resultado is not None:
            print("\n🎉 ¡Merge con CIE 10 completado exitosamente!")
            print("   El archivo ahora incluye información de diagnósticos CIE 10")
        else:
            print("\n❌ El merge no se completó correctamente. Revisa los errores anteriores.")
    else:
        print("\n❌ No se puede continuar. Verifica las rutas de los archivos.")
