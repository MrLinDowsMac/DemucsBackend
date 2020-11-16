from nameko.rpc import rpc, RpcProxy
from werkzeug.datastructures import FileStorage
import subprocess
import os
from pathlib import Path

class RemoteCallDemucsService:
    """ Service that can be called remotely """
    name = "remote_call_demucs_service"

    rpcMailServiceProxy = RpcProxy("sendmailservice")

    # This method will be called via rpc
    # it just call via cli demucs
    @rpc
    def call_demucs(self, audiofile, filename, email ):
        
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
        #self.send_notification_email(email, filename)        
        return exitcode
    
    # def send_notification_email(self,email,filename):
    #     subject = "Your audio file has been separated"
    #     body = f"We have separated your audio file and you can download them here: ${filepathw}"
    #     #Send email #pylint: disable=no-member
    #     self.rpcMailServiceProxy.send_email.call(email,subject, body )
