
from datetime import datetime, timezone
from typing import Union
from math import asin, atan2, radians, sin, cos, acos, sqrt
from app.exceptions import BusinessLogicException




def haversine_distance(lat1, lon1, lat2, lon2):
  """
  Calculates the distance between two points using the Haversine formula.

  Args:
      lat1: Latitude of the first point in degrees.
      lon1: Longitude of the first point in degrees.
      lat2: Latitude of the second point in degrees.
      lon2: Longitude of the second point in degrees.

  Returns:
      The distance between the two points in meters.
  """

  # Convert degrees to radians
  lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

  # Calculate the Haversine formula
  dlat = lat2 - lat1
  dlon = lon2 - lon1
  a = sin(dlat / 2) * sin(dlat / 2) + cos(lat1) * \
      cos(lat2) * sin(dlon / 2) * sin(dlon / 2)
  c = 2 * asin(sqrt(a))
  
  EARTH_RADIUS = 6371000


  # Return the distance in meters
  return EARTH_RADIUS * c




def get_todays_date_utc():
    """
    Extracts today's date in UTC timezone from a given date object. 
    Args:
    Returns:
      A date object representing today's date in UTC timezone.
    """
 
    # Discard time information and set timezone to UTC
    return datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0).date()


    