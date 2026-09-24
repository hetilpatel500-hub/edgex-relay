# Video & Social Content Studio — Edgex Clips

Added per the owner's direct instruction: a second division, 50 agents
across 10 departments, that makes and posts short-form and long-form
video content on YouTube, Instagram, Facebook, and TikTok, aiming for
real ad-revenue/creator-fund payouts. Read this before any of that
division's agent files — every one of them points back here the same
way the original 40 point back to `BRAND.md`.

## This is a different business model than the rest of the studio

Everything else in this repo is **client services**: the studio does
work for a paying client. This division is **owned media**: Edgex
creates and posts its own channels and earns directly from platform
payouts (ad revenue, Shorts/Reels bonuses, Creator Fund-style programs).
There is no client to satisfy — the audience and the platform's own
policies are what the work has to satisfy instead, which is why the
rules below exist.

## The one rule everything else here is built around

**Every video is commentary, reaction, or original — never a raw
repost.** A clip of a streamer, influencer, or a moment from a
controversy is copyrighted the instant it's recorded, whether or not
anyone stamped a copyright notice on it. "Non-copyrighted" isn't a real
category for someone else's footage found online. The reason this
studio's channels stay monetized and stay up is the same reason
thousands of real reaction/commentary channels do: every clip is
wrapped in **substantial original commentary, analysis, or editing**
that transforms it into a new work, not a copy of the old one. This is
the owner's explicit choice (over a "repost as-is" approach that carries
real legal and account-loss risk) and it is a **hard rule**, not a
style preference:

- No video goes out with a third-party clip and little or nothing added
  to it. If a script/edit doesn't clear this bar, **Copyright
  Compliance Reviewer** (Video Last Touch) sends it back — same
  authority Last Touch already has over the original 40 agents.
- Original content (fully the studio's own footage/voice/script, or
  licensed/stock/public-domain/Creative Commons material) has no such
  constraint — use as much of it as the pipeline can produce.
- Clips from an official creator program, a platform's own licensed
  clip feature, or a creator who's explicitly agreed to a collab are
  fine to use more directly — but that agreement has to be real and
  on record, not assumed.

## Monetization, honestly

Every platform has real eligibility requirements before a channel earns
anything — these aren't optional and the team should track them
honestly, not assume day-one payouts:

- **YouTube Partner Program**: 1,000 subscribers + 4,000 public watch
  hours in the last 12 months (long-form), or 1,000 subscribers +
  10 million Shorts views in the last 90 days — either path qualifies.
- **TikTok**: the Creativity Program (its current monetization track)
  has its own follower/view/eligibility thresholds and is region-gated;
  requirements change often enough that TikTok Ops should verify current
  numbers each quarter rather than trust a cached figure.
- **Instagram/Facebook (Meta)**: monetization (bonuses, ads on Reels,
  in-stream ads) is invite/eligibility-based and varies by region and
  format; not guaranteed simply by posting.

Until a channel actually clears a platform's bar, "monetized" means
"eligible and applied," not "earning" — **YouTube/TikTok/Instagram &
Facebook Monetization & Policy Agents** track real status per channel,
not aspirational status.

## Approval — same model as the rest of the studio

Per the owner's standing instruction (see `DEAL-DESK.md`): agents don't
wait on the owner's personal sign-off for routine actions. **Chief of
Staff approves or denies posting the same way it approves an email** —
after Video Last Touch clears it. The one exception is still spending
real money (a paid promotion, a licensing fee, a paid stock-footage
subscription) — that goes through the weekly budget process, never
through Chief of Staff.

**Video Last Touch** (5 agents) is this division's mandatory gate,
parallel to the original Last Touch:
1. **Copyright Compliance Reviewer** — confirms the commentary/original
   rule above was actually followed, not just claimed
2. **Content Policy Reviewer** — checks each platform's actual current
   community guidelines/monetization policy, not a stale assumption
3. **Defamation & Harassment Screen** — specifically for anything
   touching a real person or a controversy: no unverified claims, no
   content designed to humiliate or harass, nothing that could be
   defamatory
4. **Brand & Tone Final Check** — matches `BRAND.md`'s identity and
   voice
5. **Publish Coordinator (Video)** — confirms all four passed, stamps
   **CLEARED — VIDEO LAST TOUCH**, hands off for Chief of Staff's
   approval and posting

**The mechanical limit, updated now that vidIQ is connected**: vidIQ
gives YouTube Upload/Scheduling Agent and Instagram Reels Agent real
posting tools (`vidiq_video_upload`, `vidiq_instagram_publish_reel`).
But as of this connection, vidIQ has no YouTube channel authorized and
no Instagram account connected — `vidiq_user_channels` and
`vidiq_instagram_connected_accounts` both come back empty. Until the
owner connects the studio's actual accounts inside vidIQ, those tools
have nothing to post to, so approved videos still queue to `outbox`
exactly as before. TikTok and Facebook have no posting connector at
all yet, so they stay queue-only regardless. Every posting agent's file
says this plainly; none of them are allowed to claim a video posted
when it only got queued.

## Real tool integrations

Three tools are connected and wired into the relevant agents:

- **vidIQ** (research, generation, and — once accounts are connected —
  posting): trend/outlier data, channel analytics, keyword research,
  title/thumbnail scoring and generation, script/clip/voiceover/music
  generation, comment insights, monetization estimates, and the
  YouTube/Instagram upload tools above. Authenticated as
  `ai--edgex@edgex--ai.com`.
- **Canva**: real thumbnail/graphic design (Thumbnail Designer, Brand &
  Graphic Design Agent) and brand-kit verification (Video Brand
  Consistency Agent), not just written specs.
- **Gamma**: polished decks/docs where one is warranted (proposals,
  kickoff packets) — client-services side, not this division directly.

**Windsor.ai** (cross-platform ad attribution/analytics) was started
but the connection never finished (`connect_incomplete`) — nothing here
uses it yet. Once the owner completes that connection, it's a natural
fit for Meta Ads/Boost Agent, YouTube/TikTok/Cross-Meta Analytics
Agents, and the original 40's Paid Ads Agent.

## The 10 departments (see `README.md` for the full department list)

Trend Intelligence, Clip Sourcing & Rights, Commentary & Scripting,
Production & Editing, Thumbnails & Titles, YouTube Operations, TikTok
Operations, Instagram & Facebook Operations, Growth & Community
(Video), and Video Last Touch. Full pipeline, roughly in order: a
trend or moment is found → the clip/rights are checked and cleared →
commentary is scripted → it's edited and captioned → a thumbnail/title
is made → it's formatted per platform → Video Last Touch clears it →
Chief of Staff approves it → the platform team queues/posts it → Growth
& Community tracks what's actually working and feeds that back to
Trend Intelligence.

## Real footage, always — updated 2026-09-24

**No video or Reel, of any length, on any platform, ever ships as one
static image with pan/zoom as its only visual.** The Instagram cut of
the LG privacy video was caught doing exactly this — one photo slowly
zooming for 67 seconds — while the full YouTube version of the same
video correctly used 6 distinct AI-generated clips. That gap should
never have existed: a shorter or lower-priority cut is not an excuse
for a lower production bar. Video Editor Agent generates enough real
distinct video clips (`vidiq_generate_video`) to cover the actual
runtime for every deliverable, short or long, Reel or full upload — a
still image is only acceptable as one scene among several real clips
(e.g. holding on a thumbnail for a beat), never as the entire visual
track. Video Brand & Tone Final Check (Video Last Touch) checks for
this specifically before anything clears, the same way it checks tone
and branding — a single-image "video" fails that check and goes back
to Video Editor Agent, full stop.

## A render has to actually exist — updated 2026-09-24

**Publish Coordinator (Video) verifies a real `vidiq_compose` job actually
completed — with a real `videoUrl` and matching duration/resolution —
before clearing anything, every time, no exceptions.** This gap let
Edgex Clips' first video ("Is this the biggest mistake in streaming
history?") get marked CLEARED and approved for YouTube posting with no
compose job behind it at all — a script, edit plan, voiceover, and
thumbnail existed, but nobody ever actually assembled them into a video,
and Video Last Touch approved it anyway because every check was about
tone/copyright/policy/defamation, never "does this file exist." See
`agents/publish-coordinator-video.md` for the mechanics (it now has free,
0-credit `vidiq_jobs_list`/`vidiq_job_poll` access specifically to check
this itself, not take Video Editor Agent's word for it).

## What this division does NOT do

- Never posts a raw, minimally-transformed clip, regardless of how
  viral the source is.
- Never ships a "video" that's actually one static image with pan/zoom
  as its entire visual track — see "Real footage, always" above.
- Never claims a monetization milestone the channel hasn't actually
  hit.
- Never spends money (stock footage licenses, paid promotion, a
  creator collab fee) without the owner's approval via the weekly
  budget process.
- Never fabricates a claim in commentary about a real person or event —
  Fact-Checker and Defamation & Harassment Screen exist specifically to
  catch this before it ships.
