"""Remove unused vertex attributes and repack GLB bytes without geometry loss.

Only UV/tangent data on completely untextured materials is removed. Every
position, normal, index and image buffer is retained byte-for-byte. This is a
Cloudflare Pages delivery correction (25 MiB), unrelated to inspector caching.
"""
import copy, hashlib, json, struct, sys
from pathlib import Path

def pack(path):
 raw=path.read_bytes(); jl=struct.unpack_from('<I',raw,12)[0]
 doc=json.loads(raw[20:20+jl]); binary=raw[28+jl:]
 assert raw[:4]==b'glTF' and len(doc['buffers'])==1
 assert not doc.get('animations') and not doc.get('skins')
 assert all('sparse' not in a for a in doc['accessors'])
 before=copy.deepcopy(doc); removed=0
 for mesh in doc['meshes']:
  for primitive in mesh['primitives']:
   assert not primitive.get('extensions') and not primitive.get('targets')
   material=doc['materials'][primitive['material']]
   if 'Texture' not in json.dumps(material):
    for key in ['TANGENT','TEXCOORD_0','TEXCOORD_1']:
     if key in primitive['attributes']:
      primitive['attributes'].pop(key);removed+=1
 used_a=set()
 for m in doc['meshes']:
  for p in m['primitives']:
   used_a.update(p['attributes'].values())
   if 'indices' in p:used_a.add(p['indices'])
 amap={old:new for new,old in enumerate(sorted(used_a))}
 doc['accessors']=[doc['accessors'][old] for old in sorted(used_a)]
 for m in doc['meshes']:
  for p in m['primitives']:
   p['attributes']={key:amap[value] for key,value in p['attributes'].items()}
   if 'indices' in p:p['indices']=amap[p['indices']]
 used_v={a['bufferView'] for a in doc['accessors']}
 used_v.update(im['bufferView'] for im in doc.get('images',[]) if 'bufferView' in im)
 vmap={old:new for new,old in enumerate(sorted(used_v))};new_bin=bytearray();views=[]
 for old in sorted(used_v):
  view=copy.deepcopy(doc['bufferViews'][old]);start=view.get('byteOffset',0)
  while len(new_bin)%4:new_bin.append(0)
  view['byteOffset']=len(new_bin);new_bin.extend(binary[start:start+view['byteLength']]);views.append(view)
 doc['bufferViews']=views
 for a in doc['accessors']:a['bufferView']=vmap[a['bufferView']]
 for im in doc.get('images',[]):
  if 'bufferView' in im:im['bufferView']=vmap[im['bufferView']]
 while len(new_bin)%4:new_bin.append(0)
 doc['buffers'][0]['byteLength']=len(new_bin)
 def payload(g,b,aidx):
  a=g['accessors'][aidx];v=g['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)
  return b[start:start+v['byteLength']]
 preserved=0
 for oldm,newm in zip(before['meshes'],doc['meshes']):
  for oldp,newp in zip(oldm['primitives'],newm['primitives']):
   for key,a in newp['attributes'].items():
    assert payload(before,binary,oldp['attributes'][key])==payload(doc,new_bin,a);preserved+=1
   assert payload(before,binary,oldp['indices'])==payload(doc,new_bin,newp['indices'])
 for old,new in zip(before.get('images',[]),doc.get('images',[])):
  v=before['bufferViews'][old['bufferView']];w=doc['bufferViews'][new['bufferView']]
  assert binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]==new_bin[w['byteOffset']:w['byteOffset']+w['byteLength']]
 data=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();data+=b' '*((-len(data))%4)
 total=12+8+len(data)+8+len(new_bin)
 result=struct.pack('<4sII',b'glTF',2,total)+struct.pack('<I4s',len(data),b'JSON')+data+struct.pack('<I4s',len(new_bin),b'BIN\0')+new_bin
 assert len(result)==total
 report={'before_bytes':len(raw),'after_bytes':total,'saved_bytes':len(raw)-total,'removed_unused_attributes':removed,'retained_attribute_buffers_verified':preserved,'position_normal_index_image_bytes_unchanged':True,'sha256':hashlib.sha256(result).hexdigest(),'cloudflare_25_mib_limit':25*1024*1024}
 assert total<25*1024*1024,report
 path.write_bytes(result)
 return report
if __name__=='__main__':
 path=Path(sys.argv[1] if len(sys.argv)>1 else 'public/assets/3d/night-intersection/c0/core/night-intersection-c0.glb')
 report=pack(path);print(json.dumps(report,indent=2))
 if Path('astra-proof').is_dir():Path('astra-proof/export-pack.json').write_text(json.dumps(report,indent=2)+'\n')
