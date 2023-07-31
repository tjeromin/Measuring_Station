import utime
from machine import I2C, Pin, ADC, UART

################
# LCD Display
from lib.lcd.lcd_api import LcdApi
from lib.lcd.pico_i2c_lcd import I2cLcd

I2C_ADDRESS     = 39
I2C_NUM_ROWS    = 2
I2C_NUM_COLS    = 16

PIN_I2C_SDA     = 0
PIN_I2C_SCL     = 1

i2c = I2C(0, sda=Pin(PIN_I2C_SDA), scl=Pin(PIN_I2C_SCL), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDRESS, I2C_NUM_ROWS, I2C_NUM_COLS)

lcd.custom_char(0, bytearray([0x0E, 0x1F, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1F]))

def update_display(temperature=None, humidity=None, pm25=None, pm10=None, gas=False, low_voltage=False):
    lcd.clear()
    
    lcd.move_to(0, 0)
    lcd.putstr("{:4.1f}".format(pm25) + " pm25 " + "{:2.0f}".format(temperature) + " C")
    if (low_voltage):
        lcd.move_to(15, 0)
        lcd.putchar(chr(0))
    
    lcd.move_to(0, 1)
    lcd.putstr("{:4.1f}".format(pm10) + " pm10 " + "{:2.0f}".format(humidity) + " %")
    if (gas):
        lcd.move_to(15, 1)
        lcd.putchar("!")
    
    utime.sleep(5)

################
# Temperature sensor DHT
from dht import DHT22

PIN_DHT         = 16

dht = DHT22(Pin(PIN_DHT))

def measure_dht():
    dht.measure()
    temperature = dht.temperature()
    humidity = dht.humidity()
    
    return temperature, humidity

################
# Finedust sensor SDS011
from lib.sds011.sds011 import SDS011

PIN_SDS_TX       = 12
PIN_SDS_RX       = 13

uart = UART(0, baudrate = 9600, rx = Pin(PIN_SDS_RX), tx = Pin(PIN_SDS_TX), parity=None, stop=1)
sds011 = SDS011(uart)

def measure_finedust():
    sds011.read()
    
    return sds011.pm25, sds011.pm10

################
# MQ-5 Sensor (Propan, CO, LPG, CH4, H2, Ethanol)
PIN_MQ5_A       = 0
PIN_MQ5_D       = 22
MQ5_CONV_FACTOR = 5.0 / (65535)

mq5_a = ADC(PIN_MQ5_A)
mq5_d = Pin(PIN_MQ5_D, Pin.IN)

def measure_mq5():
    value = mq5_a.read_u16() * MQ5_CONV_FACTOR
    
    return value >= 1.0

################
# Pico voltage measurement
VOLTAGE_CONV_FACTOR = 3 * 3.3 / (65535)
LOW_VOLTAGE = 4.7

Pin(25, mode=Pin.OUT, pull=Pin.PULL_DOWN).high()
Pin(29, Pin.IN)
vsys = ADC(29)

def measure_low_voltage():
    voltage = vsys.read_u16() * VOLTAGE_CONV_FACTOR
    
    return voltage < LOW_VOLTAGE

while(True):
    gas = measure_mq5()    
    temperature, humidity = measure_dht()    
    low_voltage = measure_low_voltage()    
    pm25, pm10 = measure_finedust()

    update_display(temperature, humidity, pm25, pm10, gas, low_voltage)    


