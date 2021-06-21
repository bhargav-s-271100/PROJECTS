from trafficsim import *
from threading import Thread


def thread_main(world):
    world.show_colors()
    while not kill and cv2.waitKey(10):
        world.step()
        world.render()

if __name__ == '__main__':
    with open('log.txt', 'w') as f:
        pass
    MAP_FILE = 'maps/map0_.jpg'
    # colors = [(0, 0, 255),
    # (0, 255, 0),
    # (255, 0, 0),
    # (0, 255, 255),
    # (255, 0, 255),
    # (255, 255, 0)]
    world = World(MAP_FILE, 5, 'SVM')
    # for i, c in enumerate(colors):
    #     if i == len(world.vehicles):
    #         break
    #     world.vehicles[i].color = c
    kill = False

    thread = Thread(target=thread_main, args=(world,))
    thread.start()

    try:
        while True:
            command = input('>>> ')
            if command == 'end':
                kill = True
                break
            elif command != '':
                try:
                    op, veh, prm, val, *_ = (command.split()) + ['', '']
                    print(op, veh, prm, val)
                    veh = world.vehicles[int(veh)]
                    prm_dict = {
                        'a': 'acceleration',
                        'mxa': 'MAX_ACCEL',
                        'mna': 'MIN_ACCEL',
                        's': 'speed',
                        'mxs': 'MAX_SPEED',
                        'mns': 'MIN_SPEED',
                        'va': 'vehicle_ahead',
                    }
                    if val != '':
                        val = float(val)

                    if op == 'get':
                        print(getattr(veh, prm_dict[prm]))
                    elif op == 'set':
                        if prm in {'a','s'}:
                            setattr(veh, 'override_'+prm_dict[prm], True)
                        setattr(veh, prm_dict[prm], val)
                        print(f'set {prm_dict[prm]} to {val}')
                    elif op == 'rst':
                        veh.override_acceleration = False
                        veh.override_speed = False
                    elif op == 'bd':
                        veh.break_down()
                    else:
                        exec(command)
                except Exception as e:
                    print(e)
                    print('Invalid command')
    except KeyboardInterrupt:
        kill = True

    thread.join()

    cv2.destroyAllWindows()
