SLOW_CHARGER_POWER_KW = 4.8   # BC Hydro Level 2 ~ 4.8 kW
FAST_CHARGER_POWER_KW = 200   # BC Hydro Fast Charger ~ 200 kW Level 3

MAX_QUEUE_LENGTH = 10  # maximum acceptable queue length

# Constraints for the maximum and minimum battery levels for generated cars
BATTERY_MIN = 20 # 30% OST study recommended this assumption for the equation used for service time
BATTERY_MAX = 60 # 60%
BALK_BATTERY_LEVEL = 50 # if battery level is below this, car will balk if no stations are reachable (%)
TARGET_MAX_FINAL_BATTERY = 80   # max % they will charge up to
ENERGY_CONSUMPTION_RATE: float= 0.20# (kWh/km)
BATTERY_CAPACITY: float = 75.0 # (kWh)
MIN_BATTERY_THRESHOLD = 19 # minimum battery level to consider driving to a station (%)
MIN_CHARGE_AMOUNT = 20  # minimum amount to charge (%)
TIME_FACTOR = 15.0  # factor to estimate wait times in queue

X_MIN = 0.0 # minimum x coordinate for simulation area
X_MAX = 13 # maximum x coordinate for simulation area
Y_MIN = 0.0 # minimum y coordinate for simulation area
Y_MAX = 7.5 # maximum y coordinate for simulation area
SPEED_KM = 30 # average speed in km/h