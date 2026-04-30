import streamlit as st
import pandas as pd

# Configuración de la interfaz
st.set_page_config(
    page_title="Carga y Consulta Agrícola",
    page_icon="🚜",
    layout="wide"
)

def main():
    st.title("🚜 Analizador de Producción Agrícola")
    st.markdown("""
    Esta aplicación permite cargar un archivo de Excel con datos de producción 
    y realizar consultas filtradas por departamento y cultivo.
    """)

    # --- SECCIÓN DE CARGA DE ARCHIVO ---
    st.sidebar.header("Configuración")
    archivo_subido = st.sidebar.file_uploader(
        "Carga tu archivo Excel (.xlsx)", 
        type=["xlsx"]
    )

    if archivo_subido is not None:
        try:
            # Cargamos el archivo una vez que el usuario lo sube
            # No usamos cache aquí directamente para permitir que el usuario cambie el archivo si lo desea
            df = pd.read_excel(archivo_subido)
            
            st.success("✅ Archivo cargado correctamente")
            
            # --- SECCIÓN DE FILTROS ---
            st.subheader("🔍 Parámetros de Búsqueda")
            col1, col2 = st.columns(2)
            
            # Obtenemos listas únicas para facilitar la selección (opcional)
            # O mantenemos el input de texto como pediste originalmente:
            with col1:
                depto_input = st.text_input("Departamento (ej. Antioquia, Vichada):").strip()
            with col2:
                cultivo_input = st.text_input("Cultivo (ej. Aguacate, Yuca):").strip()

            if depto_input and cultivo_input:
                # Verificamos que las columnas necesarias existan
                columnas_requeridas = ['Departamento', 'Cultivo']
                if all(col in df.columns for col in columnas_requeridas):
                    
                    # Filtro de datos
                    filtro = (df['Departamento'].str.contains(depto_input, case=False, na=False)) & \
                             (df['Cultivo'].str.contains(cultivo_input, case=False, na=False))
                    
                    df_filtrado = df[filtro].copy()

                    if df_filtrado.empty:
                        st.warning(f"No se encontraron datos para '{cultivo_input}' en '{depto_input}'.")
                    else:
                        # Procesamiento de métricas
                        columnas_metricas = ['Área sembrada (ha)', 'Área cosechada (ha)', 'Producción (t)']
                        
                        # Limpieza de datos numéricos
                        for col in columnas_metricas:
                            if col in df_filtrado.columns:
                                df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')

                        # 1. Resumen por Año
                        if 'Año' in df_filtrado.columns:
                            st.subheader(f"📊 Desempeño Anual: {cultivo_input} en {depto_input}")
                            resumen_anual = df_filtrado.groupby('Año')[
                                [c for c in columnas_metricas if c in df_filtrado.columns]
                            ].sum().reset_index()
                            
                            st.dataframe(resumen_anual, use_container_width=True, hide_index=True)

                        # 2. Detalle Municipal
                        with st.expander("Ver detalle completo por municipio"):
                            columnas_detalle = ['Año', 'Municipio', 'Cultivo', 'Área sembrada (ha)',
                                                'Área cosechada (ha)', 'Producción (t)', 'Rendimiento (t/ha)']
                            columnas_presentes = [c for c in columnas_detalle if c in df_filtrado.columns]
                            st.dataframe(df_filtrado[columnas_presentes], use_container_width=True, hide_index=True)
                else:
                    st.error("El archivo cargado no tiene las columnas 'Departamento' y 'Cultivo'.")
            
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        # Mensaje inicial cuando no hay archivo
        st.info("Por favor, sube un archivo Excel desde el panel lateral para comenzar.")
        
        # Opcional: Mostrar una imagen de ejemplo o instrucciones
        st.markdown("""
        **Instrucciones:**
        1. Prepara tu archivo Excel (.xlsx).
        2. Asegúrate de que contenga las columnas: *Año, Departamento, Municipio, Cultivo, Área sembrada (ha), Área cosechada (ha), Producción (t)*.
        3. Arrástralo al área de carga a la izquierda.
        """)

if __name__ == "__main__":
    main()
