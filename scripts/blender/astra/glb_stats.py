"""Read exported runtime counts, not Blender edit-mesh estimates."""
import io,json,struct
from pathlib import Path
from PIL import Image
p=Path('public/assets/3d/night-intersection/c0/core/night-intersection-c0.glb')
b=p.read_bytes(); jlen=struct.unpack_from('<I',b,12)[0]; g=json.loads(b[20:20+jlen]); binary=b[28+jlen:]
a=g['accessors']; ps=[p for m in g['meshes'] for p in m['primitives']]
images=[]
for im in g.get('images',[]):
 v=g['bufferViews'][im['bufferView']]; start=v.get('byteOffset',0)
 img=Image.open(io.BytesIO(binary[start:start+v['byteLength']]))
 images.append({'name':im.get('name'), 'size':img.size,'bytes':v['byteLength']})
r={'glb_bytes':len(b),'triangles':sum(a[p['indices']]['count']//3 for p in ps),'vertices':sum(a[p['attributes']['POSITION']]['count'] for p in ps),'meshes':len(g['meshes']),'primitives':len(ps),'materials':len(g['materials']),'textures':images,'location':'Hansaplatz, Hamburg-St. Georg','lat':53.554451,'lon':10.012056}
assert r['glb_bytes']<45_000_000,r
assert r['triangles']<900_000,r
p.with_name('STATS.json').write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2))
