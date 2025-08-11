from django.shortcuts import render
import hashlib
import hmac
import datetime
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def test_initiate_upload(request):
    print("Se ejecutó la vista test_initiate_upload")
    access_key = 'b7f28ac7f3f140a4905511025de5c23d'
    secret_key = 'e5b5aec85bfb4465a140b410f5afc7b5'
    bucket = 'aap-bucket22'
    object_key = 'test.txt'  # el nombre del archivo, puede ser cualquiera
    region = 'us-east-1'
    service = 's3'
    host = 'localhost'
    endpoint = f'https://{host}:443/{bucket}/{object_key}?uploads'

    # === Fecha y hora ===
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')

    # === Canonical Request ===
    method = 'POST'
    canonical_uri = f'/{bucket}/{object_key}'
    canonical_querystring = 'uploads'
    signed_headers = 'host;x-amz-content-sha256;x-amz-date'
    payload_hash = hashlib.sha256(b'').hexdigest()

    canonical_headers = (
        f'host:{host}\n'
        f'x-amz-content-sha256:{payload_hash}\n'
        f'x-amz-date:{amz_date}\n'
    )

    canonical_request = (
        f'{method}\n'
        f'{canonical_uri}\n'
        f'{canonical_querystring}\n'
        f'{canonical_headers}\n'
        f'{signed_headers}\n'
        f'{payload_hash}'
    )
    print("=== Canonical Request ===")
    print(canonical_request)
    print("-------------------------")

    # === String to sign ===
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{date_stamp}/{region}/{service}/aws4_request'
    string_to_sign = (
        f'{algorithm}\n'
        f'{amz_date}\n'
        f'{credential_scope}\n'
        f'{hashlib.sha256(canonical_request.encode()).hexdigest()}'
    )
    print("=== String to Sign ===")
    print(string_to_sign)
    print("----------------------")

    # === Firmar ===
    def sign(key, msg): return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    k_date = sign(('AWS4' + secret_key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')
    signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    # === Headers ===
    authorization_header = (
        f'{algorithm} Credential={access_key}/{credential_scope}, '
        f'SignedHeaders={signed_headers}, Signature={signature}'
    )
    print("=== Authorization Header ===")
    print(authorization_header)
    print("----------------------------")

    headers = {
        'x-amz-date': amz_date,
        'x-amz-content-sha256': payload_hash,
        'Authorization': authorization_header,
        # ⚠️ NO incluir 'Host' manualmente aquí
    }

    print("=== Endpoint ===")
    print(endpoint)
    print("=== Headers ===")
    print(headers)
    print("----------------------------")
    # === Enviar la solicitud ===
    try:
        response = requests.post(endpoint, headers=headers, verify=False)
        return JsonResponse({
            'status': response.status_code,
            'response': response.text
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
