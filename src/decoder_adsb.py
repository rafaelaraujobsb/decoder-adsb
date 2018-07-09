import  pyModeS as pms
import pprint
import time as t
import sys

#
# Downlink Format válido: 17 ou 18
#  

data = {}
corrupted = []
incorrectDF = []

# controla qual indice alterar de posicão
# 'contPosBARO': 0, 
# 'contPosGNSS': 0

def posicao(msg, icao, key):
    '''
        Função para determinar o que fazer quando receber uma posição
        key: chave do dicionario que se deseja alterar

        0 para even
        1 para odd
    '''
    timestamp = int(t.time())

    typeMsg = pms.adsb.oe_flag(msg)

    if typeMsg == 0:
        data[icao]['evenMsg' + key] = (msg, timestamp)
    else:
        data[icao]['oddMsg' + key] = (msg, timestamp)

    # verifica se possui mensagem odd e even da posição
    if data[icao]['evenMsg' + key] != None and data[icao]['oddMsg' + key] != None:
        even = data[icao]['evenMsg' + key]
        odd = data[icao]['oddMsg' + key]

        return pms.adsb.position(even[0], odd[0], even[1], odd[1], -15.8037544, -48.0866267)

with open("../mensagens/adsb_all.txt") as f:
    msgs = []

    for line in f.readlines():
        msgs.append(line.replace("*","").replace(";","").replace("\n",""))

print("Total de mensagens captadas: %d" %(len(msgs)))

for msg in msgs:
    
    # verificação da mensagem
    if int(pms.crc(msg, encode=False)) != 0:
        corrupted.append(msg)
        continue
    elif 17 != pms.df(msg) != 18:
        incorrectDF.append(msg)
        continue

    icao = pms.adsb.icao(msg) # ICAO aeronava

    # Informações necessárias da aeronave
    if not icao in data:
        data[icao] = {
            'mensagens': 0,
            'identificação': None,
            'posiçãoSurface': [],
            'BARO': [],
            'velocidades':[],
            'GNSS': [],
            'reserved': [],
            'status': [],
            '29': [],
            'version': None,
            'evenMsgBARO': None,
            'oddMsgBARO': None,
            'evenMsgGNSS': None,
            'oddMsgGNSS': None,
            'evenMsgSurface': None,
            'oddMsgSurface': None,
            'altitude': []
        }
    
    data[icao]['mensagens'] += 1

    typecode = pms.adsb.typecode(msg) # tipo da mensagem

    # Identificação do avião
    if 1 <= typecode <= 4:
        data[icao]['identificação'] = pms.adsb.callsign(msg)
    
    # posição em relação a surface
    elif 5 <= typecode <= 8:
        data[icao]['posiçãoSurface'].append(posicao(msg, icao, "Surface"))
    
    # Airborne position (w/ Baro Altitude)
    elif 9 <= typecode <= 18:
        # data[icao]['BARO'] = pms.adsb.airborne_position_with_ref(msg,  -15.8037544, -48.0866267)
    
        data[icao]['BARO'].append(posicao(msg, icao, 'BARO'))
        data[icao]['altitude'].append(pms.adsb.altitude(msg))
    
    # Airborne velocities
    elif typecode == 19:
        data[icao]['velocidades'].append(pms.adsb.velocity(msg))
    
    # Airborne position (w/ GNSS Height)
    elif 20 <= typecode <= 22:
        data[icao]['GNSS'].append(posicao(msg, icao, 'GNSS'))

        # Altitude
        if typecode < 22:
            data[icao]['altitude'].append(pms.adsb.altitude(msg))
            
    elif 23 <= typecode <=27:
        data[icao]['reserved'].append(msg)
    
    elif typecode == 28:
        data[icao]['status'].append(msg)
    
    # Target state and status information
    elif typecode == 29:
        data[icao]['29'].append(msg)
    
    # Aircraft operation status
    elif typecode == 31:
        data[icao]['version'] = pms.adsb.version(msg)
    
    else:
        data[icao]['error'] = 'Não foi encontrado uma referência'

    #t.sleep(1.25)

print("Mensagens corrompidas ou fora do padrão: %d\n" %(len(corrupted) + len(incorrectDF)))

aeronaves = []

for icao in data.values():
    if icao['identificação'] != None:
        aeronaves.append(icao['identificação'])

aeronaves.sort()

print("Aeronaves: " + ', '.join(aeronaves))


print(pprint.pformat(data))