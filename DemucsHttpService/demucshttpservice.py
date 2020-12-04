from flask import Flask, request
from flask_restx import Api, Resource, fields
from nameko.standalone.rpc import ClusterRpcProxy
from werkzeug.wrappers import Response,Request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from nameko.rpc import rpc, RpcProxy
from pathlib import Path
import uuid
import os
from pathlib import Path
import glob
import json

app = Flask(__name__)
api = Api(app)

rabbitmq_host = os.environ.get("RABBITMQ_HOST")
rabbitmq_user = os.environ.get("RABBITMQ_USER")
rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD")

CONFIG = { 'AMQP_URI': f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}",
    'serializer': 'pickle'
  }

#name = "demucshttpservice"    
upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)

response_model = api.model('ResponseObj', {
    'uuid' : fields.FormattedString,
    'model' : fields.String,
    'status' : fields.String
})

@app.route('/upload/', methods=['POST'])
@api.expect(upload_parser)
class Upload(Resource):
  @api.response(200, 'Success', response_model)
  @api.response(400, 'Validation Error')
  def post(self):
      with ClusterRpcProxy(CONFIG) as rpc:
        # if request.content_type.startswith("multipart/form-data"):
          args = upload_parser.parse_args()
          audiofile = args['file'] #busca key 
          original_name = secure_filename(audiofile.filename)
          if audiofile.mimetype == "audio/mpeg" or audiofile.mimetype == "audio/wave":
            #Rename file before calling rpc method
            generated_uuid = str(uuid.uuid4())
            audiofile.filename = f"{Path(secure_filename(audiofile.filename)).stem.replace(' ','_')}_{generated_uuid}{Path(secure_filename(audiofile.filename)).suffix}"  
            print (audiofile.filename)
            objResponse = { "uuid": f"{generated_uuid}","model": "demucs","status" : "Processing" }
            result = rpc.remote_call_demucs_service.call_demucs.call_async(audiofile.read(), audiofile.filename)
            resp = Response(json.dumps(objResponse),200,headers={ "Content-Type" : "application/json" })
            return resp
          else:
            return Response(json.dumps({"message": "File not valid"}),400,headers={ "Content-Type" : "application/json" })
        # else:
        #   return Response(json.dumps({"message": "File not valid"}),400,headers={ "Content-Type" : "application/json" })
        #     #TODO: Check request content-type as binary


@app.route('/get_file/<uuid:token>', methods=['GET']) #uuid
class GetFile(Resource):
  @api.response(200, 'Success')
  @api.response(404, 'File not found')
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