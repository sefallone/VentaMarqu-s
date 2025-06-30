# Importaciones necesarias
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date
import pandas as pd
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def initialize_firebase():
    if not firebase_admin._apps:
        try:
            # Verificar que todos los secrets requeridos existen
            required_keys = [
                "type", "project_id", "private_key_id", "private_key",
                "client_email", "client_id", "auth_uri", "token_uri",
                "auth_provider_x509_cert_url", "client_x509_cert_url", "databaseURL"
            ]
            
            missing_keys = [key for key in required_keys if key not in st.secrets.firebase]
            if missing_keys:
                st.error(f"Faltan configuraciones requeridas: {', '.join(missing_keys)}")
                return False

            # Formatear correctamente la clave privada
            private_key = st.secrets.firebase.private_key
            private_key = private_key.replace('\\n', '\n').strip()
            
            if not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
                private_key = "-----BEGIN PRIVATE KEY-----\n" + private_key
            if not private_key.endswith("-----END PRIVATE KEY-----"):
                private_key = private_key + "\n-----END PRIVATE KEY-----"

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

            # Validación adicional de la clave
            if "PRIVATE KEY" not in private_key or "BEGIN" not in private_key or "END" not in private_key:
                st.error("Formato de clave privada inválido")
                return False

            cred = credentials.Certificate(firebase_config)
            app = firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets.firebase.databaseURL,
                'name': 'SweetBakeryPOS'
            })

            # Prueba de conexión inmediata
            try:
                test_ref = db.reference('/connection_test', app=app)
                test_ref.set({'test': datetime.now().isoformat()})
                test_ref.delete()
            except Exception as test_error:
                st.error(f"Error en prueba de conexión: {str(test_error)}")
                firebase_admin.delete_app(app)
                return False

            return True
        except Exception as e:
            st.error(f"Error crítico inicializando Firebase: {str(e)}")
            return False
    return True
# --- Datos Iniciales (Fallback) ---
def cargar_datos_iniciales():
    """Retorna datos iniciales predefinidos para usar como fallback"""
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

# --- Funciones Optimizadas de Firebase ---
def get_firebase_data():
    """Obtiene datos de Firebase con caché y manejo de errores mejorado"""
    try:
        # Usar caché si está disponible y es reciente (menos de 2 minutos)
        cache_valid = (time.time() - st.session_state.get('last_firebase_update', 0)) < 120
        if 'inventario_cache' in st.session_state and 'ventas_cache' in st.session_state and cache_valid:
            return {
                "inventario": st.session_state.inventario_cache,
                "ventas": st.session_state.ventas_cache
            }

        # Obtener datos frescos de Firebase
        inventario_ref = db.reference('/inventario')
        ventas_ref = db.reference('/ventas')
        
        inventario_data = inventario_ref.get() or {}
        ventas_data = ventas_ref.get() or []

        # Validar estructura de datos
        if not isinstance(inventario_data, dict) or not isinstance(ventas_data, list):
            raise ValueError("Estructura de datos inválida desde Firebase")

        # Actualizar caché
        st.session_state.inventario_cache = inventario_data
        st.session_state.ventas_cache = ventas_data
        st.session_state.last_firebase_update = time.time()

        return {
            "inventario": inventario_data,
            "ventas": ventas_data
        }
    except Exception as e:
        st.warning(f"Error obteniendo datos: {str(e)}. Usando caché o datos iniciales.")
        return {
            "inventario": st.session_state.get('inventario_cache', cargar_datos_iniciales()["inventario"]),
            "ventas": st.session_state.get('ventas_cache', [])
        }

def guardar_venta(venta):
    """Guarda una venta con validación y manejo de errores mejorado"""
    if not validar_venta(venta):
        st.error("La estructura de la venta no es válida")
        return False

    try:
        ref = db.reference('/ventas')
        with st.spinner("Guardando venta..."):
            # Transacción atómica
            ventas = ref.get() or []
            ventas.append(venta)
            ref.set(ventas)
            
            # Actualizar caché local
            if 'ventas_cache' in st.session_state:
                st.session_state.ventas_cache.append(venta)
            
            st.toast("Venta registrada exitosamente", icon="✅")
            return True
    except Exception as e:
        st.error(f"Error guardando venta: {str(e)}")
        return False

def actualizar_stock(categoria, producto, cantidad):
    """Actualiza stock con transacción y validación"""
    try:
        ref = db.reference(f'/inventario/{categoria}/{producto}/stock')
        
        # Transacción atómica con validación
        def update_transaction(current):
            current = current or 0
            new_value = current - cantidad
            if new_value < 0:
                return None  # Abortar transacción
            return new_value

        success, new_value = ref.transaction(update_transaction)
        
        if success:
            # Actualizar caché local
            if 'inventario_cache' in st.session_state:
                if (categoria in st.session_state.inventario_cache and 
                    producto in st.session_state.inventario_cache[categoria]):
                    st.session_state.inventario_cache[categoria][producto]['stock'] = new_value
            return True
        else:
            st.error("No hay suficiente stock disponible")
            return False
    except Exception as e:
        st.error(f"Error actualizando stock: {str(e)}")
        return False

# --- Funciones de Validación Mejoradas ---
def validar_producto(producto):
    """Valida la estructura completa de un producto"""
    required_keys = ['precio', 'stock', 'costo']
    return (isinstance(producto, dict) and
            all(key in producto for key in required_keys) and
            isinstance(producto['precio'], (int, float)) and
            isinstance(producto['costo'], (int, float)) and
            isinstance(producto['stock'], int) and
            producto['precio'] >= 0 and
            producto['costo'] >= 0 and
            producto['stock'] >= 0)

def validar_venta(venta):
    """Valida la estructura completa de una venta"""
    required_keys = ['fecha', 'productos', 'total', 'metodo_pago']
    if not (isinstance(venta, dict) and all(key in venta for key in required_keys)):
        return False
    
    if not (isinstance(venta['total'], (int, float)) and venta['total'] >= 0):
        return False
        
    if not (isinstance(venta['productos'], dict) and len(venta['productos']) > 0):
        return False
        
    for producto, detalles in venta['productos'].items():
        required_detalles = ['cantidad', 'precio', 'categoria']
        if not (isinstance(detalles, dict) and all(key in detalles for key in required_detalles)):
            return False
            
    return True

# --- Interfaz Streamlit Mejorada ---
def main():
    """Función principal con inicialización robusta"""
    st.set_page_config(
        page_title="SweetBakery POS",
        page_icon="🍰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Inicialización del Estado Mejorada ---
    default_state = {
        "inventario": {},
        "ventas": [],
        "carrito": {},
        "metodo_pago": "Efectivo",
        "firebase_initialized": False,
        "inventario_cache": None,
        "ventas_cache": None,
        "last_firebase_update": 0,
        "last_ui_update": time.time(),
        "selected_category": None
    }

    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # --- Conexión Firebase Mejorada ---
    if not st.session_state.firebase_initialized:
        with st.spinner("Inicializando sistema..."):
            if initialize_firebase():
                st.session_state.firebase_initialized = True
                firebase_data = get_firebase_data()
                st.session_state.inventario = firebase_data["inventario"]
                st.session_state.ventas = firebase_data["ventas"]
                st.toast("Conexión con Firebase establecida", icon="✅")
            else:
                initial_data = cargar_datos_iniciales()
                st.session_state.inventario = initial_data["inventario"]
                st.session_state.ventas = initial_data["ventas"]
                st.toast("Modo offline - Usando datos locales", icon="⚠️")

    # --- Actualización Periódica Mejorada ---
    if st.session_state.firebase_initialized and (time.time() - st.session_state.last_firebase_update > 30):
        with st.spinner("Sincronizando datos..."):
            firebase_data = get_firebase_data()
            st.session_state.inventario = firebase_data["inventario"]
            st.session_state.ventas = firebase_data["ventas"]
            st.session_state.last_firebase_update = time.time()

    # --- UI Principal ---
    mostrar_estado_conexion()
    
    st.sidebar.title("🍰 SweetBakery POS")
    menu_options = ["Punto de Venta", "Gestión de Inventario", "Reportes"]
    opcion = st.sidebar.radio(
        "Menú Principal",
        menu_options,
        index=0
    )

    if opcion == "Punto de Venta":
        mostrar_punto_venta()
    elif opcion == "Gestión de Inventario":
        mostrar_inventario()
    elif opcion == "Reportes":
        mostrar_reportes()

# --- Componentes UI Mejorados ---
def mostrar_estado_conexion():
    """Muestra el estado de conexión en el sidebar"""
    status_container = st.sidebar.container()
    
    if st.session_state.firebase_initialized:
        last_update = datetime.fromtimestamp(st.session_state.last_firebase_update).strftime('%H:%M:%S')
        status_container.success(f"✅ Conectado\nÚltima sincronización: {last_update}")
    else:
        status_container.warning("⚠️ Modo offline\nUsando datos locales")
    
    status_container.progress(min(100, (time.time() - st.session_state.last_firebase_update) / 30 * 100))

def mostrar_punto_venta():
    """Interfaz del punto de venta mejorada"""
    st.header("🛒 Punto de Venta")

    # Búsqueda y selección de método de pago
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            busqueda = st.text_input(
                "🔍 Buscar producto",
                placeholder="Nombre del producto...",
                key="pv_busqueda"
            )
        with col2:
            st.session_state.metodo_pago = st.selectbox(
                "Método de Pago",
                ["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia"],
                key="pv_metodo_pago"
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
                    
                    # Mostrar precio y stock
                    card.markdown(f"💵 **Precio:** ${datos['precio']:.2f}")
                    
                    if datos['stock'] > 0:
                        stock_text = f"🟢 **Stock:** {datos['stock']}"
                        if datos['stock'] < 3:
                            stock_text += " (¡Últimas unidades!)"
                            card.warning(stock_text)
                        else:
                            card.success(stock_text)
                        
                        # Botón para añadir al carrito
                        if card.button("➕ Añadir", key=f"add_{producto}", use_container_width=True):
                            if st.session_state.inventario[categoria][producto]['stock'] > 0:
                                if producto in st.session_state.carrito:
                                    st.session_state.carrito[producto]['cantidad'] += 1
                                else:
                                    st.session_state.carrito[producto] = {
                                        'cantidad': 1,
                                        'precio': datos['precio'],
                                        'categoria': categoria,
                                        'costo': datos.get('costo', 0)
                                    }
                                
                                if actualizar_stock(categoria, producto, 1):
                                    st.rerun()
                                else:
                                    # Revertir cambios si falla la actualización
                                    if producto in st.session_state.carrito:
                                        if st.session_state.carrito[producto]['cantidad'] <= 1:
                                            del st.session_state.carrito[producto]
                                        else:
                                            st.session_state.carrito[producto]['cantidad'] -= 1
                            else:
                                st.warning(f"¡{producto} está agotado!")
                    else:
                        card.error("🔴 Agotado")
                        card.button("❌ Agotado", disabled=True, key=f"disabled_{producto}", use_container_width=True)

                col_idx = (col_idx + 1) % 3
    
    # Mostrar carrito de compras en el sidebar
    with st.sidebar:
        if st.session_state.carrito:
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
            
            # Procesar eliminación de productos
            for producto in productos_a_eliminar:
                item = st.session_state.carrito[producto]
                if actualizar_stock(item['categoria'], producto, -item['cantidad']):
                    del st.session_state.carrito[producto]
                    st.rerun()
                else:
                    st.error(f"No se pudo reponer stock para {producto}")
            
            st.divider()
            st.markdown(f"**Total a Pagar:** ${total:,.2f}")
            
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
                
                if guardar_venta(venta):
                    st.session_state.carrito = {}
                    st.success("Venta registrada exitosamente!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.info("🛒 El carrito está vacío. Añade productos para comenzar.")


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
