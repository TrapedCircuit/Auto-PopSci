# Contributing a New Topic

This guide explains how to add a new science popularization video to Auto-PopSci.

## Quick Start

1. Create a new directory under `examples/`:
   ```
   examples/your-topic/
   ```

2. Copy the scaffold files:
   ```bash
   cp scaffold/animation/base.py examples/your-topic/animation/base.py
   cp scaffold/pyproject.toml.tmpl examples/your-topic/pyproject.toml
   cp scaffold/.gitignore.tmpl examples/your-topic/.gitignore
   ```

3. Edit `pyproject.toml` -- replace `{{TOPIC}}` with your topic name.

4. Follow the workflow in `SKILL.md` to create:
   - `plan.md` -- narrative outline
   - `script.md` -- full narration text
   - `animation/main.py` -- Manim scenes
   - `animation/build_video.py` -- build pipeline (use the template)

5. Build and test:
   ```bash
   cd examples/your-topic
   uv sync
   uv run python animation/build_video.py
   ```

## What to Include in Your PR

- `examples/your-topic/plan.md`
- `examples/your-topic/script.md`
- `examples/your-topic/animation/main.py`
- `examples/your-topic/animation/build_video.py`
- `examples/your-topic/animation/base.py` (copy from scaffold, unmodified)
- `examples/your-topic/pyproject.toml`
- `examples/your-topic/README.md`

Do NOT include:
- `media/` directory (generated artifacts -- gitignored)
- `.venv/` directory

## Checklist Before Submitting

- [ ] `plan.md` follows the 起承转合 structure
- [ ] `script.md` has one paragraph per `show_sub()` call
- [ ] Segment count in `build_video.py` matches `show_sub()` count in `main.py`
- [ ] `base.py` is unmodified from scaffold
- [ ] `uv run python animation/build_video.py` completes without errors
- [ ] Final video has synced audio throughout
- [ ] README.md lists all scenes with descriptions

## Topic Ideas

Looking for inspiration? Here are some topics that work well:

- **Math**: Euler's identity, Fourier transform, Bayes' theorem, P vs NP
- **CS**: Public-key cryptography, neural networks, hash functions, consensus algorithms
- **Physics**: Special relativity, quantum entanglement, entropy
- **Biology**: DNA replication, CRISPR, evolution by natural selection
