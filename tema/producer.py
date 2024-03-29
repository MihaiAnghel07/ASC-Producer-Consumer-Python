"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)

        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.id = str(marketplace.register_producer())
        self.name = kwargs['name']

    def run(self):
        """Se face o bucla infinita in care se parcurg produsele primite ca argument,
        si cantitatile din produsele respective si se incearca publicarea produsului
        curent pana cand se valideaza publicarea, apoi se trece la urmatorul produs"""
        while True:
            for product in self.products:
                for p in range(product[1]):
                    while not self.marketplace.publish(self.id, product[0]):
                        time.sleep(self.republish_wait_time)
                        time.sleep(product[2])
