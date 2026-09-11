"""Isolated Hamburg C0 production pass. Run in Blender, never in Three.js.

Macro geometry stays on official Hamburg LoD2 coordinates. Archived source objects
remain in the blend outside C0. Photographs guide proportions, never wall albedo.
"""
from __future__ import annotations
import importlib.util, json, math, random
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

ROOT=Path.cwd(); SRC=ROOT/'assets-src/blender/night-intersection'
spec=importlib.util.spec_from_file_location('facade_base',ROOT/'scripts/blender/author_hamburg_lod2_facades.py')
base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
c0=bpy.data.collections['C0']; visual=base.find_visual(c0)
assert 'Hamburg' in str(c0.get('official_lod2_reference_location',''))
bpy.context.preferences.filepaths.save_version=0
bpy.context.scene.unit_settings.system='METRIC'; bpy.context.scene.unit_settings.scale_length=1
archive=bpy.data.collections.get('Astra_legacy_source_archive')
if archive is None:
 archive=bpy.data.collections.new('Astra_legacy_source_archive'); bpy.context.scene.collection.children.link(archive)
archive.hide_render=True; archive.hide_viewport=True
for o in list(bpy.data.objects):
 if o.name.startswith('astra_'): bpy.data.objects.remove(o,do_unlink=True)

def preserve(o):
 for col in list(o.users_collection): col.objects.unlink(o)
 archive.objects.link(o)

# The old 5.5m sidewalk squares encode an invented cross intersection. Hansaplatz
# is a paved pedestrian square; keep original inputs archived, exclude from export.
for o in list(visual.all_objects):
 if (o.name.startswith('c0_') and ('sidewalk_slab' in o.name or '_curb_' in o.name)) or o.name in ('reference_hansaplatz_plaza_paving','hansaplatz_plaza_ground_reference_plane','hamburg_ground_continuity_underlay') or o.name.startswith('hamburg_hansaplatz_v10_granite_') or (o.name.startswith('hamburg_hansaplatz_v10_linden_')):
  preserve(o)

def mat(name,color,rough=.75,metal=0):
 m=bpy.data.materials.get('astra_'+name) or bpy.data.materials.new('astra_'+name)
 m.use_nodes=True; m.node_tree.nodes.clear(); n=m.node_tree.nodes
 p=n.new('ShaderNodeBsdfPrincipled'); out=n.new('ShaderNodeOutputMaterial'); m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 m.diffuse_color=(*color,1);return m

def textured(name,stem,color=(1,1,1),scale=1):
 m=mat(name,color);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 for key,suffix,space in [('Base Color','diff','sRGB'),('Roughness','rough','Non-Color'),('Normal','nor_gl','Non-Color')]:
  path=SRC/'materials/hansaplatz'/f'{stem}_{suffix}_1k.jpg'
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path),check_existing=True);t.image.colorspace_settings.name=space;t.image.pack()
  if key=='Normal':
   normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.65;l.new(t.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs['Normal'],p.inputs[key])
  else:l.new(t.outputs['Color'],p.inputs[key])
 return m

palette=[mat('sandstone',(0.43,.355,.265)),mat('chalk_stucco',(.64,.60,.51)),mat('muted_brick',(.26,.105,.055)),mat('grey_stucco',(.36,.38,.36)),mat('warm_plaster',(.53,.40,.28)),mat('limestone',(.56,.53,.45))]
# Procedural Noise/ColorRamp nodes cannot be exported as glTF albedo. Explicit
# glTF-compatible surface values remove the white default-material export defect.
for o in visual.all_objects:
 if o.name.startswith('lod2_') and o.name.endswith('_wall'):
  o.data.materials.clear();o.data.materials.append(palette[base.stable_int(o.name)%len(palette)])

buckets={};materials={}
def mesh(name,verts,faces,m,uv=False,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 if uv:
  layer=me.uv_layers.new(name='UVMap')
  for poly in me.polygons:
   for li in poly.loop_indices:
    p=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(p.x/2.4,p.y/2.4)
 if smooth:
  for p in me.polygons:p.use_smooth=True
 o=bpy.data.objects.new(name,me);visual.objects.link(o);me.materials.append(m);return o

def tube(key,a,b,r1,r2,sides=8):
 verts,faces=buckets.setdefault(key,([],[]));a=Vector(a);b=Vector(b);d=(b-a).normalized();v=d.cross(Vector((0,0,1)))
 if v.length<.01:v=d.cross(Vector((1,0,0)))
 v.normalize();w=d.cross(v);start=len(verts)
 for p,r in [(a,r1),(b,r2)]:
  for k in range(sides):verts.append(tuple(p+r*(v*math.cos(k*math.tau/sides)+w*math.sin(k*math.tau/sides))))
 for k in range(sides):faces.append((start+k,start+(k+1)%sides,start+(k+1)%sides+sides,start+k+sides))
 faces.extend([tuple(start+k for k in reversed(range(sides))),tuple(start+sides+k for k in range(sides))])

def leaf(key,c,size,rng):
 verts,faces=buckets.setdefault(key,([],[]));a=rng.random()*math.tau;u=Vector((math.cos(a),math.sin(a),rng.uniform(-.5,.5))).normalized()*size;v=Vector((-math.sin(a)*.48,math.cos(a)*.48,rng.uniform(-.35,.35)))*size;c=Vector(c);i=len(verts)
 verts.extend([tuple(c-u),tuple(c-u*.25+v),tuple(c+u*.60+v*.65),tuple(c+u),tuple(c+u*.60-v*.65),tuple(c-u*.25-v),tuple(c+Vector((0,0,.04)))])
 faces.extend((i+6,i+j,i+(j+1)%6) for j in range(6))

# Same twelve source-grounded linden anchor positions; replace opaque ico-crowns
# with tapered branching and individually modeled leaf silhouettes, autumn reference.
materials['bark']=mat('bark',(.115,.079,.048),.94)
for k,c in enumerate([(.23,.26,.07),(.32,.33,.085),(.14,.205,.06)]):
 materials['leaf'+str(k)]=mat('leaf'+str(k),c,.85);materials['leaf'+str(k)].use_backface_culling=False
for i in range(12):
 rng=random.Random(2300+i);angle=i/12*math.tau+.13;r=13.8+(.55 if i%3==0 else -.20 if i%3==1 else .15)
 x=-7.377+math.sin(angle)*r;y=30.192-math.cos(angle)*r;h=10.5+rng.random()*1.3
 tube('bark',(x,y,-.07),(x+.15,y-.12,h*.78),.33,.12,12)
 for arm in range(13):
  a=arm*2.399+rng.uniform(-.2,.2);z=3.5+arm*.32;rad=rng.uniform(2.4,4.2);start=(x,y,z);tip=(x+math.cos(a)*rad,y+math.sin(a)*rad,min(h,z+rng.uniform(2.8,4.2)))
  tube('bark',start,tip,.09,.015)
  for twig in range(9):
   t=.4+twig*.066;mid=Vector(start).lerp(Vector(tip),t);q=Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(.3,1.3)));end=mid+q
   tube('bark',mid,end,.015,.003,5)
   for j in range(10):
    pos=mid.lerp(end,rng.random())+Vector((rng.uniform(-.40,.40),rng.uniform(-.40,.40),rng.uniform(-.25,.25)))
    leaf('leaf'+str(rng.randrange(3)),pos,rng.uniform(.09,.17),rng)
for k,(v,f) in buckets.items():mesh('astra_lindens_'+k,v,f,materials[k],smooth=k=='bark')

# Elevation interpolation follows official foundation edges, with an exact photo
# origin anchor. This is an authored continuity surface, not a surveyed DTM.
verts,objects=base.load_obj(SRC/'hamburg-lod2/hansaplatz-lod2.obj'); edges=[]
for name,faces in objects.items():
 if not name.endswith('_ground'):continue
 for face in faces:
  ps=[verts[i] for i in face]
  for a,b in zip(ps,ps[1:]+ps[:1]):edges.append((a,b))
def elevation(x,z):
 nearest=[]
 for a,b in edges:
  dx=b[0]-a[0];dz=b[2]-a[2];t=max(0,min(1,((x-a[0])*dx+(z-a[2])*dz)/max(dx*dx+dz*dz,.001)))
  px=a[0]+t*dx;pz=a[2]+t*dz;d=math.hypot(x-px,z-pz);height=a[1]+t*(b[1]-a[1]);nearest.append((d,height))
 nearest.sort();d,h=nearest[0]
 if d<1.0:return h-.025
 blend=max(0,min(1,(d-1)/15));blend=blend*blend*(3-2*blend)
 # Central square and fountain stay at the accepted observer ground height.
 return h*(1-blend)-.035
paving=textured('square_paving','rectangular_paving')
v=[];f=[];coords=list(range(-180,181,3));n=len(coords)
for z in coords:
 for x in coords:v.append((x,-z,elevation(x,z)))
for iz in range(n-1):
 for ix in range(n-1):
  a=iz*n+ix;f.extend([(a,a+n,a+1),(a+1,a+n,a+n+1)])
mesh('astra_continuous_paving',v,f,paving,uv=True)

# Keep sculpture approximation honest. Improve silhouette shading, retain height
# and authored landmark placement; detailed statuary is not a scanned source.
for o in visual.all_objects:
 if o.name.startswith('hamburg_hansaplatz_v10_fountain_') and o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=False
  mod=o.modifiers.get('astra_stone_edge') or o.modifiers.new('astra_stone_edge','BEVEL');mod.width=.035;mod.segments=2
c0['astra_iteration']=1;c0['canonical_city_lock']='Hamburg';c0['raw_panorama_wall_projection']=False
c0['astra_material_rule']='glTF-compatible BSDF or packed PBR maps; no unbaked procedural albedo'
c0['astra_terrain_claim']='visual foundation-edge interpolation; photo origin and fountain at ground 0; not surveyed DTM'
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'c0/night-intersection-c0.blend'))
(ROOT/'public/assets/3d/night-intersection/c0/core/BUILD.txt').write_text('Astra experimental Hansaplatz C0 iteration 1\nCanonical Hamburg LoD2-DE 2026: 53.554451,10.012056\nNo panorama wall projection. Shared Day/Night geometry.\nPBR paving, foundation-edge ground continuity, branched lindens, exportable facade materials.\nSource objects archived outside C0, not deleted.\n')
print('ASTRA_AUTHOR_COMPLETE',len(visual.all_objects))
