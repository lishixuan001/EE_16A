#!/usr/bin/python
from __future__ import unicode_literals
import sys
import argparse
from PIL import Image
import numpy as np
import math
import matplotlib.pyplot as plt
import time
import glob
import serial
import struct
from scipy import misc
import matplotlib.cm as cm

# HELLO INTREPID EE16A STUDENT, PLEASE MODIFY THE FOLLOWING LINES
temp = str(sys.argv[1])

offset = int(temp[(temp.find("=")+1):])

quantization = 1

# Step 1a: import the image
phantom_sim = misc.imread('phantom.jpg')

def weightedAverage(pixel):
	return 0.299*pixel[0] + 0.587*pixel[1] + 0.114*pixel[2]

phantom_greyscale = np.zeros((phantom_sim.shape[0],phantom_sim.shape[1]))
for rownum in range(len(phantom_sim)):
	for colnum in range(len(phantom_sim[rownum])):
		phantom_greyscale[rownum][colnum] = weightedAverage(phantom_sim[rownum][colnum])

#phantom_greyscale = np.ones((1280,720))

#plt.imshow(phantom_greyscale, cmap = cm.Greys_r)
#plt.show()

# Step 1c: apply uneven illumination (optional)

# Step 1d: ??? (attempt to make the real world and the simulator match up)

# Step 2a: import the mask (should be the same as that the capture_image takes in)

#Hr = np.eye(1200) 
Hr = np.load("imaging_mask.npy")

# Step 2b: check whether or not the mask is an acceptable size

# Step 2c: Undersample the image

N = int(np.sqrt(720*1280/12/Hr.shape[0]))
us_x = 4*N
us_y = 3*N

M = int(np.sqrt(Hr.shape[0]/12))
im_x_dim = 4*M
im_y_dim = 3*M

us_phantom = np.zeros((im_y_dim,im_x_dim))

for us_rownum in range(im_y_dim):
	for us_colnum in range(im_x_dim):
		temp_mat = phantom_greyscale[us_rownum*us_y:us_rownum*us_y+us_y,us_colnum*us_x:us_colnum*us_x+us_x]
		us_phantom[us_rownum,us_colnum] = np.sum(temp_mat)

# Step 3: apply the mask

us_phantom_vec = np.reshape(us_phantom,(1,Hr.shape[1]))
output_vec = np.zeros(Hr.shape[1])

for mask_col in range(Hr.shape[1]):
	output_vec[mask_col] = np.dot(us_phantom_vec,Hr[:,mask_col])

# Step 4: quantize the ever loving crap out of it
if (quantization==1):
	div_rat = np.max(output_vec)/4096
	for i in range(len(output_vec)):
		output_vec[i] = math.floor(output_vec[i]/(div_rat)/50)
	output_vec = output_vec

# Apply DC offset
if (offset > 0):
	output_vec += offset

plt.imshow(np.reshape(output_vec,(im_y_dim,im_x_dim)), cmap = cm.Greys_r)
plt.show()

np.save("sim_output.npy",output_vec)