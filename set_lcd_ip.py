import os
import json
import lcddriver

def get_wlanO_ip() -> str:
    ip_add = ""
    routes = json.loads(os.popen("ip -j -4 route").read())

    for r in routes:
        if r.get("dev") == "wlan0" and r.get("prefsrc"):
            ip_add = r['prefsrc']

    return ip_add



if __name__ == "__main__":
    # get wlan0 ip adress
    ip_add = get_wlanO_ip()

    # display result on LCD
    lcd = lcddriver.lcd()

    lcd.lcd_clear() 
    lcd.lcd_display_string("WLAN_0 IP:", 1)
    lcd.lcd_display_string(ip_add if ip_add != "" else "Connect hostspot", 2)


