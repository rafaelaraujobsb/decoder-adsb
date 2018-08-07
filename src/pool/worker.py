import time
from threading import Thread, Event
from queue import Queue 
from util.adsb import start as st_adsb

messages = Queue()
event = Event()

class Worker(Thread):
    def __init__(self, target, queue, *, name='Worker'):
        super().__init__()
        self.name = name
        self.queue = queue
        self._target = target
        # self._stoped = False

    def run(self):
        print(self.name, 'pronto')
        event.wait()
        while True:
            time.sleep(1)
            try:
                adsb = self.queue.get(block=False)
            except:
                pass
            else:
                print('=> %s processando' %(self.name))
                self._target(adsb)

    '''def join(self):
        while not self._stoped:
            time.sleep(0.1)'''

def get_pool(n_th: int):
    """Retorna um número n de Threads."""
    return [Worker(target=filter_msg, queue=messages, name=f'Worker {n}') for n in range(n_th)]

def controll():
    thrs = get_pool(6)

    for th in thrs:
        time.sleep(1)
        th.start() 

    event.set()
    print('Workers iniciados') 

    '''print('joins')
    [th.join() for th in thrs]'''

def filter_msg(data):
    if len(data[0]) == 1:
        pass
    elif len(data[0]) == 31:
        data = (data[0].replace(';\r\n', ''), data[1])
        st_adsb(data)
    else:
        # tratar quando possui mais de uma mensagem adsb em data
        n_adsb = list(map(lambda x: (x, data[1]), data[0].replace('*','').split(';\r\n')[:-1]))

        for data in n_adsb:
            st_adsb(data)
