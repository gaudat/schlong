import random,threading,logging
from dilldo import ZombieSnake
from schlong import Schlong
from constants import *
import servers

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(threadName)-15s %(funcName)-15s %(message)s')
lg.info('Schlongs of Slither')

##s = servers.get_servers()
##lg.info('Got server list')
##target_server = random.choice(s)
##lg.info('Target server is %s:%s' % (target_server['ip'],target_server['port']))
zombies = []
z_threads = []
lg.debug('has_zombies: %s' % str(has_zombies))
if has_zombies:
    for i in range(zombie_count):
        zombies.append(ZombieSnake())
        lg.debug('Added ZombieSnake in zombies[%d]' % i)
        z_threads.append(None)

master = Schlong()
master.run_schlong()
lg.info('Master is schlong')
while master.state != States.STARTED:
    master.loop_once()
    lg.debug('Schlong is not started')
if master.state == States.STARTED:
    lg.debug('Schlong is started')
    master.loop_once()
    s_ip = master.get_self_ip()
    lg.debug('Master IP is %s' % s_ip)
    s_port = master.get_self_port()
    lg.debug('Master port is %s' % s_port)
    s_loc = eval(master.get_self_location())
    lg.info('Master location is %5d, %5d' % tuple(s_loc))
    if has_zombies:
        for i,z in enumerate(zombies):
            if not z.ws.connected:
                lg.debug('Zombie %d is not connected'%i)
                z.ip = s_ip
                z.port = s_port
                z.connect()
                lg.info('Zombie %d is (re)connected'%i)
                z.self_dead = False
            if z_threads[i] == None:
                lg.debug('Zombie loop %d is None' % i)
                z_threads[i] = threading.Thread(None,z.loop_once,'Zombie-Loop-%d'%i)
                z_threads[i].start()
                lg.info('Zombie loop %d started' % i)
            z.update_target(s_loc[0],s_loc[1])
            log.info('Zombie %d new target is %5d, $5d' % tuple(s_loc))
            
            
