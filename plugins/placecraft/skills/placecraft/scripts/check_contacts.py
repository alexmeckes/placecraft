"""Import a GLB in Blender and evaluate explicit world-space ray contracts."""
import argparse,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('model',type=Path);p.add_argument('contracts',type=Path);p.add_argument('--report',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(a.model.resolve()))
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
contracts=json.loads(a.contracts.read_text())
# GLB imported back into Blender restores source Z-up; contracts are in Z-up meters.
results=[]
trees={}
for c in contracts:
 direction=Vector(c['direction'])
 if direction.length==0 or c['distance']<=0:raise ValueError('Invalid ray')
 if c.get('include_materials'):
  key=tuple(sorted(c['include_materials']))
  if key not in trees:
   verts=[];faces=[]
   for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    evaluated=obj.evaluated_get(deps);data=evaluated.to_mesh()
    offset=len(verts);verts.extend(obj.matrix_world@v.co for v in data.vertices)
    for poly in data.polygons:
     material=data.materials[poly.material_index] if len(data.materials)>poly.material_index else None
     if material and material.name.split('.')[0] in key:faces.append(tuple(offset+i for i in poly.vertices))
    evaluated.to_mesh_clear()
   if not faces:raise ValueError('No mesh faces match material filter')
   trees[key]=BVHTree.FromPolygons(verts,faces)
  loc,normal,face,distance=trees[key].ray_cast(Vector(c['origin']),direction.normalized(),c['distance']);hit=loc is not None
 else:
  hit,loc,normal,face,obj,matrix=bpy.context.scene.ray_cast(deps,Vector(c['origin']),direction.normalized(),distance=c['distance'])
 passed=hit==c['expected_hit']
 if hit and 'z_range' in c:passed=passed and c['z_range'][0]<=loc.z<=c['z_range'][1]
 results.append({'name':c['name'],'passed':passed,'hit':hit,'location_z_up':list(loc) if hit else None})
a.report.write_text(json.dumps({'passed':bool(results) and all(r['passed'] for r in results),'rays':results,'scope':'Sampled exported mesh relationships, not collision/navigation certification.'},indent=2)+'\n')
if not results or not all(r['passed'] for r in results):raise RuntimeError('Export contact contract failed')
print('Export contact rays passed:',len(results))
