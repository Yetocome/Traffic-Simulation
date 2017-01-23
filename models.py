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
import random
from scipy import stats
import numpy as np

sim_clock = 0.1 # second

vehicle_data = {
    # 'Type': (length, acceleration, deceleration, probability)
    'car': (4, 3, 4, 0.9),
    'truck': (8, 1, 3.5, 0.1),
    # 'bus': (12, 1, 2, )
}

speed_data = [
    ((15,20), 1),
    ((20,25), 2),
    ((25,30), 2),
    ((30,35), 3),
    ((35,40), 5),
    ((40,45), 9),
    ((45,50), 18),
    ((50,55), 27),
    ((55,60), 21),
    ((60,65), 10),
    ((65,70), 2),
]


# Emit vechiles with poisson distribution
def poisson_distribution(flow):
    return 60*60/stats.poisson.rvs(mu=flow,loc=0,size=1)[0]

def auto_or_not(ratio):
    if random.random() > ratio:
        return False
    else:
        return True

def weighted_distribution(flow):
    return 60*60/flow

def lane_changing_model(vehicle):
    pass

def vehicle_speedup_model(vehicle):
    old_speed = vehicle.speed
    vehicle.speed += vehicle.acc_rate*sim_clock
    if vehicle.speed > vehicle.desired_speed:
        vehicle.speed = vehicle.desired_speed

    dis = (vehicle.speed+old_speed)*sim_clock/2
    vehicle.front_location += dis
    vehicle.back_location += dis

def vehicle_slowdown_model(vehicle):
    old_speed = vehicle.speed
    vehicle.speed -= vehicle.dec_rate*sim_clock
    if vehicle.speed < 0:
        vehicle.speed = 0

    dis = (vehicle.speed+old_speed)*sim_clock/2
    vehicle.front_location += dis
    vehicle.back_location += dis

def vehicle_free_traveling_model(vehicle):
    vehicle.front_location += vehicle.speed*sim_clock
    vehicle.back_location += vehicle.speed*sim_clock

def vehicle_following_model(leader, chaser):
    safe_dis = chaser.front_location+chaser.get_safe_dis(type(leader) == type(chaser))
    if leader.back_location > safe_dis+chaser.speed*sim_clock:
        if chaser.speed < chaser.desired_speed:
            vehicle_speedup_model(chaser)
        else:
            vehicle_free_traveling_model(chaser)
    elif leader.back_location > safe_dis:
        vehicle_slowdown_model(chaser)



class Section(object):
    def __init__(self, miles, demand, lanes):
        self.intsec = False
        self.demand = int(demand)            # num/hour
        self.length = int(miles*1609)        # mile to meter
        self.lanes = self.next_sec_lanes = lanes
        self.delta_demand = 0
        self.on_ramp_num = 0
        self.off_ramp_num = 0
        self.main_cap = 50
        self.ramp_cap = 50              # default ramp limit for IS
        self.mainstream_model = poisson_distribution
        self.ramp_model = weighted_distribution
        self.time_array = []

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

    def record_time(self, data):
        self.time_array.append(data)

class Vehicle(object):
    def __init__(self):
        self.desired_speed = self.desired_speed()
        self.speed = self.desired_speed
        self.type = self.get_type()
        self.length, self.acc_rate, self.dec_rate, _ = vehicle_data[self.type]
        self.manual_time_gap = 1.4
        self.front_location = 0
        self.back_location = self.front_location - self.length

    def desired_speed(self):
        population = [val for val, cnt in speed_data for i in range(cnt)]
        min_speed, max_speed = random.choice(population)
        return round(random.uniform(min_speed, max_speed)*1.609, 2)

    # generate random vehicle type
    def get_type(self):
        weighted_choices = [(v_type, int(v_data[3]*10)) for v_type, v_data in vehicle_data.items()]
        population = [val for val, cnt in weighted_choices for i in range(cnt)]
        return random.choice(population)

    def get_safe_dis(self, Flag):
        return self.manual_time_gap*self.speed

    def set_location(self, back_location):
        self.back_location = back_location
        self.front_location = back_location+self.length

class AutoVehicle(Vehicle):
    def __init__(self):
        Vehicle.__init__(self)
        self.auto_time_gap = 0.5

    def get_safe_dis(self, AutoFlag):
        if AutoFlag:
            return self.auto_time_gap*self.speed
        else:
            return self.manual_time_gap*self.speed

# Define a basic simulator to derive specific simulator
class BasicSimulator(object):
    def __init__(self):

        self.curr_time = 0
        self.countdown = [0, 0]

    def ticktock(self):
        pass

class SingleLaneSimulator(BasicSimulator):
    def __init__(self, hours):
        BasicSimulator.__init__(self)
        self.time_limits = int(hours*60*60/sim_clock)
        # self.mainstream_pending_vehicles = []
        # self.ramp_waiting_vehicles = []
        # self.mainstream_vehicles = []

    def mainstream_simulation(self):
        if self.countdown[0] == 0:
            if auto_or_not(self.auto_ratio):
                self.mainstream_pending_vehicles.append(AutoVehicle())
            else:
                self.mainstream_pending_vehicles.append(Vehicle())
            self.countdown[0] = int(poisson_distribution(self.single_lane_demand)/sim_clock)
        else:
            self.countdown[0] -= 1

        # if self.mainstream_pending_vehicles != []:
        #     vehicle = self.mainstream_pending_vehicles[0]
        #     try:
        #         vehicle_following_model(self.mainstream_vehicles[-1], vehicle)
        #     except IndexError:
        #         vehicle_free_traveling_model(vehicle)
        try:
            vehicle_free_traveling_model(self.mainstream_vehicles[0])
        except IndexError:
            pass
        for i in range(self.mainstream_vehicles.__len__()-1):
            vehicle_following_model(self.mainstream_vehicles[i], self.mainstream_vehicles[i+1])

        if self.mainstream_pending_vehicles != []:
            chaser = self.mainstream_pending_vehicles[0]
            if self.mainstream_vehicles != []:
                leader = self.mainstream_vehicles[-1]
            # # check if the leader vehicle is in front of the safe distance of the joining one
                if leader.back_location > chaser.get_safe_dis(type(leader) == type(chaser)):
                    self.mainstream_vehicles.append(chaser)
                    del self.mainstream_pending_vehicles[0]
                    #     vehicle_free_traveling_model(vehicle)
            else:
                self.mainstream_vehicles.append(chaser)
        if self.mainstream_vehicles != []:
            if self.mainstream_vehicles[0].front_location > self.curr_sec.length:
                del self.mainstream_vehicles[0]

    def ramp_simulation(self):
        if self.curr_sec.on_ramp_num > 0:
            if self.countdown[1] == 0:
                if auto_or_not(self.auto_ratio):
                    self.ramp_waiting_vehicles.append(AutoVehicle())
                else:
                    self.ramp_waiting_vehicles.append(Vehicle())
                self.countdown[1] = weighted_distribution(self.curr_sec.delta_demand/self.curr_sec.on_ramp_num/sim_clock)
            else:
                self.countdown[1] -= 1

            try:
                ramp_vehicle = self.ramp_waiting_vehicles[0]
                back_location = 7/12*self.curr_sec.length
                ramp_vehicle.set_location(back_location)
                dash_into_flag = True
                forbidden_area = (back_location+ramp_vehicle.length+ramp_vehicle.get_safe_dis(False), back_location-ramp_vehicle.get_safe_dis(False))

                for i in range(self.mainstream_vehicles.__len__()-1):
                    if self.mainstream_vehicles[i].back_location < forbidden_area[0] or self.mainstream_vehicles[i].front_location > forbidden_area[1]:
                        dash_into_flag = False
                        break
                    elif self.mainstream_vehicles[i].back_location >= forbidden_area[0] and self.mainstream_vehicles[i+1].front_location <= forbidden_area[1]:
                        self.mainstream_vehicles.insert(i, ramp_vehicle)
                        del self.ramp_waiting_vehicles[0]
                        dash_into_flag = False
                # for only one vehicle situation
                if dash_into_flag:
                    self.mainstream_vehicles.append(ramp_vehicle)
                    del self.ramp_waiting_vehicles[0]
            except IndexError:
                pass
        else:
            pass

        if self.curr_sec.off_ramp_num > 0:
            pass
        else:
            pass

    def ticktock(self):
        self.mainstream_simulation()
        self.ramp_simulation()
        self.curr_time += 1

    def log(self):
        if self.curr_time%6000 == 0:
            print(self.curr_time, self.mainstream_vehicles.__len__(), 'on the road',
                self.mainstream_pending_vehicles.__len__(), 'pending to start',
                self.ramp_waiting_vehicles.__len__(), 'waiting on the ramp',
            )

    def congestion_detection(self):
        if self.ramp_waiting_vehicles.__len__() > self.curr_sec.main_cap or self.mainstream_pending_vehicles.__len__() > self.curr_sec.ramp_cap:
            return True
        # return False

    def accident_detection(self):
        pass

    def run(self, section_list, ratio):
        self.list = section_list
        self.auto_ratio = ratio
        for sec in self.list:
            self.curr_sec = sec
            self.mainstream_pending_vehicles = []
            self.ramp_waiting_vehicles = []
            self.mainstream_vehicles = []
            self.single_lane_demand = (self.curr_sec.demand-self.curr_sec.delta_demand)/self.curr_sec.lanes
            for i in range(self.time_limits):
                self.ticktock()
                self.log()
                if self.congestion_detection():
                    self.curr_sec.record_time(self.curr_time)
                    print('After', int(self.curr_time*sim_clock), 'seconds, congestion detected!!!')
                    break
