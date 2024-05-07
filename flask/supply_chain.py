import argparse
import json
from web3 import Web3, HTTPProvider

# Configuración de la conexión a la blockchain de Hardhat
w3 = Web3(HTTPProvider('http://127.0.0.1:8545/'))

# Dirección del contrato y ABI (Application Binary Interface)
contract_address = '0x5FbDB2315678afecb367f032d93F642f64180aa3'  # Reemplaza con la dirección del contrato desplegado
with open('SupplyChain.json', 'r') as file:
    contract_abi = json.load(file)

# Instancia del contrato
supply_chain = w3.eth.contract(address=contract_address, abi=contract_abi)

# Función para agregar un nuevo producto
def add_product(name, price, stock):
    account = w3.eth.accounts[0]  # Utiliza la primera cuenta de Hardhat para las transacciones
    tx_hash = supply_chain.functions.addProduct(name, price, stock).transact({'from': account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Producto agregado. Transacción: {tx_receipt['transactionHash'].hex()}")

# Función para obtener los detalles de un producto
def get_product_details(product_id):
    product_details = supply_chain.functions.listProduct(product_id).call()
    print(f"Detalles del producto {product_id}:")
    print(f"Nombre: {product_details[0]}")
    print(f"Precio: {product_details[1]}")
    print(f"Stock: {product_details[2]}")

# Función para realizar un pedido
def place_order(product_ids, quantities):
    account = w3.eth.accounts[0]  # Utiliza la primera cuenta de Hardhat para las transacciones
    total_cost = sum(supply_chain.functions.products(product_id).call()[2] * quantity for product_id, quantity in zip(product_ids, quantities))
    tx_hash = supply_chain.functions.placeOrder(product_ids, quantities).transact({'from': account, 'value': total_cost})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Pedido realizado. Transacción: {tx_receipt['transactionHash'].hex()}")

# Función para actualizar el estado de un envío
def update_shipment(order_id, location, status):
    account = w3.eth.accounts[0]  # Utiliza la primera cuenta de Hardhat para las transacciones
    tx_hash = supply_chain.functions.updateShipment(order_id, location, status).transact({'from': account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Envío actualizado. Transacción: {tx_receipt['transactionHash'].hex()}")

# Función para entregar un pedido
def deliver_order(order_id):
    account = w3.eth.accounts[0]  # Utiliza la primera cuenta de Hardhat para las transacciones
    
    # Verifica si el pedido ya ha sido enviado
    order = supply_chain.functions.orders(order_id).call()
    if order[3] != 1:  # OrderStatus.Shipped
        # Si el pedido aún no ha sido enviado, envíalo primero
        tx_hash = supply_chain.functions.shipOrder(order_id).transact({'from': account})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Pedido enviado. Transacción: {tx_receipt['transactionHash'].hex()}")
    
    # Actualiza el estado del envío a "Delivered"
    tx_hash = supply_chain.functions.updateShipment(order_id, "Delivered", 2).transact({'from': account})  # ShipmentStatus.Delivered
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Estado del envío actualizado a 'Delivered'. Transacción: {tx_receipt['transactionHash'].hex()}")
    
    # Entrega el pedido
    tx_hash = supply_chain.functions.deliverOrder(order_id).transact({'from': account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Pedido entregado. Transacción: {tx_receipt['transactionHash'].hex()}")

# Función para autorizar o revocar una dirección
def set_authorization(address, authorized):
    account = w3.eth.accounts[0]  # Utiliza la primera cuenta de Hardhat para las transacciones
    tx_hash = supply_chain.functions.setAuthorization(address, authorized).transact({'from': account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Autorización actualizada. Transacción: {tx_receipt['transactionHash'].hex()}")

# Función para retirar fondos (solo el propietario)
def withdraw():
    account = w3.eth.accounts[0]  # Utiliza la primera cuenta de Hardhat para las transacciones
    tx_hash = supply_chain.functions.withdraw().transact({'from': account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Fondos retirados. Transacción: {tx_receipt['transactionHash'].hex()}")

# Función para obtener el estado de un pedido
def get_order_status(order_id):
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
            print(f"Estado del pedido {order_id}: {status_str}")
        else:
            print(f"No se encontró un envío para el pedido {order_id}.")
    except Exception as e:
        print(f"Error al obtener el estado del pedido {order_id}: {str(e)}")

# Configuración del parser de argumentos
parser = argparse.ArgumentParser(description='Script para interactuar con el contrato de SupplyChain')
parser.add_argument('-a', '--add_product', nargs=3, metavar=('NAME', 'PRICE', 'STOCK'), help='Agregar un nuevo producto')
parser.add_argument('-d', '--get_details', type=int, metavar='PRODUCT_ID', help='Obtener detalles de un producto')
parser.add_argument('-o', '--place_order', nargs='+', type=int, metavar=('PRODUCT_ID', 'QUANTITY'), help='Realizar un pedido')
parser.add_argument('-u', '--update_shipment', nargs=3, metavar=('ORDER_ID', 'LOCATION', 'STATUS'), help='Actualizar el estado de un envío')
parser.add_argument('-e', '--deliver_order', type=int, metavar='ORDER_ID', help='Entregar un pedido')
parser.add_argument('-s', '--set_authorization', nargs=2, metavar=('ADDRESS', 'AUTHORIZED'), help='Autorizar o revocar una dirección')
parser.add_argument('-w', '--withdraw', action='store_true', help='Retirar fondos (solo el propietario)')
parser.add_argument('-os', '--order_status', type=int, metavar='ORDER_ID', help='Obtener el estado de un pedido')

args = parser.parse_args()

if args.add_product:
    name, price, stock = args.add_product
    add_product(name, int(price), int(stock))
elif args.get_details:
    product_id = args.get_details
    get_product_details(product_id)
elif args.place_order:
    product_ids = args.place_order[::2]
    quantities = args.place_order[1::2]
    place_order(product_ids, quantities)
elif args.update_shipment:
    order_id, location, status = args.update_shipment
    update_shipment(int(order_id), location, int(status))
elif args.deliver_order:
    order_id = args.deliver_order
    deliver_order(order_id)
elif args.set_authorization:
    address, authorized = args.set_authorization
    set_authorization(address, authorized.lower() == 'true')
elif args.withdraw:
    withdraw()
elif args.order_status:
    order_id = args.order_status
    get_order_status(order_id)
else:
    parser.print_help()
