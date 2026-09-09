"""A bounded kiln-shelter study; run inside Blender via scripts/run.py."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import sys
import bpy
from mathutils import Vector

SKILL = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL/'scripts'))
from blender_review import export_and_review
from preview import prepare

p=argparse.ArgumentParser()
p.add_argument('--out',type=Path,required=True)
p.add_argument('--stage',choices=['massing','construction','finish'],default='finish')
p.add_argument('--seed',type=int,default=23)
p.add_argument('--pass',dest='pass_number',type=int,choices=[1,2],default=2)
p.add_argument('--render',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
rng=random.Random(a.seed)
finish=a.stage=='finish'
parts=[]
colors={'earth':(.52,.255,.115),'clay':(.46,.18,.077),'stone':(.56,.47,.32),
        'timber':(.20,.115,.055),'ceramic':(.065,.265,.26),'dark':(.06,.034,.02),
        'pot':(.43,.24,.115),'paint':(.66,.56,.37)}
if a.pass_number==2:
 colors.update(earth=(.37,.145,.059),clay=(.36,.12,.04),ceramic=(.028,.16,.165),
               timber=(.145,.077,.034),stone=(.52,.43,.30))
materials={}
for name,color in colors.items():
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1)
 bsdf.inputs['Roughness'].default_value=.82 if name!='ceramic' else .56
 attr=m.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name='Paint'
 m.node_tree.links.new(attr.outputs['Color'],bsdf.inputs['Base Color'])
 materials[name]=m

def mesh(name,vertices,faces,material='stone',bevel=0,smooth=False):
 data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
 obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);parts.append(obj)
 data.materials.append(materials[material]);paint=data.color_attributes.new(name='Paint',type='FLOAT_COLOR',domain='CORNER')
 base=colors[material] if a.stage!='massing' else (.40,.42,.43)
 tint=rng.uniform(.83,1.13) if finish and a.pass_number==2 else rng.uniform(.89,1.09) if finish else 1
 if a.pass_number==2 and name.startswith(('Front bonded infill','Kiln spring wall','Kiln rear closure')):tint=1
 for poly in data.polygons:
  poly.use_smooth=smooth
  for li in poly.loop_indices:
   v=data.vertices[data.loops[li].vertex_index].co
   # Low-frequency painted value variation, with calmer broad planes.
   shade=1
   if finish:
    shade=.94+.04*math.sin(v.x*3.2+v.z*1.1)+.035*math.sin(v.y*4.1-v.z*2.3)
    if material=='timber':shade+=.06*math.sin(v.x*29+v.y*3+v.z*.5)
   paint.data[li].color=tuple(min(.95,c*tint*shade) for c in base)+(1,)
 if bevel:
  mod=obj.modifiers.new('Restrained edge softness','BEVEL');mod.width=bevel;mod.segments=2 if a.pass_number==2 else 3
  mod=obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 return obj

def box(name,center,size,material='stone',bevel=.025,warp=0):
 cx,cy,cz=center;sx,sy,sz=[v/2 for v in size]
 vertices=[(cx+x*sx,cy+y*sy,cz+z*sz) for z in [-1,1] for y in [-1,1] for x in [-1,1]]
 if finish and warp:
  vertices=[(x+rng.uniform(-warp,warp),y+rng.uniform(-warp,warp),z) for x,y,z in vertices]
 return mesh(name,vertices,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],material,bevel)

def beam(name,start,end,width=.16,depth=None,material='timber'):
 start,end=Vector(start),Vector(end);d=end-start
 obj=box(name,(0,0,0),(width,depth or width,d.length),material,.022)
 obj.location=(start+end)/2;obj.rotation_euler=d.to_track_quat('Z','Y').to_euler();return obj

def extrude_profile(name,profile,yfront,yback,material='clay',bevel=.025):
 n=len(profile);verts=[(x,y,z) for y in [yfront,yback] for x,z in profile]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,faces,material,bevel)

def arch_strip(name,cx,z,r1,r2,start,end,y1,y2,material,segments=8,bevel=.015):
 angles=[start+(end-start)*i/segments for i in range(segments+1)]
 profile=[(cx+r2*math.cos(t),z+r2*math.sin(t)) for t in angles]
 profile += [(cx+r1*math.cos(t),z+r1*math.sin(t)) for t in reversed(angles)]
 return extrude_profile(name,profile,y1,y2,material,bevel)

# Source axes: X right, front -Y, Z up. Foundation datum is z=0.
box('Foundation core',(0,0,.13),(5.8,3.6,.26),'stone',.06)
if a.stage!='massing':
 for row in range(2):
  z=.065+row*.135
  for side,y in [('front',-1.79),('rear',1.79)]:
   for i in range(10):
    box(f'Foundation {side} {row}-{i}',(-2.61+i*.58,y,z),(.565,.22,.13),'stone',.018)
 for i in range(8):
  for j in range(5):
   box(f'Floor slab {i}-{j}',(-2.52+i*.72,-1.42+j*.70,.27),(.704,.684,.08),'stone',.016)
# Entry does not block working bay.
box('Broad approach step',(-.75,-2.05,.08),(2.15,.58,.16),'stone',.035)

cx=-1.43;outer=1.32;inner=1.10;knee=1.12;front=-1.44;back=1.35;floor=.31
# Connected longitudinal barrel shell, with truly empty firing chamber.
arch_strip('Continuous kiln vault',cx,knee,inner,outer,0,math.pi,front,back,'earth',32,.025)
for side in [-1,1]:
 box(f'Kiln spring wall {side}',(cx+side*(outer+inner)/2,(front+back)/2,(knee+floor)/2),(outer-inner,back-front,knee-floor),'earth',.025)
# Front infill bridges outer barrel silhouette to smaller arched opening.
ro=.67;zo=.87
outerpath=[(cx-outer,floor)]+[(cx+outer*math.cos(math.pi-i*math.pi/32),knee+outer*math.sin(math.pi-i*math.pi/32)) for i in range(33)]+[(cx+outer,floor)]
innerpath=[(cx-ro,floor)]+[(cx+ro*math.cos(math.pi-i*math.pi/32),zo+ro*math.sin(math.pi-i*math.pi/32)) for i in range(33)]+[(cx+ro,floor)]
for i in range(len(outerpath)-1):
 extrude_profile(f'Front bonded infill {i}',[outerpath[i],innerpath[i],innerpath[i+1],outerpath[i+1]],front-.035,front+.23,'earth',0)
rear_profile=[(cx-outer,floor)]+[(cx+outer*math.cos(math.pi-i*math.pi/32),knee+outer*math.sin(math.pi-i*math.pi/32)) for i in range(33)]+[(cx+outer,floor)]
extrude_profile('Kiln rear closure',rear_profile,back-.18,back+(.035 if a.pass_number==2 else 0),'earth',.02)
box('Firing chamber bed',(cx,-.15,.32),(2.2,2.55,.08),'dark',.01)
# A black patch on a facade would hide an absent opening; the chamber is actual mesh depth.
for s in [-1,1]:
 for row in range(3):
  box(f'Portal jamb {s}-{row}',(cx+s*.81,front-.09,floor+(row+.5)*(zo-floor)/3),(.29,.34,(zo-floor)/3-.012),'stone',.024)
for i in range(9):
 arch_strip(f'Portal voussoir {i}',cx,zo,.67,.96,i*math.pi/9+.006,(i+1)*math.pi/9-.006,front-.29,front+.08,'ceramic' if i==4 else 'stone',4,.022)
if a.stage!='massing':
 # Staggered curved brick courses articulate the vault without turning it into shingles.
 for row in range(13):
  y=front+.12+row*.208
  for j in range(15):
   start=(j+(row%2)*.5)*math.pi/15
   end=min(math.pi,start+math.pi/15-.009)
   if start>=math.pi:continue
   arch_strip(f'Vault brick {row}-{j}',cx,knee,outer-.012,outer+.018,start+.005,end,y-.096,y+.096,'earth',3,.012)
 # Front masonry above opening: only stones whose entire lower face clears the arch.
 for row in range(7):
  z=.44+row*.28
  for col in range(8):
   x=cx-1.17+col*.33+(row%2)*.11
   dx=abs(x-cx)
   if dx+.155>outer:continue
   upper=knee+math.sqrt(max(0,outer*outer-(dx+.155)**2))
   hole=zo+math.sqrt(max(0,.98**2-max(0,dx-.16)**2)) if dx<1.13 else floor
   if z+.13<upper and z-.13>hole:
    box(f'Face brick {row}-{col}',(x,front-.065,z),(.31,.105,.245),'earth',.018,warp=.008)

# Chimney is deliberately rear-left, clear of the shelter roof and kiln opening.
for row in range(10):
 z=2.12+(row+.5)*.225;width=.74-row*.022
 mat='stone' if row==8 else 'earth'
 for side in [-1,1]:
  box(f'Flue X {row}-{side}',(-2.16+side*(width-.12)/2,.83,z),(.12,width,.213),mat,.015)
  box(f'Flue Y {row}-{side}',(-2.16,.83+side*(width-.12)/2,z),(width-.24,.12,.213),mat,.015)
box('Flue dark inner seat',(-2.16,.83,2.15),(.42,.42,.04),'dark',.005)

# Shelter plan owns its four posts and two end beams once.
def roofz(x):return 3.34-.27*x
for x in [.18,2.63]:
 for y in [-1.30,1.30]:
  h=roofz(x)-.12
  beam(f'Shelter post {x}-{y}',(x,y,.37),(x,y,h),.20)
  box(f'Post footing {x}-{y}',(x,y,.40),(.31,.31,.18),'stone',.025)
  box(f'Post shoe {x}-{y}',(x,y,.53),(.224,.224,.17),'ceramic',.02)
for y in [-1.30,1.30]:
 beam(f'Roof sloping cross tie {y}',(.02,y,roofz(.02)-.10),(2.86,y,roofz(2.86)-.10),.23,.19)
 for x,direction in [(.18,1),(2.63,-1)]:
  beam(f'Knee brace {x}-{y}',(x,y,roofz(x)-.65),(x+direction*.48,y,roofz(x+direction*.48)-.20),.13)
for x in [.18,2.63]:
 beam(f'Longitudinal tie {x}',(x,-1.50,roofz(x)-.20),(x,1.50,roofz(x)-.20),.18)
# Back screen is a useful boundary but leaves the working bay front/right open.
box('Screen wall core',(1.41,1.4,.87),(2.4,.22,1.1),'earth',.035)
if a.stage!='massing':
 for row in range(4):
  for i in range(6):
   box(f'Screen face stone {row}-{i}',(.39+i*.395,1.245,.45+row*.255),(.378,.14,.24),'stone',.022,warp=.006)
for i in range(6):
 x=.15+i*.51
 beam(f'Rafter {i}',(x,-1.64,roofz(x)),(x,1.60,roofz(x)),.13,.13)
# Continuous roof underlay and curved ceramic tiles. Slope is X, tile channels run X.
mesh('Roof underlay',[(x,y,roofz(x)+h) for h in [.02,.085] for y in [-1.68,1.65] for x in [-.05,2.95]],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],'timber',.018)
if a.stage!='massing':
 for row in range(7):
  xa=-.10+row*.435;xb=xa+.51
  for col in range(10):
   yy=-1.56+col*.337
   vertices=[]
   end_variation=(.027*math.sin(col*2.1+row*.9)) if a.pass_number==2 else 0
   for x in [xa,xb]:
    for k in range(9):
     ang=k*math.pi/8
     xx=x+(end_variation if x==xb else 0)
     sag=(-.018*math.sin((yy+1.6)*math.pi/3.25)) if a.pass_number==2 else 0
     lap_lift=((x-xa)/.51*.045) if a.pass_number==2 else 0
     vertices.append((xx,yy+.18*math.cos(ang),roofz(xx)+.10+.075*math.sin(ang)+sag+lap_lift))
   faces=[(k,k+1,k+10,k+9) for k in range(8)]
   o=mesh(f'Ceramic roof tile {row}-{col}',vertices,faces,'ceramic',0,True)
   solid=o.modifiers.new('Tile thickness','SOLIDIFY');solid.thickness=.035
   b=o.modifiers.new('Tile lip softness','BEVEL');b.width=.009;b.segments=2
else:
 box('Massing canopy volume',(1.45,0,3.02),(3.1,3.35,.10),'ceramic',.025).rotation_euler.y=.264
# Workbench: each foot reaches the floor and each pot seats on its real top.
bench_top=1.06
box('Bench plank top',(1.47,.77,bench_top),(1.96,.64,.13),'timber',.028)
for x in [.66,2.27]:
 for y in [.52,1.02]:beam(f'Bench leg {x}-{y}',(x,y,.32),(x,y,1.0),.12)
beam('Bench long stretcher',(.66,.78,.53),(2.27,.78,.53),.10)

def pot(name,cx,cy,height,width):
 # Revolved profile includes an inner lip and chamber; no capped cylinder mouth.
 base=bench_top+.065
 profile=[(0,0),(.62,0),(.78,.07),(1,.35),(.95,.58),(.70,.78),(.62,.88),(.73,.91),(.73,.97),(.58,.98),(.54,.9),(.58,.80),(.77,.55),(.72,.25),(.50,.14),(0,.14)]
 verts=[];n=32
 for r,z in profile:
  for i in range(n):
   t=i*2*math.pi/n;verts.append((cx+r*width*math.cos(t),cy+r*width*math.sin(t),base+z*height))
 faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)]
 return mesh(name,verts,faces,'pot',0,True)
for i,(x,h,w) in enumerate([(1.00,.57,.27),(1.62,.41,.20),(2.12,.31,.16)]):pot(f'Open clay pot {i}',x,.75,h,w)

# Paint accents are restrained small face patches, kept out of contact surfaces.
if finish:
 for i in range(18):
  y=-1.25+rng.random()*2.45;t=.25+rng.random()*2.60
  x=cx+(outer+.023)*math.cos(t);z=knee+(outer+.023)*math.sin(t)
  # Skip the front portal; patches live on exposed vault surfaces.
  dt=.024;dy=.055+rng.random()*.08
  verts=[(cx+(outer+.027)*math.cos(tt),yy,knee+(outer+.027)*math.sin(tt)) for tt,yy in [(t-dt,y-dy),(t+dt*.6,y-dy*.8),(t+dt,y+dy),(t-dt*.5,y+dy*.7)]]
  mesh(f'Broken limewash {i}',verts,[(3,2,1,0)],'paint')
# Calculate real mesh ray contacts for a bounded example, not physics certification.
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
def cast(origin,direction,length):
 return bpy.context.scene.ray_cast(deps,Vector(origin),Vector(direction),distance=length)
checks={}
checks['open_firebox_ray']=not cast((cx,-2,.65),(0,1,0),1.2)[0]
checks['chamber_backstop']=cast((cx,-1,.65),(0,1,0),3)[0]
checks['work_approach_clear']=not cast((1.5,-2.1,1.6),(0,1,0),2.2)[0]
checks['bench_feet_on_floor']=all(cast((x,y,.34),(0,0,-1),.06)[0] for x in [.66,2.27] for y in [.52,1.02])
checks['single_owned_shelter_posts']=len([o for o in parts if o.name.startswith('Shelter post')])==4
(a.out/'contact-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
if not all(checks.values()):raise RuntimeError(f'Contact checks failed: {checks}')
for o in parts:
 # Consistent outward normals for closed parts. Open paint patches are authored explicitly.
 if o.name.startswith('Broken limewash'):continue
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 # Mesh construction is closed except tile sheets, which receive Solidify.
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o.select_set(False)
metadata={'example':'kiln-shelter','stage':a.stage,'seed':a.seed,'pass':a.pass_number,
 'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'reference':'reference.png','checks':checks,'visual_approval':'pending',
 'limits':['Authored exterior study; no functional kiln simulation.','No engine collision, LODs or performance certification.','Fixed footprint; seed varies surface treatment, not architecture.']}
export_and_review(a.out,parts,metadata,a.render)
shutil.copy2(Path(__file__).with_name('reference.png'),a.out/'reference.png')
prepare(a.out)
print('WORLDWRIGHT_BUILD_COMPLETE',a.out)
