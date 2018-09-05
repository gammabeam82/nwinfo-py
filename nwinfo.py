#!/usr/bin/env python3

import enum
import re
import subprocess
from datetime import datetime
from time import sleep

INTERVAL = 60
STORAGE_FILE = './known-devices.txt'


class Network:
    SCAN_COMMAND = ('sudo', 'nmap', '-sn','192.168.1.1/26', '--disable-arp-ping')
    MAC_REGEX = r'([0-9a-f]{2}:?){6}'
    IP_REGEX = r'([0-9]{1,3}\.){3}[0-9]{1,3}'

    def scan(self) -> set:
        result = subprocess.run(self.SCAN_COMMAND, stdout=subprocess.PIPE)
        cmd_output = result.stdout.decode('UTF-8')
        return self.parse(cmd_output)

    def parse(self, raw_output: str) -> set:
        macs = [m.group(0) for m in re.finditer(self.MAC_REGEX, raw_output, re.IGNORECASE)]
        ip = [i.group(0) for i in re.finditer(self.IP_REGEX, raw_output)]

        result = set()
        for index, addr in enumerate(ip):
            mac = macs[index] if index < len(macs) else ''
            result.add((addr, mac))
        return result


class Storage:
    DEFAULT_DEVICE_NAME = 'Unknown'

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.load_known_devices()

    def load_known_devices(self) -> None:
        self.devices = dict()
        with open(self.filename, 'a+') as file:
            file.seek(0)
            for line in file:
                mac, name = line.split('>')
                self.devices[mac.strip()] = name.strip()

    def add_device(self, mac: str) -> None:
        with open(self.filename, 'a+') as file:
            file.write('{} > {}\n'.format(mac, self.DEFAULT_DEVICE_NAME))
            self.load_known_devices()

    def get_device_name(self, mac: str) -> str:
        device_name = self.DEFAULT_DEVICE_NAME
        if len(mac):
            if mac in self.devices:
                device_name = self.devices.get(mac)
            else:
                self.add_device(mac)
        return device_name


class Colors(enum.Enum):
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    WHITE = '\33[37m'
    RED = '\033[91m'


class Notifier():
    ICON_ONLINE = 'notification-network-wireless-connected'

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def process_list(self, data: set, message='', color=Colors.WHITE, desktop_notify=False) -> None:
        for ip, mac in data:
            device_name = self.storage.get_device_name(mac)
            if desktop_notify:
                desktop_message = '{} online'.format(device_name)
                subprocess.run(('notify-send', desktop_message, '-i', self.ICON_ONLINE))
            mac = mac if len(mac) else " " * 17
            line = '{}{}\t{}\t{}\t{}\t{}'.format(
                color.value,
                datetime.now().strftime('%H:%M:%S'),
                ip,
                mac,
                message,
                device_name
            )
            print(line)
        print('{}{}'.format(Colors.WHITE.value, '-' * 120))


scanner = Network()
storage = Storage(STORAGE_FILE)
notifier = Notifier(storage)


try:
    previous = scanner.scan()
    notifier.process_list(data=previous)

    while True:
        sleep(INTERVAL)
        current = scanner.scan()

        offline = previous.difference(current)
        online = current.difference(previous)

        if len(offline):
            params = {
                'data': offline,
                'color': Colors.RED,
                'message': 'offline'
            }
            notifier.process_list(**params)

        if len(online):
            params = {
                'data': online,
                'color': Colors.GREEN,
                'desktop_notify': True,
                'message': 'online'
            }
            notifier.process_list(**params)

        previous = current.copy()

except KeyboardInterrupt:
    pass
