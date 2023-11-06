# DRIVER FILE FOR THE WEB SERVER

from flask import Flask, render_template, request
from gpiozero import LED, MotionSensor
from flask_socketio import SocketIO, send, emit
from threading import Lock
from datetime import datetime
from time import time, ctime
# from adafruit_LCD1602 import Adafruit_CharLCD # important that files are in same directory as app file
# from PCF8574 import PCF8574_GPIO 
async_mode = None

led = LED(17)
pir_unit = MotionSensor(4)
app = Flask(__name__)
socketio = SocketIO(app)
thread = None
thread_lock = Lock()


def background_thread():
    motion_event_counter = 0
    while True:
        pir_unit.wait_for_motion()
        motion_event_counter += 1
        event_date = datetime.now().strftime("%-d %b %Y")
        event_time = datetime.now().strftime("%X %p")
        # socketio.emit('log_motion', {
        #     'time': ctime(time()), 'event_counter': motion_event_counter
        #     })        
        socketio.emit('log_motion', {
            'date': event_date,
            'time': event_time, 
            'event_counter': motion_event_counter
            })
        pir_unit.wait_for_no_motion()
        
@app.route('/')                           # determines entry point (/ is root)
def index():                              # name of route    
    return render_template('index.html')

@app.route('/toggle/', methods=['POST'])
def toggle():
    led.toggle()
    return render_template('index.html')

@app.route('/pir/', methods=['POST'])
def pir():
    data = {
        'is_active': pir_unit.is_active
    }
    return render_template('pir.html', **data)
    
@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)            
#     socketio.emit('log_motion', "connection") # good for debugging or showing initial connection

if __name__ == '__main__':                 # this block runs the web server and the app    
    # app.run(debug=True, host='0.0.0.0')    # 0.0.0.0 host means web app is accessible to any device on network
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True, host='0.0.0.0')
