import numpy as np

class Car:
    def __init__(self):
        self.position = self.get_position()
        self.battery_level = self.get_battery_level()
        self.arrival_time = 0.0
        self.queue_entry_time = 0.0
        self.drive_time = 0.0
        self.station_routed_to = None

    def get_position(self):
        X_MIN = 48.42242
        X_MAX = 48.46956

        Y_MIN = -123.48509
        Y_MAX = -123.35944

        x = np.random.uniform(X_MIN, X_MAX)
        y = np.random.uniform(Y_MIN, Y_MAX)

        return x, y
    
    def get_battery_level(self):
        Battery_MIN = 20
        Battery_MAX = 65

        return np.random.uniform(Battery_MIN, Battery_MAX)
    
if __name__ == "__main__":
    car = Car()
    print("Position:", car.position)
    print("Battery:", car.battery_level)