"""agn_binder.py"""

import atexit
import gobject
import os
import fcntl
import socket
import struct
import time
from subprocess import Popen, PIPE

STATE_UNKNOWN = 0
STATE_UNCHANGED = 1
STATE_NOT_CONNECTED = 10
STATE_DAEMON_DEAD = 15
STATE_BEFORE_CONNECT = 100
STATE_SMX_AUTHENTICATING = 200
STATE_VPN_CONNECTING = 300
STATE_VPN_RECONNECTED = 350
STATE_CONNECTED = 400
STATE_DISCONNECTING = 500
STATE_AFTER_CONNECT = 600

SERVICE_MANAGER_ADDRESS = '204.146.172.230' # AT&T Production RIG

class AgnBinder(gobject.GObject):
    """
    Provides an interface between python and AGNC's daemon.
    """

    cmd = '../dist/agnc-bind'

    def __init__(self):
        super(AgnBinder, self).__init__()

        execfilepath = os.path.join(os.path.dirname(__file__), self.cmd)
        self.proc = proc = Popen([execfilepath], stdout=PIPE, stdin=PIPE)

        # https://www.domenkozar.com/2009/09/13/read-popenstdout-object- \
        #   asynchronously-or-why-low-level-knowledge-holes-are-killing-me/
        fdn = proc.stdout.fileno()
        file_flags = fcntl.fcntl(fdn, fcntl.F_GETFL)
        fcntl.fcntl(fdn, fcntl.F_SETFL, file_flags | os.O_NDELAY)

        gobject.io_add_watch(proc.stdout, gobject.IO_IN, self.__get_output__)
        atexit.register(self.proc.kill)

    def __get_output__(self, stdout, _):
        out = __get_line__(stdout)
        if out == '':
            return False
        self.__process_line__(out)
        print 'vpn >', out
        return True

    def __next_line__(self):
        while True:
            try:
                line = __get_line__(self.proc.stdout)
            except IOError as err:
                print err
                time.sleep(0.1)
                continue
            return line

    def __get_lines__(self):
        lines = []
        while True:
            line = self.__next_line__()
            print 'vpn >', line
            if line == 'EOF':
                return lines
            else:
                lines.append(line)

    def __wait__(self, type_change=None):
        line = self.__next_line__()
        print 'vpn >', line
        self.__process_line__(line)
        if line.startswith(type_change):
            return

    def __process_line__(self, line):
        try:
            (change_type, param) = line.split('\t')
            self.emit('agn_' + change_type, int(param))
        except ValueError:
            pass

    def __get_object_response__(self):
        res = {}
        for line in self.__get_lines__():
            try:
                (_, prop, value) = line.split("\t")
                if 'IP' in prop:
                    value = long2ip(long(value))
                res[prop] = value
            except ValueError:
                self.__process_line__(line)
        return res

    def __send__(self, num, args=None):
        if not args:
            args = []

        stdin = '\n'.join([str(num) + ' ' + str(len(args))] + args) + '\n'
        print 'vpn <', stdin,
        self.proc.stdin.write(stdin)

    def exit(self):
        """
        Exit subprocess.
        """
        self.__send__(0)

    def action_connect(self, account, username, password):
        """
        Issues a connect action to AGNC's daemon with the provided account,
        username and password against AT&T's production servers.
        """
        self.__send__(1, [account, username, password, SERVICE_MANAGER_ADDRESS])
        self.__wait__('state_change')

    def action_disconnect(self):
        """
        Issues a disconnect action to the daemon.
        """
        self.__send__(2)
        self.__wait__('state_change')

    def get_connect_attempt_info(self):
        """
        Returns a dictionary with AGNC's connect attempt information.
        """
        self.__send__(3)
        return self.__get_object_response__()

    def get_state(self):
        """
        Returns an int with AGNC's current state
        """
        self.__send__(4)
        return int(self.__get_lines__()[0])

    def get_user_info(self):
        """
        Returns a dictionary with AGNC's user information.
        """
        self.__send__(5)
        return self.__get_object_response__()


def long2ip(long_ip):
    """
    Convert a long to an IP string
    """
    packed = struct.pack('<L', long_ip)
    return socket.inet_ntoa(packed)

def __get_line__(stream):
    line = stream.readline()
    # trim \n
    return line[0:len(line) - 1]

for evt in ['agn_action_requested', 'agn_state_change']:
    gobject.signal_new(evt, AgnBinder, gobject.SIGNAL_RUN_CLEANUP, None, (int, ))
