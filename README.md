
# AXIOM local portfolio stack

`axiom-infra` provides the local Docker Compose integration stack and
cross-repository portfolio validation workflow for AXIOM RAG, APEX, ASON, API,
and demos.

## Repository layout

```text
axiom-infra/
├── .env.example
├── .github/workflows/portfolio.yml
├── docker-compose.yml
└── README.md
```

The Compose build expects sibling checkouts under one parent directory:

```text
axiom-llc/
├── axiom-infra/
├── axiom-rag/
├── axiom-apex/
├── axiom-ason/
├── axiom-api/
└── axiom-demos/
```

The local image is built from `axiom-ason/Dockerfile` using the matching sibling
RAG, APEX, and ASON packages.

## Configure

From `axiom-infra`:

```bash
cp .env.example .env
```

Set `GEMINI_API_KEY` and a non-empty `APEX_API_KEY` in `.env`.

Validate the resolved Compose configuration:

```bash
docker compose config --quiet
```

## Run

Start APEX:

```bash
docker compose up --build -d apex
```

APEX is published at `127.0.0.1:8080`, requires `X-Apex-Key`, and stores
history/memory in the `apex_data` volume.

Submit an ASON plan through the on-demand tools profile:

```bash
cat plan.json | docker compose run --rm -T ason submit -
```

ASON uses:

```text
APEX_URL=http://apex:8080
```

and shares the configured APEX API key.

Stop the stack without deleting persistent data:

```bash
docker compose down
```

## Current service boundary

The current Compose file runs APEX and on-demand ASON. It does not run a
separate `axiom-rag` HTTP service.

RAG 1.4.0 provides a protected HTTP storage compatibility API, but CLI/APEX
storage adapters have not yet migrated to it. Deployment mapping and migration
are separate follow-up work; this Compose stack must not be treated as having
completed that migration.

## Portfolio CI

`.github/workflows/portfolio.yml` runs:

* on pushes and pull requests;
* manually through `workflow_dispatch`;
* daily on its configured schedule;
* on Python 3.11 and 3.12.

The workflow checks out:

* `axiom-infra`;
* `axiom-rag`;
* `axiom-apex`;
* `axiom-ason`;
* `axiom-api`;
* `axiom-demos`.

It records the exact checked-out revisions, builds matching package wheels,
installs them together, runs each repository's offline tests in a separate
process, verifies installed entry points outside source trees, and exercises the
local Compose integration with an empty ASON plan.

All listed AXIOM repositories are currently public. The workflow still
references read-only deploy-key secrets for the RAG and API checkouts and
removes checkout credentials before repository code executes. Those credential
references are current workflow state, not a repository-visibility requirement.
Removing them requires a separate workflow change and validation.

## Local validation

```bash
docker compose config --quiet
docker compose up --build --wait apex
cat plan.json | docker compose run --rm -T ason submit -
docker compose down
git diff --check
```

Live-provider benchmarks are intentionally outside the portfolio workflow.
