import websocket,struct,random,binascii,threading,math,logging,time
from constants import *

class ZombieSnake():
    def __init__(self,debug=False):
        #websocket.setdefaulttimeout(1) # Prevent locking
        self.pool = []
        self.debug = debug
        self.skins = 39
        self.skin_id = int(random.random()*self.skins)
        self.ip = ""
        self.port = ""
        self.pingthread = None
        self.snakes = []
        self.self_snake = {}
        self.self_target = {}
        self.self_dead = True
        self.pong = True
        if self.debug:
            lg.debug('Zombie debug is True')
            websocket.enableTrace(1)
            self.wss = []
        lg.info('ZombieSnake inited')

    def set_username_and_skin(self):
        return struct.pack('BBBs',115,7,self.skin_id,self.nick.encode('utf8'))

    def ping(self):
        lg.debug('Sent ping')
        return struct.pack('B',251)

    def connect(self,ip,port):
        self.ws = None
        self.ws = websocket.create_connection('ws://%s:%s/slither'%(self.ip,self.port)
                                        ,header=["User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17"]
                                        ,origin='http://slither.io'
                                        ,host='%s:%s'%(self.ip,self.port))
        assert self.ws.connected
        lg.info('Connected to %s:%s' % (self.ip,str(self.port)))

    def set_pool_of_snakes(self,pool):
        self.pool = pool

    def send_ping(self):
        if self.pong:
            self.ws.send(self.ping())
        self.pong = False

    def update_target(self,xx,yy):
        self.self_target = {'xx':xx,'yy':yy}
        lg.info('Set target to %5d, %5d' % (xx,yy))

    def start_game(self):
        self.snakes = []
        self.self_snake = {'sid':-1,'xx':-1,'yy':-1}
        self.self_target = {'xx':-1,'yy':-1}
        self.self_dead = False
        self.ws.send(self.set_username_and_skin())
        self.pong = True
        self.send_ping()
        logging.logging('Started game')
        def set_interval(func, sec):
            def func_wrapper():
                set_interval(func, sec)
                func()
            t = threading.Timer(sec, func_wrapper)
            t.start()
            return t
        self.pingthread = set_interval(self.send_ping,0.25)
        lg.debug('Started ping thread')

    def loop_once(self):
        run_eugenics()
        if self.self_dead:
            lg.info('Zombie is dead')
            self.pingthread.cancel()
            self.pingthread = None
            lg.debug('Stopped ping thread')
            self.ws.close()
            lg.debug('Closed connection')
            time.sleep((random.random()*1.5+0.5)*zombie_spawn_delay)
            self.connect()
            self.start_game()
        packet = self.ws.recv()
        self.parse_packet(packet)
        if self.debug:
            self.wss.append(packet)
        self.send_packet()

    def send_packet(self):
        """Send packet to change direction"""
        deltax = self.self_target['xx'] - self.self_snake['xx']
        deltay = self.self_target['yy'] - self.self_snake['yy']
        angle = math.atan(deltay/deltax)
        if deltax < 0:
            angle += math.pi
        angle = int(angle/2/math.pi*250)

        lg.debug("Send angle: %i" % angle)
        self.ws.send()

    def update_snake_pool(self,sid,xx,yy):
        if sids == []:
            self.snake['sid'] = sid
            self.snake['xx'] = xx
            self.snake['yy'] = yy
        if sid == self.snake['sid']:
            self.snake['xx'] = xx
            self.snake['yy'] = yy
        sids = [i['sid'] for i in self.pool]
        if sid not in sids:
            self.pool.append({'sid':sid,'xx':xx,'yy':yy})
        else:
            assert self.pool[sids.index(sid)]['sid'] == sid
            self.pool[sids.index(sid)]['xx'] = xx
            self.pool[sids.index(sid)]['yy'] = yy

    def update_snake_pool_rel(self,sid,offsetx,offsety):
        if sid == self.snake['sid']:
            self.snake['xx'] += (offsetx - 128)
            self.snake['yy'] += (offsety - 128)            
        sids = [i['sid'] for i in self.pool]
        assert self.pool[sids.index(sid)]['sid'] == sid
        self.pool[sids.index(sid)]['xx'] += (offsetx - 128)
        self.pool[sids.index(sid)]['yy'] += (offsety - 128)

    def del_snake_from_pool(self,sid):
        if sid == self.snake['sid']:
            self.self_dead = True
            lg.info('Zombie is dead')
        sids = [i['sid'] for i in self.pool]
        assert self.pool[sids.index(sid)]['sid'] == sid
        self.pool.pop(sids.index(sid))

    def run_eugenics(self):
        """Kills the snake if it is not near the master enough"""
        if self.self_target['xx'] == -1 or self.snake['xx'] == -1:
            return
        if abs(self.snake['xx'] - self.self_target['xx']) > zombie_spawn_radius:
            lg.info('Killed zombie because it spawned too far')
            self.self_dead = True

    def parse_packet(self,payload):
        #print(binascii.hexlify(payload))
        ptype = payload[2]
        if ptype == ord('a'):
            func = 'initial setup'
        elif ptype == ord('g'):
            sid = (payload[3] << 8) + payload[4]
            xx = (payload[5] << 8) + payload[6]
            yy = (payload[7] << 8) + payload[8]
            self.update_snake_pool(sid,xx,yy)
            func = 'move snake, id=%s, xx=%s, yy=%s'% (sid,xx,yy)
        elif ptype == ord('G'):
            sid = (payload[3] << 8) + payload[4]
            offsetx = payload[5]
            offsety = payload[6]
            self.update_snake_pool_rel(sid,offsetx,offsety)
            func = 'move snake rel, id=%s, ofsx=%s, ofsy=%s'% (sid,offsetx,offsety)
        elif ptype == ord('n') or ptype == ord('N'):
            sid = (payload[3] << 8) + payload[4]
            xx = (payload[5] << 8) + payload[6]
            yy = (payload[7] << 8) + payload[8]
            func = 'increase snake, id=%s, xx=%s, yy=%s'% (sid,xx,yy)
        elif ptype == ord('s'):
            if len(payload) == 6:
                sid = (payload[3] << 8) + payload[4]
                self.del_snake_from_pool(sid)
                func = 'delete snake, id=%s' % sid
            else:
                assert len(payload) >= 31
                sid = (payload[3] << 8) + payload[4]
                print('s payload: %s' % binascii.hexlify(payload))
                xx = (payload[18] << 16) + (payload[19] << 8) + payload[20]
                yy = (payload[21] << 16) + (payload[22] << 8) + payload[23]
                xx /= 5
                yy /= 5
                self.update_snake_pool(sid,xx,yy)
                func = 'add snake, id=%s, xx=%s, yy=%s'% (sid,xx,yy)
        elif ptype == ord('p'):
            self.pong = True
            func = 'pong'
        elif ptype == ord('v'):
            func = 'dead'
        else:
            return
            func = chr(ptype)
            # Other packets are of no use
        lg.debug('Received %s' % (func))
    
