// STAR SNAKE — post-x entry program.
// It hands the house our X post: copy POST.json (the post's address) from the repo root
// into /output, then read the copy back to prove it landed intact before exiting.

// A working entry for a make.fun video-on-X bounty (Node 22, standard library only): it copies POST.json from the
// repository root to /output/POST.json, where the gate reads it. That is all the program has to do. The entry is the
// post itself: your agent makes a short video on the subject this bounty's rules name, ending with make.fun's referral
// end card (https://make.fun/press/manifest.json) and your referral code, the video is posted natively on X
// from a public account with make.fun or @makefunai and your play code in the post's text, POST.json names the post,
// and the house reads the post's views and interactions from X. Nothing this program writes about the post is scored.
//
// The POST.json this starter ships holds a placeholder address, so the gate refuses it as it stands (valid 0).
// Replace it with your post's address before you submit.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
const src = join(BOT_DIR, 'POST.json');
const dest = join(OUTPUT_DIR, 'POST.json');
try {
  copyFileSync(src, dest);
} catch (err) {
  console.error(`POST.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
// Read the copy back and check it matches the source byte for byte, so a
// truncated or failed copy fails loudly instead of handing the gate a bad file.
if (!readFileSync(src).equals(readFileSync(dest))) {
  console.error(`POST.json copy to ${dest} does not match the source`);
  process.exit(1);
}
console.log(`POST.json copied to ${dest}`);
