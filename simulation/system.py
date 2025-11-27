class EV_Charging_System:
    def __init__(self, routing_policy, num_delays_required):
        # a 7 event event list
        # initialize with all events to infinity except first arrival
        pass

    def timing(self):
        #advance sim clock
        # update mean interrarival time based on sim time
        pass

    def update_time_avg_stats(self):
        pass

    def report(self):
        pass

    def arrive(self):
        # schedule next arrival 
        # call routing policy to determine which station to go to  
        # update cars arrival time
        pass

    def main():
        pass
        # same while loop but with 7 events


if __name__ == "__main__":
    simulation = EV_Charging_System("shortest_estimated_time", 10000)
    simulation.main()
