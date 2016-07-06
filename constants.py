import logging

lg = logging.getLogger('schlang')
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(threadName)-15s %(funcName)-15s %(message)s')
lg.addHandler(logging.StreamHandler())
lg.setLevel(0)
auto_restart = False
default_name = 'schlang'

has_zombies = True
zombie_debug = False
zombie_count = 10
zombie_spawn_radius = 5000
zombie_spawn_delay = 1

from enum import Enum
class States(Enum):
        WAITING_START = 0
        STARTED = 1
        DEAD = 2
