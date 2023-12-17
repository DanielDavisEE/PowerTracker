import json
import os
import platform
import getpass
import re
import subprocess

PREFERRED_WIFI = "homebase2"


def createNewConnection(name=None, SSID=None, key=None):
    config = """<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>""" + name + """</name>
    <SSIDConfig>
        <SSID>
            <name>""" + SSID + """</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>""" + key + """</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    if platform.system() == "Windows":
        command = f'netsh wlan add profile filename="{name}.xml" interface=WiFi'
        with open(name + ".xml", 'w', encoding='utf-8') as file:
            file.write(config)
    elif platform.system() == "Linux":
        command = f"nmcli dev wifi connect '{SSID}' password '{key}'"
    else:
        raise OSError("OS is neither Windows nor Linux?")
    subprocess.run(command,
                   shell=True,
                   check=True)
    if platform.system() == "Windows":
        os.remove(name + ".xml")


def connect(name=None, SSID=None, key=None):
    try:
        if platform.system() == "Windows":
            command = f'netsh wlan connect name="{name}" ssid="{SSID}" interface=WiFi'
        elif platform.system() == "Linux":
            command = f"nmcli con up {SSID}"
        subprocess.run(command,
                       shell=True,
                       check=True)
    except subprocess.CalledProcessError:
        if not key:
            raise ValueError("Missing keyword argument 'key'.")
        createNewConnection(name, SSID, key)


def displayAvailableNetworks():
    if platform.system() == "Windows":
        command = "netsh wlan show networks interface=WiFi"
    elif platform.system() == "Linux":
        command = "nmcli dev wifi list"
    subprocess.run(command,
                   shell=True,
                   check=True)


def connectToKnownNetwork():
    output = subprocess.run('iwlist wlan0 scanning | grep "ESSID:"',
                            shell=True,
                            check=True,
                            capture_output=True,
                            encoding='utf-8')
    text = output.stdout
    pattern = re.compile(r'ESSID:"(.*)"')
    ssids = [re.search(pattern, n).group(1) for n in text.splitlines()]

    with open("metadata/wifi_info.json", 'r', encoding='utf-8') as wifi_infile:
        wifi_info = json.load(wifi_infile)
    if PREFERRED_WIFI in ssids:
        ssid = PREFERRED_WIFI
    else:
        for ssid in ssids:
            if ssid in wifi_info:
                break
    connect(ssid, ssid, wifi_info[ssid]['key'])


if __name__ == "__main__":
    name = "Elizabeth House Wifi"
    connect(name, name)
    try:
        displayAvailableNetworks()
        option = input("New connection (y/n)? ")
        if option.lower() == "n" or option == "":
            name = input("Name: ")
            connect(name, name)
            print("If you aren't connected to this network, try connecting with correct credentials")
        elif option.lower() == "y":
            name = input("Name: ")
            key = getpass.getpass("Password: ")
            createNewConnection(name, name, key)
            connect(name, name)
            print("If you aren't connected to this network, try connecting with correct credentials")
    except KeyboardInterrupt as e:
        print("\nExiting...")
