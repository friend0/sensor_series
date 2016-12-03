from gritty_soap.client import Client
import re
import os
import io
import mmap

def format_wsdl(ip):
    formatted_wsdl = ''
    map = mmap.mmap(fileno=0, length=2**16)
    with open('../opc_xml_da_server_formattable.asmx', 'r') as f:
        for idx, line in enumerate(f):
            match = re.search(r'{ip}', line)
            if match:
                line = line.format(ip=ip)
            formatted_wsdl = formatted_wsdl + line
    with open('../opc_temp.wsdl', 'w') as f:
        for idx, line in enumerate(formatted_wsdl):
            f.write(line)
    # todo: figure out how to return some kind of in-memory file object that Client will accept

if __name__ == '__main__':
    wsdl = format_wsdl('172.16.22.100')
    client = Client(wsdl='../opc_temp.wsdl', service_name='OpcXmlDA')