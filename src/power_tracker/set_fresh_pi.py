import json
from os.path import join as path_join
import tkinter as tk
from tkinter.filedialog import askdirectory

tk.Tk().withdraw()
boot_folder = askdirectory()

# ssh file
try:
    with open(path_join(boot_folder, 'ssh'), 'x', encoding='utf-8') as _:
        print("Created 'ssh'")
except FileExistsError:
    print('ssh file already exists.')

# edit 'config.txt'
new_config = 'dtoverlay=dwc2'
with open(path_join(boot_folder, 'config.txt'), 'r+', encoding='utf-8') as config:
    if config.readlines()[-1].strip() != new_config:
        config.write('dtoverlay=dwc2')
        print("Appended to 'config.txt'")

# edit 'cmdline.txt'
# original contents:
# console=serial0,115200 console=tty1 root=PARTUUID=4a422963-02 rootfstype=ext4 fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh splash plymouth.ignore-serial-consoles
with open(path_join(boot_folder, 'cmdline.txt'), 'r', encoding='utf-8') as cmdline:
    commands = cmdline.read().split()

new_cmd = 'modules-load=dwc2,g_ether'
rw_command = commands.index('rootwait')
if commands[rw_command + 1] != new_cmd:
    commands.insert(rw_command + 1, new_cmd)

    with open(path_join(boot_folder, 'cmdline.txt'), 'w', encoding='utf-8') as cmdline:
        cmdline.write(' '.join(commands))
        print("Added command to 'cmdline.txt'")

# create 'wpa_supplicant.conf'
with open("metadata/wifi_info.json", 'r', encoding='utf-8') as wifi_infile:
    wifi_info = json.load(wifi_infile)
WIFI_NAME = "Elizabeth House Wifi"
wifi = wifi_info[WIFI_NAME]

wpa_contents = """ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country={country}

network={{
	ssid="{SSID}"
	psk="{key}"
	key_mgmt=WPA-PSK
}}"""
with open(path_join(boot_folder, 'wpa_supplicant.conf'), 'w', encoding='utf-8') as wpa_supplicant:
    wpa_supplicant.write(wpa_contents.format(country='NZ',
                                             SSID=wifi['SSID'],
                                             key=wifi['key']))
    print("Created 'wpa_supplicant.conf'")
