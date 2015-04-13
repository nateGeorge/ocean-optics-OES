# ocean-optics-OES
  
This is a program I wrote for monitoring optical emission spectroscopy using the ocean optics USB 2000+ spectrometer.  
It also includes code for dealing with a MPM-2000 multiplexer.  Any code with 'measure' in the name does as implied; 
it measures spectra and saves them to a directory.  The 'plot OES...pyw' files are for live plotting of the 
data during collection.  Some code for processing the data is also included:  

'plot all OES data - look at raw data from each zone.py'  -- this exports each raw spectra that was collected  
and overlays color blocks in the areas where the spectra are integrated to get a measure of elemental composition.  
It also uses another file with time and length (down web position) of our 'runs' to convert the time of spectrum 
collection to a down web position.  'raw OES spectrum demo.png' is an example of this.  
  
'plot all OES data - PC.py' integrates the raw spectra, converts the times of measurement to a downweb position, 
and saves an image of the plot.  'OES signal demo.png' is an example.