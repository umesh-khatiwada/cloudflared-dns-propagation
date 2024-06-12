**Domain routing with Cloudflare Tunneling**

run application
```
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8081
```


Before applying manifest file in k8s we need to create the cloudflare authorization Token.
Installation on debian:
sudo apt install cloudflared


Step 1: cloudflared login to get the cert.pem
```
cloudflared tunnel login
```

Step 2 :
```
cloudflared tunnel create example-tunnel
```


Step 3:Creating the secret file using the json.
```
kubectl create secret generic tunnel-credentials --from-file=credentials.json=/home/umesh-khatiwada/.cloudflared/2e86e4f1-562d-4089-88da-87580caa5daf.json
```

/home/umesh-khatiwada/.cloudflared/2e86e4f1-562d-4089-88da-87580caa5daf.json is 

Step 4: Creating the certificate secret.
```
kubectl create secret generic origin-cert --from-file=origin-cert.pem=/home/umesh-khatiwada/.cloudflared/cert.pem
```
/home/umesh-khatiwada/.cloudflared/cert.pem is certificate provide by cloudflare.

Step 5:Associate your Tunnel with a DNS record
``` Go to the Cloudflare dashboard.
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
```
**ROUTE**


**1.URL:** `http://0.0.0.0:8081/v1/domain/remove-dns`

```json
{
  "hostname": "phpmyadmin-tunnel.umeshkhatiwada.com.np"
}
```



**2.URL:** `POST: http://0.0.0.0:8081/v1/domain/setup`
certpem payload need to be base64 encoded
```json
{
    "TunnelIDData": {
      "AccountTag": "7412b2d59622a47fed36e28f145",
      "TunnelSecret": "SeW3FH5vvq7ANWGcMW/PEDAvSwk2oOkGjTyN",
      "TunnelID": "2e86e4f1-562d-4089-88da-87580c"
    },
    "certpem": "XSmtOVGcwTlRVd0xXWmlPR05qTVdKbApNVGt3TURRek9UWTJZamMxTWpSak5XTmhOalZsTVRObU5tRXpaR1F6TVdKaU1EaGxZamxrTVRaa1pHTXpNVGt4ClpHRTJOR00zTm1VM016VmpZMlpsWVRJME1UZzRPVEJtT1dVMVpEZzJaR1UyTWpneE9XSmhNR0kzTVRNNE5tRTEKTmpWbVlXRmhPRFkxTURnelltTXdOR05tWkRnME0yTTRPR0prWVRnNU1HSTFaVGd5TURkak16azNORFJqWWpZeApZemxrWXpjNVpHWWlMQ0poY0dsVWIydGxiaUk2SW1wclNrZDNPWGxCZEdRM1FsWk9NWFo0VEZaUVNuTnZWRkZICmRUWlJUazloU1Y5MU9EWTBiRjhpZlE9PQotLS0tLUVORCBBUkdPIFRVTk5FTCBUT0tFTi0tLS0tCg=="
  }
  ```

**3.URL:** `POST: http://0.0.0.0:8081/v1/domain/add-dns`
```json
{
  "hostname":"phpmyadmin-tunnel.umeshkhatiwada.com.np",
  "service":"http://my-phpmyadmin:80"
}
```

**4.URL:** `http://0.0.0.0:8081/v1/domain/list-dns`

# References

1. [Cloudflare Developers: Many Cloudflare Tunnels, One Tunnel](https://developers.cloudflare.com/cloudflare-one/tutorials/many-cfd-one-tunnel/)
2. [GitHub: Cloudflare Argo Tunnel Examples - Named Tunnel in Kubernetes](https://github.com/cloudflare/argo-tunnel-examples/blob/master/named-tunnel-k8s/cloudflared.yaml)
3. [Troy Cude's Blog: Creating Cloudflare Tunnels on Ubuntu](https://tcude.net/creating-cloudflare-tunnels-on-ubuntu/)

