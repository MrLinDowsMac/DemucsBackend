from flask import Flask, request, Blueprint
from flask_restx import Api, Resource, fields
from nameko.standalone.rpc import ClusterRpcProxy
from werkzeug.wrappers import Response,Request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from pathlib import Path
import uuid
import os
from pathlib import Path
import glob
import json
from flask.logging import create_logger
import socket

app = Flask(__name__)
log = create_logger(app)
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, doc='/apidoc/',version='1.0', title='Demucs API', description='An API for separate tracks in an audio file using Demucs')

app.register_blueprint(blueprint)
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'

rabbitmq_host = os.environ.get("RABBITMQ_HOST")
rabbitmq_user = os.environ.get("RABBITMQ_USER")
rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD")

CONFIG = { 'AMQP_URI': f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}",
    'serializer': 'pickle'
  }

upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)

requestResult = api.model('RequestResult', {
    'uuid' : fields.FormattedString(uuid.uuid4(),description='An uuid or token that is required to retrieve file after processing'
    ,example=str(uuid.uuid4())),
    'model' : fields.String(description='Selected model: demucs, tasnet, etc',example='Demucs'),
    'status' : fields.String(description='A status of the current request',example="Queued")
})

errorResponse = api.model('ErrorResponse',{ 'message' : fields.String(description='Message describing error') } )

@api.route('/upload', methods=['POST'])
@api.expect(upload_parser)
class Upload(Resource):
  '''Upload a file and receive a token or uuid for further file retrieving after processing'''
  @api.doc('upload')
  @api.response(200, 'Success', requestResult)
  @api.response(400, 'Validation Error', errorResponse)
  @api.response(500, 'Internal Server Error', errorResponse)
  def post(self):
          '''Upload a file and receive a token or uuid for further file retrieving after processing'''
          # if request.content_type.startswith("multipart/form-data"):
          args = upload_parser.parse_args()
          audiofile = args['file'] #busca key 
          original_name = secure_filename(audiofile.filename)
          if audiofile.mimetype == "audio/mpeg" or audiofile.mimetype == "audio/wave":
            #Rename file before calling rpc method
            generated_uuid = str(uuid.uuid4())
            audiofile.filename = f"{Path(original_name).stem.replace(' ','_')}_{generated_uuid}{Path(original_name).suffix}"  
            log.info('filename %s will be sent to queue', audiofile.filename)
            try: 
              with ClusterRpcProxy(CONFIG) as rpc:
                objResponse = { "uuid": f"{generated_uuid}","model": "Demucs","status" : "Queued" }
                result = rpc.remote_call_demucs_service.call_demucs.call_async(audiofile.read(), audiofile.filename)
                resp = Response(json.dumps(objResponse),200,headers={ "Content-Type" : "application/json" })
                return resp
            except (ConnectionRefusedError):
              api.abort(code=500, message="An internal server error ocurred. Unable to reach Demucs service")  
            except (OSError, socket.gaierror):
              api.abort(code=500, message="An internal server error ocurred. Demucs service unavailable")  
          else:
            api.abort(code=415, message="File not valid.")
        # else:
        #   return Response(json.dumps({"message": "File not valid"}),400,headers={ "Content-Type" : "application/json" })
        #     #TODO: Check request content-type as binary
        
@api.route('/get_file/<uuid:token>', methods=['GET']) #uuid
class GetFile(Resource):
  '''Request file by token/uuid and retrieve if is already processed''' 
  @api.produces(['application/zip','application/json'])
  @api.response(200, 'Success')
  @api.response(404, 'File not found',errorResponse)
  def get(self,token):
    '''Request file by token and retrieve if is already processed''' 
    match = glob.glob(f"/data/*{token}/result-demucs-separated.zip")
    if (len(match) > 0):
        filepathw = Path(match[0])
        f = open(str(filepathw),"rb")
        resp = Response(f.read(),200,headers={ "Content-Type" : "application/zip" })
        return resp
    else:
        api.abort(code=404, message="File not found.")

if __name__ == '__main__':
  app.run()