#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de ejemplo actualizado para PyVPP con la nueva librería HDA

Este script muestra cómo usar PyVPP con la versión actualizada de la librería HDA.
"""

from pyvpp import wekeo_download, create_hdarc, delete_hdarc, clean_old_hdarc

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Tus credenciales de WEkEO (obténlas en https://www.wekeo.eu/)
WEKEO_USER = "tu_usuario_aqui"
WEKEO_PASSWORD = "tu_contraseña_aqui"

# Configuración del área de estudio
# Puedes usar:
# 1. Un DEIMS ID: "deimsid:https://deims.org/..."
# 2. Ruta a un shapefile: "/path/to/tu/shapefile.shp"
AREA_DE_ESTUDIO = "deimsid:https://deims.org/bcbc866c-3f4f-47a8-bbbc-0a93df6de7b2"

# Dataset a descargar
# Opciones: 'VPP_Index', 'VPP_ST', 'VPP_Pheno', 'SLSTR'
DATASET = 'VPP_Pheno'

# Rango de fechas (formato: 'YYYY-MM-DD')
FECHA_INICIO = '2020-01-01'
FECHA_FIN = '2020-12-31'

# Productos a descargar
# Para VPP_Pheno: 'SOSD', 'MAXD', 'EOSD', 'SOSV', 'MAXV', 'EOSV', 'LENGTH', 
#                 'AMPL', 'LSLOPE', 'RSLOPE', 'SPROD', 'TPROD'
# Para VPP_Index: 'LAI', 'FAPAR', 'FCOVER', 'NDVI'
# Para VPP_ST: 'PPI', 'QFLAG'
PRODUCTOS = ['SOSD', 'MAXD', 'EOSD']

# =============================================================================
# OPCIÓN 1: USAR ARCHIVO .hdarc (Recomendado para uso local)
# =============================================================================

def ejemplo_con_hdarc():
    """
    Ejemplo usando archivo .hdarc para almacenar credenciales.
    Recomendado para uso en tu ordenador personal.
    """
    print("\n" + "="*60)
    print("EJEMPLO 1: Usando archivo .hdarc")
    print("="*60 + "\n")
    
    # Limpiar cualquier archivo .hdarc antiguo
    clean_old_hdarc()
    
    # Crear archivo .hdarc con credenciales
    create_hdarc(WEKEO_USER, WEKEO_PASSWORD)
    
    try:
        # Inicializar descargador (leerá credenciales de .hdarc)
        downloader = wekeo_download(
            dataset=DATASET,
            shape=AREA_DE_ESTUDIO,
            dates=[FECHA_INICIO, FECHA_FIN],
            products=PRODUCTOS
        )
        
        # Ejecutar proceso completo
        downloader.run()
        
        print("\n✓ Descarga completada con éxito!")
        print(f"Los archivos están en: {downloader.pyhda}")
        
    except Exception as e:
        print(f"\n✗ Error durante la descarga: {e}")
        import traceback
        traceback.print_exc()

# =============================================================================
# OPCIÓN 2: PASAR CREDENCIALES DIRECTAMENTE (Recomendado para entornos compartidos)
# =============================================================================

def ejemplo_sin_hdarc():
    """
    Ejemplo pasando credenciales directamente sin crear archivo .hdarc.
    Recomendado para Jupyter notebooks o entornos compartidos.
    """
    print("\n" + "="*60)
    print("EJEMPLO 2: Pasando credenciales directamente")
    print("="*60 + "\n")
    
    try:
        # Inicializar descargador con credenciales
        downloader = wekeo_download(
            dataset=DATASET,
            shape=AREA_DE_ESTUDIO,
            dates=[FECHA_INICIO, FECHA_FIN],
            products=PRODUCTOS,
            user=WEKEO_USER,
            password=WEKEO_PASSWORD
        )
        
        # Ejecutar proceso completo
        downloader.run()
        
        print("\n✓ Descarga completada con éxito!")
        print(f"Los archivos están en: {downloader.pyhda}")
        
    except Exception as e:
        print(f"\n✗ Error durante la descarga: {e}")
        import traceback
        traceback.print_exc()

# =============================================================================
# OPCIÓN 3: PROCESO PASO A PASO
# =============================================================================

def ejemplo_paso_a_paso():
    """
    Ejemplo ejecutando el proceso paso a paso.
    Útil para debugging o control granular.
    """
    print("\n" + "="*60)
    print("EJEMPLO 3: Proceso paso a paso")
    print("="*60 + "\n")
    
    try:
        # Inicializar
        downloader = wekeo_download(
            dataset=DATASET,
            shape=AREA_DE_ESTUDIO,
            dates=[FECHA_INICIO, FECHA_FIN],
            products=PRODUCTOS,
            user=WEKEO_USER,
            password=WEKEO_PASSWORD
        )
        
        # Paso 1: Descargar tiles
        print("\n--- PASO 1: Descargando tiles ---")
        downloader.download()
        
        # Paso 2: Crear mosaicos y recortar
        print("\n--- PASO 2: Creando mosaicos y recortando ---")
        downloader.mosaic_and_clip()
        
        # Paso 3: Limpiar archivos intermedios
        print("\n--- PASO 3: Limpiando archivos intermedios ---")
        downloader.clean()
        
        print("\n✓ Proceso completado con éxito!")
        print(f"Los archivos finales están en: {downloader.pyhda}")
        
    except Exception as e:
        print(f"\n✗ Error durante el proceso: {e}")
        import traceback
        traceback.print_exc()

# =============================================================================
# OPCIÓN 4: PARA JUPYTER/DATALAB (con limpieza de credenciales)
# =============================================================================

def ejemplo_jupyter_seguro():
    """
    Ejemplo seguro para Jupyter notebooks o entornos compartidos.
    Crea y elimina el archivo .hdarc automáticamente.
    """
    print("\n" + "="*60)
    print("EJEMPLO 4: Jupyter/Datalab con limpieza automática")
    print("="*60 + "\n")
    
    # Crear credenciales temporales
    create_hdarc(WEKEO_USER, WEKEO_PASSWORD)
    
    try:
        # Ejecutar descarga
        downloader = wekeo_download(
            dataset=DATASET,
            shape=AREA_DE_ESTUDIO,
            dates=[FECHA_INICIO, FECHA_FIN],
            products=PRODUCTOS
        )
        downloader.run()
        
        print("\n✓ Descarga completada con éxito!")
        print(f"Los archivos están en: {downloader.pyhda}")
        
    finally:
        # Siempre limpiar credenciales al terminar
        print("\nLimpiando credenciales...")
        delete_hdarc()

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    """
    Función principal - Elige qué ejemplo ejecutar.
    """
    print("\n" + "="*60)
    print("EJEMPLOS DE USO DE PyVPP ACTUALIZADO")
    print("="*60)
    
    # Verificar que las credenciales no sean las de ejemplo
    if WEKEO_USER == "tu_usuario_aqui" or WEKEO_PASSWORD == "tu_contraseña_aqui":
        print("\n⚠ AVISO: Debes configurar tus credenciales de WEkEO primero!")
        print("   Edita las variables WEKEO_USER y WEKEO_PASSWORD en este script.")
        return
    
    # Mostrar menú
    print("\nSelecciona el ejemplo a ejecutar:")
    print("1. Usar archivo .hdarc (recomendado para uso local)")
    print("2. Pasar credenciales directamente")
    print("3. Proceso paso a paso")
    print("4. Jupyter/Datalab con limpieza automática de credenciales")
    print("0. Salir")
    
    opcion = input("\nOpción: ").strip()
    
    if opcion == "1":
        ejemplo_con_hdarc()
    elif opcion == "2":
        ejemplo_sin_hdarc()
    elif opcion == "3":
        ejemplo_paso_a_paso()
    elif opcion == "4":
        ejemplo_jupyter_seguro()
    elif opcion == "0":
        print("Saliendo...")
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main()
