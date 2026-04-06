# Zero-Knowledge Proof -- Narrative Plan

## Overview

- Duration: ~10 minutes
- Audience: People with basic math/programming background
- Language: Chinese (zh-CN)
- Voice: zh-CN-YunxiNeural
- Style: 3Blue1Brown (dark background, math animations)

## Structure (起承转合)

### Part 1: 起 -- Hook (0:00 - 2:00)

**S01_HookScene** (~60s)
- Real-life scenario: standing at a door with a password, bystanders watching
- The paradox: proving knowledge without revealing it
- "Mathematicians say: yes, it's completely doable."

**S02_TitleScene** (~15s)
- Lock icon + title reveal: "零知识证明 Zero-Knowledge Proof"

### Part 2: 承 -- Build Intuition (2:00 - 5:30)

**S03_CaveIntroScene** (~40s)
- Ali Baba's Cave: ring-shaped cave, secret door, paths A and B
- Introduce Peggy (prover) and Victor (verifier)

**S04_CaveProtocolScene** (~60s)
- Full protocol walkthrough: success case then failure case
- Success: Peggy crosses door, exits correctly
- Failure: Peggy can't open door, gets caught

**S05_ProbabilityScene** (~40s)
- Repeat the protocol: probability decay (1/2)^n
- 10 rounds = 0.1%, 20 rounds = one in a million

**S06_CoreInsightScene** (~20s)
- Victor's perspective: he learns nothing beyond "Peggy passed"
- Cannot retell the proof to a third party

**S07_PropertiesScene** (~40s)
- Completeness, Soundness, Zero-Knowledge -- three property cards

### Part 3: 转 -- Math (5:30 - 8:30)

**S08_MathBridgeScene** (~30s)
- Transition: "Can we do this with real math?"
- One-way functions: easy forward, impossible backward

**S09_DiscreteLogScene** (~30s)
- Discrete logarithm: y = g^x mod p (fast) vs x = log_g(y) (infeasible)

**S10_SchnorrProtocolScene** (~60s)
- Schnorr protocol: Commit (t), Challenge (c), Response (s), Verify
- Key insight: x is never transmitted

**S11_VerificationScene** (~30s)
- Equation expansion: g^s = g^{r+cx} = ... = t * y^c

**S12_SimulatorScene** (~40s)
- Simulator argument: fake transcripts indistinguishable from real ones

### Part 4: 合 -- Synthesis (8:30 - 10:00)

**S13_ApplicationScene** (~40s)
- zk-SNARKs (blockchain), identity verification, private computation

**S14_OutroScene** (~30s)
- Return to opening question, philosophical closing
- "在不暴露秘密的前提下，证明你掌握真理。"
