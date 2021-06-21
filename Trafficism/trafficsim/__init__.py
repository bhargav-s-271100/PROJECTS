import math
import random
from collections import namedtuple, deque

import cv2
import numpy as np

ROAD_TYPES = {
    0: 'GOOD',
    1: 'BAD'
}

Position = namedtuple('Position', ['x', 'y'])
Message = namedtuple(
    'Message', ['veh_id', 'priority', 'data', 'radius', 'ack_req', 'position', 'direction'])


def angle_limit(angle):
    if angle > math.pi:
        angle -= 2 * math.pi
    elif angle < -2 * math.pi:
        angle += 2 * math.pi
    return angle

# {message.priority},{self.acceleration},{self.speed},{self.direction},{is_ahead},{same_heading},{dist},{useful},{rebroadcast}
def naive_classifier(data):
    priority, acceleration, speed, direction, is_ahead, same_heading, dist = data
    if in_range:
        if priority == 3 and not (is_ahead and same_heading):
            return False, False
        return True, dist > message.radius * 0.5
    return False, False

class World:
    vehicles = []

    def __init__(self, map_file, n_vehicles, classifier=None):
        self.map = Map(map_file)
        self.channel = Channel(self)
        self.tick = 0
        self.render_broadcast = []
        self.render_receive = []
        self.colors = np.ones((100, 100*n_vehicles, 3), dtype=np.uint8) * 255

        if classifier is None:
            self.classifier = naive_classifier
        elif classifier == 'KNN':
            print('Loading KNN model...')
            from .KNN import KNN
            self.classifier = KNN(7).predict
        elif classifier == 'SVM':
            print('Loading SVM model...')
            from .SVM import SVM
            self.classifier = SVM().predict
        elif classifier == 'ANN':
            print('Loading ANN model...')
            from .ANN import ANN
            self.classifier = ANN().predict
        else:
            raise Exception()

        for _ in range(n_vehicles):
            self.spawn_vehicle()

    def show_colors(self):
        for i, vehicle in enumerate(self.vehicles):
            cv2.circle(
                self.colors,
                (100*i+50, 50),
                40,
                vehicle.color,
                -1
            )
        cv2.imshow('Colors', self.colors)

    def spawn_vehicle(self):
        vehicle = Vehicle(*random.choice(self.map.valid_points), self)
        self.vehicles.append(vehicle)
        return vehicle

    def step(self):
        self.render_broadcast = []
        self.render_receive = []
        self.tick += 1
        for vehicle in self.vehicles:
            vehicle.read_message()
        for vehicle in self.vehicles:
            vehicle.step()

    def render(self):
        disp_map = self.map.map.copy()
        for vehicle in self.vehicles:
            cv2.arrowedLine(disp_map, vehicle.position, (round(vehicle.position.x + 20 * math.cos(
                vehicle.direction)), round(vehicle.position.y + 20 * math.sin(vehicle.direction))), vehicle.color, 10)
            cv2.circle(
                disp_map,
                tuple(vehicle.position),
                3,
                (0, 0, 0),
                # vehicle.color,
                -1
            )
            if vehicle in self.render_broadcast:
                cv2.circle(
                    disp_map,
                    tuple(vehicle.position),
                    self.channel.broadcast_radius,
                    # (0, 0, 0),
                    vehicle.color,
                    2
                )
            for veh_id, veh in self.render_receive:
                if veh is vehicle:
                    cv2.circle(
                        disp_map,
                        tuple(vehicle.position),
                        8,
                        # (0, 0, 0),
                        self.vehicles[veh_id].color,
                        -1
                    )
                    break

        cv2.imshow(self.map.map_file, disp_map)

    def vehicle_ahead(self, vehicle, r=25):
        r = r ** 2
        for v in self.vehicles:
            if v == vehicle or v.broken:
                continue
            x = v.position.x-vehicle.position.x
            y = v.position.y-vehicle.position.y
            if x**2 + y**2 < r and abs(angle_limit(v.direction - vehicle.direction)) < 1.8 and abs(angle_limit(math.atan2(y, x) - vehicle.direction)) < 1.8:
                return True, v.id
        return False, None


class Channel:

    def __init__(self, world):
        self.world = world
        self.vehicles = world.vehicles
        self.broadcast_radius = 200

    def broadcast(self, vehicle, message):
        self.world.render_broadcast.append(vehicle)
        for v in self.vehicles:
            if v is vehicle or (vehicle.position.x - v.position.x) ** 2 + (vehicle.position.y - v.position.y) ** 2 > self.broadcast_radius ** 2:
                continue
            v.receive_message(message)


class Vehicle:
    __ID = 0

    MAX_SPEED = max(random.random() * 2, 1)
    MAX_SPEED_BAD = 0.3
    MIN_SPEED = 0.05
    MAX_ACCEL = 1
    MIN_ACCEL = -2
    MAX_STEER = 0.05

    DELTA_TIME = 1
    DELTA_ACCEL = 0.001
    DELTA_DECEL = 0.001

    ROAD_WIDTH = 8

    def __init__(self, x, y, world):
        self._position = Position(x, y)
        self._speed = max(random.random(), self.MIN_SPEED)
        self._acceleration = 0
        self._direction = 0
        self.prev_direction = 0
        self.lane = random.randint(0, 1)
        self.color = tuple(random.randint(50, 255) for _ in range(3))
        self.world = world
        self.map = world.map
        self.comm = world.channel
        self._steer = 0
        self.prev_sensor = 0
        self.__messages = []
        self.__out_messages = []
        self.id = Vehicle.__ID
        self.override_acceleration = False
        self.override_speed = False
        self.past = [deque([0]*5, 5),  # acceleration
                     deque([0]*5, 5),  # road type
                     deque([0]*5, 5),  # sensor
                     deque([0]*5, 5),  # speed
                     ]
        self.road_type = 0
        self.broken = False
        self.new_message = None
        self.slowing_down = False
        self.prev_broadcasts = deque([(0, 0)]*5, 5)
        self.received = deque([(0, 0)]*5, 5)
        Vehicle.__ID += 1

        self.align()

    @property
    def position(self):
        return Position(round(self._position.x), round(self._position.y))

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = min(max(value, self.MIN_SPEED),
                          self.MAX_SPEED_BAD if self.road_type else self.MAX_SPEED)

    @property
    def acceleration(self):
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value):
        self._acceleration = min(max(value, self.MIN_ACCEL), self.MAX_ACCEL)

    @property
    def steer(self):
        return self._steer

    @steer.setter
    def steer(self, value):
        self._steer = max(min(value, self.MAX_STEER), -self.MAX_STEER)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = angle_limit(value)

    @property
    def vehicle_ahead(self):
        return self.world.vehicle_ahead(self)

    def is_message_useful(self, message):
        x = message.position.x - self.position.x
        y = message.position.y - self.position.y
        dist = math.sqrt(x**2 + y**2)
        useful = False
        rebroadcast = False
        in_range = dist <= message.radius

        is_ahead = abs(angle_limit(
            math.atan2(y, x) - self.direction)) < 1
        same_heading = abs(angle_limit(
            message.direction - self.direction)) < 1

        return self.world.classifier([message.priority, self.acceleration, self.speed, self.direction, is_ahead, same_heading, dist])

        # if in_range:
        #     if message.data in ['Slow Down']:
        #         # is_ahead = abs(angle_limit(
        #         #     math.atan2(y, x) - self.direction)) < 1
        #         # same_heading = abs(angle_limit(
        #         #     message.direction - self.direction)) < 1
        #         if not (is_ahead and same_heading):
        #             #             return False, False
        #             pass
        #         else:
        #             useful = True
        #             rebroadcast = dist > message.radius * 0.5
        #     else:
        #         useful = True
        #         rebroadcast = dist > message.radius * 0.5
        #     return True, dist > message.radius * 0.5
        # return False, False
        # with open('data.csv', 'a') as f:
        #     f.write(
        #         f'{message.priority},{self.acceleration},{self.speed},{self.direction},{is_ahead},{same_heading},{dist},{useful},{rebroadcast}\n')
        # return useful, rebroadcast

    def read_message(self):
        if len(self.__messages) > 0:
            message = self.__messages.pop()
            msg_data = (message.veh_id, message.priority,
                        message.data, message.position, message.direction)
            if msg_data not in self.received:
                self.received.appendleft(msg_data)
                useful, rebroadcast = self.is_message_useful(message)
                if useful:
                    self.new_message = message
                    self.world.render_receive.append((message.veh_id, self))
                    if rebroadcast:
                        self.re_broadcast_message(self.new_message)
                    with open('log.txt', 'a') as f:
                        f.write(
                            f'Vehicle {self.id} received {self.new_message.data} from vehicle {self.new_message.veh_id} {"Rebroadcasting" if rebroadcast else ""}\n')

                else:
                    self.new_message = None
                    with open('log.txt', 'a') as f:
                        f.write(
                            f'Vehicle {self.id} discarded {message.data} from vehicle {message.veh_id}\n')

            else:
                self.new_message = None
        else:
            self.new_message = None

    def receive_message(self, message):
        self.__messages.append(message)
        self.__messages.sort(key=lambda x: x.priority)

    def broadcast_message(self, priority, data, radius, ack_req=False):
        d = (priority, data, radius, ack_req)
        for bc in self.prev_broadcasts:
            if d == bc[0] and self.world.tick - bc[1] < 1000:
                break
        else:
            message = Message(self.id, priority, data, radius, ack_req,
                              self.position, self.direction)
            self.__out_messages.append(message)
            self.prev_broadcasts.appendleft(
                (d, self.world.tick))

    def re_broadcast_message(self, message):
        self.__out_messages.append(message)

    def broadcast(self):
        if len(self.__out_messages) > 0:
            self.__out_messages.sort(key=lambda x: x.priority)
            message = self.__out_messages.pop()
            self.comm.broadcast(self, message)
            with open('log.txt', 'a') as f:
                f.write(
                    f'Vehicle {self.id} broadcasted {message.data} with priority {message.priority}\n')

    def align(self):
        r = 20
        surroundings, _ = self.map.surroundings(self, r)

        for point in surroundings:
            if (point[0]+1, point[1]+1) in surroundings and (point[0]+1, point[1]-1) in surroundings and (point[0]-1, point[1]+1) in surroundings and (point[0]-1, point[1]-1) in surroundings and math.sqrt((r - point[0]) ** 2 + (r - point[1]) ** 2) > 0.8 * r:
                self.direction = math.atan2(point[1] - r, point[0] - r)
                break
        else:
            print('Spawn Error')

    def step(self):
        self.read_message()
        self.update_direction()
        if not self.override_acceleration:
            self.update_acceleration()
        if not self.override_speed:
            self.update_speed()
        self.update_position()
        self.event_tracker()
        self.broadcast()

    def sense(self):
        r = 2 * self.ROAD_WIDTH
        theta1 = math.atan2(self.ROAD_WIDTH / 2, r)
        theta2 = math.atan2(self.ROAD_WIDTH / 4, r)
        l1 = math.sqrt(r ** 2 + (self.ROAD_WIDTH / 2) ** 2)
        l2 = math.sqrt(r ** 2 + (self.ROAD_WIDTH / 4) ** 2)
        sensor = [(self.direction - theta1, l1),
                  (self.direction - theta2, l2),
                  (self.direction, r),
                  (self.direction + theta2, l2),
                  (self.direction + theta1, l1)]
        x, y = self._position
        for i, item in enumerate(sensor):
            p = round(x + item[1] * math.cos(item[0]))
            q = round(y + item[1] * math.sin(item[0]))
            sensor[i] = all(self.map.map[q, p] != [255, 255, 255])

        turn_weights = [2, 1, 0, 1, 2]
        z = list(zip(turn_weights, sensor))
        return - sum(value * weight for weight, value in z[:2]) / (
            sum(sensor[:2]) or 1
        ) + sum(value * weight for weight, value in z[3:]) / (sum(sensor[3:]) or 1), sum(sensor)

    def update_direction(self):
        self.prev_direction = self.direction
        self.direction += self.steer

    def update_position(self):
        r = 10
        surroundings, self.road_type = self.map.surroundings(self, r)
        delta_new_position = Position(self.speed * math.cos(self.direction),
                                      self.speed * math.sin(self.direction))
        if (round(delta_new_position.x + r), round(delta_new_position.y + r)) not in surroundings:
            dist = 999999
            new_point = delta_new_position
            for point in surroundings:
                d = (new_point.x - point[0] + r) ** 2 + \
                    (new_point.y - point[1] + r) ** 2
                if d < dist:
                    dist = d
                    new_point = Position(*point)
            delta_new_position = Position(new_point.x - r, new_point.y - r)

        self._position = Position(self._position.x + delta_new_position.x,
                                  self._position.y + delta_new_position.y)

    def update_speed(self):
        self.speed += self.acceleration * self.DELTA_TIME

    def update_acceleration(self):
        if self.speed == self.MAX_SPEED or self.vehicle_ahead[0]:
            self.decelerate(0.01)
        # elif self.speed < (self.MAX_SPEED + self.MIN_SPEED) / 2:
        #     self.accelerate(0.005)
        elif abs(angle_limit((self.prev_direction - self.direction))) < 0.07:
            self.accelerate()
            self.slowing_down = False
        else:
            self.decelerate()

    def accelerate(self, delta=None):
        self.acceleration += self.DELTA_ACCEL if delta is None else delta

    def decelerate(self, delta=None):
        self.acceleration -= self.DELTA_DECEL if delta is None else delta

    def event_tracker(self):
        sensor_value, s = self.sense()
        if not s and sum(self.past[2]) < 2:
            self.direction += math.pi
            # broadcast road close
            self.broadcast_message(2, 'Road Closed', 100)
        self.past[2].append(s)
        self.steer = sensor_value * 0.2 + self.prev_sensor * 0.01
        self.prev_sensor = sensor_value

        self.past[0].append(self.acceleration)
        self.past[3].append(self.speed)
        if (
            self.slowing_down == False
            and min(self.past[3][i] for i in range(4)) > self.past[3][-1] == self.MAX_SPEED_BAD
        ):
            # broadcast slowdown
            self.slowing_down = True
            self.broadcast_message(3, 'Slow Down', 60)

        self.past[1].append(self.road_type)
        if self.road_type == 1 and sum(self.past[1]) == 1:
            # broadcast bad road
            self.broadcast_message(1, 'Bad Road', 150)

        if self.world.tick % 1000 == 0:
            self.broadcast_message(0, 'Weather', 500)

    def break_down(self):
        self.broken = True
        self.override_acceleration = True
        self.override_speed = True
        self._acceleration = 0
        self._speed = 0


class Map:
    vehicles = []

    def __init__(self, map_file):
        self.map_file = map_file
        self.map = cv2.imread(map_file)
        # if add_border:
        #     h, w = self.map.shape[0:2]
        #     base_size = h+20, w+20, 3
        #     base = np.ones(base_size, dtype=np.uint8) * 255
        #     base[10:h+10, 10:w+10] = self.map
        #     self.map = base
        x, y, _ = np.where(self.map == (0, 0, 0))
        self.valid_points = list(set(zip(y, x)))

    def surroundings(self, vehicle, r=10):
        x, y = vehicle.position.x - r, vehicle.position.y - r
        sub_map = self.map[y:y + 2 * r, x:x + 2 * r]
        # cv2.imshow(str(vehicle.color), sub_map)
        x, y, _ = np.where(sub_map != (255, 255, 255))
        bad = all(self.map[vehicle.position.y, vehicle.position.x] == [0, 0, 253]) or all(self.map[vehicle.position.y,
                                                                                                   vehicle.position.x] == [0, 0, 254]) or all(self.map[vehicle.position.y, vehicle.position.x] == [0, 0, 255])
        return list(set(zip(y, x))), bad
