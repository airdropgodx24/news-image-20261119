# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/airdropgodx24/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/airdropgodx24/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A program that draws a newspaper front page summing up the world news of Thursday 19 November 2026 and writes it to /output/entry.png.

The front page leads with the International Court of Justice ruling that Myanmar committed genocide against the Rohingya, and the first-ever Trump-Xi-Putin trilateral summit in Shenzhen. It also covers the COP31 deadlock in Antalya, the Strait of Hormuz tanker crisis, the GTA VI launch, unrest in Bangladesh, the Crimea Bridge strike, Hakeem Jeffries becoming set to be the first Black US House Speaker, a record $190.4 million Van Gogh sale, the Anthropic IPO, the day's markets, and a briefs column (Voyager 1, the word of the year, Haiti, moon-soil potatoes, and more).

`main.py` uses only the Python standard library: it renders the whole page with its own built-in bitmap font and drawing primitives, and encodes the result as a deterministic 1024x1024 PNG.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---
<sub>Entered on [make.fun](https://make.fun/?ref=ty7xpzdw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
