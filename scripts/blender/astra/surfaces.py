"""Small packed PBR maps authored from mathematical material structure.
No reference photograph is sampled. UV scale is in metres, not per-window tiles.
"""
import bpy
import numpy as np

def image(name, rgb, space):
 h,w,_=rgb.shape
 old=bpy.data.images.get(name)
 if old:bpy.data.images.remove(old)
 im=bpy.data.images.new(name,width=w,height=h,alpha=False)
 im.colorspace_settings.name=space
 rgba=np.ones((h,w,4),dtype=np.float32);rgba[:,:,:3]=rgb
 im.pixels.foreach_set(rgba.ravel());im.pack();return im

def add_maps(material, name, brick=False):
 n=512 if brick else 256;rng=np.random.default_rng(640 if brick else 312)
 yy,xx=np.mgrid[0:n,0:n];noise=rng.random((n,n))
 nodes=material.node_tree.nodes;links=material.node_tree.links;p=nodes.get('Principled BSDF')
 if brick:
  row=(yy//32); bx=(xx+(row%2)*64)%128;by=yy%32
  joint=(bx<3)|(by<3)
  seed=((xx+(row%2)*64)//128+row*19)%23
  value=.83+seed/115+noise*.045
  rgb=np.stack([value*.60,value*.29,value*.17],axis=-1)
  rgb[joint]=(.36,.33,.28)
  texture=nodes.new('ShaderNodeTexImage');texture.image=image(name+'_albedo_512',rgb,'sRGB')
  links.new(texture.outputs['Color'],p.inputs['Base Color'])
  height=np.where(joint,0,.65)+noise*.025
 else:height=noise*.018
 dx=np.roll(height,-1,axis=1)-np.roll(height,1,axis=1)
 dy=np.roll(height,-1,axis=0)-np.roll(height,1,axis=0)
 normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 texture=nodes.new('ShaderNodeTexImage');texture.image=image(name+'_normal',normal*.5+.5,'Non-Color')
 nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5 if brick else .35
 links.new(texture.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
