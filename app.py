# DRIVER FILE FOR THE WEB SERVER

from flask import Flask, render_template, request
from newsapi import NewsApiClient
from gpiozero import LED, MotionSensor, AngularServo

import RPi.GPIO as GPIO
from flask_socketio import SocketIO, send, emit
from threading import Lock
from datetime import datetime
from time import time, ctime, sleep
from ADCDevice import *
import Freenove_DHT as DHT
import MPU6050
from adafruit_LCD1602 import Adafruit_CharLCD # important that files are in same directory as app file
from PCF8574 import PCF8574_GPIO 

async_mode = None

newsapi = NewsApiClient(api_key='287b8dfe04834dbd99cba4dd736699d5')
bbc_top_headlines = newsapi.get_top_headlines(sources='bbc-news')

# led = LED(17)
# pir_unit = MotionSensor(23)
# adc = ADCDevice() # Define an ADCDevice class object
# mpu = MPU6050.MPU6050()     # instantiate a MPU6050 class object
# accel = [0]*3               # define an arry to store accelerometer data
# gyro = [0]*3                # define an arry to store gyroscope data

PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print ('I2C Address Error !')
        exit(1)
# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
mcp.output(3,1)     # turn on LCD backlight
lcd.begin(16,2)     # set number of LCD lines and columns


app = Flask(__name__)
socketio = SocketIO(app)
# pir_thread = None
# ldr_thread = None
# mpu_thread = None
# # lcd_thread = None
# thread_lock = Lock()

# def adc_setup():
#     global adc
#     if(adc.detectI2C(0x48)): # Detect the pcf8591.
#         adc = PCF8591()
#     elif(adc.detectI2C(0x4b)): # Detect the ads7830
#         adc = ADS7830()
#     else:
#         print("No correct I2C address found, \n"
#         "Please use command 'i2cdetect -y 1' to check the I2C address! \n"
#         "Program Exit. \n");
#         exit(-1)

# def mpu_setup():
#     mpu.dmp_initialize()    # initialize MPU6050

# def ldr_background_thread():
#     while True:
#         value = adc.analogRead(0) # read the ADC value of channel 0
#         # voltage = value / 255.0 * 3.3
#         if value > 100:
#             socketio.emit('set_darkmode', 'dark mode')
#         else:
#             socketio.emit('set_lightmode', 'light mode')
#         # print ('ADC Value : %d, Voltage : %.2f'%(value,voltage))
#         sleep(0.1)

# def pir_background_thread():
#     motion_event_counter = 0
#     while True:
#         pir_unit.wait_for_motion()
#         motion_event_counter += 1
#         event_date = datetime.now().strftime("%-d %b %Y")
#         event_time = datetime.now().strftime("%X %p")       
#         socketio.emit('log_motion', {
#             'date': event_date,
#             'time': event_time, 
#             'event_counter': motion_event_counter
#             })
#         pir_unit.wait_for_no_motion()
                
# def mpu_background_thread():
#     GYRO_CONVERSION_FACTOR = 131.0
#     PRECISION = 1
#     while(True):
#         # accel = mpu.get_acceleration()      # get accelerometer data
#         gyro = mpu.get_rotation()           # get gyroscope data
#         # print("gyro[0] pitch: %d \t gyro[1] roll: %d \t gyro[2] yaw: %d" %(gyro[0], gyro[1], gyro[2]))
#         # print("gyro[0] pitch: %d \t gyro[1] roll: %d \t gyro[2] yaw: %d" %(gyro[0]/131.0, gyro[1]/131.0, gyro[2]/131.0))
#         # print("a/g:%d\t%d\t%d\t%d\t%d\t%d "%(accel[0],accel[1],accel[2],gyro[0],gyro[1],gyro[2]))
#         # print("a/g:%.2f g\t%.2f g\t%.2f g\t%.2f d/s\t%.2f d/s\t%.2f d/s"%(accel[0]/16384.0,accel[1]/16384.0,
#         #     accel[2]/16384.0,gyro[0]/131.0,gyro[1]/131.0,gyro[2]/131.0))
#         pitch = round(gyro[0] / GYRO_CONVERSION_FACTOR, PRECISION)
#         roll = round(gyro[1] / GYRO_CONVERSION_FACTOR, PRECISION)
#         yaw = round(gyro[2] / GYRO_CONVERSION_FACTOR, PRECISION)        
#         # pitch = gyro[0] / GYRO_CONVERSION_FACTOR
#         # roll = gyro[1] / GYRO_CONVERSION_FACTOR
#         # yaw = gyro[2] / GYRO_CONVERSION_FACTOR
#         socketio.emit('display_gyro_data', {
#             'pitch': pitch,
#             'roll': roll,
#             'yaw': yaw
#         })
#         # socketio.emit('display_gyro_data', 'test')
#         sleep(0.1)
   
# def lcd_background_thread():
#     while True:
#         lcd.setCursor(0,0)  # set cursor position
#         lcd.message(datetime.now().strftime('    %H:%M:%S'))   # display the time
#         sleep(1)

        
@app.route('/')                           # determines entry point (/ is root)
def index():     
    return render_template('index.html')

@app.route('/lcd/', methods=['POST'])
def lcd_page():
    headlines = bbc_top_headlines
    return render_template('lcd.html', **headlines)

@app.route('/toggle/', methods=['POST'])
def toggle():
    # led.toggle()
    return render_template('index.html')

@app.route('/pir/', methods=['POST'])
def pir():
    # data = {
    #     'is_active': pir_unit.is_active
    # }
    return render_template('pir.html',
                        #    **data
                           )

@app.route('/dht/', methods=['POST', 'GET'])
def dht():
    return render_template('dht.html')

@app.route('/mpu/', methods=['POST'])
def mpu_page():
    return render_template('mpu.html')
   

@socketio.event
def update_lcd(text):
    lcd.clear()
    lcd.message(text)
    if len(text) > 16:
        for i in range(len(text)):
            sleep(0.5)
            lcd.DisplayLeft()
        lcd.clear()
        lcd.message(text)

    # lcd.message(text)
    # if the length of text is greater than 16, then loop through the characters
    # and move left every half second
    

@socketio.event
def update_dht_clicked():
    dht = DHT.DHT(26) 
    for i in range(0,15):            
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            print("DHT11,OK!")
            break
    sleep(0.1)
    data = {
        'temperature': dht.temperature *  1.8 + 32,
        'humidity': dht.humidity,
        'time': ctime(time())
    }
    socketio.emit('log_temp_hum', data)

    
# @socketio.event
# def connect():
    # global pir_thread
    # global ldr_thread
    # global mpu_thread
    # # global lcd_thread
    # with thread_lock:
    #     if pir_thread is None:
    #         pir_thread = socketio.start_background_task(pir_background_thread)  
    #     if ldr_thread is None:
    #         ldr_thread = socketio.start_background_task(ldr_background_thread) 
    #     if mpu_thread is None:
    #         mpu_thread = socketio.start_background_task(mpu_background_thread) 
        # if lcd_thread is None:
        #     lcd_thread = socketio.start_background_task(lcd_background_thread) 
             
             
if __name__ == '__main__':                 # this block runs the web server and the app    
    # app.run(debug=True, host='0.0.0.0')    # 0.0.0.0 host means web app is accessible to any device on network
    # adc_setup()
    # mpu_setup()
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True, host='0.0.0.0')





###################################################################
### UNUSED SERVO CODE, HALF FUNCTIONAL ###
###################################################################

# servo_pin = 18

# myGPIO=18
# SERVO_DELAY_SEC = 0.001 
# myCorrection=0.0
# maxPW=(2.5+myCorrection)/1000
# minPW=(0.5-myCorrection)/1000
# servo =  AngularServo(myGPIO,initial_angle=0,min_angle=0, max_angle=180,min_pulse_width=minPW,max_pulse_width=maxPW)

# servo_on = False

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(servo_pin, GPIO.OUT)

# servo_pwm = GPIO.PWM(18, 50)
# servo_pwm.start(0)

# @app.route('/servo/test', methods=['POST'])
# def servo_test():
#     slider1 = request.form["slider1"]
#     servo_pwm.ChangeDutyCycle(float(slider1))
#     sleep(1)
#     servo_pwm.ChangeDutyCycle(0)
#     return render_template('servo.html')


# @socketio.event
# def toggle_servo(is_running):
#     socketio.emit('check_is_running', is_running)
#     while True:
#         for angle in range(0, 181, 1):   # make servo rotate from 0 to 180 deg
#             servo.angle = angle
#             sleep(SERVO_DELAY_SEC)
#         sleep(0.5)
#         for angle in range(180, -1, -1): # make servo rotate from 180 to 0 deg
#             servo.angle = angle
#             sleep(SERVO_DELAY_SEC)
#         sleep(0.5)
    
# @app.route('/servo/', methods=['POST'])
# def servo_page():

#     return render_template('servo.html')
