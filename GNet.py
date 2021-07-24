import socket
import multiprocessing
import subprocess
import os
from getmac import get_mac_address
from datetime import datetime
from prettytable import PrettyTable

def pinger(job_q, results_q):
    """
    Do Ping
    :param job_q:
    :param results_q:
    :return:
    """
    DEVNULL = open(os.devnull, 'w')
    c = 0
    while True:
        ip = job_q.get()
        if ip is None:
            break
        try:
            subprocess.check_call(['ping','-c1', ip],
                                  stdout=DEVNULL)
            results_q.put(ip)
        except:
            pass


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def map_network(pool_size=255):
    ip_list = list()

    # get my IP and compose a base like 192.168.1.xxx
    ip_parts = get_my_ip().split('.')
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'

    # prepare the jobs queue
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    pool = [multiprocessing.Process(target=pinger, args=(jobs, results)) for i in range(pool_size)]

    for p in pool:
        p.start()

    # cue hte ping processes
    for i in range(1, 255):
        jobs.put(base_ip + '{0}'.format(i))

    for p in pool:
        jobs.put(None)

    for p in pool:
        p.join()

    # Collect IPs result
    while not results.empty():
        ip = results.get()
        ip_list.append(ip)
    if results.empty():
        ip = "None"
        ip_list.append(ip)
    return ip_list

def getSSID():
    results = subprocess.check_output(["netsh", "wlan", "show", "network"])
    results = results.decode("ascii")
    results = results.replace("\r","")
    ls = results.split("\n")
    ls = ls[4:]
    ssids = []
    x = 0
    while x < len(ls):
        if x % 5 == 0:
            ssids.append(ls[x])
        x += 1
    return ssids

def getCurrentNetwork():
    current_network = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8').split('\n')
    ssid_line = [x for x in current_network if 'SSID' in x and 'BSSID' not in x]
    if ssid_line:
        ssid_list = ssid_line[0].split(':')
        connected_ssid = ssid_list[1].strip()
        return connected_ssid

def getDataTable():
    counter = 1
    lst = map_network()
    dt = PrettyTable()
    dt.field_names = ["ID", "IP","MAC Address", "Hostname", "Date/Time"]
    macDefault = "None"
    now = datetime.now()
    dt_string = now.strftime("%d-%M-%Y %H:%M:%S")

    for i in range(len(lst)):
            mac = get_mac_address(ip=lst[i])
            dt.add_row([counter,lst[i],mac,macDefault,dt_string])
            counter += 1
    return dt

if __name__ == '__main__':
    print()
    print('Mapping Local Area Network')

    # Get all networks SSID avalaibles
    #BSSID = getSSID()
    #for i in range(len(BSSID)):
    #    print(BSSID[i])

    # Get current connected network
    print("\u001b[36;1m" + getCurrentNetwork(), " ", get_my_ip() + "\u001b[37m")
    print('Developed by G')
    print()
    print(getDataTable())

    exit()