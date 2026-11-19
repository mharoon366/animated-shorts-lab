# Production Review v7 (2026-11-19)

## Verified deliverables

- [Successful GitHub Actions production test](https://github.com/mharoon366/animated-shorts-lab/actions/runs/44550162402)
- Source: `blender/production_scene.py`
- Production specifications: `PRODUCTION_STANDARD.md`
- MP4: H.264, 360 x 640, 30 fps, 90 frames, exactly 3 seconds
- Hero image: 540 x 960
- Blender source: saved `.blend` included in workflow artifact
- Artifact name: `bucket-war-production-qa`

## Frame-by-frame diagnostic summary

The numeric QA evaluated all 90 frames before the CPU animation render.

- Largest bucket translation per 1/30-second step: **0.0737 m**
- Peak bucket speed implied by these steps: **2.211 m/s**
- Hand-to-bucket pin gap while carried: mean **0.0954 m**, maximum **0.1503 m**
- Face centers outside tighter safety region: **0 frames** for both characters
- Automated warnings: **none**

These quantitative results prove the object trajectory and basic framing checks pass. They do **not** certify the shot as professionally animated, or prove exact hand contact.

## Visual review

v7 maintains both characters in frame, unlike the earlier too-tight v6. The camera composition is less prone to edge cropping and still closer than the early wide scene. Procedural stone, costumes, and wooden bucket materials are consistent across the shot. The bucket passes through anticipation, lifting and carry positions without the previous teleport.

**Quality verdict: technical pass, artistic revision required.** The characters still look relatively simple, the thief's arm and body are not convincingly interacting under weight, the 3-second running action is stiff, and the staging/camera should use more purposeful shot choices. The current level does **not** match the Ricks Clips reference. A larger resolution will not resolve acting problems.

## Next production priorities

1. Rebuild character armature and foot grounding with more reliable body biomechanics (shoulders, hips, contact timing) instead of isolated procedural limb rotations.
2. Author a compelling 1-2-second close-up with anticipation, grip, and weight transfer before expanding to a chase.
3. Replace the mostly generic background with an original, coherent Italian medieval set, art-directed for the specific camera shot.
4. Improve facial performance with gaze shifts, blink, mouth shapes and reactions tied to exact story beats.
5. Make measurable contact tolerances stricter after the improved rig is implemented.
6. Run a preview quality gate before producing the longer 10-second or full-short animation.

## Rendering workflow

GitHub Actions installs a cached official Blender 4.5 build and uses Blender's own H.264 output. A hero still is generated first, then a frame-by-frame QA script inspects the scene *before* the 90-frame animation. If numerical checks fail, the expensive motion render is skipped.

No local Blender installation or paid artist is required for the current prototype pipeline. Production-quality output still requires significantly better art direction and animation engineering.
