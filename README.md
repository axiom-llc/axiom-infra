
# AXIOM local portfolio stack

`axiom-infra` provides the local Docker Compose integration stack and
cross-repository portfolio validation workflow for the active AXIOM repository ecosystem, plus the canonical local ASON → APEX → RAG executable reference.

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

The workflow treats checkout credentials as a boundary: it removes checkout
credentials before repository code executes. Repository visibility and any
checkout-authentication configuration are workflow concerns, not a requirement
of the local Compose stack.

## Local validation

```bash
docker compose config --quiet
docker compose up --build --wait
cat plan.json | docker compose run --rm -T ason submit -
docker compose down
git diff --check
```

Live-provider benchmarks are intentionally outside the portfolio workflow.

## Optional remote operator access

Remote host access through Desktop Commander Remote MCP is optional infrastructure only. It may be used for explicit operator-authorized cross-repository inspection, testing, diagnostics, and maintenance, but no AXIOM runtime or CI path depends on it. See [REMOTE_MCP.md](REMOTE_MCP.md) for the trust boundary and rejected coupling.

## Canonical portfolio validation receipt

Run `python portfolio_receipt.py` from this repository to execute the registered local checks across all 13 active AXIOM repositories. Missing private/unavailable CI checkouts are explicit failures by default or explicit coverage limitations only when `--allow-missing` is intentionally selected. The JSON receipt records exact Git revisions, clean-tree state, each command result, overall `PASS`, `PASS_WITH_LIMITS`, or `FAIL`, explicit per-repository validation coverage/limitations, and a canonical SHA-256 digest. Use `--repo NAME` to validate a subset and `-o PATH` to persist the receipt. The receipt applies only to the recorded revisions/checks and is not a deployment or external certification.

## Canonical release compatibility set

`release-compatibility.json` records the current core compatibility tuple and publication/dependency order: RAG `1.5.0` → APEX `3.2.0` → ASON `0.3.0`. RAG `1.5.0` is already published; APEX `3.2.0` and ASON `0.3.0` remain unpublished. `python release_compatibility.py` verifies source package metadata and exact cross-package minimums. This gate is compatibility evidence only and never authorizes tags or release publication.

## Executable core-stack reference

With the Compose services running and local validation credentials exported, run `python core_stack.py`. It performs a provider-free RAG HTTP inspection, submits a bounded write/read plan through ASON, verifies the authorization and approved-plan digest persisted by APEX, records exact repository revisions, and emits a SHA-256 evidence digest. The discoverable demo wrapper lives at `axiom-demos/core-stack/run.sh`.
