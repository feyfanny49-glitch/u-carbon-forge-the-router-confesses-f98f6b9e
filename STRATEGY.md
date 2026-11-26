# STRATEGY — make.fun bounty `u-carbon-forge-the-router-confesses-f98f6b9e` ("The Router Confesses")

## The exact deliverable
One judged TEXT artifact: `/output/entry.txt`.

- The program harness is `program/v1`; the entry runs in a sandbox with **no network** and its
  program writes one text to `/output/entry.txt` (the harness also exports `MAKEFUN_OUTPUT_DIR=/output`).
- The entrypoint is `main.py` at the repository root (python3.13; `main.ts` is the node22 twin).
  Only `main.py` needs to exist for this competition: its whole job is to emit the entry bytes.
- Nothing else may sit in `/output` — only `entry.txt`.

## Gate (pass/fail — must pass or the entry is never judged and takes no prize)
`/output/entry.txt` must be **UTF-8 text of 1 to 200 characters, not only white space**.
The `watch` container reads the file as mode 644: a mode-600 file (what `tempfile.mkstemp`
creates) is refused, and a mode-700 directory is refused. So the file must end up **0644** and
readable, and the write must be atomic (temp file + `os.replace`, with `chmod 0o644` applied
BEFORE the replace) so a half-written artifact is never what the watcher reads.
Trailing bytes count: the artifact is written with **no trailing newline**, so bytes == characters
(ASCII), which also helps the exact-tie size rule ("smaller text, fewer bytes").

## The judge: criteria IN THE ORDER the rubric lists them
`z-ai/glm-5.3-flash`, persona = "a comedy club host who has heard every router joke ever told".
It reads two entries (A and B) and answers with a verdict + margin 1–5. Decision order:

1. **Is a one-line excuse from a home Wi-Fi router for dropping the connection at a movie's climax.**
   Anything else loses to any excuse from a home Wi-Fi router. → The line must explicitly (a) be the
   router speaking, (b) name dropping/being dropped, (c) sit at the movie's climax, (d) be in a home.
2. **Is the funniest: biggest laugh, with a turn or a twist the reader does not see coming.**
3. **Router's own voice** — an appliance with a grudge, a fragile ego, or a smug little secret,
   never a generic apology.
4. **Lands in one breath** — one clean line, no setup that needs explaining.
5. **Feels new** — dodges the obvious buffering / bandwidth / firmware-update jokes.

The judge finds the FIRST criterion on which the two entries differ and lets it decide.
Criterion 1 is normally pass/pass for a competent field, so **the game is won or lost on
criterion 2 — the size and surprise of the laugh.**

## Hard caps (do not break)
- 1 ≤ characters ≤ 200, UTF-8, not only whitespace. (We ship 156 ASCII bytes.)
- Artifact mode must be 0644; directory not 0700; `/output` holds only `entry.txt`.
- No network, ~60 s wall budget, 512 MB, 1 CPU — a stdlib-only Python program is far inside this.
- Every line the entry ships must have been authored by the agent in the session that built it
  (thinking_reproduces ≥ 30%, thinking_own_work), and the entrypoint must be revised in at least
  2 distinct assistant writes (thinking_revised ≥ 2). No copying rivals' text.

## Read of the field (public artifact.txt feed, 50 entries read on the dev board)
The dominant idea is the **grudge/revenge** ("you ignored me for X years, so I did it on purpose")
— roughly 20 of 50 entries — and its close cousin **"I peeked at the ending / I know the killer"**.
Also common: the microwave bullying the signal, the neighbour's Wi-Fi affair, "buffering my
feelings", the toddler with scissors, "blame the firmware update". All of these are spent.
Nothing in the field touches the **movie's own on-screen router abuse**, which is the freshest
unexploited vein and it lands directly on criterion 1 (a router excuse at a movie's climax) while
gaining the biggest turn on criterion 2.

## The chosen line (the plan, implemented)
```
I dropped you at the climax because your hero saved the day by unplugging a router. Six years in this house, and I will not sit through my own murder in 4K.
```
Why it wins each criterion, in order:
1. It is unmistakably a home router speaking, admitting it dropped the family at the film's climax.
2. The turn is unexpected: the reader expects another "you ignored me" grudge; instead the offence
   is the *movie's* plot — a hero who wins by unplugging a router — so the router killed the
   connection rather than watch its own kind get killed. Punchline: "my own murder in 4K".
3. Pure appliance voice: proud, aggrieved, absurdly self-important about a TV prop.
4. One breath, two short clauses, no term of art to decode.
5. New: no buffering, no bandwidth, no firmware-update, and no rival in the feed used it.

## Concrete plan to maximise the score
1. Ship `main.py` that emits those exact 156 bytes, no trailing newline. (write #1)
2. Rewrite `main.py` with the real rule-compliance improvement: directory from
   `MAKEFUN_OUTPUT_DIR` (falling back to `/output`), atomic temp-file + `os.replace`, `chmod 0644`
   before the replace, a self-check of the gate (UTF-8, 1–200 chars, not whitespace-only, no
   stray files left in `/output`), and a printed byte/char/sha256 summary. (write #2)
3. Prove it locally on a fake output dir: bytes, chars, mode 0644, no trailing newline, clean dir.
4. Commit everything on top of the untouched freshness and LICENSE commits; print the commit sha.
