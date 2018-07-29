import threading
import schedule
import time as t
from server.adsb_server import start_server
from pool.worker import controll
from utils.adsb import save

if __name__ == "__main__":
    # inicar servidor
    threading.Thread(target=start_server).start()
    threading.Thread(target=controll).start()

    schedule.every(30).seconds.do(save)

    while True:
        schedule.run_pending()
        t.sleep(3)
