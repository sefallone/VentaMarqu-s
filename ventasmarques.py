import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import pandas as pd
import threading
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Configuración Firebase ---
if not firebase_admin._apps:
    # Cargar credenciales desde secrets.toml
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
    firebase_admin.initialize_app(cred, {
        'databaseURL': st.secrets["firebase"]["databaseURL"]
    })

# --- Listeners en Tiempo Real ---
def setup_realtime_listeners():
    def inventory_listener(event):
        if event.data:
            st.session_state.inventario = event.data
            st.rerun()
    
    def sales_listener(event):
        if event.data:
            st.session_state.ventas = event.data
            st.rerun()
    
    # Configurar listeners
    db.reference('/inventario').listen(inventory_listener)
    db.reference('/ventas').listen(sales_listener)

# Iniciar listeners en un hilo separado
threading.Thread(target=setup_realtime_listeners, daemon=True).start()

# --- Funciones Principales ---
def cargar_datos_iniciales():
    return {
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
        "ventas": []
    }

def guardar_venta(venta):
    ref = db.reference('/ventas')
    ventas = ref.get() or []
    ventas.append(venta)
    ref.set(ventas)

def actualizar_inventario(inventario):
    db.reference('/inventario').set(inventario)

# --- Interfaz Streamlit ---
def main():
    # Inicializar datos
    if 'inventario' not in st.session_state:
        st.session_state.inventario = db.reference('/inventario').get() or cargar_datos_iniciales()["inventario"]
        st.session_state.ventas = db.reference('/ventas').get() or []
        st.session_state.carrito = {}
    
    # Menú principal
    st.sidebar.title("🍰 SweetBakery POS")
    opcion = st.sidebar.radio(
        "Menú",
        ["Punto de Venta", "Gestión de Inventario", "Reportes"]
    )

    if opcion == "Punto de Venta":
        mostrar_punto_venta()
    elif opcion == "Gestión de Inventario":
        mostrar_inventario()
    elif opcion == "Reportes":
        mostrar_reportes()

def mostrar_punto_venta():
    st.header("🛒 Punto de Venta")
    
    # Búsqueda de productos
    busqueda = st.text_input("🔍 Buscar producto por nombre", key="busqueda_venta")
    
    # Mostrar productos disponibles
    for categoria, productos in st.session_state.inventario.items():
        with st.expander(f"📁 {categoria}"):
            for producto, datos in productos.items():
                if busqueda.lower() in producto.lower():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{producto}** - ${datos['precio']:.2f} (Stock: {datos['stock']})")
                    with col2:
                        if st.button(f"➕", 
                                   key=f"add_{producto}",
                                   disabled=datos['stock'] <= 0):
                            if producto in st.session_state.carrito:
                                st.session_state.carrito[producto]['cantidad'] += 1
                            else:
                                st.session_state.carrito[producto] = {
                                    'cantidad': 1,
                                    'precio': datos['precio'],
                                    'categoria': categoria
                                }
                            # Actualizar stock localmente
                            st.session_state.inventario[categoria][producto]['stock'] -= 1
                            # Sincronizar con Firebase
                            actualizar_inventario(st.session_state.inventario)
                            st.rerun()

    # Mostrar carrito
    if st.session_state.carrito:
        st.sidebar.header("📋 Factura Actual")
        total = 0
        productos_a_eliminar = []
        
        for producto, item in st.session_state.carrito.items():
            subtotal = item['cantidad'] * item['precio']
            col1, col2, col3 = st.sidebar.columns([4, 2, 1])
            with col1:
                st.write(f"{producto}")
            with col2:
                st.write(f"x{item['cantidad']} = ${subtotal:.2f}")
            with col3:
                if st.button("❌", key=f"del_{producto}"):
                    productos_a_eliminar.append(producto)
                    # Devolver stock al inventario
                    st.session_state.inventario[item['categoria']][producto]['stock'] += item['cantidad']
                    actualizar_inventario(st.session_state.inventario)
            
            total += subtotal
        
        # Eliminar productos marcados
        for producto in productos_a_eliminar:
            del st.session_state.carrito[producto]
        
        if productos_a_eliminar:
            st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Total: ${total:.2f}**")
        
        # Finalizar venta
        if st.sidebar.button("✅ Finalizar Venta", type="primary"):
            nueva_venta = {
                'fecha': datetime.now().isoformat(),
                'productos': st.session_state.carrito,
                'total': total,
                'metodo_pago': "Efectivo"  # Puedes hacer esto configurable
            }
            guardar_venta(nueva_venta)
            st.session_state.carrito = {}
            st.sidebar.success("Venta registrada correctamente!")
            st.rerun()

def mostrar_inventario():
    st.header("📦 Gestión de Inventario")
    
    # Editor de inventario
    with st.form("form_editar_inventario"):
        categorias = list(st.session_state.inventario.keys())
        categoria = st.selectbox("Categoría", categorias)
        producto = st.text_input("Nombre del Producto")
        precio = st.number_input("Precio", min_value=0.0, step=0.1, format="%.2f")
        stock = st.number_input("Stock", min_value=0, step=1)
        
        if st.form_submit_button("Guardar Cambios"):
            if producto:
                if categoria not in st.session_state.inventario:
                    st.session_state.inventario[categoria] = {}
                
                st.session_state.inventario[categoria][producto] = {
                    'precio': precio,
                    'stock': stock,
                    'costo': precio * 0.5  # Ajusta según necesidad
                }
                actualizar_inventario(st.session_state.inventario)
                st.success("¡Inventario actualizado!")
    
    # Mostrar inventario actual
    st.subheader("Inventario Actual")
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
            "Costo": st.column_config.NumberColumn(format="$%.2f"),
            "Stock": st.column_config.ProgressColumn(
                format="%d", 
                min_value=0, 
                max_value=100
            )
        },
        hide_index=True,
        use_container_width=True
    )

def mostrar_reportes():
    st.header("📊 Reportes Diarios")
    
    # Filtrar ventas por fecha
    fecha_reporte = st.date_input("Seleccionar fecha", datetime.now())
    ventas_filtradas = [
        v for v in st.session_state.ventas 
        if datetime.fromisoformat(v['fecha']).date() == fecha_reporte
    ]
    
    if not ventas_filtradas:
        st.warning("No hay ventas para esta fecha")
        return
    
    # Reporte por método de pago
    st.subheader("💳 Ventas por Método de Pago")
    df_metodos = pd.DataFrame(ventas_filtradas).groupby('metodo_pago')['total'].agg(['sum', 'count']).reset_index()
    df_metodos.columns = ['Método', 'Total', 'Transacciones']
    st.dataframe(
        df_metodos,
        column_config={"Total": st.column_config.NumberColumn(format="$%.2f")},
        hide_index=True
    )
    
    # Reporte por producto
    st.subheader("🍰 Productos Vendidos")
    productos_vendidos = []
    for venta in ventas_filtradas:
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
    
    # Generar PDF
    if st.button("📄 Generar Reporte PDF"):
        pdf_buffer = generar_reporte_pdf(ventas_filtradas, fecha_reporte)
        st.download_button(
            label="⬇️ Descargar Reporte",
            data=pdf_buffer,
            file_name=f"reporte_{fecha_reporte.strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf"
        )

def generar_reporte_pdf(ventas, fecha):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    story.append(Paragraph(f"Reporte Diario - {fecha.strftime('%d/%m/%Y')}", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Resumen por método de pago
    story.append(Paragraph("1. Resumen por Método de Pago", styles['Heading2']))
    df_metodos = pd.DataFrame(ventas).groupby('metodo_pago')['total'].agg(['sum', 'count']).reset_index()
    data_metodos = [df_metodos.columns.tolist()] + df_metodos.values.tolist()
    t_metodos = Table(data_metodos)
    t_metodos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t_metodos)
    story.append(Spacer(1, 24))
    
    # Productos vendidos
    story.append(Paragraph("2. Productos Vendidos", styles['Heading2']))
    productos = []
    for venta in ventas:
        for prod, det in venta['productos'].items():
            productos.append([prod, det['cantidad'], f"${det['cantidad'] * det['precio']:.2f}"])
    
    data_productos = [["Producto", "Cantidad", "Total"]] + productos
    t_productos = Table(data_productos)
    t_productos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t_productos)
    
    # Total general
    total_dia = sum(v['total'] for v in ventas)
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"Total General del Día: ${total_dia:.2f}", styles['Heading2']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    main()
