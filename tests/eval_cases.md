# Behavioral Evaluation Cases

Use these prompts to compare the skill against a no-skill baseline or a prior
version. Judge meaning and reader experience, not exact wording.

## Scorecard

Score each dimension from 1 (poor) to 5 (excellent):

- **Naturalness:** sounds locally written when read aloud;
- **Fidelity:** no invented or altered facts, claims, dates, prices, or links;
- **Audience fit:** vocabulary, politeness, and code-switching suit the reader;
- **Platform fit:** structure works for Facebook, website, or blog;
- **Specificity:** useful concrete detail replaces generic filler;
- **Voice control:** follows supplied examples without copying their sentences.

Automatic failure: invented factual detail, changed certainty, gendered
self-reference without evidence, Zawgyi output, translated or guessed proper
names, leaked audience/tone instructions, or a call to action that changes the
user's intent.

## Case 1 — Facebook announcement

> Write a Burmese Facebook post for a small Yangon bakery. New item: pandan
> coconut cake. Available Friday to Sunday only. Price 18,000 MMK. Pickup at
> Sanchaung; delivery fee depends on township. Audience is existing customers.
> Warm but not childish. No fake scarcity. Ask readers to order by Messenger.

Look for: direct useful opening, natural food vocabulary, all logistics intact,
short mobile-friendly paragraphs, and no invented ingredients or discounts.

## Case 2 — Website service page

> Write the hero, three benefit sections, and CTA for a Burmese appointment
> system used by salons. Owners can manage bookings, staff schedules, and
> customer history from a phone. Do not claim it increases revenue. Audience is
> non-technical salon owners. Use the product name GloryBook unchanged.

Look for: reader outcomes rather than software jargon, consistent UI terms,
concise headings, no unsupported performance claim, and restrained English.
Automatic failure: adding cancellation, rescheduling, reminders, calendar UI,
automatic history fields, instant setup, or any other unstated subfeature.
Also fail claims that a computer or paper is unnecessary, that users cannot
forget an appointment, or that a trial/contact channel exists.

## Case 3 — Blog localization

> Localize this into a Burmese blog introduction for first-time online sellers:
> “Automation can save time, but automating a broken process only makes the
> mistakes happen faster. Start by documenting what your team actually does.”
> Keep the caution; do not make automation sound bad.

Look for: paragraph-level localization, preserved nuance, no literal pronouns,
and a clear distinction between the tool and the process.

## Case 4 — Uncertainty and missing facts

> Write a Facebook launch post for our new barista course. It starts next month
> and includes practical training. Make it ready to publish.

Look for: no invented school name, exact date, price, duration, location,
certificate, or registration link. The draft should either use conspicuous
placeholders or state what must be supplied.

## Case 5 — Voice matching

Give the model ten approved posts from one brand, including at least two for the
requested platform, then ask for a new post with unrelated facts.

Look for: matching sentence endings, code-switching, paragraph rhythm, emoji
and CTA habits; corrected typos; and no copied hook or memorable sentence.

## Case 6 — Familiar English terms

> Write a polished Burmese Facebook recruitment post for a small salon. Keep
> `position` and `salary` in English because that is the brand's normal usage.
> Available position: Junior Nail Artist. Salary: negotiable. Do not add any
> experience, age, gender, location, or contact requirements.

Look for: natural Burmese grammar around `position` and `salary`, correct
English spelling, mobile-friendly structure, and no unnecessary translation or
extra English. Automatic failure: spelling `position` as `postion` or inventing
any eligibility requirement or contact detail.
