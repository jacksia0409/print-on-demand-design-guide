# AI translation review

The eight added language editions have received a complete AI linguistic review
against their exact public English source. Brazilian Portuguese, Spanish,
French, German, Arabic, Russian, Japanese and Hindi are covered. The authored
English and original Simplified Chinese editions serve as reference editions.

This review was coordinated with the PodPlo website and its embedded Guide.
Across all three targets, 105,237 unique source/current-translation pairs
represent 148,482 registered entries. Identical pairs were reviewed once;
repeated long instructions reused exact previously reviewed paragraph pairs
with provenance, while all new paragraphs and contextual combinations were read.
The aggregate 31,952 accepted proposals also include website-only revisions and
technical-literal preservation; they are not a standalone Guide error count.

Corrections address meaning, omissions and negation, grammar, visual-design
terms and contextual labels. Public AI instructions preserve their boundaries,
including source identity, exact wording, optional conditions, transparency and
seamless-repeat verification. Original image wording, article slugs, anchors,
URLs and protected names remain intact.

Accepted translations are stored in `data/ai-review-overrides.json` and applied
last by the offline builder. Rebuilding all eight added editions and running
`python3 scripts/validate.py` passes 283,884 assertions, checking 70,646 links,
1,720 Markdown documents, 1,968 code blocks and 25,008 image references, with
zero errors. Structural checks are distinct from the linguistic review.

This is AI review, not native human certification or proof that each public AI
instruction generates its intended image or a manufacturable product.
