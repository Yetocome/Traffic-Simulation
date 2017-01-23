# Basic model of each Section
# oneway-Section type:
# Take delta_demand = curr_demand - last_demand
# delta_demand > 0 ? up : (delta_demand < 0 ? down : steady)
# out_lanes-next_in_lanes = 0
#   up, one on-ramp
#   down, one off-ramp
#   steady, no ramp
# out_lanes-next_in_lanes = -1
#   up, one on-ramp
#   down, one on-ramp, one off-ramp
# out_lanes-next_in_lanes = -2
#   up, two on-ramps
#   down, two on-ramps, two off-ramps
# out_lanes-next_in_lanes = 1
#   up, one on-ramp, one off-ramp
#   down, one off-ramp
# out_lanes-next_in_lanes = 2
#   down, two off-ramp
# Assume on-ramp and off-ramp are independent
# If there is a intersection

# Emit vechiles with poisson distribution
def poisson_distribution(flow):
    pass

# Emit vechiles with weighted uniform
def weighted_distribution(flow):
    pass

def lane_changing_model():
    pass

def vehicle_following_model():
    pass

class Section(object):
    def __init__(self, miles, demand, lanes):
        self.intsec = False
        self.demand = int(demand)            # num/hour
        self.length = int(miles*1609)        # mile to meter
        self.lanes = self.next_sec_lanes = lanes
        self.delta_demand = 0
        self.on_ramp_num = 0
        self.off_ramp_num = 0
        self.ramp_cap = 50              # default ramp limit for IS
        self.mainstream_model = poisson_distribution
        self.ramp_model = weighted_distribution

    def set_delta_demand(self, delta):
        self.delta_demand = int(delta)

    def set_next_sec_lanes(self, lanes):
        self.next_sec_lanes = lanes

    def ramp_build(self):
        if self.intsec:
            return
        delta_lanes = self.lanes - self.next_sec_lanes
        if self.delta_demand > 0:
            self.on_ramp_num = 1
        elif self.delta_demand < 0:
            self.off_ramp_num = 1
        if delta_lanes == -2:
            self.on_ramp_num = 2
            if self.delta_demand < 0:
                raise Exception('Not considered condition: delta_lanes', delta_lanes)
                self.off_ramp_num = 2
        elif delta_lanes == -1:
            if self.on_ramp_num == 0:
                self.on_ramp_num = 1

        elif delta_lanes == 0:
            pass
        elif delta_lanes == 1:
            if self.delta_demand > 0:
                self.off_ramp_num = 1
        elif delta_lanes == 2:
            if self.delta_demand > 0:
                raise Exception('Not considered condition: delta_lanes', delta_lanes)
            else:
                # print('Not Boom!!!!')
                self.off_ramp_num = 2
        else:
            print('Strange data here:', self.lanes, self.next_sec_lanes)
            # raise Exception('Not considered ', delta_lanes)

    def set_if_intersection(self):
        # self.on_ramp_num = self.off_ramp_num = 0
        self.intsec = True
        self.ramp_model = weighted_distribution # vehicle generation model changed
        if self.delta_demand > 0:
            self.on_ramp_num = self.lanes
            self.off_ramp_num = 0
        else:
            self.off_ramp_num = self.lanes
            self.on_ramp_num = 0

    def set_ramp_capability(self, cap):
        self.ramp_cap = cap

    def show_my_parameters(self):
        print('Demand:', self.demand, 'vehicles/hour')
        print('Lanes:', self.lanes)
        print('Delta demand:', self.delta_demand, 'vehicles/hour')
        print('On/Off-ramp:', self.on_ramp_num, self.off_ramp_num)
        print('Length:', self.length, 'meters')
        if self.intsec:
            print('Intersection')
        else:
            print('Not a Intersection')
        if self.next_sec_lanes >= self.lanes:
            print('Not a bottleneck section')
        else:
            print('Bottleneck Section, decrease to', self.next_sec_lanes, 'lanes.')
        print('-----------------------------')

class Vehicle(object):
    def __init__(self):
        self.speed = desired_speed()
        self.acc_rate = 2 # m/s
        self.size = 2

    def desired_speed(self):
        return 60

class AutoVehicle(Vehicle):
    def __init__(self):
        self.time_gap

# Define a basic simulator to derive specific simulator
class BasicSimulator(object):
    def __init__(self, section_list):
        time_slot = 0.1 # second
        self.list = section_list

    def run(self):
        pass

class SingleLaneSimulator(BasicSimulator):
    def __init__(self, section_list):
        super.__init__(self, section_list)

    def run(self):
        pass
