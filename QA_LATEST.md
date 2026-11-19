# Latest render baseline and motion QA

As of 2026-11-19, the current technical baseline is the successful GitHub Actions run:
https://github.com/mharoon366/animated-shorts-lab/actions/runs/44528057698

## Verified delivered assets
- 3.000-second original Bucket War motion test, 30 fps, 90 frames, 360x640, H.264 MP4
- 540x960 hero render and editable Blender source
- `quality_report.json` with metrics for every frame

## Quantitative QC (all 90 frames)
| Metric | Measured | Interpretation |
|---|---:|---|
| Largest bucket step | 0.0737 m/frame | Teleport fixed |
| Max bucket movement speed | 2.211 m/s | Plausible stylized run |
| Average glove-to-handle-pin distance after grip | 0.1466 m | Connection improved, still visibly approximate |
| Maximum glove-to-handle-pin distance | 0.2849 m | **Not acceptable as a final rigid grip** |
| Frames with face centers outside 4%-96% viewport | 0 | Framing center passes |
| Automated warnings | 0 | No measured motion jumps beyond thresholds |

The previous test had a **0.8489 m** single-frame bucket teleport at 1.37s. It was detected and repaired through the new quality-gate script.

## Visual signoff
**TECHNICALLY PASS / ARTISTICALLY REVISE.** The scene is more consistent than earlier procedural tests, but still not ready for public release or for scaling to 60 seconds. Exact parity with the creator's quality is not established.

Remaining issues:
1. Wide static staging makes characters small on the 9:16 canvas. Plan camera angles and close-ups rather than indiscriminate zooming.
2. Leg cycle is more controlled, but needs verified planted-foot arcs and weight changes in character performance.
3. Exact palm-to-bucket grip still requires inverse kinematics aligned with the prop in 3D, not approximate 2D solving.
4. Improve facial acting, stylized movement accents, set dressing and lighting specificity.
5. Add original narration and sound design only when the animation passes visual review.

## System status
All animation, render and QA scripts operate in cloud GitHub Actions, no local Blender or paid services needed for these tests.
The standard render remains intentionally lightweight: 3s 360x640 at 30fps for movement, 540x960 at higher samples for hero still.
The completed code is versioned and repeatable, but it is still a **procedural pilot**, not yet an easy one-topic-to-full-Short production system.

## Next quality gate
A 3-second two-shot or multi-shot staging test with characters closer to camera, anatomically coherent prop gripping and visibly planted shoes. Only move to a 10-second pilot after that passes visual review.
