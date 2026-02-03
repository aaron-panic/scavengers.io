# Development Roadmap

**Legend:**
- [ ] Todo
- [/] In Progress
- [x] Complete
- [!] Broken/Needs Repair

---

## 1. Admin Suite (Role: Admin)

### User Management
* **Phase 1: Restoration & Stability (Current Priority)**
    - [ ] Repair `admin_users.html` (fix broken HTML/logic from pattern switch).
    - [ ] Ensure "As-Is" functionality works: List, Approve, Ban, Suspend, Reset Password.
* **Phase 2: Public Registration Gateway**
    - [ ] Move `/register` endpoint to public-facing (non-VPN) access.
    - [ ] Implement Altcha PoW verification on public form.
* **Phase 3: Automated Onboarding**
    - [ ] "Push-button" approval workflow.
    - [ ] Server-side generation of WireGuard Keypair + PSK.
    - [ ] GPG Encryption of credentials.
    - [ ] Automated emailing of credentials to user.

### Announcements
* **Phase 1: Basic Publishing**
    - [ ] Create simple text-based CRUD interface (Create, Read, Update, Delete).
    - [ ] Ensure formatting handles basic line breaks/paragraphs without HTML injection risks.
* **Phase 2: Rich Text**
    - [ ] Research and implement lightweight Markdown editor (minimal dependencies).

### Theme Management
* **Phase 1: Manual Integration**
    - [x] Themes handled via file system placement (Manual upload to `static/css/themes/`).
* **Phase 2: Admin Tooling**
    - [ ] Create web-based "Theme Uploader" for admins (accepts `.css` files).
    - [ ] Validation logic to ensure uploaded themes don't break layout.

### System Health
* **Phase 1: Dashboard Metrics**
    - [ ] Implement basic Server Stats widget (CPU Usage %, RAM Usage %).
    - [ ] Add "Active Users" counter (Session based or WireGuard handshake based).

---

## 2. Media Suite (Role: User)

### Media Library
* **Phase 1: Database & Schema**
    - [ ] Design DB Schema for media types: `Audio`, `Video`, `Print` (Books/Manuals), `Images`.
    - [ ] Implement Stored Procedures for fetching media by type.
* **Phase 2: The Gallery**
    - [ ] Build scrollable list/grid view for browsing content.
    - [ ] Implement file serving logic (secure static file delivery).
* **Phase 3: Administration**
    - [ ] Add "Delete" control for Admins (UI-based removal of DB entry + file).
    - [ ] Implement "Upload/Ingest" workflow for Admins to add approved content.

### Requests
* **Phase 1: Public Board**
    - [ ] Create `Requests` table (User, Title, Description, Link, Status).
    - [ ] Build "Active Requests" view visible to ALL users (to spark engagement).
* **Phase 2: Submission Form**
    - [ ] Simple form for users to submit new requests.
    - [ ] Admin controls to mark requests as "Filled" or "Rejected".

### Reports
* **Phase 1: The Drop Box**
    - [ ] Create `Reports` table (User, Category [Media/App/Site], Content, Timestamp).
    - [ ] Build submission form for users.
* **Phase 2: Admin Review**
    - [ ] Add "Reports" tab to Admin Panel for reviewing issues.
    - [ ] Ability to dismiss/archive resolved reports.

---

## 3. Dev Suite (Role: Admin/User)

### Application Sandbox
* **Phase 1: The Launcher**
    - [ ] Create `Applications` table (Name, Description, Status, ContainerID/Port, "State" Comment).
    - [ ] Build Dashboard view listing available apps.
    - [ ] **Technical Spike:** Investigate secure method for Flask to interact with Docker Socket (for "spin up on fly" functionality).
* **Phase 2: Integration**
    - [ ] Implement "Launch" button (Opens app in new tab).
    - [ ] Implement dynamic Status indicators (Online/Offline) via ping/health check.

---

## 4. Social Suite (Role: Social)

### The Feed (Aggregator)
* **Phase 1: Core Posting**
    - [ ] Create `Feed_Posts` table (User, Link, Text Content, Timestamp).
    - [ ] Enforce character limit constraint (Encourage brevity/external hosting).
    - [ ] Render Logic: Parse links for basic display; Text-only content.
* **Phase 2: Interaction**
    - [ ] Create `Feed_Comments` table (Flat structure: PostID, User, Comment).
    - [ ] Implement single-thread comment view (No nesting).

### Chat (IRC-Style)
* **Phase 1: The Log**
    - [ ] Create `Chat_Log` table (User, Message, Timestamp).
    - [ ] Build basic view: Input box + Scrolling history (Page refresh/Poll based).
* **Phase 2: Enhancements**
    - [ ] Implement username highlighting (@mention logic).
    - [ ] Add DM support (Database flag for private messages).
    - [ ] **Constraint Enforcement:** No Emoji support (Text-only/ASCII emoticons).

### Bulletin Board
* **Phase 1: Structure (3-Tier)**
    - [ ] Create Tables: `Board_Categories` -> `Board_Threads` -> `Board_Posts`.
    - [ ] Ensure strict hierarchy (No sub-forums).
* **Phase 2: Interface**
    - [ ] Build Index View (Categories).
    - [ ] Build Thread List View.
    - [ ] Build Post View (Linear discussion).

### Profile
* **Phase 1: Identity & Settings**
    - [ ] Update `Users` table or `User_Preferences` to include `Bio` and `Public_Email` (Optional).
    - [ ] Implement "Theme Switcher" UI (linked to UserPreferences).
    - [ ] Change Password functionality.
* **Phase 2: Future**
    - [ ] Avatar upload support (Low Priority).

---

## 5. Global / Interface Requirements

### In-Context Administration
* **Direct Controls**
    - [ ] Develop shared Jinja2 macros (e.g., `admin_controls.html`) for Delete/Hide actions.
    - [ ] Integrate macros into Feed, Chat, Board, and Media views.
    - [ ] Ensure actions are performed via AJAX or POST without leaving the current page context.