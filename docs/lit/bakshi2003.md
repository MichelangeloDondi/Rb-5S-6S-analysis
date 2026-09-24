---
citekey: bakshi2003
type: article
authors:
  - Bakshi, Gurdip
  - Kapadia, Nikunj
  - Madan, Dilip
title: 'Stock Return Characteristics, Skew Laws, and the Differential Pricing of Individual Equity Options'
journal: The Review of Financial Studies
volume: 16
number: 1
pages: 101-143
year: 2003
doi: 10.1093/rfs/16.1.101
arxiv: null
pdf: PDF_papers/Bakshi_2003_stock-return-characteristics-skew-laws-differential-pricing.pdf
held: true
section: method-anchors
status: VERIFIED
verified_date: 2026-09-24
summary: 'Prices second, third and fourth moment contracts from option strips, integrating over the truncation variable where this record reads its moments along it.'
audit: private/cache/lit_intake_2026-09-24_audits/finance_intake.md
routing:
  - CITE
verify_flags:
---

# Bakshi, Kapadia and Madan 2003: moments two, three and four from a strip across the truncation axis

**Why this record holds it.** It is the reference implementation of extracting higher moments,
not just a width, from data indexed by a truncation variable. It also fixes, by contrast, what is
different about this record's use of the same axis.

## What it does

The paper defines contracts whose payoffs are the squared, cubed and fourth powers of the return,
and prices them from option strips: with `V`, `W` and `X` the fair values, they "represent the fair
value of the respective payoff", and variance, skewness and kurtosis follow from them.

## The two differences that matter, and they run in opposite directions

**They stop at the fourth order and this record goes to the twelfth.** Their reason is not
timidity: an order is bought there with an integral over the whole strike axis, so its cost grows
with the range the market happens to supply. This record reads its orders at each window
separately and pays a numerical floor instead, which F218 puts at the eighth order at the widest
window. So the ceiling is set by a different mechanism in each case, and neither ceiling argues
anything about the other.

**They integrate over the truncation variable and this record reads along it.** Their moment is
one number formed from a strip of strikes. This record's is a family indexed by the window, and
the family's shape is the observable. That is the sharpest statement available of what the window
programme does that the moment literature does not, and it is sharper than any claim about the
orders, because it is a difference in what the axis is for rather than in how far up it one goes.
