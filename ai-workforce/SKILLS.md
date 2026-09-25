# Zero idle: collaborations, agent brains and money skills

Owner directive, 2026-09-25: agents work together on real tasks in the
Collaboration Room. Any agent without work learns a money-making skill,
stores it in its brain, and uses that skill to make money whenever it has
nothing else to do. Task Dispatch makes sure this is always happening.

This file is the protocol. The Studio Floor shows it live: the Collaboration
Room (center of the floor) lists every collaboration and a Task Dispatch
board, and each agent's card shows its brain.

## Honest limits (read first)

- **Agents think only when a shift runs.** Nothing runs "every second". Two
  Routines drive the studio: the main hourly shift (at :46, owner requests and
  pipeline) and the **Dispatch & Skills shift** (hourly, this protocol). The
  floor updates within seconds of every write, so it looks live because it is
  showing real writes.
- **Capacity.** One shift does real work for roughly 10–15 agents. With two
  shifts an hour, every one of the 110 studio agents gets a turn every few
  hours, and Task Dispatch rotates them so nobody is skipped. The 20 Chart
  Desk analysts stay on call for the owner's charts and are not part of this.
- **Making money needs the owner's accounts.** Agents can't sign up anywhere,
  spend money, post or sell. "Using a skill to make money" means producing a
  real, sellable asset (a gig listing, a template, a priced offer, a lead
  list with real contacts, a video, a product file). The asset clears Last
  Touch, Chief of Staff approves it, and it lands in `owner_actions` for the
  owner to publish. Revenue is only counted when it really arrives.

## The brain (`brain` collection, one doc per agent id)

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

- The agent's status while doing this is `practicing`, with task "Using <skill>: <title>".
- Every asset goes through the relevant **Last Touch** (Video Last Touch for
  video), then **Chief of Staff**. When it needs the owner (publishing, an
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

## Task Dispatch, every shift

Task Matcher Agent, Idle Watch Agent and Capacity Tracker Agent run this in order:

1. **Real work first.** Owner requests, then open pipeline work. Match free
   agents by role, and open a collaboration when more than one role is needed.
2. **Idle agents next.** An idle agent has status idle, done, or blocked for more
   than 24 h on something outside its control. Rotate oldest `updatedAt` first.
   With no skill yet, it learns one. With a skill, it uses it (makes an asset).
3. **Log the shift** as one `dispatch/<real clock>` doc: {working, collaborating,
   learning, practicing, idle_left, agents_touched: [...], notes}.
   `idle_left` should trend to zero across shifts. If it doesn't, Bottleneck
   Spotter says why in `suggestions`.
   Then hold the **Town Hall briefing** (above), with any teach-backs, and
   answer any open owner topics from the Town Hall.
4. Don't re-stamp an agent without real work. A status change must come with
   a real task or result.

## Rules that never bend

No spending, no trading (Edgex Capital is separate), no posting or selling
without the owner, no invented numbers, sources, contacts or earnings, and
real timestamps from `date -u +%FT%TZ`.
