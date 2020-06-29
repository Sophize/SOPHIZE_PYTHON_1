"""Flask application SOPHIZE_PYTHON_1."""
# To use the package (after renaming to sophize_datamode_temp) on your system uncomment below:
# import sys
# sys.path.insert(1, '/home/abc/code/Sophize/datamodel-python')
# from sophize_datamodel_temp import *
import json

from flask import Flask, request
from sophize_datamodel import ProofRequest, ProofResponse, remove_nulls

from machines import num_schema, sum_machine
import machines_managed

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello from SOPHIZE_PYTHON_1!'


@app.route('/proof_request', methods=['POST'])
def handle_proof_request():
    """Endpoint to handle machine requests from Sophize."""
    machine_request = ProofRequest.from_dict(json.loads(request.data))
    # print(machine_request.to_dict())
    if machine_request.machine_ptr == machines_managed.NUMBER_MACHINE:
        response = num_schema.get_response(machine_request)
    elif machine_request.machine_ptr == machines_managed.SUM_MACHINE:
        response = sum_machine.get_response(machine_request)
    else:
        return 'unknown machine', 400
    if isinstance(response, ProofResponse):
        return remove_nulls(response.to_dict())
    return response


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5001, debug=True)
