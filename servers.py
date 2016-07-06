import requests

server_list = 'http://slither.io/i33628.txt'

def get_servers(server_list=server_list):
    """Returns a dict of servers from the list file"""
    resp = requests.get(server_list)
    if resp.ok:
        servers = resp.text
    servers = servers[1:]
    servers = [ord(l)-97 for l in servers]
    servers = [(l-7*i)%26 for i,l in enumerate(servers)]
    servers = [a*16+b for a,b in zip(servers[::2],servers[1::2])]
    # 11 numbers = 1 server
    serverdict = []
    for i in range(int(len(servers)/11)):
        start_index = 11*i
        server = {}
        server["ip"] = '.'.join([str(i) for i in servers[start_index:start_index+4]])
        server["port"] = (servers[start_index+4]<<16)+(servers[start_index+5]<<8)+servers[start_index+6]
        server["port"] = str(server["port"])
        serverdict.append(server)
    return serverdict
