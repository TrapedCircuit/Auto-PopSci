# 格密码学 (Lattice Cryptography) — 科普视频叙事计划

## 参数

- **时长**: ~10 分钟
- **语言**: zh-CN
- **语速**: 稍快 (rate="+10%")
- **受众**: cs-student
- **配音**: zh-CN-YunxiNeural

## 结构（起承转合）

### Part 1: 起 (Hook) — ~15% (~1.5 min)

**S01_HookScene**: 量子计算威胁——RSA、椭圆曲线等现行加密体系即将被量子计算机攻破。你的银行密码、网购信息、国家机密，全都可能暴露。那么，谁来保护后量子时代的安全？

**S02_TitleScene**: 标题揭晓——"格密码学：后量子时代的安全基石"，引出格（Lattice）这个看似简单的数学结构。

### Part 2: 承 (Build) — ~30% (~3 min)

**S03_LatticeBasicsScene**: 什么是格？从二维点阵出发，用基向量生成整数线性组合，展示格的直观图景。介绍"好基"与"坏基"的区别。

**S04_HardProblemsScene**: 格上的困难问题——最短向量问题(SVP)和最近向量问题(CVP)。为什么这些问题连量子计算机都解不了？展示高维空间中搜索的指数爆炸。

### Part 3: 转 (Deepen) — ~35% (~3.5 min)

**S05_LWEScene**: 带错误学习(LWE)问题——格密码学的核心基础。展示"秘密+噪声"的思想：已知一组近似等式，要还原秘密向量为何极其困难。

**S06_EncryptionScene**: 基于LWE的加密方案——如何用LWE构造公钥加密。Alice生成公钥（加入噪声），Bob加密消息，Alice用私钥解密。

### Part 4: 合 (Conclude) — ~20% (~2 min)

**S07_ApplicationsScene**: 现实应用——NIST后量子标准(CRYSTALS-Kyber/Dilithium)、全同态加密(FHE)、零知识证明。格密码学正在改变密码学的未来。

**S08_OutroScene**: 总结——从格这个简单的数学结构，到守护全人类数字安全的最前沿武器。数学之美，就在于此。
