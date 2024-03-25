# -*- coding: utf-8 -*-

from struct import pack, unpack
from .zkconst import *


def zkfaceon(self):
    """Start a connection with the time clock"""
    command = CMD_DEVICE
    command_string = 'FaceFunOn'
    chksum = 0
    session_id = self.session_id
    reply_id = unpack('HHHH', self.data_recv[:8])[3]

    buf = self.createHeader(command, chksum, session_id,
        reply_id, command_string)
    self.zkclient.sendto(buf, self.address)
    try:
        self.data_recv, addr = self.zkclient.recvfrom(1024)
        self.session_id = unpack('HHHH', self.data_recv[:8])[2]
        return self.data_recv[8:]
    except:
        return False

