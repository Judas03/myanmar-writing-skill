# Contributing

Contributions that improve naturalness, factual fidelity, platform fit, and
Burmese-English code-switching are welcome.

## Before contributing

- Open an issue for broad behavior changes so the intended outcome can be
  discussed before rules accumulate.
- Prefer a narrow correction supported by a realistic prompt and observable
  failure.
- Do not turn one writer's preference into a universal Burmese rule.
- Keep the skill focused on Facebook posts, website copy, and blog posts.

## Privacy and content rights

Never submit:

- API keys, credentials, environment files, or private repository details;
- personal phone numbers, email addresses, home addresses, or customer data;
- private messages or unpublished client material;
- copied posts, articles, or datasets that you do not have permission to
  redistribute.

Use synthetic examples whenever possible. If an authentic example is essential,
remove identifying details and confirm that its license permits redistribution.

## Language changes

For a language or style change:

1. Add or update a prompt in `tests/eval_cases.md`.
2. Explain the undesirable behavior and the preferred decision, not a required
   sentence to reproduce.
3. Update the smallest relevant instruction or reference.
4. Check that the change does not invent facts or overfit one example.
5. Record live evaluation results only when the prompt was actually run.

English terminology should follow the intended audience and brand. Do not add a
fixed English percentage or a universal list that every draft must use.

## Run the checks

```bash
python3 tests/run_tests.py
python3 /path/to/skill-creator/scripts/quick_validate.py \
  .opencode/skills/myanmar-writing
git diff --check
```

## Pull-request checklist

- The change has a clear user-facing reason.
- Names, numbers, links, claims, and uncertainty remain protected.
- New examples are synthetic or redistributable.
- No secrets or personal data are included.
- Mechanical tests and skill validation pass.
- Documentation reflects any changed behavior.
