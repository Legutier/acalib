import matplotlib.pyplot as plt
import synthetic.imc as imc
import astropy.units as u
import synthetic.vu as vu
import numpy as np
import math
import random

#TODO This is not working for near zero positions!!! (it is fault of the wcs i think!)
univ=vu.Universe()

# Create Source
center=[1.0,1.0]*u.deg
univ.create_source('example',center)

# Defines a central component
mol_list=dict()
mol_list['CH3OHvt=0']=[200,200]* u.Jy/u.beam
temp=78*u.K
offset=np.array([0,0])*u.arcsec
std = np.array([15,15])*u.arcsec
angle=0*u.rad
fwhm=30*u.km/u.s
gradient=np.array([0.0,0.0])*u.km/(u.s*u.arcsec)
rad_vel=150*u.km/u.s
# Create Component
model=imc.GaussianIMC(mol_list,temp,offset,std,angle,fwhm,gradient)
model.set_velocity(rad_vel)
univ.add_component('example',model)
mol_list['CH3OHvt=0']=[100,200]* u.Jy/u.beam

for i in range(10):
  offset=(80*np.random.random(2) - 40)*u.arcsec
  std = 20*np.random.random(2)*u.arcsec
  angle= random.random()*math.pi*u.rad
  fwhm=50*random.random()*u.km/u.s
  gradient=(20*np.random.random(2) - 10)*u.km/(u.s*u.arcsec)
  model=imc.GaussianIMC(mol_list,temp,offset,std,angle,fwhm,gradient)
  model.set_velocity(rad_vel)
  univ.add_component('example',model)

# Create Cube
ang_res=np.array([1.0,1.0])*u.arcsec
fov=np.array([200,200])*u.arcsec
freq=229.5*u.GHz
spe_res=0.005*u.GHz
bw=2*u.GHz
noise=0.01*u.Jy/u.beam

(cube,tab)=univ.gen_cube(center,ang_res,fov, freq,spe_res,bw,noise)
print tab
plt.plot(cube.get_stacked(axis=(1,2)))
plt.show()
plt.clf
plt.imshow(cube.get_stacked())
plt.show()

