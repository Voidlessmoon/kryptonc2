import re
import ipaddress

class Validator:
    @staticmethod
    def validate_ip(ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_port(port, allow_zero=False):
        try:
            port = int(port)
            if allow_zero and port == 0:
                return True
            return 1 <= port <= 65535
        except ValueError:
            return False

    @staticmethod
    def validate_time(seconds):
        try:
            secs = int(seconds)
            return 10 <= secs <= 1300
        except ValueError:
            return False

    @staticmethod
    def validate_size(size):
        try:
            size = int(size)
            return 1 <= size <= 65500
        except ValueError:
            return False

    @staticmethod
    def validate_url(url):
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

    @staticmethod
    def validate_domain(domain):
        domain_pattern = re.compile(
            r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$',
            re.IGNORECASE
        )
        return domain_pattern.match(domain) is not None

    @staticmethod
    def is_blocked_domain(domain):
        blocked_tlds = [".gov", ".gob", ".edu", ".mil"]
        return any(domain.lower().endswith(tld) for tld in blocked_tlds)"}}}