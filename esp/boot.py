# MP Reference: https://docs.micropython.org/en/latest/esp8266/quickref.html
# https://docs.micropython.org/en/latest/library/machine.html
import network
import utime

from cred import WIFI_SSID, WIFI_PASS

wlan = network.WLAN(network.STA_IF)  # create station interface
wlan.active(True)
print("Connecting...")
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    utime.sleep_ms(200)
    print('Waiting for Wi-Fi connection...')
# wlan.scan()             # scan for access points
# wlan.isconnected()      # check if the station is connected to an AP
mac = wlan.config('mac')  # get the interface's MAC adddress
for b in mac:
    print('%02x' % b, end=':')
print(wlan.ifconfig())    # get the interface's IP/netmask/gw/DNS addresses

# ap = network.WLAN(network.AP_IF) # create access-point interface
# ap.active(True)         # activate the interface
# ap.config(essid='ESP-AP') # set the ESSID of the access point