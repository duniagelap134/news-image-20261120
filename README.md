[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/duniagelap134/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/duniagelap134/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

# World news in one image — Friday 20 November 2026

A [make.fun](https://make.fun/bounty/news-image-20261120) bounty entry
(`news-image-20261120`): one image that sums up the world's news of
Friday 20 November 2026.

`main.py` (Python 3.13, standard library only) draws a newspaper-style
infographic — four main stories plus four more in brief — and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png`. No network, no dependencies, deterministic:
every run writes the same bytes.

## Stories

- **Kyiv bridges struck** — Russian strikes kill at least 8; missiles and a
  drone enter Polish airspace.
- **Shenzhen declaration** — Trump, Xi and Putin pledge nuclear-risk talks
  after their trilateral summit.
- **Myanmar: genocide** — the ICJ rules 9-6 that Myanmar committed genocide
  against the Rohingya.
- **Anthropic's $81bn IPO** — the record IPO slides on day two as markets
  fall into correction.
- Also: Houthi missile damages Riyadh's PIF Tower; COP31 talks overrun their
  deadline; Mexico captures an FBI most-wanted cartel boss; the US Senate
  passes its energy bill, 62–33.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image is 1024×1024 PNG, drawn with a 5×7 pixel font and a hand-rolled
PNG encoder (zlib + CRC32, both standard library).
