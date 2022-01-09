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

i2c = board.I2C()  # uses board.SCL and board.SDA
sht = adafruit_sht4x.SHT4x(i2c)
sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

try:
    from secrets import secrets
except ImportError:
    raise
wifi.radio.stop_scanning_networks()
wifi.radio.connect(secrets["ssid"], secrets["password"])

while True:
    temperature, relative_humidity = sht.measurements
    tempF = temperature * 9 / 5 + 32

    temp_data = "temperature,host=SHT40,room=roaming value=%s" % tempF
    humid_data = "humidity,host=SHT40,room=roaming value=%s" % relative_humidity
    temp_request = requests.post(POST_URL, data=temp_data)
    loghumid = requests.post(POST_URL, data=humid_data)
    time.sleep(30)