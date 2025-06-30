# Importaciones necesarias
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date # Importar date para st.date_input
import pandas as pd
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Funciones de Inicialización y Conexión a Firebase ---

def initialize_firebase():
    """
    Inicializa la aplicación de Firebase con las credenciales de Streamlit Secrets.
    Retorna True si la inicialización es exitosa, False en caso contrario.
    """
    if not firebase_admin._apps:
        try:
            # Obtener la clave privada y asegurar el formato correcto
            private_key = st.secrets.firebase.private_key
            
            # Verificar que la clave comienza y termina correctamente
            if not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
                private_key = "-----BEGIN PRIVATE KEY-----\n" + private_key
            if not private_key.endswith("-----END PRIVATE KEY-----"):
                private_key = private_key + "\n-----END PRIVATE KEY-----"
            
            # Reemplazar dobles barras invertidas si existen
            private_key = private_key.replace('\\n', '\n')
            
            firebase_config = {
                "type": st.secrets.firebase.type,
                "project_id": st.secrets.firebase.project_id,
                "private_key_id": st.secrets.firebase.private_key_id,
                "private_key": private_key,
                "client_email": st.secrets.firebase.client_email,
                "client_id": st.secrets.firebase.client_id,
                "auth_uri": st.secrets.firebase.auth_uri,
                "token_uri": st.secrets.firebase.token_uri,
                "auth_provider_x509_cert_url": st.secrets.firebase.auth_provider_x509_cert_url,
                "client_x509_cert_url": st.secrets.firebase.client_x509_cert_url
            }
            
            # Verificar la configuración antes de inicializar
            required_keys = ["type", "project_id", "private_key_id", "private_key",
                             "client_email", "client_id", "auth_uri", "token_uri",
                             "auth_provider_x509_cert_url", "client_x509_cert_url"]
            
            for key in required_keys:
                if not firebase_config.get(key):
                    st.error(f"Falta configuración requerida en st.secrets para Firebase: {key}")
                    return False
            
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets.firebase.databaseURL
            })
            return True
        except Exception as e:
            st.error(f"Error inicializando Firebase. Asegúrate de que st.secrets está configurado correctamente. Detalles: {str(e)}")
            return False
    return True

# --- Datos Iniciales (Fallback) ---
def cargar_datos_iniciales():
    """Retorna datos iniciales predefinidos para usar como fallback si Firebase no está disponible."""
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

# --- Funciones de Firebase Mejoradas ---
def get_firebase_data():
    """
    Obtiene los datos de inventario y ventas de Firebase.
    Retorna un diccionario con "inventario" y "ventas", o datos iniciales si falla.
    """
    try:
        inventario_data = db.reference('/inventario').get()
        ventas_data = db.reference('/ventas').get()
        return {
            "inventario": inventario_data if inventario_data is not None else {},
            "ventas": ventas_data if ventas_data is not None else []
        }
    except Exception as e:
        st.warning(f"No se pudo conectar a Firebase o leer datos. Usando datos iniciales. Detalles: {str(e)}")
        return cargar_datos_iniciales()

def guardar_venta(venta):
    """Guarda una venta en Firebase."""
    try:
        ref = db.reference('/ventas')
        ventas = ref.get() or [] # Obtener la lista actual, o una lista vacía si no existe
        ventas.append(venta)
        ref.set(ventas)
        return True
    except Exception as e:
        st.error(f"Error guardando venta en Firebase: {str(e)}")
        return False

def actualizar_stock(categoria, producto, cantidad):
    """
    Actualiza el stock de un producto en Firebase usando una transacción para asegurar atomicidad.
    Cantidad puede ser positiva (sumar) o negativa (restar).
    """
    try:
        ref = db.reference(f'/inventario/{categoria}/{producto}/stock')
        # Usar una transacción para evitar race conditions al actualizar stock
        result = ref.transaction(lambda current: (current or 0) - cantidad)
        if result[0]: # result[0] es True si la transacción se completó exitosamente
            return True
        else:
            st.error(f"Error en la transacción de stock para {producto}. Posible conflicto de datos.")
            return False
    except Exception as e:
        st.error(f"Error actualizando stock en Firebase para {producto}: {str(e)}")
        return False

# --- Interfaz Streamlit ---
def main():
    """Función principal de la aplicación Streamlit."""
    st.set_page_config(
        page_title="SweetBakery POS",
        page_icon="🍰",
        layout="wide"
    )

    # 1. INICIALIZACIÓN ROBUSTA DEL ESTADO DE LA SESIÓN
    # Inicializa todas las claves necesarias en st.session_state
    if "firebase_initialized" not in st.session_state:
        st.session_state.firebase_initialized = False
    if "inventario" not in st.session_state:
        st.session_state.inventario = {}
    if "ventas" not in st.session_state:
        st.session_state.ventas = []
    if "carrito" not in st.session_state:
        st.session_state.carrito = {}
    if "metodo_pago" not in st.session_state:
        st.session_state.metodo_pago = "Efectivo"
    if "last_firebase_sync" not in st.session_state:
        st.session_state.last_firebase_sync = 0 # Usar un nombre más específico

    # 2. CONEXIÓN Y SINCRONIZACIÓN CON FIREBASE
    # Asegura que Firebase se inicialice una sola vez por sesión
    if not st.session_state.firebase_initialized:
        with st.spinner("Conectando a Firebase..."):
            if initialize_firebase():
                st.session_state.firebase_initialized = True
                # Una vez inicializado, carga los datos por primera vez
                firebase_data = get_firebase_data()
                st.session_state.inventario = firebase_data.get("inventario", {})
                st.session_state.ventas = firebase_data.get("ventas", [])
                st.session_state.last_firebase_sync = time.time()
                st.success("Conexión a Firebase establecida.")
            else:
                st.error("Error crítico: No se pudo conectar a Firebase. La aplicación podría funcionar con datos de prueba.")
                # Si falla, carga datos iniciales como fallback
                initial_fallback_data = cargar_datos_iniciales()
                st.session_state.inventario = initial_fallback_data["inventario"]
                st.session_state.ventas = initial_fallback_data["ventas"]
                st.session_state.firebase_initialized = False # Indicar que no se pudo inicializar completamente
                # No se detiene la app, para que el usuario pueda usarla con datos de prueba
    
    # 3. ACTUALIZACIÓN PERIÓDICA DE DATOS DESDE FIREBASE (solo si Firebase se inicializó con éxito)
    if st.session_state.firebase_initialized and (time.time() - st.session_state.last_firebase_sync > 30):
        try:
            with st.spinner("Sincronizando datos desde Firebase..."):
                firebase_data = get_firebase_data()
                if firebase_data:
                    st.session_state.inventario = firebase_data.get("inventario", {})
                    st.session_state.ventas = firebase_data.get("ventas", [])
                    st.session_state.last_firebase_sync = time.time()
                    # st.info("Datos actualizados desde Firebase.") # Descomentar para depuración
        except Exception as e:
            st.error(f"Error durante la sincronización periódica con Firebase: {str(e)}")
            st.session_state.firebase_initialized = False # Marcar como no inicializado para reintentar o usar fallback

    # Sidebar principal
    st.sidebar.title("🍰 SweetBakery POS")
    opcion = st.sidebar.radio(
        "Menú Principal",
        ["Punto de Venta", "Gestión de Inventario", "Reportes"],
        horizontal=False # Vertical es mejor para sidebar
    )
    
    # Navegación entre páginas
    if opcion == "Punto de Venta":
        mostrar_punto_venta()
    elif opcion == "Gestión de Inventario":
        mostrar_inventario()
    elif opcion == "Reportes":
        mostrar_reportes()

# --- Punto de Venta Mejorado ---
def mostrar_punto_venta():
    """Interfaz del punto de venta."""
    st.header("🛒 Punto de Venta")
    
    # Búsqueda y método de pago
    col1, col2 = st.columns([3, 1])
    with col1:
        busqueda = st.text_input("🔍 Buscar producto", placeholder="Nombre del producto...", key="pv_busqueda")
    with col2:
        st.session_state.metodo_pago = st.selectbox(
            "Método de Pago",
            ["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia"],
            key="pv_metodo_pago_select"
        )
    
    # Mostrar productos por categoría
    for categoria, productos in st.session_state.inventario.items():
        with st.expander(f"📦 {categoria}", expanded=True):
            cols = st.columns(3)
            col_idx = 0
            
            for producto, datos in productos.items():
                # Filtrar por búsqueda
                if busqueda.lower() not in producto.lower():
                    continue
                    
                with cols[col_idx]:
                    card = st.container(border=True)
                    card.markdown(f"**{producto}**")
                    card.markdown(f"💵 Precio: ${datos['precio']:.2f}")
                    
                    # Mostrar estado del stock
                    if datos['stock'] > 0:
                        card.markdown(f"🟢 Disponible ({datos['stock']})")
                        if card.button("➕ Añadir", key=f"add_{producto}", use_container_width=True):
                            # Verificar si hay suficiente stock antes de añadir al carrito
                            if st.session_state.inventario[categoria][producto]['stock'] > 0:
                                if producto in st.session_state.carrito:
                                    st.session_state.carrito[producto]['cantidad'] += 1
                                else:
                                    st.session_state.carrito[producto] = {
                                        'cantidad': 1,
                                        'precio': datos['precio'],
                                        'categoria': categoria,
                                        'costo': datos.get('costo', 0) # Asegurar que el costo esté en el carrito
                                    }
                                if not actualizar_stock(categoria, producto, 1): # Reducir stock en DB
                                    st.error("No se pudo actualizar el stock en la base de datos.")
                                st.rerun() # Forzar rerun para actualizar el estado visual
                            else:
                                st.warning(f"¡{producto} está agotado!")
                    else:
                        card.markdown("🔴 Agotado")
                        card.button("❌ Agotado", disabled=True, use_container_width=True)
                        
                    # Alerta para stock bajo
                    if 0 < datos['stock'] < 3:
                        card.warning(f"¡Últimas {datos['stock']} unidades!")
                
                col_idx = (col_idx + 1) % 3
    
    # Mostrar carrito de compras en el sidebar
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
            
            # Eliminar productos del carrito y reponer stock
            for producto in productos_a_eliminar:
                item = st.session_state.carrito[producto]
                # Aumentar stock en DB
                if actualizar_stock(item['categoria'], producto, -item['cantidad']): 
                    del st.session_state.carrito[producto]
                    st.rerun() # Forzar rerun
                else:
                    st.error(f"No se pudo reponer el stock para {producto}.")
            
            st.divider()
            st.markdown(f"**Total a Pagar:** ${total:,.2f}") # Formato con coma para miles
            
            if st.button("✅ Finalizar Venta", type="primary", use_container_width=True):
                if not st.session_state.carrito:
                    st.warning("El carrito está vacío. Añade productos para finalizar una venta.")
                    return
                    
                venta = {
                    'fecha': datetime.now().isoformat(),
                    'productos': st.session_state.carrito.copy(), # Guardar una copia del carrito
                    'total': total,
                    'metodo_pago': st.session_state.metodo_pago
                }
                
                if guardar_venta(venta):
                    st.session_state.carrito = {} # Limpiar carrito después de la venta
                    st.success("Venta registrada exitosamente!")
                    time.sleep(1) # Pequeña pausa para que el usuario vea el mensaje
                    st.rerun() # Forzar rerun para limpiar el carrito y actualizar datos

    else:
        st.sidebar.info("🛒 El carrito está vacío. Añade productos para comenzar.")


def mostrar_inventario():
    """Interfaz para la gestión del inventario."""
    st.header("📦 Gestión de Inventario")
    
    # Editor de inventario mejorado
    with st.form("form_editar_inventario", border=True):
        st.subheader("✏️ Añadir/Editar Producto")
        
        categorias = list(st.session_state.inventario.keys())
        # Opción para añadir nueva categoría
        nueva_categoria_option = "➕ Nueva Categoría..."
        categorias_options = [nueva_categoria_option] + sorted(categorias)
        
        selected_categoria = st.selectbox(
            "Seleccionar Categoría",
            options=categorias_options,
            key="inv_select_categoria"
        )
        
        if selected_categoria == nueva_categoria_option:
            categoria_input = st.text_input("Nombre de la Nueva Categoría", key="inv_nueva_categoria_input")
            categoria_final = categoria_input if categoria_input else "Nueva Categoría" # Usar el input o un placeholder
        else:
            categoria_final = selected_categoria

        # Si se selecciona un producto existente, precargar sus datos
        productos_en_categoria = list(st.session_state.inventario.get(categoria_final, {}).keys())
        selected_producto_name = st.selectbox(
            "Seleccionar Producto Existente (o escribe uno nuevo)",
            options=[""] + sorted(productos_en_categoria),
            key="inv_select_producto_existente"
        )

        # Precargar datos si se selecciona un producto existente
        initial_producto_name = selected_producto_name if selected_producto_name else ""
        initial_precio = st.session_state.inventario.get(categoria_final, {}).get(initial_producto_name, {}).get('precio', 0.0)
        initial_costo = st.session_state.inventario.get(categoria_final, {}).get(initial_producto_name, {}).get('costo', 0.0)
        initial_stock = st.session_state.inventario.get(categoria_final, {}).get(initial_producto_name, {}).get('stock', 0)

        producto_name = st.text_input("Nombre del Producto", value=initial_producto_name, key="inv_producto_name")
        
        col1, col2 = st.columns(2)
        with col1:
            stock = st.number_input("Stock Disponible", min_value=0, step=1, value=initial_stock, key="inv_stock")
        with col2:
            precio = st.number_input("Precio de Venta", min_value=0.0, step=0.1, format="%.2f", value=initial_precio, key="inv_precio")
            costo = st.number_input("Costo Unitario", min_value=0.0, step=0.1, format="%.2f", value=initial_costo, key="inv_costo")
        
        submitted = st.form_submit_button("💾 Guardar Producto", type="primary")
        
        if submitted:
            if not producto_name or not categoria_final:
                st.error("El nombre del producto y la categoría son requeridos.")
                return
            
            try:
                # Si la categoría es nueva y no tiene nombre, no guardar
                if selected_categoria == nueva_categoria_option and not categoria_input:
                     st.error("Por favor, introduce un nombre para la nueva categoría.")
                     return

                # Inicializar la categoría si no existe
                if categoria_final not in st.session_state.inventario:
                    st.session_state.inventario[categoria_final] = {}
                
                st.session_state.inventario[categoria_final][producto_name] = {
                    'precio': precio,
                    'stock': stock,
                    'costo': costo
                }
                
                # Actualizar Firebase
                db.reference('/inventario').set(st.session_state.inventario)
                st.success("¡Producto actualizado correctamente!")
                time.sleep(1)
                st.rerun() # Forzar rerun para actualizar la tabla y los selects
            except Exception as e:
                st.error(f"Error al guardar el producto en Firebase: {str(e)}")
    
    # Visualización de inventario mejorada
    st.subheader("📊 Inventario Actual")
    
    inventario_df_data = []
    for categoria, productos in st.session_state.inventario.items():
        for producto, datos in productos.items():
            # Calcular margen solo si precio y costo son válidos
            margen = datos['precio'] - datos['costo'] if datos['precio'] is not None and datos['costo'] is not None else 0.0
            # Calcular valor stock solo si stock y costo son válidos
            valor_stock = datos['stock'] * datos['costo'] if datos['stock'] is not None and datos['costo'] is not None else 0.0
            
            inventario_df_data.append({
                "Categoría": categoria,
                "Producto": producto,
                "Precio": datos['precio'],
                "Costo": datos['costo'],
                "Margen": margen,
                "Stock": datos['stock'],
                "Valor Stock": valor_stock
            })
    
    df = pd.DataFrame(inventario_df_data)
    
    # Mostrar métricas resumen
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Productos", len(df))
        col2.metric("Valor Total Stock", f"${df['Valor Stock'].sum():,.2f}")
        col3.metric("Margen Promedio", f"${df['Margen'].mean():.2f}")
        
        # Mostrar tabla con filtros
        with st.expander("🔍 Filtros Avanzados"):
            filtro_categoria = st.multiselect(
                "Filtrar por categoría",
                options=sorted(df['Categoría'].unique()),
                default=sorted(df['Categoría'].unique()),
                key="inv_filtro_categoria"
            )
            filtro_stock = st.slider(
                "Filtrar por stock mínimo",
                min_value=0,
                max_value=int(df['Stock'].max()) if len(df) > 0 else 100,
                value=0,
                key="inv_filtro_stock"
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
    else:
        st.info("No hay productos en el inventario. Añade algunos usando el formulario de arriba.")

# --- Reportes Mejorados ---
def mostrar_reportes():
    """Interfaz para mostrar reportes de ventas."""
    st.header("📊 Reportes Avanzados")
    
    # Selector de fechas mejorado
    col1, col2 = st.columns(2)
    with col1:
        # Asegurarse de que la fecha de inicio no sea futura
        fecha_inicio_default = datetime.now().date().replace(day=1) # Primer día del mes actual
        if 'report_fecha_inicio' not in st.session_state:
            st.session_state.report_fecha_inicio = fecha_inicio_default
        fecha_inicio = st.date_input("Fecha de inicio", value=st.session_state.report_fecha_inicio, key="report_fecha_inicio_input")
        st.session_state.report_fecha_inicio = fecha_inicio # Actualizar estado de sesión
    with col2:
        fecha_fin_default = datetime.now().date() # Hoy
        if 'report_fecha_fin' not in st.session_state:
            st.session_state.report_fecha_fin = fecha_fin_default
        fecha_fin = st.date_input("Fecha de fin", value=st.session_state.report_fecha_fin, key="report_fecha_fin_input")
        st.session_state.report_fecha_fin = fecha_fin # Actualizar estado de sesión
    
    if fecha_fin < fecha_inicio:
        st.error("La fecha de fin no puede ser anterior a la fecha de inicio.")
        return
    
    # Filtrar ventas
    ventas_filtradas = []
    for v in st.session_state.ventas:
        try:
            venta_fecha = datetime.fromisoformat(v['fecha']).date()
            if fecha_inicio <= venta_fecha <= fecha_fin:
                ventas_filtradas.append(v)
        except ValueError:
            # Manejar ventas con formato de fecha inválido
            st.warning(f"Se encontró una venta con formato de fecha inválido y fue omitida: {v.get('fecha', 'N/A')}")
            continue
    
    if not ventas_filtradas:
        st.info("No hay ventas registradas en el período seleccionado.")
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
                hide_index=True,
                use_container_width=True # Asegurar que la tabla se expande
            )
        with col2:
            st.bar_chart(df_metodos.set_index('Método')['Total'])
    
    with tab2:
        st.subheader("🍰 Productos Vendidos")
        productos_vendidos = []
        for venta in ventas_filtradas:
            for producto, datos in venta['productos'].items():
                # Asegurarse de que 'categoria' y 'costo' existan, con valores por defecto si no
                categoria = datos.get('categoria', 'Desconocida')
                costo_unitario = datos.get('costo', 0) # Obtener costo unitario del producto en la venta
                
                productos_vendidos.append({
                    'Producto': producto,
                    'Cantidad': datos['cantidad'],
                    'Precio Unitario': datos['precio'],
                    'Total Venta': datos['cantidad'] * datos['precio'],
                    'Costo Total': datos['cantidad'] * costo_unitario,
                    'Margen Bruto': (datos['cantidad'] * datos['precio']) - (datos['cantidad'] * costo_unitario),
                    'Categoría': categoria
                })
        
        df_productos = pd.DataFrame(productos_vendidos)
        
        if not df_productos.empty:
            df_agrupado = df_productos.groupby('Producto').agg({
                'Cantidad': 'sum',
                'Total Venta': 'sum',
                'Costo Total': 'sum',
                'Margen Bruto': 'sum'
            }).sort_values('Total Venta', ascending=False).reset_index()
            
            st.dataframe(
                df_agrupado,
                column_config={
                    "Total Venta": st.column_config.NumberColumn(format="$%.2f"),
                    "Costo Total": st.column_config.NumberColumn(format="$%.2f"),
                    "Margen Bruto": st.column_config.NumberColumn(format="$%.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            st.bar_chart(df_agrupado.set_index('Producto')['Total Venta'].head(10)) # Top 10 productos
        else:
            st.info("No hay datos de productos vendidos para mostrar.")
    
    with tab3:
        st.subheader("📦 Ventas por Categoría")
        if not df_productos.empty: # Reutilizar df_productos de la pestaña anterior
            df_categorias = df_productos.groupby('Categoría').agg({
                'Cantidad': 'sum',
                'Total Venta': 'sum',
                'Costo Total': 'sum',
                'Margen Bruto': 'sum'
            }).sort_values('Total Venta', ascending=False).reset_index()
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(
                    df_categorias,
                    column_config={
                        "Total Venta": st.column_config.NumberColumn(format="$%.2f"),
                        "Costo Total": st.column_config.NumberColumn(format="$%.2f"),
                        "Margen Bruto": st.column_config.NumberColumn(format="$%.2f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            with col2:
                st.bar_chart(df_categorias.set_index('Categoría')['Total Venta'])
        else:
            st.info("No hay datos de ventas por categoría para mostrar.")
            
    # Generación de PDF mejorada
    st.subheader("📄 Exportar Reporte")
    if st.button("🖨️ Generar PDF", type="primary"):
        if not ventas_filtradas:
            st.warning("No hay ventas para generar el reporte en PDF en el período seleccionado.")
            return
        
        with st.spinner("Generando reporte..."):
            pdf_buffer = generar_reporte_pdf(ventas_filtradas, fecha_inicio, fecha_fin)
            st.download_button(
                label="⬇️ Descargar Reporte",
                data=pdf_buffer,
                file_name=f"reporte_ventas_sweetbakery_{fecha_inicio.strftime('%Y%m%d')}_a_{fecha_fin.strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

def generar_reporte_pdf(ventas, fecha_inicio, fecha_fin):
    """Genera un reporte PDF de ventas."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    story = []
    
    # Encabezado
    story.append(Paragraph("SweetBakery - Reporte de Ventas", styles['Title']))
    story.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", styles['H2']))
    story.append(Spacer(1, 24))
    
    # Resumen general
    total_ventas = sum(v['total'] for v in ventas)
    num_ventas = len(ventas)
    
    story.append(Paragraph("Resumen General", styles['H2']))
    data_resumen = [
        ["Total Ventas", f"${total_ventas:,.2f}"],
        ["N° de Transacciones", num_ventas],
        ["Ticket Promedio", f"${total_ventas/num_ventas if num_ventas > 0 else 0:.2f}"]
    ]
    t_resumen = Table(data_resumen)
    t_resumen.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t_resumen)
    story.append(Spacer(1, 24))
    
    # Ventas por Método de Pago
    story.append(Paragraph("Ventas por Método de Pago", styles['H2']))
    df_metodos = pd.DataFrame(ventas).groupby('metodo_pago')['total'].agg(['sum', 'count']).reset_index()
    df_metodos.columns = ['Método', 'Total Venta', 'Transacciones']
    data_metodos = [df_metodos.columns.tolist()] + df_metodos.values.tolist()
    
    # Formatear el total de venta para la tabla PDF
    for row_idx, row in enumerate(data_metodos):
        if row_idx > 0: # Saltar el encabezado
            row[1] = f"${row[1]:,.2f}"
            row[2] = int(row[2]) # Asegurar que las transacciones son enteros
    
    t_metodos = Table(data_metodos)
    t_metodos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F2F6')), # Un color claro para el encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(t_metodos)
    story.append(Spacer(1, 24))

    # Productos más vendidos y margen
    productos_agrupados = {}
    for venta in ventas:
        for prod_nombre, datos in venta['productos'].items():
            cantidad = datos['cantidad']
            precio_unitario = datos['precio']
            costo_unitario = datos.get('costo', 0) # Usar 0 si no se encuentra el costo

            if prod_nombre not in productos_agrupados:
                productos_agrupados[prod_nombre] = {'Cantidad': 0, 'Total Venta': 0, 'Costo Total': 0, 'Margen Bruto': 0}
            
            productos_agrupados[prod_nombre]['Cantidad'] += cantidad
            productos_agrupados[prod_nombre]['Total Venta'] += cantidad * precio_unitario
            productos_agrupados[prod_nombre]['Costo Total'] += cantidad * costo_unitario
            productos_agrupados[prod_nombre]['Margen Bruto'] += (cantidad * precio_unitario) - (cantidad * costo_unitario)

    if productos_agrupados:
        story.append(Paragraph("Detalle de Productos Vendidos", styles['H2']))
        df_productos_pdf = pd.DataFrame.from_dict(productos_agrupados, orient='index').reset_index()
        df_productos_pdf.columns = ['Producto', 'Cantidad', 'Total Venta', 'Costo Total', 'Margen Bruto']
        df_productos_pdf = df_productos_pdf.sort_values('Total Venta', ascending=False)

        data_productos = [df_productos_pdf.columns.tolist()] + df_productos_pdf.values.tolist()

        # Formatear columnas monetarias
        for row_idx, row in enumerate(data_productos):
            if row_idx > 0: # Saltar el encabezado
                row[2] = f"${row[2]:,.2f}" # Total Venta
                row[3] = f"${row[3]:,.2f}" # Costo Total
                row[4] = f"${row[4]:,.2f}" # Margen Bruto
        
        t_productos = Table(data_productos)
        t_productos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F2F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t_productos)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    main()
