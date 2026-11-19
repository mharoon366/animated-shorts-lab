"""Frame-by-frame motion diagnostics for a Blender .blend scene.
Runs without external Python dependencies:
blender -b output/hero/bucket_war_production.blend --python blender/quality_gate.py -- --out output/quality_report.json
It does not replace visual direction or animator approval.
"""
import bpy, json, math, sys, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
def opt(name,default):
    return argv[argv.index(name)+1] if name in argv else default
outfile=os.path.abspath(opt("--out","output/quality_report.json"))
scene=bpy.context.scene
bucket=bpy.data.objects["BUCKET CONTROL"]
red=bpy.data.objects["BOLOGNA_GUARD ROOT"]
blue=bpy.data.objects["MODENA_THIEF ROOT"]
glove=bpy.data.objects["MODENA_THIEF glove -1"]
faces=[bpy.data.objects["MODENA_THIEF big shaded round face"],
       bpy.data.objects["BOLOGNA_GUARD big shaded round face"]]
pin=next(o for o in bucket.children if o.name.startswith("handle pin") and o.location.x>0)
frames=list(range(scene.frame_start,scene.frame_end+1))
samples=[]
previous=None
for f in frames:
    scene.frame_set(f)
    bpy.context.view_layer.update()
    t=(f-1)/scene.render.fps
    xyz={name:tuple(round(v,5) for v in obj.matrix_world.translation)
         for name,obj in (("bucket",bucket),("red",red),("blue",blue),("glove",glove),("pin",pin))}
    grip=(glove.matrix_world.translation-pin.matrix_world.translation).length
    screen=[]
    for face in faces:
        p=world_to_camera_view(scene,scene.camera,face.matrix_world.translation)
        screen.append([round(p.x,5),round(p.y,5),round(p.z,5)])
    sample={"frame":f,"seconds":round(t,4),"positions":xyz,
            "grip_gap_m":round(grip,5),"face_viewport":screen}
    if previous is not None:
        sample["bucket_step_m"] = round(
            (Vector(xyz["bucket"])-Vector(previous["positions"]["bucket"])).length,5)
    samples.append(sample);previous=sample
contact=[s for s in samples if s["seconds"]>=1.35]
gap=[s["grip_gap_m"] for s in contact]
jumps=[s.get("bucket_step_m",0) for s in samples]
face_oob={str(i):sum(not (0.04<=s["face_viewport"][i][0]<=.96 and
                           0.04<=s["face_viewport"][i][1]<=.96)
                     for s in samples)
          for i in range(len(faces))}
report={
    "note":"Automated numerical checks are not equivalent to animator-level visual QA.",
    "fps":scene.render.fps,
    "frames_checked":len(samples),
    "duration_seconds":len(samples)/scene.render.fps,
    "max_bucket_step_m":round(max(jumps),4),
    "max_bucket_speed_m_per_s":round(max(jumps)*scene.render.fps,3),
    "grip_contact_window_s":[1.35,round((frames[-1]-1)/scene.render.fps,3)],
    "mean_hand_to_bucket_pin_gap_m":round(sum(gap)/len(gap),4) if gap else None,
    "max_hand_to_bucket_pin_gap_m":round(max(gap),4) if gap else None,
    "face_center_outside_safe_viewport_frames":face_oob,
    "warnings":[],
    "frame_samples":samples
}
if max(jumps)>.20:
    report["warnings"].append("Bucket position jump greater than 0.20 m in a single frame")
if gap and max(gap)>.35:
    report["warnings"].append("Hand not reliably attached to bucket pin (gap above 0.35 m)")
if sum(face_oob.values()):
    report["warnings"].append("Face center leaves 4%-96% safe viewport at least once")
os.makedirs(os.path.dirname(outfile),exist_ok=True)
with open(outfile,"w") as fp:json.dump(report,fp,indent=2)
print("QUALITY REPORT",json.dumps({k:v for k,v in report.items() if k!="frame_samples"}),flush=True)
if report["warnings"]:
    raise SystemExit("FAIL: frame-level motion QA reported: "+", ".join(report["warnings"]))
