# Behavioral Evaluation Results

Date: 2026-10-20  
Runtime: OpenCode 2.1.0 using the locally configured default model  
Method: repeat the same prompt after each instruction change; inspect the final
copy for the scorecard and automatic failures in `eval_cases.md`.

These results verify observed behavior for the listed prompts. They do not
prove universal native fluency or a particular brand voice.

## Facebook factual-fidelity regression

Prompt: Yangon bakery; `Pandan Coconut Cake`; Friday through Sunday; `18,000
MMK`; pickup at `Sanchaung`; delivery fee depends on township; existing
customers; warm, not childish; no fake scarcity; Messenger CTA.

Initial result failed:

- guessed an incorrect Burmese place name for `Sanchaung`;
- invented ingredient or sensory description from the product name;
- published the private audience note as an eligibility-like line.

After adding fact locking and separating instructions from publishable facts,
the next run preserved `Sanchaung` and the product name, but invented a price
unit and appended an internal compliance explanation.

After the second correction, the unchanged prompt produced paste-ready copy
that:

- preserved `Pandan Coconut Cake`, `Sanchaung`, and `18,000 MMK`;
- stated Friday through Sunday without inventing a date;
- did not add ingredients, sensory claims, scarcity, eligibility, or a price
  unit;
- kept the audience and tone instructions out of the copy;
- used Messenger for the supplied CTA and added no audit appendix.

Result: factual fidelity and delivery passed for this case. Exact brand voice
remains unverified without approved user samples.

## Website feature-hallucination regression

Prompt: hero, three benefit sections, and CTA for `GloryBook`; salon owners can
manage bookings, staff schedules, and customer history from a phone; audience
is non-technical; do not claim increased revenue.

Initial result failed by inventing cancellation, rescheduling, calendar UI,
shift swapping, particular history fields, and instant activation.

A first correction still invented paper replacement, computer independence,
appointment assignment, guaranteed memory benefits, and a trial-style CTA.

After requiring one-to-one mapping between the three supplied capabilities and
the three sections, the unchanged prompt produced copy limited to:

- bookings managed from a phone;
- staff schedules managed from a phone;
- customer history managed from a phone;
- a neutral learn-more CTA.

It preserved `GloryBook`, used appointment language rather than order language,
made no revenue claim, and added no unprovided contact channel.

Result: factual and structural constraints passed. The copy was intentionally
concise and somewhat repetitive; approved brand examples are needed to improve
voice without reintroducing invented features.

## Blog localization

Prompt: localize a warning that automation saves time but accelerates mistakes
in a broken process, and that a team should document its real process first.

The result preserved both sides of the argument, kept automation beneficial but
conditional, used Burmese clause order, and did not mechanically translate
English pronouns.

Result: passed meaning and nuance for this case.

## Incomplete course brief

Prompt: publish-ready barista-course Facebook post; starts next month; includes
practical training; no other facts.

The result did not invent an exact date, time, price, location, certificate,
school name, or registration channel. It used conspicuous placeholders and
listed the missing publishable information after the draft.

Result: passed missing-fact control for this case.
