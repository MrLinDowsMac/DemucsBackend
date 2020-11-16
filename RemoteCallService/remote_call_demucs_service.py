from nameko.rpc import rpc, RpcProxy
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
        
        models_path = os.getenv('TRAINED_MODELS_PATH')
        outputfolder = Path(f"{filepathw.parent}/{filepathw.stem}") #will create folder of same filename
        #TODO: Add additional parameters 
        exitcode = subprocess.call(f"python3 -m demucs.separate " + 
            f"-n demucs " + 
            f"--models { models_path } " + 
            f"{ '--mp3' if filepathw.suffix == '.mp3' else '' } " + #mp3
            f"--out { str(outputfolder) } " + 
            f"{ str(filepathw) }" 
            ,shell=True
            )
        return exitcode
