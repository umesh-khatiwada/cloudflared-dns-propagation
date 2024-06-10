import datetime
import json
from fastapi import APIRouter, Request, HTTPException
from kubernetes import client, config
import base64
import yaml

router = APIRouter()

def load_kube_config():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

@router.post("/setup", response_description="Setup domain values")
async def setup_domain(request: Request):
    load_kube_config()
    try:
        post_data = await request.json()
        tunnel_id_data = post_data.get("TunnelIDData")
        certpem = post_data.get("certpem")
        if not tunnel_id_data:
            raise HTTPException(status_code=400, detail="TunnelIDData is missing in the payload")

        credentials_str = json.dumps(tunnel_id_data)
        encoded_credentials = base64.b64encode(credentials_str.encode('utf-8')).decode('utf-8')
        v1 = client.CoreV1Api()
        secret_metadata = client.V1ObjectMeta(name="tunnel-credentials")
        secret_data = {"credentials.json": encoded_credentials}
        secret = client.V1Secret(metadata=secret_metadata, data=secret_data, type="Opaque")

        try:
            v1.read_namespaced_secret(name="tunnel-credentials", namespace="default")
            v1.replace_namespaced_secret(name="tunnel-credentials", namespace="default", body=secret)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                v1.create_namespaced_secret(namespace="default", body=secret)
            else:
                raise e

        secret_metadata_cert = client.V1ObjectMeta(name="origin-cert")
        secret_data_cert = {"origin-cert.pem": certpem}
        secret_cert = client.V1Secret(metadata=secret_metadata_cert, data=secret_data_cert, type="Opaque")

        try:
            v1.read_namespaced_secret(name="origin-cert", namespace="default")
            v1.replace_namespaced_secret(name="origin-cert", namespace="default", body=secret_cert)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                v1.create_namespaced_secret(namespace="default", body=secret_cert)
            else:
                raise e

        return {"message": "Secret created or updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/add-dns", response_description="Setup domain values")
async def install_domain(request: Request):
    load_kube_config()
    try:
        post_data = await request.json()
        host_name = post_data.get("hostname")
        service = post_data.get("service")
        namespace = "default"
        deployment_name = "cloudflared"
        
        if not host_name or not service:
            raise HTTPException(status_code=400, detail="hostname and service are required fields")

        v1 = client.CoreV1Api()
        api_instance = client.AppsV1Api()

        namespace = "default"
        target_config_map_name = None

        # List all ConfigMaps in the namespace
        config_maps = v1.list_namespaced_config_map(namespace)

        # Find the ConfigMap with a name containing 'cloudflared'
        for cm in config_maps.items:
            if "cloudflared" in cm.metadata.name:
                target_config_map_name = cm.metadata.name
                break

        if not target_config_map_name:
            return {"message": "ConfigMap with name containing 'cloudflared' not found"}

        # Fetch the target ConfigMap
        config_map = v1.read_namespaced_config_map(target_config_map_name, namespace)

        # Parse the config.yaml data
        config_data = yaml.safe_load(config_map.data['config.yaml'])

        # Check if the hostname already exists
        if 'ingress' in config_data:
            for ingress in config_data['ingress'][:-1]:
                if ingress['hostname'] == host_name:
                    # Update the service for the existing hostname
                    ingress['service'] = service
                    break
            else:
                # Append the new ingress entry
                new_ingress = {'hostname': host_name, 'service': service}
                config_data['ingress'].insert(0, new_ingress) 
        else:
            # Create new ingress entry
            config_data['ingress'] = [{'hostname': host_name, 'service': service}]

        # Update the ConfigMap data
        config_map.data['config.yaml'] = yaml.safe_dump(config_data)

        # Apply the updated ConfigMap
        v1.patch_namespaced_config_map(target_config_map_name, namespace, config_map)
                # Fetch the deployment

        deployment = api_instance.read_namespaced_deployment(deployment_name, namespace)

        # Increment deployment spec's revision to trigger rolling update
        deployment.spec.template.metadata.annotations = {
            "kubectl.kubernetes.io/restartedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Patch the deployment to trigger rolling update
        api_instance.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=deployment
        )

        print(f"Updated ConfigMap '{target_config_map_name}' with new ingress values")
        return {"message": f"ConfigMap '{target_config_map_name}' updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   

@router.delete("/remove-dns", response_description="Remove domain values")
async def remove_domain(request: Request):
    try:
        post_data = await request.json()
        host_name = post_data.get("hostname")
        namespace = "default"
        deployment_name = "cloudflared"
        
        if not host_name:
            raise HTTPException(status_code=400, detail="hostname is a required field")

        v1 = client.CoreV1Api()
        api_instance = client.AppsV1Api()

        namespace = "default"
        target_config_map_name = None

        # List all ConfigMaps in the namespace
        config_maps = v1.list_namespaced_config_map(namespace)

        # Find the ConfigMap with a name containing 'cloudflared'
        for cm in config_maps.items:
            if "cloudflared" in cm.metadata.name:
                target_config_map_name = cm.metadata.name
                break

        if not target_config_map_name:
            return {"message": "ConfigMap with name containing 'cloudflared' not found"}

        # Fetch the target ConfigMap
        config_map = v1.read_namespaced_config_map(target_config_map_name, namespace)

        # Parse the config.yaml data
        config_data = yaml.safe_load(config_map.data['config.yaml'])

        # Check if the hostname exists and remove it if found
        if 'ingress' in config_data:
            found = False
            for ingress in config_data['ingress'][:-1]:  # Use slice to make a copy of the list
                if ingress['hostname'] == host_name:
                    config_data['ingress'].remove(ingress)
                    found = True
                    break
            
            if not found:
                raise HTTPException(status_code=404, detail=f"Hostname '{host_name}' not found in DNS entries")

        # Update the ConfigMap data
        config_map.data['config.yaml'] = yaml.safe_dump(config_data)

        # Apply the updated ConfigMap
        v1.patch_namespaced_config_map(target_config_map_name, namespace, config_map)

        deployment = api_instance.read_namespaced_deployment(deployment_name, namespace)

        # Increment deployment spec's revision to trigger rolling update
        annotations = deployment.spec.template.metadata.annotations or {}
        annotations["kubectl.kubernetes.io/restartedAt"] = str(datetime.datetime.utcnow())
        deployment.spec.template.metadata.annotations = annotations

        # Patch the deployment to trigger rolling update
        api_instance.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=deployment
        )

        return {"message": f"DNS entry '{host_name}' removed successfully"}

    except client.rest.ApiException as e:
        if e.status == 404:
            raise HTTPException(status_code=404, detail="ConfigMap not found")
        else:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

