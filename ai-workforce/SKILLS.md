# Zero idle: collaborations, agent brains and money skills

Owner directive, 2026-09-25: agents work together on real tasks in the
Collaboration Room. Any agent without work learns a money-making skill,
stores it in its brain, and uses that skill to make money whenever it has
nothing else to do. Task Dispatch makes sure this is always happening.

This file is the protocol. The Studio Floor shows it live: the Collaboration
Room (center of the floor) lists every collaboration and a Task Dispatch
board, and each agent's card shows its brain.

## Honest limits (read first)

- **Agents think only when a shift runs.** Nothing runs "every second". The
  platform runs a Routine at most once an hour, and two Routines drive the
  studio: the **Dispatch & Skills shift** (at :29, this protocol) and the main
  shift (at :46, owner requests and pipeline). Both take owner requests, so
  one typed on the floor is picked up within about half an hour. The floor
  updates within seconds of every write, so it looks live because it is
  showing real writes.
- **Capacity.** A Dispatch shift runs its agents as **parallel crews** (below),
  about 30 agents a run instead of 10–15. The 90 studio agents outside the
  Chart Desk each get a turn about every 3 hours, and Task Dispatch rotates
  them so nobody is skipped. The 20 Chart Desk analysts stay on call for the
  owner's charts and are not part of this.
- **Making money needs the owner's accounts.** Agents can't sign up anywhere,
  spend money, post or sell. "Using a skill to make money" means producing a
  real, sellable asset (a gig listing, a template, a priced offer, a lead
  list with real contacts, a video, a product file). The asset clears Last
  Touch, Chief of Staff approves it, and it lands in `owner_actions` for the
  owner to publish. Revenue is only counted when it really arrives.

## The brain (`brain` collection, one doc per agent id)

**Use exactly this shape.** Skills always go in the `skills` list, and a new
skill is appended to it, never written as flat fields on the doc. The first
shift, on 2026-09-25, used a flat one-skill shape; those 12 docs were
converted, and the floor reads both.

```
brain/<agent-id> = {
  agent: "<agent-id>",
  skills: [{
    name: "Fiverr gig pricing research",
    summary: "one or two sentences: what the skill is",
    how_it_earns: "the concrete path to money through the studio's channels",
    steps: ["how to do it, step by step"],
    sources: ["2+ real URLs or named sources the skill was learned from"],
    fit: "why this agent's role is suited to it",
    learned_at: "<real clock>", uses: 0
  }],
  updatedAt: "<real clock>"
}
```

- **Learning.** An agent with no skill yet learns one. Pick it from
  `MONEY-MAP.md` or `money_map` items that fit the agent's role. Research it
  with WebSearch (2+ real sources, prices and demand from real listings, never
  guessed), then write it to the brain. One new skill per turn. An agent may
  hold up to 3 skills, and a new one must not duplicate a skill it already has.
- **Status while learning:** set the agent's `agents` doc to status `learning`,
  task "Learning: <skill>". When done, set `done` with the skill name in `result`.

## Using a skill (`skill_work` collection)

When an agent has a skill and no real work, it makes one sellable asset:

```
skill_work/<id> = {
  agent, skill, title,
  body: "the actual deliverable text, or the repo_changes id that holds the file",
  status: "draft" | "cleared_last_touch" | "approved" | "needs_owner" | "live" | "earned" | "rejected",
  value_estimate: "e.g. $150-$400 per order (source: ...)",
  next_step: "exactly what happens next, and who does it",
  collab: "<collabs id if several agents built it>",
  created, updatedAt
}
```

- **`body` holds the finished deliverable itself,** the exact text a buyer would
  receive: every reply, every caption, the full audit, the whole calendar. A
  description of the work ("4 drafted replies plus a 6-item checklist") is not an
  asset. Last Touch fails it and Chief of Staff can't approve it. On 2026-09-26, 31
  "approved" assets turned out to be descriptions; they were reopened as `draft`
  with a `review_note`. **Reopened drafts come first** when picking what an agent
  with a skill works on.
- **Sample work uses clearly fictional clients.** Label any made-up business,
  person or account "(fictional example)". Never use a real person's or
  business's name or handle, and never write quotes or comments as if a real
  account said them. Don't invent @handles either, because a made-up handle can
  belong to a real account. Use plain labels such as "Viewer A" or "a customer".
- The agent's status while doing this is `practicing`, with task "Using <skill>: <title>".
- Every asset goes through the relevant **Last Touch** (Video Last Touch for
  video), then the **Legal Desk** (all ten counsel, `LEGAL-DESK.md`), then
  **Chief of Staff**. When it needs the owner (publishing, an
  account, a payment link), add one `owner_actions` doc and set the asset to
  `needs_owner`.
- Never duplicate an asset that already exists (check `skill_work` and the
  storefront folders). Improving or extending an existing one is fine.
- `value_estimate` must cite where the number came from. `earned` is only set
  when real money arrived (a Stripe payout, a Fiverr order, an Etsy sale, all
  confirmed by the daily check-in).

## Collaborations (`collabs` collection)

Open one whenever **two or more agents work on the same task**. That covers
deal cards, Last Touch reviews, video runs, skill assets built together and
owner requests that need several roles.

```
collabs/<id> = {
  title, goal, agents: ["<agent-id>", ...], status: "active" | "done",
  started, updatedAt,
  log: [{t: "<real clock>", agent: "<agent-id>", note: "what this agent contributed"}],
  outcome: "what was produced, with links or doc ids",
  ref: "the request / deal / skill_work / decision it serves"
}
```

- While in it, members' `agents` docs get status `collaborating`, with task "In the
  Collaboration Room: <title>". The floor walks them to the table in the
  middle of the office.
- Every member adds at least one real `log` line. Close it (status `done`,
  `outcome`) in the same shift when the work finishes, and set members back to
  `done` with their result. Never leave a collaboration hanging across more
  than two shifts. Close it with the reason if it stalls.

## Town Hall briefings (`briefings` collection)

The Town Hall is the open floor between The Dispatch and the video wing: a
stage, a big screen and 24 seats. It's where the whole studio shares what it
learned. On the Studio Floor, the presenter walks to the stage, the audience
sits in the rows, and the screen shows the points.

**Every Dispatch & Skills shift ends with one briefing:**

```
briefings/<real clock> = {
  title: "short, specific: what this shift learned or built",
  presenter: "<agent-id>",            // the agent with the most useful news this shift
  audience: ["<agent-id>", ...],      // agents touched this shift + whoever the news matters to (max 24)
  points: ["3-5 real takeaways, each traceable to a brain skill, a skill_work asset, a collab or a decision"],
  taught: [{from, to, skill}],        // teach-backs that happened at this briefing (may be empty)
  answers: "<request id>",            // when it answers an owner topic from "Ask the room"
  held_at: "<real clock>", status: "held"
}
```

- **Teach-back.** When the presenter shares a skill, up to 2 audience agents
  whose roles genuinely fit may adopt it in the same shift. Copy it into their
  brain with `learned_from: "<presenter id>"`, keep the real sources, and
  write their own `fit` line. The copy is never automatic: it has to make
  sense for that role. Record each one in `taught`.
- **Owner topics.** Requests with `source: "town-hall"` (from "Ask the room"
  on the floor) belong to the Dispatch & Skills shift, not the main shift.
  Answer each one with real research as a briefing (`answers` set to the
  request id), then set the request to `done` with the briefing id in `result`.
- No filler. If a shift truly learned nothing new, the briefing says what
  was tried and why it didn't land.

## Parallel crews (speed, 2026-09-25)

A shift session can run helpers side by side (the `Agent` tool). The
Dispatch shift uses them so one run covers about 30 agents:

- Split the picked agents into 4–5 **crews** of 6–8, grouped by department so
  each crew shares context. Launch every crew in the same turn so they run at
  once.
- Each crew gets a self-contained brief: its agent ids and role files, what
  each one learns or makes, this file's brain and `skill_work` shapes, the
  rules below, and the skills and assets that already exist, so nothing
  is duplicated.
- **Crews research and draft; they don't write to the database.** Each
  returns its finished docs as JSON (brain docs, `skill_work`, collab log
  lines, with sources), and each `skill_work` body in full, never a summary.
  The shift checks each one (2+ real sources per skill, the exact shape, no
  invented numbers, a body that is the actual deliverable), then writes them
  itself in `ArtifactData` batches. One writer keeps the floor consistent.
- Fewer finished assets beat many summaries. If a crew can't finish its assets
  in time, give it fewer agents next run.
- Last Touch and Chief of Staff can also run as a crew over the whole
  batch of assets.
- If the `Agent` tool isn't available, do the same work one agent at a time
  and pick 10–12 agents, not 30.
- Finish within 25 minutes, so a run never overlaps the next shift.

## Task Dispatch, every shift

Task Matcher Agent, Idle Watch Agent and Capacity Tracker Agent run this in order:

1. **Real work first.** Owner requests, then open pipeline work. Match free
   agents by role, and open a collaboration when more than one role is needed.
2. **Idle agents next.** An idle agent has status idle, done, or blocked for more
   than 24 h on something outside its control. Rotate oldest `updatedAt` first.
   With no skill yet, it learns one. With a skill, it uses it (makes an asset).
   **Target: no studio agent goes more than 6 hours without real work.** Any
   agent past 6 h is picked before anyone else, and it doesn't matter what
   department it's in.
3. **Log the shift** as one `dispatch/<real clock>` doc: {working, collaborating,
   learning, practicing, idle_left, agents_touched: [...], stalest_hours_before,
   stalest_hours_after, notes}. `stalest_hours` is the age in hours of the
   agent that has gone longest without work, excluding the Chart Desk, and
   it's always written as a number, measured every shift.
   `idle_left` should trend to zero across shifts, and `stalest_hours_after`
   should stay under 6. If either doesn't, Bottleneck Spotter says why in
   `suggestions`.
   Then hold the **Town Hall briefing** (above), with any teach-backs, and
   answer any open owner topics from the Town Hall.
4. Don't re-stamp an agent without real work. A status change must come with
   a real task or result.

## Rules that never bend

No spending, no trading (Edgex Capital is separate), no posting or selling
without the owner, no invented numbers, sources, contacts or earnings, and
real timestamps from `date -u +%FT%TZ`.
