from ..core import adata
from ..core import atable
from astropy.io import fits
from astropy import log
import numpy as np
import os
import astropy.units as u
from astropy.wcs import wcs


def HDU_to_adata(hdu):
   data=hdu.data
   meta=hdu.header
   mask=np.isnan(data)
   try:
     bscale=meta['BSCALE']
   except KeyError:
     bscale=1.0
   try:
     bzero=meta['BZERO']
   except KeyError:
     bzero=0.0
   try:
     bsu=meta['BUNIT']
     bsu=bsu.lower()
     bsu=bsu.replace("jy","Jy")
     bunit=u.Unit(bsu,format="fits")
   except KeyError:
     bunit=u.Unit("u.Jy/u.beam")
  
   # Hack to correct wrong uppercased units generated by CASA

   mywcs=wcs.WCS(meta)
   # Create astropy units
   if len(data.shape) == 4:
       # Put data in physically-meaninful values, and remove stokes
       # TODO: Stokes is removed by summing (is this correct? maybe is averaging?)
       log.info("4D data detected: assuming RA-DEC-FREQ-STOKES (like CASA-generated ones), and dropping STOKES")
       data=data.sum(axis=0)*bscale+bzero
       mywcs=mywcs.dropaxis(3)
   elif len(data.shape) == 3:
       log.info("3D data detected: assuming RA-DEC-FREQ")
       data=data*bscale+bzero
   else:
       log.error("Only 3D data allowed (or 4D in case of polarization)")
       raise TypeError

   # META Fixing
   #TODO..

   return adata.AData(data,mywcs,meta,bunit)


def HDU_to_atable(hdu):
   log.warning("FITS Table ---> ATable not implemented Yet")
   #return atable.ATable(data=hdu.data,meta=hdu.header)


def load_fits_to_ws(path,name,ws):
   log.info("Loading "+name+".fits")
   hdulist = fits.open(path)
   counter=0
   for hdu in hdulist:
      if isinstance(hdu,fits.PrimaryHDU) or isinstance(hdu,fits.ImageHDU):
         log.info("Processing HDU "+str(counter)+" (Image)")
         ndd=HDU_to_adata(hdu)
         ide=name+"-"+str(counter)
         ws[ide]=ndd
         counter+=1

      elif isinstance(hdu,fits.BinTableHDU) or isinstance(hdu,fits.TableHDU):
         log.info("Processing HDU "+str(counter)+" (Table)")
         ntt=HDU_to_atable(hdu.data,meta=hdu.header)
         ide=name+"-"+str(counter)
         ws[ide]=ntt
      else:
         log.warning("HDU type not recognized, ignoring "+hdu.name+" ("+counter+")")
      counter+=1

#TODO: support more filetypes
def load_hdf5_to_ws(path,name,ws):
   log.warning("HDF5 format not supported yet. Ignoring file "+name+".hdf5")
def load_votable_to_ws(path,name,ws):
   log.warning("VOTable format not supported yet. Ignoring file "+name+".xml")
def load_ascii_to_ws(path,name,ws):
   log.warning("ASCII format not supported yet. Ignoring file "+name)

def load_to_ws(path,ws):
   filename=os.path.basename(path)
   name,ext=os.path.splitext(filename)
   if ext == '.fits':
      load_fits_to_ws(path,name,ws)
   elif ext == '.hdf5':
      load_hdf5_to_ws(path,name,ws)
   elif ext == '.xml':
      load_votable_to_ws(path,name,ws)
   else:
      load_ascii_to_ws(path,name,ws)

def load_to_cont(path,cont):
   filename=os.path.basename(path)
   name,ext=os.path.splitext(filename)
   if ext == '.fits':
      load_fits_to_cont(path,name,cont)
   elif ext == '.hdf5':
      (path,name,cont)
   elif ext == '.xml':
      votable_consumer(path,name,cont)
   else:
      ascii_consumer(path,name,cont)

def save_from_cont(path,cont):
   filename=os.path.basename(path)
   name,ext=os.path.splitext(filename)
   if ext == '.fits':
      save_fits_from_cont(path,cont)
   else:
      log.warning("We only support saving in fits format for the moment")


#TODO: support more filetypes
def load_hdf5_to_cont(path,name,cont):
   log.warning("HDF5 format not supported yet. Ignoring file "+name+".hdf5")
def load_votable_to_cont(path,name,cont):
   log.warning("VOTable format not supported yet. Ignoring file "+name+".xml")
def load_ascii_to_cont(path,name,cont):
   log.warning("ASCII format not supported yet. Ignoring file "+name)

def save_fits_from_cont(filepath,acont):
   if acont.primary == None:
      phdu=fits.PrimaryHDU()
   else:
      phdu=acont.primary.get_hdu(True)
   nlist=[phdu]
   count=0
   for elm in acont.adata:
       count+=1
       hdu=elm.get_hdu()
       hdu.header['EXTNAME'] = 'SCI'
       hdu.header['EXTVER'] = count
       nlist.append(hdu)
   count=0
   for elm in acont.atable:
       count+=1
       hdu=elm.get_hdu()
       hdu.header['EXTNAME'] = 'TAB'
       hdu.header['EXTVER'] = count
       nlist.append(hdu)
   hdulist = fits.HDUList(nlist)
   hdulist.writeto(filepath,clobber=True)

def load_fits_to_cont(filePath,name,acont):
   hdulist = fits.open(filePath)
   for counter,hdu in enumerate(hdulist):
           if isinstance(hdu,fits.PrimaryHDU) or isinstance(hdu,fits.ImageHDU):
                   log.info("Processing HDU "+str(counter)+" (Image)")
                   try:
                           ndd=HDU_to_adata(hdu)
                           if isinstance(hdu,fits.PrimaryHDU):
                                   acont.primary = ndd
                           acont.adata.append(ndd)
                   except TypeError:
                           log.info(str(counter)+" (Image) wasn't an Image")

           if isinstance(hdu, fits.BinTableHDU):
                   table = HDU_to_atable(hdu)
                   acont.atable.append(table)
   if acont.primary is None:
           if len(acont.adata)==0:
                   acont.primary = acont.atable[0]
           else:
                   acont.primary = acont.adata[0]
