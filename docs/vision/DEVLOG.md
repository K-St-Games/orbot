# Session Devlog

Running log of substantive working sessions on Orbot/Hi-Orbit. Append a new dated entry
rather than replacing this file. Each entry should let a cold reader (human or agent) get
oriented fast: what happened, what it produced, and exactly where to look next.

---

## 2026-09-11 — Vision review, canonical article model, wiki bootstrap, Quill deploy diagnosis

**Closed by:** Claude (orbot repo session `session_016NniwJmNihXX8axgZNZMzJ`)

### Start here if picking this up cold

1. **This session's own thread is fully wrapped** — nothing of mine is pending action.
2. **Two other threads moved *underneath* this session, independently, after my last direct
   involvement.** I have not reviewed either of the newer states below — treat them as
   "known to exist, needs a fresh look," not "already checked."
3. The single most useful first step for a new session: re-fetch both repos' `main` and diff
   against the commit SHAs cited in this entry to see exactly what's new.

### What this session did

**1. Vision review** (orbot repo). Read the freshly-drafted `docs/vision/VISION.md` against
the older, stale deployment-pilot docs (`README.md`, `AGENTS.md`, `SOUL.md`,
`architecture.md`) and the earlier wiki-evolution proposal. Talked through four open
questions with the owner and recorded the resulting decisions in
[`docs/vision/VISION_FEEDBACK.md`](VISION_FEEDBACK.md):
- Full doc rewrite (`AGENTS.md` first) is a roadmap item, not done yet as of this session.
- **Canonical-first retrieval** — no full source-shaped "brain"; evidence-layer robustness
  deliberately left open pending real Google Drive access.
- **Safety is behavioral, not access-control** for MVP — a `safety_class`/`[safety]` tag on
  canonical content drives the agent to escalate rather than instruct; hazardous content
  stays fully readable by humans in the repo.
- **Discord/Hermes stays the primary surfacing interface**, but the loop must *feed* the
  repo (repair-log entry + draft improvement per resolved thread), or Orbot collapses back
  into "just a chatbot."

**2. Canonical article content model.** Landed 5 real Hi-Orbit source docs under
[`example_breakdowns/`](../../example_breakdowns/) and used them to design and stress-test a
three-band article shape (Operator / Maintenance / Engineering, operator-first, explicit
depth boundary), with mandatory basis-tagging (`[source]` / `[authored — review]` / `[gap]`
/ `[safety]` / `[sensitive]`) and a source-tier model (current / supporting / draft-intent)
for reconciling conflicting evidence rather than silently merging it. Prototyped three
articles in [`docs/vision/examples/`](examples/): Payphone (single clean source), Laser Maze
(three disagreeing sources — this is where the tier model earned its keep: the vibe-coding
notes' Mode B sequence directly contradicts the shipped v52 firmware), and COGS (the first
*system* article — centers on the puzzle↔COGS integration contract rather than
troubleshooting, and honestly scopes that COGS itself is undocumented in the corpus).
Generalized the shape into [`docs/vision/templates/puzzle-article-template.md`](templates/puzzle-article-template.md)
and an authoring-agent procedure,
[`docs/vision/templates/puzzle-authoring-prompt.md`](templates/puzzle-authoring-prompt.md).

**3. Bootstrapped the real `hi-orbit-wiki` submodule.** Got repo access, landed the three
prototype articles plus the template/prompt (co-located there so Hermes — which only has
wiki + Drive access, not this repo — can use them) as **`hi-orbit-wiki` PR #1**
(`claude/seed-first-drafts`), along with `meta/contradictions.md` and
`meta/unresolved-questions.md`. Wrote `meta/authoring-session-plan.md` — an evidence-coverage
map and procedure for the next authoring batch. Hermes executed it independently and pushed
6 more puzzle drafts (Battleship, Campfire, Dartboard, Light Chase, Simon Says, UFO Cube) plus
two evidence-ingestion batches. Reviewed that batch against the actual firmware source and
fixed a real correctness bug (Campfire's draft claimed the COGS completion signal was
disabled by an `#ifdef DEBUG_LOGGING` guard — backwards: `#ifdef` tests whether a macro is
*defined*, not its value, so the guarded code was actually compiling and running) plus a
mis-framed contradiction (UFO Cube's UC-1), consistency gaps (missing draft headers, an
inconsistent troubleshooting-table column), an unjustified `safety_class`, and some
over-applied `[sensitive]` tags. Pushed as `8bbef1d`.

**4. Diagnosed a live deployment bug** (unprompted pivot — the owner reported the Quill
documentation viewer still defaulting to its native "Narrative" interface instead of the
intended read-only repository view). Root-caused it as a **deploy gap, not a code gap**: the
fix was real, independently browser-verified, and pinned at `vendor/kst-beta-ide@7c9c113`
on `main`, but `single-compose/Dockerfile.orbot-quill-web` `COPY`s the fixed frontend into
the nginx image at *build* time — so nothing changes on a running host until that image is
rebuilt and restarted. `feedback.md`'s own review explicitly listed "Docker/Compose image
build and clean restart" as a still-open host gate, and the PR merged into `main` anyway
despite the review's "do not merge yet." Also flagged that `CURRENT_TASK.md` is internally
self-contradictory (references both `1057eae` and `7c9c113` as "the" final commit; states
141 tests where the real count is 142) — exactly the reconciliation the review asked for,
not done. Presented options (rebuild commands / fix the doc / get direct endpoint access /
pull in `vendor/kst-beta-ide` to inspect the real fix); the owner was still weighing these
when the session moved to closing out — **see "Open thread" below, since it looks like this
got picked up directly on the real host afterward.**

### Repo state at close (verify freshness before trusting)

**orbot** — branch `claude/vision-doc-review-gfes51`, reset to match `origin/main` @
`6b667e6` ("Fix orbot.k-st.games redirect leaking internal port 8080"). This commit is
**new since the diagnosis above** — authored directly on the live host (Tailscale hostname
in the commit's author address) and its message cites a `curl -H "Host: orbot.k-st.games"`
check against the real domain. That's strong evidence someone continued the Quill
investigation for real after this session's diagnosis and made further verified progress —
**but this session has not confirmed whether the original "defaults to Narrative" symptom is
now actually resolved**, only that a closely-related redirect bug in the same nginx config
got found and fixed live. Also on `main` now, not reviewed by this session:
`MVP_ROADMAP.md` (root) and a substantially rewritten `AGENTS.md` — the two items this
session's own "what's next" discussion had flagged as the top priorities. Worth reading
before assuming they still need doing.

**hi-orbit-wiki** — `claude/seed-first-drafts` (PR #1, `8bbef1d`) **merged** to `main`. Three
further commits landed after that, none reviewed by this session:
`90485fb docs(evidence): add 260803 extraction batch; reconcile meta ledgers`,
`bbd6e5c docs(drafts): seed articles for the five uncovered puzzles, room book, ingestion
method`, `bf9c396 docs: apply metadata schema v0.1 frontmatter across the tree`. The "room
book" commit likely resolves the room/zone-assignment gap flagged repeatedly across every
draft this session touched — worth checking first.

### Open threads, prioritized

1. **Confirm live-endpoint state of the Quill/Narrative issue.** Check `orbot.k-st.games`
   directly, or read whatever happened on the host after `6b667e6`. If still broken, the
   rebuild-commands option from this session's diagnosis is the fastest path.
2. **Reconcile `CURRENT_TASK.md`** (root) — still stale/self-contradictory as of this
   session's last read (unchanged, "Last updated: 2026-07-15"). Low-risk doc fix, flagged
   twice now by two different reviews.
3. **Review the 3 newer hi-orbit-wiki commits** (metadata schema v0.1, the 5 newly-seeded
   puzzles + room book + ingestion method, the 260803 evidence batch) the way this session
   reviewed the first Hermes batch — cross-check firmware-derived claims against real source
   where it matters.
4. **Read `MVP_ROADMAP.md` and the new `AGENTS.md`** on `main` — both appear to already
   fulfill asks this session was about to make; confirm they hold up rather than re-doing
   the work.
5. **Evidence-layer robustness** — still an explicitly open decision (deferred pending real
   Drive access; see VISION_FEEDBACK.md §2). Worth revisiting now that real evidence batches
   exist and a metadata schema has apparently been formalized.
6. Minor: a Battleship draft was authored in `hi-orbit-wiki` despite an earlier note that one
   was "in progress elsewhere" — confirm no unresolved duplicate exists.

### Access notes

`vendor/kst-beta-ide` (private; holds the actual Quill/writer source) was not in this
session's GitHub scope and its submodule clone fails as a result — add it via `add_repo` if
a future session needs to read that code directly rather than trusting `feedback.md`'s
account of it. This session also had no shell/SSH access to the actual deployment host.
