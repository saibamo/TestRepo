# E-Commerce Simulation System
# Dieses Skript simuliert eine einfache E-Commerce-Anwendung mit mehreren Klassen, 
# die miteinander interagieren, um Benutzer, Produkte, Lager, Bestellungen und Zahlungen zu verwalten.

import logging, random, datetime, subprocess
from typing import List, Dict, Optional

# 1. Logger-Klasse
# Zentralisiert alle Ausgaben von Info-, Warn- und Fehlermeldungen.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Logger:
    """Logger class to standardize logging across the system."""

    def __init__(self):
        self._logger = logging.getLogger("ECommerceSimulation")

    def log_info(self, message: str):
        self._logger.info(message)

    def log_warning(self, message: str):
        self._logger.warning(message)

    def log_error(self, message: str):
        self._logger.error(message)


# 2. NotificationService
# Simuliert das Versenden von E-Mails/Alerts (z. B. Bestellbestätigungen, Lagerwarnungen).
class NotificationService:
    """
    Notification service to simulate sending notifications to users.
    In a real system, this might integrate with email/SMS APIs.
    """

    def __init__(self, logger: Logger):
        self._logger = logger

    def send_order_confirmation(self, user_email: str, order_id: str):
        timestamp = datetime.datetime.now().isoformat()
        self._logger.log_info(f"Sending order confirmation to {user_email} for Order {order_id} at {timestamp}")
        print(f"[Notification] Order {order_id} confirmed and sent to {user_email}.")

    def send_inventory_alert(self, product_name: str, current_stock: int):
        timestamp = datetime.datetime.now().isoformat()
        self._logger.log_warning(f"Low inventory alert for {product_name}: only {current_stock} left as of {timestamp}")
        print(f"[Notification] Admin alerted: Low stock on {product_name}. Current stock: {current_stock}.")


# 3. Product-Klasse
# Repräsentiert ein Produkt mit ID, Name und Preis.
class Product:
    """Product class to represent items in the catalog."""

    def __init__(self, product_id: str, name: str, price: float):
        self.product_id = product_id
        self.name = name
        self.price = price

    def __repr__(self):
        return f"{self.name} (ID: {self.product_id}) - ${self.price:.2f}"


# 4. Inventory-Klasse
# Verwaltet Lagerbestände, Prüfen, Entfernen (Abverkauf), Nachfüllen
class Inventory:
    """
    Inventory class that holds products and their stock quantities.
    Provides methods to add, remove, check stock, and restock products.
    """

    def __init__(self, logger: Logger, notification_service: NotificationService):
        self._stock: Dict[str, int] = {}       # Produkt-ID -> Menge im Lager
        self._products: Dict[str, Product] = {}# Produkt-ID -> Product-Objekt
        self._logger = logger
        self._notifier = notification_service

    def add_product(self, product: Product, quantity: int):
        self._products[product.product_id] = product
        self._stock[product.product_id] = self._stock.get(product.product_id, 0) + quantity
        self._logger.log_info(f"Added {quantity} units of {product.name} to inventory. Total: {self._stock[product.product_id]}")

    def remove_stock(self, product_id: str, quantity: int) -> bool:
        if self._stock.get(product_id, 0) >= quantity:
            self._stock[product_id] -= quantity
            product_name = self._products[product_id].name
            self._logger.log_info(f"Removed {quantity} units of {product_name}. Remaining: {self._stock[product_id]}")
            # Wenn Restbestand < 5, löse Lagerwarnung aus
            if self._stock[product_id] < 5:
                self._notifier.send_inventory_alert(product_name, self._stock[product_id])
            return True
        else:
            self._logger.log_error(f"Insufficient stock for product ID {product_id}. Requested: {quantity}, Available: {self._stock.get(product_id, 0)}")
            return False

    def check_stock(self, product_id: str) -> int:
        return self._stock.get(product_id, 0)

    def restock(self, product_id: str, quantity: int):
        if product_id in self._products:
            self._stock[product_id] = self._stock.get(product_id, 0) + quantity
            product_name = self._products[product_id].name
            self._logger.log_info(f"Restocked {quantity} units of {product_name}. New level: {self._stock[product_id]}")
        else:
            self._logger.log_error(f"Attempted to restock unknown product ID {product_id}")

    def _interact_with_inventory_legacy_system(self, product_id: str, quantity: int):
        # Simuliert Interaktion mit einem Legacy-System (z.B. Datenbank)
        # In einer echten Anwendung könnte dies eine API
        # Example: simulate a legacy system update for inventory
        command = f"echo 'Update inventory for {product_id} by {quantity}'"
        result = self._run_command(command)
        self._logger.log_info(f"Legacy system responded: {result.decode().strip()}")

    def _run_command(self, text: str)-> bytes:
        # Simuliert das Ausführen eines Kommandos (z.B. SQL-Query)
        self._logger.log_info(f"Running command: {text}")
        answer = subprocess.check_output(text, shell=True, stderr=subprocess.STDOUT)
        return answer

# 5. User-Klasse
# Modelliert einen Kunden mit Bestellhistorie
class User:
    """User class to represent a customer in the system."""

    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self._orders: List["Order"] = []

    def place_order(self, order: "Order"):
        self._orders.append(order)

    def get_order_history(self) -> List["Order"]:
        return self._orders

    def __repr__(self):
        return f"{self.name} (User ID: {self.user_id})"


# 6. PaymentProcessor-Klasse
# Simuliert Zahlungsvorgänge mit zufälligem Erfolg/Misserfolg (~75 % Erfolg)
class PaymentProcessor:
    """
    PaymentProcessor class to simulate payment processing.
    In reality, this might connect to Stripe, PayPal, etc.
    """

    def __init__(self, logger: Logger):
        self._logger = logger

    def process_payment(self, user: User, amount: float) -> bool:
        success = random.choice([True, True, True, False])  # 75% chance of success
        if success:
            self._logger.log_info(f"Payment of ${amount:.2f} from {user.email} processed successfully.")
            return True
        else:
            self._logger.log_error(f"Payment of ${amount:.2f} from {user.email} failed.")
            return False


# 7. Order-Klasse
# Repräsentiert eine Bestellung, kümmert sich um Artikelauswahl, Gesamtberechnung, Lagerentnahme, Zahlung, 
# Markieren der Bestellung als abgeschlossen, Versenden der Bestätigungen.
class Order:
    """
    Order class to represent a customer order.
    Handles calculating totals, interacting with inventory and payment processing.
    """

    def __init__(
        self, 
        order_id: str, 
        user: User, 
        inventory: Inventory, 
        payment_processor: PaymentProcessor, 
        notifier: NotificationService, 
        logger: Logger
    ):
        self.order_id = order_id
        self.user = user
        self._items: Dict[str, int] = {}  # product_id -> quantity
        self._inventory = inventory
        self._payment_processor = payment_processor
        self._notifier = notifier
        self._logger = logger
        self._is_processed = False

    def add_item(self, product_id: str, quantity: int):
        if quantity <= 0:
            self._logger.log_error(f"Attempted to add invalid quantity {quantity} for product {product_id} in order {self.order_id}")
            return
        available = self._inventory.check_stock(product_id)
        if available < quantity:
            self._logger.log_error(f"Not enough stock for product {product_id}. Requested: {quantity}, Available: {available}")
            return
        self._items[product_id] = self._items.get(product_id, 0) + quantity
        self._logger.log_info(f"Added {quantity} of product {product_id} to order {self.order_id}")

    def calculate_total(self) -> float:
        total = 0.0
        for pid, qty in self._items.items():
            product = self._inventory._products[pid]
            total += product.price * qty
        self._logger.log_info(f"Calculated total for order {self.order_id}: ${total:.2f}")
        return total

    def process_order(self):
        if self._is_processed:
            self._logger.log_warning(f"Order {self.order_id} has already been processed.")
            return False
        # 1. Lagerbestand prüfen und reduzieren
        for pid, qty in self._items.items():
            if not self._inventory.remove_stock(pid, qty):
                self._logger.log_error(f"Order {self.order_id} failed due to stock issues.")
                return False
        # 2. Gesamt berechnen und Zahlung ausführen
        total_amount = self.calculate_total()
        if not self._payment_processor.process_payment(self.user, total_amount):
            self._logger.log_error(f"Order {self.order_id} payment failed.")
            return False
        # 3. Bestellung als verarbeitet markieren
        self._is_processed = True
        self._logger.log_info(f"Order {self.order_id} processed successfully.")
        # 4. Bestätigung an Kunden senden
        self._notifier.send_order_confirmation(self.user.email, self.order_id)
        # 5. Bestellung historisieren
        self.user.place_order(self)
        return True

    def __repr__(self):
        items_str = ", ".join([f"{pid} x{qty}" for pid, qty in self._items.items()])
        return f"Order {self.order_id} for {self.user.name}: {items_str}"


# 8. Haupt-Applikationsklasse: ECommerceApp
# Koordiniert alle Komponenten und enthält eine Beispielsimulation.
class ECommerceApp:
    """
    ECommerceApp coordinates all components to simulate user interactions.
    """

    def __init__(self):
        self._logger = Logger()
        self._notifier = NotificationService(self._logger)
        self._inventory = Inventory(self._logger, self._notifier)
        self._payment_processor = PaymentProcessor(self._logger)
        self._users: Dict[str, User] = {}

    def register_user(self, user_id: str, name: str, email: str) -> User:
        if user_id in self._users:
            self._logger.log_warning(f"User ID {user_id} already exists. Returning existing user.")
            return self._users[user_id]
        user = User(user_id, name, email)
        self._users[user_id] = user
        self._logger.log_info(f"Registered new user: {user}")
        return user

    def add_product_to_catalog(self, product_id: str, name: str, price: float, quantity: int):
        product = Product(product_id, name, price)
        self._inventory.add_product(product, quantity)

    def place_order_for_user(self, user_id: str, order_id: str, items: Dict[str, int]):
        if user_id not in self._users:
            self._logger.log_error(f"Order {order_id} creation failed. User {user_id} not found.")
            return
        user = self._users[user_id]
        order = Order(order_id, user, self._inventory, self._payment_processor, self._notifier, self._logger)
        for pid, qty in items.items():
            order.add_item(pid, qty)
        success = order.process_order()
        if not success:
            self._logger.log_error(f"Order {order_id} could not be completed for user {user_id}.")

    def restock_product(self, product_id: str, quantity: int):
        self._inventory.restock(product_id, quantity)

    def user_order_history(self, user_id: str) -> Optional[List[Order]]:
        if user_id not in self._users:
            self._logger.log_error(f"Cannot fetch order history. User {user_id} not found.")
            return None
        return self._users[user_id].get_order_history()

    def simulate(self):
        """Simulate a sequence of events in the e-commerce application."""
        # Benutzerregistrierung
        user_a = self.register_user("U001", "Alice Smith", "alice@example.com")
        user_b = self.register_user("U002", "Bob Johnson", "bob@example.com")

        # Produkte ins Inventar aufnehmen
        self.add_product_to_catalog("P100", "Laptop", 999.99, 10)
        self.add_product_to_catalog("P200", "Smartphone", 499.99, 15)
        self.add_product_to_catalog("P300", "Headphones", 79.99, 20)

        # Alice gibt eine Bestellung auf
        self.place_order_for_user("U001", "O1001", {"P100": 1, "P300": 2})

        # Bob versucht eine Bestellung mit zu wenig Stock
        self.place_order_for_user("U002", "O1002", {"P200": 16})

        # Smartphone-Lager nachfüllen und neue Bestellung
        self.restock_product("P200", 10)
        self.place_order_for_user("U002", "O1003", {"P200": 5, "P300": 1})

        # Bestellhistorien ausgeben (über Logger sichtbar)
        self._logger.log_info(f"Alice's Order History: {user_a.get_order_history()}")
        self._logger.log_info(f"Bob's Order History: {user_b.get_order_history()}")

        # Lager auf < 5 überprüfen und gegebenenfalls nachfüllen
        low_stock_products = [pid for pid, qty in self._inventory._stock.items() if qty < 5]
        for pid in low_stock_products:
            self.restock_product(pid, 10)

        self._logger.log_info("Simulation completed.")

# 9. Skript-Einstiegspunkt
if __name__ == "__main__":
    app = ECommerceApp()
    app.simulate()
