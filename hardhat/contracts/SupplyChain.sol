// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract SupplyChain {
    // Struct definitions
    struct Product {
        uint256 id;
        string name;
        uint256 price;
    }

    struct Order {
        uint256 id;
        uint256[] productIds;
        uint256[] quantities;
        uint256 total;
        address client;
        OrderStatus status;
    }

    struct Shipment {
        uint256 orderId;
        string location;
        ShipmentStatus status;
    }

    // Enum definitions
    enum OrderStatus { Placed, Shipped, Delivered }
    enum ShipmentStatus { InWarehouse, InTransit, Delivered }

    // State variables
    mapping(uint256 => Product) public products;
    mapping(uint256 => Order) public orders;
    mapping(uint256 => Shipment) public shipments;
    mapping(uint256 => uint256) public inventory;
    mapping(address => bool) public authorizedAddresses;
    mapping(uint256 => address) public productOwners;

    uint256 public productCount;
    uint256 public orderCount;
    uint256 public shipmentCount;

    address public owner;

    // Events
    event OrderPlaced(uint256 orderId);
    event ShipmentUpdated(uint256 orderId, string location, ShipmentStatus status);
    event AuthorizationChanged(address indexed _address, bool _authorized);
    event ProductAdded(uint256 indexed productId, string name, uint256 price, uint256 stock);
    event OrderDelivered(uint256 orderId);
    event OrderShipped(uint256 orderId);

    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }

    modifier onlyAuthorized() {
        require(msg.sender == owner || authorizedAddresses[msg.sender], "Unauthorized");
        _;
    }

    // Constructor to set the contract owner as authorized
    constructor() {
        owner = msg.sender;
        authorizedAddresses[owner] = true;
        for (uint256 i = 1; i <= productCount; i++) {
            productOwners[i] = msg.sender;
        }
    }

    // Function to list products
    function listProduct(uint256 _productId) public view returns (string memory, uint256, uint256) {
        require(_productId != 0, "Invalid product ID");
        Product storage product = products[_productId];
        return (product.name, product.price, inventory[_productId]);
    }

    // Function to add a new product
    function addProduct(string memory _name, uint256 _price, uint256 _stock) public onlyAuthorized {
        productCount++;
        uint256 productId = productCount;
        products[productId] = Product(productId, _name, _price);
        inventory[productId] = _stock;
        productOwners[productId] = msg.sender;
        emit ProductAdded(productCount, _name, _price, _stock);
    }

    function placeOrder(uint256[] memory _productIds, uint256[] memory _quantities) public payable {
        // Verifica si hay suficiente ether transferido para cubrir el costo total del pedido
        require(msg.value >= calculateTotalCost(_productIds, _quantities), "Insufficient payment");

        // Realiza el pedido y transfiere los pagos a los propietarios de los productos
        _processOrder(_productIds, _quantities);

        // Incrementa el contador de pedidos y emite un evento
        orderCount++;
        orders[orderCount] = Order(orderCount, _productIds, _quantities, calculateTotalCost(_productIds, _quantities), msg.sender, OrderStatus.Placed);
        shipments[orderCount] = Shipment(orderCount, "Warehouse", ShipmentStatus.InWarehouse);

        emit OrderPlaced(orders[orderCount].id);
    }

    function _processOrder(uint256[] memory _productIds, uint256[] memory _quantities) internal {
        // Realiza el pedido y maneja excepciones
        if (!_executeOrder(_productIds, _quantities)) {
            revert("Order processing failed");
        }
    }

    function _executeOrder(uint256[] memory _productIds, uint256[] memory _quantities) internal returns (bool success) {
        for (uint256 i = 0; i < _productIds.length; i++) {
            uint256 productId = _productIds[i];
            uint256 quantity = _quantities[i];
            Product storage product = products[productId];
            require(product.id != 0, "Invalid product ID");
            require(inventory[productId] >= quantity, "Insufficient inventory");

            // Actualiza el inventario
            inventory[productId] -= quantity;

            // Transfiere el pago al propietario del producto
            if (!payable(productOwners[productId]).send(product.price * quantity)) {
                // Maneja la falla de la transferencia de ether
                revert("Failed to transfer payment to product owner");
            }
        }
        return true;
    }


    function calculateTotalCost(uint256[] memory _productIds, uint256[] memory _quantities) internal view returns (uint256 totalCost) {
        for (uint256 i = 0; i < _productIds.length; i++) {
            uint256 productId = _productIds[i];
            uint256 quantity = _quantities[i];
            Product storage product = products[productId];
            require(product.id != 0, "Invalid product ID");

            // Calcula el costo total sumando el precio de cada producto multiplicado por la cantidad
            totalCost += product.price * quantity;
        }
        return totalCost;
    }

    function shipOrder(uint256 _orderId) public onlyAuthorized {
         Order storage order = orders[_orderId];
         require(order.id != 0, "Invalid order ID");
         require(order.status == OrderStatus.Placed, "Order already shipped");

         order.status = OrderStatus.Shipped;
         shipments[_orderId].status = ShipmentStatus.InTransit; // Actualiza el estado del envío
         emit OrderShipped(_orderId);
    }
    // Function to update the shipment location and status
    function updateShipment(uint256 _orderId, string memory _location, ShipmentStatus _status) public onlyAuthorized {
        Shipment storage shipment = shipments[_orderId];
        require(shipment.orderId != 0, "Invalid order ID");

        Order storage order = orders[_orderId];
        require(_status != ShipmentStatus.Delivered || order.status == OrderStatus.Shipped, "Order not shipped yet");

        shipment.location = _location;
        shipment.status = _status;

        emit ShipmentUpdated(_orderId, _location, _status);
    }

    // Function to update inventory levels (for IoT device integration)
    function updateInventory(uint256 _productId, uint256 _quantity) public onlyAuthorized {
        inventory[_productId] += _quantity;
    }

    // Function to authorize or revoke an address
    function setAuthorization(address _address, bool _authorized) public onlyOwner {
        authorizedAddresses[_address] = _authorized;
        emit AuthorizationChanged(_address, _authorized);
    }

    // Function to transfer ownership of products to the client (order delivery)
    function deliverOrder(uint256 _orderId) public onlyAuthorized {
        Order storage order = orders[_orderId];
        require(order.id != 0, "Invalid order ID");
        require(order.status == OrderStatus.Shipped, "Order not shipped yet");

        Shipment storage shipment = shipments[_orderId];
        require(shipment.status == ShipmentStatus.Delivered, "Order not delivered yet");

        order.status = OrderStatus.Delivered;
        emit OrderDelivered(_orderId);
    }

    function withdraw() public onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}
// Comentario para compilar test

