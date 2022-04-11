"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import unittest
from threading import Lock


class TestMarketplace(unittest.TestCase):

    def setUp(self):
        self.marketplace = Marketplace(2)

    def test_register_producer(self):
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.register_producer(), 2)
        self.assertEqual(self.marketplace.register_producer(), 3)

    def test_publish(self):
        product = {"product_type": "Coffee",
                   "name=": "Arabica",
                   "price=": 10,
                   "acidity": "3.13",
                   "roast_level": "MEDIUM"}
        self.assertEqual(self.marketplace.publish("1", product), True)
        self.assertEqual(self.marketplace.publish("1", product), True)
        self.assertEqual(self.marketplace.publish("1", product), False)
        self.assertEqual(self.marketplace.publish("2", product), True)
        self.assertEqual(self.marketplace.publish("2", product), True)
        self.assertEqual(self.marketplace.publish("2", product), False)

    def test_new_cart(self):
        self.assertEqual(self.marketplace.new_cart(), 1)
        self.assertEqual(self.marketplace.new_cart(), 2)
        self.assertEqual(self.marketplace.new_cart(), 3)

    def test_add_to_cart(self):
        product = {"product_type": "Coffee",
                   "name=": "Arabica",
                   "price=": 10,
                   "acidity": "3.13",
                   "roast_level": "MEDIUM"}
        self.assertEqual(self.marketplace.add_to_cart(1, product), False)
        self.assertEqual(self.marketplace.publish("1", product), True)
        self.assertEqual(self.marketplace.add_to_cart(1, product), True)
        self.assertEqual(self.marketplace.add_to_cart(2, product), False)

    def test_remove_from_cart(self):
        product = {"product_type": "Coffee",
                   "name=": "Arabica",
                   "price=": 10,
                   "acidity": "3.13",
                   "roast_level": "MEDIUM"}
        product2 = {"product_type": "Tea",
                    "name=": ":Linden",
                    "price=": 9,
                    "type=": "Herbal"}

        self.assertEqual(self.marketplace.publish("1", product), True)
        self.assertEqual(self.marketplace.publish("1", product2), True)
        self.assertEqual(self.marketplace.publish("2", product2), True)
        self.assertEqual(len(self.marketplace.reserved_products), 0, True)
        self.assertEqual(self.marketplace.add_to_cart(1, product), True)
        self.assertEqual(len(self.marketplace.reserved_products), 1, True)
        self.assertEqual(self.marketplace.add_to_cart(1, product2), True)
        self.assertEqual(len(self.marketplace.reserved_products), 2, True)
        self.marketplace.remove_from_cart(1, product)
        self.assertEqual(len(self.marketplace.reserved_products), 1, True)
        self.marketplace.remove_from_cart(1, product)
        self.assertEqual(len(self.marketplace.reserved_products), 0, True)


    def test_place_order(self):
        product = {"product_type": "Coffee",
                   "name=": "Arabica",
                   "price=": 10,
                   "acidity": "3.13",
                   "roast_level": "MEDIUM"}
        product2 = {"product_type": "Tea",
                    "name=": ":Linden",
                    "price=": 9,
                    "type=": "Herbal"}

        """Am testat lungimea listei pentru ca altfel nu am stiut cum"""
        self.assertEqual(self.marketplace.publish("1", product), True)
        self.assertEqual(self.marketplace.publish("2", product2), True)
        self.assertEqual(self.marketplace.publish("3", product), True)
        self.assertEqual(self.marketplace.publish("3", product2), True)
        self.assertEqual(self.marketplace.add_to_cart(1, product), True)
        self.assertEqual(len(self.marketplace.place_order(1)), 1, True)
        self.assertEqual(self.marketplace.add_to_cart(1, product2), True)
        self.assertEqual(len(self.marketplace.place_order(1)), 2, True)
        self.assertEqual(self.marketplace.add_to_cart(1, product), True)
        self.assertEqual(len(self.marketplace.place_order(1)), 3, True)


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):

        self.queue_size_per_producer = queue_size_per_producer
        self.lock = Lock()
        self.lock2 = Lock()
        self.lock3 = Lock()
        self.returnProducerId = 0
        self.returnCartId = 0
        """
         marketplace_products este dictionarul in care vor fi plasate produsele
         generate de producatori
        """
        self.marketplace_products = dict()
        """
        reserved_products este dictionarul in care vor fi plasate produsele
        'rezervate', adica cele luate de catre consumator, consumatorul neplasand comanda
        pana la momentul respectiv
        """
        self.reserved_products = dict()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.lock:
            self.returnProducerId = self.returnProducerId + 1
            return self.returnProducerId

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace
        :type producer_id: String
        :param producer_id: producer id
        :type product: Product
        :param product: the Product that will be published in the Marketplace
        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        with self.lock2:
            if producer_id not in self.marketplace_products.keys():
                self.marketplace_products[producer_id] = []
                self.marketplace_products[producer_id].append(product)
                return True
            elif len(self.marketplace_products[producer_id]) < self.queue_size_per_producer:
                self.marketplace_products[producer_id].append(product)
                return True

            return False

    def new_cart(self):
        """
        Creates a new cart for the consumer
        :returns an int representing the cart_id
        """
        with self.lock:
            self.returnCartId = self.returnCartId + 1
            return self.returnCartId

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns
        :type cart_id: Int
        :param cart_id: id cart
        :type product: Product
        :param product: the product to add to cart
        :returns True or False. If the caller receives False, it should wait and then try again
        """
        with self.lock3:
            """
            Se parcurge lista cu produse existente in marketplace. Daca produsul
            pe care vreau sa il adaug in cos exista in marketplace si este disponibil
            (nu este rezervat de catre alt consumator), atunci se adauga in cos
            """
            for products_values_list in self.marketplace_products.values():
                if product in products_values_list:
                    if product not in self.reserved_products.values():
                        if cart_id not in self.reserved_products.keys():
                            self.reserved_products[cart_id] = []
                            self.reserved_products[cart_id].append(product)
                            return True
                        else:
                            self.reserved_products[cart_id].append(product)
                            return True

            return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.
        :type cart_id: Int
        :param cart_id: id cart
        :type product: Product
        :param product: the product to remove from cart
        """

        """
        In momentul in care un consumator returneaza produsul, acesta este scos din lista
        de produse rezervate, deci poate fi luat de catre alt consumator
        """
        self.reserved_products[cart_id].remove(product)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.
        :type cart_id: Int
        :param cart_id: id cart
        """
        return self.reserved_products[cart_id]


if __name__ == '__main__':
    unittest.main()
