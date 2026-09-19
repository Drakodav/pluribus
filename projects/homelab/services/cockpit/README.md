# Cockpit Host Administration Service

Cockpit runs as a native systemd service on the Macerator host, providing a web-based management interface for storage, networking, containers, and logs.

## Setup & Configuration

- Cockpit is installed on the host via `apt install cockpit`.
- `startup.sh` configures systemd socket overrides to disable backend TLS (`cockpit-tls --no-tls`), as SSL is terminated by Traefik on the Aperio gateway.
- Reverse proxy headers and origins are allowed via `/etc/cockpit/cockpit.conf`.
- Protected by Authentik forwardAuth via `auth-cockpit@docker` middleware.
- Accessible at: `https://manage.<ROOT_DOMAIN>`
