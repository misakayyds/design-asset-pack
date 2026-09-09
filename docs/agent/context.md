# Project context

Portable Codex skill with Python helpers and generated Adobe ExtendScript.

- SKILL.md is the discoverable entrypoint; references contain conditional workflow details.
- build_pack.py uses the Python standard library; audit_alpha.py, demo and tests use Pillow.
- layout.json version 1 is deliberately narrow. Preserve its validation and no-overwrite behavior.
- Public examples must be synthetic. Do not add user artwork, credentials or machine-specific paths.
- No actual Adobe import validation has been completed. Do not imply otherwise from Python or syntax checks.
- Run `python -m unittest discover -s tests -v` and the README example before publishing changes to helpers.
