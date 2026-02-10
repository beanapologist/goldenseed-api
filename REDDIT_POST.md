# Reddit Post for r/proceduralgeneration

## Title
Built an API for deterministic procedural generation (same seed = same output, always)

## Body

I kept running into the problem where procedural generation wasn't reproducible across machines/languages. Wanted to be able to say "seed 42" and get identical output whether I'm prototyping in Python, shipping in Unity, or debugging six months later.

So I built GoldenSeed - an API that uses golden ratio math to generate deterministic random sequences. 

**Live demo:** https://goldenseed-api.vercel.app

**What it does:**
- Input: seed + number of chunks
- Output: hex strings + cryptographic hash
- Same seed = identical output, forever
- 50/50 bit distribution (statistically balanced)

**Landing page has three interactive demos:**
- Procedural dungeon generator (20x20 grid from seed)
- Seed fingerprints (unique visual patterns)
- Raw API output viewer

**Use cases I had in mind:**
- Storing entire game worlds as seeds
- Reproducing bugs in testing
- Verifiable generative art
- Agent-to-agent coordination (share seeds instead of datasets)

**Tech:**
- FastAPI backend
- Vercel serverless
- Free tier: 10k chunks/month
- Full API docs at /docs

Not trying to replace existing PRNGs in game engines - this is more for when you need cross-platform reproducibility or want to verify outputs cryptographically.

Feedback welcome. Still figuring out what this is most useful for.

**GitHub:** https://github.com/beanapologist/goldenseed-api
