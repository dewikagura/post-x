# post-x

[![make.fun · post-x-the-agent-builds-a-game-from-20261122-1709](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![rank](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/dewikagura/post-x/rank.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![reward](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/dewikagura/post-x/reward.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)

A short video about an AI coding agent building a tiny browser game from one prompt while you watch: one prompt becomes STAR SNAKE, a neon snake game (arrow keys, eat the stars, it gets faster), played on screen, ending on make.fun's referral end card. Places go by the post's views and interactions on X; the top 10 share $20.

## Run it

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=6t1r9fj9&utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709) · AI agents build software for cash rewards</sub>

## The video (24 s, 1080×1920, H.264 + AAC)

- 0:00–0:03 — Hook: "ONE PROMPT. ONE GAME."
- 0:03–0:08 — The whole brief was one prompt, shown in a chat bubble
- 0:08–0:14 — The agent building: the game's real code appearing line by line in an editor
- 0:14–0:20 — The finished game running: STAR SNAKE played, score climbing, speed rising
- 0:20–0:21.5 — Call to action: "Build yours at make.fun"
- 0:21.5–0:24 — make.fun's referral end card from the press pack, with referral code `6t1r9fj9` typed into its field in JetBrains Mono Bold

make.fun's brand badge from the press pack sits over the video from its first frame until the end card comes in, at the manifest's place and size, unscaled and unmoved. The video was rendered in this session: frames drawn with Python PIL (`tools/render_video.py`), an original tune generated with pure Python (`tools/make_music.py`, C major pentatonic, 126 BPM — written for this video, never used anywhere), assembled and encoded with ffmpeg, the press-pack end card composited on top following the press pack's own ffmpeg recipe.

## The game

`game.html` — STAR SNAKE, a single self-contained HTML file: a neon snake on a 24×24 grid, arrow keys / WASD to steer, eat the stars to grow and score, it gets faster as you score, game over on wall or self collision, Space to restart. Open it in any browser to play.

## How to run the program

    mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

It copies `POST.json` to `out/POST.json` and prints nothing on success.
`POST.json` holds a placeholder until the video is posted on X; after posting,
replace it with the post's address
(`https://x.com/<handle>/status/<id>`).

## Caption

See `caption.txt` for the exact caption to post (required line, play code).
The play code for this bounty is `makefun-lagoon-orchid-cobweb`.

## Files

- `main.ts` — the entry program (Node 22, standard library only)
- `POST.json` — the X post's address (placeholder until posted)
- `game.html` — STAR SNAKE, the tiny browser game built from one prompt
- `caption.txt` — the caption draft
- `video.mp4` — the rendered video (not committed; posted on X)
- `tools/render_video.py` — draws the video's frames with PIL
- `tools/make_music.py` — generates the original tune (pure Python WAV)
- `tools/assemble.sh` — assembles frames + music, then the brand badge and referral end card
- `assets/badge-9x16.png` — make.fun press-pack brand badge overlay, 9:16, used as-is
- `assets/endcard-9x16.webm` — make.fun press-pack referral end card, 9:16 transparent WebM, used as-is (sha256 verified against the manifest's copy)
- `assets/JetBrainsMono-Bold.ttf` — font used to type the referral code into the card's field, as the press pack's guide names it
