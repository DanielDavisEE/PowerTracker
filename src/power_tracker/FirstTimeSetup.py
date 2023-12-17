import connWiFi, os

HOUSE = "flat"
WIFI_INFO = {
    "flat": {"name": "Elizabeth House Wifi",
             "SSID": "Elizabeth House Wifi",
             "key": "setthealarm"},
    "oldflat": {"name": "DoBro Stinson",
                "SSID": "DoBro Stinson",
                "key": "Barney69"},
    "home": {"name": "homebase",
             "SSID": "homebase",
             "key": "tobycat12"},
    "homenew": {"name": "homebase2",
                "SSID": "homebase2",
                "key": "tobycat12"},
}

connWiFi.createNewConnection(**WIFI_INFO[HOUSE])
connWiFi.connect(**WIFI_INFO[HOUSE])

os.system("PowerTrackerGUI.py")
