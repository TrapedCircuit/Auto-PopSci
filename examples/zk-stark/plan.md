# ZK-STARKs -- Narrative Plan

## Overview

- Duration: ~10 minutes (fast pace, ~280 chars/min)
- Audience: CS students / anyone with basic math background
- Language: Chinese (zh-CN)
- Voice: zh-CN-YunxiNeural (rate: +10%)
- Style: 3Blue1Brown (dark background, math animations)
- Special: includes prerequisite introductions (polynomials, finite fields)

## Structure (起承转合)

### Part 1: 起 -- Hook & Prerequisites (0:00 - 3:00)

**S01_HookScene** (~50s)
- Open with the trust problem: how do you verify a massive computation without re-doing it?
- Example: a supercomputer claims it checked 10 billion transactions — do you trust it?
- Reveal: ZK-STARKs let you verify in milliseconds

**S02_TitleScene** (~15s)
- Title reveal: "ZK-STARKs: 零知识可扩展透明知识论证"
- Acronym breakdown: Zero-Knowledge Scalable Transparent ARguments of Knowledge

**S03_PrereqPolyScene** (~60s)
- Prerequisite 1: Polynomials and their key property
- Schwartz-Zippel lemma intuition: two different degree-d polynomials can agree on at most d points
- Concrete example: f(x)=2x²+3x+1 vs g(x)=x²+5x+1, show they intersect at ≤2 points
- "Polynomials are like fingerprints — almost impossible to fake"

**S04_PrereqFieldScene** (~50s)
- Prerequisite 2: Finite fields (mod arithmetic)
- Concrete example: arithmetic mod 7
- Why finite fields: computers can't do real-number arithmetic exactly, but modular arithmetic is exact
- Connection: polynomials over finite fields = the language of STARKs

### Part 2: 承 -- Core Idea (3:00 - 5:30)

**S05_CoreIdeaScene** (~50s)
- The big idea: "proving computation = proving you know a polynomial"
- Execution trace → polynomial encoding
- If the polynomial satisfies constraints → computation was correct

**S06_ArithmetizationScene** (~60s)
- Arithmetization: turning a computation into polynomial constraints
- Simple example: Fibonacci-like sequence (a₀=1, a₁=1, aᵢ=aᵢ₋₁+aᵢ₋₂)
- Show: encoding trace as polynomial P(x), constraint as P(x·ω²) = P(x·ω) + P(x)
- "If P satisfies this everywhere on a special domain → computation correct"

**S07_PolynomialTestScene** (~40s)
- Low-degree testing intuition
- If someone claims P is degree-d, spot-check at random points
- Schwartz-Zippel: probability of cheating drops exponentially with checks
- Connection to the cave analogy from ZK proofs

### Part 3: 转 -- The FRI Protocol (5:30 - 8:00)

**S08_FRIIntroScene** (~50s)
- FRI: Fast Reed-Solomon IOP of Proximity
- Goal: prove a function is "close to" a low-degree polynomial
- Analogy: folding a long paper in half repeatedly until it's tiny enough to check directly

**S09_FRIStepsScene** (~60s)
- Step-by-step FRI walkthrough:
  1. Start with evaluations of f(x) on domain D (size N)
  2. Verifier sends random α
  3. Prover "folds": f₁(x) = (f(x)+f(-x))/2 + α·(f(x)-f(-x))/(2x) — degree halved!
  4. Repeat: domain shrinks by half each round
  5. After log(N) rounds, polynomial is constant — trivially checkable
- Visual: bars/towers shrinking by half each iteration

**S10_WhyTransparentScene** (~40s)
- SNARKs vs STARKs comparison
- SNARKs need "trusted setup" (toxic waste problem)
- STARKs only use hash functions — no secrets, fully transparent
- Quantum resistance: hash-based security survives quantum computers

### Part 4: 合 -- Putting It Together (8:00 - 10:00)

**S11_FullPipelineScene** (~40s)
- The full STARK pipeline recap:
  Computation → Trace → Polynomial → Constraints → FRI proof → Verify
- Prover: heavy work (minutes), Verifier: lightweight (milliseconds)
- Proof size: polylogarithmic in computation size

**S12_ApplicationScene** (~40s)
- Real-world applications:
  - StarkNet / StarkEx: Ethereum L2 scaling
  - Cairo language: write provable programs
  - Verifiable computation: cloud computing trust

**S13_OutroScene** (~30s)
- Return to opening: "A supercomputer says it's done — and now you can verify it"
- Philosophical close: trust through mathematics, not authority
- "ZK-STARKs: making the unverifiable, verifiable"
