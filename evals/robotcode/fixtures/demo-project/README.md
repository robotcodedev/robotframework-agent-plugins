# Demo fixture project

A small, **self-contained** Robot Framework project for exercising the [`robotcode` skill evals](../../). No network, no database, no external services — a tiny Python library (`libs/OrderLibrary.py`) backs everything in memory, so the suite runs fully offline.

It's a throwaway: point the evals (or a manual Claude session) at it, let the agent run `robotcode` commands against it, and discard any artifacts.

## Layout

```
demo-project/
├── robot.toml            # paths=tests, python-path=libs, output-dir=results
├── setup.sh              # the test setup — runs the suites to produce results/{baseline,output}.xml
├── libs/OrderLibrary.py  # in-memory login + orders backend (custom keywords)
├── orders.resource       # higher-level keywords: Login With Credentials, Submit Order, …
└── tests/
    ├── login.robot       # 'Login Works' FAILS BY DEFAULT; 'smoke' + 'login' tags
    ├── orders.robot      # passing tests; 'smoke' + 'orders' tags
    └── checkout.robot    # calls undefined 'Finalize Checkout' → a static error
```

## The test setup (`setup.sh`)

Several evals need a *finished run* to analyze. `./setup.sh` runs the suites and writes two runs under `results/` (gitignored — `output.xml` embeds absolute paths):

- **`results/baseline.xml`** — every test passes (login forced good with `-v PASSWORD:'correct horse'`).
- **`results/output.xml`** — the default run, where `Login Works` fails on purpose.

So the current run carries a **planted regression** against the passing baseline — exactly what the results and diff evals inspect. Run it once before those cases:

```bash
./setup.sh        # writes results/baseline.xml (all pass) and results/output.xml (1 expected failure)
```

## What's planted (and which eval uses it)

- **`Login Works` fails by default** — `${PASSWORD}` is wrong, so the backend returns `status=error` and the assertion on `tests/login.robot:25` fails, leaving a `${response}` dict in scope. The baseline run overrides `${PASSWORD}` so it passes. → results (`02`), diff (`03`), debugger (`08`, `09`).
- **`smoke` tag** on `Login Works` and `Shipped Order Has Status Shipped`. → run-tests (`01`), discover (`04`).
- **`Submit Order`** keyword in `orders.resource`. → libdoc (`05`), REPL-breakpoint (`10`).
- **`checkout.robot` calls undefined `Finalize Checkout`** — a `KeywordNotFound` that `analyze code` reports without running anything. → analyze (`06`).

## Prerequisites

- `robotcode` installed **in the environment you run it from** (`pip install robotcode[all]`), so `discover`, `analyze`, `repl`, `robot-debug`, and `results` are all present.
- The results (`02`) and diff (`03`) evals need `./setup.sh` run first (see above).
- The browser eval (`07`) additionally needs a browser library — `pip install robotframework-seleniumlibrary` (or `robotframework-browser` + `rfbrowser init`). It's the only case that isn't offline; the fixture defines no browser keywords.

## Quick manual smoke check

```bash
robotcode discover all                       # 3 suites, 6 tests, tags incl. smoke
robotcode analyze code tests/checkout.robot  # reports KeywordNotFound: 'Finalize Checkout'
./setup.sh                                   # 1 failure expected ('Login Works')
robotcode results summary --failed           # 4 passed, 1 failed     (needs robotcode >= 2.6)
robotcode results diff results/baseline.xml  # 'Login Works' shows as a new failure
```

Run artifacts (`results/`, `.robotcode_cache/`, `*.html`) are gitignored.
