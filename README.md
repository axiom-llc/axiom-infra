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
