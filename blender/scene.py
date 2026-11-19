"""Bucket War: original procedural Blender animation test.

Run: blender -b --python blender/scene.py -- --seconds 2 --width 360
Rendering intentionally low-resolution for first end-to-end GitHub Actions test.
Replace procedural models with production-quality assets after pipeline is verified.
"""
import bpy
import sys
import os
import math
import random
from mathutils import Vector

random.seed(26)
argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
def option(name, default):
    return argv[argv.index(name)+1] if name in argv else default

DURATION=float(option("--seconds","2"))
WIDTH=int(option("--width","360"))
FPS=30
NFRAMES=round(DURATION*FPS)
OUT=os.path.abspath(option("--out","output/frames"))
os.makedirs(OUT,exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name,color,roughness=.7,metallic=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=roughness
    bs.inputs["Metallic"].default_value=metallic
    return m

sand=mat("sandstone courtyard",(.52,.40,.29))
stone=mat("medieval stone",(.70,.62,.48))
wall=mat("worn castle limestone",(.52,.51,.43))
roof=mat("terracotta",(.50,.20,.11))
green=mat("rolling green hill",(.18,.38,.18))
red=mat("Bologna red",(.60,.045,.055))
redcape=mat("Bologna cape shade",(.34,.025,.036))
blue=mat("Modena blue",(.05,.13,.61))
bluecape=mat("Modena cape shade",(.025,.055,.31))
gold=mat("gold",(.95,.58,.11),.38)
ivory=mat("skin",(.95,.84,.72))
black=mat("ink black",(.018,.020,.026))
wood=mat("bucket timber",(.52,.25,.085))
woodlight=mat("bucket staves",(.70,.38,.14))
iron=mat("bucket forged iron",(.16,.20,.23),.3,.63)
water=mat("water",(.075,.48,.72),.24,.12)
dust=mat("dust",(.75,.68,.49))

def parent_to(o,p):
    if p is not None:o.parent=p
    return o
def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(o)
    o.location=loc
    parent_to(o,parent)
    return o
def box(name,loc,dims,ma,parent=None,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=bpy.context.object
    o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.location=loc
    o.data.materials.append(ma)
    parent_to(o,parent)
    if bevel:
        mod=o.modifiers.new("Rounded edges","BEVEL")
        mod.width=bevel;mod.segments=2
        o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o
def sphere(name,loc,radii,ma,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12)
    o=bpy.context.object;o.name=name;o.location=loc;o.scale=radii
    o.data.materials.append(ma);parent_to(o,parent)
    for face in o.data.polygons:face.use_smooth=True
    return o
def cylinder(name,loc,radius,depth,ma,parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth)
    o=bpy.context.object;o.name=name;o.location=loc
    o.data.materials.append(ma);parent_to(o,parent)
    o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o
def tube(name,pts,radius,ma,parent=None):
    cu=bpy.data.curves.new(name,"CURVE")
    cu.dimensions="3D"
    cu.bevel_depth=radius
    cu.bevel_resolution=2
    spline=cu.splines.new("POLY")
    spline.points.add(len(pts)-1)
    for p,point in zip(spline.points,pts):p.co=(*point,1)
    o=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(ma);parent_to(o,parent)
    return o
def keyed(obj,path,fr):
    obj.keyframe_insert(data_path=path,frame=fr)
def clamp(v):return max(0,min(1,v))
def smooth(v):
    v=clamp(v);return v*v*(3-2*v)
def lerp(a,b,u):return a+(b-a)*u
def travel(t,keys):
    if t<=keys[0][0]:return keys[0][1]
    for (t0,v0),(t1,v1) in zip(keys,keys[1:]):
        if t<=t1:return lerp(v0,v1,smooth((t-t0)/(t1-t0)))
    return keys[-1][1]

# Native geometry. This is a genuinely three-dimensional scene with depth.
box("COURTYARD",(0,2.3,-.13),(30,17,.25),sand)
for i in range(80):
    x=random.uniform(-8,8);y=random.uniform(-1,5)
    item=box("handset paving stone",(x,y,.003),
             (random.uniform(.25,.73),random.uniform(.23,.55),.024),stone,bevel=.02)
    item.rotation_euler.z=random.uniform(-.2,.2)
for x in range(-12,15,3):
    sphere("green distant hill",(x,8.6,.55),(3.0,1.4,1.8),green)
for x in range(-10,13,2):
    box("castle outer wall",(x,6.6,1.25),(2.1,.65,2.55),wall)
    box("battlement merlon",(x,6.6,2.66),(.5,.77,.32),stone)
for x in (-9,-4,2,7,11):
    h=random.uniform(3.4,5.0)
    box("Italian medieval tower",(x,8,h/2),(1.2,1.1,h),stone)
    box("tile roof",(x,8,h+.16),(1.55,1.52,.31),roof)
    for z in (h*.50,h*.72):
        box("tower slit",(x,7.43,z),(.08,.02,.27),black,bevel=0)
# Small well pedestal.
cylinder("BUCKET PEDESTAL",(0,0,.33),.64,.66,stone)
cylinder("pedestal top",(0,0,.66),.73,.09,wall)

# Prop is one independently animated rig.
bucket=empty("BUCKET PROP ROOT")
cylinder("wooden bucket body",(0,0,.31),.35,.62,wood,bucket)
for i in range(12):
    a=i*math.tau/12
    stave=box("oak stave",(.342*math.cos(a),.342*math.sin(a),.31),
              (.165,.085,.62),woodlight if i%3 else wood,bucket,.014)
    stave.rotation_euler.z=a-math.pi/2
for z in (.12,.53):
    cylinder("iron reinforcement band",(0,0,z),.392,.055,iron,bucket)
cylinder("waterline",(0,0,.625),.328,.023,water,bucket)
tube("curved bucket handle",[(.395*math.cos(math.pi-i*math.pi/20),0,
                              .60+.47*math.sin(math.pi-i*math.pi/20)) for i in range(21)],
     .030,iron,bucket)
bucket.location=(0,0,.70)

def character(name,base,cape_mat,x):
    root=empty(name+" root",(x,-.20,0))
    body=empty(name+" torso",parent=root)
    box(name+" tunic",(0,0,1.29),(.67,.40,.78),base,body,.10)
    box(name+" crest background",(0,-.22,1.40),(.24,.035,.29),gold,body,.02)
    cape=empty(name+" cape hinge",(0,.19,1.60),body)
    box(name+" cloth cape",(0,.17,-.39),(.75,.09,.93),cape_mat,cape,.04)
    sphere(name+" circular face",(0,-.015,2.13),(.43,.385,.43),ivory,body)
    sphere(name+" beret brim",(0,-.02,2.48),(.47,.38,.095),black,body)
    sphere(name+" colored beret",(0,-.01,2.56),(.45,.39,.17),base,body)
    for side in (-1,1):
        sphere(name+" black eye",(side*.14,-.395,2.16),(.048,.026,.059),black,body)
        eyebrow=box(name+" eyebrows",(side*.14,-.417,2.31),(.20,.026,.034),black,body,.008)
        eyebrow.rotation_euler.y=side*.24
    mouth=sphere(name+" mouth",(0,-.402,1.94),(.095,.026,.05),black,body)
    arms=[]
    for side in (-1,1):
        p=empty(name+" arm pivot "+str(side),(side*.37,0,1.51),body)
        cylinder(name+" skinny arm",(0,0,-.25),.047,.49,black,p)
        sphere(name+" black glove",(0,-.025,-.49),(.095,.09,.09),black,p)
        arms.append(p)
    legs=[]
    for side in (-1,1):
        p=empty(name+" leg pivot "+str(side),(side*.19,0,.91),root)
        cylinder(name+" slim leg",(0,0,-.33),.053,.65,black,p)
        sphere(name+" foot",(0,-.13,-.67),(.12,.22,.07),black,p)
        legs.append(p)
    return dict(root=root,body=body,cape=cape,mouth=mouth,arms=arms,legs=legs)

guard=character("RED GUARD",red,redcape,-1.60)
thief=character("BLUE THIEF",blue,bluecape,1.72)

flags=[]
for x,ma,name in ((-3.15,red,"Bologna"),(3.15,blue,"Modena")):
    cylinder(name+" pole",(x,2.9,2.15),.055,4.3,wood)
    pivot=empty(name+" flag hinge",(x,2.8,3.78))
    box(name+" flag fabric",(.55,0,-.33),(1.1,.05,.73),ma,pivot,.012)
    box(name+" flag heraldry",(.55,-.04,-.33),(.23,.025,.31),gold,pivot,.01)
    flags.append(pivot)

# Plausible lights and physically coherent cast shadows.
bpy.context.scene.world.use_nodes=True
bpy.context.scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.49,.65,.81,1)
bpy.context.scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.8
def area(name,loc,power,color,size):
    bpy.ops.object.light_add(type="AREA",location=loc)
    o=bpy.context.object;o.name=name
    o.data.energy=power;o.data.color=color;o.data.size=size
    o.rotation_euler=(Vector((0,0,1.25))-o.location).to_track_quat("-Z","Y").to_euler()
area("warm sun",(-6,-6,9),950,(1,.85,.70),8)
area("cool sky fill",(5,-3,7),650,(.73,.84,1),9)
area("rim light",(0,5,7),500,(1,.93,.73),8)

bpy.ops.object.camera_add(location=(0,-12,4.10))
cam=bpy.context.object;cam.name="cinematic camera"
scene=bpy.context.scene
scene.camera=cam
cam.data.type="ORTHO"
cam.data.ortho_scale=7.4

def move_actor(actor,x,t,run=False,reaction=False,reach=False):
    root=actor["root"]
    root.location=(x,-.2,.025 + (.045*abs(math.sin(15*t)) if run else 0))
    actor["body"].rotation_euler.y=(-.21 if run else (.15 if reach else 0))
    actor["cape"].rotation_euler.x=-.12-.12*math.sin(10*t)
    actor["mouth"].scale=(.09,.025,.13 if reaction else .05)
    for j,p in enumerate(actor["legs"]):
        p.rotation_euler.y=math.sin(16*t+j*math.pi)*.62 if run else 0
        keyed(p,"rotation_euler",fr)
    for j,p in enumerate(actor["arms"]):
        p.rotation_euler.y=(-.72 if reach else math.sin(16*t+j*math.pi+math.pi)*.47 if run else 0)
        keyed(p,"rotation_euler",fr)
    for p,path in ((root,"location"),(actor["body"],"rotation_euler"),
                   (actor["cape"],"rotation_euler"),(actor["mouth"],"scale")):
        keyed(p,path,fr)

for fr in range(1,NFRAMES+1):
    t=(fr-1)/FPS
    thief_x=travel(t,[(0,1.72),(.4,.60),(.9,.58),(1.15,.75),(2.0,3.3),(10,18)])
    guard_x=travel(t,[(0,-1.6),(1.05,-1.6),(1.40,-1.45),(2.0,-.3),(10,12)])
    move_actor(thief,thief_x,t,run=t>1.1,reaction=False,reach=.34<t<1.05)
    move_actor(guard,guard_x,t,run=t>1.4,reaction=t>1.05)
    if t<.60:
        bucket.location=(0,0,.70)
    elif t<1.13:
        u=smooth((t-.60)/.53)
        bucket.location=(.45*u,-.13*u,.70+.22*u)
    else:
        bucket.location=(thief_x-.25,-.26, .91+.075*abs(math.sin(t*16)))
    bucket.rotation_euler.y=.1*math.sin(t*12) if t>.6 else 0
    keyed(bucket,"location",fr);keyed(bucket,"rotation_euler",fr)
    for i,f in enumerate(flags):
        f.rotation_euler.z=.08*math.sin(3.3*t+i*2)
        keyed(f,"rotation_euler",fr)
    cam.location=(travel(t,[(0,0),(1.3,0),(2,1.2),(10,13)]),-12,4.1)
    cam.rotation_euler=(Vector((cam.location.x,0,1.7))-cam.location).to_track_quat("-Z","Y").to_euler()
    keyed(cam,"location",fr);keyed(cam,"rotation_euler",fr)

scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=8 if WIDTH<=360 else 24
scene.cycles.use_denoising=True
scene.render.resolution_x=WIDTH
scene.render.resolution_y=round(WIDTH*16/9)
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.fps=FPS
scene.render.filepath=os.path.join(OUT,"frame_")
scene.frame_start=1
scene.frame_end=NFRAMES
scene.view_settings.view_transform="Standard"
# Set no GPU requirements; the standard free public-repo Ubuntu runner uses CPU.
scene.frame_set(1)
os.makedirs("output",exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("output/bucket_war_pilot.blend"))
print("RENDER CONFIG",NFRAMES,FPS,WIDTH,scene.render.resolution_y,flush=True)
bpy.ops.render.render(animation=True)
print("DONE",flush=True)
