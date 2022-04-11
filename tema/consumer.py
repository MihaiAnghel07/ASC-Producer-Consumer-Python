"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)

        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs['name']
        """Se genereaza un cos de cumparaturi pentru consumator"""
        self.cart_id = int(self.marketplace.new_cart())

    def run(self):
        """Se parcurge lista de operatii pe care le are de facut consumatorul,
        si pentru fiecare produs(respectiv cantitate de produs), se incearca adaugarea
        in cosul de cumparaturi sau eliminarea din cos. Adaugarea se face intr-o bucla
        pana cand se valideaza adaugarea
        """
        for operations in self.carts:
            for operation in operations:
                for id in range(operation['quantity']):
                    self.do_operation(operation)

        self.print_result()

    def do_operation(self, operation):
        if operation['type'] == "remove":
            self.marketplace.remove_from_cart(self.cart_id, operation['product'])
        else:
            while not self.marketplace.add_to_cart(self.cart_id, operation['product']):
                time.sleep(self.retry_wait_time)

    def print_result(self):
        bought_products_list = self.marketplace.place_order(self.cart_id)
        for bought_product in bought_products_list:
            print("%s bought %s" % (self.name, bought_product))
