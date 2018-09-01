#!/usr/bin/env python3

import enum
import re
import subprocess
from datetime import datetime
from time import sleep

INTERVAL = 60
SCAN_COMMAND = ('sudo', 'nmap', '-sn', '192.168.1.1/26', '--disable-arp-ping')
ICON_ONLINE = 'notification-network-wireless-connected'
MAC_REGEX = r'([0-9a-f]{2}:?){6}'
IP_REGEX = r'([0-9]{1,3}\.){3}[0-9]{1,3}'


class Colors(enum.Enum):
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    WHITE = '\33[37m'
    RED = '\033[91m'


def scan() -> str:
    result = subprocess.run(SCAN_COMMAND, stdout=subprocess.PIPE)
    return result.stdout.decode('UTF-8')


def format_output(cmd_output: str) -> set:
    macs = [m.group(0) for m in re.finditer(MAC_REGEX, cmd_output, re.IGNORECASE)]
    ip = [i.group(0) for i in re.finditer(IP_REGEX, cmd_output)]

    result = set()
    for index, addr in enumerate(ip):
        if(index < len(macs)):
            mac = macs[index]
        else:
            mac = ''
        result.add((addr, mac))

    return result


def print_list(data: set, message='', color=Colors.WHITE, notify=False):
    for ip, mac in data:
        if notify:
            n_message = '{} online'.format(mac)
            subprocess.run(('notify-send', n_message, '-i', ICON_ONLINE))
        line = '{4}{0}\t{1}\t{2}\t{3}'.format(datetime.now().strftime('%H:%M:%S'), ip, mac, message, color.value)
        print(line)
    print('{}{}'.format(Colors.WHITE.value, '-'*80))


try:
    previous = format_output(scan())
    print_list(previous)

    while True:
        sleep(INTERVAL)
        current = format_output(scan())

        offline = previous.difference(current)
        online = current.difference(previous)

        if len(offline):
            params = {
                'data': offline,
                'color': Colors.RED,
                'notify': False,
                'message': 'offline'
            }
            print_list(**params)

        if len(online):
            params = {
                'data': online,
                'color': Colors.GREEN,
                'notify': True,
                'message': 'online'
            }
            print_list(**params)

        previous = current.copy()

except KeyboardInterrupt:
    pass
