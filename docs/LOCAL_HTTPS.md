````markdown
Local HTTPS for mobile testing (iOS) — trusted local certificate with mkcert

Goal

Serve the frontend from Docker with HTTPS so an iPhone on the same local network can connect and use browser geolocation.

Approach

1. Create a local TLS certificate trusted by your mac (and your iPhone) using mkcert.
2. Place the cert and key in `./docker/certs` as `cert.pem` and `key.pem`.
3. Start docker-compose. Nginx in the frontend container will use the mounted certs and listen on 443.

Requirements

- macOS host
- Homebrew (recommended)
- mkcert (to generate locally-trusted certs)
- Your iPhone and mac must be on the same local network.

Install mkcert (if you don't have it)

```bash
brew install mkcert nss
mkcert -install
```

Generate certs for your machine IP and localhost

Replace `192.168.1.100` with your Mac's LAN IP (obtain with `ipconfig getifaddr en0` or `ipconfig getifaddr en1`). Include any hostnames you plan to use (e.g., `my-mac.local`).

```bash
mkdir -p docker/certs
mkcert -cert-file docker/certs/cert.pem -key-file docker/certs/key.pem 192.168.1.100 localhost
```

Trusting the mkcert root on iPhone

mkcert installs the local CA into your macOS trust store. To trust the same CA on an iPhone:

1. Export the mkcert root CA file: `mkcert -CAROOT` will show a folder (usually `~/.local/share/mkcert` or `/Users/<you>/Library/Application Support/mkcert`). The root CA file is named `rootCA.pem`.
2. Serve it locally or transfer to the iPhone (AirDrop or host a small web server). Example:

```bash
cp "$(mkcert -CAROOT)/rootCA.pem" ./docker/certs/rootCA.pem
# serve it temporarily so you can open the URL from iPhone
python3 -m http.server 8001 --directory ./docker/certs
# then on iPhone open http://<your-mac-ip>:8001/rootCA.pem and install the profile
```

3. On the iPhone: go to Settings → Profile Downloaded (or General → VPN & Device Management), install the profile, then go to Settings → About → Certificate Trust Settings and enable full trust for the installed certificate.

Start Docker

```bash
# from repo root
docker compose up --build
```

Access from iPhone

Open https://<your-mac-ip> (default port 443) in Safari on the iPhone.

Notes & troubleshooting

- Safari on iOS requires TLS to grant geolocation. If the certificate is untrusted, geolocation will be blocked.
- If you prefer not to install the CA on the iPhone, consider using a public tunneling service (ngrok/Cloudflare tunnel) which provides a trusted certificate.
- If port 443 on host is already used by another service, pick another host port (e.g. `8443:443`) and access https://<your-mac-ip>:8443.
- Keep the certificates out of source control (add `docker/certs` to `.gitignore` if not already ignored).

Using Certbot / Let's Encrypt
--------------------------------

If you have a public DNS name that points to your machine (or a VM) and can expose ports 80/443 from the internet to that machine, you can obtain a trusted certificate from Let's Encrypt via Certbot. There are two common approaches:

1) Webroot / HTTP challenge (requires port 80 reachable from the internet)
	 - Install certbot on the host or use a certbot container.
	 - Use the webroot plugin to place the challenge file under your site webroot. Example (on host):

```bash
# Replace example.com with your domain
sudo certbot certonly --webroot -w /var/www/html -d example.com
```

	 - After obtaining certs, copy or symlink the files into `docker/certs` as `cert.pem` and `key.pem`, or mount the Let's Encrypt live folder into the container (see notes below).

2) DNS challenge (recommended if you cannot open port 80/443 publicly)
	 - Use Certbot with your DNS provider plugin to complete a DNS-01 challenge. This does not require an externally reachable webserver but does require API access to your DNS provider.
	 - Example (provider-specific):

```bash
# with the appropriate DNS plugin; this creates certificates without exposing port 80
sudo certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d example.com
```

Mounting Let's Encrypt certs into the frontend container
-------------------------------------------------------

Option A (copy the files):
	- Copy `fullchain.pem` -> `docker/certs/cert.pem` and `privkey.pem` -> `docker/certs/key.pem`.
	- This is the easiest approach and works regardless of how the certs were obtained.

Option B (mount the live folder directly):
	- On many systems Certbot places certificates under `/etc/letsencrypt/live/<domain>/`.
	- You can mount that folder into the container by editing `docker-compose.yml` and adding a volume mapping:

```yaml
	frontend:
		volumes:
			- /etc/letsencrypt/live/example.com:/etc/nginx/certs:ro
```

	- In this case Nginx will read `/etc/nginx/certs/fullchain.pem` and `/etc/nginx/certs/privkey.pem`.

Notes and constraints
---------------------
- Let's Encrypt requires proof of domain ownership. For a local LAN IP this is not feasible unless you control a public DNS that points to your public IP and you forward ports from your router to your Mac.
- If you use Option B and mount `/etc/letsencrypt` from the host, be careful with permissions and automatic renewal (Certbot may update files in place; Nginx will need to be reloaded after renewal).
- For automatic renewal in a containerized environment, consider running a certbot container or a small host cron job that runs `certbot renew` and then signals the nginx container to reload (e.g., `docker kill -s HUP <nginx-container>`).

Example: obtain certs on the host then copy + restart Docker
-----------------------------------------------------------

```bash
# Obtain certificate on host (webroot or dns)
sudo certbot certonly --webroot -w /var/www/html -d example.com

# Copy or symlink the certs into the docker folder used by compose
sudo cp /etc/letsencrypt/live/example.com/fullchain.pem docker/certs/cert.pem
sudo cp /etc/letsencrypt/live/example.com/privkey.pem docker/certs/key.pem

# Start the containers
docker compose up --build
```

If you want, I can also:
- Add a certbot service to `docker-compose.yml` that obtains certs (requires additional setup and a public domain).  
- Implement an entrypoint/template for Nginx to dynamically select Let's Encrypt certs when present (useful for automated setups).

Tell me if you have a public domain available and whether you prefer the Certbot-in-container approach or obtaining certs on the host and copying them into `docker/certs` — I can update `docker-compose.yml` with a certbot service template and automation steps.
````
Local HTTPS for mobile testing (iOS) — trusted local certificate with mkcert

Goal

Serve the frontend from Docker with HTTPS so an iPhone on the same local network can connect and use browser geolocation.

Approach

1. Create a local TLS certificate trusted by your mac (and your iPhone) using mkcert.
2. Place the cert and key in `./docker/certs` as `cert.pem` and `key.pem`.
3. Start docker-compose. Nginx in the frontend container will use the mounted certs and listen on 443.

Requirements

- macOS host
- Homebrew (recommended)
- mkcert (to generate locally-trusted certs)
- Your iPhone and mac must be on the same local network.

Install mkcert (if you don't have it)

```bash
brew install mkcert nss
mkcert -install
```

Generate certs for your machine IP and localhost

Replace `192.168.1.100` with your Mac's LAN IP (obtain with `ipconfig getifaddr en0` or `ipconfig getifaddr en1`). Include any hostnames you plan to use (e.g., `my-mac.local`).

```bash
mkdir -p docker/certs
mkcert -cert-file docker/certs/cert.pem -key-file docker/certs/key.pem 192.168.1.100 localhost
```

Trusting the mkcert root on iPhone

mkcert installs the local CA into your macOS trust store. To trust the same CA on an iPhone:

1. Export the mkcert root CA file: `mkcert -CAROOT` will show a folder (usually `~/.local/share/mkcert` or `/Users/<you>/Library/Application Support/mkcert`). The root CA file is named `rootCA.pem`.
2. Serve it locally or transfer to the iPhone (AirDrop or host a small web server). Example:

```bash
cp "$(mkcert -CAROOT)/rootCA.pem" ./docker/certs/rootCA.pem
# serve it temporarily so you can open the URL from iPhone
python3 -m http.server 8001 --directory ./docker/certs
# then on iPhone open http://<your-mac-ip>:8001/rootCA.pem and install the profile
```

3. On the iPhone: go to Settings → Profile Downloaded (or General → VPN & Device Management), install the profile, then go to Settings → About → Certificate Trust Settings and enable full trust for the installed certificate.

Start Docker

```bash
# from repo root
docker compose up --build
```

Access from iPhone

Open https://<your-mac-ip> (default port 443) in Safari on the iPhone.

Notes & troubleshooting

- Safari on iOS requires TLS to grant geolocation. If the certificate is untrusted, geolocation will be blocked.
- If you prefer not to install the CA on the iPhone, consider using a public tunneling service (ngrok/Cloudflare tunnel) which provides a trusted certificate.
- If port 443 on host is already used by another service, pick another host port (e.g. `8443:443`) and access https://<your-mac-ip>:8443.
- Keep the certificates out of source control (add `docker/certs` to `.gitignore` if not already ignored).