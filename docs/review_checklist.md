# Review Checklist

Use this after every Codex task.

## Scope

- Was the requested task completed?
- Did the change go beyond the requested scope?
- Were forbidden areas modified?
- Was real hardware communication avoided unless explicitly requested?

## Runtime

- Does Mock mode still run?
- Did `python -m pytest` pass?
- Did GUI smoke pass when UI changed?
- Were tests updated only when behavior legitimately changed?

## Architecture

- Is UI still decoupled from hardware transport?
- Did backend changes stay behind `BackendInterface`?
- Did configs/models stay consistent?
- Were protocols changed only with matching docs?

## Provenance

- Was external code copied, adapted or strongly derived?
- Was `docs/code_provenance.md` updated?
- Is license risk recorded?
- Is future action clear?

## Docs

- Was README updated if user-facing behavior changed?
- Were phase docs updated if plan/status changed?
- Were review/provenance docs updated if governance changed?

## Next Step

- Is the next phase recommended clearly?
- Should the current version be committed or tagged?
- Are there unresolved risks or manual checks?
