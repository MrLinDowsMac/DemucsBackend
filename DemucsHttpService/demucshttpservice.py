from nameko.web.handlers import http
from werkzeug.wrappers import Response,Request
from werkzeug.datastructures import FileStorage
from nameko.rpc import rpc, RpcProxy
from pathlib import Path
import uuid
import os
from pathlib import Path
import glob
import json

class DemucsHttpService:
    name = "demucshttpservice"    

    y = RpcProxy("remote_call_demucs_service")

    @http('POST', '/send_file')
    def do_post(self, request): 
      if request.content_type.startswith("multipart/form-data"):
        audiofile = request.files.get("file") #busca key
        original_name = audiofile.filename
        if audiofile.mimetype == "audio/mpeg" or audiofile.mimetype == "audio/wave":
          #Rename file before calling rpc method
          generated_uuid = str(uuid.uuid4())
          audiofile.filename = f"{Path(audiofile.filename).stem.replace(' ','_')}_{generated_uuid}{Path(audiofile.filename).suffix}"  
          print (audiofile.filename)
          self.metodo_llamar(audiofile)
          objResponse = { "token": f"{generated_uuid}","model": "demucs","status" : "Processing" }
          resp = Response(json.dumps(objResponse),200,headers={ "Content-Type" : "application/json" })
          return resp
        else:
          return 400, "File not valid"
      else:
        return 400, "File not valid"
        #TODO: Check request content-type as binary
    
    #TODO: Add parameter for model
    @http('GET','/get_file/<string:value>') #uuid
    def get_method(self,request,value):
      match = glob.glob(f"/data/*{value}/result-demucs-separated.zip")
      if (len(match) > 0):
        filepathw = Path(match[0])
        f = open(str(filepathw),"rb")
        resp = Response(f.read(),200,headers={ "Content-Type" : "application/octet-stream" })
        return resp
      else:
        return 404, "File not found"


    @rpc
    def metodo_llamar(self, audiofile):
      #This calls remotely demucs
      self.y.call_demucs.call_async(audiofile.read(), audiofile.filename )
