import json
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from kubernetes import client, config
import base64


router = APIRouter()
config.load_kube_config()

@router.post("/setup", response_description="setup domain values")
async def setup_domain(request: Request):
    try:
        post_data = await request.json() 
        tunnel_id_data = post_data.get("TunnelIDData")
        certpem=post_data.get("certpem")
        if not tunnel_id_data:
            raise HTTPException(status_code=400, detail="TunnelIDData is missing in the payload")
        
        # Convert the TunnelIDData to a string and then base64 encode it
        credentials_str = json.dumps(tunnel_id_data)
        encoded_credentials = base64.b64encode(credentials_str.encode('utf-8')).decode('utf-8')
        secret_metadata = client.V1ObjectMeta(name="tunnel-credentials")
        secret_data = {"credentials.json": encoded_credentials}
        secret = client.V1Secret(metadata=secret_metadata, data=secret_data, type="Opaque")

        # Create the secret in the default namespace
        v1 = client.CoreV1Api()
        v1.create_namespaced_secret(namespace="default", body=secret)

        # create a secret of certificates
        secret_metadata_cert = client.V1ObjectMeta(name="origin-cert")
        secret_data = {"origin-cert.pem": certpem}
        secret = client.V1Secret(metadata=secret_metadata_cert, data=secret_data, type="Opaque")

        # Create the secret in the default namespace
        v1.create_namespaced_secret(namespace="default", body=secret)

        return {"message": "Secret created successfully"}



    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/install", response_description="setup domain values")
async def install_domain(request: Request):
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
  
    return

