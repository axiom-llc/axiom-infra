# AXIOM local portfolio stack

Use sibling checkouts of `axiom-infra`, `axiom-rag`, `axiom-apex`, and
`axiom-ason`. Compose builds one shared image from the ASON Dockerfile using
all three local Python packages, so unpublished matching versions work together.
The Dockerfile-specific ignore file allows only package source and build metadata
into the build context, excluding local credentials, Git history, and archives.

From this directory:

```sh
cp .env.example .env
# Set GEMINI_API_KEY and a non-empty APEX_API_KEY in .env.
docker compose config --quiet
docker compose up --build -d apex
cat plan.json | docker compose run --rm -T ason submit -
```

APEX is published on `127.0.0.1:8080`, requires `X-Apex-Key`, and persists
history/memory in `apex_data`. ASON is an on-demand CLI in the `tools` profile,
not an idle daemon. It reads `APEX_URL=http://apex:8080` and shares the API key.
The optional `--apex-url` CLI argument overrides that environment variable.

Use `docker compose down` to stop the stack without deleting its data volume.

The `Portfolio validation` GitHub workflow checks the current runtime, policy,
retrieval, HTTP-client, and demo repositories daily and on demand. It builds and
installs matching wheels, runs each repository's offline tests in its own process,
checks installed entry points outside the source trees, and exercises Compose
with an empty ASON plan. Live-provider benchmarks remain separate.

## Private dependency access

The portfolio workflow reads the current `main` branches of its dependencies.
`axiom-rag` and `axiom-api` are private; the default `GITHUB_TOKEN` only grants
access to this repository. Each private dependency has one dedicated **read-only
deploy key**, with the private half stored only in this repository's Actions secrets:

| Dependency | Actions secret in `axiom-infra` |
| --- | --- |
| `axiom-llc/axiom-rag` | `PORTFOLIO_RAG_DEPLOY_KEY` |
| `axiom-llc/axiom-api` | `PORTFOLIO_API_DEPLOY_KEY` |

The keys cannot write or access another repository. Checkouts use strict SSH host
verification and `persist-credentials: false`, removing credentials before any
repository code runs. The workflow records all checked-out commits in its log.
Secrets are unavailable to fork pull requests; those runs cannot validate private
dependencies and must be rerun from a reviewed branch in this repository.

Deploy keys do not expire automatically. To rotate one, register a new read-only
key on its dependency, replace the matching Actions secret, validate a workflow
run, then delete the old deploy key. To revoke access immediately, delete that
dependency's deploy key and the matching secret. Never commit private keys or
include them in logs or artifacts.

This uses existing repository administration without granting organization-wide
permissions or storing a personal token. A GitHub App with read-only Contents
access to these two repositories is the alternative if organization App
administration becomes available; it provides short-lived installation tokens
but still requires protecting and rotating its signing key.
