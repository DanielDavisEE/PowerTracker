import os
import platform
import getpass

def createNewConnection(name=None, SSID=None, key=None):
    config = """<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>"""+name+"""</name>
    <SSIDConfig>
        <SSID>
            <name>"""+SSID+"""</name>
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
                <keyMaterial>"""+key+"""</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    if platform.system() == "Windows":
        command = "netsh wlan add profile filename=\""+name+".xml\""+" interface=WiFi"
        with open(name+".xml", 'w') as file:
            file.write(config)
    elif platform.system() == "Linux":
        command = "nmcli dev wifi connect '"+SSID+"' password '"+key+"'"
    os.system(command)
    if platform.system() == "Windows":
        os.remove(name+".xml")
        
def connect(name=None, SSID=None, key=None):
    if platform.system() == "Windows":
        command = "netsh wlan connect name=\""+name+"\" ssid=\""+SSID+"\" interface=WiFi"
    elif platform.system() == "Linux":
        command = "nmcli con up "+SSID
    os.system(command)
    
def displayAvailableNetworks():
    if platform.system() == "Windows":
        command = "netsh wlan show networks interface=WiFi"
    elif platform.system() == "Linux":
        command = "nmcli dev wifi list"
    os.system(command)

if __name__ == "__main__":   
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