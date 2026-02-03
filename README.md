# .scavengers

**Version:** 0.1.0 (Alpha)
**Status:** Active Development
**License:** AGPL-3.0

---

## Overview
**Scavengers** is a self-hosted, Flask-based web application designed to operate as a digital sanctuary. It rejects the modern web's reliance on client-side bloat, invasive tracking, and cloud dependencies in favor of server-side rendering, minimal JavaScript, and strict data sovereignty.

While the core application operates within a closed WireGuard VPN environment to ensure complete isolation, the system includes a hardened public-facing gateway strictly for user registration. This hybrid model allows for controlled growth while maintaining a "trust-first" security perimeter.

## Philosophy & Design
The project is built on three core pillars:
* **Security First:** Database access is strictly gatekept via Stored Procedures. No direct table access is permitted from the application layer.
* **The "Old Web" Aesthetic:** A return to functional, text-driven design. Content is king; aesthetics are functional.
* **Data Sovereignty:** Zero reliance on external cloud providers. If it cannot be hosted locally, it is not part of the stack.

## Architecture
The application acts as the central node in a containerized home network.
* **Frontend:** HTML5, CSS3 (Strict hierarchy), Minimal Vanilla JS.
* **Backend:** Python 3.11, Flask, Gunicorn.
* **Database:** MariaDB (Strict role-based stored procedure access).
* **Infrastructure:** Docker Compose orchestrated on Arch Linux.
* **Network:** Nginx Reverse Proxy routing local VPN traffic and handling limited public ingress.

## Features

### Core Systems
* **RBAC (Role-Based Access Control):** A strict hierarchy (`admin` > `user` > `social`) enforcing feature visibility and data access at the database level.
* **Dynamic Theming:** User-selectable CSS themes and effects layers.

### The "Dev" Sandbox
* **Container Integration:** A dedicated section for hosting and experimenting with internal applications. These run in isolated containers but are accessible via the Scavengers interface, allowing for rapid prototyping of new tools without destabilizing the main stack.

### Social Suite (Role: Social)
* **Feed:** A content aggregator for internal news, memes, and community updates.
* **Chat:** An IRC-style, persistent chat interface optimized for low bandwidth.
* **Board:** A classic bulletin board system for threaded discussions.
* **Profile:** User settings management, including theme switching and password rotation.

### Media Suite (Role: User)
* **Media:** A personal file sharing system for documents, images, and videos.
* **Requests:** A formalized system for users to request specific content acquisition.
* **Reports:** Internal issue tracking for bug reports and feature requests.

### Administration (Role: Admin)
* **User Management:** Approval, suspension, and banning of users.
* **Announcements:** Global system notifications and landing page management.

## Security Model & Registration Workflow
Access to the internal network is granted via WireGuard. To maintain security while allowing new users to join, the following registration protocol is enforced:

1.  **Public Gateway:** The `/register` endpoint is exposed to the public internet.
2.  **Proof of Work:** Submission is guarded by **Altcha** (PoW) to prevent bot spam and DDoS attempts on the registration form.
3.  **Encrypted Exchange:**
    * Registrants must provide a **GPG Public Key** during the request.
    * Upon Admin approval, the system generates unique WireGuard credentials (Keypair + PSK).
    * These credentials are encrypted using the registrant's GPG key and sent via email.
    * This ensures that even if the transmission is intercepted, the VPN credentials remain secure.

## Installation

### Prerequisites
* Docker & Docker Compose
* Nginx (Host)
* WireGuard (Host)

### Environment Setup
Create a `.env` file in the root directory. You must define the following secrets:
```bash
FLASK_SECRET_KEY=
DB_PASS_ROOT=
DB_PASS_LOGIN_BOT=
DB_PASS_ADMIN_BOT=
DB_PASS_ADMIN=
DB_PASS_SOCIAL=
DB_PASS_USER=
```

### Deployment
`docker compose up --build -d`
* No users are provided upon initialization from scripts in the db/init directory. You will have to manually seed an admin user.
* No themes are currently installed, but they'll be coming along as time goes on.

## License
This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.