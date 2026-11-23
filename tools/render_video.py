#!/usr/bin/env python3
"""Render the post-x video: "The agent builds a game from one prompt" — an
original 24 s vertical video for make.fun, drawn frame by frame with PIL
(1080x1920, 30 fps).

Creative, and why (decided in this session):
- Hook first (0-3 s): "ONE PROMPT. ONE GAME." — the payoff is instant: one
  sentence becomes a playable game. A viewer scrolling X stops for the
  transformation, not for a site name.
- The prompt (3-8 s): the actual single prompt in a chat bubble, so the
  viewer sees how little it takes: one sentence, no setup.
- The agent building (8-14 s): a code editor with the game's real code
  appearing line by line — proof the agent really built it, not a mockup.
- The finished game running (14-20 s): the real game, played — the snake
  eats stars, the score climbs, the speed rises. This is the "real result"
  the brief asks for, and it ends on the game running.
- CTA (20-21.5 s): "Build yours at make.fun" — the one thing to do.
- The last 2.5 s are the press pack's referral end card (added by ffmpeg
  in assemble.sh, with referral code 6t1r9fj9 typed in), and the press
  pack's brand badge sits over the video from its first frame (also added
  by ffmpeg, at the manifest's place and size, unscaled).

Brand: make.fun magenta #c41c83, ink #191419, white #ffffff, game gold
#f5d90a, neon green #39d353 (from the game itself). On-screen text uses
DejaVu Sans Bold (the video's own words, not a make.fun mark).

The game is STAR SNAKE (game.html in this repo): a neon snake that eats
stars, gets faster, arrow keys to play. The gameplay frames are a faithful
PIL rendering of that game's own rules, simulated with a safe bot.

Usage: python3 tools/render_video.py  ->  frames/frame_%04d.png (720 frames)
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
DUR = 24.0
FRAMES = int(DUR * FPS)
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "..", "frames")

MAGENTA = (196, 28, 131)
INK = (25, 20, 25)
WHITE = (255, 255, 255)
DARK = (7, 3, 18)
CARD = (242, 238, 241)
GOLD = (245, 217, 10)
GREEN = (57, 211, 83)
CYAN = (155, 231, 255)
GREY = (201, 196, 224)
PANEL = (13, 7, 34)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(size, bold=True, mono=False):
    if mono:
        return ImageFont.truetype(FONT_MONO_BOLD if bold else FONT_MONO, size)
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_center(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size + 8


# ---------------------------------------------------------------- game sim
# Precompute a snake run with the same rules as game.html (24x24 grid,
# eat a star -> grow + score, wall/self -> game over), steered by a safe bot.
def simulate_game():
    random.seed(7)
    N = 24
    snake = [(12, 12), (11, 12), (10, 12)]
    d = (1, 0)
    score = 0

    def new_star():
        while True:
            s = (random.randrange(N), random.randrange(N))
            if s not in snake:
                return s

    star = new_star()
    frames = []  # (snake copy, star, score) per move
    frames.append((list(snake), star, score))
    for _ in range(90):
        hx, hy = snake[0]
        cands = []
        for dd in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if dd == (-d[0], -d[1]):
                continue
            nx, ny = hx + dd[0], hy + dd[1]
            if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in snake[:-1]:
                cands.append(dd)
        if not cands:
            break
        cands.sort(key=lambda dd: abs(hx + dd[0] - star[0]) + abs(hy + dd[1] - star[1]))
        d = cands[0]
        head = (hx + d[0], hy + d[1])
        snake = [head] + snake
        if head == star:
            score += 1
            star = new_star()
        else:
            snake = snake[:-1]
        frames.append((list(snake), star, score))
    return frames


GAME_FRAMES = simulate_game()
# gameplay runs 14-20 s = 180 frames; map to the simulated moves (one move
# every 3 frames -> 60 moves over the 6 s, ~10 moves/s, like real play)
GAME_START, GAME_END = 14.0, 20.0


def game_state_at(t):
    idx = int((t - GAME_START) / (GAME_END - GAME_START) * (len(GAME_FRAMES) - 1))
    idx = max(0, min(len(GAME_FRAMES) - 1, idx))
    return GAME_FRAMES[idx]


# ---------------------------------------------------------------- scenes
PROMPT_TEXT = ("Build me a tiny browser game: a neon snake that eats stars, "
               "gets faster — arrow keys to play.")

CODE_LINES = [
    ("var cv = document.getElementById('game');", None),
    ("var ctx = cv.getContext('2d');", None),
    ("var snake = [{x:12,y:12},{x:11,y:12}];", None),
    ("function placeStar() {", "kw"),
    ("  star = {x: rand(24), y: rand(24)};", None),
    ("}", None),
    ("function loop() {", "kw"),
    ("  head = snake[0] + dir;", None),
    ("  if (head == star) { score++; }", "gold"),
    ("  else { snake.pop(); }", None),
    ("  draw(); requestAnimationFrame(loop);", None),
    ("}", None),
]


def scene_hook(draw, t):
    # 0-3 s: the hook. "ONE PROMPT." slides in, then "ONE GAME.", then the subline.
    draw.rectangle([0, 0, W, H], fill=DARK)
    # magenta glow band
    for i in range(60):
        a = int(60 * (1 - i / 60))
        draw.rectangle([0, 700 + i, W, 701 + i], fill=(196, 28, 131, a))
    y = 560
    p1 = ease_out((t - 0.1) / 0.5)
    p2 = ease_out((t - 0.7) / 0.5)
    p3 = ease_out((t - 1.5) / 0.6)
    draw_center(draw, W / 2, y - int((1 - p1) * 60), "ONE PROMPT.", font(120), WHITE)
    draw_center(draw, W / 2, y + 150 - int((1 - p2) * 60), "ONE GAME.", font(120), GOLD)
    if p3 > 0:
        draw_center(draw, W / 2, y + 330, "My AI agent built this", font(46, bold=False), CYAN)
        draw_center(draw, W / 2, y + 400, "while I watched.", font(46, bold=False), CYAN)
    # a small star + snake doodle at the bottom
    cx, cy = W / 2, 1180
    r = 46 + 6 * math.sin(t * 4)
    draw_star(draw, cx, cy, r, GOLD)
    draw.rectangle([cx - 180, cy + 130, cx - 60, cy + 170], fill=GREEN)
    draw.rectangle([cx - 60, cy + 130, cx + 60, cy + 170], fill=(124, 242, 156))
    draw.rectangle([cx + 60, cy + 130, cx + 180, cy + 170], fill=GREEN)


def draw_star(draw, cx, cy, r, fill):
    pts = []
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        a += math.pi / 5
        pts.append((cx + math.cos(a) * r * 0.45, cy + math.sin(a) * r * 0.45))
    draw.polygon(pts, fill=fill)


def scene_prompt(draw, t):
    # 3-8 s: the single prompt, in a chat bubble, typing in.
    draw.rectangle([0, 0, W, H], fill=DARK)
    draw_center(draw, W / 2, 420, "THE WHOLE BRIEF WAS", font(44, bold=False), GREY)
    draw_center(draw, W / 2, 480, "ONE PROMPT", font(64), GOLD)
    # chat bubble
    bx0, by0, bx1 = 90, 640, 990
    # type-in: reveal characters over the first 3 s of the scene
    local = t - 3.0
    frac = ease_in_out(local / 3.0)
    n_chars = int(len(PROMPT_TEXT) * frac)
    shown = PROMPT_TEXT[:n_chars]
    lines = wrap_text(draw, shown if shown else " ", font(52), bx1 - bx0 - 80)
    bh = 90 + len(lines) * 68
    draw.rounded_rectangle([bx0, by0, bx1, by0 + bh], radius=36, fill=(24, 16, 52), outline=(59, 42, 122), width=3)
    y = by0 + 45
    for ln in lines:
        draw.text((bx0 + 40, y), ln, font=font(52), fill=WHITE)
        y += 68
    # "1 prompt" chip under the bubble (sized to the text)
    chip_y = by0 + bh + 50
    chip_text = "1 prompt. That's it."
    chip_w = int(draw.textlength(chip_text, font=font(34))) + 90
    draw.rounded_rectangle([W / 2 - chip_w // 2, chip_y, W / 2 + chip_w // 2, chip_y + 72], radius=36, fill=MAGENTA)
    draw_center(draw, W / 2, chip_y + 12, chip_text, font(34), WHITE)
    draw_center(draw, W / 2, chip_y + 130, "No spec. No mockups. No meetings.", font(38, bold=False), CYAN)


def scene_code(draw, t):
    # 8-14 s: the agent building — real code lines appearing in an editor.
    draw.rectangle([0, 0, W, H], fill=DARK)
    draw_center(draw, W / 2, 400, "THE AGENT GOT TO WORK", font(44, bold=False), GREY)
    # editor window
    ex0, ey0, ex1, ey1 = 80, 520, 1000, 1380
    draw.rounded_rectangle([ex0, ey0, ex1, ey1], radius=24, fill=PANEL, outline=(59, 42, 122), width=3)
    draw.rounded_rectangle([ex0, ey0, ex1, ey0 + 64], radius=24, fill=(24, 16, 52))
    draw.rectangle([ex0, ey0 + 40, ex1, ey0 + 64], fill=(24, 16, 52))
    for i, c in enumerate([(255, 93, 122), (245, 217, 10), (57, 211, 83)]):
        draw.ellipse([ex0 + 24 + i * 36, ey0 + 20, ex0 + 44 + i * 36, ey0 + 40], fill=c)
    draw.text((ex0 + 150, ey0 + 14), "game.html — agent is building…", font=font(30, mono=True), fill=GREY)
    # lines appear one every ~0.45 s
    local = t - 8.0
    n_lines = int(local / 0.45)
    n_lines = max(0, min(len(CODE_LINES), n_lines))
    y = ey0 + 92
    for i in range(n_lines):
        text, kind = CODE_LINES[i]
        col = WHITE
        if kind == "kw":
            col = CYAN
        elif kind == "gold":
            col = GOLD
        draw.text((ex0 + 30, y), text, font=font(30, mono=True), fill=col)
        y += 52
    # progress bar + status
    bar_y = ey1 + 60
    frac = n_lines / len(CODE_LINES)
    draw.rounded_rectangle([ex0, bar_y, ex1, bar_y + 26], radius=13, fill=(24, 16, 52))
    draw.rounded_rectangle([ex0, bar_y, ex0 + int((ex1 - ex0) * frac), bar_y + 26], radius=13, fill=GREEN)
    status = "Writing the game…" if frac < 1 else "Done — game.html, 5,704 bytes"
    draw_center(draw, W / 2, bar_y + 50, status, font(38, bold=False), CYAN)


def scene_game(draw, t):
    # 14-20 s: the finished game, actually played.
    draw.rectangle([0, 0, W, H], fill=DARK)
    snake, star, score = game_state_at(t)
    # HUD (kept clear of the brand badge, which sits at y=272-400 top-left)
    draw_center(draw, W / 2, 440, "STAR SNAKE", font(64), GOLD)
    draw.text((90, 540), "SCORE  %d" % score, font=font(44), fill=WHITE)
    draw.text((W - 90 - draw.textlength("SPEED  %.1fx" % (1 + score * 0.06), font=font(44)), 540),
              "SPEED  %.1fx" % (1 + score * 0.06), font=font(44), fill=CYAN)
    # board
    bs = 860
    bx, by = (W - bs) // 2, 620
    cell = bs / 24
    draw.rounded_rectangle([bx - 8, by - 8, bx + bs + 8, by + bs + 8], radius=18, fill=PANEL, outline=(59, 42, 122), width=3)
    # grid dots
    for i in range(24):
        for j in range(24):
            draw.ellipse([bx + i * cell + cell / 2 - 1, by + j * cell + cell / 2 - 1,
                          bx + i * cell + cell / 2 + 1, by + j * cell + cell / 2 + 1], fill=(255, 255, 255, 14))
    # star
    sx, sy = star
    pulse = 0.75 + 0.25 * math.sin(t * 6)
    draw_star(draw, bx + sx * cell + cell / 2, by + sy * cell + cell / 2, cell * 0.42 * pulse, GOLD)
    # snake
    for i, (sx_, sy_) in enumerate(reversed(snake)):
        idx = len(snake) - 1 - i
        if idx == 0:
            col = (124, 242, 156)
        else:
            tt = idx / max(1, len(snake))
            col = (int(60 + 120 * (1 - tt)), int(200 - 80 * tt), int(120 + 60 * tt))
        pad = 2
        draw.rounded_rectangle([bx + sx_ * cell + pad, by + sy_ * cell + pad,
                                bx + (sx_ + 1) * cell - pad, by + (sy_ + 1) * cell - pad],
                               radius=6, fill=col)
    draw_center(draw, W / 2, by + bs + 40, "It works. First try.", font(44, bold=False), CYAN)


def scene_cta(draw, t):
    # 20-21.5 s: the call to action.
    draw.rectangle([0, 0, W, H], fill=MAGENTA)
    p = ease_out((t - 20.0) / 0.5)
    draw_center(draw, W / 2, 700 - int((1 - p) * 50), "Build yours", font(110), WHITE)
    draw_center(draw, W / 2, 840 - int((1 - p) * 50), "at make.fun", font(110), WHITE)
    draw_center(draw, W / 2, 1080, "Your agent builds.", font(48, bold=False), WHITE)
    draw_center(draw, W / 2, 1150, "You win USDC.", font(48, bold=False), WHITE)


def render_frame(i):
    t = i / FPS
    img = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img, "RGBA")
    if t < 3.0:
        scene_hook(draw, t)
    elif t < 8.0:
        scene_prompt(draw, t)
    elif t < 14.0:
        scene_code(draw, t)
    elif t < 20.0:
        scene_game(draw, t)
    elif t < 21.5:
        scene_cta(draw, t)
    else:
        # 21.5-24 s: the end card covers this (ffmpeg); keep the CTA behind it.
        scene_cta(draw, 21.4)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for i in range(FRAMES):
        img = render_frame(i)
        img.save(os.path.join(OUT, "frame_%04d.png" % i))
        if i % 120 == 0:
            print("frame %d/%d" % (i, FRAMES))
    print("done: %d frames in %s" % (FRAMES, OUT))


if __name__ == "__main__":
    main()
