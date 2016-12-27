# Micropython Http Temperature Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

class Display():
    def __init__(self):
        self.d = None
        try:
            import ssd1306
            from machine import I2C, Pin
            i2c = I2C(sda=Pin(4), scl=Pin(5))
            self.d = ssd1306.SSD1306_I2C(64, 48, i2c, 60)
            print ("Display available")
        except Exception as e:
            print ("Display just print")
            self.d = None

    def display(self, text, text1='', text2='', text3='', text4=''):
        if self.d :
            self.d.fill(0)
            if text:  self.d.text(text,0, 0, 1)
            if text1: self.d.text(text1,0, 10, 1)
            if text2: self.d.text(text2,0, 20, 1)
            if text3: self.d.text(text3,0, 30, 1)
            if text4: self.d.text(text4,0, 40, 1)
            self.d.show()
        else:
            print(text, text1, text2, text3, text4)

display = Display()
