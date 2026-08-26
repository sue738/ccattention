# ccattention 🧠

**How much of your attention did Claude Code actually cost you?**

Measuring an assistant by its token count or its uptime misses what you
actually spend. The cost you pay is **how many times you had to type** — and
how much of that typing was re-explaining, correcting, or chasing.

```
$ ccattention --days 7

期間          ｾｯｼｮﾝ    あなた  発話/ｾｯｼｮﾝ    私の通数    通/発話    読む分    自己訂正   状況確認   催促   差戻
2026-08-20     37    158       4.3     950     6.0    288    0.6%      0    0   78
2026-08-21     34    102       3.0     471     4.6    163    0.4%      0    0   37
2026-08-22     21     69       3.3     429     6.2    116    1.2%      1    0   43

  セッション = その日に実際に話した会話ウィンドウの数。
  これはセッションの長さであって、仕事の重さではない — 仕事単位は測れていない。
  負担そのものを見るなら自己訂正・差戻の列の方が直接的。
```

## What each column means

| column | meaning |
|---|---|
| ｾｯｼｮﾝ | conversations you actually spoke in that day |
| あなた | your utterances (main loop only; subagents excluded) |
| 発話/ｾｯｼｮﾝ | how long an average conversation ran |
| 私の通数 / 通/発話 | how much the assistant said back, per turn |
| 読む分 | rough minutes of assistant text you had to read |
| 自己訂正 | share of assistant turns that walked back its own previous answer |
| 状況確認 / 催促 | times you had to ask "is it running?" or "why did you stop?" |
| 差戻 | times a Stop hook bounced the assistant back |

## On the unit — read this before trusting 発話/ｾｯｼｮﾝ

An earlier version split the day into "用件" (tasks) using a 90-minute
idle gap. That threshold produced the answer rather than measuring it: a day
spent typing continuously never crossed it, so 239 utterances collapsed into
"one task" and the ratio exploded; a quiet day yielded zero tasks and the
ratio was undefined. Measured over 30 days it swung with CV 1.15 (range
1.5–239) and was undefined on 2 of 31 days.

Sessions have no tuning parameter — the count is an observable fact. Same 30
days: CV 0.56, range 3.0–50, defined every day.

**But making it computable changed the question.** A session is not a unit of
work, so one session covering three topics reads long and one topic split
across two sessions reads short. "How many turns to finish one job" is still
not measured here. 自己訂正 and 差戻 are raw counts that don't depend on any
segmentation, so lean on those when you want the friction itself.

## Install

```sh
npm install -g ccattention
```

**Requires `python3` on your PATH.** Unlike the sibling tools, this one is a
single Python script rather than Node — npm is only being used to put it on
your PATH. macOS ships python3; on Linux install it from your package manager.

## Security & trust

- **No dependencies** — Python standard library only, one file you can read
- **Fully local** — reads `~/.claude/projects/**/*.jsonl` and nothing else, no
  network calls, no telemetry
- **Read-only** — it never modifies a transcript
- Paranoid path: `git clone https://github.com/sue738/ccattention.git && python3 ccattention/bin/ccattention`

## License
MIT
