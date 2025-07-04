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
        cred = credentials.Certificate("arte-paris-api-firebase-adminsdk-fbsvc-0562938c8a.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://arte-paris-api-default-rtdb.firebaseio.com/'
        })

initialize_firebase()

# Estructura de datos inicial (ejemplo reducido)
initial_data = {
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
                st.write(f"Cantidad: {item['cantidad']}") 
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
