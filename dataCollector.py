import thingy52
import sqlite3
import time
import binascii

class DBConnection:
  
  con = None
  cur = None
  dataBase = 'environment'
  fileName = dataBase + '.db'


  def __init__(self):
    self.con = sqlite3.connect(self.fileName)
    self.cur = self.con.cursor()

  def saveData(self, measurement, time):
    
    self.addData(measurement['temperature'], 
    0,0,0)
                #  measurement['humidity'],
                #  measurement['pressure'],
                #  measurement['co2']
                 

  def addData(self, temperature, humidity, pressure, co2, timestamp = None):
    #add date/time
    id = 'F6:CD:CD:6D:62:09'
    if timestamp is None:
      timestamp = int(time.time())
    self.cur.execute(f"INSERT into {self.dataBase} VALUES ({timestamp},'{id}', {temperature},{humidity}, {pressure}, {co2})")
    self.con.commit()

  def __del__(self):
    self.con.close()

class MyDelegate(thingy52.MyDelegate):

    def __init__(self):
        self.measurements = dict()


    def getCurrentMeasurement(self):
      return self.measurements


    def handleNotification(self, hnd, data):
        
        # self.callback(1,2,3,4)

        #update val in dict
    
        # Debug print repr(data)
        if (hnd == thingy52.e_temperature_handle):
            teptep = binascii.b2a_hex(data)
            temperature = self._str_to_int(teptep[:-2]) + int(teptep[-2:], 16) * 0.01
            self.measurements['temperature'] = temperature

            print(f'Notification: Temp received:  {temperature} degCelsius')
            
        elif (hnd == e_pressure_handle):
            pressure_int, pressure_dec = self._extract_pressure_data(data)
            print('Notification: Pressure received: {}.{} hPa'.format(
                        pressure_int, pressure_dec))

        elif (hnd == e_humidity_handle):
            teptep = binascii.b2a_hex(data)
            print('Notification: Humidity received: {} %'.format(self._str_to_int(teptep)))

        elif (hnd == e_gas_handle):
            eco2, tvoc = self._extract_gas_data(data)
            print('Notification: Gas received: eCO2 ppm: {}, TVOC ppb: {} %'.format(eco2, tvoc))
 
        else:
            teptep = binascii.b2a_hex(data)
            print('Notification: UNKOWN: hnd {}, data {}'.format(hnd, teptep))
#Write your own delegate

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
      minute_to_sec  = 60
      thingy.environment.configure(temp_int = 1 * second_to_ms, press_int = 60 * second_to_ms, humid_int = 60 * second_to_ms, gas_mode_int = 3)
      thingy.environment.set_temperature_notification(True)

      last_snapshot = time.time()
      while True:
        
        now = time.time()
        
        interval = 20
        if int(now - last_snapshot) > interval :
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