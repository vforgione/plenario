import json
import uuid
import time

from dateutil.parser import parse
from flask import request, make_response

from plenario.api.common import crossdomain
from plenario.api.common import unknown_object_json_handler
from plenario.api.validator import sensor_network_validate, IFTTTValidator
from plenario.sensor_network.api.sensor_networks import sanitize_validated_args, get_observation_queries, \
    get_raw_metadata
from plenario.api.response import bad_request

# dictionary mapping the curated drop-down list name to the correct feature and property
curated_map = {"Temperature": "temperature.temperature",
               "Humidity": "relative_humidity.humidity"}


# TODO: format errors how ifttt wants
# TODO: decide on time or datetime
@crossdomain(origin="*")
def get_ifttt_observations():
    input_args = request.json
    args = dict()
    args['network'] = 'plenario_development'
    args['nodes'] = [input_args['triggerFields']['node']]
    args['feature'] = curated_map[input_args['triggerFields']['prop']].split('.')[0]
    args['limit'] = input_args['limit'] if 'limit' in input_args.keys() else 50
    args['filter'] = json.dumps({'prop': curated_map[input_args['triggerFields']['prop']].split('.')[1],
                                 'op': input_args['triggerFields']['op'],
                                 'val': input_args['triggerFields']['val']})
    # pass through the curated input property so we can return it to the user for display purposes
    curated_property = input_args['triggerFields']['prop']

    fields = ('network', 'nodes', 'feature', 'sensors',
              'start_datetime', 'end_datetime', 'limit', 'filter')

    validated_args = sensor_network_validate(IFTTTValidator(only=fields), args)
    if validated_args.errors:
        return bad_request(validated_args.errors)
    validated_args.data.update({
        "features": [validated_args.data["feature"]],
        "feature": None
    })
    validated_args = sanitize_validated_args(validated_args)

    observation_queries = get_observation_queries(validated_args)
    if type(observation_queries) != list:
        return observation_queries

    return run_ifttt_queries(observation_queries, curated_property)


@crossdomain(origin="*")
def get_ifttt_meta(field):
    data = []
    if field == 'node':
        args = {"network": "plenario_development"}
        fields = ('network',)
        validated_args = sensor_network_validate(IFTTTValidator(only=fields), args)
        data = [{"label": node.id,
                 "value": node.id} for node in get_raw_metadata('nodes', validated_args)]
    elif field == 'property':
        data = [{"label": curated_property,
                 "value": curated_property} for curated_property in curated_map.keys()]

    return make_ifttt_response(data)


def format_ifttt_observations(obs, curated_property):
    obs_response = {
        "node": obs.node_id,
        "datetime": obs.datetime.isoformat().split('+')[0],
        "property": curated_property,
        "value": getattr(obs, curated_map[curated_property].split('.')[1]),
        "meta": {
            "id": uuid.uuid1().hex,
            "timestamp": int(time.time())
        }
    }

    return obs_response


def run_ifttt_queries(queries, curated_property):
    data = list()
    for query, table in queries:
        data += [format_ifttt_observations(obs, curated_property) for obs in query.all()]

    data.sort(key=lambda x: parse(x["datetime"]), reverse=True)

    return make_ifttt_response(data)


def make_ifttt_response(data):
    resp = {
        "data": data
    }
    resp = make_response(json.dumps(resp, default=unknown_object_json_handler), 200)
    resp.headers['Content-Type'] = 'application/json'
    return resp
