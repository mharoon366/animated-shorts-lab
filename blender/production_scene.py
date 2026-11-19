"""Production-grade LIGHT stylized 3D Bucket War scene; all-original procedural assets.
Blender 4.5; headless in GitHub Actions.
Commands:
 blender -b --python blender/production_scene.py -- --mode preview --seconds 3 --width 360
 blender -b --python blender/production_scene.py -- --mode hero --width 540
"""
import bpy, sys, math, random, os
from mathutils import Vector
from math import sin, cos, pi
random.seed(1325)

argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
def opt(key, default):
    return argv[argv.index(key)+1] if key in argv else default
MODE=opt("--mode","preview")
WIDTH=int(opt("--width","360" if MODE=="preview" else "540"))
SECONDS=min(10,max(1,float(opt("--seconds","3"))))
OUT=os.path.abspath(opt("--out","output"))
FPS=30
FRAMES=int(SECONDS*FPS)
os.makedirs(OUT,exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def material(name,base,rough=.66,metal=0,grain=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*base,1)
    m.use_nodes=True
    tree=m.node_tree; bs=tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*base,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    if grain:
        noise=tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=grain
        noise.inputs["Detail"].default_value=2.1
        noise.inputs["Roughness"].default_value=.76
        mix=tree.nodes.new("ShaderNodeMixRGB")
        mix.blend_type="MULTIPLY"
        mix.inputs[0].default_value=.23
        mix.inputs[1].default_value=(*base,1)
        tree.links.new(noise.outputs["Fac"],mix.inputs[2])
        tree.links.new(mix.outputs[0],bs.inputs["Base Color"])
        # A small bump lends stone/wood/cloth grain without image textures.
        bump=tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.055 if grain<25 else .028
        bump.inputs["Distance"].default_value=.035
        tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return m
ink=material("ink navy charcoal",(.018,.024,.036),.64)
white=material("warm ivory face",(.92,.79,.66),.64)
highlight=material("warm cream eye shine",(.98,.94,.82),.36)
brown=material("brown hair",(.16,.085,.048),.80)
red=material("brick red wool",(.60,.058,.052),.80,grain=18)
redshadow=material("dark crimson cape",(.29,.028,.035),.91,grain=13)
blue=material("royal cobalt wool",(.055,.16,.54),.82,grain=18)
blueshadow=material("deep navy cape",(.025,.069,.22),.90,grain=13)
gold=material("brushed antique gold",(.89,.51,.11),.40,.45,grain=19)
linen=material("embroidered ivory cloth",(.88,.82,.66),.84,grain=22)
leather=material("dark worn brown leather",(.16,.075,.035),.76,grain=21)
wood=material("aged oak",(.43,.19,.07),.67,grain=31)
woodalt=material("honey oak",(.64,.32,.12),.67,grain=27)
metal=material("forged steel blue black",(.16,.19,.23),.38,.72)
stone=material("sunlit limestone",(.67,.57,.45),.91,grain=12)
stone2=material("old worn sandstone",(.43,.36,.29),.91,grain=15)
paving=material("warm cobblestone",(.50,.39,.31),.94,grain=21)
soil=material("earth between cobbles",(.30,.24,.18),.99)
terracotta=material("terracotta roof tiles",(.55,.23,.12),.89,grain=18)
foliage=material("olive green foliage",(.25,.38,.16),.94,grain=12)
foliage2=material("lighter sunlit foliage",(.40,.52,.21),.94,grain=14)
bark=material("olive bark",(.28,.15,.08),.96,grain=22)
water=material("deep aqua water",(.045,.40,.70),.17,.1)
foam=material("water edge glint",(.58,.86,1.0),.12)
dust=material("soft beige dust",(.69,.57,.40),1.0)

def assign(o,mat,parent=None):
    if mat:o.data.materials.append(mat)
    if parent:o.parent=parent
    return o
def empty(name, loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(o)
    o.location=loc
    if parent:o.parent=parent
    return o
def cube(name,loc,dimensions,mat,bevel=.035,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=bpy.context.object;o.name=name;o.location=loc;o.dimensions=dimensions
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    assign(o,mat,parent)
    if bevel:
        mod=o.modifiers.new("Hand softened edges","BEVEL");mod.width=bevel;mod.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o
def ball(name,loc,sc,mat,parent=None,sides=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=sides,ring_count=12)
    o=bpy.context.object;o.name=name;o.location=loc;o.scale=sc
    assign(o,mat,parent)
    for poly in o.data.polygons:poly.use_smooth=True
    return o
def cyl(name,loc,r,h,mat,parent=None,vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=h)
    o=bpy.context.object;o.name=name;o.location=loc
    assign(o,mat,parent)
    b=o.modifiers.new("rounded cylinder rims","BEVEL");b.width=min(h*.16,.024);b.segments=2
    o.modifiers.new("weighted cylinder normals","WEIGHTED_NORMAL")
    return o
def line(name,points,thick,mat,parent=None):
    c=bpy.data.curves.new(name,"CURVE");c.dimensions="3D"
    c.bevel_depth=thick;c.bevel_resolution=3
    s=c.splines.new("POLY");s.points.add(len(points)-1)
    for p,v in zip(s.points,points):p.co=(*v,1)
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o)
    assign(o,mat,parent)
    return o
def mesh(name,verts,faces,mat,parent=None,bevel=0):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    obj=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(obj)
    assign(obj,mat,parent)
    if bevel:
        b=obj.modifiers.new("soft cloth or leather edges","BEVEL");b.width=bevel;b.segments=2
        obj.modifiers.new("weighted corners","WEIGHTED_NORMAL")
    return obj
def tapered(name,zs,rxs,rys,mat,parent=None,yoff=0,segments=12):
    verts=[]
    for z,rx,ry in zip(zs,rxs,rys):
        for i in range(segments):
            a=2*pi*i/segments
            verts.append((rx*cos(a),yoff+ry*sin(a),z))
    faces=[]
    faces.append(tuple(reversed(tuple(range(segments)))))
    for j in range(len(zs)-1):
        for k in range(segments):
            l=j*segments+k;r=j*segments+(k+1)%segments
            faces.append((l,r,r+segments,l+segments))
    faces.append(tuple((len(zs)-1)*segments+i for i in range(segments)))
    return mesh(name,verts,faces,mat,parent,.018)
def k(o,path,f):o.keyframe_insert(data_path=path,frame=f)
def cl(x):return max(0,min(1,x))
def smooth(x):x=cl(x);return x*x*(3-2*x)
def interpolate(keys,t):
    if t<=keys[0][0]:return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<=b:return va+(vb-va)*smooth((t-a)/(b-a))
    return keys[-1][1]

# === Layered hand-built Italian courtyard, no heavy texture downloads ===
# Ground brick shader forms coherent mortar lines; loose pieces are only accents.
ground_paving=material("full courtyard brick paving",(.54,.42,.31),.94)
n=ground_paving.node_tree.nodes;lk=ground_paving.node_tree.links
br=n.new("ShaderNodeTexBrick");br.inputs["Scale"].default_value=48
br.inputs["Color1"].default_value=(.59,.47,.37,1)
br.inputs["Color2"].default_value=(.46,.37,.29,1)
br.inputs["Mortar"].default_value=(.28,.235,.19,1)
br.inputs["Mortar Size"].default_value=.012
lk.new(br.outputs["Color"],n.get("Principled BSDF").inputs["Base Color"])
cube("ground base",(0,3.6,-.20),(34,22,.38),ground_paving,.02)
for i in range(44):
    x=random.uniform(-7,7);y=random.uniform(-2.9,5.7)
    if abs(x)<.72 and abs(y)<.72:continue
    s=random.uniform(.10,.26);h=random.uniform(.008,.016)
    p=cube("individual bevelled cobblestone",(x,y,h/2),(s,random.uniform(.09,.20),h),
           stone if i%5==0 else paving if i%3 else stone2,.016)
    p.rotation_euler.z=random.uniform(-.20,.20)
for x in range(-17,18,3):
    ball("rolling hill silhouette",(x,13,1.0),(3.6,2.8,2.0),foliage,sides=14)
for x in range(-14,17,2):
    cube("layered limestone wall",(x,8,1.3),(2.08,.85,2.7),stone,.08)
    cube("square battlement",(x,8,2.85),(.65,.95,.60),stone2,.05)
    for z in (.55,1.28,2.0):
        line("subtle masonry mortar",[(x-1.02,7.54,z),(x+1.02,7.54,z)],.012,stone2)
for tx,h in [(-12,4.0),(-6,5.8),(0,4.9),(6,5.4),(12,4.3)]:
    cube("fortified town tower",(tx,9.7,h/2),(1.22,1.35,h),stone,.10)
    cube("overhanging tower roof",(tx,9.7,h+.10),(1.53,1.65,.28),terracotta,.04)
    for z in (h*.45,h*.7):
        cube("narrow arched tower window",(tx,8.99,z),(.15,.033,.39),ink,.035)
# Trees: slender trunks and clustered, textured olive canopies.
for i in range(20):
    x=random.uniform(-14,15);y=random.uniform(7.8,12.8)
    if abs(x)<2 and y<10:continue
    height=random.uniform(1.1,2.1)
    cyl("olive trunk",(x,y,height*.33),.085,height*.65,bark,vertices=9)
    for j in range(3):
        ball("distinct olive crown cluster",
            (x+(j-1)*.28,y+(.08 if j%2 else -.10),height*.79+random.uniform(-.08,.25)),
            (.48,.40,.46),foliage2 if (i+j)%3==0 else foliage,sides=12)
# Market set dressing and tall banners placed in architectural depth.
for x,col,name in [(-3.25,red,"Bologna"),(3.15,blue,"Modena")]:
    cyl(name+" flag pole",(x,2.2,2.33),.052,4.66,woodalt,vertices=10)
    ball(name+" brass finial",(x,2.2,4.71),(.11,.11,.14),gold)
    pivot=empty(name+" FLAG_HINGE",(x,2.18,4.15))
    banner=mesh(name+" blue/red stitched flag",[(0,0,0),(1.28,0,-.03),(1.32,0,-.82),(.64,.0,-.70),(0,0,-.86)],
                [(0,1,2,3,4)],col,pivot,.016)
    # Banner edging and geometric unique emblem; readable from a distance.
    line(name+" gold hem",[(.02,-.04,-.03),(1.26,-.04,-.06)],.024,gold,pivot)
    cube(name+" heraldic emblem",(.65,-.06,-.40),(.34,.025,.36),gold,.03,pivot)
    if name=="Bologna":globals()["red_flag"]=pivot
    else:globals()["blue_flag"]=pivot

# === Hero prop: true barrel staves, handles, rings and sloshing water ===
pedestal=cyl("rough stone pedestal",(0,0,.38),.71,.76,stone)
cyl("pedestal carved rim",(0,0,.75),.77,.095,stone2)
for i in range(10):
    a=i*2*pi/10
    line("pedestal radial chisel line",[(.54*cos(a),.54*sin(a),.798),(.75*cos(a),.75*sin(a),.80)],.009,stone2)
bucket=empty("BUCKET CONTROL")
tapered("tapered solid oak bucket",(0,.22,.62),(.31,.35,.37),(.31,.35,.37),wood,bucket)
for i in range(14):
    a=i*2*pi/14
    r=.34
    stave=cube("individually shaped wooden stave",(r*cos(a),r*sin(a),.32),
               (.15,.078,.61),woodalt if i%3==0 else wood,.015,bucket)
    stave.rotation_euler.z=a-pi/2
    line("stave wood grain",[(r*cos(a),r*sin(a)-.043,.14),(r*cos(a),r*sin(a)-.043,.51)],
         .004,leather,bucket)
for z in (.16,.54):
    cyl("steel wrap ring",(0,0,z),.395,.052,metal,bucket)
    for i in range(8):
        a=i*2*pi/8
        ball("iron ring rivet",(.397*cos(a),.397*sin(a),z),(.022,.022,.022),gold,bucket,sides=10)
cyl("water surface",(0,0,.615),.352,.025,water,bucket)
for i in range(3):
    r=.14+i*.055
    line("water circular reflection",[(r*cos(j*2*pi/32),r*sin(j*2*pi/32),.639)
        for j in range(33)],.012,foam,bucket)
handle_pts=[(.40*cos(pi-j*pi/28),0,.53+.51*sin(pi-j*pi/28)) for j in range(29)]
line("BUCKET handle arched",(handle_pts),.042,woodalt,bucket)
for x in (-.40,.40):
    ball("handle pin",(x,-.020,.55),(.075,.061,.075),metal,bucket)
bucket.location=(0,-.285,.86)

# === Reusable character rig and original identity ===
def character(name,color,cape_color,x,emblem):
    root=empty(name+" ROOT",(x,-.30,0))
    torso=empty(name+" TORSO",(0,0,.89),root)
    # Shaped, tailored coat rather than a primitive cube.
    tapered(name+" fitted coat",(.04,.20,.65,.86),(.42,.40,.32,.35),
            (.29,.28,.235,.25),color,torso)
    cube(name+" belt",(0,-.292,.25),(.79,.065,.115),leather,.03,torso)
    cube(name+" antiqued belt buckle",(0,-.34,.25),(.16,.048,.105),gold,.01,torso)
    # Costuming: front panels, gold decorative piping and heraldry.
    line(name+" side trim",[(-.23,-.267,.22),(-.21,-.24,.69),(-.17,-.22,.83)],.017,gold,torso)
    line(name+" opposite trim",[(.23,-.267,.22),(.21,-.24,.69),(.17,-.22,.83)],.017,gold,torso)
    cube(name+" crest patch",(0,-.287,.58),(.24,.045,.31),linen,.03,torso)
    if emblem=="hawk":
        ball(name+" hawk crest body",(0,-.32,.59),(.083,.018,.10),gold,torso)
        line(name+" hawk wing",[(-.14,-.33,.65),(0,-.33,.57),(.14,-.33,.65)],.022,ink,torso)
    else:
        line(name+" tower crest",[(0,-.327,.46),(0,-.327,.69)],.022,red,torso)
        line(name+" cross crest",[(-.08,-.327,.60),(.08,-.327,.60)],.022,red,torso)
    # Cape as an articulated curved triangle-mesh, visibly separate from coat.
    cape=empty(name+" CAPE HINGE",(0,.25,.82),torso)
    capeverts=[(-.30,0,0),(.30,0,0),(.44,.19,-.96),(.08,.29,-1.04),(-.42,.14,-.92)]
    capeobj=mesh(name+" tailored curved cape",capeverts,[(0,1,2,3,4)],cape_color,cape,.017)
    # The round head is a thick disc with proper material response.
    head=empty(name+" HEAD CONTROL",(0,-.027,1.39),torso)
    ball(name+" neck",(0,0,-.12),(.12,.12,.17),white,head)
    ball(name+" brown hair underneath", (0,.095,.07),(.485,.31,.48),brown,head)
    ball(name+" big shaded round face",(0,-.12,.06),(.47,.305,.465),white,head,sides=40)
    # Explicit eyes/brows/mouth on front surface: readable mobile expression.
    eyes=[];brows=[]
    for side in (-1,1):
        ball(name+" sclera "+str(side),(side*.165,-.399,.11),(.092,.033,.100),highlight,head)
        eye=ball(name+" pupil "+str(side),(side*.170,-.429,.11),(.040,.024,.065),ink,head)
        ball(name+" pupil glint "+str(side),(side*.165-.014,-.448,.138),(.013,.009,.019),highlight,head,sides=12)
        brow=empty(name+" brow control "+str(side),(side*.16,-.448,.275),head)
        cube(name+" thick expressive brow "+str(side),(0,0,0),(.235,.035,.046),ink,.017,brow)
        brows.append(brow);eyes.append(eye)
    ball(name+" small round nose",(0,-.425,-.04),(.057,.028,.045),white,head)
    mouth=ball(name+" changing mouth",(0,-.433,-.16),(.12,.023,.052),ink,head)
    smile=line(name+" subtle lower smile",[(-.09,-.434,-.14),(0,-.455,-.165),(.09,-.434,-.14)],.013,ink,head)
    # Cloth beret made of two pieces, detailed with a stitched band.
    ball(name+" dark hat brim",(0,-.08,.45),(.53,.34,.095),ink,head,sides=36)
    ball(name+" beret crown",(0,-.035,.53),(.50,.345,.20),color,head,sides=36)
    line(name+" beret band",[(-.39,-.30,.50),(0,-.36,.48),(.39,-.30,.50)],.019,gold,head)
    # Jointed arms: jacket upper sleeves, black forearms and gloves.
    arms=[];elbows=[]
    for side in (-1,1):
        shoulder=empty(name+" shoulder "+str(side),(side*.365,0,.69),torso)
        ball(name+" sleeve cap",(0,0,-.075),(.155,.16,.17),color,shoulder)
        tapered(name+" sleeve "+str(side),(-.40,-.08),(.085,.135),(.10,.14),color,shoulder)
        elbow=empty(name+" elbow "+str(side),(0,0,-.40),shoulder)
        cyl(name+" black forearm "+str(side),(0,-.025,-.16),.050,.32,ink,elbow)
        ball(name+" glove "+str(side),(0,-.055,-.32),(.105,.09,.104),ink,elbow)
        for finger in (-1,0,1):
            ball(name+" glove finger",(finger*.055,-.112,-.35),(.035,.055,.049),ink,elbow,sides=12)
        arms.append(shoulder);elbows.append(elbow)
    legs=[];knees=[];feet=[]
    for side in (-1,1):
        hip=empty(name+" hip "+str(side),(side*.205,0,.88),root)
        tapered(name+" trouser leg "+str(side),(-.36,-.01),(.091,.13),(.094,.12),ink,hip)
        knee=empty(name+" knee "+str(side),(0,0,-.36),hip)
        cyl(name+" boot shaft "+str(side),(0,-.01,-.19),.085,.40,leather,knee)
        foot=empty(name+" foot pivot "+str(side),(0,0,-.39),knee)
        ball(name+" shaped leather shoe "+str(side),(0,-.12,-.06),(.13,.24,.11),leather,foot)
        cube(name+" gold shoe clasp "+str(side),(0,-.33,-.033),(.10,.02,.055),gold,.005,foot)
        legs.append(hip);knees.append(knee);feet.append(foot)
    return dict(root=root,torso=torso,head=head,arms=arms,elbows=elbows,
                cape=cape,legs=legs,knees=knees,feet=feet,brows=brows,
                mouth=mouth,smile=smile,eyes=eyes)

guard=character("BOLOGNA_GUARD",red,redshadow,-1.15,"tower")
thief=character("MODENA_THIEF",blue,blueshadow,.85,"hawk")

# Lightweight FX with actual 3D placement.
droplets=[]
for i in range(12):
    droplets.append(ball("independent ballistic water droplet "+str(i),(0,0,-30),
                         (.045,.045,.07),water,sides=12))
dust_puffs=[]
for i in range(6):
    dust_puffs.append(ball("ground contact dust puff "+str(i),(0,0,-30),
                          (.11,.13,.10),dust,sides=12))

# Light and camera. Contact shadows and background parallax are real 3D.
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.49,.64,.83,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.65
def lamp(name,loc,energy,size,rgb):
    bpy.ops.object.light_add(type="AREA",location=loc)
    o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.size=size;o.data.color=rgb
    o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat("-Z","Y").to_euler()
lamp("large warm late-afternoon key",(-6,-5,10),1250,7,(1,.82,.65))
lamp("soft cool sky bounce",(4,-3,7),550,9,(.68,.82,1))
lamp("separating warm rim light",(2,4,8),900,6,(1,.89,.69))
bpy.ops.object.camera_add(location=(0,-10.4,3.38))
cam=bpy.context.object;cam.name="PRODUCTION CAMERA"
scene=bpy.context.scene;scene.camera=cam
cam.data.type="PERSP";cam.data.lens=56
cam.data.dof.use_dof=False

# Timeline: anticipation -> grip -> lift -> pursuit; no disjoint image interpolation.
N=max(90,FRAMES)
for frame in range(1,N+1):
    t=(frame-1)/30
    blue_x=interpolate([(0,.85),(2.12,.85),(2.36,.95),(3.0,1.78),
                        (5,5.0),(10,13.0)],t)
    red_x=interpolate([(0,-1.15),(2.12,-1.15),(2.40,-1.05),(3,-.49),
                       (5,2.8),(10,9)],t)
    reach=smooth((t-.61)/.48)*(1-smooth((t-2.18)/.28))
    lift=smooth((t-1.34)/.72)
    run=smooth((t-2.09)/.35)
    guard_run=smooth((t-2.0)/.38)
    surprised=smooth((t-1.45)/.21)
    # Animate root, gravity-inspired bob, body lean, cape lag and facial acting.
    for actor,x,phase,lean,alarm in [(thief,blue_x,run,.32*reach-.18*run,0),
                                    (guard,red_x,guard_run,.19*guard_run,surprised)]:
        actor["root"].location=(x,-.25 if actor is thief else -.32,.025+phase*.018*abs(sin((t-2.0)*16)))
        actor["torso"].rotation_euler.y=lean
        actor["torso"].rotation_euler.x=0  # keep IK working in the arm/shoulder plane
        actor["head"].rotation_euler.y=.10*sin(t*3.3)
        actor["head"].rotation_euler.z=(-.09*reach if actor is thief else .11*alarm)
        actor["cape"].rotation_euler.x=-.13-.23*phase+.08*sin(t*7.1)
        actor["cape"].rotation_euler.y=.10*sin(t*5.2-.55)
        actor["mouth"].scale.z=.016+.135*alarm
        actor["mouth"].scale.x=.085+.060*alarm
        actor["smile"].scale=(1-alarm*.97,1-alarm*.97,1-alarm*.97)
        k(actor["root"],"location",frame)
        for node,prop in [(actor["torso"],"rotation_euler"),
                          (actor["head"],"rotation_euler"),
                          (actor["cape"],"rotation_euler"),
                          (actor["mouth"],"scale"),(actor["smile"],"scale")]:
            k(node,prop,frame)
        for j,b in enumerate(actor["brows"]):
            b.rotation_euler.y=(-.23 if j else .23)*(1+alarm*.6)
            b.location.z=.275+alarm*.07
            k(b,"rotation_euler",frame);k(b,"location",frame)
        for j,(arm,elbow) in enumerate(zip(actor["arms"],actor["elbows"])):
            a=sin((t-2)*16 + j*pi)
            if actor is thief:
                arm.rotation_euler.y= (.42*reach if j==0 else -.29*reach) + a*.55*phase
                arm.rotation_euler.x= -.14*reach
                elbow.rotation_euler.y=(-.17*reach if j==0 else .12*reach)
            else:
                arm.rotation_euler.y= (.23*alarm if j==0 else -.12*alarm)+ a*.66*phase
                elbow.rotation_euler.y=.14*alarm
            k(arm,"rotation_euler",frame);k(elbow,"rotation_euler",frame)
        # Eyes follow the bucket (thief) and chase (guard) with separate acting controls.
        for eye in actor["eyes"]:
            neutral=.170 if eye.location.x>0 else -.170
            eye.location.x=neutral+(-.035*reach if actor is thief else .033*alarm)
            k(eye,"location",frame)
        # Ground-oriented gait: two-bone leg solution with a stance / swing cycle.
        # A planted stance receives little height motion; swing moves the boot on an arc.
        for j,(leg,knee,foot) in enumerate(zip(actor["legs"],actor["knees"],actor["feet"])):
            old_step=sin((t-2)*16+j*pi)*phase
            old_upper=.72*old_step
            old_knee=max(0,-old_step)*.42
            stance_weight=smooth((t-2.12)/.39)*phase
            cycle=((t-2.24)*2.25+j*.5)%1.0
            if cycle<.56:
                off=.125*(1-2*cycle/.56)
                foot_lift=0
            else:
                frac=(cycle-.56)/.44
                off=-.125+.25*smooth(frac)
                foot_lift=.18*sin(frac*pi)
            # Hip origin under root, foot pivot at a stable ground-level target.
            hip_z=actor["root"].location.z+.88
            dx=off
            dz=(.190+foot_lift)-hip_z
            l1=.36;l2=.39
            reachdist=max(abs(l1-l2)+.002,min(l1+l2-.003,math.hypot(dx,dz)))
            cosq=max(-1,min(1,(reachdist**2-l1*l1-l2*l2)/(2*l1*l2)))
            q2=math.acos(cosq)
            theta=math.atan2(-dx,-dz)
            q1=theta-math.atan2(l2*sin(q2),l1+l2*cos(q2))
            leg.rotation_euler.y=(1-stance_weight)*old_upper+stance_weight*q1
            knee.rotation_euler.y=(1-stance_weight)*old_knee+stance_weight*q2
            foot.rotation_euler.y=(1-stance_weight)*(-.16*old_step)+stance_weight*(-.72*(q1+q2))
            k(leg,"rotation_euler",frame)
            k(knee,"rotation_euler",frame)
            k(foot,"rotation_euler",frame)
    # One continuous physical bucket path; no duplicate object substitutions.
    if t<1.35:
        bucket.location=(0,0,.86)
        bucket.rotation_euler=(0,0,0)
    elif t<2.10:
        u=smooth((t-1.35)/.75)
        bucket.location=((blue_x-.77)*u, -.285, .86+.46*u)
        bucket.rotation_euler=(.12*u,.15*u,0)
    else:
        bucket.location=(blue_x-.77+.12*run,-.285,1.30+.08*run*abs(sin(t*16)))
        bucket.rotation_euler=(.11*sin(t*9),.13*sin(t*12),-.11*sin(t*14))
    k(bucket,"location",frame);k(bucket,"rotation_euler",frame)
    # Analytic two-bone IK, locking the thief's left glove to the bucket handle.
    # The same moving bucket object is followed during lift and escape.
    if t>=.60:
        arm=thief["arms"][0]
        elbow=thief["elbows"][0]
        lean=thief["torso"].rotation_euler.y
        rootz=thief["root"].location.z
        # Target = near-side bucket handle pin, including a modest handle swing.
        target_x=bucket.location.x+.395
        target_z=bucket.location.z+.54
        dx_world=target_x-blue_x
        dz_world=target_z-(rootz+.89)
        # Transform target into torso space before solving the linked arm.
        lx=cos(lean)*dx_world-sin(lean)*dz_world
        lz=sin(lean)*dx_world+cos(lean)*dz_world
        dx=lx+.365      # shoulder origin in torso coordinates
        dz=lz-.69
        upper=.40
        forearm=.32
        length=max(abs(upper-forearm)+.002,min(upper+forearm-.003,math.hypot(dx,dz)))
        c2=max(-1,min(1,(length*length-upper*upper-forearm*forearm)/(2*upper*forearm)))
        q2=math.acos(c2)
        theta=math.atan2(-dx,-dz)
        q1=theta-math.atan2(forearm*sin(q2),upper+forearm*cos(q2))
        # Ease into the physical grip, then hold the connection continuously.
        w=smooth((t-.60)/.67)
        arm.rotation_euler.y=(1-w)*arm.rotation_euler.y+w*q1
        arm.rotation_euler.x=0
        elbow.rotation_euler.y=(1-w)*elbow.rotation_euler.y+w*q2
        k(arm,"rotation_euler",frame)
        k(elbow,"rotation_euler",frame)
    for i,d in enumerate(droplets):
        age=t-(2.24+i*.11)
        if 0<=age<.54:
            bx=interpolate([(0,.85),(2.25,.85),(3,1.78),(5,5.0)],2.24+i*.11)
            d.location=(bx-.36+age*(.6+(i%3)*.33), -.21+(.05*(i%4)),
                        1.40+age*(1.4+.16*(i%4))-4.8*age*age)
        else:d.location=(0,0,-30)
        k(d,"location",frame)
    for i,d in enumerate(dust_puffs):
        if t>2.15:
            phase=(t*2.6+i*.19)%1
            d.location=(blue_x-phase*.6,-.20,.05+phase*.26)
            d.scale=(.12+phase*.08,.12+phase*.10,.08+phase*.04)
        else:d.location=(0,0,-30)
        k(d,"location",frame);k(d,"scale",frame)
    for i,f in enumerate((red_flag,blue_flag)):
        f.rotation_euler.x=.06*sin(t*2.6+i)
        f.rotation_euler.z=.10*sin(t*3.4+i)
        k(f,"rotation_euler",frame)
    # Slow, spatially coherent dolly as thief begins escape.
    cx=interpolate([(0,0),(2.25,0),(3,.28),(10,7.5)],t)
    cam.location=(cx,-10.2,3.25+.045*sin(t*.8))
    cam.rotation_euler=(Vector((cx,0,1.40))-cam.location).to_track_quat("-Z","Y").to_euler()
    k(cam,"location",frame);k(cam,"rotation_euler",frame)

# Output: modest rendering cost but significantly richer geometry and materials.
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=11 if MODE=="preview" else 48
scene.cycles.use_denoising=True
scene.render.resolution_x=WIDTH if WIDTH%2==0 else WIDTH+1
scene.render.resolution_y=round(scene.render.resolution_x*16/9/2)*2
scene.render.resolution_percentage=100
scene.render.fps=FPS
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
scene.view_settings.view_transform="Standard"
scene.render.image_settings.color_mode="RGBA"
scene.frame_start=1;scene.frame_end=FRAMES
os.makedirs(OUT,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,"bucket_war_production.blend"))
if MODE=="hero":
    scene.frame_set(min(49,N))
    scene.render.filepath=os.path.join(OUT,"bucket_war_hero.png")
    print("HERO RENDER",scene.render.resolution_x,scene.render.resolution_y,flush=True)
    bpy.ops.render.render(write_still=True)
else:
    # Blender official builds include FFmpeg libraries for direct H.264 export,
    # so there is no fragile third-party GitHub setup step.
    scene.render.image_settings.file_format="FFMPEG"
    scene.render.image_settings.color_mode="RGB"
    scene.render.ffmpeg.format="MPEG4"
    scene.render.ffmpeg.codec="H264"
    scene.render.ffmpeg.constant_rate_factor="HIGH"
    scene.render.filepath=os.path.join(OUT,"bucket_war_production_test.mp4")
    print("PREVIEW MPEG4",scene.frame_end,scene.render.resolution_x,scene.render.resolution_y,flush=True)
    bpy.ops.render.render(animation=True)
print("RENDER COMPLETE",flush=True)
