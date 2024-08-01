from flask import Flask, render_template, jsonify
import serial
import time

app = Flask(__name__)

startMarker = '<'
endMarker = '>'
dataStarted = False
dataBuf = ""
messageComplete = False

serialPort = None

def setupSerial(baudRate, serialPortName):
    global serialPort
    serialPort = serial.Serial(port=serialPortName, baudrate=baudRate, timeout=0, rtscts=True)
    print("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))
    waitForArduino()

def sendToArduino(stringToSend):
    global startMarker, endMarker, serialPort
    stringWithMarkers = (startMarker)
    stringWithMarkers += stringToSend
    stringWithMarkers += (endMarker)
    serialPort.write(stringWithMarkers.encode('utf-8'))

def recvLikeArduino():
    global startMarker, endMarker, serialPort, dataStarted, dataBuf, messageComplete
    if serialPort.inWaiting() > 0 and not messageComplete:
        x = serialPort.read().decode("utf-8")
        if dataStarted:
            if x != endMarker:
                dataBuf += x
            else:
                dataStarted = False
                messageComplete = True
        elif x == startMarker:
            dataBuf = ''
            dataStarted = True
    if messageComplete:
        messageComplete = False
        return dataBuf
    else:
        return "XXX"

def waitForArduino():
    print("Waiting for Arduino to reset")
    msg = ""
    while "Arduino is ready" not in msg:
        msg = recvLikeArduino()
        if msg != 'XXX':
            print(msg)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send/<message>')
def send(message):
    sendToArduino(message)
    return jsonify(status="Message sent")

@app.route('/receive')
def receive():
    arduinoReply = recvLikeArduino()
    return jsonify(reply=arduinoReply)

if __name__ == '__main__':
    setupSerial(115200, "/dev/ttyACM0")
    app.run(debug=True)
