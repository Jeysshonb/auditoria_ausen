import pandas as pd
import os
from pathlib import Path

# Rutas de entrada
ruta_excel = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_planos\Reporte 45_082025_26082025 ausentismo.XLSX"
ruta_csv = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida\relacion_laboral_con_validaciones.csv"

# Ruta de salida
ruta_salida = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida"
nombre_archivo_salida = "super_merge_ausentismos.csv"

# Valores para filtrar
valores_filtro = [
    'Enf Gral SOAT',
    'Inc. Accidente de Trabajo',
    'Inca. Enfer Gral Integral',
    'Inca. Enfermedad  General',
    'Prorroga Enf Gral SOAT',
    'Prorroga Inc. Accid. Trab',
    'Prorroga Inca/Enfer Gene',
    'Incapa.fuera de turno'
]

# Paso 1: Leer el archivo Excel
print("Leyendo archivo Excel...")
df_excel = pd.read_excel(ruta_excel)
print(f"Registros en Excel: {len(df_excel)}")

# Paso 2: FILTRAR EL EXCEL por 'Txt.cl.pres./ab.' ANTES del merge
print("\nFiltrando Excel por 'Txt.cl.pres./ab.'...")
if 'Txt.cl.pres./ab.' in df_excel.columns:
    df_excel = df_excel[df_excel['Txt.cl.pres./ab.'].isin(valores_filtro)].copy()
    print(f"Registros en Excel después del filtro: {len(df_excel)}")
else:
    print("⚠️  Columna 'Txt.cl.pres./ab.' no encontrada en Excel")

# Paso 3: Leer el archivo CSV
print("\nLeyendo archivo CSV...")
df_csv = pd.read_csv(ruta_csv)
print(f"Registros en CSV: {len(df_csv)}")

# Paso 4: FILTRAR EL CSV por 'external_name_label' ANTES del merge
print("\nFiltrando CSV por 'external_name_label'...")
if 'external_name_label' in df_csv.columns:
    df_csv = df_csv[df_csv['external_name_label'].isin(valores_filtro)].copy()
    print(f"Registros en CSV después del filtro: {len(df_csv)}")
else:
    print("⚠️  Columna 'external_name_label' no encontrada en CSV")

# Paso 5: Preparar las columnas para el SUPER MERGE
print("\nPreparando columnas para el SUPER MERGE...")

# Normalizar ID de personal
df_excel['Número de personal'] = df_excel['Número de personal'].astype(str).str.strip()
df_csv['id_personal'] = df_csv['id_personal'].astype(str).str.strip()

# Convertir fechas en formato DÍA/MES/AÑO (ejemplo: 3/02/2025)
print("Convirtiendo fechas (formato: día/mes/año)...")

# Para Excel - formato día/mes/año
df_excel['Inicio de validez'] = pd.to_datetime(df_excel['Inicio de validez'], format='%d/%m/%Y', errors='coerce')
df_excel['Fin de validez'] = pd.to_datetime(df_excel['Fin de validez'], format='%d/%m/%Y', errors='coerce')

# Para CSV - formato día/mes/año
df_csv['start_date'] = pd.to_datetime(df_csv['start_date'], format='%d/%m/%Y', errors='coerce')
df_csv['end_date'] = pd.to_datetime(df_csv['end_date'], format='%d/%m/%Y', errors='coerce')

# Normalizar fechas a solo fecha (sin hora) para comparación exacta
df_excel['Inicio de validez'] = df_excel['Inicio de validez'].dt.normalize()
df_excel['Fin de validez'] = df_excel['Fin de validez'].dt.normalize()
df_csv['start_date'] = df_csv['start_date'].dt.normalize()
df_csv['end_date'] = df_csv['end_date'].dt.normalize()

# Mostrar ejemplos de datos antes del merge
print("\n📋 Ejemplo de datos Excel:")
print(df_excel[['Número de personal', 'Inicio de validez', 'Fin de validez']].head(3))
print("\n📋 Ejemplo de datos CSV:")
print(df_csv[['id_personal', 'start_date', 'end_date']].head(3))

# Paso 6: SUPER MERGE usando las 3 columnas
print("\nRealizando SUPER MERGE con 3 columnas...")
df_merged = pd.merge(
    df_csv,
    df_excel,
    left_on=['id_personal', 'start_date', 'end_date'],
    right_on=['Número de personal', 'Inicio de validez', 'Fin de validez'],
    how='inner'
)

print(f"Registros después del SUPER MERGE: {len(df_merged)}")

# Eliminar columnas duplicadas del merge
columnas_duplicadas = ['Número de personal', 'Inicio de validez', 'Fin de validez']
for col in columnas_duplicadas:
    if col in df_merged.columns:
        df_merged = df_merged.drop(columns=[col])

# Paso 7: Eliminar filas vacías
print("\nEliminando filas vacías...")
df_final = df_merged.dropna(how='all')
print(f"Registros después de eliminar vacíos: {len(df_final)}")

# Paso 8: Guardar el resultado
print("\nGuardando archivo de salida...")
ruta_completa_salida = os.path.join(ruta_salida, nombre_archivo_salida)
df_final.to_csv(ruta_completa_salida, index=False, encoding='utf-8-sig')

# Paso 9: Mostrar estadísticas
print("\n" + "="*60)
print("✓ PROCESO COMPLETADO EXITOSAMENTE!")
print("="*60)
print(f"\n📊 ESTADÍSTICAS DEL PROCESO:")
print(f"   • Registros finales con MATCH: {len(df_final):,}")
print(f"\n📁 Archivo guardado en:")
print(f"   {ruta_completa_salida}")
print(f"\n📋 Total de columnas: {len(df_final.columns)}")
print("="*60)
