const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");
const ONE_GWEI = 1_000_000_000n;

module.exports = buildModule("SupplyChainModule", (m) => {
  const supplyChain = m.contract("SupplyChain");

  const addProduct = async (name, price, stock) => {
    await supplyChain.addProduct(name, price, stock);
  };

  const listProduct = async (productId) => {
    return await supplyChain.listProduct(productId);
  };

  const placeOrder = async (productIds, quantities, value) => {
    await supplyChain.placeOrder(productIds, quantities, { value });
  };

  const updateShipment = async (orderId, location, status) => {
    await supplyChain.updateShipment(orderId, location, status);
  };

  const updateInventory = async (productId, quantity) => {
    await supplyChain.updateInventory(productId, quantity);
  };

  const setAuthorization = async (address, authorized) => {
    await supplyChain.setAuthorization(address, authorized);
  };

  const deliverOrder = async (orderId) => {
    await supplyChain.deliverOrder(orderId);
  };

  const withdraw = async () => {
    await supplyChain.withdraw();
  };

  return {
    supplyChain,
    addProduct,
    listProduct,
    placeOrder,
    updateShipment,
    updateInventory,
    setAuthorization,
    deliverOrder,
    withdraw,
  };
});
