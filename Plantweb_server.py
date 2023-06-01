import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
from pmon import PlantMonitor
import time

ssid = 'the internet'
password = 'YouGetAStar!'
pm = PlantMonitor()

time.sleep(2) # PlantMonitor startup time



def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    count = 4
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        if count % 2 == 0:
            pico_led.on()
        else:
            pico_led.off()
        count = count + 1
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    pico_led.on()
    sleep(3)
    pico_led.off()
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

    
def webpage(temperature, humidity, wetness, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <title>Plant Station</title>
            <meta http-equiv="refresh" content="10">
            </head>
            <body>
            <p>refresh to update <p/>
            <p>Temperature is {temperature}</p>
            <p>Humidity is {humidity} <p/>
            <p>Wetness is {wetness} <p/>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            state = 'ON'
        elif request =='/lightoff?':
            pico_led.off()
            state = 'OFF'
            
        temperature = pm.get_temp()
        humidity = pm.get_humidity()
        wetness = pm.get_wetness()
    
        
        html = webpage(temperature, humidity, wetness, state)
        client.send(html)
        client.close()
        
        
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
