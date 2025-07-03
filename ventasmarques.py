import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from datetime import datetime

# Inicializar Firebase
def initialize_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://tu-proyecto.firebaseio.com/'
        })

initialize_firebase()

# Estructura de datos inicial (ejemplo reducido)
initial_data = {
    "Pastelería": {
        "Dulce Tres Leche (porción)": {"precio": 4.30, "stock": 0, "costo": 2.15},
        "Milhojas Arequipe (porción)": {"precio": 4.30, "stock": 0, "costo": 2.15}
    },
    "Hojaldre": {
        "Hojaldre de Pollo": {"precio": 3.50, "stock": 2, "costo": 1.75}
    }
}

# Función para obtener el inventario
def get_inventory():
    ref = db.reference('/inventario')
    return ref.get()

# Función para actualizar el inventario
def update_inventory(category, product, data):
    ref = db.reference(f'/inventario/{category}/{product}')
    ref.update(data)

# Función para registrar ventas
def record_sale(items, total, payment_method):
    ref = db.reference('/ventas')
    sale_ref = ref.push()
    sale_ref.set({
        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'items': items,
        'total': total,
        'metodo_pago': payment_method
    })
    
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
    
    # Editor de datos nativo de Streamlit
    st.subheader("Inventario Completo")
    edited_df = st.data_editor(
        df,
        column_config={
            "Precio": st.column_config.NumberColumn(format="%.2f"),
            "Costo": st.column_config.NumberColumn(format="%.2f"),
            "Margen": st.column_config.NumberColumn(format="%.2f")
        },
        num_rows="dynamic",
        key="inventory_editor"
    )
    
    if st.button("Guardar Cambios"):
        for index, row in edited_df.iterrows():
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
        st.rerun()
    
    # Agregar nuevo producto
    st.subheader("Agregar Nuevo Producto")
    with st.form("nuevo_producto"):
        cols = st.columns(2)
        with cols[0]:
            new_category = st.text_input("Categoría")
        with cols[1]:
            new_product = st.text_input("Nombre del Producto")
        
        cols = st.columns(3)
        with cols[0]:
            new_price = st.number_input("Precio", min_value=0.0, step=0.1, format="%.2f")
        with cols[1]:
            new_cost = st.number_input("Costo", min_value=0.0, step=0.1, format="%.2f")
        with cols[2]:
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
                st.rerun()
            else:
                st.error("Debes ingresar categoría y nombre del producto")

# Interfaz de Punto de Venta
def pos_interface():
    st.title("💵 Punto de Venta")
    
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    
    inventory = get_inventory()
    
    # Selección de categoría
    categories = list(inventory.keys())
    selected_category = st.selectbox("Selecciona una categoría", categories)
    
    # Mostrar productos
    products = inventory[selected_category]
    
    cols = st.columns(3)
    for i, (product, details) in enumerate(products.items()):
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(product)
                st.write(f"💰 Precio: ${details['precio']:.2f}")
                st.write(f"📦 Stock: {details['stock']}")
                
                if details['stock'] > 0:
                    if st.button(f"Agregar {product}", key=f"add_{product}"):
                        found = False
                        for item in st.session_state.cart:
                            if item['producto'] == product and item['categoria'] == selected_category:
                                item['cantidad'] += 1
                                found = True
                                break
                        
                        if not found:
                            st.session_state.cart.append({
                                'categoria': selected_category,
                                'producto': product,
                                'precio': details['precio'],
                                'cantidad': 1
                            })
                        st.rerun()
                else:
                    st.warning("Sin stock")

    # Carrito de compras
    st.subheader("🛒 Carrito de Compras")
    if not st.session_state.cart:
        st.info("El carrito está vacío")
    else:
        total = 0
        for i, item in enumerate(st.session_state.cart):
            cols = st.columns([4, 2, 2, 1])
            with cols[0]:
                st.write(f"**{item['producto']}**")
            with cols[1]:
                st.write(f"${item['precio']:.2f} c/u")
            with cols[2]:
                st.write(f"Cantidad: {item['cantidad']")
            with cols[3]:
                if st.button("❌", key=f"remove_{i}"):
                    if item['cantidad'] > 1:
                        item['cantidad'] -= 1
                    else:
                        st.session_state.cart.pop(i)
                    st.rerun()
            
            total += item['precio'] * item['cantidad']
        
        st.divider()
        st.markdown(f"### Total: **${total:.2f}**")
        
        # Método de pago
        payment_method = st.radio(
            "Método de pago",
            ["Efectivo", "Tarjeta", "Transferencia"],
            horizontal=True
        )
        
        if st.button("Finalizar Venta", type="primary"):
            record_sale(st.session_state.cart, total, payment_method)
            st.session_state.cart = []
            st.success("Venta registrada correctamente!")
            st.rerun()

# Interfaz de Reportes
def reports_interface():
    st.title("📊 Reportes de Ventas")
    
    ref = db.reference('/ventas')
    sales = ref.get()
    
    if not sales:
        st.info("No hay ventas registradas aún")
        return
    
    sales_list = []
    for sale_id, sale_data in sales.items():
        sales_list.append({
            'Fecha': sale_data['fecha'],
            'Total': sale_data['total'],
            'Método de Pago': sale_data['metodo_pago'],
            'Productos Vendidos': sum(item['cantidad'] for item in sale_data['items'])
        })
    
    df = pd.DataFrame(sales_list)
    
    st.subheader("Historial de Ventas")
    st.dataframe(
        df,
        column_config={
            "Total": st.column_config.NumberColumn(format="$%.2f")
        }
    )
    
    st.subheader("Estadísticas")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Ventas", f"${df['Total'].sum():.2f}")
    with col2:
        st.metric("Venta Promedio", f"${df['Total'].mean():.2f}")
    with col3:
        st.metric("Total Transacciones", len(df))
    
    st.subheader("Ventas por Método de Pago")
    st.bar_chart(df['Método de Pago'].value_counts())

# Menú principal
def main():
    st.sidebar.title("Menú Principal")
    app_mode = st.sidebar.radio(
        "Selecciona una sección",
        ["Punto de Venta", "Gestión de Inventario", "Reportes de Ventas"]
    )
    
    if app_mode == "Punto de Venta":
        pos_interface()
    elif app_mode == "Gestión de Inventario":
        inventory_interface()
    elif app_mode == "Reportes de Ventas":
        reports_interface()

if __name__ == "__main__":
    main()
