SLOW_CHARGER_POWER_KW = 4.8   # BC Hydro Level 2 ~ 4.8 kW
FAST_CHARGER_POWER_KW = 200   # BC Hydro Fast Charger ~ 200 kW Level 3

ASSUMED_SOC_INITIAL = 20.0  # percent
ASSUMED_SOC_FINAL = 80.0    # percent
MAX_QUEUE_LENGTH = 20  # maximum acceptable queue length

# Constraints for the maximum and minimum battery levels for generated cars
BATTERY_MIN = 30 # 30% OST study recommended this assumption for the equation used for service time
BATTERY_MAX = 60 # 60%
TARGET_MAX_FINAL_BATTERY = 80   # max % they will charge up to
ENERGY_CONSUMPTION_RATE: float= 0.20# (kWh/km)
BATTERY_CAPACITY: float = 75.0 # (kWh)
MIN_BATTERY_THRESHOLD = 20 # minimum battery level to consider driving to a station (%)
MIN_CHARGE_AMOUNT = 20  # minimum amount to charge (%)
TIME_FACTOR = 15.0  # factor to estimate wait times in queue

X_MIN = 0.0 # minimum x coordinate for simulation area
X_MAX = 9.3 # maximum x coordinate for simulation area
Y_MIN = 0.0 # minimum y coordinate for simulation area
Y_MAX = 5.2 # maximum y coordinate for simulation area
SPEED_KM = 40 # average speed in km/h