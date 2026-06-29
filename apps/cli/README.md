# AgentForge CLI

Canonical command-line interface for AgentForge.

## Status

- Module: `apps/cli`
- Status: Genesis context explanation MVP
- Related requirements: `.agentforge/requirements/canonical-cli-mvp.md`, `.agentforge/requirements/installable-cli.md`, `.agentforge/requirements/context-scaffolding-mvp.md`, `.agentforge/requirements/context-explanation-mvp.md`
- Related ADRs: `.agentforge/adrs/0003-cli-module-architecture.md`, `.agentforge/adrs/0004-cli-packaging-and-distribution.md`, `.agentforge/adrs/0005-context-scaffolding-strategy.md`, `.agentforge/adrs/0006-context-explanation-boundary.md`

The canonical CLI now supports `agentforge validate-context`, `agentforge init-context`, and `agentforge explain-context`.

## Run Locally

From the repository root:

```bash
PYTHONPATH=apps/cli/src python -m agentforge_cli validate-context
```

Source-tree wrapper:

```bash
python apps/cli/bin/agentforge.py validate-context
```

Editable install:

```bash
python -m pip install -e apps/cli
agentforge validate-context
agentforge init-context demo-project
agentforge explain-context demo-project
```

This Genesis workflow assumes a standard Python environment with local packaging tools available. Public registry publishing remains deferred.

Windows PowerShell:

```powershell
$env:PYTHONPATH = "apps/cli/src"
python -m agentforge_cli validate-context
```

Windows PowerShell wrapper:

```powershell
python apps\cli\bin\agentforge.py validate-context
```

Windows PowerShell editable install:

```powershell
python -m pip install -e apps/cli
agentforge validate-context
agentforge init-context demo-project
agentforge explain-context demo-project
```

Validate an explicit project path:

```bash
PYTHONPATH=apps/cli/src python -m agentforge_cli validate-context examples/aics/minimal-project
```

Source-tree wrapper:

```bash
python apps/cli/bin/agentforge.py validate-context examples/aics/minimal-project
```

Installed command:

```bash
agentforge validate-context examples/aics/minimal-project
```

Initialize a new project context:

```bash
PYTHONPATH=apps/cli/src python -m agentforge_cli init-context demo-project
python apps/cli/bin/agentforge.py init-context demo-project
agentforge init-context demo-project
```

The scaffold creates the required AICS v0.1 baseline under `.agentforge/` and is intended as a starting point for project-specific governance work.

## Safety Behavior

`init-context` is safe by default.

- It creates a minimal AICS-compatible context baseline.
- It does not overwrite scaffold-managed files that already exist.
- It fails with actionable conflict output instead of merging or forcing changes.

Validate a generated project:

```bash
agentforge validate-context demo-project
```

Explain a project context:

```bash
PYTHONPATH=apps/cli/src python -m agentforge_cli explain-context demo-project
python apps/cli/bin/agentforge.py explain-context demo-project
agentforge explain-context demo-project
```

`explain-context` prints a read-only orientation report with the resolved project root, AICS validation status, context root, primary governance files, and validation signals when context is incomplete.

`validate-context` remains the canonical pass/fail command. `explain-context` can still return success when it successfully explains an incomplete context.

## Install Validation

Local install smoke coverage runs in:

```bash
python -m unittest apps.cli.tests.test_install
```

CI runs the same smoke test after checkout to confirm the editable install path still exposes `agentforge`.

## Output and Exit Codes

Successful validation prints:

```text
aics ok
```

Validation failures print one actionable error per line and return exit code `1`.

Invalid CLI usage, such as a missing project path, returns exit code `2`.

Initialization failures caused by scaffold conflicts or filesystem errors return exit code `1`.

Explanation failures caused by missing or inaccessible project paths return exit code `1`.

Installer-level packaging and global `agentforge` command distribution are deferred during Genesis.
