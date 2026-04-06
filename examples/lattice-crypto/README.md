# Lattice Cryptography -- Example Project

A ~10 minute pop-sci video explaining lattice-based cryptography,
from the quantum threat to post-quantum encryption standards.

Features a **3D lattice visualization** using oblique projection (`_proj()`)
-- see `S04_Lattice3DScene` in `animation/main.py`.

## Build

```bash
uv sync
uv run python animation/build_video.py
open media/final/output_full.mp4
```

## Scenes

| # | Class | Content |
|---|-------|---------|
| 01 | HookScene | Quantum threat to RSA and elliptic curves |
| 02 | TitleScene | "Lattice Cryptography: post-quantum security" |
| 03 | LatticeBasicsScene | 2D lattice, basis vectors, good vs bad basis |
| 04 | Lattice3DScene | **3D lattice with oblique projection + rotation** |
| 05 | HardProblemsScene | SVP and CVP -- why they're hard even for quantum |
| 06 | LWEScene | Learning With Errors -- step-by-step numerical example |
| 07 | EncryptionScene | LWE-based public-key encryption walkthrough |
| 08 | ApplicationsScene | CRYSTALS-Kyber, FHE, zero-knowledge proofs |
| 09 | OutroScene | "Math protects the digital world" closing |

## 3D Projection Helper

This example demonstrates the recommended approach for 3D-like visuals
without `ThreeDScene` (which causes OOM with many `Dot3D`/`Sphere` objects):

```python
def _proj(x, y, z, phi=0.55, theta=-0.7):
    cp, sp = np.cos(phi), np.sin(phi)
    ct, st = np.cos(theta), np.sin(theta)
    sx = x * ct - y * st
    sy = x * st * sp + y * ct * sp + z * cp
    return np.array([sx * 0.65, sy * 0.65, 0])
```

"Rotate" the camera by transforming all dots to a different `(phi, theta)`.
