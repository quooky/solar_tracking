"""
Skript to downlode Fits file with the help of the sunpy package, from a 
specific start date and a end date.  Also the interval lenght can be definet
and wich instument.
"""
import sunpy.net
from sunpy.net import Fido, attrs as a
from astropy import units as u

# Define the time range
start_time = '2023-12-04 20:00:00'
end_time = '2023-12-05 00:00:00'

# Define the search criteria
instrument = a.Instrument.hmi

data_type = a.Physobs.intensity  
sample = 1 * u.hour  # Interval of the images

# The search with the sunpy
results = Fido.search(a.Time(start_time, end_time), instrument, data_type, a.Sample(sample))

# Download the data
downloaded_files = Fido.fetch(results)
print(f"Downloaded files: {downloaded_files}")