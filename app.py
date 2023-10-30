# DRIVER FILE FOR THE WEB SERVER

from flask import Flask, render_template, request
from gpiozero import LED
# from adafruit_LCD1602 import Adafruit_CharLCD # important that files are in same directory as app file
# from PCF8574 import PCF8574_GPIO 

led = LED(17)
app = Flask(__name__)


@app.route('/')                           # determines entry point (/ is root)
def index():                              # name of route    
    return render_template('index.html')

@app.route('/toggle/', methods=['POST'])
def toggle():
    led.toggle()
    return render_template('index.html')

if __name__ == '__main__':                 # this block runs the web server and the app
    app.run(debug=True, host='0.0.0.0')    # 0.0.0.0 host means web app is accessible to any device on network

