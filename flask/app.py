from flask import Flask, render_template, request, redirect, url_for
import json
from web3 import Web3, HTTPProvider

app = Flask(__name__)

# Configuración de la conexión a la blockchain de Hardhat
w3 = Web3(HTTPProvider('http://127.0.0.1:8545/'))

# Dirección del contrato y ABI (Application Binary Interface)
contract_address = '0x5FbDB2315678afecb367f032d93F642f64180aa3'  # Reemplaza con la dirección del contrato desplegado
with open('SupplyChain.json', 'r') as file:
    contract_abi = json.load(file)

# Instancia del contrato
supply_chain = w3.eth.contract(address=contract_address, abi=contract_abi)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = int(request.form['price'])
        stock = int(request.form['stock'])
        account = w3.eth.accounts[0]
        tx_hash = supply_chain.functions.addProduct(name, price, stock).transact({'from': account})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return redirect(url_for('list_products'))
    return render_template('add_product.html')

@app.route('/list_products')
def list_products():
    product_count = supply_chain.functions.productCount().call()
    products = []
    for i in range(1, product_count + 1):
        product = supply_chain.functions.listProduct(i).call()
        products.append({'id': i, 'name': product[0], 'price': product[1], 'stock': product[2]})
    return render_template('list_products.html', products=products)

@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    if request.method == 'POST':
        product_ids = list(map(int, request.form.getlist('product_id')))
        quantities = list(map(int, request.form.getlist('quantity')))
        account = w3.eth.accounts[0]
        total_cost = sum(supply_chain.functions.products(product_id).call()[2] * quantity for product_id, quantity in zip(product_ids, quantities))
        tx_hash = supply_chain.functions.placeOrder(product_ids, quantities).transact({'from': account, 'value': total_cost})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        order_id = supply_chain.functions.orderCount().call()
        return redirect(url_for('order_status', order_id=order_id))
    product_count = supply_chain.functions.productCount().call()
    products = []
    for i in range(1, product_count + 1):
        product = supply_chain.functions.listProduct(i).call()
        products.append({'id': i, 'name': product[0], 'price': product[1], 'stock': product[2]})
    return render_template('place_order.html', products=products)

@app.route('/order_status/<int:order_id>')
def order_status(order_id):
    try:
        shipment = supply_chain.functions.shipments(order_id).call()
        if shipment[0] != 0:
            status = shipment[2]
            if status == 0:
                status_str = "In Warehouse"
            elif status == 1:
                status_str = "In Transit"
            elif status == 2:
                status_str = "Delivered"
            else:
                status_str = "Unknown"
        else:
            status_str = "Order not found"
    except Exception as e:
        status_str = f"Error: {str(e)}"
    return render_template('order_status.html', order_id=order_id, status=status_str)

if __name__ == '__main__':
    app.run(debug=True)