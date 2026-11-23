#!/bin/bash
# Assemble the post-x video: frames + music -> clip, then the press pack's
# brand badge (from frame 0 until the end card) and referral end card
# (last 2.5 s, referral code typed in) -> video.mp4.
# The end-card part follows the press pack's own ffmpeg recipe
# (https://make.fun/press/llms.txt): transparent VP9 card over the last
# 2.5 s, clip blurred (sigma 28) and desaturated under it, code in
# JetBrains Mono Bold 62 px, ink #191419, from x=210 centred on y=1271,
# shown once the field rests (1.433 s into the card).
set -e
cd "$(dirname "$0")/.."

CODE=6t1r9fj9
FONT=assets/JetBrainsMono-Bold.ttf
CARD=assets/endcard-9x16.webm
BADGE=assets/badge-9x16.png
W=1080 H=1920 LEN=2.5 REST=1.433 CX=210 CY=1232 CW=5 CH=78 MID=1271 SIZE=62
D=24.0
T=$(awk "BEGIN{print $D-$LEN}")

echo "pass 1: frames + music -> clip.mp4"
ffmpeg -y -v error -framerate 30 -i frames/frame_%04d.png -i tools/music.wav \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -r 30 -c:a aac -b:a 160k \
  -shortest clip.mp4

echo "pass 2: badge + end card + code -> video.mp4 (T=$T)"
ffmpeg -y -v error -i clip.mp4 -c:v libvpx-vp9 -i "$CARD" -i "$BADGE" \
  -filter_complex "\
[0:v]scale=$W:$H:force_original_aspect_ratio=increase,crop=$W:$H,setsar=1,fps=60,format=yuva420p,split[clip][soft];\
[soft]gblur=sigma=28,eq=saturation=0.35,fade=t=in:st=$T:d=0.8:alpha=1[soft];\
[clip][soft]overlay[bg];\
[1:v]format=yuva420p,setpts=PTS-STARTPTS+$T/TB[card];\
[bg][card]overlay=eof_action=pass[bg2];\
[2:v]format=yuva420p[badge];\
[bg2][badge]overlay=enable='between(t,0,$T)'[bg3];\
[bg3]drawbox=x=$CX-2:y=$CY-2:w=$CW+4:h=$CH+4:color=white:t=fill:enable='gte(t,$T+$REST)',\
drawtext=fontfile=$FONT:text=$CODE:fontsize=$SIZE:fontcolor=0x191419:x=$CX:y=$MID-(ascent-descent)/2:enable='gte(t,$T+$REST)'[v]" \
  -map '[v]' -map '0:a?' -c:v libx264 -pix_fmt yuv420p -crf 18 \
  -c:a aac -movflags +faststart video.mp4

echo "frames for checking"
ffmpeg -y -v error -sseof -0.1 -i video.mp4 -frames:v 1 check-last.png
ffmpeg -y -v error -ss 1 -i video.mp4 -frames:v 1 check-first.png
ffmpeg -y -v error -ss 5 -i video.mp4 -frames:v 1 check-mid.png
ffmpeg -y -v error -ss 11 -i video.mp4 -frames:v 1 check-code.png
ffmpeg -y -v error -ss 17 -i video.mp4 -frames:v 1 check-game.png
ffmpeg -y -v error -ss 22.9 -i video.mp4 -frames:v 1 check-end.png
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,codec_name,duration -of default=noprint_wrappers=1 video.mp4
sha256sum video.mp4
