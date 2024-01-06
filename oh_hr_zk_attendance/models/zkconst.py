# -*- coding: utf-8 -*-
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################
from datetime import datetime

USHRT_MAX = 65535


CMD_CONNECT = 1000
CMD_EXIT = 1001
CMD_ENABLEDEVICE = 1002
CMD_DISABLEDEVICE = 1003

CMD_ACK_OK = 2000
CMD_ACK_ERROR = 2001
CMD_ACK_DATA = 2002

CMD_PREPARE_DATA = 1500
CMD_DATA = 1501

CMD_USERTEMP_RRQ = 9
CMD_ATTLOG_RRQ = 13
CMD_CLEAR_DATA = 14
CMD_CLEAR_ATTLOG = 15

CMD_WRITE_LCD = 66

CMD_GET_TIME  = 201
CMD_SET_TIME  = 202

CMD_VERSION = 1100
CMD_DEVICE = 11

CMD_CLEAR_ADMIN = 20
CMD_SET_USER = 8

LEVEL_USER = 0
LEVEL_ADMIN = 14

def encode_time(t):
    """Encode a timestamp send at the timeclock

    copied from zkemsdk.c - EncodeTime"""
    d = ( (t.year % 100) * 12 * 31 + ((t.month - 1) * 31) + t.day - 1) *\
         (24 * 60 * 60) + (t.hour * 60 + t.minute) * 60 + t.second

    return d


def decode_time(t):
    """Decode a timestamp retrieved from the timeclock

    copied from zkemsdk.c - DecodeTime"""
    second = t % 60
    t = t / 60

    minute = t % 60
    t = t / 60

    hour = t % 24
    t = t / 24

    day = t % 31+1
    t = t / 31

    month = t % 12+1
    t = t / 12

    year = t + 2000

    d = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

    return d
