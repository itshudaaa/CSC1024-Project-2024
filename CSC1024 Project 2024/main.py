import streamlit as st
from datetime import datetime
import pandas as pd

# File paths
PRODUCTS_FILE = 'products.txt'
SUPPLIERS_FILE = 'suppliers.txt'
ORDERS_FILE = 'orders.txt'
SALES_FILE = 'sales.txt'  # New file for storing sales data

def initialize_files():
    open(PRODUCTS_FILE, 'a').close()
    open(SUPPLIERS_FILE, 'a').close()
    open(ORDERS_FILE, 'a').close()
    open(SALES_FILE, 'a').close()

initialize_files()

def load_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip().split(',') for line in file.readlines()]
    except FileNotFoundError:
        return []

def save_data(file_path, data):
    with open(file_path, 'w') as file:
        for item in data:
            file.write(','.join(item) + '\n')

# Load initial data
products = load_data(PRODUCTS_FILE)
suppliers = load_data(SUPPLIERS_FILE)
orders = load_data(ORDERS_FILE)
sales = load_data(SALES_FILE)  # Load sales data

def is_unique_id(id_to_check, existing_data):
    """Check if the ID is unique within the given dataset."""
    return id_to_check not in [item[0] for item in existing_data]

def add_supplier():
    st.subheader("Add Supplier")
    supplier_id = st.text_input("Supplier ID")
    name = st.text_input("Supplier Name")
    contact = st.text_input("Supplier Contact")

    existing_ids = [supplier[0] for supplier in suppliers]
    if supplier_id in existing_ids:
        st.error("Supplier ID already exists. Please choose a unique ID.")
        return

    if st.button("Add Supplier"):
        suppliers.append([supplier_id, name, contact])
        save_data(SUPPLIERS_FILE, suppliers)
        st.success("Supplier added successfully!")


def place_order():
    st.subheader("Place Supplier Order")

    if not suppliers:
        st.error("No suppliers available. Please add suppliers first.")
        return

    if not products:
        st.error("No products available. Please add products first.")
        return

    product_choices = [product[1] for product in products]
    supplier_choices = [supplier[1] for supplier in suppliers]

    selected_product = st.selectbox("Select Product", product_choices)
    selected_supplier = st.selectbox("Select Supplier", supplier_choices)
    quantity = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Place Order"):
        product = next((prod for prod in products if prod[1] == selected_product), None)
        supplier = next((supp for supp in suppliers if supp[1] == selected_supplier), None)

        if product and supplier:
            product_id = product[0]
            order_id = f"O{len(orders) + 1}"
            order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Validate stock quantity (ensure sufficient stock is available)
            if quantity <= 0:
                st.error("Quantity must be a positive integer.")
                return

            # Update inventory and record the order
            product[4] = str(int(product[4]) + quantity)
            save_data(PRODUCTS_FILE, products)

            orders.append([order_id, product_id, str(quantity), order_date, supplier[0]])
            save_data(ORDERS_FILE, orders)

            st.success(f"Order placed successfully! {quantity} units of {selected_product} ordered from {selected_supplier}.")


def record_sales():
    st.subheader("Record Sales")
    
    if not products:
        st.error("No products available. Please add products first.")
        return

    # Select product for the sale
    product_choices = [product[1] for product in products]
    selected_product = st.selectbox("Select Product", product_choices)

    product = next((prod for prod in products if prod[1] == selected_product), None)

    if product:
        # Validate Quantity Sold (ensure it's a positive integer)
        quantity_sold = st.number_input("Quantity Sold", min_value=1, step=1)

        # Validate dates (ensure start date is not after end date)
        start_date = st.date_input("Start Date", datetime(2024, 1, 1))
        end_date = st.date_input("End Date", datetime.now())

        if end_date < start_date:
            st.error("End date cannot be earlier than start date.")
            return

        # Proceed only if the user clicks "Record Sale"
        if st.button("Record Sale"):
            current_stock = int(product[4])

            # Check if sufficient stock is available
            if quantity_sold > current_stock:
                st.error(f"Insufficient stock! Current stock is {current_stock}.")
                return

            # Update stock and record the sale
            product[4] = str(current_stock - quantity_sold)
            save_data(PRODUCTS_FILE, products)

            # Record the sale persistently
            sales_id = f"S{len(sales) + 1}"  # Unique Sales ID
            sales.append([sales_id, product[0], product[1], str(quantity_sold), start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
            save_data(SALES_FILE, sales)

            st.success(f"Sales recorded for {selected_product}! Quantity Sold: {quantity_sold}. Remaining Stock: {product[4]}.")


def generate_reports():
    st.subheader("Reports")
    report_type = st.selectbox("Select Report Type", ["Low Stock", "Product Sales", "Supplier Orders"])

    if report_type == "Low Stock":
        threshold = st.number_input("Stock Threshold", min_value=1, step=1, value=5)
        low_stock_items = [product for product in products if int(product[4]) < threshold]
        st.write(f"Products with stock below {threshold}:")
        if low_stock_items:
            df = pd.DataFrame(low_stock_items, columns=["ID", "Name", "Description", "Price", "Stock"])
            st.table(df)
        else:
            st.info("No products with low stock.")

    elif report_type == "Product Sales":
        st.write("Product Sales Report:")
        if sales:
            sales_df = pd.DataFrame(sales, columns=["Sales ID", "Product ID", "Product Name", "Quantity Sold", "Start Date", "End Date"])
            st.table(sales_df)
        else:
            st.info("No sales recorded yet.")

    elif report_type == "Supplier Orders":
        st.write("Supplier Orders:")
        if orders:
            orders_df = pd.DataFrame(orders, columns=["Order ID", "Product ID", "Quantity", "Date", "Supplier ID"])
            st.table(orders_df)
        else:
            st.info("No orders available.")


def add_product():
    st.subheader("Add Product")
    product_id = st.text_input("Product ID")
    name = st.text_input("Product Name")
    description = st.text_input("Product Description")
    price_input = st.text_input("Product Price")
    stock_input = st.text_input("Product Stock")

    # Only perform validation if the "Add Product" button is clicked
    if st.button("Add Product"):
        # Validate Price Input
        if price_input:
            try:
                price = float(price_input)
                if price <= 0:
                    raise ValueError("Price must be a positive number.")
            except ValueError as e:
                st.error(f"Invalid price: {e}")
                return
        else:
            st.error("Price cannot be empty.")
            return

        # Validate Stock Input
        if stock_input:
            try:
                stock = int(stock_input)
                if stock < 0:
                    raise ValueError("Stock must be a non-negative integer.")
            except ValueError as e:
                st.error(f"Invalid stock: {e}")
                return
        else:
            st.error("Stock cannot be empty.")
            return

        # If no errors, proceed to add the product
        if is_unique_id(product_id, products):
            products.append([product_id, name, description, str(price), str(stock)])
            save_data(PRODUCTS_FILE, products)
            st.success("Product added successfully!")
        else:
            st.error("Product ID already exists. Please use a unique ID.")


# Streamlit Interface
st.title("Inventory Management System")

menu = ["Add Product", "Update Product", "Record Sales", "View Inventory", "Generate Reports", "Place Supplier Order", "Add Supplier"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Product":
    add_product()
elif choice == "Update Product":
    st.subheader("Update Product")
    product_id = st.text_input("Enter Product ID to Update")

    if product_id:
        product = next((prod for prod in products if prod[0] == product_id), None)
        if product:
            name = st.text_input("New Product Name", value=product[1])
            description = st.text_input("New Product Description", value=product[2])
            price = st.text_input("New Product Price", value=product[3])
            stock = st.text_input("New Product Stock", value=product[4])

            if st.button("Update Product"):
                product[1] = name
                product[2] = description
                product[3] = price
                product[4] = stock
                save_data(PRODUCTS_FILE, products)
                st.success(f"Product {product_id} updated successfully!")
        else:
            st.error("Product not found. Please check the ID.")

elif choice == "Record Sales":
    record_sales()
elif choice == "View Inventory":
    st.subheader("View Inventory")
    if not products:
        st.info("No products available in inventory.")
    else:
        inventory_df = pd.DataFrame(products, columns=["ID", "Name", "Description", "Price", "Stock"])
        st.table(inventory_df)
elif choice == "Generate Reports":
    generate_reports()
elif choice == "Place Supplier Order":
    place_order()
elif choice == "Add Supplier":
    add_supplier()
