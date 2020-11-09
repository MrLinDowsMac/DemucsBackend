from nameko.events import EventDispatcher, event_handler, SERVICE_POOL, SINGLETON
from nameko.rpc import rpc
from werkzeug.datastructures import FileStorage
import subprocess
import os
from pathlib import Path

class RemoteCallDemucsService:
    """ Service that can be called remotely """
    name = "remote_call_demucs_service"

    # This method will be called via rpc
    # it just call via cli demucs
    @rpc
    def call_demucs(self, audiofile, filename ):
        
        #Receives binary file from caller and writes to volume
        filepathw = Path(f"/data/{ filename }")
        f = open(str(filepathw),"wb")
        f.write(audiofile)
        f.close()
        #print("recibido desde http service:", payload)
        
        models_path = os.getenv('TRAINED_MODELS_PATH')
        outputfolder = Path(f"{filepathw.parent}/{filepathw.stem}")
        #TODO: Add additional parameters and a way to called in a sanitized way
        #TODO: Add parameter mp3
        exitcode = subprocess.call(f"python3 -m demucs.separate -n demucs --models { models_path } --out { str(outputfolder) } { str(filepathw) }" , shell=True)
        return exitcode
