from nameko.events import EventDispatcher, event_handler, SERVICE_POOL, SINGLETON
from nameko.rpc import rpc
from werkzeug.datastructures import FileStorage
import subprocess

class RemoteCallDemucsService:
    """ Service that can be called remotely """
    name = "remote_call_demucs_service"

    # This method will be called via rpc
    # it just call via cli demucs
    @rpc
    def call_demucs(self, audiofile, filename ):
        # f = open(str(uuid.uuid1())+".mp3","wb")
        f = open(filename,"wb")
        f.write(audiofile)
        f.close()
        #print("recibido desde http service:", payload)
        #return "archivo procesado"
        code = subprocess.call("python3 -m demucs.separate --dl -n demucs { filename }", shell=True)
        return code
