---
description: How to set up the development environment for Nexus v2
---

This workflow helps you set up the Next.js frontend and Python backend.

1.  **Frontend Setup**
    -   Navigate to `frontend`
    -   Install dependencies: `npm install`

2.  **Backend Setup**
    -   Navigate to `backend`
    -   Create virtual environment (optional but recommended): `python -m venv venv`
    -   Activate venv:
        -   Windows: `venv\Scripts\activate`
        -   Unix: `source venv/bin/activate`
    -   Install dependencies: `pip install -r requirements.txt`

3.  **Verification**
    -   Check if `node_modules` exists in `frontend`.
    -   Check if dependencies are installed in `backend`.
