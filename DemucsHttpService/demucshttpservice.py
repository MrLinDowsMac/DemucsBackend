from flask import Flask, request
from flasgger import Swagger, swag_from
#from nameko.standalone.rpc import ClusterRpcProxy
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

app = Flask(__name__)
Swagger(app)
CONFIG = {'AMQP_URI': "amqp://guest:guest@localhost"}

name = "demucshttpservice"    
y = RpcProxy("remote_call_demucs_service")

@app.route('/send_file', methods=['POST'])
def send_file(request):
    """Upload a WAV or MP3 file to be processed
     ---
    summary: "uploads a sound file"
    consumes:
      - "multipart/form-data"
    produces:
      - "application/json"
    parameters:
      - name: file
        in: "formData"
        description: "file to upload"
        required: false
        type: "file"
    definitions:
      Response:
        type: "object"
        properties:
          token:
            type: "string"
            format: "uuid"
          model:
            type: "string"
            example: "demucs"
          status:
            type: "string"
            example: "Processing"
    responses:
        "200":
          description: "successful operation"
          schema:
            $ref: "#/definitions/Response"
        "400":
          description: "File not valid"
    """ 
    if request.content_type.startswith("multipart/form-data"):
      audiofile = request.files.get("file") #busca key
      original_name = audiofile.filename
      if audiofile.mimetype == "audio/mpeg" or audiofile.mimetype == "audio/wave":
        #Rename file before calling rpc method
        generated_uuid = str(uuid.uuid4())
        audiofile.filename = f"{Path(audiofile.filename).stem.replace(' ','_')}_{generated_uuid}{Path(audiofile.filename).suffix}"  
        print (audiofile.filename)
        metodo_llamar(audiofile)
        objResponse = { "token": f"{generated_uuid}","model": "demucs","status" : "Processing" }
        resp = Response(json.dumps(objResponse),200,headers={ "Content-Type" : "application/json" })
        return resp
      else:
        return 400, "File not valid"
    else:
      return 400, "File not valid"
        #TODO: Check request content-type as binary

#TODO: Add parameter for model
@app.route('/get_file/<uuid:token>', methods=['GET']) #uuid
def get_file(request,token):
  """Request file by token and retrieve if is already processed
     ---
    summary: "Request file by token and retrieve it in a zip file if is already processed"
    produces:
      - "application/zip"
    parameters:
      - name: "token"
        in: "path"
        description: "Token (or uuid) received after successful post in /send_file"
        required: true
        type: "string"
    responses:
        "200":
          description: "successful operation"
        "404":
          description: "File not found"
  """ 
  match = glob.glob(f"/data/*{token}/result-demucs-separated.zip")
  if (len(match) > 0):
      filepathw = Path(match[0])
      f = open(str(filepathw),"rb")
      resp = Response(f.read(),200,headers={ "Content-Type" : "application/zip" })
      return resp
  else:
      return 404, "File not found"

#@rpc
def metodo_llamar(audiofile):
  #This calls remotely demucs
  y.call_demucs.call_async(audiofile.read(), audiofile.filename )

if __name__ == '__main__':
  app.run(debug=True)