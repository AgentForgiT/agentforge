# AgentForge CLI

Canonical command-line interface for AgentForge.

## Status

- Module: `apps/cli`
- Status: Genesis MVP
- Related requirements: `.agentforge/requirements/canonical-cli-mvp.md`
- Related ADR: `.agentforge/adrs/0003-cli-module-architecture.md`

## Run Locally

From the repository root:

```bash
PYTHONPATH=apps/cli/src python -m agentforge_cli validate-context
```

Source-tree wrapper:

```bash
python apps/cli/bin/agentforge.py validate-context
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "apps/cli/src"
python -m agentforge_cli validate-context
```

Windows PowerShell wrapper:

```powershell
python apps\cli\bin\agentforge.py validate-context
```

Validate an explicit project path:

```bash
PYTHONPATH=apps/cli/src python -m agentforge_cli validate-context examples/aics/minimal-project
```

Source-tree wrapper:

```bash
python apps/cli/bin/agentforge.py validate-context examples/aics/minimal-project
```

## Output and Exit Codes

Successful validation prints:

```text
aics ok
```

Validation failures print one actionable error per line and return exit code `1`.

Invalid CLI usage, such as a missing project path, returns exit code `2`.

Installer-level packaging and global `agentforge` command distribution are deferred during Genesis.
