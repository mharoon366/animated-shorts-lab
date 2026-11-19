# Animated Shorts Lab: Lightweight Production Standard (v1)

## Goal
Build a reusable **original** 2.5D/3D cartoon production kit for fast-paced history Shorts, using the uploaded Ricks Clips reference for animation *principles* (perspective, performance, weight, anticipation and impactful staging), not copied character models, distinctive assets, footage or frame compositions.

## Creative direction
- Visual language: rounded expressive faces, clear silhouettes, ink-dark accents, rich cloth, weathered stone, realistic cast/contact shadows and warm/cool light separation.
- Original identity: Modena character wears cobalt and ochre with a hawk-like geometric crest; Bologna guard wears brick red with an ivory heraldic mark. Do not replicate the creator's proprietary designs.
- The first sequence is a bucket theft in a fortified Italian courtyard. One dramatic action and one visible reaction per beat; no slideshow or frame interpolation of unrelated AI stills.
- Faces must be readable on a phone. Character silhouettes should survive reduction to 25% size.

## Asset budgets
| Asset | Target | Approach |
|---|---|---|
| Lead character | ~4k-15k tris | Shaped volumes, bevels, independent head/face/arm/leg pivots |
| Secondary character | reuse same rig | Color/costume/face variations |
| Bucket and hero props | ~1k-4k tris each | Actual staves, bands, rivets and carrying handle |
| Set dressing | instanced modular | Repeated arches, battlements, tiles, trees; seeded procedural layout |
| Image textures | zero external dependencies for v1 | Procedural shader noise, roughness and color variation |
| Cloth | animated rigid sections for v1 | No expensive cloth sim for recurring characters |
| Water | lightweight shaped surface and individual ballistic droplets | Avoid expensive fluid simulations |
| Lighting | 1 principal sun/area, 1 cool fill, 1 warm rim, world ambient | Unified shadows and stable exposure |

These are design targets, not measured counts in the initial code. Profile rendered scene with Blender stats before claiming compliance.

## Rig and motion rules
- Every character has a persistent rig root and separate torso, head, expression, arms, knees/feet and cape controls.
- Hands hold the same physical bucket throughout lift and escape. Prop trajectories must be mathematically continuous, not object swaps.
- Action arcs: look → anticipate → contact/grasp → weight shift → lift → accelerate → visible reaction.
- Plant feet during holds, separate anticipation from action, shift center of mass over the support foot.
- Deliberate holds are acceptable. Never confuse 30-fps delivery with independent full-body motion on all 30 frames.
- Secondary motion trails main motion: cape and hat, bucket tilt, water slosh, dust after foot contacts.
- Check all consecutive frames for mesh intersections, trajectory jumps, clipping or unmotivated facial changes.

## Editorial guide: Bucket War pilot
| Time | Beat | Acceptance criterion |
|---|---|---|
| 0.0-0.7s | Modena notices the bucket | Clear glance and anticipation |
| 0.7-1.4s | Lean and reach | Hand approaches handle; feet remain grounded |
| 1.4-2.2s | Grasp and lift | Bucket takes weight and moves on a continuous path |
| 2.2-3.0s | Guard reacts and pursuit begins | Big readable facial acting and acceleration |

This 3s test is **only** a quality gate before a 10s narrative pilot.

## Rendering budget
- Master: 1080x1920 9:16 at 30fps; H.264 MP4.
- Diagnostic animation: 360x640, 30fps, 3 seconds, low-sample Cycles CPU or faster compatible render engine.
- One approval hero still: 540x960 or 720x1280, increased sampling and denoise.
- Lock all render dimensions to even integers for H.264 yuv420p.
- No paid GPU servers, no cloud AI generation costs, no third-party model licenses.
- Keep output frames as transient GitHub runner data; retain only useful MP4, hero still and editable .blend artifact.
- GitHub free CPU runner speed is an operational constraint, not a quality guarantee.

## Gate-based QA
1. **Geometry**: recognizably improved heads, apparel, bucket and environment; no obvious primitive-only look.
2. **Motion**: test hand-bucket continuity, arm pose and foot placement in all 90 frames.
3. **Render**: consistent lighting, no flicker or missing materials; MP4 opens and duration is 3.00s.
4. **Production**: hero render and motion preview pass visual review before full 10s high-resolution render.

## Long-term reusable system
- Parameterized costumes/colors, character rig definitions, modular prop builders, environment palette, camera presets and pose functions.
- Each new episode receives a script, shot schedule and unique props while reusing the core rig, material library and set dressing.
- Originality check: never trace or reproduce a competitor's sequence frame-for-frame. Apply animation principles, not asset copying.

## Current implementation
- `blender/scene.py`: original technical proof of pipeline.
- `blender/production_scene.py`: upgraded stylized visual and motion prototype.
- `.github/workflows/blender-render.yml`: cloud preview/hero render and MP4 artifact.

**Status is provisional until the new workflow completes and the output is visually inspected.**
