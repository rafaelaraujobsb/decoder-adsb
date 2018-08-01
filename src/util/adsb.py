import  pyModeS as pms
import pprint
import time as t

#
# Downlink Format válido: 17 ou 18
#  

# Localização da antena
lat_antenna = -15.8037544
lon_antenna = -48.0866267

aircrafts = {} # armazena as instâncias das classes

class Aircraft():
    def __init__(self, icao):
        self.icao = icao
        self.identification = None

        self.code_29 = [] # state and status information
        self.count_msgs = 0
        
        # (w/ Baro Altitude)
        # (w/ GNSS Height)
        self.position = {'baro': [], 'gnss':[], 'surface':[]}

        self.altitude = []
        self.velocities = []

        # usado para formar a posição
        self.even_msg = {'baro':(), 'gnss':(), 'surface': ()}
        self.odd_msg = {'baro':(), 'gnss':(), 'surface': ()}
        
        self.status = []
        self.version = None # versão do adsb
        self.reserved = []

        self.last_msg = None

    # substitui o hash
    def __repr__(self):
        return self.icao

    def print_info(self):
        info = 'Quantidade de mensagens: {}\n'.format(self.count_msgs)
        info += 'ICAO: {}\nIdentificação: {}\nPosição(c/ Baro Altitude): {}\n'.format(self.icao, self.identification, self.position['baro'])
        info += 'Posição(c/ Gnss Height): {}\nPosição(surface): {}\n'.format(self.position['gnss'], self.position['surface'])
        info += 'Altitude: {}\nVelocidades: {}\n'.format(self.altitude, self.velocities)
        info += 'Versão ADSB: {}\n'.format(self.version)
        info += 'Última mensagem: {}\n'.format(self.last_msg)
        
        return info

    # verifica code
    def code(self, msg):
        self.count_msgs += 1
        self.last_msg = t.strftime("%D %H:%M", t.localtime(msg[1]))

        typecode = pms.adsb.typecode(msg[0])

        # Identificação do avião
        if 1 <= typecode <= 4:
            self.identification = pms.adsb.callsign(msg[0])
        
        # posição em relação a surface
        elif 5 <= typecode <= 8:
            self.posicao(msg, "surface")
        
        # Airborne position (w/ Baro Altitude)
        elif 9 <= typecode <= 18:        
            self.posicao(msg, "baro")
            self.altitude.append(pms.adsb.altitude(msg[0]))
        
        # Airborne velocities
        elif typecode == 19:
            self.velocities.append(pms.adsb.velocity(msg[0]))
        
        # Airborne position (w/ GNSS Height)
        elif 20 <= typecode <= 22:
            self.posicao(msg, "gnss")

            # Altitude
            if typecode < 22:
                self.altitude.append(pms.adsb.altitude(msg[0]))
                
        elif 23 <= typecode <=27:
            self.reserved.append(msg)
        
        elif typecode == 28:
            self.status.append(msg)
        
        # Target state and status information
        elif typecode == 29:
            self.code_29.append(msg)
        
        # Aircraft operation status
        elif typecode == 31:
            self.version = pms.adsb.version(msg[0])
        
        else:
            print('Não foi encontrado uma referência')

    def posicao(self, msg, key):
        """
            Método que verifica o tipo da mensagem de posição e cálcula latitude e longitude.
            key: indica se é baro, gnss ou surface

            Tipo:
                0 para even
                1 para odd
        """
        type_msg = pms.adsb.oe_flag(msg[0])

        if type_msg == 0:
            self.even_msg[key] = msg
        else:
            self.odd_msg[key] = msg

        if self.even_msg[key] != () and self.odd_msg[key] != ():
            even = self.even_msg[key]
            odd = self.odd_msg[key]

            # limpando a informação usada
            self.odd_msg[key] = ()
            self.even_msg[key] = ()

            global lat_antenna
            global lon_antenna

            # index 0 = msg
            # index 1 = timestamp
            loc = pms.adsb.position(even[0], odd[0], even[1], odd[1], lat_antenna, lon_antenna)

            self.position[key].append(loc)

def save():
    global aircrafts

    with open('../info2_0.txt','w') as f:
        for aircraft in aircrafts.values():
            f.write('=====================\n')
            f.write(aircraft.print_info())
            f.write('=====================\n')
            

#função que será chamada pelo servidor
def start(msg):
    global aircrafts

    # verificação da mensagem
    try:
        if int(pms.crc(msg[0], encode=False)) != 0:
            with open('../mensagens/output/corrupted.txt', 'a') as f:
                f.write('{} {}\n'.format(msg[0], msg[1]))
        elif 17 != pms.df(msg[0]) != 18:
            with open('../mensagens/output/incorrectDF.txt', 'a') as f:
                f.write('{} {}\n'.format(msg[0], msg[1]))
        else:
            icao = pms.adsb.icao(msg[0]) # ICAO aeronave

            if icao not in aircrafts:
                aircrafts[icao] = Aircraft(icao)

            aircrafts[icao].code(msg)
    except:
        print("Erro com a mensage: ", msg)
    

def main():
    """
        SERÁ USADO PARA QUANDO O MÓDULO FOR A MAIN, OU SEJA, PASSANDO UM ARQUIVO QUE JÁ POSSUA DADOS.
    """

    """for icao in data.values():
        if icao['identificação'] != None:
        aeronaves.append(icao['identificação'])

        aeronaves.sort()

        print("Aeronaves: " + ', '.join(aeronaves))

    with open("../mensagens/adsb_all.txt") as f:
        msgs = []

        for line in f.readlines():
            msgs.append(line.replace("*","").replace(";","").replace("\n",""))

    print(pprint.pformat(data))"""
    print("Em desenvolvimento")
    

if __name__ == "__main__":
    main()
