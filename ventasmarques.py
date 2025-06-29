import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import pandas as pd
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

import firebase_admin
from firebase_admin import credentials, db

def initialize_firebase():
    # Verificar si ya está inicializada
    if not firebase_admin._apps:
        try:
            # Configuración desde secrets.toml
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
            
            # Inicializar con nombre específico para evitar conflictos
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase"]["databaseURL"],
                'name': 'SweetBakeryApp'  # Nombre único para la app
            })
            return True
        except Exception as e:
            st.error(f"Error inicializando Firebase: {str(e)}")
            st.stop()
    return True

    try:
        st.write("Probando conexión a Firebase...")
        test_ref = db.reference('/test_connection')
        test_ref.set({"timestamp": datetime.now().isoformat()})
        st.success("¡Conexión exitosa a Firebase!")
    except Exception as e:
        st.error(f"Fallo en la conexión: {str(e)}")


# --- Datos Iniciales ---
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
            },
        "ventas": []
    }}

# --- Funciones de Firebase Mejoradas ---
def get_firebase_data():
    """Obtiene datos de Firebase con manejo de errores"""
    try:
        return {
            "inventario": db.reference('/inventario').get() or cargar_datos_iniciales()["inventario"],
            "ventas": db.reference('/ventas').get() or []
        }
    except Exception as e:
        st.error(f"Error conectando a Firebase: {e}")
        return cargar_datos_iniciales()

def guardar_venta_segura(venta):
    try:
        ref = db.reference('/ventas')
        ventas_actuales = ref.get() or []
        ventas_actuales.append(venta)
        ref.set(ventas_actuales)
        return True
    except Exception as e:
        st.error(f"Error guardando venta: {e}")
        return False

def actualizar_stock_seguro(categoria, producto, cantidad):
    try:
        ref = db.reference(f'/inventario/{categoria}/{producto}/stock')
        ref.transaction(lambda current: (current or 0) - cantidad)
        return True
    except Exception as e:
        st.error(f"Error actualizando stock: {e}")
        return False

# --- Interfaz Streamlit Mejorada ---
def main():
    # Inicializar Firebase primero
    if not initialize_firebase():
        st.error("No se pudo conectar a Firebase. Verifica la configuración.")
        st.stop()
    
    # Obtener datos de Firebase con manejo de errores
    try:
        firebase_data = {
            "inventario": db.reference('/inventario').get() or {},
            "ventas": db.reference('/ventas').get() or []
        }
    except Exception as e:
        st.error(f"Error obteniendo datos de Firebase: {str(e)}")
        firebase_data = {"inventario": {}, "ventas": []}
    

    
    # Actualización periódica segura (cada 30 segundos)
    if time.time() - st.session_state.last_update > 30:
        firebase_data = get_firebase_data()
        st.session_state.inventario = firebase_data["inventario"]
        st.session_state.ventas = firebase_data["ventas"]
        st.session_state.last_update = time.time()
    
    # Sidebar principal
    st.sidebar.title("🍰 SweetBakery POS")
    opcion = st.sidebar.radio(
        "Menú Principal",
        ["Punto de Venta", "Gestión de Inventario", "Reportes"],
        horizontal=True
    )
    
    if opcion == "Punto de Venta":
        mostrar_punto_venta()
    elif opcion == "Gestión de Inventario":
        mostrar_inventario()
    elif opcion == "Reportes":
        mostrar_reportes()

# --- Punto de Venta Mejorado ---
def mostrar_punto_venta():
    st.header("🛒 Punto de Venta")
    
    # Búsqueda mejorada
    col1, col2 = st.columns([3, 1])
    with col1:
        busqueda = st.text_input("🔍 Buscar producto", placeholder="Nombre del producto...")
    with col2:
        st.session_state.metodo_pago = st.selectbox(
            "Método de Pago",
            ["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia"],
            key="select_metodo_pago"
        )
    
    # Mostrar productos con mejor UI
    for categoria, productos in st.session_state.inventario.items():
        with st.expander(f"📦 {categoria}", expanded=True):
            cols = st.columns(3)
            col_idx = 0
            
            for producto, datos in productos.items():
                if busqueda.lower() not in producto.lower():
                    continue
                    
                with cols[col_idx]:
                    card = st.container(border=True)
                    card.markdown(f"**{producto}**")
                    card.markdown(f"💵 Precio: ${datos['precio']:.2f}")
                    
                    stock_text = "✅ Disponible" if datos['stock'] > 0 else "❌ Agotado"
                    color = "green" if datos['stock'] > 0 else "red"
                    card.markdown(f"<span style='color:{color}'>{stock_text} ({datos['stock']})</span>", unsafe_allow_html=True)
                    
                    if datos['stock'] > 0:
                        if card.button("➕ Añadir", key=f"add_{producto}", use_container_width=True):
                            if producto in st.session_state.carrito:
                                st.session_state.carrito[producto]['cantidad'] += 1
                            else:
                                st.session_state.carrito[producto] = {
                                    'cantidad': 1,
                                    'precio': datos['precio'],
                                    'categoria': categoria
                                }
                            if not actualizar_stock_seguro(categoria, producto, 1):
                                st.session_state.carrito[producto]['cantidad'] -= 1
                                if st.session_state.carrito[producto]['cantidad'] <= 0:
                                    del st.session_state.carrito[producto]
                            st.rerun()
                    else:
                        card.button("❌ Agotado", disabled=True, use_container_width=True)
                    
                    if datos['stock'] < 3 and datos['stock'] > 0:
                        card.warning(f"¡Últimas {datos['stock']} unidades!")
                
                col_idx = (col_idx + 1) % 3
    
    # Carrito mejorado
    if st.session_state.carrito:
        with st.sidebar:
            st.header("📋 Factura Actual")
            total = 0
            productos_a_eliminar = []
            
            for producto, item in st.session_state.carrito.items():
                subtotal = item['cantidad'] * item['precio']
                total += subtotal
                
                col1, col2, col3 = st.columns([5, 3, 1])
                col1.write(f"▪️ {producto}")
                col2.write(f"x{item['cantidad']} = ${subtotal:.2f}")
                if col3.button("❌", key=f"del_{producto}"):
                    productos_a_eliminar.append(producto)
            
            # Eliminar productos del carrito
            for producto in productos_a_eliminar:
                item = st.session_state.carrito[producto]
                if actualizar_stock_seguro(item['categoria'], producto, -item['cantidad']):
                    del st.session_state.carrito[producto]
                    st.rerun()
            
            st.divider()
            st.markdown(f"**Total a Pagar:** ${total:.2f}")
            
            if st.button("✅ Finalizar Venta", type="primary", use_container_width=True):
                if not st.session_state.carrito:
                    st.warning("El carrito está vacío")
                    return
                
                venta = {
                    'fecha': datetime.now().isoformat(),
                    'productos': st.session_state.carrito.copy(),
                    'total': total,
                    'metodo_pago': st.session_state.metodo_pago
                }
                
                if guardar_venta_segura(venta):
                    st.session_state.carrito = {}
                    st.success("Venta registrada exitosamente!")
                    time.sleep(1)
                    st.rerun()
    else:
        st.sidebar.info("🛒 El carrito está vacío. Añade productos para comenzar.")

# --- Inventario Mejorado ---
def mostrar_inventario():
    st.header("📦 Gestión de Inventario")
    
    # Editor de inventario mejorado
    with st.form("form_editar_inventario", border=True):
        st.subheader("✏️ Editar Producto")
        
        categorias = list(st.session_state.inventario.keys())
        col1, col2 = st.columns(2)
        
        with col1:
            categoria = st.selectbox("Categoría", categorias)
            producto = st.text_input("Nombre del Producto")
            stock = st.number_input("Stock Disponible", min_value=0, step=1)
        
        with col2:
            precio = st.number_input("Precio de Venta", min_value=0.0, step=0.1, format="%.2f")
            costo = st.number_input("Costo Unitario", min_value=0.0, step=0.1, format="%.2f")
        
        submitted = st.form_submit_button("💾 Guardar Producto", type="primary")
        
        if submitted:
            if not producto:
                st.error("El nombre del producto es requerido")
                return
            
            try:
                if categoria not in st.session_state.inventario:
                    st.session_state.inventario[categoria] = {}
                
                st.session_state.inventario[categoria][producto] = {
                    'precio': precio,
                    'stock': stock,
                    'costo': costo
                }
                
                db.reference('/inventario').set(st.session_state.inventario)
                st.success("¡Producto actualizado correctamente!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {str(e)}")
    
    # Visualización de inventario mejorada
    st.subheader("📊 Inventario Actual")
    
    inventario_df = []
    for categoria, productos in st.session_state.inventario.items():
        for producto, datos in productos.items():
            inventario_df.append({
                "Categoría": categoria,
                "Producto": producto,
                "Precio": datos['precio'],
                "Costo": datos['costo'],
                "Margen": datos['precio'] - datos['costo'],
                "Stock": datos['stock'],
                "Valor Stock": datos['stock'] * datos['costo']
            })
    
    df = pd.DataFrame(inventario_df)
    
    # Mostrar métricas resumen
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Productos", len(df))
    col2.metric("Valor Total Stock", f"${df['Valor Stock'].sum():,.2f}")
    col3.metric("Margen Promedio", f"${df['Margen'].mean():.2f}")
    
    # Mostrar tabla con filtros
    with st.expander("🔍 Filtros Avanzados"):
        filtro_categoria = st.multiselect(
            "Filtrar por categoría",
            options=df['Categoría'].unique(),
            default=df['Categoría'].unique()
        )
        filtro_stock = st.slider(
            "Filtrar por stock mínimo",
            min_value=0,
            max_value=int(df['Stock'].max()) if len(df) > 0 else 100,
            value=0
        )
    
    df_filtrado = df[
        (df['Categoría'].isin(filtro_categoria)) & 
        (df['Stock'] >= filtro_stock)
    ]
    
    st.dataframe(
        df_filtrado,
        column_config={
            "Precio": st.column_config.NumberColumn(format="$%.2f"),
            "Costo": st.column_config.NumberColumn(format="$%.2f"),
            "Margen": st.column_config.NumberColumn(format="$%.2f"),
            "Valor Stock": st.column_config.NumberColumn(format="$%.2f"),
            "Stock": st.column_config.ProgressColumn(
                format="%d",
                min_value=0,
                max_value=df['Stock'].max() if len(df) > 0 else 100
            )
        },
        hide_index=True,
        use_container_width=True
    )

# --- Reportes Mejorados ---
def mostrar_reportes():
    st.header("📊 Reportes Avanzados")
    
    # Selector de fechas mejorado
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha de inicio", datetime.now())
    with col2:
        fecha_fin = st.date_input("Fecha de fin", datetime.now())
    
    if fecha_fin < fecha_inicio:
        st.error("La fecha de fin no puede ser anterior a la fecha de inicio")
        return
    
    # Filtrar ventas
    ventas_filtradas = [
        v for v in st.session_state.ventas
        if fecha_inicio <= datetime.fromisoformat(v['fecha']).date() <= fecha_fin
    ]
    
    if not ventas_filtradas:
        st.warning("No hay ventas en el período seleccionado")
        return
    
    # Métricas rápidas
    total_ventas = sum(v['total'] for v in ventas_filtradas)
    num_ventas = len(ventas_filtradas)
    avg_venta = total_ventas / num_ventas if num_ventas > 0 else 0
    
    st.subheader("📈 Resumen General")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ventas", f"${total_ventas:,.2f}")
    col2.metric("N° Transacciones", num_ventas)
    col3.metric("Ticket Promedio", f"${avg_venta:.2f}")
    
    # Pestañas para diferentes reportes
    tab1, tab2, tab3 = st.tabs(["Métodos de Pago", "Productos Vendidos", "Análisis por Categoría"])
    
    with tab1:
        st.subheader("💳 Ventas por Método de Pago")
        df_metodos = pd.DataFrame(ventas_filtradas).groupby('metodo_pago')['total'].agg(['sum', 'count']).reset_index()
        df_metodos.columns = ['Método', 'Total', 'Transacciones']
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(
                df_metodos,
                column_config={
                    "Total": st.column_config.NumberColumn(format="$%.2f")
                },
                hide_index=True
            )
        with col2:
            st.bar_chart(df_metodos.set_index('Método')['Total'])
    
    with tab2:
        st.subheader("🍰 Productos Vendidos")
        productos_vendidos = []
        for venta in ventas_filtradas:
            for producto, datos in venta['productos'].items():
                productos_vendidos.append({
                    'Producto': producto,
                    'Cantidad': datos['cantidad'],
                    'Total': datos['cantidad'] * datos['precio'],
                    'Categoría': datos.get('categoria', 'Desconocida')
                })
        
        df_productos = pd.DataFrame(productos_vendidos)
        
        if not df_productos.empty:
            df_agrupado = df_productos.groupby('Producto').agg({
                'Cantidad': 'sum',
                'Total': 'sum'
            }).sort_values('Total', ascending=False).reset_index()
            
            st.dataframe(
                df_agrupado,
                column_config={
                    "Total": st.column_config.NumberColumn(format="$%.2f")
                },
                hide_index=True
            )
    
    with tab3:
        st.subheader("📦 Ventas por Categoría")
        if not df_productos.empty:
            df_categorias = df_productos.groupby('Categoría').agg({
                'Cantidad': 'sum',
                'Total': 'sum'
            }).sort_values('Total', ascending=False).reset_index()
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(
                    df_categorias,
                    column_config={
                        "Total": st.column_config.NumberColumn(format="$%.2f")
                    },
                    hide_index=True
                )
            with col2:
                st.bar_chart(df_categorias.set_index('Categoría')['Total'])
    
    # Generación de PDF mejorada
    st.subheader("📄 Exportar Reporte")
    if st.button("🖨️ Generar PDF", type="primary"):
        with st.spinner("Generando reporte..."):
            pdf_buffer = generar_reporte_pdf(ventas_filtradas, fecha_inicio, fecha_fin)
            st.download_button(
                label="⬇️ Descargar Reporte",
                data=pdf_buffer,
                file_name=f"reporte_{fecha_inicio}_a_{fecha_fin}.pdf",
                mime="application/pdf"
            )

def generar_reporte_pdf(ventas, fecha_inicio, fecha_fin):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Encabezado
    story.append(Paragraph("SweetBakery - Reporte de Ventas", styles['Title']))
    story.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", styles['Heading2']))
    story.append(Spacer(1, 24))
    
    # Resumen general
    total_ventas = sum(v['total'] for v in ventas)
    num_ventas = len(ventas)
    
    story.append(Paragraph("Resumen General", styles['Heading2']))
    data_resumen = [
        ["Total Ventas", f"${total_ventas:,.2f}"],
        ["N° de Transacciones", num_ventas],
        ["Ticket Promedio", f"${total_ventas/num_ventas if num_ventas > 0 else 0:.2f}"]
    ]
    t_resumen = Table(data_resumen)
    t_resumen.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    story.append(t_resumen)
    story.append(Spacer(1, 24))
    
    # Productos más vendidos
    productos = {}
    for venta in ventas:
        for prod, det in venta['productos'].items():
            if prod not in productos:
                productos[prod] = 0
            productos[prod] += det['cantidad']
    
    if productos:
        story.append(Paragraph("Productos Más Vendidos", styles['Heading2']))
        productos_ordenados = sorted(productos.items(), key=lambda x: x[1], reverse=True)[:10]
        data_productos = [["Producto", "Cantidad"]] + [[p[0], str(p[1])] for p in productos_ordenados]
        t_productos = Table(data_productos)
        t_productos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t_productos)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    main()
