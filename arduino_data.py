import serial.tools.list_ports
import serial
import requests
isArduinoConnected = False
com_port = 0


def devicesList(isArduinoConnected, com_port):
    try:
        if serial.tools.list_ports.comports() == None:
            return isArduinoConnected, com_port
        for p in list(serial.tools.list_ports.comports()):
            port = list(p)[1]
            com_port_read = list(p)[0]
            # print(port)
            if 'Arduino' in port:
                isArduinoConnected = True
                com_port = com_port_read
        return isArduinoConnected, com_port
    except:
        print('no device connected')

# function to display line read from the comport selected with baud rate 9600


def getSerialData(com_port):
    s = serial.Serial(com_port, 9600)
    while True:
        try:
            l = s.readline()
            l = l.decode('utf-8')  # converting bytes to string of utf-8
            r = requests.post('http://127.0.0.1:5000/data',
                              json={'value': l})  # sending data to api
            print(r.text)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            try:
                s = serial.Serial(com_port, 9600)
            except:
                pass

# function to check if arduino is connected. If yes then data is acquired from it or it can check again


def checkIfArduinoConnected(isArduinoConnected, com_port):
    if(isArduinoConnected):
        print("Arduino Connected!", "press ctrl+c to stop")
        s = getSerialData(com_port)
    else:
        print("Arduino not connected")
        r = requests.post('http://127.0.0.1:5000/data',
                          json={'value': (-1)})  # sending data to api
        print(r.text)


# Calling the created functions
isArduinoConnected, com_port = devicesList(isArduinoConnected, com_port)
checkIfArduinoConnected(isArduinoConnected, com_port)
