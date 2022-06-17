import os
import socket
import csv
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

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
    output_stream = os.popen("nslookup " + ip_address)
    server_address = output_stream.read()

    if 'Name' not in server_address:
        hostname = "No Connection / Does Not Exist"
        output_address = ip_address

    else:
        if 'Addresses' in server_address:
            substring = server_address.split('Name:')[1].split("Addresses:")
        else:
            substring = server_address.split('Name:')[1].split("Address:")
        hostname = substring[0].strip().split()
        output_address = substring[1].strip().split()
    return ','.join(hostname), ','.join(output_address)


def pingable(address):
    """
    Checks to see if the given address is pingable.
    :param address: Host name or ip address
    :return: True if pingable, false if not
    """
    output_stream = os.popen("ping " + address)
    ping_output = output_stream.read()
    if "Reply from" in ping_output:
        can_ping = True
    else:
        can_ping = False
    return [can_ping]


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