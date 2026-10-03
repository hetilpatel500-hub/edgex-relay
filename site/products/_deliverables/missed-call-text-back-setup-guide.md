# Missed-Call Text-Back: Do-It-Yourself Setup Guide

**Twilio + Make.com, step by step**

Version 1.0 · September 2026 · Edgex · ai--edgex@edgex--ai.com

---

## What you are building

When someone calls your business and nobody picks up, they get a friendly
text message from your business within about a minute, so the conversation
keeps going instead of going to a competitor.

Here is the whole flow:

1. A customer calls your normal business number.
2. Nobody answers (or the line is busy). Your phone carrier forwards the
   call to a Twilio number you own.
3. Twilio plays a short greeting: "Sorry we missed you, we're texting you
   now." Optionally, the caller can leave a voicemail.
4. When the call ends, Twilio tells a Make.com scenario about it.
5. The Make.com scenario checks the caller's number, makes sure it hasn't
   already texted this person recently, and sends them your text message
   through Twilio.
6. If the customer texts back, their reply is forwarded to your mobile
   phone, so you can call or text them back.

You keep your existing business number. Customers never see the Twilio
number unless they reply to the text.

### What this guide is, and what it isn't

- **It is** a written, step-by-step setup guide. You create the accounts,
  click through the settings, and build the Make.com scenario yourself by
  following the steps. Every value you need to type is written out.
- **It is not** a one-click import file, a hosted service, or software we
  run for you. We haven't included a Make.com blueprint file, because we
  would rather give you clear steps than a file that may not import
  cleanly into your version of Make.
- **It is not** legal advice. Part 10 covers the texting rules in plain
  language, but you are responsible for how you use texting in your
  business.

Prices and menu names below are correct to the best of our knowledge as of
September 2026. Twilio and Make.com change their screens and prices from
time to time. If a button has moved, search for its name in the app's
search bar.

---

## Before you start

**You will need:**

- A business phone line that supports **conditional call forwarding**
  (forward only when you don't answer or are busy). Most mobile carriers
  and most business VoIP systems do. Check with your provider if unsure.
- A **Twilio** account (twilio.com). New accounts start on a free trial.
- A **Make.com** account (make.com). The free plan is enough to test.
- A card to upgrade Twilio from trial when you go live (trial accounts can
  only text numbers you have verified, and add a "trial account" prefix).
- Your business details for texting registration: legal business name,
  address, website if you have one, and a tax ID (EIN in the US) if you
  have one.
- A mobile phone you can use for testing that is **not** your business
  line.

**Time:** about 60 to 90 minutes of hands-on setup. US texting
registration (Part 2) needs approval from the carriers and can take
anywhere from a few days to a few weeks, so start it first.

### Running costs (estimates, September 2026)

These are paid to Twilio and Make.com directly, not to us. Check both
pricing pages before you commit.

| Item | Typical cost |
|---|---|
| Twilio US local number | about $1.15 / month |
| Incoming forwarded call minutes (Twilio) | about $0.0085 / minute |
| Outgoing text (Twilio, US) | about $0.0083 per message segment, plus small carrier fees |
| US texting registration (A2P 10DLC) | about $4.50 one-time brand fee + $15 one-time campaign vetting fee, then roughly $1.50 to $10 / month depending on campaign type |
| Make.com | Free plan: 1,000 credits / month. Paid plans start at roughly $9 to $16 / month |

Each missed call uses about 5 Make.com credits (one per step), so the free
plan covers roughly 200 missed calls a month. Your phone carrier may
charge for call forwarding; check your plan.

---

## Part 1: Set up Twilio and get a number

1. Sign up at twilio.com and verify your email and your own mobile number.
2. In the Twilio Console, go to **Phone Numbers → Manage → Buy a number**.
3. Filter by your country and area code. Tick **Voice** and **SMS** under
   capabilities. Buy a local number.
4. Write down the number in full international format, for example
   `+15551234567`. This guide calls it **YOUR_TWILIO_NUMBER**.
5. From the Console home page, copy your **Account SID** and **Auth
   Token**. You will need them in Part 4. Treat the Auth Token like a
   password: don't paste it into emails or shared documents.

---

## Part 2: Register for business texting (start this early)

US carriers block texts from unregistered business numbers. Canada, the
UK and other countries have their own rules (see Part 10).

**United States (A2P 10DLC):**

1. In the Twilio Console, go to **Messaging → Regulatory Compliance** (or
   search "A2P 10DLC").
2. Choose your brand type:
   - **Sole Proprietor**: for a US or Canadian individual or business
     **without** a tax ID. Limited to one number and low volume, which is
     fine for this setup.
   - **Low Volume Standard**: for businesses **with** a tax ID (EIN) that
     send fewer than about 6,000 texts a day. This is the right choice for
     most small businesses.
3. Register a campaign. When asked for the use case, describe it
   honestly. Example text you can adapt:

   > Use case: Customer care. When a customer calls [Business Name] and
   > the call is missed, we send one text so they can reach us by text.
   > We only text people who have just called us. Recipients can reply
   > STOP to opt out.

   Sample message:

   > Hi, it's [Business Name]. Sorry we missed your call! What can we
   > help with? Reply here and we'll get right back to you. Reply STOP to
   > opt out.

   Opt-in description: "The customer initiates contact by calling our
   business phone number. We send a single text in response to that
   call."
4. Add YOUR_TWILIO_NUMBER to the campaign's Messaging Service when
   prompted.
5. Wait for approval. You can finish Parts 3 to 7 while you wait; texts
   to real customers won't deliver reliably until the campaign is
   approved.

**Toll-free alternative:** if you'd rather use a toll-free number, Twilio
requires "toll-free verification" instead of A2P 10DLC. The rest of this
guide works the same way.

---

## Part 3: Create the call greeting (TwiML Bin)

A TwiML Bin is a small set of instructions that Twilio hosts for you. It
tells Twilio what to say when a forwarded call arrives.

1. In the Twilio Console, search for **TwiML Bins** and click **Create new
   TwiML Bin**.
2. Friendly name: `missed-call-greeting`
3. Paste this, replacing `[Business Name]`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Sorry we missed your call at [Business Name]. We are sending you a text message right now, so you can reply there. Thank you, goodbye.</Say>
  <Hangup/>
</Response>
```

4. Save.

### Optional: let callers leave a voicemail

If you want voicemail too, you need **two** bins. (A voicemail step with
no follow-up instruction makes Twilio replay the greeting in a loop, so
the second bin tells it to end the call.)

Bin 1, named `voicemail-done`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Thanks, we got your message. Goodbye.</Say>
  <Hangup/>
</Response>
```

Save it and copy its URL (shown at the top of the bin, starting with
`https://handler.twilio.com/twiml/`).

Bin 2, use this instead of the greeting above in `missed-call-greeting`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Sorry we missed your call at [Business Name]. We are sending you a text message right now. If you would like to leave a short message instead, please speak after the tone.</Say>
  <Record maxLength="120" timeout="5" playBeep="true" action="PASTE_VOICEMAIL_DONE_URL_HERE"/>
</Response>
```

Recordings appear in the Twilio Console under **Monitor → Logs → Call
recordings** (or search "Recordings"). Recording is charged per minute,
and some places require you to tell callers they are being recorded; the
greeting above does that by asking them to leave a message.

---

## Part 4: Build the Make.com scenario

This is the part that decides who gets a text, and sends it.

### 4.1 Create the data store (the "who have we texted" list)

This list stops the same person being texted twice for the same call, or
over and over if they call several times in a row.

1. In Make.com, open **Data stores** from the left menu and click **Add
   data store**.
2. Name: `missed-call-log`
3. Data structure: click **Add**, name it `missed-call-record`, and add
   these fields:

| Field name | Type |
|---|---|
| `last_call_sid` | Text |
| `last_texted_at` | Date |
| `business_line` | Text |

4. Size: the smallest option is plenty.

If your Make.com plan doesn't include data stores, you can use a Google
Sheet with the same three columns instead (use the Google Sheets "Search
rows" and "Add a row / Update a row" modules in place of the data store
modules below).

### 4.2 Create the scenario

Click **Create a new scenario** and name it `Missed-call text-back`.
You will add these modules in order:

```
[1 Webhook] → (filter A) → [2 Get record] → (filter B) → [3 Send text]
     → [4 Save record] → [5 Notify you (optional)]
```

#### Module 1: Webhooks → Custom webhook

1. Click the big plus, search **Webhooks**, choose **Custom webhook**.
2. Click **Add**, name it `twilio-missed-call`, and save.
3. Make shows a URL like `https://hook.us1.make.com/abc123...`. Copy it.
4. Add a secret to the end of the URL so only Twilio (which you will give
   the full URL to) can trigger it. Make up a random string of 20 or more
   letters and numbers, for example:

   `https://hook.us1.make.com/abc123...?k=Rq7Lm2Vx9Pz4Tn8Wc5Hy`

   Save this full URL somewhere safe. This guide calls it
   **YOUR_WEBHOOK_URL**, and the random part **YOUR_SECRET**.
5. Leave the webhook "listening" for now. You'll send it a real test call
   in Part 5 so Make learns what the data looks like.

#### Filter A (between module 1 and 2): "Real caller, and really Twilio"

Click the small wrench on the line between modules 1 and 2 and choose
**Set up a filter**. Label: `Real caller`. Add these conditions, joined
with **AND**:

| Field | Operator | Value |
|---|---|---|
| `k` (from module 1) | Text operators: Equal to | YOUR_SECRET |
| `From` (from module 1) | Text operators: Matches pattern | `^\+1[2-9]\d{9}$` |

The pattern allows only US and Canadian numbers, which filters out blocked
or "anonymous" callers and avoids surprise international texting costs.
For UK mobile numbers use `^\+447\d{9}$` instead.

#### Module 2: Data store → Get a record

- Data store: `missed-call-log`
- Key: map `From` from module 1

If no record exists (a first-time caller), this module returns empty
values and the scenario continues.

#### Filter B (between module 2 and 3): "Not a duplicate, not texted recently"

This filter uses two condition groups joined with **OR**. Click **Add OR
rule** to create the second group.

Group 1 (first-time caller):

| Field | Operator | Value |
|---|---|---|
| `last_texted_at` (from module 2) | Basic operators: Does not exist | |

**OR** Group 2 (returning caller, new call, and it's been a while):

| Field | Operator | Value |
|---|---|---|
| `last_call_sid` (from module 2) | Text operators: Not equal to | `CallSid` from module 1 |
| `last_texted_at` (from module 2) | Datetime operators: Earlier than | `{{addHours(now; -12)}}` |

(The two rows in group 2 are joined with AND.) Change `-12` if you want a
different "don't text again within X hours" window.

#### Module 3: Twilio → Create a Message

1. Add the **Twilio** app and choose the module that sends a message
   (called **Create a Message** at the time of writing).
2. Connection: click **Add**, paste your Account SID and Auth Token from
   Part 1.
3. Fill in:
   - **From:** YOUR_TWILIO_NUMBER (for example `+15551234567`)
   - **To:** map `From` from module 1
   - **Body:** your message. Keep it under 160 characters and use plain
     straight quotes and apostrophes (curly ones can double the cost).
     Example:

     `Hi, it's [Business Name]. Sorry we missed your call! What can we help with? Reply here and we'll get right back to you. Reply STOP to opt out.`

If you can't find the Twilio module, see Appendix A for a version that
uses Make's built-in HTTP module instead.

**Add retry protection.** Right-click module 3 → **Add error handler** →
choose **Break**. Set **Number of attempts** to `3` and **Interval between
attempts** to `2` minutes. Then open the scenario **Settings** (gear icon
at the bottom) and turn on **Allow storing of incomplete executions**.
The Break handler doesn't work without that setting. This way, if Twilio
has a brief hiccup, Make tries again instead of silently dropping the
text.

#### Module 4: Data store → Add/replace a record

- Data store: `missed-call-log`
- Key: map `From` from module 1
- Overwrite an existing record: **Yes**
- `last_call_sid`: map `CallSid` from module 1
- `last_texted_at`: `{{now}}`
- `business_line`: map `ForwardedFrom` from module 1 if it's there,
  otherwise leave blank

#### Module 5 (optional): Tell yourself about the missed call

Add an email module (Gmail, Microsoft 365 Email, or Make's **Email → Send
an email**) or a second Twilio **Create a Message** to your own mobile:

- To: your email or mobile
- Subject/Body: `Missed call from {{1.From}} at {{formatDate(now; "h:mm A, MMM D")}}. We sent them the auto-text.`

### 4.3 Turn it on

1. Click **Save**.
2. Set scheduling to **Immediately** (as soon as data arrives), which is
   the default for webhooks.
3. Switch the scenario **ON** (the toggle at the bottom left).

---

## Part 5: Connect your Twilio number

1. In the Twilio Console, go to **Phone Numbers → Manage → Active
   numbers** and click YOUR_TWILIO_NUMBER.
2. Under **Voice Configuration**:
   - **A call comes in:** choose **TwiML Bin**, then select
     `missed-call-greeting`.
   - **Call status changes:** paste YOUR_WEBHOOK_URL (including the
     `?k=YOUR_SECRET` part). Method: **HTTP POST**.
3. Save.

Why "call status changes" and not "a call comes in"? Twilio sends the
status update after the call ends and doesn't wait for a reply, so your
greeting always plays even if Make is slow or down. Make just gets told
"this call happened, here's the caller's number."

**Teach Make the data shape:** open your Make scenario, right-click module
1 and choose **Redetermine data structure** (or click **Run once**). Then,
from your test phone, call YOUR_TWILIO_NUMBER directly and hang up after
the greeting. Make should show "Successfully determined". Now all the
fields (`From`, `To`, `CallSid`, `CallStatus`, `k` and so on) can be
mapped in the filters and modules above. If you set up the filters before
this step, reopen them and re-select the fields.

---

## Part 6: Forward missed calls from your business line

Now tell your business phone to send unanswered calls to
YOUR_TWILIO_NUMBER. How you do this depends on your phone provider.

**Business VoIP systems** (RingCentral, Vonage, Grasshopper, Google
Voice, 8x8, Dialpad and similar): look in the admin settings for "call
forwarding", "call handling" or "when I don't answer". Set the
"no answer" and "busy" destination to YOUR_TWILIO_NUMBER instead of
voicemail.

**Mobile phones:** most carriers support star codes. Common examples
(confirm with your carrier, as codes vary):

| Carrier type | Forward when not answered | Forward when busy |
|---|---|---|
| Most GSM carriers (for example AT&T, T-Mobile in the US) | `**61*+1XXXXXXXXXX#` then call | `**67*+1XXXXXXXXXX#` then call |
| Verizon | `*71` followed by the 10-digit number (covers no answer and busy) | (same code) |

Replace `XXXXXXXXXX` with YOUR_TWILIO_NUMBER without the +1. On many GSM
phones you can set the ring time before forwarding by adding `**20` before
the `#` (for example `**61*+15551234567**20#` for 20 seconds).

**Landlines:** ask your provider for "call forward no answer" and "call
forward busy".

Tip: set the ring time long enough that you still have a fair chance to
answer (15 to 25 seconds is common).

---

## Part 7: Make sure you see customer replies

When a customer replies to your text, the reply goes to
YOUR_TWILIO_NUMBER. Forward it to your own mobile:

1. Create another TwiML Bin named `forward-replies`. Replace the number
   with your own mobile:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message to="+15559876543">Reply from {{From}}: {{Body}}</Message>
</Response>
```

2. On YOUR_TWILIO_NUMBER, under **Messaging Configuration → A message
   comes in**, choose **TwiML Bin** → `forward-replies`. Save.
3. After A2P registration, your number belongs to a **Messaging
   Service**. Open **Messaging → Services → (your service) →
   Integration** and choose **Defer to sender's webhook**, so the setting
   in step 2 is used.

You'll receive "Reply from +1555...: Can you come out Tuesday?" on your
mobile. Call or text the customer back from your normal business phone.
Each forwarded reply is one more text on your Twilio bill.

Twilio automatically handles STOP, UNSUBSCRIBE and similar replies on
US and Canadian numbers: anyone who replies STOP won't receive further
texts from that number.

---

## Part 8: Test it end to end

Use a phone that is **not** your business line. Tick each one off:

1. [ ] **Missed call → text.** Call your business number and don't
   answer. You should hear the greeting, and receive the text within
   about a minute.
2. [ ] **No duplicate.** Look at the scenario's **History** in Make: one
   run, one text sent.
3. [ ] **Cooldown works.** Call again straight away and don't answer. You
   should hear the greeting but **not** get a second text (the run shows
   it stopped at filter B).
4. [ ] **Answered calls are left alone.** Call and answer. No greeting,
   no text.
5. [ ] **Replies reach you.** Reply to the text from the test phone. The
   reply should arrive on your mobile.
6. [ ] **Blocked caller ID.** Call with caller ID hidden (often `*67`
   before the number in the US). The run should stop at filter A. No
   text, no error.
7. [ ] **Opt-out.** Reply STOP from the test phone. Clear the test
   phone's record from the data store, then call and miss again. Module 3
   should fail with Twilio error 21610 (the person has opted out). That's
   correct behavior. Reply START to opt back in.
8. [ ] **Optional notification** (module 5) arrives.

To repeat test 1 with the same phone, open the `missed-call-log` data
store in Make and delete that phone's record first.

---

## Part 9: Troubleshooting

| What you see | Likely cause | Fix |
|---|---|---|
| Caller hears your normal voicemail, not the greeting | Carrier forwarding not active, or voicemail picks up first | Re-enter the forwarding code; ask your carrier to disable voicemail or lengthen the ring time before voicemail |
| Greeting plays but no text, and Make shows no run | "Call status changes" URL missing or wrong, or scenario off | Recheck Part 5 step 2; make sure the scenario toggle is ON |
| Make run stops at filter A | Secret `k` doesn't match, or caller's number isn't in the allowed pattern | Compare the `k` value in the run details with YOUR_SECRET; check the pattern |
| Make run stops at filter B on a first call | `last_texted_at` exists for that number from testing | Delete the record in the data store |
| Twilio module error 21610 | The person replied STOP earlier | Expected; they must text START to opt back in |
| Text shows "Sent from your Twilio trial account" or only reaches your own phone | Twilio account still on trial | Upgrade the Twilio account |
| Texts not delivered to customers (error 30034 or similar) | US texting registration not approved yet | Finish Part 2 and wait for approval |
| Greeting loops over and over | Voicemail `<Record>` has no `action` URL | Add the `voicemail-done` URL as shown in Part 3 |
| `From` shows your own business number instead of the caller | Your carrier doesn't pass the original caller ID when forwarding | Ask your carrier; some VoIP systems have a "pass through caller ID" option |

Make keeps a history of every run. Click any run to see each module's
input and output, which usually shows the problem straight away.

---

## Part 10: Texting rules in plain language (not legal advice)

- **One helpful reply, not marketing.** This setup texts someone once,
  right after they called you, about their call. Don't add promotions,
  coupons, or follow-up sequences to it without getting proper consent;
  marketing texts have much stricter rules (for example the TCPA in the
  US).
- **Always identify your business** and include "Reply STOP to opt out."
- **Respect opt-outs.** Twilio blocks texts to people who replied STOP.
  Don't try to work around it.
- **Canada:** Canada's anti-spam law (CASL) applies to commercial
  electronic messages. A reply to a customer's own inquiry is generally
  treated differently from marketing, but keep it purely about their call
  and include your business name and an opt-out.
- **UK and EU:** use a Twilio number that is SMS-capable in that country,
  keep the message about their call, identify your business, and include
  an opt-out. Data protection rules (UK GDPR / GDPR) apply to the phone
  numbers you store; the data store in Part 4 keeps only the number, the
  call ID and a timestamp. Delete records you don't need.
- **Recording calls:** if you use the voicemail option, some states and
  countries require telling callers they are being recorded. The greeting
  asks them to leave a message, which most people treat as notice, but
  check your local rules.
- **Healthcare, legal and finance businesses:** don't put anything
  sensitive in the text, and check your industry's rules on patient or
  client communication before turning this on.

If you're unsure, a short conversation with a local lawyer or your
industry association is worth it before you go live.

---

## Appendix A: Send the text with Make's HTTP module instead

If the Twilio app in Make isn't available or behaves differently, replace
module 3 with **HTTP → Make a request**:

- **URL:** `https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json`
- **Method:** POST
- **Authentication type:** Basic auth (in some versions, add a "Basic
  auth" credential): username = your Account SID, password = your Auth
  Token
- **Body type:** `application/x-www-form-urlencoded`
- **Fields:**
  - `To` = `From` from module 1
  - `From` = YOUR_TWILIO_NUMBER
  - `Body` = your message
- **Parse response:** Yes

Add the same **Break** error handler as in module 3. A successful request
returns status `201` and a message `sid` starting with `SM`.

---

## Appendix B: Message templates

Keep each under 160 characters with straight quotes, and always include
your business name and "Reply STOP to opt out."

**Trades and home services**

`Hi, it's [Business]. Sorry we missed your call! Is this about a repair or a quote? Reply here and we'll get back to you soon. Reply STOP to opt out.`

**Salons, spas, clinics (booking-driven)**

`Hi from [Business]! Sorry we missed you. Want to book or change an appointment? Reply with a day and time that works. Reply STOP to opt out.`

**Professional offices**

`[Business] here. Sorry we missed your call. Reply with a good time to reach you and we'll call you back. Reply STOP to opt out.`

**After hours**

`Thanks for calling [Business]. We're closed right now but we'll reply first thing tomorrow. Reply with what you need. Reply STOP to opt out.`

---

## Appendix C: Quick reference card

| Setting | Where | Value |
|---|---|---|
| Greeting | Twilio number → Voice → A call comes in | TwiML Bin `missed-call-greeting` |
| Tell Make | Twilio number → Voice → Call status changes | YOUR_WEBHOOK_URL (with `?k=`), HTTP POST |
| Replies | Twilio number → Messaging → A message comes in | TwiML Bin `forward-replies` |
| Messaging Service | Messaging → Services → Integration | Defer to sender's webhook |
| Duplicate/cooldown | Make data store `missed-call-log` | Key = caller number, 12-hour window |
| Retry | Make module 3 error handler | Break, 3 attempts, 2 minutes apart |
| Forwarding | Your phone provider | No answer + busy → YOUR_TWILIO_NUMBER |

---

Questions about this guide: ai--edgex@edgex--ai.com

Twilio and Make are trademarks of their respective owners. Edgex isn't
affiliated with or endorsed by either company.
