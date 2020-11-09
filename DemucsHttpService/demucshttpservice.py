from nameko.web.handlers import http
from werkzeug.wrappers import Response,Request
from werkzeug.datastructures import FileStorage
from nameko.events import EventDispatcher, SERVICE_POOL, SINGLETON
from nameko.rpc import rpc, RpcProxy

class DemucsHttpService:
    name = "demucshttpservice"    

    y = RpcProxy("remote_call_demucs_service")

    @http('POST', '/send_file')
    def do_post(self, request): 
      if request.content_type.startswith("multipart/form-data"):
        audiofile = request.files.get("archivo") #busca key
        print (audiofile.filename)
        if audiofile.mimetype == "audio/mpeg" or audiofile.mimetype == "audio/wave":
          #TODO: Perform additional validations?
          self.metodo_llamar(audiofile)
          return 200, "Recibido"
        else:
          return 400, "Archivo no valido"
      else:
        return 400, "Archivo no valido"
        #TODO: Check request content-type as binary
    
    @rpc
    def metodo_llamar(self, audiofile):
      #This calls remotely demucs
      self.y.call_demucs.call_async(audiofile.read(), audiofile.filename )
