import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas  # Importación faltante
import plotly.express as px  # Importación faltante

# Configuración inicial de la página
st.set_page_config(
    page_title="SweetBakery POS",  # Nombre corregido para consistencia
    page_icon="🍰", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BASE DE DATOS ---
def inicializar_datos():
    """Inicializa los datos en session_state si no existen"""
    if "inventario" not in st.session_state:
        st.session_state.inventario = {
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
        }
    
    if "ventas" not in st.session_state:
        st.session_state.ventas = []
    
    if "carrito" not in st.session_state:
        st.session_state.carrito = {}
    
    if "clientes" not in st.session_state:
        st.session_state.clientes = {}

# Asegurarse de que los datos se inicialicen AL INICIO
if 'inicializado' not in st.session_state:
    inicializar_datos()
    st.session_state.inicializado = True

# --- FUNCIONES PRINCIPALES ---
def buscar_productos(termino):
    """Busca productos en todas las categorías"""
    resultados = {}
    for categoria, items in st.session_state.inventario.items():
        for producto, datos in items.items():
            if termino.lower() in producto.lower():
                if categoria not in resultados:
                    resultados[categoria] = {}
                resultados[categoria][producto] = datos
    return resultados

def agregar_al_carrito(producto, cantidad, categoria):
    """Función mejorada para agregar productos al carrito con validación de stock"""
    stock_disponible = st.session_state.inventario[categoria][producto]["stock"]
    
    if stock_disponible <= 0:
        st.error(f"⚠️ No hay stock disponible de {producto}")
        return False
    
    if cantidad > stock_disponible:
        st.error(f"⚠️ Solo hay {stock_disponible} unidades disponibles de {producto}")
        return False
    
    if producto in st.session_state.carrito:
        nueva_cantidad = st.session_state.carrito[producto]["cantidad"] + cantidad
        if nueva_cantidad > stock_disponible:
            st.error(f"⚠️ No puedes agregar {cantidad} más. Máximo disponible: {stock_disponible - st.session_state.carrito[producto]['cantidad']}")
            return False
        
        st.session_state.carrito[producto]["cantidad"] = nueva_cantidad
        st.session_state.carrito[producto]["subtotal"] = nueva_cantidad * st.session_state.carrito[producto]["precio"]
    else:
        st.session_state.carrito[producto] = {
            "cantidad": cantidad,
            "precio": st.session_state.inventario[categoria][producto]["precio"],
            "categoria": categoria,
            "subtotal": cantidad * st.session_state.inventario[categoria][producto]["precio"]
        }
    
    return True

def finalizar_venta(cliente, metodo_pago):
    """Registra la venta y actualiza el inventario"""
    if not st.session_state.carrito:
        st.error("El carrito está vacío")
        return
    
    fecha = datetime.datetime.now()
    total = sum(item["subtotal"] for item in st.session_state.carrito.values())
    costo_total = sum(
        item["cantidad"] * st.session_state.inventario[item["categoria"]][producto]["costo"]
        for producto, item in st.session_state.carrito.items()
    )
    
    # Registrar venta
    venta = {
        "fecha": fecha,
        "cliente": cliente,
        "metodo_pago": metodo_pago,
        "productos": st.session_state.carrito.copy(),
        "total": total,
        "costo": costo_total,
        "ganancia": total - costo_total
    }
    
    st.session_state.ventas.append(venta)
    
    # Actualizar inventario
    for producto, item in st.session_state.carrito.items():
        st.session_state.inventario[item["categoria"]][producto]["stock"] -= item["cantidad"]
    
    # Limpiar carrito
    st.session_state.carrito = {}
    st.success("Venta registrada exitosamente!")
    return venta

def generar_factura(venta):
    """Genera un PDF con la factura de la venta"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Encabezado
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height-50, "SweetBakery �")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height-70, "Av. Principal 123 - Tel: 555-1234")
    c.drawCentredString(width/2, height-85, f"Factura #{len(st.session_state.ventas)}")
    c.drawCentredString(width/2, height-100, f"Fecha: {venta['fecha'].strftime('%Y-%m-%d %H:%M')}")
    
    # Información del cliente
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height-130, "Cliente:")
    c.setFont("Helvetica", 12)
    c.drawString(170, height-130, venta['cliente'])
    
    # Tabla de productos
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height-160, "Producto")
    c.drawString(300, height-160, "Cant.")
    c.drawString(350, height-160, "P.Unit")
    c.drawString(450, height-160, "Subtotal")
    
    y_position = height-180
    c.setFont("Helvetica", 10)
    for producto, item in venta['productos'].items():
        c.drawString(100, y_position, producto)
        c.drawString(300, y_position, str(item['cantidad']))
        c.drawString(350, y_position, f"${item['precio']}")
        c.drawString(450, y_position, f"${item['subtotal']}")
        y_position -= 20
    
    # Totales
    c.line(100, y_position-20, width-100, y_position-20)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(350, y_position-40, "TOTAL:")
    c.drawString(450, y_position-40, f"${venta['total']}")
    
    # Método de pago
    c.setFont("Helvetica", 10)
    c.drawString(100, y_position-70, f"Método de pago: {venta['metodo_pago']}")
    
    # Pie de página
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 50, "¡Gracias por su compra! Vuelva pronto")
    
    c.save()
    buffer.seek(0)
    return buffer

def mostrar_estadisticas():
    """Muestra gráficos y estadísticas de ventas"""
    if not st.session_state.ventas:
        st.warning("No hay datos de ventas para mostrar")
        return
    
    df_ventas = pd.DataFrame(st.session_state.ventas)
    df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
    df_ventas['dia'] = df_ventas['fecha'].dt.date
    
    # Gráfico de ventas por día
    st.subheader("📈 Ventas Diarias")
    ventas_diarias = df_ventas.groupby('dia').agg({'total':'sum', 'ganancia':'sum'}).reset_index()
    fig1 = px.line(ventas_diarias, x='dia', y=['total', 'ganancia'], 
                  title="Ventas y Ganancias por Día",
                  labels={'value': 'Monto ($)', 'variable': 'Tipo'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Productos más vendidos
    st.subheader("🏆 Productos Más Vendidos")
    productos_vendidos = []
    for venta in st.session_state.ventas:
        for producto, datos in venta['productos'].items():
            productos_vendidos.append({
                'Producto': producto,
                'Cantidad': datos['cantidad'],
                'Categoría': datos['categoria']
            })
    
    if productos_vendidos:
        df_productos = pd.DataFrame(productos_vendidos)
        top_productos = df_productos.groupby('Producto').sum().nlargest(5, 'Cantidad')
        fig2 = px.bar(top_productos, x=top_productos.index, y='Cantidad',
                     title="Top 5 Productos por Cantidad Vendida")
        st.plotly_chart(fig2, use_container_width=True)

# --- INTERFAZ DE USUARIO ---

def mostrar_interfaz_ventas():
    """Interfaz mejorada para el proceso de ventas con manejo de stock cero"""
    st.header("🛒 Punto de Venta - SweetBakery")
    
    # Barra de búsqueda mejorada
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            busqueda = st.text_input("🔍 Buscar producto:", "", 
                                   placeholder="Escribe el nombre del producto...",
                                   help="Busca por nombre de producto")
        with col2:
            categoria_filtro = st.selectbox("🗂️ Filtrar por categoría", 
                                          ["Todas"] + list(st.session_state.inventario.keys()))
    
    # Mostrar productos según búsqueda/filtro
    if busqueda or categoria_filtro != "Todas":
        resultados = []
        for categoria, productos in st.session_state.inventario.items():
            if categoria_filtro != "Todas" and categoria != categoria_filtro:
                continue
                
            for producto, datos in productos.items():
                if not busqueda or busqueda.lower() in producto.lower():
                    resultados.append({
                        "Producto": producto,
                        "Categoría": categoria,
                        "Precio": datos['precio'],
                        "Stock": datos['stock'],
                        "Imagen": "🎂" if categoria == "Pastelería" else 
                                 "🥐" if categoria == "Hojaldre" else
                                 "☕" if categoria == "Bebidas" else
                                 "🍪"
                    })
        
        if resultados:
            st.subheader(f"📦 Productos Disponibles ({len(resultados)} encontrados)")
            
            # Mostrar productos en tarjetas
            cols = st.columns(4)
            col_index = 0
            
            for idx, item in enumerate(resultados):
                with cols[col_index]:
                    with st.container(border=True):
                        # Cambiar color del borde si stock es cero
                        border_color = "#FF4B4B" if item['Stock'] == 0 else "#E0E0E0"
                        st.markdown(
                            f"""<div style='border: 2px solid {border_color}; border-radius: 5px; padding: 10px;'>
                            <p style='margin-bottom: 5px;'><strong>{item['Imagen']} {item['Producto']}</strong></p>
                            <p style='margin-bottom: 5px;'>💵 <strong>Precio:</strong> ${item['Precio']:.2f}</p>
                            <p style='margin-bottom: 10px;'>📦 <strong>Stock:</strong> {item['Stock']}</p>
                            </div>""", 
                            unsafe_allow_html=True
                        )
                        
                        # Mostrar mensaje si no hay stock
                        if item['Stock'] == 0:
                            st.error("Agotado", icon="⛔")
                        else:
                            # Botón para agregar con cantidad
                            cantidad = st.number_input(
                                "Cantidad:",
                                min_value=1,
                                max_value=item['Stock'],
                                value=1,
                                key=f"cant_{item['Producto']}",
                                label_visibility="collapsed"
                            )
                            
                            if st.button("➕ Agregar", 
                                       key=f"add_{item['Producto']}",
                                       use_container_width=True,
                                       disabled=(item['Stock'] == 0)):
                                agregar_al_carrito(item['Producto'], cantidad, item['Categoría'])
                                st.toast(f"✅ {cantidad} x {item['Producto']} agregado!")
                
                col_index = (col_index + 1) % 4
                if col_index == 0 and idx < len(resultados) - 1:
                    cols = st.columns(4)
        else:
            st.warning("No se encontraron productos con esos criterios")
            if st.button("Mostrar todos los productos"):
                st.session_state.busqueda_venta = ""
                st.rerun()
    else:
        # Mostrar todas las categorías con expansores si no hay búsqueda
        for categoria, productos in st.session_state.inventario.items():
            with st.expander(f"📂 {categoria} ({len(productos)} productos)", expanded=True):
                cols = st.columns(4)
                col_index = 0
                
                for idx, (producto, datos) in enumerate(productos.items()):
                    with cols[col_index]:
                        # Cambiar color del borde si stock es cero
                        border_color = "#FF4B4B" if datos['stock'] == 0 else "#E0E0E0"
                        st.markdown(
                            f"""<div style='border: 2px solid {border_color}; border-radius: 5px; padding: 10px;'>
                            <p style='margin-bottom: 5px;'><strong>{'🎂' if categoria == 'Pastelería' else '🥐' if categoria == 'Hojaldre' else '☕' if categoria == 'Bebidas' else '🍪'} {producto}</strong></p>
                            <p style='margin-bottom: 5px;'>💵 <strong>Precio:</strong> ${datos['precio']:.2f}</p>
                            <p style='margin-bottom: 10px;'>📦 <strong>Stock:</strong> {datos['stock']}</p>
                            </div>""", 
                            unsafe_allow_html=True
                        )
                        
                        # Mostrar mensaje si no hay stock
                        if datos['stock'] == 0:
                            st.error("Agotado", icon="⛔")
                        else:
                            # Botón para agregar con cantidad
                            cantidad = st.number_input(
                                "Cantidad:",
                                min_value=1,
                                max_value=datos['stock'],
                                value=1,
                                key=f"cant_{categoria}_{producto}",
                                label_visibility="collapsed"
                            )
                            
                            if st.button("➕ Agregar", 
                                       key=f"add_{categoria}_{producto}",
                                       use_container_width=True):
                                agregar_al_carrito(producto, cantidad, categoria)
                                st.toast(f"✅ {cantidad} x {producto} agregado!")
                    
                    col_index = (col_index + 1) % 4
                    if col_index == 0 and idx < len(productos) - 1:
                        cols = st.columns(4)

def mostrar_carrito():
    """Carrito de compras mejorado"""
    st.sidebar.header("📋 Factura Actual")
    
    if not st.session_state.carrito:
        st.sidebar.info("🛒 El carrito está vacío")
        st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2038/2038854.png", 
                        width=150, caption="Agrega productos para comenzar")
        return
    
    # Mostrar resumen compacto
    total_items = sum(item['cantidad'] for item in st.session_state.carrito.values())
    st.sidebar.subheader(f"🛍️ {total_items} {'producto' if total_items == 1 else 'productos'}")
    
    # Lista de productos con opciones de edición
    for producto, item in st.session_state.carrito.items():
        with st.sidebar.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{producto}**")
                st.caption(f"${item['precio']:.2f} c/u")
            with col2:
                nueva_cantidad = st.number_input(
                    "Cantidad",
                    min_value=1,
                    max_value=st.session_state.inventario[item['categoria']][producto]['stock'] + item['cantidad'],
                    value=item['cantidad'],
                    key=f"side_cant_{producto}",
                    label_visibility="collapsed"
                )
                
                if nueva_cantidad != item['cantidad']:
                    item['cantidad'] = nueva_cantidad
                    item['subtotal'] = nueva_cantidad * item['precio']
                    st.rerun()
            
            if st.button("❌ Eliminar", key=f"side_del_{producto}", use_container_width=True):
                del st.session_state.carrito[producto]
                st.rerun()
    
    # Resumen de compra
    st.sidebar.divider()
    subtotal = sum(item['subtotal'] for item in st.session_state.carrito.values())
    st.sidebar.markdown(f"**Subtotal:** ${subtotal:.2f}")
    
    # Opciones de pago mejoradas
    with st.sidebar.expander("💳 Información de Pago", expanded=True):
        cliente = st.text_input("👤 Nombre del cliente:", "Consumidor Final")
        
        metodo_pago = st.selectbox(
            "Método de pago:", 
            ["Efectivo Bs", "Efectivo $", "Tarjeta Débito", "Tarjeta Crédito", "Pago Móvil", "Zelle"],
            index=0
        )
        
        if metodo_pago.startswith("Efectivo"):
            monto_recibido = st.number_input("Monto recibido:", min_value=0.0, value=subtotal, step=1.0)
            cambio = monto_recibido - subtotal
            if cambio >= 0:
                st.markdown(f"**Cambio:** ${cambio:.2f}")
            else:
                st.error("El monto recibido es insuficiente")
    
    # Botones de acción
    st.sidebar.divider()
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Vaciar Carrito", use_container_width=True, type="secondary"):
            st.session_state.carrito = {}
            st.toast("Carrito vaciado")
            st.rerun()
    with col2:
        if st.button("✅ Finalizar Compra", use_container_width=True, type="primary"):
            venta = finalizar_venta(cliente, metodo_pago)
            if venta:
                st.sidebar.success("Venta registrada correctamente!")
                st.balloons()
                
                # Generar y ofrecer descarga de factura
                pdf_buffer = generar_factura(venta)
                st.sidebar.download_button(
                    label="📄 Descargar Factura",
                    data=pdf_buffer,
                    file_name=f"factura_{venta['fecha'].strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.session_state.carrito = {}
                st.rerun()
def mostrar_carrito():
    """Muestra el carrito de compras actual con opciones de edición"""
    st.sidebar.header("📋 Factura Actual")
    
    if not st.session_state.carrito:
        st.sidebar.info("El carrito está vacío")
        return
    
    # Mostrar items con opción de eliminar
    productos_a_eliminar = []
    for producto, item in st.session_state.carrito.items():
        col1, col2, col3 = st.sidebar.columns([6, 3, 1])
        with col1:
            st.write(f"**{producto}**")
        with col2:
            nueva_cantidad = st.number_input(
                f"Cantidad {producto}",
                min_value=1,
                max_value=st.session_state.inventario[item['categoria']][producto]['stock'],
                value=item['cantidad'],
                key=f"cant_{producto}",
                label_visibility="collapsed"
            )
            if nueva_cantidad != item['cantidad']:
                item['cantidad'] = nueva_cantidad
                item['subtotal'] = nueva_cantidad * item['precio']
        with col3:
            if st.button("❌", key=f"del_{producto}"):
                productos_a_eliminar.append(producto)
    
    # Eliminar productos marcados
    for producto in productos_a_eliminar:
        del st.session_state.carrito[producto]
    
    if productos_a_eliminar:
        st.rerun()
    
    # Resumen y total
    st.sidebar.markdown("---")
    total = sum(item['subtotal'] for item in st.session_state.carrito.values())
    st.sidebar.markdown(f"### Total: ${total:.2f}")
    
    # Datos del cliente y pago
    cliente = st.sidebar.text_input("👤 Nombre del cliente:", "Consumidor Final", key="nombre_cliente")
    metodo_pago = st.sidebar.selectbox(
        "💳 Método de pago:", 
        ["Efectivo Bs", "Efectivo $", "Tarjeta Débito", "Tarjeta Crédito", "Pago Móvil", "Zelle"],
        key="metodo_pago"
    )
    
    # Botones de acción
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Limpiar", use_container_width=True):
            st.session_state.carrito = {}
            st.rerun()
    with col2:
        if st.button("✅ Finalizar", type="primary", use_container_width=True):
            if finalizar_venta(cliente, metodo_pago):
                st.sidebar.success("Venta registrada correctamente!")
                st.session_state.carrito = {}
                st.rerun()
                
                
def mostrar_inventario():
    """Muestra y permite gestionar el inventario"""
    st.header("📦 Gestión de Inventario")
    
    # Mostrar todo el inventario
    inventario_df = []
    for categoria, productos in st.session_state.inventario.items():
        for producto, datos in productos.items():
            inventario_df.append({
                "Categoría": categoria,
                "Producto": producto,
                "Precio": datos["precio"],
                "Costo": datos["costo"],
                "Stock": datos["stock"],
                "Margen": f"{((datos['precio']-datos['costo'])/datos['costo']*100):.1f}%"
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
            ),
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Editor de inventario
    with st.expander("✏️ Editar Producto"):
        categorias = list(st.session_state.inventario.keys())
        producto_seleccionado = st.selectbox(
            "Seleccionar producto a editar",
            options=[(cat, prod) for cat in categorias for prod in st.session_state.inventario[cat].keys()],
            format_func=lambda x: f"{x[1]} ({x[0]})"
        )
        
        if producto_seleccionado:
            categoria, producto = producto_seleccionado
            datos = st.session_state.inventario[categoria][producto]
            
            with st.form(f"form_edit_{producto}"):
                nuevo_precio = st.number_input("Precio", value=datos["precio"], min_value=0.0, step=0.1)
                nuevo_costo = st.number_input("Costo", value=datos["costo"], min_value=0.0, step=0.1)
                nuevo_stock = st.number_input("Stock", value=datos["stock"], min_value=0, step=1)
                
                if st.form_submit_button("Guardar cambios"):
                    st.session_state.inventario[categoria][producto] = {
                        "precio": nuevo_precio,
                        "costo": nuevo_costo,
                        "stock": nuevo_stock
                    }
                    st.success("¡Cambios guardados!")
                    st.rerun()

def mostrar_historial_ventas():
    """Muestra el historial completo de ventas"""
    st.header("📊 Historial de Ventas")
    
    if not st.session_state.ventas:
        st.info("No hay ventas registradas aún")
        return
    
    # Filtros para el historial
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_inicio = st.date_input("Fecha inicio", datetime.date.today())
    with col2:
        fecha_fin = st.date_input("Fecha fin", datetime.date.today())
    with col3:
        filtro_categoria = st.selectbox(
            "Filtrar por categoría", 
            ["Todas"] + list(st.session_state.inventario.keys())
        )
    
    # Convertir ventas a DataFrame
    ventas_df = []
    for venta in st.session_state.ventas:
        if fecha_inicio <= venta["fecha"].date() <= fecha_fin:
            for producto, item in venta["productos"].items():
                if filtro_categoria == "Todas" or item["categoria"] == filtro_categoria:
                    ventas_df.append({
                        "Fecha": venta["fecha"],
                        "Cliente": venta["cliente"],
                        "Producto": producto,
                        "Categoría": item["categoria"],
                        "Cantidad": item["cantidad"],
                        "Precio Unitario": item["precio"],
                        "Subtotal": item["subtotal"],
                        "Método Pago": venta["metodo_pago"],
                        "Total Venta": venta["total"],
                        "Ganancia": venta["ganancia"]
                    })
    
    if not ventas_df:
        st.warning("No hay ventas que coincidan con los filtros")
        return
    
    df = pd.DataFrame(ventas_df)
    
    # Mostrar resumen
    st.subheader("Resumen de Ventas")
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas Totales", f"${df['Subtotal'].sum():.2f}")
    col2.metric("Ganancias Totales", f"${df['Ganancia'].sum():.2f}")
    col3.metric("Venta Promedio", f"${df['Total Venta'].mean():.2f}")
    
    # Mostrar tabla detallada
    st.subheader("Detalle de Ventas")
    st.dataframe(
        df.sort_values("Fecha", ascending=False),
        column_config={
            "Precio Unitario": st.column_config.NumberColumn(format="$%.2f"),
            "Subtotal": st.column_config.NumberColumn(format="$%.2f"),
            "Total Venta": st.column_config.NumberColumn(format="$%.2f"),
            "Ganancia": st.column_config.NumberColumn(format="$%.2f"),
            "Fecha": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Opción para exportar
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📤 Exportar a CSV",
        data=csv,
        file_name=f"ventas_{fecha_inicio}_{fecha_fin}.csv",
        mime="text/csv"
    )

def generar_reporte_diario():
    """Genera un reporte PDF con el cierre diario"""
    # Filtrar ventas del día actual
    hoy = datetime.date.today()
    ventas_hoy = [v for v in st.session_state.ventas if v['fecha'].date() == hoy]
    
    if not ventas_hoy:
        st.warning("No hay ventas registradas hoy")
        return None
    
    # Preparar datos para los reportes
    reporte_metodos = pd.DataFrame(ventas_hoy).groupby('metodo_pago')['total'].agg(['sum', 'count']).reset_index()
    reporte_metodos.columns = ['Método de Pago', 'Total Vendido', 'N° Transacciones']
    
    # Reporte por producto
    productos_vendidos = []
    for venta in ventas_hoy:
        for producto, datos in venta['productos'].items():
            productos_vendidos.append({
                'Producto': producto,
                'Categoría': datos['categoria'],
                'Cantidad': datos['cantidad'],
                'Total': datos['subtotal']
            })
    
    reporte_productos = pd.DataFrame(productos_vendidos).groupby(['Producto', 'Categoría']).agg({'Cantidad': 'sum', 'Total': 'sum'}).reset_index()
    
    # Crear PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    story.append(Paragraph(f"Reporte Diario - {hoy.strftime('%d/%m/%Y')}", styles['Title']))
    story.append(Spacer(1, 12))
    
    # 1. Reporte por Método de Pago
    story.append(Paragraph("1. Resumen por Método de Pago", styles['Heading2']))
    
    # Convertir DataFrame a lista para ReportLab
    data_metodos = [reporte_metodos.columns.tolist()] + reporte_metodos.values.tolist()
    
    # Crear tabla
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
    
    # 2. Reporte por Producto
    story.append(Paragraph("2. Ventas por Producto", styles['Heading2']))
    
    data_productos = [reporte_productos.columns.tolist()] + reporte_productos.values.tolist()
    
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
    story.append(Spacer(1, 24))
    
    # Totales
    total_dia = reporte_metodos['Total Vendido'].sum()
    story.append(Paragraph(f"Total General del Día: ${total_dia:.2f}", styles['Heading2']))
    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def mostrar_reportes_diarios():
    """Interfaz para generar y mostrar reportes diarios"""
    st.header("📊 Reportes Diarios")
    
    # Filtrar ventas del día actual
    hoy = datetime.date.today()
    ventas_hoy = [v for v in st.session_state.ventas if v['fecha'].date() == hoy]
    
    if not ventas_hoy:
        st.warning("No hay ventas registradas hoy")
        return
    
    # 1. Reporte por Método de Pago
    st.subheader("1. Resumen por Método de Pago")
    reporte_metodos = pd.DataFrame(ventas_hoy).groupby('metodo_pago')['total'].agg(['sum', 'count']).reset_index()
    reporte_metodos.columns = ['Método de Pago', 'Total Vendido', 'N° Transacciones']
    st.dataframe(
        reporte_metodos,
        column_config={
            "Total Vendido": st.column_config.NumberColumn(format="$%.2f")
        },
        hide_index=True
    )
    
    # Gráfico de métodos de pago
    st.bar_chart(reporte_metodos.set_index('Método de Pago')['Total Vendido'])
    
    # 2. Reporte por Producto
    st.subheader("2. Ventas por Producto")
    productos_vendidos = []
    for venta in ventas_hoy:
        for producto, datos in venta['productos'].items():
            productos_vendidos.append({
                'Producto': producto,
                'Categoría': datos['categoria'],
                'Cantidad': datos['cantidad'],
                'Total': datos['subtotal']
            })
    
    reporte_productos = pd.DataFrame(productos_vendidos).groupby(['Producto', 'Categoría']).agg({'Cantidad': 'sum', 'Total': 'sum'}).reset_index()
    st.dataframe(
        reporte_productos,
        column_config={
            "Total": st.column_config.NumberColumn(format="$%.2f")
        },
        hide_index=True
    )
    
    # Gráfico de productos más vendidos
    st.subheader("Productos Más Vendidos (Cantidad)")
    top_productos = reporte_productos.sort_values('Cantidad', ascending=False).head(10)
    st.bar_chart(top_productos.set_index('Producto')['Cantidad'])
    
    # Botón para generar PDF
    if st.button("📄 Generar Reporte PDF"):
        pdf = generar_reporte_diario()
        if pdf:
            st.success("Reporte generado correctamente!")
            st.download_button(
                label="⬇️ Descargar Reporte Completo",
                data=pdf,
                file_name=f"reporte_diario_{hoy.strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

# Actualizar la función main para incluir el nuevo menú
def main():
    # Menú de navegación
    st.sidebar.title("SweetBakery POS")
    opcion = st.sidebar.radio(
        "Menú Principal",
        ["Punto de Venta", "Gestión de Inventario", "Historial de Ventas", "Estadísticas", "Reportes Diarios"]
    )
    
    # Mostrar sección según selección
    if opcion == "Punto de Venta":
        mostrar_interfaz_ventas()
        mostrar_carrito()
    elif opcion == "Gestión de Inventario":
        mostrar_inventario()
    elif opcion == "Historial de Ventas":
        mostrar_historial_ventas()
    elif opcion == "Estadísticas":
        mostrar_estadisticas()
    elif opcion == "Reportes Diarios":
        mostrar_reportes_diarios()

if __name__ == "__main__":
    main()
