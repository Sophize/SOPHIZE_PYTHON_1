# To use the datamodel package (which you rename to sophize_datamode_temp) on your system uncomment below:
# import sys
# sys.path.insert(1, '/home/abc/code/Sophize/datamodel-python')
# from sophize_datamodel_temp import *

import json
import re

from flask import Flask, jsonify, request
from sophize_datamodel import (Language, MachineRequest, MachineResponse, Term,
                               TruthValue, remove_nulls, resource_from_dict)

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.route('/machine_request', methods=['POST'])
def machine_request():
    """Return a friendly HTTP greeting."""
    machine_request = MachineRequest.from_dict(json.loads(request.data))
    print(machine_request.to_dict())
    if(machine_request.machine_ptr == "#sophize/M.l9L"):
        response = get_number_schema_response(machine_request)
        if isinstance(response, MachineResponse):
            return remove_nulls(response.to_dict())
        return response

    return 'unknown machine', 400


DONT_KNOW_RESPONSE = MachineResponse.from_dict(
    {'truthValue': TruthValue.UNKNOWN})
TRUE_STUB_RESPONSE = MachineResponse.from_dict({'truthValue': TruthValue.TRUE})
FALSE_STUB_RESPONSE = MachineResponse.from_dict(
    {'truthValue': TruthValue.FALSE})
NUMBER_SCHEMA = re.compile(r'^\s*(\d+)\s*=\s*(\d+)\s*\+\s*1\s*$')


def _string_to_int(s: str):
    try:
        return int(s)
    except ValueError:
        return None


def get_number_schema_response(request: MachineRequest):
    proposition = request.proposition
    if proposition is None or proposition.statement is None:
        return 'Must provide statement to check', 400

    if request.try_completing_proposition:
        return 'This machine does not support completion', 400
    if (proposition.language is not Language.INFORMAL):
        return DONT_KNOW_RESPONSE
    statement = proposition.statement

    matcher = NUMBER_SCHEMA.match(statement)
    if matcher is None or len(matcher.groups()) != 2:
        return DONT_KNOW_RESPONSE
    definingNumber = _string_to_int(matcher.group(1))
    previousNumber = _string_to_int(matcher.group(2))
    if definingNumber is None or previousNumber is None:
        return DONT_KNOW_RESPONSE
    if (definingNumber == previousNumber + 1):
        return TRUE_STUB_RESPONSE
    else:
        return FALSE_STUB_RESPONSE


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5001, debug=True)
