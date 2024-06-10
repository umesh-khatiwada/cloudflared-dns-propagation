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



DEL: http://0.0.0.0:8081/v1/domain/remove-dns
{
  "hostname":"phpmyadmin-tunnel.umeshkhatiwada.com.np"
}



POST: http://0.0.0.0:8081/v1/domain/setup
{
    "TunnelIDData": {
      "AccountTag": "7412b2d59622a47fed36e28f1454737e",
      "TunnelSecret": "SeW3FH5vvq7ANWGcMW/PEDAvSwk2oOkGjTyNJ7NgvcQ=",
      "TunnelID": "2e86e4f1-562d-4089-88da-87580caa5daf"
    },
    "certpem": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZytOc2tFVllpYzQ1WW9neHEKK3NpNkdXS2xyZ3gyUVM5NG9obWh6aXdqREEyaFJBTkNBQVRqUlBqaXFIOU0ybTFyTEZ6TEdQc2E3RjBzR1J2YQpFK2JIbWtCQnJTUzRWOWZJSE4zLytWSEVLNGQ2bUtUay9pQnFCU2YveGkxMDRiRmFtTFFBd1RMZwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tCi0tLS0tQkVHSU4gQ0VSVElGSUNBVEUtLS0tLQpNSUlETmpDQ0F0eWdBd0lCQWdJVWRBb0JxS0JpdDUwZStDL25HTk5SYzJhbjlENHdDZ1lJS29aSXpqMEVBd0l3CmdZOHhDekFKQmdOVkJBWVRBbFZUTVJNd0VRWURWUVFJRXdwRFlXeHBabTl5Ym1saE1SWXdGQVlEVlFRSEV3MVQKWVc0Z1JuSmhibU5wYzJOdk1Sa3dGd1lEVlFRS0V4QkRiRzkxWkVac1lYSmxMQ0JKYm1NdU1UZ3dOZ1lEVlFRTApFeTlEYkc5MVpFWnNZWEpsSUU5eWFXZHBiaUJUVTB3Z1JVTkRJRU5sY25ScFptbGpZWFJsSUVGMWRHaHZjbWwwCmVUQWVGdzB5TkRBMk1EVXdOakV4TURCYUZ3MHpPVEEyTURJd05qRXhNREJhTUdJeEdUQVhCZ05WQkFvVEVFTnMKYjNWa1JteGhjbVVzSUVsdVl5NHhIVEFiQmdOVkJBc1RGRU5zYjNWa1JteGhjbVVnVDNKcFoybHVJRU5CTVNZdwpKQVlEVlFRREV4MURiRzkxWkVac1lYSmxJRTl5YVdkcGJpQkRaWEowYVdacFkyRjBaVEJaTUJNR0J5cUdTTTQ5CkFnRUdDQ3FHU000OUF3RUhBMElBQk9ORStPS29mMHphYldzc1hNc1kreHJzWFN3Wkc5b1Q1c2VhUUVHdEpMaFgKMThnYzNmLzVVY1FyaDNxWXBPVCtJR29GSi8vR0xYVGhzVnFZdEFEQk11Q2pnZ0ZBTUlJQlBEQU9CZ05WSFE4QgpBZjhFQkFNQ0JhQXdIUVlEVlIwbEJCWXdGQVlJS3dZQkJRVUhBd0lHQ0NzR0FRVUZCd01CTUF3R0ExVWRFd0VCCi93UUNNQUF3SFFZRFZSME9CQllFRklnb2tydnVVMEFNR0V1aERvc1V0NmdIVXRhNU1COEdBMVVkSXdRWU1CYUEKRklVd1hUc3FjTlR0MVpKbkIvM3JPYlFhRGppbk1FUUdDQ3NHQVFVRkJ3RUJCRGd3TmpBMEJnZ3JCZ0VGQlFjdwpBWVlvYUhSMGNEb3ZMMjlqYzNBdVkyeHZkV1JtYkdGeVpTNWpiMjB2YjNKcFoybHVYMlZqWTE5allUQTVCZ05WCkhSRUVNakF3Z2hjcUxuVnRaWE5vYTJoaGRHbDNZV1JoTG1OdmJTNXVjSUlWZFcxbGMyaHJhR0YwYVhkaFpHRXUKWTI5dExtNXdNRHdHQTFVZEh3UTFNRE13TWFBdm9DMkdLMmgwZEhBNkx5OWpjbXd1WTJ4dmRXUm1iR0Z5WlM1agpiMjB2YjNKcFoybHVYMlZqWTE5allTNWpjbXd3Q2dZSUtvWkl6ajBFQXdJRFNBQXdSUUlnS2g0OVdTeDR0WC9VCmRVbWtLUW84T3RsWGE2TkxhKzRMbmdVYm1nNjNwMnNDSVFDYlg4NW1DRm1GU1Z5bi9VejVZY3BXU3A5Z0dBWEsKeEVOS3NoTjlYTnY1anc9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCi0tLS0tQkVHSU4gQVJHTyBUVU5ORUwgVE9LRU4tLS0tLQpleUo2YjI1bFNVUWlPaUl4T1RRM1pUWmtOVFkwTW1GaVpUSmlPV0ppTjJNNVl6UTNOVGM1TTJJek5TSXNJbUZqClkyOTFiblJKUkNJNklqYzBNVEppTW1RMU9UWXlNbUUwTjJabFpETTJaVEk0WmpFME5UUTNNemRsSWl3aWMyVnkKZG1salpVdGxlU0k2SW5ZeExqQXRNR0kyWVdVd09XUXlNekV5T1RGbU1XSmtOVGcwTlRVd0xXWmlPR05qTVdKbApNVGt3TURRek9UWTJZamMxTWpSak5XTmhOalZsTVRObU5tRXpaR1F6TVdKaU1EaGxZamxrTVRaa1pHTXpNVGt4ClpHRTJOR00zTm1VM016VmpZMlpsWVRJME1UZzRPVEJtT1dVMVpEZzJaR1UyTWpneE9XSmhNR0kzTVRNNE5tRTEKTmpWbVlXRmhPRFkxTURnelltTXdOR05tWkRnME0yTTRPR0prWVRnNU1HSTFaVGd5TURkak16azNORFJqWWpZeApZemxrWXpjNVpHWWlMQ0poY0dsVWIydGxiaUk2SW1wclNrZDNPWGxCZEdRM1FsWk9NWFo0VEZaUVNuTnZWRkZICmRUWlJUazloU1Y5MU9EWTBiRjhpZlE9PQotLS0tLUVORCBBUkdPIFRVTk5FTCBUT0tFTi0tLS0tCg=="
  }

http://0.0.0.0:8081/v1/domain/add-dns
{
  "hostname":"phpmyadmin-tunnel.umeshkhatiwada.com.np",
  "service":"http://my-phpmyadmin:80"
}

Reference:
https://developers.cloudflare.com/cloudflare-one/tutorials/many-cfd-one-tunnel/
https://github.com/cloudflare/argo-tunnel-examples/blob/master/named-tunnel-k8s/cloudflared.yaml
https://tcude.net/creating-cloudflare-tunnels-on-ubuntu/
