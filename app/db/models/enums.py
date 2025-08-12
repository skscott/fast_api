# app/db/models/enums.py
from enum import Enum

class TariffSort(str, Enum):
  PERCENTAGE = "PERCENTAGE"
  SINGLE = "SINGLE"
  NORMAL = "NORMAL"
  REDUCED = "REDUCED"
  FIXED = "FIXED"
  VARIABLE = "VARIABLE"
  TAX = "TAX"          # Tax & surcharge
  NETWORK = "NETWORK"  # Network costs

class Frequency(str, Enum):
  DAY = "DAY"
  KWH = "KWH"
  M3 = "M3"
  MONTH = "MONTH"
  YEAR = "YEAR"
