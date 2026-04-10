

## 💙 To the Community — A Personal Word

> *"The universe doesn't yield its secrets to a single observer.  
> It never has. It never will."*

I want to speak to you directly for a moment — not as a project README, but as one person who built something they genuinely believe in, reaching out to the people who might care about it just as much.

GRANITE started as a private obsession: the conviction that the astrophysics community deserved an open-source engine capable of simulating the most extreme multi-body events the universe produces — not one day, not in theory, but *now*, with rigorous physics and reproducible science. Every line of this codebase was written with that conviction. The CCZ4 formulation, the GRMHD Valencia kernel, the AMR subcycling, the constraint monitors — none of it was scaffolded or approximated. It was derived, implemented, debugged, and validated with the same standard I would hold any published code to.

But a single developer, no matter how driven, is still just one person. And a scientific instrument — which is what GRANITE is meant to become — is not built by one person. It is built by a community of people who each bring something irreplaceable: a sharper eye for a subtle numerical instability, a deeper familiarity with a particular cluster's topology, a physical intuition that catches what the tests don't, a weekend spent stress-testing a benchmark nobody else thought to run.

**This is that invitation.**

---

### 🌍 How You Can Contribute — On Your Own Terms

There is no minimum. There is no gatekeeping. There is no "small enough to not matter." Every form of engagement strengthens this project in a way that cannot be faked or automated:

| What you bring | How it helps GRANITE |
|---|---|
| **You run it on your cluster** | Real-world scaling data and hardware-specific failure modes that a desktop simply cannot surface |
| **You read the physics and find something wrong** | A wrong formula caught early is worth a thousand correct ones discovered late |
| **You submit a PR — any size** | A one-line fix to a comment, a new unit test, a missing edge case in the C2P solver — all of it moves the needle |
| **You open an issue** | Describing what broke, what confused you, or what's missing is itself a contribution of enormous value |
| **You share it with a colleague** | The person most likely to find the deepest bug is the one we haven't met yet |
| **You validate a benchmark** | Running B2_eq or the single-puncture test on your hardware and sharing the constraint norms takes 20 minutes and generates ground truth we cannot produce alone |
| **You review the theory** | If you work in numerical relativity, GRMHD, or computational astrophysics — your professional eye on the formulation is the most valuable thing you could offer |

No contribution requires you to understand the whole codebase. The physics modules are deliberately decoupled precisely so that an expert in radiation transport can engage with `src/radiation/` without needing to understand the CCZ4 RHS loop, and vice versa.

---

### 🏛️ To Research Groups & Institutions

If you lead or belong to a numerical relativity group, a gravitational wave observatory preparation team, a nuclear physics collaboration, or a supercomputing center — GRANITE was built with you in mind.

The codebase is **fully open, MIT-licensed, and architecturally designed for extension**. We are not asking you to use GRANITE instead of your existing tools. We are asking whether some of what we have built might be useful to you, and whether some of what you know might make GRANITE better for everyone.

We are actively interested in:
- **Joint validation campaigns** against established codes (Einstein Toolkit, GRChombo, SpECTRE, AthenaK)
- **Allocation access** on Tier-0/1 systems for the B5\_star benchmark and strong-scaling studies  
- **Graduate student and postdoc involvement** — the codebase is intentionally pedagogically clean and test-covered for exactly this reason
- **Waveform template collaboration** with LIGO/Virgo/LISA preparation groups

If any of this resonates, open an issue tagged `[partnership]` or reach out via the repository. We will respond to every serious inquiry.

---

### 🙏 A Genuine Thank You

To everyone who has already read this far: **thank you**. Seriously.

In a world where every repository competes for attention, the fact that you read through the physics, understood what this is trying to do, and are still here means more than any star count or fork metric ever could. You are exactly the kind of person this was built for.

To those who will file a bug report at 11pm because something didn't converge and they couldn't let it go — thank you in advance.  
To those who will spend a Saturday afternoon writing a test for a corner case nobody asked them to cover — thank you in advance.  
To those who will send an email saying "I ran your B2_eq benchmark on our cluster and here's what happened" — thank you in advance.  
To those who will read a formula in `ccz4_rhs.cpp` and say "wait, shouldn't that sign be negative?" — *especially* thank you in advance.

This project exists because the science demands it. It will reach its potential because the community makes it.

**Welcome aboard. Let's simulate the universe — together.**

— **LiranOG**, Founder & Lead Developer  
April 10, 2026

<div align="right">

[![GitHub Issues](https://img.shields.io/github/issues/LiranOG/Granite?label=open%20issues&color=blue)](https://github.com/LiranOG/Granite/issues)
[![GitHub Discussions](https://img.shields.io/github/discussions/LiranOG/Granite?label=discussions&color=purple)](https://github.com/LiranOG/Granite/discussions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/LiranOG/Granite/blob/main/.github/CONTRIBUTING.md)

</div>
