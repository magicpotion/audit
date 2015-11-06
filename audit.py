"""
This module provides abstraction layer to message broker.
Logging module to be used with Kombu Messaging library:
https://pypi.python.org/pypi/kombu/
Requires Kombu 1.5.1 to maintain compatibility with Python 2.4.

Although designed to be used with RabbitMQ and Graylog,
it will work with any message broker and log management system.

Example:
    import audit

    message = '{"short_message":"Test", "host":"example.org"}'
    Audit = audit.Audit()
    Audit.custom_exchange(exchange='logs'...) # optional
    Audit.log(message)

"""
from kombu import BrokerConnection, Exchange


class ExchangeSetup:
    def __init__(self, exchange='logs', exchange_type='direct',
                 routing_key='log_messages'):
        """Broker exchange.

        Args:
            exchange (str): Exchange name
            exchange_type (str): AMQP exchange type, see your broker manual
            routing_key (str)
        """
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key


class Audit:
    def __init__(self, hostname='localhost', port='5672',
                 userid='', password='', virtual_host='/',
                 exchange=None):
        self.hostname = hostname
        self.port = port
        self.userid = userid
        self.password = password
        self.virtual_host = virtual_host
        self.connection = BrokerConnection()
        self.exchange_setup = exchange or ExchangeSetup()

    def custom_exchange(self, exchange, exchange_type, routing_key):
        """Broker exchange can be set after the object has been instantiated.

        Args:
            exchange (str): Exchange name
            exchange_type (str): AMQP exchange type, see your broker manual
            routing_key (str)
        """
        self.exchange_setup.exchange = exchange
        self.exchange_setup.exchange_type = exchange_type
        self.exchange_setup.routing_key = routing_key

    def log(self, message):
        """Pushes argument object to message broker.

        Args:
            message (json/gelp): Message can depend on third-party log software
                Graylog uses gelp format: https://www.graylog.org/resources/gelf/
        """
        self.connection.connect()

        channel = self.connection.channel()
        exchange = Exchange(self.exchange_setup.exchange,
                            type=self.exchange_setup.exchange_type)
        # bound queue - it is a standard to always declare it
        queue = exchange(channel)
        queue.declare(nowait=True)

        # example_message = '{"short_message":"Kombu", "host":"example.org"}'
        message = queue.Message(message)
        queue.publish(message, routing_key=self.exchange_setup.routing_key)

        self.connection.release()
