# AgentForge CLI

Canonical command-line interface for AgentForge.

## Status

- Module: `apps/cli`
- Status: Genesis context scaffolding MVP
- Related requirements: `.agentforge/requirements/canonical-cli-mvp.md`, `.agentforge/requirements/installable-cli.md`, `.agentforge/requirements/context-scaffolding-mvp.md`
- Related ADRs: `.agentforge/adrs/0003-cli-module-architecture.md`, `.agentforge/adrs/0004-cli-packaging-and-distribution.md`, `.agentforge/adrs/0005-context-scaffolding-strategy.md`

The canonical CLI now supports both `agentforge validate-context` and `agentforge init-context`.

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

Installer-level packaging and global `agentforge` command distribution are deferred during Genesis.
