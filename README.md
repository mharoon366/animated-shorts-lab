# Animated Shorts Lab

A free, scripted Blender animation pipeline controlled through GitHub.

## Current status

The first stage is a **technical render test**, not the final character or animation quality. It verifies that the remote Ubuntu runner can install Blender, build an original 3D scene, render continuous keyframed motion, assemble an MP4, and provide a downloadable artifact.

### First scene: Bucket War

- Original stylized 3D characters for Bologna and Modena
- A wooden bucket and medieval courtyard assembled with Blender Python
- Keyframed character, bucket and camera motion with true 3D geometry
- Cycles CPU render at 30 fps
- Initial 2-second low-resolution preview, then higher-quality iterations

## Get the first video

Open the [GitHub Actions page](../../actions/workflows/blender-render.yml), open the latest successful **Blender Bucket War Pilot** run, and download the `bucket-war-first-render` artifact. The ZIP contains `bucket_war_preview.mp4`.

## Source

- `blender/scene.py`: creates, animates and renders the procedural scene
- `.github/workflows/blender-render.yml`: installs Blender and FFmpeg, runs the renderer, assembles video and uploads the result
- `.gitignore`: excludes rendered outputs and automatic backup files

The reference creator's footage, characters, textures and proprietary assets are not included. Future Shorts should develop an original visual identity while applying professional animation principles.

## Roadmap

1. Confirm a successful end-to-end automatic render.
2. Improve original character topology, facial rigs, materials and scene layout.
3. Improve foot planting, hand-to-object constraints, weight, arcs, secondary motion and effects.
4. Review motion frame-by-frame, approve an initial 10-second pilot, then raise quality to 1080 × 1920.
5. Add reusable narration, captions, audio and episode templates.

This repository uses GitHub's standard public-repository runners, not paid GPU instances. Rendering speed and visual quality will require iterative testing.

## Production-quality upgrade

The newer [production scene](blender/production_scene.py) uses a shaped character rig, procedural weathering, modular medieval architecture, detailed bucket hardware, and continuous three-second choreography. [Production quality and geometry budget](PRODUCTION_STANDARD.md) sets visual/animation targets. The automated workflow exports both a hero still and a 3-second H.264 motion test. This is a **quality gate**, not yet a complete Short.
