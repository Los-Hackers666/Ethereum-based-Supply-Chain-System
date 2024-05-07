# Interacting with the Supply Chain Smart Contract

## 📦 Preparation

1. 🛠️ Compile the contract:

```
 npx hardhat compile
```

2. 🚀 Deploy the contract on the testnet:

 a. ⚙️ Activate the local node:
 
    ```
    npx hardhat node
    ```
 
 b. 📜 Deploy the contract:
 
    ```
    npx hardhat ignition deploy ./ignition/modules/SupplyChain.js --network localhost
    ```

## 🔍 Testing with the IoT Device

1. 🆕 Add a new product:

```
 python3 IOT.py -a "Test Product" 100 10
```

2. 📋 Get product details:

```
 python3 IOT.py -d 1
```

3. 🛒 Place an order:

```
 python3 IOT.py -o 1 2
```

4. 🏭 Get order status (should be "In Warehouse"):

```
 python3 IOT.py -os 1
```

5. 🚚 Ship the order:

```
 python3 IOT.py -u 1 "In Transit" 1
```

6. 🛣️ Get order status (should be "In Transit"):

```
 python3 IOT.py -os 1
```

7. 🎉 Deliver the order:

```
 python3 IOT.py -e 1
```

8. ✅ Get order status (should be "Delivered"):

```
 python3 IOT.py -os 1
```

