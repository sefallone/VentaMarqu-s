import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="POS Pastelería", layout="wide")

# --- BASE DE DATOS SIMULADA (puedes reemplazar con SQLite/CSV real) ---
if "inventario" not in st.session_state:
    st.session_state.inventario = {
        "Pastelería": {
            "Pastel de Chocolate (porción)": {"precio": 45, "stock": 20},
            "Pastel de Vainilla (porción)": {"precio": 40, "stock": 15},
            "Cheesecake (porción)": {"precio": 50, "stock": 10},
        },
        "Hojaldre": {
            "Empanada de Pollo": {"precio": 25, "stock": 30},
            "Empanada de Carne": {"precio": 25, "stock": 30},
            "Volován de Queso": {"precio": 30, "stock": 20},
        },
        "Bebidas": {
            "Café Americano": {"precio": 20, "stock": 50},
            "Café Capuchino": {"precio": 30, "stock": 40},
            "Jugo de Naranja": {"precio": 25, "stock": 25},
        }
    }

if "ventas" not in st.session_state:
    st.session_state.ventas = []

if "carrito" not in st.session_state:
    st.session_state.carrito = {}

# --- FUNCIONES ---
def guardar_venta(carrito, total):
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.ventas.append({
        "fecha": fecha,
        "productos": carrito,
        "total": total,
    })
    # Actualizar inventario
    for producto, datos in carrito.items():
        for categoria in st.session_state.inventario.values():
            if producto in categoria:
                categoria[producto]["stock"] -= datos["cantidad"]
    st.session_state.carrito = {}  # Reiniciar carrito

def mostrar_graficos():
    if not st.session_state.ventas:
        st.warning("No hay datos de ventas aún.")
        return
    
    # Convertir ventas a DataFrame
    df_ventas = pd.DataFrame(st.session_state.ventas)
    df_ventas["fecha"] = pd.to_datetime(df_ventas["fecha"])
    
    # Gráfico 1: Ventas por día
    st.subheader("📈 Ventas por día")
    df_diario = df_ventas.resample('D', on='fecha').sum(numeric_only=True).reset_index()
    fig1 = px.line(df_diario, x="fecha", y="total", title="Total de Ventas Diarias")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico 2: Productos más vendidos
    st.subheader("🍰 Productos más vendidos")
    productos_vendidos = []
    for venta in st.session_state.ventas:
        for producto, datos in venta["productos"].items():
            productos_vendidos.append({"producto": producto, "cantidad": datos["cantidad"]})
    
    if productos_vendidos:
        df_productos = pd.DataFrame(productos_vendidos)
        df_top = df_productos.groupby("producto").sum().sort_values("cantidad", ascending=False).head(5)
        fig2 = px.bar(df_top, x=df_top.index, y="cantidad", title="Top 5 Productos")
        st.plotly_chart(fig2, use_container_width=True)

# --- INTERFAZ PRINCIPAL ---
st.title("🍰 POS - Pastelería Deliciosa")

# Sidebar: Carrito y Total
st.sidebar.title("🛒 Carrito")
for producto, datos in st.session_state.carrito.items():
    st.sidebar.write(f"{producto} x {datos['cantidad']} = ${datos['subtotal']}")

total = sum(datos["subtotal"] for datos in st.session_state.carrito.values())
st.sidebar.markdown(f"**Total: ${total}**")

if st.sidebar.button("✅ Finalizar Venta", type="primary"):
    if total == 0:
        st.sidebar.error("Agrega productos al carrito")
    else:
        guardar_venta(st.session_state.carrito.copy(), total)
        st.sidebar.success("Venta registrada!")
        st.experimental_rerun()  # Refrescar la página

# Mostrar Productos
for categoria, items in st.session_state.inventario.items():
    st.subheader(categoria)
    cols = st.columns(3)
    
    for i, (producto, datos) in enumerate(items.items()):
        with cols[i % 3]:
            st.write(f"**{producto}**")
            st.write(f"Precio: ${datos['precio']} | Stock: {datos['stock']}")
            cantidad = st.number_input(
                f"Cantidad de {producto}",
                min_value=0,
                max_value=datos["stock"],
                key=f"cant_{producto}",
            )
            
            if cantidad > 0:
                st.session_state.carrito[producto] = {
                    "cantidad": cantidad,
                    "precio": datos["precio"],
                    "subtotal": cantidad * datos["precio"],
                }

# Pestañas para Historial y Gráficos
tab1, tab2, tab3 = st.tabs(["Inventario", "Historial de Ventas", "Gráficos"])

with tab1:
    st.subheader("📦 Inventario Actual")
    for categoria, items in st.session_state.inventario.items():
        st.write(f"### {categoria}")
        df = pd.DataFrame(items).T.reset_index()
        df.columns = ["Producto", "Precio", "Stock"]
        st.dataframe(df, hide_index=True)

with tab2:
    st.subheader("📋 Historial de Ventas")
    if st.session_state.ventas:
        df_ventas = pd.DataFrame(st.session_state.ventas)
        st.dataframe(df_ventas, hide_index=True)
    else:
        st.info("No hay ventas registradas aún.")

with tab3:
    mostrar_graficos()