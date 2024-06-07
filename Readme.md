fastapi dev main.py
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8081

Domain routing with Cloudflare Tunneling

Before applying manifest file in k8s we need to create the cloudflare authorization Token.
Installation on debian:
sudo apt install cloudflared


Step 1: cloudflared login to get the cert.pem
cloudflared tunnel login


Step 2 :
cloudflared tunnel create example-tunnel



Step 3:Creating the secret file using the json.
kubectl create secret generic tunnel-credentials --from-file=credentials.json=/home/umesh-khatiwada/.cloudflared/2e86e4f1-562d-4089-88da-87580caa5daf.json


/home/umesh-khatiwada/.cloudflared/2e86e4f1-562d-4089-88da-87580caa5daf.json is 

Step 4: Creating the certificate secret.
kubectl create secret generic origin-cert --from-file=origin-cert.pem=/home/umesh-khatiwada/.cloudflared/cert.pem

/home/umesh-khatiwada/.cloudflared/cert.pem is certificate provide by cloudflare.

Step 5:Associate your Tunnel with a DNS record
Go to the Cloudflare dashboard.
Go to the DNS tab.
Now create a CNAME targeting .cfargotunnel.com. In this example, the tunnel ID is ef824aef-7557-4b41-a398-4684585177ad, so create a CNAME record specifically targeting ef824aef-7557-4b41-a398-4684585177ad.cfargotunnel.com.

You can also create multiple CNAME records targeting the same Tunnel, if desired.
Alternatively 
 	curl -X POST "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records" \
 	-H "Authorization: Bearer{API_TOKEN}" \
 	-H "Content-Type: application/json" \
 	--data '{
   	"type": "CNAME",
   	"name": "tunnel3",
   	"content": "2e86e4f1-562d-4089-88da-87580caa5daf.cfargotunnel.com",
   	"ttl": 1,
   	"proxied": true
 	}'







Step 6: Apply cloudflare Yaml  in Kubernetes

---
apiVersion: apps/v1
kind: Deployment
metadata:
 name: cloudflared
spec:
 selector:
   matchLabels:
     app: cloudflared
 replicas: 1
 template:
   metadata:
     labels:
       app: cloudflared
   spec:
     containers:
     - name: cloudflared
       image: cloudflare/cloudflared:latest
       args:
       - tunnel
       - --config
       - /etc/cloudflared/config/config.yaml
       - run
       volumeMounts:
       - name: config
         mountPath: /etc/cloudflared/config
         readOnly: true
       - name: creds
         mountPath: /etc/cloudflared/creds
         readOnly: true
       - name: cert
         mountPath: /etc/cloudflared/cert
         readOnly: true
       resources:
         requests:
           memory: "64Mi"
           cpu: "250m"
         limits:
           memory: "128Mi"
           cpu: "500m"
     volumes:
     - name: creds
       secret:
         secretName: tunnel-credentials
     - name: config
       configMap:
         name: cloudflared
         items:
         - key: config.yaml
           path: config.yaml
     - name: cert
       secret:
         secretName: origin-cert
---
apiVersion: v1
kind: ConfigMap
metadata:
 name: cloudflared
data:
 config.yaml: |
   tunnel: umeshdomain_np
   credentials-file: /etc/cloudflared/creds/credentials.json
   origincert: /etc/cloudflared/cert/origin-cert.pem
   metrics: 0.0.0.0:2000
   no-autoupdate: true
   ingress:
   - hostname: tunnel2.umeshkhatiwada.com.np
     service: http://my-phpmyadmin:80
   - hostname: tunnel3.umeshkhatiwada.com.np
     service: http://my-phpmyadmin:80
   - hostname: tunnel4.umeshkhatiwada.com.np
     service: http://my-phpmyadmin:80
   - service: http_status:404






kubectl apply -f cloudflared.yaml


RESULT



Reference:
https://developers.cloudflare.com/cloudflare-one/tutorials/many-cfd-one-tunnel/
https://github.com/cloudflare/argo-tunnel-examples/blob/master/named-tunnel-k8s/cloudflared.yaml
https://tcude.net/creating-cloudflare-tunnels-on-ubuntu/
