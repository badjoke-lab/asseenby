"""Camera-prioritized opening meshes on exact Hamburg LoD2 wall planes.

Reconstruct selected wall polygons with apertures, not an applied window skin.
Profiles are restrained interpretations of the checked-in photographic plates,
not surveyed window locations. Original uncut source remains outside export C0.
"""
import json, math, importlib.util
from collections import defaultdict
import bpy, bmesh

# Distinct perimeter buildings, identified by the immutable LGV source IDs.
PROFILES = {
 '0zSs': ('render', 4, 2.8), '0zPg': ('brick', 5, 2.65),
 '0zyc': ('ornate', 6, 2.6), '0zxx': ('ornate', 5, 2.5),
 '0zuh': ('ornate', 5, 2.65), '0zP6': ('ornate', 5, 2.5),
 '0101Q': ('brick', 5, 2.6), '0zeJ': ('ornate', 5, 2.55),
 '0zQf': ('render', 5, 2.7), '0zon': ('render', 4, 2.65),
}

def clip(poly, axis, bound, positive):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=(a[axis]-bound)*(1 if positive else -1)>=-1e-7
  ib=(b[axis]-bound)*(1 if positive else -1)>=-1e-7
  if ia: out.append(a)
  if ia != ib:
   t=(bound-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[i]+t*(b[i]-a[i]) for i in range(2)))
 return out

def run(base, visual, archive, mat, palette, src):
 def preserve(o):
  for c in list(o.users_collection): c.objects.unlink(o)
  archive.objects.link(o)
 for o in list(visual.all_objects):
  if o.name.startswith(('hamburg_facade_', 'hamburg_authored_facade_')): preserve(o)
 vertices, objects=base.load_obj(src/'hamburg-lod2/hansaplatz-lod2.obj')
 candidates=[]
 for name,faces in objects.items():
  if not name.endswith('_wall'):continue
  for index,face in enumerate(faces):
   points=[vertices[i] for i in face]; s=base.facade_segment(points)
   if not s or s['height']<9 or s['length']<5 or s['distance']>108:continue
   if max(abs((p[0]-s['a'][0])*s['n'][0]+(p[2]-s['a'][1])*s['n'][1]) for p in points)>.025:continue
   candidates.append((name,index,points,s))
 def cross(a,b):return a[0]*b[1]-a[1]*b[0]
 def visible(s):
  # Occlusion against actual wall segments, not a radial all-building pass.
  target=s['mid']
  for _,_,_,other in candidates:
   a=other['a'];d=(other['b'][0]-a[0],other['b'][1]-a[1]);den=cross(target,d)
   if abs(den)<1e-8:continue
   t=cross(a,d)/den; u=cross(a,target)/den
   if .02<t<.985 and .015<u<.985:return False
  return True
 selected=[];seen=set()
 for row in sorted(candidates,key=lambda r:r[3]['distance']):
  s=row[3];key=tuple(round(x,2) for x in (*s['mid'],s['length']))
  if key in seen or not visible(s):continue
  seen.add(key);selected.append(row)
 assert len(selected)>=12, len(selected)
 mats={
  'frame':mat('sash_paint',(.67,.64,.56),.48),
  'metal':mat('shop_bronze',(.08,.092,.082),.38,.45),
  'stone':mat('cut_limestone',(.47,.43,.35),.84),
  'trim':mat('moulded_stucco',(.64,.60,.51),.76),
  'base':mat('stone_base',(.245,.225,.19),.91),
  'glass':mat('recess_glass',(.10,.165,.20),.2,.18),
  'glass_alt':mat('recess_glass_alt',(.16,.205,.225),.24,.12),
  'glass_warm':mat('recess_glass_warm',(.25,.22,.16),.3,.08),
  'backing':mat('shop_interior',(.13,.12,.105),.93),
 }
 for i,m in enumerate(palette):mats['wall'+str(i)]=m
 mats['dress']=mat('dressed_ground_floor',(.36,.335,.29),.88)
 mats['curtain']=mat('linen_blind',(.44,.405,.33),.94)
 # Only a minority of interiors are illuminated, with no daylight white plates.
 mats['lit']=mat('interior_lamp',(.38,.29,.16),.7)
 lamp=mats['lit'].node_tree.nodes.get('Principled BSDF')
 lamp.inputs['Emission Color'].default_value=(1,.64,.29,1)
 lamp.inputs['Emission Strength'].default_value=.32
 spec=importlib.util.spec_from_file_location('astra_surfaces',src.parents[2]/'scripts/blender/astra/surfaces.py')
 surf=importlib.util.module_from_spec(spec);spec.loader.exec_module(surf)
 surf.add_maps(mats['wall2'],'astra_fired_brick',brick=True)
 # Share one subtle plaster normal image across stucco materials.
 surf.add_maps(mats['wall1'],'astra_plaster')
 normal_image=bpy.data.images['astra_plaster_normal']
 for key in ['wall0','wall3','wall4','wall5','trim','dress']:
  m=mats[key];t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=normal_image
  nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.35
  m.node_tree.links.new(t.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],m.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
 buckets={};records=[];replaced=defaultdict(set)
 def polygon(key,ps):
  if len(ps)<3:return
  vs,fs=buckets.setdefault(key,([],[]));start=len(vs);vs.extend(ps);fs.append(tuple(range(start,start+len(ps))))
 for name,index,points,s in selected:
  style,floors,target_pitch=next((v for k,v in PROFILES.items() if k in name),('render',max(3,round(s['height']/3.6)),2.7))
  lo=s['min_y']; hi=s['max_y']; length=s['length'];u=s['u'];n=s['n'];a=s['a']
  poly=[((p[0]-a[0])*u[0]+(p[2]-a[1])*u[1],p[1]) for p in points]
  # Eaves are the lower upper-envelope vertices; keep original gable above.
  eave=min(y for _,y in poly if y>lo+3)
  if eave-lo<8:eave=hi
  floor_h=(eave-lo-.65)/floors
  columns=max(2,round((length-1.0)/target_pitch));pitch=(length-1.0)/columns
  wallkey='wall'+str(2 if style=='brick' else ([1,5,4][base.stable_int(name)%3] if style=='ornate' else 1))
  def point(x,y,d):return (a[0]+u[0]*x+n[0]*d,-(a[1]+u[1]*x+n[1]*d),y)
  def face(key,ps):polygon(key,[point(*p) for p in ps])
  def box(key,x,y,w,h,depth,offset=0):
   center=(a[0]+u[0]*x+n[0]*offset,y,a[1]+u[1]*x+n[1]*offset)
   base.add_box_geometry(buckets,key,center,u,n,w,h,depth)
  holes=[]
  for floor in range(floors):
   for col in range(columns):
    x=.5+pitch*(col+.5)
    width=min(1.35,pitch*.52) if floor else pitch*.78
    height=min(2.35,floor_h*.62) if floor else floor_h*.74
    bottom=lo+floor*floor_h+(.72 if floor else .12)
    if bottom+height>eave-.5:height=eave-.5-bottom
    holes.append((x-width/2,x+width/2,bottom,bottom+height,floor,col))
  # Grid subdivision clips the actual LoD2 polygon. Missing cells ARE openings.
  xs=sorted(set([0,length]+[h[i] for h in holes for i in (0,1)]))
  ys=sorted(set([lo,hi]+[h[i] for h in holes for i in (2,3)]))
  for x0,x1 in zip(xs,xs[1:]):
   for y0,y1 in zip(ys,ys[1:]):
    if any(h[0]<(x0+x1)/2<h[1] and h[2]<(y0+y1)/2<h[3] for h in holes):continue
    q=poly
    for axis,bound,pos in [(0,x0,True),(0,x1,False),(1,y0,True),(1,y1,False)]:q=clip(q,axis,bound,pos) if q else []
    face('dress' if (y0+y1)/2<lo+floor_h-.28 else wallkey,[(x,y,.012) for x,y in q])
  for x0,x1,y0,y1,floor,col in holes:
   x=(x0+x1)/2;y=(y0+y1)/2;w=x1-x0;h=y1-y0;back=-.32 if floor else -.68
   reveal='stone' if floor==0 else wallkey
   # Four masonry returns connecting the wall to the deep glazing plane.
   for q in [ [(x0,y0,.013),(x0,y1,.013),(x0,y1,back),(x0,y0,back)],
              [(x1,y1,.013),(x1,y0,.013),(x1,y0,back),(x1,y1,back)],
              [(x0,y1,.013),(x1,y1,.013),(x1,y1,back),(x0,y1,back)],
              [(x1,y0,.013),(x0,y0,.013),(x0,y0,back),(x1,y0,back)]]:face(reveal,q)
   glass=['glass','glass_alt','glass','glass_warm'][(base.stable_int(name)+col+floor*3)%4]
   seed=base.stable_int(f'{name}/{floor}/{col}')
   if seed%11==0:glass='lit'
   box(glass,x,y,w-.06,h-.06,.025,back)
   if floor and seed%5==0:
    # Half-drawn interior roller blind sits within the recessed opening.
    box('curtain',x,y1-h*.16,w-.16,h*.28,.016,back+.027)
   frame='frame' if floor else 'metal'
   for xx in [x0+.045,x1-.045]:box(frame,xx,y,.09,h,.10,back+.065)
   for yy in [y0+.045,y1-.045]:box(frame,x,yy,w,.09,.10,back+.065)
   box(frame,x,y,.075,h,.105,back+.07)
   box(frame,x,y0+h*.73,w,.075,.105,back+.07)
   if floor:
    box('stone',x,y0-.065,w+.29,.13,.40,.10)
    box('trim',x,y0-.16,w+.19,.065,.24,.055)
    if style=='ornate':
     for xx in [x0-.075,x1+.075]:box('trim',xx,y,.15,h+.22,.14,.055)
     box('trim',x,y1+.09,w+.34,.18,.25,.095)
     box('trim',x,y1+.22,w+.46,.075,.34,.14)
     if floor<=2:
      box('stone',x,y1+.33,.20,.20,.21,.095)
      if floor==1 and col%2==0:
       # Restrained raised triangular lintel, seen on ornate perimeter references.
       face('trim',[(x-w*.62,y1+.28,.16),(x+w*.62,y1+.28,.16),(x,y1+.56,.16)])
       face('stone',[(x-w*.62,y1+.28,.07),(x-w*.62,y1+.28,.16),(x,y1+.56,.16),(x,y1+.56,.07)])
       face('stone',[(x,y1+.56,.07),(x,y1+.56,.16),(x+w*.62,y1+.28,.16),(x+w*.62,y1+.28,.07)])
      box('trim',x,y0-.39,w*.70,.28,.095,.032)
    elif style=='brick':
     box('stone',x,y1+.10,w+.22,.20,.13,.04)
   else:
    # Deep portal/retail joinery: threshold, transom, separate signage fascia.
    box('stone',x,y0-.04,w+.1,.10,.83,-.20)
    box('metal',x,y1+.21,w+.18,.30,.16,.035)
    box('stone',x,y0+.20,w*.43,.36,.085,back+.05)
    if col==columns//2:
     box('metal',x+.15,y0+.95,.035,.35,.07,back+.14)
     box('base',x,y0+.30,w-.12,.50,.05,back+.07)
  # Shallow corner quoins terminate each ornate facade instead of a blank edge.
  if style=='ornate':
   for x in [.18,length-.18]:
    for k in range(int((eave-lo)/.44)):
     box('trim',x,lo+.22+k*.44,.36 if k%2 else .48,.405,.12,.04)
  # Ground-floor piers and rustication have a different scale from upper sash.
  for col in range(columns+1):
   x=.5+col*pitch
   if style=='ornate':
    for k in range(max(1,int(floor_h/.36))):box('stone',x,lo+.18+k*.36,pitch*.20,.32,.12,.05)
  for floor in range(1,floors):
   level=lo+floor_h*floor
   if style!='brick' or floor==1:
    box('trim',length/2,level-.06,length,.16,.24,.075)
    if floor==1:box('stone',length/2,level-.23,length,.14,.38,.12)
  box('base',length/2,lo+.055,length,.11,.20,.055)
  for drop,h,depth in [(.40,.20,.20),(.22,.16,.35),(.055,.15,.54)]:
   box('trim' if style!='brick' else 'stone',length/2,eave-drop,length+.04,h,depth,depth*.38)
  if style=='ornate':
   for k in range(int(length/.45)):box('trim',.22+k*.45,eave-.47,.14,.18,.21,.10)
  replaced[name].add(index)
  records.append({'source_object':name,'face':index,'mid_runtime_xz':s['mid'],'profile':style,'floors':floors,'openings':len(holes),'recess_m':.32,'shop_recess_m':.68,'macro_boundary':'original LoD2 polygon retained'})
 # Replace only selected polygon faces. Preserve every other official face/roof.
 for name,indices in replaced.items():
  old=bpy.data.objects.get(name)
  if old:
   old.name='source_'+name;preserve(old)
  fs=[tuple(f) for i,f in enumerate(objects[name]) if i not in indices]
  if fs:
   me=bpy.data.meshes.new(name);me.from_pydata([base.runtime_to_blender(p) for p in vertices],[],fs);me.update()
   o=bpy.data.objects.new(name,me);visual.objects.link(o);me.materials.append(palette[base.stable_int(name)%len(palette)])
   o['source_semantic']='wall';o['source_geometry']='Hamburg LoD2-DE 2026 unmodified remaining faces'
 for key,(vs,fs) in buckets.items():
  me=bpy.data.meshes.new('astra_facades_'+key);me.from_pydata(vs,[],fs);me.update()
  bm=bmesh.new();bm.from_mesh(me)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces))
  bm.to_mesh(me);bm.free()
  uv=me.uv_layers.new(name='UVMap')
  # Box projection in world metres: 1.024 m tile = 4 bricks x 16 courses.
  for poly in me.polygons:
   normal=poly.normal
   axis=0 if abs(normal.y)>abs(normal.x) else 1
   for li in poly.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co
    uv.data[li].uv=(co[axis]/1.024,co.z/1.024)
  o=bpy.data.objects.new('astra_facades_'+key,me);visual.objects.link(o);me.materials.append(mats[key])
  o['canonical_city_lock']='Hamburg';o['authored_geometry']='LoD2 polygon apertures, reveals and architectural joinery'
 (src.parents[2]/'astra-proof').mkdir(exist_ok=True)
 (src.parents[2]/'astra-proof/facade-registration.json').write_text(json.dumps(records,indent=2))
 print('ASTRA_FACADE_OPENINGS',len(records),sum(r['openings'] for r in records))
