from vcr import VCR
import json
import os

# remove sensitive values from JSON response
bad_fields = [
    'recordLocator',
    'checkInSessionToken',
    'name',
    'firstName',
    'lastName',
    'passengers',
    'first-name',
    'last-name'
]


def redact(obj):
    for k, v in list(obj.items()):
        if k in bad_fields:
            obj[k] = '[REDACTED]'
        elif isinstance(v, list) and not isinstance(v, str):
            for o in v:
                redact(o)
        elif isinstance(v, dict):
            redact(v)


def filter_payload(response):
    string_body = response['body']['string'].decode('utf8')
    body = json.loads(string_body)
    redact(body)
    response['body']['string'] = json.dumps(body).encode()
    return response


def custom_vcr():
    dirname = os.path.dirname(__file__)
    return VCR(
        decode_compressed_response=True,
        cassette_library_dir=os.path.join(dirname, 'fixtures/cassettes'),
        path_transformer=VCR.ensure_suffix('.yml'),
        filter_query_parameters=bad_fields,
        before_record_response=filter_payload,
        filter_post_data_parameters=bad_fields
    )
