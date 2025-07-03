import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import json
from datetime import datetime

# Inicializar Firebase
def initialize_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        # Configura tus credenciales de Firebase
        cred = credentials.Certificate("serviceAccountKey.json")  # Reemplaza con tu archivo de credenciales
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://tu-proyecto.firebaseio.com/'  # Reemplaza con tu URL de Firebase
        })

initialize_firebase()

# Estructura inicial de datos
initial_data = {
    "Pastelería": {
        "Dulce Tres Leche (porción)": {"precio": 4.30, "stock": 0, "costo": 2.15},
        "Milhojas Arequipe (porción)": {"precio": 4.30, "stock": 0, "costo": 2.15},
        # ... (todos los demás productos)
    },
    "Hojaldre": {
        # ... (todos los productos de hojaldre)
    },
    "Bebidas": {
        # ... (todas las bebidas)
    },
    "Dulces Secos": {
        # ... (todos los dulces secos)
    }
}

# Función para cargar datos iniciales (solo ejecutar una vez)
def load_initial_data():
    ref = db.reference('/inventario')
    ref.set(initial_data)
    st.success("Datos iniciales cargados correctamente!")

# Función para obtener el inventario
def get_inventory():
    ref = db.reference('/inventario')
    return ref.get()

# Función para actualizar el inventario
def update_inventory(category, product, data):
    ref = db.reference(f'/inventario/{category}/{product}')
    ref.update(data)

# Función para registrar una venta
def record_sale(items, total, payment_method):
    ref = db.reference('/ventas')
    sale_ref = ref.push()
    sale_ref.set({
        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'items': items,
        'total': total,
        'metodo_pago': payment_method
    })
    
    # Actualizar stock
    for item in items:
        category = item['categoria']
        product = item['producto']
        quantity = item['cantidad']
        
        current_data = get_inventory()[category][product]
        new_stock = current_data['stock'] - quantity
        update_inventory(category, product, {'stock': new_stock})

# Interfaz de Inventario
def inventory_interface():
    st.title("📦 Gestión de Inventario")
    
    inventory = get_inventory()
    
    # Mostrar inventario completo en una tabla
    st.subheader("Inventario Completo")
    
    # Convertir a DataFrame para mejor visualización
    inventory_list = []
    for category, products in inventory.items():
        for product, details in products.items():
            inventory_list.append({
                'Categoría': category,
                'Producto': product,
                'Precio': details['precio'],
                'Stock': details['stock'],
                'Costo': details['costo'],
                'Margen': details['precio'] - details['costo']
            })
    
    df = pd.DataFrame(inventory_list)
    
    # Configurar AgGrid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
    grid_options = gb.build()
    
    edited_df = st.data_editor(df, num_rows="dynamic")
    
    data = grid_response['data']
    edited_rows = grid_response['data'].to_dict('records')
    
    if st.button("Guardar Cambios"):
        for row in edited_rows:
            update_inventory(
                row['Categoría'],
                row['Producto'],
                {
                    'precio': row['Precio'],
                    'stock': row['Stock'],
                    'costo': row['Costo']
                }
            )
        st.success("Cambios guardados correctamente!")
    
    # Agregar nuevo producto
    st.subheader("Agregar Nuevo Producto")
    with st.form("nuevo_producto"):
        new_category = st.text_input("Categoría")
        new_product = st.text_input("Nombre del Producto")
        new_price = st.number_input("Precio", min_value=0.0, step=0.1)
        new_cost = st.number_input("Costo", min_value=0.0, step=0.1)
        new_stock = st.number_input("Stock", min_value=0, step=1)
        
        if st.form_submit_button("Agregar Producto"):
            if new_category and new_product:
                update_inventory(
                    new_category,
                    new_product,
                    {
                        'precio': new_price,
                        'costo': new_cost,
                        'stock': new_stock
                    }
                )
                st.success("Producto agregado correctamente!")
            else:
                st.error("Debes ingresar categoría y nombre del producto")

# Interfaz de Punto de Venta
def pos_interface():
    st.title("💵 Punto de Venta")
    
    inventory = get_inventory()
    cart = st.session_state.get('cart', [])
    
    # Selección de categoría
    categories = list(inventory.keys())
    selected_category = st.selectbox("Selecciona una categoría", categories)
    
    # Mostrar productos de la categoría seleccionada
    products = inventory[selected_category]
    product_names = list(products.keys())
    
    cols = st.columns(3)
    for i, product in enumerate(product_names):
        with cols[i % 3]:
            st.subheader(product)
            st.write(f"Precio: ${products[product]['precio']:.2f}")
            st.write(f"Stock: {products[product]['stock']}")
            
            if products[product]['stock'] > 0:
                if st.button(f"Agregar al carrito", key=f"add_{product}"):
                    # Verificar si ya está en el carrito
                    found = False
                    for item in cart:
                        if item['producto'] == product and item['categoria'] == selected_category:
                            item['cantidad'] += 1
                            found = True
                            break
                    
                    if not found:
                        cart.append({
                            'categoria': selected_category,
                            'producto': product,
                            'precio': products[product]['precio'],
                            'cantidad': 1
                        })
                    
                    st.session_state.cart = cart
                    st.experimental_rerun()
            else:
                st.warning("Sin stock disponible")
    
    # Mostrar carrito
    st.subheader("🛒 Carrito de Compras")
    if not cart:
        st.info("El carrito está vacío")
    else:
        total = 0
        for i, item in enumerate(cart):
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                st.write(f"{item['producto']}")
            with cols[1]:
                st.write(f"${item['precio']:.2f} c/u")
            with cols[2]:
                st.write(f"Cantidad: {item['cantidad']}")
            with cols[3]:
                if st.button("❌", key=f"remove_{i}"):
                    if item['cantidad'] > 1:
                        item['cantidad'] -= 1
                    else:
                        cart.pop(i)
                    st.session_state.cart = cart
                    st.experimental_rerun()
            
            total += item['precio'] * item['cantidad']
        
        st.write(f"## Total: ${total:.2f}")
        
        # Opciones de pago
        payment_method = st.radio("Método de pago", ["Efectivo", "Tarjeta", "Transferencia"])
        
        if st.button("Finalizar Venta"):
            # Registrar venta
            record_sale(cart, total, payment_method)
            
            # Limpiar carrito
            st.session_state.cart = []
            st.success("Venta registrada correctamente!")
            st.experimental_rerun()

# Interfaz de Reportes
def reports_interface():
    st.title("📊 Reportes de Ventas")
    
    # Obtener ventas
    ref = db.reference('/ventas')
    sales = ref.get()
    
    if not sales:
        st.info("No hay ventas registradas aún")
        return
    
    # Convertir a DataFrame
    sales_list = []
    for sale_id, sale_data in sales.items():
        sales_list.append({
            'Fecha': sale_data['fecha'],
            'Total': sale_data['total'],
            'Método de Pago': sale_data['metodo_pago'],
            'Cantidad de Productos': len(sale_data['items'])
        })
    
    df = pd.DataFrame(sales_list)
    
    # Mostrar tabla de ventas
    st.subheader("Historial de Ventas")
    st.dataframe(df)
    
    # Estadísticas
    st.subheader("Estadísticas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Ventas", f"${df['Total'].sum():.2f}")
    
    with col2:
        st.metric("Venta Promedio", f"${df['Total'].mean():.2f}")
    
    with col3:
        st.metric("Total de Transacciones", len(df))
    
    # Gráficos
    st.subheader("Ventas por Método de Pago")
    payment_counts = df['Método de Pago'].value_counts()
    st.bar_chart(payment_counts)

# Menú principal
def main():
    st.sidebar.title("Menú")
    app_mode = st.sidebar.radio("Selecciona una opción", 
                               ["Punto de Venta", "Gestión de Inventario", "Reportes de Ventas"])
    
    if app_mode == "Punto de Venta":
        pos_interface()
    elif app_mode == "Gestión de Inventario":
        inventory_interface()
    elif app_mode == "Reportes de Ventas":
        reports_interface()

if __name__ == "__main__":
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    main()
