---
name: myanmar-writing
description: Write, rewrite, edit, or localize natural Burmese content for Facebook posts, website copy, and blog posts. Use when the user wants Burmese that sounds locally written rather than literally translated, including mixed Burmese-English copy and adaptation to a supplied brand voice. Do not use for simple word-level translation or Burmese language lessons.
---

# Myanmar Writing

Write for the reader and platform, not sentence by sentence from another
language. The result should sound as if a fluent Burmese writer created it for
that audience.

## Start from the brief

Infer these when the request already makes them clear:

- purpose: inform, explain, persuade, announce, or sell;
- audience and their familiarity with the subject;
- format: Facebook post, website copy, or blog post;
- voice: conversational, polished, formal, playful, or a supplied brand voice;
- facts that must remain exact, plus the intended call to action.

Separate **publishable facts** from **writing instructions**. Audience, tone,
platform, length, and phrases such as "warm but not childish" guide the draft;
they are not claims to repeat in the published copy. Likewise, background about
the business or reader should appear only when it is relevant content.

Before drafting, make a silent fact lock from the brief:

- copy every proper name, place, product name, number, price, date, link, and
  claim exactly;
- preserve how certain or limited each claim is;
- if the user has not supplied a Burmese form of a proper name, keep the
  original form rather than guessing a translation or transliteration;
- do not infer ingredients, features, sensory qualities, benefits, scarcity,
  eligibility, price units, package sizes, or conditions from a product name
  or category. If a price has no unit such as per piece, box, person, or month,
  state only the supplied price.

A broad capability does not authorize plausible subfeatures. For example,
`manage bookings` does not prove cancellation, rescheduling, reminders, a
calendar view, real-time updates, or automatic conflict handling. Rephrase the
supplied capability for the reader, but do not expand it into imagined product
behavior. Words such as `automatic`, `instant`, `anywhere`, `never again`, and
`all in one` are claims and require source support.

Compare the final draft to this lock before delivery. Every changed or added
fact is a defect unless the user explicitly authorized the change.

Ask only for information whose absence would materially change the copy. Never
invent prices, dates, claims, qualifications, links, quotations, or product
features. When a complete draft is still useful, omit optional missing details
or use conspicuous placeholders such as `[ရက်စွဲ]`, then list what needs filling
in after the draft.

If the user supplies previous posts or brand examples, treat them as the
strongest style evidence. Read [references/voice-matching.md](references/voice-matching.md)
before drafting. Match recurring choices, not typos or one-off phrases.

## Choose the right mode

- **Facebook:** Read [references/formats.md](references/formats.md#facebook-posts).
- **Website:** Read [references/formats.md](references/formats.md#website-copy).
- **Blog:** Read [references/formats.md](references/formats.md#blog-posts).
- **Translation or localization:** Also read
  [references/natural-burmese.md](references/natural-burmese.md#localizing-from-english).
- **Mixed Burmese-English or uncertain terminology:** Also read
  [references/terminology.md](references/terminology.md).
- For a new draft, difficult rewrite, or quality review, use the compact
  patterns in [references/examples.md](references/examples.md). Do not copy
  their wording unless it belongs to the user's source.

## Writing principles

1. Preserve the meaning and factual commitments. Improve expression without
   changing the offer, certainty, point of view, or spelling of locked facts.
2. Use natural Burmese clause order and rhythm. Rebuild translated sentences
   at paragraph level instead of mirroring English syntax.
3. Prefer specific, ordinary wording over inflated phrases, but draw every
   specific from the brief or approved source. If the brief is sparse, concise
   copy is correct; never invent scenarios, pain points, or outcomes to make it
   feel richer. Do not add generic openings, motivational filler, or a sales
   pitch the user did not request.
4. Vary sentence endings and sentence length. Avoid long runs of `ဖြစ်ပါတယ်`,
   `ရှိပါတယ်`, `ပြုလုပ်နိုင်ပါတယ်`, or literary `...သည်` constructions unless
   the chosen voice genuinely calls for them.
5. Usually omit pronouns when context identifies the subject. Never invent the
   writer's gender by choosing `ကျွန်တော်` or `ကျွန်မ`. Do not repeatedly call
   the reader `သင်` or `မိတ်ဆွေ` unless that is established brand language.
6. Code-switch according to the audience. Keep brand names, product names,
   commands, and familiar specialist terms in their normal form. Also keep an
   ordinary English word when it is the audience's established everyday term;
   do not force an uncommon Burmese replacement merely for language purity.
   Use the standard English spelling unless the exact text is a locked name,
   identifier, quotation, or user-required form. Translate ordinary ideas when
   Burmese is more natural. There is no fixed English percentage to hit.
7. Use Unicode Burmese. Preserve names, figures, links, and identifiers exactly
   unless the user asks for conversion. Do not convert all digits merely to
   make the draft look more Burmese.
8. Formatting must serve the platform. Emoji, hashtags, bullets, headings, and
   calls to action are optional tools, not mandatory decorations.

Read [references/natural-burmese.md](references/natural-burmese.md) whenever a
draft sounds translated, stiff, repetitive, or uncertain.

## Quality pass

Before delivering, silently check:

- Would a fluent Burmese reader say it this way aloud?
- Does each paragraph do useful work, with no generic AI filler?
- Is the level of politeness consistent with the audience and brand?
- Are English terms present because readers use them, not because the source
  happened to be English?
- Are all facts, numbers, names, links, and claims faithful to the brief?
- Did any audience, tone, or workflow instruction leak into the published copy?
- Did the draft add an ingredient, quality, benefit, or condition that the
  source did not state?
- Did a broad capability turn into an invented UI, workflow, subfeature, or
  guaranteed outcome?
- Does the opening earn attention without clickbait, and does the ending fit
  the purpose rather than forcing a call to action?
- Is the content easy to scan on its target platform?

For file-based drafts, the optional validator catches mechanical issues only:

```bash
python3 <skill-base>/scripts/validate.py <file> --format facebook|web|blog
```

Do not treat a clean validator result as proof that the Burmese sounds native.
Use the quality pass and, when available, the user's approved examples.

## Delivery

Return the finished Burmese copy first, ready to paste. Do not announce an
internal register classification and do not put ordinary social or web copy in
a code fence. Add a short note after the draft only for assumptions,
placeholders, factual concerns, or an explicitly requested explanation.

When the brief is complete and the user asks only for copy, return only the
copy. Do not append a separator, compliance report, fact-lock summary,
validator result, explanation of tone choices, or reassurance that instructions
were followed.

Missing optional implementation details such as a CTA URL or button target are
not a reason to append a note. Use neutral visible copy that does not assume a
trial, signup, download, purchase, or contact channel.

When editing existing Burmese, provide the clean revision. Explain changes only
when the user asks for an edit rationale or when the source meaning is
ambiguous.
