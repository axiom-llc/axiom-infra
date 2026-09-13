
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

Set `GEMINI_API_KEY`, `RAG_API_TOKEN`, and a non-empty `APEX_API_KEY` in
`.env`. `GEMINI_API_KEY` belongs only to the RAG service; APEX does not receive
or forward it for RAG operations. Compose defaults APEX to its credential-free
local Ollama provider; configure a reachable local provider before using APEX
model-generation features.

Validate the resolved Compose configuration:

```bash
docker compose config --quiet
```

## Run

Start RAG and APEX:

```bash
docker compose up --build -d
```

RAG binds `0.0.0.0:8000` inside its container and is published only at
`127.0.0.1:8000` on the host. Its callers use `http://rag:8000` inside Compose
and `http://127.0.0.1:8000` from the host; both require `RAG_API_TOKEN`.
It alone mounts `rag_data` at `/root/.rag/chroma`, the canonical persistence
root. The namespace is `documents-gemini-embedding-2`; its embedding identity
is `google-gemini / gemini-embedding-2 / 3072 / schema 1`.

APEX is published at `127.0.0.1:8080`, requires `X-Apex-Key`, stores
history/memory in the `apex_data` volume, and reaches RAG at `http://rag:8000`.

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

## RAG service boundary

The Compose stack runs the single RAG storage owner, APEX, and on-demand ASON.
The RAG service owns the canonical persistence volume and its provider
credential. APEX only has the HTTP target, bearer token, and explicit mapped
namespace/embedding assertion. No caller mounts RAG persistence.

The RAG container's non-loopback bind is intentionally token-protected. It does
not publish beyond host loopback. The host URL is for local inspection/tools;
container callers must use the Compose DNS name rather than host loopback.
`rag_multi_query` remains a legacy `/query` tool boundary, while evaluator and
local-provider operations remain outside this shared service/root.

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
local Compose integration with an empty ASON plan. APEX tests marked
`host_isolation` are excluded here; APEX CI owns those probes and configures
Bubblewrap and delegated systemd/cgroup resource controllers.

All listed AXIOM repositories are currently public. The workflow still
references read-only deploy-key secrets for the RAG and API checkouts and
removes checkout credentials before repository code executes. Those credential
references are current workflow state, not a repository-visibility requirement.
Removing them requires a separate workflow change and validation.

## Local validation

```bash
docker compose config --quiet
docker compose up --build --wait
cat plan.json | docker compose run --rm -T ason submit -
docker compose down
git diff --check
```

Live-provider benchmarks are intentionally outside the portfolio workflow.
