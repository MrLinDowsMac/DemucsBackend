from flask import Flask, request
from flasgger import Swagger, swag_from
from nameko.standalone.rpc import ClusterRpcProxy
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

rabbitmq_host = os.environ.get("RABBITMQ_HOST")
rabbitmq_user = os.environ.get("RABBITMQ_USER")
rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD")

CONFIG = { 'AMQP_URI': f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}",
    'serializer': 'pickle'
  }

#name = "demucshttpservice"    

@app.route('/upload', methods=['POST'])
def upload():
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
      ProcessUUID:
        type: "object"
        properties:
          uuid:
            type: "string"
            format: "uuid"
          model:
            type: "string"
            example: "demucs"
          status:
            type: "string"
            example: "Processing"
      ErrorResponse:
        type: "object"
        properties:
          message:
            type: "string"
            format: "string"
    responses:
        "200":
          description: "Successful request"
          schema:
            $ref: "#/definitions/ProcessUUID"
        "400":
          description: "File not valid"
          schema:
            $ref: "#/definitions/ErrorResponse"
    """ 
    with ClusterRpcProxy(CONFIG) as rpc:
      if request.content_type.startswith("multipart/form-data"):
        audiofile = request.files.get("file") #busca key
        original_name = audiofile.filename
        if audiofile.mimetype == "audio/mpeg" or audiofile.mimetype == "audio/wave":
          #Rename file before calling rpc method
          generated_uuid = str(uuid.uuid4())
          #TODO: Try to use secure_filename()?
          audiofile.filename = f"{Path(audiofile.filename).stem.replace(' ','_')}_{generated_uuid}{Path(audiofile.filename).suffix}"  
          print (audiofile.filename)
          objResponse = { "uuid": f"{generated_uuid}","model": "demucs","status" : "Processing" }
          result = rpc.remote_call_demucs_service.call_demucs.call_async(audiofile.read(), audiofile.filename)
          resp = Response(json.dumps(objResponse),200,headers={ "Content-Type" : "application/json" })
          return resp
        else:
          return Response(json.dumps({"message": "File not valid"}),400,headers={ "Content-Type" : "application/json" })
      else:
        return Response(json.dumps({"message": "File not valid"}),400,headers={ "Content-Type" : "application/json" })
          #TODO: Check request content-type as binary

#TODO: Add parameter for model
@app.route('/get_file/<uuid:token>', methods=['GET']) #uuid
def get_file(token):
  """Request file by token and retrieve if is already processed
     ---
    summary: "Request file by token and retrieve it in a zip file if is already processed"
    produces:
      - "application/zip"
      - "application/json"
    parameters:
      - name: "token"
        in: "path"
        description: "Token (or uuid) received after successful post in /send_file"
        required: true
        type: "string"
    definitions:
      ErrorResponse:
        type: "object"
        properties:
          message:
            type: "string"
            format: "string"
    responses:
        "200":
          description: "successful request"
        "404":
          description: "File not found"
          schema:
            $ref: "#/definitions/ErrorResponse"
  """ 
  match = glob.glob(f"/data/*{token}/result-demucs-separated.zip")
  if (len(match) > 0):
      filepathw = Path(match[0])
      f = open(str(filepathw),"rb")
      resp = Response(f.read(),200,headers={ "Content-Type" : "application/zip" })
      return resp
  else:
      return Response(json.dumps({"message": "File not found"}),404,headers={ "Content-Type" : "application/json" })

if __name__ == '__main__':
  app.run()