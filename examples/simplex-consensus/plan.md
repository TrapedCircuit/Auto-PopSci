# Simplex 共识算法 -- Narrative Plan

Duration: ~10 min | Audience: cs-student | Language: zh-CN | Voice: zh-CN-YunxiNeural | Pace: fast (~300 chars/min)

## Part 1: 起 -- Hook (0:00 - 1:40)

**S01_HookScene** (~50s) - 银行转账、航班预订、区块链交易——数十台服务器必须对同一份数据达成一致。如果其中几台机器被黑客入侵、发送虚假消息呢？这就是「拜占庭容错」问题。

**S02_TitleScene** (~50s) - 2023 年，Cornell 的 Benjamin Chan 和 Rafael Pass 提出了一个优雅到令人惊讶的解法。标题揭晓：Simplex 共识算法。引出「简单而正确」的设计哲学。

## Part 2: 承 -- Build (1:40 - 4:40)

**S03_ByzantineScene** (~60s) - 拜占庭将军问题科普。多个将军围城，其中有叛徒发送矛盾命令。引入 n 个节点、f < n/3 拜占庭容错上界、2n/3 多数票（quorum）概念。

**S04_ConsensusBasicsScene** (~50s) - 共识协议需要什么？一致性（no fork）+ 活性（liveness）。部分同步网络模型：好的时候消息 Δ 秒送达，坏的时候无保证。

**S05_PriorWorkScene** (~50s) - PBFT (1999) 开创性但复杂，Tendermint 更简洁但 leader 需等待 2Δ、超时 6Δ。Simplex 的目标：更简单、更快。

## Part 3: 转 -- Deepen (4:40 - 8:20)

**S06_SimplexOverviewScene** (~60s) - 高层结构：迭代 h=1,2,3...，每轮一个随机 leader，leader 提案 → 投票 → 公证（notarization, ≥2n/3 票）→ 进入下一轮。3Δ 超时后投 dummy block。

**S07_ProtocolDetailScene** (~70s) - 完整协议逐步演示：Leader 广播提案 → 节点验证并投票 → 收集 2n/3 票形成公证 → 发送 finalize 消息 → 进入下一迭代。用具体 n=4, f=1 的例子。

**S08_KeyInsightScene** (~60s) - 核心创新：finalize 和 dummy vote 互斥。如果一个诚实节点发了 finalize，就不会发 dummy vote；反之亦然。2n/3 的 finalize 和 2n/3 的 dummy vote 不可能同时存在——这是 Simplex 安全性的关键。

**S09_LivenessScene** (~50s) - 活性论证：诚实 leader 情况下 2δ 完成，恶意 leader 最多浪费 3Δ+δ。对比 Tendermint 的 6Δ 超时。

## Part 4: 合 -- Conclude (8:20 - 10:00)

**S10_ApplicationScene** (~50s) - 实际应用：Solana Alpenglow、Commonware、Ava Labs。从学术论文到生产系统。

**S11_OutroScene** (~50s) - 回到开头：如何在不信任的网络中达成共识？Simplex 的回答是「用最简单的规则，构建最坚固的信任」。结语：简单是终极的复杂。
