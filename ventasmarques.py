import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(
    page_title="ARTE PARÍS POS", 
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
    """Agrega un producto al carrito de compras"""
    if producto in st.session_state.carrito:
        st.session_state.carrito[producto]["cantidad"] += cantidad
        st.session_state.carrito[producto]["subtotal"] = (
            st.session_state.carrito[producto]["cantidad"] * 
            st.session_state.carrito[producto]["precio"]
        )
    else:
        st.session_state.carrito[producto] = {
            "cantidad": cantidad,
            "precio": st.session_state.inventario[categoria][producto]["precio"],
            "categoria": categoria,
            "subtotal": cantidad * st.session_state.inventario[categoria][producto]["precio"]
        }

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
    """Interfaz principal para el proceso de ventas con búsqueda mejorada"""
    st.header("🛒 Punto de Venta")
    
    # --- Barra de búsqueda ---
    busqueda = st.text_input("🔍 Buscar producto por nombre:", "", 
                           key="busqueda_producto",
                           placeholder="Escribe para buscar productos...")
    
    # --- Resultados de búsqueda en tiempo real ---
    if busqueda:
        # Buscar productos que coincidan (sin distinguir mayúsculas/minúsculas)
        resultados = []
        for categoria, productos in st.session_state.inventario.items():
            for producto, datos in productos.items():
                if busqueda.lower() in producto.lower():
                    resultados.append({
                        "Producto": producto,
                        "Categoría": categoria,
                        "Precio": f"${datos['precio']:.2f}",
                        "Stock": datos['stock']
                    })
        
        if resultados:
            # Mostrar resultados en grupos de 6
            st.write(f"📝 {len(resultados)} resultado(s) para: '{busqueda}'")
            
            # Dividir resultados en columnas para mejor presentación
            cols = st.columns(2)
            for i, producto_info in enumerate(resultados[:6]):  # Mostrar hasta 6 resultados iniciales
                with cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"**{producto_info['Producto']}**")
                        st.caption(f"Categoría: {producto_info['Categoría']}")
                        st.write(f"Precio: {producto_info['Precio']}")
                        st.write(f"Stock: {producto_info['Stock']}")
                        
                        # Botón para agregar directamente
                        if st.button(f"Agregar {producto_info['Producto']}",
                                    key=f"add_{producto_info['Producto']}"):
                            if producto_info['Stock'] > 0:
                                if producto_info['Producto'] in st.session_state.carrito:
                                    st.session_state.carrito[producto_info['Producto']]['cantidad'] += 1
                                else:
                                    st.session_state.carrito[producto_info['Producto']] = {
                                        'cantidad': 1,
                                        'precio': float(producto_info['Precio'].replace('$', '')),
                                        'categoria': producto_info['Categoría'],
                                        'subtotal': float(producto_info['Precio'].replace('$', ''))
                                    }
                                st.success(f"✔ {producto_info['Producto']} agregado!")
                                st.rerun()
                            else:
                                st.error("No hay stock disponible")
            
            if len(resultados) > 6:
                with st.expander(f"Ver más resultados ({len(resultados)-6} restantes)"):
                    cols_extra = st.columns(2)
                    for i, producto_info in enumerate(resultados[6:]):
                        with cols_extra[i % 2]:
                            with st.container(border=True):
                                st.markdown(f"**{producto_info['Producto']}**")
                                st.caption(f"Categoría: {producto_info['Categoría']}")
                                st.write(f"Precio: {producto_info['Precio']}")
                                st.write(f"Stock: {producto_info['Stock']}")
                                
                                if st.button(f"Agregar {producto_info['Producto']}",
                                            key=f"add_extra_{producto_info['Producto']}"):
                                    if producto_info['Stock'] > 0:
                                        if producto_info['Producto'] in st.session_state.carrito:
                                            st.session_state.carrito[producto_info['Producto']]['cantidad'] += 1
                                        else:
                                            st.session_state.carrito[producto_info['Producto']] = {
                                                'cantidad': 1,
                                                'precio': float(producto_info['Precio'].replace('$', '')),
                                                'categoria': producto_info['Categoría'],
                                                'subtotal': float(producto_info['Precio'].replace('$', ''))
                                            }
                                        st.success(f"✔ {producto_info['Producto']} agregado!")
                                        st.rerun()
                                    else:
                                        st.error("No hay stock disponible")
        else:
            st.warning("No se encontraron productos con ese nombre")
    else:
        # Mostrar todas las categorías si no hay búsqueda
        for categoria, productos in st.session_state.inventario.items():
            with st.expander(f"📁 {categoria} ({len(productos)} productos)"):
                for producto, datos in productos.items():
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
                                    'categoria': categoria,
                                    'subtotal': datos['precio']
                                }
                            st.success(f"✔ {producto} agregado!")
                            st.rerun()
                        if datos['stock'] <= 0:
                            st.error("Sin stock")
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
    
    # Mostrar niveles actuales
    st.subheader("Niveles de Inventario")
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
    
    # Agregar nuevo producto
    st.subheader("Agregar/Actualizar Producto")
    with st.form("form_producto"):
        col1, col2 = st.columns(2)
        with col1:
            nueva_categoria = st.selectbox(
                "Categoría",
                list(st.session_state.inventario.keys()) + ["Nueva Categoría"]
            )
            if nueva_categoria == "Nueva Categoría":
                nueva_categoria = st.text_input("Nombre de nueva categoría:")
            
            nombre_producto = st.text_input("Nombre del producto:")
        with col2:
            precio = st.number_input("Precio de venta:", min_value=0.0, step=0.5)
            costo = st.number_input("Costo unitario:", min_value=0.0, step=0.5)
            stock = st.number_input("Stock inicial:", min_value=0, step=1)
        
        if st.form_submit_button("Guardar Producto"):
            if nueva_categoria and nombre_producto:
                if nueva_categoria not in st.session_state.inventario:
                    st.session_state.inventario[nueva_categoria] = {}
                
                st.session_state.inventario[nueva_categoria][nombre_producto] = {
                    "precio": precio,
                    "costo": costo,
                    "stock": stock
                }
                st.success("Producto guardado exitosamente!")
            else:
                st.error("Debe ingresar categoría y nombre del producto")

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

# --- APLICACIÓN PRINCIPAL ---
def main():
    inicializar_datos()
    
    # Menú de navegación
    st.sidebar.title("SweetBakery POS")
    opcion = st.sidebar.radio(
        "Menú Principal",
        ["Punto de Venta", "Gestión de Inventario", "Historial de Ventas", "Estadísticas"]
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
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**SweetBakery POS** v1.0")
    st.sidebar.markdown(f"*{datetime.datetime.now().year}*")

if __name__ == "__main__":
    main()
