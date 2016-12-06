from gritty_soap.client import Client
import re
import os
import io
import mmap
import xml.etree.ElementTree as etree

def format_wsdl(ip):
    formatted_wsdl = ''
    with open('../panopticon/opc_xml_da_server_formattable.asmx', 'r') as f:
        for idx, line in enumerate(f):
            match = re.search(r'{ip}', line)
            if match:
                line = line.format(ip=ip)
            formatted_wsdl = formatted_wsdl + line
    # todo: figure out how to return some kind of in-memory file object that Client will accept
    formatted_wsdl = io.BytesIO(formatted_wsdl.encode('utf-8'))
    return formatted_wsdl

if __name__ == '__main__':
    wsdl = format_wsdl('172.16.22.100')
    client = Client(wsdl=wsdl, service_name='OpcXmlDA')
