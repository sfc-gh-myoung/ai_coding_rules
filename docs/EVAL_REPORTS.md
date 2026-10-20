# Evidence-bound eval reports

Reports are local development artifacts. Rendering needs no Snowflake connection,
credentials, live benchmark, or AI call. It does not change evaluator scoring.

## Select evidence explicitly

Snapshot exact completed run directories before comparing models:

```bash
uv run ai-rules rule-loader select-report results/model-a_5x_timestamp results/model-b_5x_timestamp --output .workbench/selection.json --archive results/interrupted_5x_timestamp --exclude "glm-5.2=Excluded after exhausted server errors"
make eval-report CLI_ARGS="--selection .workbench/selection.json --output .workbench/reports"
```

Use real run names. Selection stores manifest/sample SHA-256 digests, model
identities, exact source paths and a copy of the catalog rate card. Relative source
paths in a selection resolve against that file. Never include credentials. Selected
sources must share source commit, fixture inventory, package version and evaluator
settings. Duplicate configurations/samples or changed evidence fail closed.

Interrupted sources belong in `--archive`, not in the competitive cohort. Archives
and explicit exclusions remain visible without inventing never-started attempts.
Incomplete selected configurations show reduced capture and do not qualify for
comparative extrema. Do not choose a later run merely because its timestamp is newer.

## Inspection is not comparison

```bash
make eval-report CLI_ARGS="--results-dir results --output .workbench/reports"
```

Without `--selection`, the command retains latest-run discovery as labeled
inspection. It disables rankings/extrema and does not establish protocol
compatibility. Evidence must have the current manifest/per-fixture layout; legacy
summary-only reports require their archived original HTML, not invented samples.
`--strict` is retained for compatibility: malformed evidence always fails closed.
`--connection` is accepted but unused by local rendering. An inherited connection
environment variable cannot trigger authentication or AI narration. Optional AI
analysis can be performed separately; it is not part of deterministic report metrics.

## Read the metrics

- `pass@1` is the equal-fixture mean of successful-attempt fractions across every
  observed outcome, including skipped reads and infrastructure outcomes as non-passes.
- `pass@3` estimates at least one success in a random size-three subset of observed
  outcomes without replacement. `pass^3` estimates all three successes. Fixtures with
  fewer than three attempts are omitted with an explicit reduced-cohort count.
- Scored rate is a separate diagnostic that excludes `error` and
  `model-skipped-reads`, matching evaluator outcome semantics. It must not substitute
  for protocol reliability.
- Mean AI Credits use the selection's embedded rates. Inclusive input tokens subtract
  cache-write and cache-read counters before uncached input pricing. Unknown rates or
  missing counters are unavailable/partial, never zero. Recorded dollar counters do
  not become metered costs. Uncaptured retry spend and infrastructure spend are not
  included. Credits per pass is unavailable unless selected-attempt cost is complete.
- Capture labels show exact captured/expected counts. Qualified Best/Worst cells show
  displayed descriptive extrema, including ties, not statistical superiority.

Filters change visibility only; estimates and cohorts remain fixed. Tables sort using
full numeric precision. Fixture links show actual run records. Print includes all
configurations and unvisited execution evidence, then restores screen selection.
The self-contained viewer has no CDN, runtime fetch, dynamic evaluation or browser
storage dependency. Reports include raw final text and local source metadata: review
them before deliberate sharing.

## Verify artifacts

Each invocation prints a new immutable generation directory containing `report.html`
and `report.json`. Both appear through one atomic directory rename; input evidence
is never modified. Generations do not overwrite earlier reports.

```bash
make eval-report-verify REPORT=.workbench/reports/eval-report-id
make test-report-browser
```

Replace the generation ID with the printed directory. Verification validates embedded
JSON equality, source hashes and recomputed metrics; source directories must remain
available for this evidence check. Opening the HTML itself requires no source files.
Browser tests explicitly install the pinned Chromium revision and do not run in normal
`make validate`. Check the actual report at desktop/mobile, light/dark and A4 portrait
and landscape print widths before delivering a PDF. Large evidence appendices can
produce long PDFs; an exported file alone is not proof of layout correctness.
