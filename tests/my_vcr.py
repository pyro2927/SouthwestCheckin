from vcr import VCR
import json
import os

# remove sensitive values from JSON response
bad_fields = [
    'checkInSessionToken',
    'first-name',
    'firstName',
    'last-name',
    'lastName',
    'name',
    'passengerInfo',
    'passengers',
    'recordLocator'
]


def redact(obj):
    if isinstance(obj, ("".__class__, u"".__class__)):
        return
    for k, v in list(obj.items()):
        if k in bad_fields:
            obj[k] = '[REDACTED]'
        elif isinstance(v, list) and not isinstance(v, str):
            for o in v:
                redact(o)
        elif isinstance(v, dict):
            redact(v)


def filter_payload(response):
    s = response['body']['string']
    if len(s) == 0:
        return response
    string_body = s.decode('utf8')
    try:
        body = json.loads(string_body)
        redact(body)
        response['body']['string'] = json.dumps(body).encode()
    finally:
        return response


def custom_vcr():
    dirname = os.path.dirname(__file__)
    return VCR(
        decode_compressed_response=True,
        cassette_library_dir=os.path.join(dirname, 'fixtures/cassettes'),
        path_transformer=VCR.ensure_suffix('.yml'),
        filter_query_parameters=bad_fields,
        before_record_response=filter_payload,
        filter_post_data_parameters=bad_fields,
        match_on=['path', 'method']
    )
