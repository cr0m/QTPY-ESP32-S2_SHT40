import time
import board
import adafruit_sht4x

# For wifi
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
import busio

POST_URL = "http://192.168.9.15:8086/write?db=TempHumid"

# I2C #######################################################################

i2c = board.I2C()  # uses board.SCL and board.SDA
sht = adafruit_sht4x.SHT4x(i2c)
print("Found SHT4x with serial number", hex(sht.serial_number))

sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
# Can also set the mode to enable heater
# sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS
print("Current mode is: ", adafruit_sht4x.Mode.string[sht.mode])

# END I2C ###################################################################

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("y u no secrets.py?!")
    raise
print("ESP32-S2 WebClient Test")
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
print("Available WiFi networks:")
for network in wifi.radio.start_scanning_networks():
    print(
        "\t%s\t\tRSSI: %d\tChannel: %d"
        % (str(network.ssid, "utf-8"), network.rssi, network.channel)
    )
wifi.radio.stop_scanning_networks()

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)
ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4) * 1000))

ct = 0
loggedtemp = 0

while True:
    ct = ct + 1
    temperature, relative_humidity = sht.measurements
    tempF = temperature * 9 / 5 + 32
    print("Temperature: %0.1f F" % tempF)
    print("Humidity: %0.1f %%" % relative_humidity)
      
    if (ct == 30):
      print("Logging Temp(%sF) & Humidity(%s%%) to InfluxDB @ %s" % (tempF, relative_humidity, POST_URL))
      ct = 0
      temp_data = "temperature,host=SHT40,room=roaming value=%s" % tempF
      humid_data = "humidity,host=SHT40,room=roaming value=%s" % relative_humidity
      temp_request = requests.post(POST_URL, data=temp_data)
      loghumid = requests.post(POST_URL, data=humid_data)
    time.sleep(1)