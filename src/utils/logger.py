import logging
from datetime import datetime
import os

class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Set up file handler
        log_file = os.path.join(log_dir, f'krypton_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatters and add it to the handlers
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        # Get the logger
        self.logger = logging.getLogger('KryptonC2')
        self.logger.setLevel(logging.INFO)

        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def debug(self, message):
        self.logger.debug(message)

    def log_attack(self, method, target, duration, status):
        self.logger.info(f"Attack - Method: {method}, Target: {target}, Duration: {duration}s, Status: {status}")

    def log_connection(self, client_ip, status):
        self.logger.info(f"Connection - IP: {client_ip}, Status: {status}")

    def log_command(self, user, command):
        self.logger.info(f"Command - User: {user}, Command: {command}")