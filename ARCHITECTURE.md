# AutoDoc Architecture (Working Notes)

## 1. Entry Points
- CLI commands:
  - autodoc scan
  - autodoc generate
  - autodoc status (?)

## 2. Core Modules
- autodoc/cli.py
- autodoc/core/state.py
- autodoc/core/scan.py
- autodoc/core/...

## 3. State Model
- Location: .autodoc/state.json
- High-level fields:
  - repo
  - files
  - last_scan
  - dependencies

## 4. Workflows
### Scan
TBD

### Generate
TBD

## 5. Open Questions
- TBD
