import socket
import csv
import dns.resolver
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
import subprocess
import platform


list_of_ports = [22, 80, 443, 5000, 7878, 8080]

ip_address_list = ["dc1prnsrvgr0001.es.ad.adp.com",
                   "c003gisapp01.net.adp.com",
                   "10.204.224.105",
                   "cdlprscdvap0001.es.ad.adp.com",
                   "11.17.1.41",
                   "7.6.255.240",
                   "10.204.226.73",
                   "7.6.254.72",
                   "dc1prscdvap0003.es.ad.adp.com",
                   "dc2prscdvap0003.es.ad.adp.com",
                   "smartservices.net.adp.com"]


def multi_thread(address_list, input_function):
    """
    This function takes advantage of multi-threading and runs the input_function on each item in the address_list.

    :param address_list: A list of addresses (host name or ip address)
    :param input_function: A function to be run over each address
    :return: A list of output from the input_function
    """
    pool = Pool(cpu_count())
    results = pool.map(input_function, address_list)
    pool.close()
    pool.join()
    return results


# extracting name and address
def getNameAndAddress(ip_address):
    """
    Given a host name or ip address, returns both host name and ip address

    :param ip_address: Host name or ip address for nslookup
    :return: Host name, ip address
    """
    if socket.gethostbyname(ip_address) == ip_address:
        (hostname,aliases,output_address) = socket.gethostbyaddr(ip_address)
    else:
        hostname = ip_address
        output_address = []
        resolver = dns.resolver.Resolver()
        result = resolver.resolve(hostname)
        for res in result:
            output_address.append(str(res))
    return ','.join([hostname]), ','.join(output_address)


def pingable(address):
    """
    Checks to see if the given address is pingable.

    :param address: Host name or ip address
    :return: True if pingable, false if not
    """
    def pingOk(sHost):
        try:
            output = subprocess.check_output(
                "ping -{} 1 {}".format('n' if platform.system().lower() == "windows" else 'c', sHost), shell=True)
        except:
            return [False]
        return [True]
    return pingOk(address)


def check_ports(address):
    """
    Checks to see if ports 22, 80, 443, 5000, 7878, 8080 are open given an address
    :param address: Host name or ip address
    :return: List of all open ports (if none are open, returns empty list)
    """
    open_ports = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in list_of_ports:
        result = sock.connect_ex((address, i))
        if result == 0:
            i = str(i)
            open_ports.append(i)
    sock.close()
    return open_ports


def threadForSingleAddress(ip_address):
    """
    Process that gets both host name and ip address, checks to see if the address is pingable, and then gets a list of open ports.
    :param ip_address: Host name or ip address
    :return: List of summarizing data for the input address
    """
    # extracting name and address
    hostname, output_address = getNameAndAddress(ip_address)

    # check if IP is pingable
    can_ping = pingable(ip_address)[0]

    # check if port is open
    open_ports = []
    if can_ping:
        open_ports = check_ports(ip_address)

    return [output_address, hostname, can_ping, ','.join(open_ports)]


if __name__ == "__main__":

    csv_rows = multi_thread(ip_address_list, threadForSingleAddress)

    # write to csv
    header = ["Ip_Addresses", "Name", "Pingable", "Open Ports"]
    with open('data_generated.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in csv_rows:
            writer.writerow(row)