import win32gui,pyscreenshot,random,time,logging
from constants import *
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

lg = logging.getLogger()

class Schlong():
    def __init__(self):
        self.driver = None
        self.state = States.DEAD
        self.snake = {'name':'','sid':-1,'score':-1,'xx':-1,'yy':-1}
        lg.info('Inited master')
        
    def __del__(self):
        self.driver.quit()
                
    def start_driver(self):
        cdpath = 'C:\\Users\\anon\\Desktop\\schlong\\chromedriver.exe'
        copt = Options()
        copt.add_extension('C:\\Users\\anon\\Desktop\\schlong\\uBlock.crx')
        self.driver = webdriver.Chrome(executable_path=cdpath,chrome_options=copt)
        lg.info('Started chromedriver')

    def start_schlong(self):
        """Set up chromedriver and returns the hwnd for screencap"""
        self.driver.get('http://slither.io')
        self.driver.execute_script('nbg.remove()')
        self.driver.execute_script('smh.remove()')
        self.driver.execute_script('social.remove()')
        lg.info('Started schlong')
     
    def force_server(self,ip,port):
        self.driver.execute_script('forceServer(%s,%s)'%ip,str(port))

    def clean_up_game_field(self):
        self.driver.execute_script('loch.remove()') # Minimap
        self.driver.execute_script('lbs.remove()') # Leaderboard
        self.driver.execute_script('lbh.remove()')
        self.driver.execute_script('lbn.remove()')
        self.driver.execute_script('lbp.remove()')
        self.driver.execute_script('lbf.remove()')
        self.driver.execute_script('vcm.remove()')
        self.driver.execute_script('plq.remove()')
        
    # bso is the server
    def get_server_ip(self):
        return self.driver.execute_script('return bso.ip')

    #snakes[0] is self
    def get_self_location(self):
        """Returns a tuple (x,y) of the snake's head"""
        return self.driver.execute_script('return (snake == null ? [-1,-1] : [snake.xx,snake.yy])')

    def get_self_name(self):
        return self.driver.execute_script('return snake == null ? \'\' : snake.nk')

    def get_self_id(self):
        return self.driver.execute_script('return snake.id || -1')

    def get_self_dead(self):
        return self.driver.execute_script('return snake.dead || false')

    def get_self_score(self):
        return self.driver.execute_script('return Math.floor(15*(fpsls[snake.sct]+snake.fam/fmlts[snake.sct]-1)-5)')

    def get_self_rank(self):
        return self.driver.execute_script('return [rank || -1,snake_count || -1]')

    def get_self_angle(self):
        return self.driver.execute_script('return (snake == null ? -1 : snake.ang)')

    def get_self_ip(self):
        return self.driver.execute_script('return window.bso ? window.bso.ip : ""')

    def get_self_port(self):
        return self.driver.execute_script('return window.bso ? window.bso.po : ""')
        
    def snake_defined(self):
        return self.driver.execute_script('return snake == null')

    def start_new_game(self):
        self.driver.refresh()

    def run_schlong(self):
        self.start_driver()
        self.start_schlong()
        self.state = States.DEAD
            
    def loop_once(self):
        lg.debug('Master state is %s' % str(self.state))
        if self.state == States.WAITING_START:
            if self.snake_defined() == 'false':
                return
            self.snake['name'] = self.get_self_name()
            lg.debug('Master name is %s' % self.snake['name'])
            if self.snake['name'] != "":
                self.snake['sid'] = self.get_self_id()
                lg.debug('Master sid is %s' % self.snake['sid'])
                self.state == States.STARTED
        elif self.state == States.STARTED:
            self.clean_up_game_field()
            self.snake['xx'],snake['yy'] = eval(self.get_self_location())
            lg.debug('Master loc is %5d, %5d' % (self.snake['xx'],self.snake['yy']))
            if self.get_self_dead() == 'true':
                lg.debug('Master is dead')
                self.state = States.DEAD
        elif self.state == States.DEAD:
            if auto_restart:
                if force_server:
                    self.force_server(force_server_ip,force_server_port)
                self.start_game()
            self.state = States.WAITING_START
        lg.debug('Master state becomes %s' % str(self.state))
