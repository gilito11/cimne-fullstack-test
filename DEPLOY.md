# Deployment guide — hosted demo

This document walks through deploying the project to free-tier services so the
reviewer can use the application without installing anything locally.

Components:

- **Neo4j Aura Free** — managed Neo4j 5.x database (50k nodes, 175k relationships)
- **Fly.io** — backend (FastAPI) on a shared 256 MB machine
- **Vercel** — frontend (static SPA)

The end result is a single URL where the reviewer can register, log in, manage
users and view the buildings indicator on the map.

---

## 1. Database — Neo4j Aura Free

1. Create a free instance at <https://console.neo4j.io>.
2. Choose **Aura Free** and download the generated `.env` file — it contains
   the connection URI and password. Save them.
3. Open the **Neo4j Browser** for your instance and run:
   ```cypher
   CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
   CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
   ```
4. Seed the buildings locally against the Aura instance:
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt

   export NEO4J_URI="neo4j+s://<your-id>.databases.neo4j.io"
   export NEO4J_USER=neo4j
   export NEO4J_PASSWORD="<your-aura-password>"
   python scripts/seed_buildings.py ../data/buildings.geojson
   ```

---

## 2. Backend — Fly.io

```bash
cd backend
fly auth login
fly launch --copy-config --no-deploy --name cimne-test-api --region cdg

fly secrets set \
  NEO4J_URI="neo4j+s://<your-id>.databases.neo4j.io" \
  NEO4J_USER=neo4j \
  NEO4J_PASSWORD="<your-aura-password>" \
  JWT_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')" \
  EXTERNAL_API_EMAIL="testui_registered@cimne.upc.edu" \
  EXTERNAL_API_PASSWORD="123456aA!" \
  CORS_ORIGINS="https://<your-frontend>.vercel.app"

fly deploy
```

Note the assigned URL (e.g. `https://cimne-test-api.fly.dev`).

---

## 3. Frontend — Vercel

```bash
cd frontend
npm install -g vercel
vercel login
vercel link              # accept defaults, create new project
vercel env add VITE_API_BASE production   # paste https://cimne-test-api.fly.dev
vercel --prod
```

Vercel will print the production URL. Add it back to the Fly backend so CORS
allows it:

```bash
fly secrets set CORS_ORIGINS="https://<your-frontend>.vercel.app" -a cimne-test-api
```

---

## 4. Smoke test

```bash
curl https://cimne-test-api.fly.dev/health
# {"status":"ok"}
```

Open the Vercel URL, register an admin user, log in, and check the Buildings
page to confirm the external indicator integration works against the
production database.
