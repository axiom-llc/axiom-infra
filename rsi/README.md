# Infra native RSI

A deterministic source-pinned proposal removes redundant short-lived list copies from the `portfolio_receipt.build` repository-selection path. It preserves the existing ACTIVE set, missing-checkout classification, checks, hashes, and all report fields. No candidate is applied. Benchmarks use 100% synthetic checkout directories and stubbed Git/CI commands, with 11 paired runs of 200 iterations each, and seven semantic holdouts including empty lists, tuples, subsets and missing repositories.

The native runner independently tests source revisions, deduplication, unsafe paths, normal Git apply/reverse and existing portfolio regressions. The mocked benchmark does not measure real end-to-end Git/CI runtime and cannot justify production promotion without representative validation.
