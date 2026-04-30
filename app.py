import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(
    page_title="Consulta Agrícola",
    page_icon="🌾",
    layout="wide"
)

# El uso de cache evita que el Excel se recargue en cada interacción del usuario
@st.cache_data
def cargar_datos():
    archivo_excel = '20250617_BaseAgricola20192024.xlsx'
    # Cargamos el archivo Excel (requiere openpyxl)
    df = pd.read_excel(archivo_excel)
    return df

def main():
    st.title("🌾 Consulta de Desempeño Agrícola (2019 - 2024)")
    st.markdown("---")
    
    # Intentamos cargar los datos
    try:
        with st.spinner("Cargando la base de datos de Excel... (esto puede tomar unos segundos)"):
            df = cargar_datos()
    except FileNotFoundError:
        st.error(f"**Error:** No se encontró el archivo '20250617_BaseAgricola20192024.xlsx'.")
        st.info("Asegúrate de haber subido el archivo Excel al repositorio de GitHub en la misma carpeta que este script.")
        return

    # Usamos columnas para organizar mejor los inputs
    col1, col2 = st.columns(2)
    
    with col1:
        depto_input = st.text_input("1. Ingresa el nombre del Departamento (ej. Antioquia, Vichada):").strip()
    with col2:
        cultivo_input = st.text_input("2. Ingresa el nombre del Cultivo (ej. Aguacate, Yuca):").strip()

    # Solo ejecutamos la búsqueda si el usuario ha ingresado ambos datos
    if depto_input and cultivo_input:
        
        # Filtramos ignorando mayúsculas y minúsculas (case=False)
        filtro = (df['Departamento'].str.contains(depto_input, case=False, na=False)) & \
                 (df['Cultivo'].str.contains(cultivo_input, case=False, na=False))
        
        df_filtrado = df[filtro].copy()

        if df_filtrado.empty:
            st.warning("No se encontraron registros que coincidan con tu búsqueda.")
        else:
            # Variables extraídas
            columnas_metricas = [
                'Área sembrada (ha)',
                'Área cosechada (ha)',
                'Producción (t)'
            ]
            
            # Nos aseguramos de que las métricas sean valores numéricos
            for col in columnas_metricas:
                if col in df_filtrado.columns:
                    df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')
            
            st.success(f"✅ Resultados encontrados para **'{cultivo_input}'** en el departamento de **'{depto_input}'**")
            
            # 1. Agrupar la información por Año a nivel departamental
            if 'Año' in df_filtrado.columns:
                resumen_anual = df_filtrado.groupby('Año')[columnas_metricas].sum().reset_index()
                
                st.subheader("📊 Resumen Departamental por Año")
                # Mostramos la tabla formateada
                st.dataframe(resumen_anual, use_container_width=True, hide_index=True)
                
            st.markdown("---")
            
            # 2. Ofrecer la opción de ver los detalles exactos con un Checkbox
            ver_detalle = st.checkbox("¿Deseas ver el detalle desglosado por Municipio y Periodo?")
            
            if ver_detalle:
                columnas_detalle = ['Año', 'Municipio', 'Cultivo', 'Área sembrada (ha)',
                                    'Área cosechada (ha)', 'Producción (t)', 'Rendimiento (t/ha)']
                
                # Filtramos solo las columnas que realmente existen en el archivo
                columnas_presentes = [col for col in columnas_detalle if col in df_filtrado.columns]
                
                st.subheader("📍 Detalle a nivel Municipal")
                st.dataframe(df_filtrado[columnas_presentes], use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()