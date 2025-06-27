import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Configuración Firebase ---
if not firebase_admin._apps:
    firebase_config = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    }
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase"]["databaseURL"]})

# --- Funciones Firebase ---
def cargar_datos():
    ref = db.reference('/')
    datos = ref.get()
    if not datos:
        datos = {
            "inventario": {
                "Pastelería": {
                "Dulce Tres Leche (porción)": {"precio": 4.30, "stock": 0, "costo": 2.15},
                "Milhojas Arequipe (porción)": {"precio": 4.30, "stock": 0, "costo": 2.15},
                "Mousse de Chocolate (porción)": {"precio": 4.80, "stock": 0, "costo": 2.40},
                "Mousse de Parchita (porción)": {"precio": 3.70, "stock": 1, "costo": 1.85},
                "Ópera (porción)": {"precio": 3.70, "stock": 2 , "costo": 1.85},
                "Petit Fours (Mini Dulce)": {"precio": 0.80, "stock": 10, "costo": 0.40},
                "Profiterol (porción)": {"precio": 4.20, "stock": 0, "costo": 2.10},
                "Sacher (porción)": {"precio": 3, "stock": 0, "costo": 1.5},
                "Cheesecake Arequipe (porción)": {"precio": 5.40, "stock": 0, "costo": 2.70},
                "Cheesecake Fresa (porción)": {"precio": 5.40, "stock": 2, "costo": 2.70},
                "Cheesecake Chocolate (porción)": {"precio": 5.40, "stock": 2, "costo": 2.70},
                "Cheesecake Pistacho (porción)": {"precio": 5.40, "stock": 0, "costo": 2.70},
                "Selva Negra (porción)": {"precio": 4.30, "stock": 2, "costo": 2.65},
                "Tartaleta Limón (porción)": {"precio": 4.30, "stock": 0, "costo": 2.65},
                "Tartaleta Parchita (porción)": {"precio": 4.30, "stock": 2, "costo": 2.65},
                "Torta Imposible (porción)": {"precio": 2.50, "stock": 0, "costo": 1.25},
                "Torta Pan (porción)": {"precio": 2.80, "stock": 0, "costo": 1.40},
                "Brazo Gitano Limón (porción)": {"precio": 2.20, "stock": 0, "costo": 1.10},
                "Brazo Gitano Arequipe (porción)": {"precio": 2.20, "stock": 3, "costo": 1.10},
                "Brazo Gitano Chocolate (porción)": {"precio": 2.20, "stock": 2, "costo": 1.10}
            },
            "Hojaldre": {
                "Hojaldre de Pollo": {"precio": 3.50, "stock": 2, "costo": 1.75},
                "Hojaldre de Carne": {"precio": 3.00, "stock": 2, "costo": 1.50},
                "Hojaldre de Queso": {"precio": 3.00, "stock": 1, "costo": 1.50},
                "Hojaldre de Jamón": {"precio": 3.00, "stock": 1, "costo": 1.50},
                "Croissant de Pavo/ Queso Crema": {"precio": 3.50, "stock": 0, "costo": 1.75},
                "Cachito de Queso": {"precio": 3.00, "stock": 2, "costo": 1.50},
                "Cachito de Jamón": {"precio": 3.00, "stock": 2, "costo": 1.50},
                "Cachito de Pavo/Queso Crema": {"precio": 3.20, "stock": 1, "costo": 1.60},
                "Croissant": {"precio": 2.60, "stock": 2, "costo": 1.30}
                                
            },
            "Bebidas": {
                "Café Pequeño": {"precio": 1.30, "stock": 200, "costo": 0.65},
                "Café Grande": {"precio": 2.60, "stock": 200, "costo": 1.30},
                "Mocchaccino": {"precio": 3.00, "stock": 200, "costo": 1.50},
                "Cappuccino": {"precio": 3.00, "stock": 200, "costo": 1.50},
                "Chocolate Caliente": {"precio": 3.00, "stock": 200, "costo": 1.50},
                "Café Arte París": {"precio": 3.50, "stock": 200, "costo": 1.75},
                "Jugo Naranja": {"precio": 2.50, "stock": 200, "costo": 1.25},
                "Jugo Fresa": {"precio": 3, "stock": 200, "costo": 1.50},
                "Jugo Melocoton": {"precio": 3, "stock": 200, "costo": 1.50},
                "Jugo Guayaba": {"precio": 2.50, "stock": 200, "costo": 1.25},
                "Jugo Piña": {"precio": 2.50, "stock": 200, "costo": 1.25},
                "Jugo Lechoza": {"precio": 2.50, "stock": 200, "costo": 1.25},
                "Jugo Mora": {"precio": 3, "stock": 200, "costo": 1.50},
                "Agua Mineral": {"precio": 2, "stock": 8, "costo": 1},
                "Té caliente": {"precio": 2.00, "stock": 200, "costo": 1.00},
                "Malta Retornable": {"precio": 1.00, "stock": 11, "costo": 0.50},
                "Nestea": {"precio": 3.00, "stock": 200, "costo": 1.50},
                "Refresco Bomba": {"precio": 1.50, "stock": 200, "costo": 0.75},
                "Flor de Jamaica Frío": {"precio": 2.50, "stock": 200, "costo": 1.25},
                "Papelón con Limón": {"precio": 2.50, "stock": 200, "costo": 1.25}
            },
            "Dulces Secos": {
                "Mini Dulce Manzana": {"precio": 1.25, "stock": 8, "costo": 0.625},
                "Mini Croissant Chocolate": {"precio": 0.80, "stock": 2, "costo": 0.40},
                "Trio Mini Dulces": {"precio": 3.40, "stock": 0, "costo": 1.70},
                "Trio Mini Croissant": {"precio": 2.20, "stock": 0, "costo": 1.10},
                "Palmeras": {"precio": 3.20, "stock": 2, "costo": 1.60},
                "Panque Marmoleado": {"precio": 2.50, "stock": 0, "costo": 1.25},
                "Hojaldre de Manzana": {"precio": 4, "stock": 2, "costo": 2},
                "Galletas Arte París Chocolate": {"precio": 2.50, "stock": 5, "costo": 1.25},
                "Galletas Arte París Avena/Pasas": {"precio": 2.50, "stock": 5, "costo": 1.25},
                "Ambrosia Chocolate": {"precio": 1.40, "stock": 0, "costo": 0.70},
                "Ambrosia Frutas Confitadas": {"precio": 1.40, "stock": 0, "costo": 0.70},
                "Pasta Seca (100 grs)": {"precio": 2.50, "stock": 0, "costo": 1.25}
                }   
            },
            "ventas": [],
            "carritos": {}
        }
        ref.set(datos)
    return datos

def guardar_datos(datos):
    ref = db.reference('/')
    ref.set(datos)

# --- Interfaz Streamlit ---
def main():
    # Cargar datos al inicio
    if 'datos' not in st.session_state:
        st.session_state.datos = cargar_datos()
        st.session_state.inventario = st.session_state.datos["inventario"]
        st.session_state.ventas = st.session_state.datos["ventas"]
        st.session_state.carrito = {}

    # Menú principal
    st.sidebar.title("🍰 SweetBakery POS")
    opcion = st.sidebar.radio(
        "Menú",
        ["Punto de Venta", "Inventario", "Reportes"]
    )

    if opcion == "Punto de Venta":
        mostrar_punto_venta()
    elif opcion == "Inventario":
        mostrar_inventario()
    elif opcion == "Reportes":
        mostrar_reportes()

    # Guardar cambios si hay modificaciones
    if st.session_state.get('needs_save', False):
        st.session_state.datos = {
            "inventario": st.session_state.inventario,
            "ventas": st.session_state.ventas,
            "carritos": {}
        }
        guardar_datos(st.session_state.datos)
        st.session_state.needs_save = False

# --- Punto de Venta ---
def mostrar_punto_venta():
    st.header("🛒 Punto de Venta")
    
    # Búsqueda
    busqueda = st.text_input("🔍 Buscar producto por nombre")
    
    # Mostrar productos
    for categoria, productos in st.session_state.inventario.items():
        with st.expander(f"📁 {categoria}"):
            for producto, datos in productos.items():
                if busqueda.lower() in producto.lower():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{producto}** - ${datos['precio']:.2f} (Stock: {datos['stock']})")
                    with col2:
                        if st.button("➕", key=f"add_{producto}", disabled=datos['stock'] <= 0):
                            if producto in st.session_state.carrito:
                                st.session_state.carrito[producto]['cantidad'] += 1
                            else:
                                st.session_state.carrito[producto] = {
                                    'cantidad': 1,
                                    'precio': datos['precio'],
                                    'categoria': categoria
                                }
                            st.session_state.inventario[categoria][producto]['stock'] -= 1
                            st.session_state.needs_save = True
                            st.rerun()

    # Carrito
    if st.session_state.carrito:
        st.sidebar.header("📋 Factura")
        total = 0
        for producto, item in list(st.session_state.carrito.items()):
            subtotal = item['cantidad'] * item['precio']
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.write(f"{producto} x{item['cantidad']}")
            with col2:
                if st.button("❌", key=f"del_{producto}"):
                    st.session_state.inventario[item['categoria']][producto]['stock'] += item['cantidad']
                    del st.session_state.carrito[producto]
                    st.session_state.needs_save = True
                    st.rerun()
            total += subtotal
        
        st.sidebar.markdown(f"**Total: ${total:.2f}**")
        if st.sidebar.button("✅ Finalizar Venta", type="primary"):
            nueva_venta = {
                'fecha': datetime.now().isoformat(),
                'productos': st.session_state.carrito,
                'total': total,
                'metodo_pago': "Efectivo"
            }
            st.session_state.ventas.append(nueva_venta)
            st.session_state.carrito = {}
            st.session_state.needs_save = True
            st.sidebar.success("Venta registrada!")

# --- Gestión de Inventario ---
def mostrar_inventario():
    st.header("📦 Gestión de Inventario")
    
    # Editor de productos
    with st.form("nuevo_producto"):
        categoria = st.selectbox("Categoría", list(st.session_state.inventario.keys()))
        producto = st.text_input("Nombre del producto")
        precio = st.number_input("Precio", min_value=0.0, step=0.1, format="%.2f")
        stock = st.number_input("Stock", min_value=0, step=1)
        
        if st.form_submit_button("Guardar Producto"):
            if producto and categoria:
                if producto not in st.session_state.inventario[categoria]:
                    st.session_state.inventario[categoria][producto] = {
                        'precio': precio,
                        'stock': stock,
                        'costo': precio * 0.5  # Ajusta según necesidad
                    }
                    st.session_state.needs_save = True
                    st.success("¡Producto agregado!")
                else:
                    st.error("¡El producto ya existe!")
    
    # Tabla de inventario
    inventario_df = []
    for categoria, productos in st.session_state.inventario.items():
        for producto, datos in productos.items():
            inventario_df.append({
                "Categoría": categoria,
                "Producto": producto,
                "Precio": datos['precio'],
                "Stock": datos['stock'],
                "Costo": datos.get('costo', 0)
            })
    
    st.dataframe(
        pd.DataFrame(inventario_df),
        column_config={
            "Precio": st.column_config.NumberColumn(format="$%.2f"),
            "Costo": st.column_config.NumberColumn(format="$%.2f")
        },
        hide_index=True,
        use_container_width=True
    )

# --- Reportes Diarios ---
def mostrar_reportes():
    st.header("📊 Reportes Diarios")
    
    # Filtrar por fecha
    hoy = datetime.now().date()
    ventas_hoy = [v for v in st.session_state.ventas if datetime.fromisoformat(v['fecha']).date() == hoy]
    
    if not ventas_hoy:
        st.warning("No hay ventas hoy")
        return
    
    # Reporte por método de pago
    st.subheader("💳 Ventas por Método de Pago")
    df_metodos = pd.DataFrame(ventas_hoy).groupby('metodo_pago')['total'].agg(['sum', 'count']).reset_index()
    df_metodos.columns = ['Método', 'Total', 'Transacciones']
    st.dataframe(
        df_metodos,
        column_config={"Total": st.column_config.NumberColumn(format="$%.2f")},
        hide_index=True
    )
    
    # Reporte por producto
    st.subheader("🍰 Productos Vendidos")
    productos_vendidos = []
    for venta in ventas_hoy:
        for producto, datos in venta['productos'].items():
            productos_vendidos.append({
                'Producto': producto,
                'Cantidad': datos['cantidad'],
                'Total': datos['cantidad'] * datos['precio']
            })
    
    df_productos = pd.DataFrame(productos_vendidos).groupby('Producto').sum().reset_index()
    st.dataframe(
        df_productos,
        column_config={"Total": st.column_config.NumberColumn(format="$%.2f")},
        hide_index=True
    )

if __name__ == "__main__":
    main()
