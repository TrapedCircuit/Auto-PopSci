# Transformer -- Example Project

A ~5 minute pop-sci video explaining the Transformer architecture,
from the "Attention Is All You Need" paper to GPT, BERT, and ViT.

## Build

```bash
uv sync
uv run python animation/build_video.py
open media/final/transformer_full.mp4
```

## Scenes

| # | Class | Content |
|---|-------|---------|
| 01 | HookScene | ChatGPT's secret: the 2017 Transformer paper |
| 02 | OverviewScene | Encoder-decoder architecture overview |
| 03 | EmbeddingScene | Word embedding + positional encoding |
| 04 | SelfAttentionScene | Q, K, V and attention weights |
| 05 | MultiHeadScene | Multiple attention heads in parallel |
| 06 | TransformerBlockScene | Full block: attention + FFN + residual + norm |
| 07 | ApplicationScene | GPT, BERT, Vision Transformer |
| 08 | OutroScene | "Attention Is All You Need" closing |

This example was generated as an E2E test of the Auto-PopSci skill.
