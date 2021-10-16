import thingy52
import sqlite3
import time
import binascii

class DBConnection:
  
  dataBase = 'environment'
  fileName = dataBase + '.db'


  def __init__(self):
    self.con = sqlite3.connect(self.fileName)
    self.cur = self.con.cursor()

  def saveData(self, measurement, time):
    
    self.addData(measurement['temperature'], 
                 measurement['humidity'],
                 measurement['pressure'],
                 measurement['eco2'],
                 measurement['tvoc'],
                 measurement['battery'])
                 

  def addData(self, temperature, humidity, pressure, eco2, tvoc, battery, timestamp = None):
    #add date/time
    id = 'F6:CD:CD:6D:62:09'
    if timestamp is None:
      timestamp = int(time.time())
    self.cur.execute(f"INSERT into {self.dataBase} VALUES ({timestamp},'{id}', {temperature},{humidity}, {pressure}, {eco2}, {tvoc}, {battery})")
    self.con.commit()

  def __del__(self):
    self.con.close()

class MyDelegate(thingy52.MyDelegate):

    def __init__(self):
      self.measurements = dict()
      self.measurements['eco2'] = 0
      self.measurements['tvoc'] = 0
      self.measurements['battery'] = 100
      self.measurements['temperature'] = 23.0
      self.measurements['pressure'] = 1000.0
      self.measurements['humidity'] = 60

    def addBatteryMeasurement(self, battery_level):
      self.measurements['battery'] = battery_level

    def getCurrentMeasurement(self):
      return self.measurements


    def handleNotification(self, handle, data):
        
        if (handle == thingy52.e_temperature_handle):
            teptep = binascii.b2a_hex(data)
            temperature = self._str_to_int(teptep[:-2]) + int(teptep[-2:], 16) * 0.01
            self.measurements['temperature'] = temperature

            print(f'Notification: Temp received:  {temperature} degCelsius')
            
        elif (handle == thingy52.e_pressure_handle):
            pressure_int, pressure_dec = self._extract_pressure_data(data)
            pressure = pressure_int + pressure_dec * 0.01
            self.measurements['pressure'] = pressure

            print(f'Notification: Pressure received: {pressure} hPa')

        elif (handle == thingy52.e_humidity_handle):
            humidity = int(binascii.b2a_hex(data),16)
            self.measurements['humidity'] = humidity

            print(f'Notification: Humidity received: {humidity} %')

        elif (handle == thingy52.e_gas_handle):
            eco2, tvoc = self._extract_gas_data(data)
            self.measurements['eco2'] = eco2
            self.measurements['tvoc'] = tvoc

            print(f'Notification: Gas received: eCO2 ppm: {eco2}, TVOC ppb: {tvoc} %')

        else:
            print(f'Notification: UNKOWN: handle {handle}')


def main():
    thingy = thingy52.Thingy52('F6:CD:CD:6D:62:09') 
    delegate = MyDelegate()
    thingy.setDelegate(delegate)
    
    db = DBConnection()
  
    try:
      
      thingy.ui.enable()
      thingy.ui.set_led_mode_off()

      thingy.environment.enable()

      second_to_ms = 1000
      thingy.environment.configure(temp_int =  5* 60 * second_to_ms,
                                  press_int = 5 * 60 * second_to_ms,
                                  humid_int = 5 * 60 * second_to_ms,
                                  gas_mode_int = 3)
      thingy.environment.set_temperature_notification(True)
      thingy.environment.set_gas_notification(True)
      thingy.environment.set_humidity_notification(True)
      thingy.environment.set_pressure_notification(True)

      thingy.battery.enable()


      last_snapshot = time.time()
      while True:
        
        now = time.time()
        
        interval = 20
        if int(now - last_snapshot) > interval :
          delegate.addBatteryMeasurement(thingy.battery.read())
          print("saving data to DB")
          last_snapshot = now
          db.saveData(delegate.getCurrentMeasurement(), now)



        thingy.waitForNotifications(10)

    except Exception as e:
      print (e)
      thingy.disconnect()


def test():
  db = DBConnection()

  db.addData(1,2,3,4, int(time.time()-60))
  db.addData(2,1,3,10, int(time.time()-120))
  db.addData(3,1,3,10, int(time.time()-240))
  db.addData(1,0,3,4, int(time.time()-300))


main()