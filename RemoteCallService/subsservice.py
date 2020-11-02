from nameko.events import EventDispatcher, event_handler, SERVICE_POOL, SINGLETON
from nameko.rpc import rpc
from werkzeug.datastructures import FileStorage
import subprocess

class SubService:
    """ Event listening service. """
    name = "subsservice"

    #@event_handler("http_service", event_type=SINGLETON )
    #def handle_event(self, payload):
    @rpc
    def servicio_remoto(self, audiofile, filename ):
        # f = open(str(uuid.uuid1())+".mp3","wb")
        f = open(filename,"wb")
        f.write(audiofile)
        f.close()
        #print("recibido desde http service:", payload)
        #return "archivo procesado"
        code = subprocess.call("python3 -m demucs.separate --dl -n demucs { filename }", shell=True)
        return code
