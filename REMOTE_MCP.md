# Optional Remote MCP operator access

Desktop Commander Remote MCP is an optional operator channel for reaching an authorized AXIOM development host from ChatGPT, Claude, or another MCP client. It is infrastructure scaffolding, not an AXIOM runtime dependency.

## Accepted uses

- inspect sibling repositories, Git state, logs, and local configuration;
- run bounded builds, tests, validation, and diagnostic commands;
- perform explicit operator-authorized repository maintenance across the portfolio;
- access long-running local processes when direct local execution is otherwise inconvenient.

These uses preserve existing repository CLIs, HTTP APIs, Compose, GitHub Actions, Director, Harness, ASON, and APEX as the authoritative system interfaces.

## Trust boundary

Remote MCP can expose the real host filesystem, terminal, and processes to a remote AI client. Treat every invocation as privileged host access. Scope allowed directories and blocked commands to the minimum needed, keep credentials out of prompts/results, and review mutations before canonical acceptance.

The observed beta client supports configurable allowed directories, blocked commands, shell selection, file/process tools, and telemetry. A configuration with an empty allowed-directory list means unrestricted filesystem scope and is unsuitable as an unattended production executor.

Remote tool output is evidence only. It does not acquire Owner, Director, Harness, ASON, or APEX authority by transport. Existing approval, spend, sensitivity, validation, effect-ledger, and recovery boundaries remain unchanged.

## Rejected coupling

Do not add Desktop Commander to `APEX_MCP_SERVERS` by default, register it as a Harness executor, require it in CI, or make any repository depend on its remote service. Those paths duplicate existing execution interfaces and expand the remote effect surface without demonstrated acceptance gain.

If a future bounded workload justifies machine routing through Remote MCP, first define its exact tool allowlist, filesystem scope, authentication, execution-profile identity, failure semantics, cost, telemetry/privacy posture, and deterministic acceptance evidence.

## Availability and cost

Local Desktop Commander MCP is open-source infrastructure; Remote MCP depends on the third-party remote service and may change independently. Treat beta availability, account status, quotas, and pricing as external state to verify at use time. No AXIOM workload may assume remote availability or paid capacity.
