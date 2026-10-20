# Myanmar Writing

An open-source agent skill for writing Burmese Facebook posts, website copy,
and blog posts that sound locally written rather than translated.

It helps an AI writing assistant preserve facts, use natural Burmese sentence
structure, and mix familiar English words only where Myanmar readers would
actually use them.

## Highlights

- Writes and rewrites Facebook, website, and blog content.
- Localizes ideas at paragraph level instead of translating word by word.
- Uses familiar English terms such as `website`, `domain`, `position`, or
  `salary` when they fit the audience and brand.
- Preserves names, prices, dates, links, uncertainty, and supplied claims.
- Avoids invented product features, fake scarcity, forced emoji, and generic
  marketing filler.
- Adapts to approved brand examples without copying their sentences.
- Includes a local validator for Unicode, Zawgyi, spacing, placeholders, and
  other mechanical defects.

The skill does not guarantee perfect native voice. Burmese varies by audience,
region, and brand, so important public copy should still receive human review.

## Supported tools

| Tool | Project skill path | Explicit invocation |
|---|---|---|
| OpenCode | `.opencode/skills/myanmar-writing/` | `@myanmar-writing` |
| Codex | `.agents/skills/myanmar-writing/` | `$myanmar-writing` |
| Claude Code | `.claude/skills/myanmar-writing/` | `/myanmar-writing` |

Codex and Claude Code use repository-scoped symlinks to the OpenCode skill
folder, so the project has one maintained copy of the instructions.

## Quick start

```bash
git clone https://github.com/Judas03/myanmar-writing-skill.git
cd myanmar-writing-skill
```

Launch Codex, Claude Code, or OpenCode from this directory. Then ask for copy:

```text
$myanmar-writing Write a professional Burmese Facebook announcement.
Brand: Example Studio
Audience: existing customers
Facts: Our website domain changed from old.example to new.example
CTA: Ask readers to save the new address
Do not invent any other details.
```

Use `@myanmar-writing` in OpenCode or `/myanmar-writing` in Claude Code.

## Personal installation

### OpenCode

The installer links the skill and its convenience commands into
`~/.config/opencode`:

```bash
./install.sh
```

Useful options:

```bash
./install.sh --project /path/to/project
./install.sh --copy
./install.sh --uninstall
```

Convenience commands include `/burmese`, `/burmese-casual`,
`/burmese-formal`, and `/burmese-diaspora`.

### Codex

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$PWD/.opencode/skills/myanmar-writing" \
  "$HOME/.agents/skills/myanmar-writing"
```

Restart Codex if the skill does not appear immediately.

### Claude Code

```bash
mkdir -p "$HOME/.claude/skills"
ln -s "$PWD/.opencode/skills/myanmar-writing" \
  "$HOME/.claude/skills/myanmar-writing"
```

Restart Claude Code if the skill does not appear immediately.

If a destination already exists, inspect it before replacing it.

## Give the skill a strong brief

For reliable output, provide:

- target format: Facebook, website, or blog;
- audience and desired tone;
- facts, names, numbers, and links that must remain exact;
- preferred English or Burmese terms;
- the intended call to action;
- claims or details the model must not add.

For a close brand match, include 10–20 approved posts from the same writer or
brand. Remove customer data, private messages, unpublished business details,
and personal contact information before sharing examples.

## How English terms are handled

The skill does not impose an English-word quota or translate every term into
Burmese. It chooses the form the audience is most likely to recognize.

- Proper names, URLs, commands, and identifiers stay exact.
- Established English words can remain English when they are the natural local
  choice.
- Burmese carries the surrounding grammar and explanation.
- Ordinary English spelling is corrected unless the text is a locked name,
  identifier, quotation, or explicitly required form.
- English is not added merely to make the writing look modern.

See
[`references/terminology.md`](.opencode/skills/myanmar-writing/references/terminology.md)
for the full decision guide.

## Mechanical validator

```bash
python3 .opencode/skills/myanmar-writing/scripts/validate.py draft.md \
  --format facebook
```

Primary formats are `facebook`, `web`, `blog`, and `generic`. Add `--json` for
machine-readable output or `--strict` to make warnings fail the command.

Accurate Zawgyi detection is optional:

```bash
pip3 install -r .opencode/skills/myanmar-writing/scripts/requirements.txt
```

The validator checks mechanical defects only. A clean result does not prove
that the writing sounds native.

## Tests

```bash
python3 tests/run_tests.py
python3 /path/to/skill-creator/scripts/quick_validate.py \
  .opencode/skills/myanmar-writing
```

Behavioral prompts and observed regressions are documented in
[`tests/eval_cases.md`](tests/eval_cases.md) and
[`tests/eval_results.md`](tests/eval_results.md). Test fixtures are synthetic
and contain no real customer or contributor data.

## Project structure

```text
.agents/skills/myanmar-writing  -> ../../.opencode/skills/myanmar-writing
.claude/skills/myanmar-writing  -> ../../.opencode/skills/myanmar-writing
.opencode/
├── commands/
└── skills/myanmar-writing/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── assets/
tests/
├── eval_cases.md
├── eval_results.md
├── fixtures/
└── run_tests.py
```

## Privacy and security

The skill and validator do not send content to an additional service or include
telemetry. Your chosen AI host still processes prompts according to its own
privacy and retention policies.

Do not commit API keys, credentials, private client content, or unredacted real
posts. See [SECURITY.md](SECURITY.md) for reporting security issues.

## Contributing

Burmese writers, editors, developers, and localization practitioners are
welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue
or pull request.

The general language foundations are informed by Microsoft's
[Burmese (Myanmar) Localization Style Guide](https://download.microsoft.com/download/055e0e21-a0d7-482c-aeea-8b0190008c9a/mya-MMR-StyleGuide.pdf)
and the Unicode Consortium's
[Myanmar FAQ](https://www.unicode.org/faq/myanmar.html). Product-localization
rules are not treated as universal rules for social or editorial writing.

## License

Released under the [MIT License](LICENSE).
