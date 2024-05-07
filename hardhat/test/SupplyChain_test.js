const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");

/*const {
  time,
  loadFixture,
} = require("@nomicfoundation/hardhat-network-helpers");
const { ethers } = require("hardhat");*/
//const { expect } = require("chai");

describe("SupplyChain", function () {

	before(async function () {
		const { expect } = await import("chai");
		global.expect = expect;
	});

  async function deploySupplyChainFixture() {
    const [owner, otherAccount] = await ethers.getSigners();
    // const [owner] = await ethers.getSigners();
    // const otherAccount = owner.address;

    const SupplyChain = await ethers.getContractFactory("SupplyChain");
    const supplyChain = await SupplyChain.deploy();

    return { supplyChain, owner, otherAccount };
  }

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      const { supplyChain, owner } = await loadFixture(deploySupplyChainFixture);

      expect(await supplyChain.owner()).to.equal(owner.address);
    });

    it("Should authorize the owner", async function () {
      const { supplyChain, owner } = await loadFixture(deploySupplyChainFixture);

      expect(await supplyChain.authorizedAddresses(owner.address)).to.be.true;
    });
  });

  describe("Product Management", function () {
    describe("Validations", function () {
      it("Should revert if an unauthorized address tries to add a product", async function () {
        const { supplyChain, otherAccount } = await loadFixture(deploySupplyChainFixture);

        await expect(
          supplyChain.connect(otherAccount).addProduct("Product 1", 100, 10)
        ).to.be.revertedWith("Unauthorized");
      });
      
      /*await expect(
          supplyChain.connect(otherAccount).callStatic.addProduct("Product 1", 100, 10)
        ).to.be.revertedWith("Unauthorized");
      });*/

      it("Should allow an authorized address to add a product", async function () {
        const { supplyChain, owner } = await loadFixture(deploySupplyChainFixture);

        await expect(supplyChain.connect(owner).addProduct("Product 1", 100, 10))
          .to.emit(supplyChain, "ProductAdded")
          .withArgs(1, "Product 1", 100, 10);
      });
    });
  });

  describe("Order Management", function () {
    describe("Validations", function () {
      it("Should revert if the product IDs and quantities arrays have different lengths", async function () {
        const { supplyChain } = await loadFixture(deploySupplyChainFixture);

        await expect(supplyChain.placeOrder([1], [1, 2])).to.be.revertedWith("Invalid input arrays");
      });

      it("Should revert if the order includes an invalid product ID", async function () {
        const { supplyChain } = await loadFixture(deploySupplyChainFixture);

        await expect(supplyChain.placeOrder([1], [1])).to.be.revertedWith("Invalid product ID");
      });

      it("Should revert if there is insufficient inventory for the order", async function () {
        const { supplyChain, owner } = await loadFixture(deploySupplyChainFixture);

        await supplyChain.connect(owner).addProduct("Product 1", 100, 5);

        await expect(supplyChain.placeOrder([1], [10])).to.be.revertedWith("Insufficient inventory");
      });

      it("Should place an order and emit the OrderPlaced event", async function () {
        const { supplyChain, owner } = await loadFixture(deploySupplyChainFixture);

        await supplyChain.connect(owner).addProduct("Product 1", 100, 10);

        await expect(supplyChain.placeOrder([1], [5], { value: 500 }))
          .to.emit(supplyChain, "OrderPlaced")
          .withArgs(1);
      });
    });
  });

  // Add more test cases for other functions as needed
  // GeraTests
describe("Product Listing", function () {
  it("Should add a new product and emit ProductAdded event", async function () {
    const { supplyChain, owner } = await loadFixture(deploySupplyChainFixture);

    await expect(supplyChain.connect(owner).addProduct("New Product", 200, 20))
      .to.emit(supplyChain, "ProductAdded")
      .withArgs(1, "New Product", 200, 20);
  });
});

describe("Order Placement", function () {
  it("Should place a new order and emit OrderPlaced event", async function () {
    const { supplyChain, owner } = await loadFixture(deploySupplyChainFixture);

    await supplyChain.connect(owner).addProduct("Product 1", 100, 10);

    await expect(supplyChain.placeOrder([1], [3], { value: 300 }))
      .to.emit(supplyChain, "OrderPlaced")
      .withArgs(1);
  });
});

describe("Shipment Updates", function () {
  it("Should update shipment location and status", async function () {
    const { supplyChain, owner } = await loadFixture(deploySupplyChainFixture);

    await supplyChain.connect(owner).addProduct("Product 1", 100, 10);
    await supplyChain.placeOrder([1], [3], { value: 300 });

    await expect(supplyChain.connect(owner).updateShipment(1, "New Location", 1))
      .to.emit(supplyChain, "ShipmentUpdated")
      .withArgs(1, "New Location", "1");
  });
});

describe("Order Delivery", function () {
  it("Should deliver an order", async function () {
    const { supplyChain, owner } = await loadFixture(deploySupplyChainFixture);

    await supplyChain.connect(owner).addProduct("Product 1", 100, 10);
    await supplyChain.placeOrder([1], [3], { value: 300 });
    
    await supplyChain.connect(owner).updateShipment(1, "New Location", 1);
    
    await supplyChain.connect(owner).updateShipment(1, "Destination", 2);

    /*await supplyChain.connect(owner).deliverOrder(1);
    const order = await supplyChain.orders(1);
    expect(order.status).to.equal(2); // OrderStatus.Delivered*/
    
    await expect(supplyChain.connect(owner).deliverOrder(1))
      .to.emit(supplyChain, "OrderDelivered")
      .withArgs(1);
      
    const order = await supplyChain.orders(1);
    expect(order.status).to.equal(2); // OrderStatus.Shipped  
  });
});
});
