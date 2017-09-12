#!/usr/bin/python
from __future__ import unicode_literals
import sys
import argparse
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import time
import glob
import serial
import struct

from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

global EE16A_SCAN_DELAY
EE16A_SCAN_DELAY = 1000 #10000 #Total time to delay for at start of scan in miliseconds 
EE16A_SCAN_DELAY_USER = 0

DEFAULT_WIDTH = 1240
DEFAULT_HEIGHT = 760
global serial_count

BAUD_RATE = 9600

help_menu = """Quit: press [Esc], [Ctrl+Q], or [Ctrl+W] at any time to exit\n
Help: press [H] to show this help menu\n
Fullscreen: press [F] to toggle full screen mode\n
Start scanning: press [Enter] start or continue scanning\n
Pause scanning: press [Space] to pause  scanning"""

def serial_ports():
  """Lists serial ports

  Raises:
  EnvironmentError:
      On unsupported or unknown platforms
  Returns:
      A list of available serial ports
  """
  if sys.platform.startswith('win'):
      ports = ['COM' + str(i + 1) for i in range(256)]

  elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
      # this is to exclude your current terminal "/dev/tty"
      ports = glob.glob('/dev/tty[A-Za-z]*')

  elif sys.platform.startswith('darwin'):
      ports = glob.glob('/dev/tty.*')

  else:
      raise EnvironmentError('Unsupported platform')

  result = []
  for port in ports:
      try:
          s = serial.Serial(port)
          s.close()
          result.append(port)
      except (OSError, serial.SerialException):
          pass
  return result

def serial_write(ser, data):
  global serial_count
  if sys.platform.startswith('win'):
    ser.write([data,])
  else:
    ser.write(str(data))

class Mask(QtGui.QWidget):
  def __init__(self, ser, fps=10, width=40, height=30, infile="imaging_mask.npy", outfile="data/sensor_readings"):
    super(Mask, self).__init__()

    # Set up shortcuts to close the program
    QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self, self.close)
    QtGui.QShortcut(QtGui.QKeySequence("Ctrl+W"), self, self.close)
    QtGui.QShortcut(QtGui.QKeySequence("Ctrl+C"), self, self.close)
    QtGui.QShortcut(QtGui.QKeySequence("Ctrl+D"), self, self.close)
    QtGui.QShortcut(QtGui.QKeySequence("Esc"), self, self.close)
    QtGui.QShortcut(QtGui.QKeySequence("H"), self, self.help)

    self.ser = ser       # Serial port
    self.scan_rate = fps # Scan rate in fps (each pixel movement = 1 frame)
    self.N = width       # Matrix width
    self.M = height      # Matrix height
    self.mask_file = infile
    self.out_file = outfile

    self.width = DEFAULT_WIDTH   # Display width
    self.height = DEFAULT_HEIGHT # Display height
    self.count = 0
    self.runs = 0
    self.started= False
    self.fullscreen = True
    self.sensor_readings = np.zeros(self.M*self.N)
    self.sensor_readings_final = np.zeros(self.M*self.N)
    self.time0 = 0 #will be used to time scan
    self.time_final = 0
    self.fp_flag = 0

    self.initUI()

  def initUI(self):
     # global EE16A_SCAN_DELAY
     # Choose a display
     print("Detected %d screens"%QtGui.QDesktopWidget().numScreens())
     if QtGui.QDesktopWidget().numScreens() == 1:
       print("Projector not detected. Please check the connection and try again.")
       if input("Continue? [y/n]").capitalize() != "Y":
         quit()
     print("Currently displaying on screen %d"%(QtGui.QDesktopWidget().screenNumber()+1))

     for s in range(QtGui.QDesktopWidget().numScreens()):
        print("%d) %dx%d"%(s+1, QtGui.QDesktopWidget().screenGeometry(s).width(),
           QtGui.QDesktopWidget().screenGeometry(s).height()))
     self.screen = int(input("Select the projector screen: "))-1

     # Set window size and center
     self.resize(self.width, self.height)
     self.center()

     
     # Load the imaging mask
     self.Hr = np.load(self.mask_file)*255

     # Create a label (used to display the image)
     self.label = QtGui.QLabel(self)

     # Set the window title
     #self.setWindowTitle('EE16A Imaging Lab')
     self.col = QtGui.QColor(0, 0, 0) 
     # Display the first frame
     self.label.setGeometry(QtCore.QRect(0, 0, self.width, self.height))
     mask = np.reshape(self.Hr[:,0], (self.M, self.N))
     mask = np.require(mask, np.uint8, 'C')
     
     QI=QtGui.QImage(mask.data, self.N, self.M, QtGui.QImage.Format_Indexed8)
     self.label.setPixmap(QtGui.QPixmap.fromImage(QI).scaled(self.width,
       self.height))
     time.sleep(.5)


     # Set up the timer
     self.timer = QtCore.QTimer()
     self.showNormal()
     print("Period in msecs:",1000/self.scan_rate)

  def center(self):
    qr = self.frameGeometry()
    cp = QtGui.QDesktopWidget().availableGeometry(self.screen).center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())
    if QtGui.QDesktopWidget().numScreens() == 2 and self.screen ==1: #they have chosen to display on projector
      self.move(QtGui.QDesktopWidget().screenGeometry(0).width()+12,-12)

  def updateData(self):
    global EE16A_SCAN_DELAY
    if self.count < self.N*self.M:
      if self.fp_flag <EE16A_SCAN_DELAY/(1000 / self.scan_rate):
        self.fp_flag += 1
        self.count = 0

      elif self.fp_flag == EE16A_SCAN_DELAY/(1000 / self.scan_rate):
        self.time0 = time.time()
        self.fp_flag += 1
      
      #time.sleep(.1)
      #Update what's being displayed to projector
      mask = np.reshape(self.Hr[:, self.count], (self.M, self.N))
      mask = np.require(mask, np.uint8, 'C')
      QI=QtGui.QImage(mask.data, self.N, self.M, QtGui.QImage.Format_Indexed8)
      self.label.setPixmap(QtGui.QPixmap.fromImage(QI).scaled(self.width,self.height))
      
      #sleep for some time to allow low-pass filter time to settle
      #time.sleep(.1)

      #read from serial port
      serial_write(self.ser, 1)
      serial_data = self.ser.readline()
      #time.sleep(.1)

      #if self.count == 0:
      #    self.ser.flushInput()
      #    self.ser.flushOutput()

      serial_data_processed = []
      for i in serial_data:
        if chr(i) != '\r' and chr(i) != '\n':
          serial_data_processed.append(i)
      data = 0
      count = 1
      serial_data_length = len(serial_data_processed)
      for j in serial_data_processed:
        data += pow(10,serial_data_length-count)*int(chr(j))
        count += 1      
      self.sensor_readings[self.count] = data
      print("data: %r count: %r" % (data, self.count)) 
      self.count += 1
      
    else:
      print("count:",self.count)
      self.timer.stop()
      self.time_final = time.time()
      print("Scan completed")
      print("Scan time per pixel: %.3f s" % ((self.time_final-self.time0)/(self.M*self.N)))
      #print("Bytes left in Serial Buffer: ",self.ser.inWaiting())

      #Read the rest of the data in the serial port
      num_extra_data = 0
      self.fp_flag = 0
      extra_data = []
      while(self.ser.inWaiting()):
        serial_data = self.ser.readline()
        serial_data_processed = []
        for i in serial_data:
          if chr(i) != '\r' and chr(i) != '\n':
            serial_data_processed.append(i)
        data = 0
        count = 1
        serial_data_length = len(serial_data_processed)
        for j in serial_data_processed:
          data += pow(10,serial_data_length-count)*int(chr(j))
          count +=1
        extra_data.append(data)
        num_extra_data += 1
      print("Length of extra_data:",len(extra_data))
      print("Extra Data:",extra_data)
      #print("Extra data: ",num_extra_data, "Data: ",extra_data)
      self.sensor_readings_final = self.sensor_readings[num_extra_data:]
      
      #print("Lenghth of _final: ",len(self.sensor_readings_final), len(self.sensor_readings[num_extra_data:]))


      print("Saving data as %s..."%self.out_file)
      # self.sensor_readings = np.concatenate((np.array(self.sensor_readings_final),np.array(extra_data))) # ORIGINAL
      self.sensor_readings = np.roll(np.concatenate((np.array(self.sensor_readings_final),np.array(extra_data))), -self.scan_rate // 10 - 1) # WITH ROLL
      m = np.mean(self.sensor_readings)
      for i,v in enumerate(self.sensor_readings):
        if v < m - 500 or v > m + 500 or v == 0:
          self.sensor_readings[i] = m
      # self.sensor_readings = np.concatenate((np.array(extra_data), np.array(self.sensor_readings_final))) # SWAPPED
      np.save("%s%d.npy"%(self.out_file, self.runs), self.sensor_readings)
      self.runs += 1

      print("Reconstructing image...")
      #Original plotting code
      #plt.figure()
      #self.sensor_readings = self.sensor_readings - np.mean(self.sensor_readings)
      #img = np.reshape(np.array(self.sensor_readings),(self.M, self.N))
      #plt.imshow(img,cmap='gray',interpolation='none')
      #plt.show()
      
      #second plot
      #plt.figure()
      #self.sensor_readings = self.sensor_readings - np.mean(self.sensor_readings)
      #img = np.reshape(np.array(self.sensor_readings),(self.M, self.N))
      #plt.imshow(img,cmap='gray',interpolation='none',vmin=img[3:self.M,3:self.N].min(),vmax = img[3:self.M,3:self.N].max())
      #plt.show()

      #third plot
      plt.figure()
      self.sensor_readings = np.array(self.sensor_readings)
      c_min = self.sensor_readings[1:].min()
      c_max = self.sensor_readings.max()
      #print(c_min,c_max)
      #print(len(self.sensor_readings),self.M,self.N)
      #print(self.width,self.height)
      img = np.reshape(np.array(self.sensor_readings),(self.M, self.N))
      plt.imshow(img,cmap='gray',vmin=c_min*.95,vmax = c_max)
      #plt.imshow(img,cmap='gray')
      plt.show()
      print("Press [Enter] to scan again")
      self.count = 0
      self.sensor_readings = np.zeros(self.M*self.N)

  def help(self):
    self.fullscreen = True
    self.rescale()
    self.showNormal()
    print(help_menu)

  def keyPressEvent(self, e):
    if e.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
      if not self.started:
    # Load the imaging mask from "imaging_mask.npy"
        self.ser.flushOutput()
        self.ser.flushInput()
        time.sleep(.2)
        self.Hr = np.load(self.mask_file)*255
        print("Starting scan...")
        self.started=True
        print(type(self))
        self.timer.start(1000/self.scan_rate)
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.updateData)
      else:
        print("Resuming scan...")
        self.timer.start()

      if self.count == self.N*self.M:
        self.count=0

    if e.key() == QtCore.Qt.Key_Space:
        print("Scan paused")
        self.timer.stop()

    if e.key() == QtCore.Qt.Key_F:
        if self.fullscreen:
           self.showNormal()
        else:
           self.showFullScreen()
        self.rescale()
        self.fullscreen = not self.fullscreen

  def rescale(self):
    if self.fullscreen:
      self.width = DEFAULT_WIDTH   # Display width
      self.height = DEFAULT_HEIGHT # Display height
    else:
      self.width = QtGui.QDesktopWidget().screenGeometry(self.screen).width()
      self.height = QtGui.QDesktopWidget().screenGeometry(self.screen).height()

    self.label.setGeometry(QtCore.QRect(0, 0, self.width, self.height))
    QI=QtGui.QImage(self.mask.data, self.N, self.M, QtGui.QImage.Format_Indexed8)
    self.label.setPixmap(QtGui.QPixmap.fromImage(QI).scaled(self.width,
       self.height, QtCore.Qt.KeepAspectRatio))

def main():
  global serial_count
  print("EE16A Imaging Lab")

  # Parse arguments
  parser = argparse.ArgumentParser(description='This program projects a sampling pattern and records the corresponding solar cell voltage.')
  parser.add_argument('-f', '--fps', type=int, default=20, help='frames per second (default=20)')
  parser.add_argument('--width', type=int, default=40, help='width of the image in pixels (default=40px)')
  parser.add_argument('--height', type=int, default=30, help='height of the image in pixels (default=30px)')
  parser.add_argument('--mask', default="imaging_mask.npy", help='saved sampling pattern mask (default="imaging_mask.npy")')
  parser.add_argument('--out', default="data/sensor_readings", help='output path (default="data/sensor_readings", saved as "data/sensor_readings0.npy")')
  args = parser.parse_args() 
  serial_count = 0

  print("Checking serial connections...")

  ports = serial_ports()
  if ports:
    print("Available serial ports:")
    for (i,p) in enumerate(ports):
      print("%d) %s"%(i+1,p))
  else:
    print("No ports available. Check serial connection and try again.")
    print("Exiting...")
    quit()

  selection = input("Select the port to use: ")
  ser = serial.Serial(ports[int(selection)-1],BAUD_RATE,timeout = .01)
  #ser.write([9,])

  #Read from serial port to check if it's getting cleared
  # serial_data = ser.readline()

  # serial_data_processed = []
  # for i in serial_data:
  #   if chr(i) != '\r' and chr(i) != '\n':
  #     serial_data_processed.append(i)
  # data = 0
  # count = 1
  # serial_data_length = len(serial_data_processed)
  # for j in serial_data_processed:
  #   data += pow(10,serial_data_length-count)*int(chr(j))
  #   count += 1      
  # print(data)



  app = QtGui.QApplication(sys.argv)
  print("Press [Esc], [Ctrl+Q], or [Ctrl+W] at any time to exit.")
  print("Press [F] for fullscreen and press [H] to show a help menu.\n")

  mask = Mask(ser, args.fps, args.width, args.height, args.mask, args.out)
  print("Press [Enter] to start scanning an image, press [Space] to pause.")
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
