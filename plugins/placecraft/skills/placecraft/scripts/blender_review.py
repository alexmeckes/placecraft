"""Blender-side fixed review views and static preview export. Import inside Blender."""
import hashlib
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector


def point_at(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()


def export_and_review(out, objects, metadata, render=False):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    # Evaluate and batch copies by material; source objects remain independently editable.
    deps = bpy.context.evaluated_depsgraph_get()
    groups = {}
    for obj in objects:
        evaluated = obj.evaluated_get(deps)
        data = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=deps)
        data.transform(obj.matrix_world)
        duplicate = bpy.data.objects.new('Runtime copy', data)
        scene_collection = bpy.context.scene.collection
        scene_collection.objects.link(duplicate)
        key = tuple(m.name for m in data.materials)
        groups.setdefault(key, []).append(duplicate)
    runtime = []
    for key, group in sorted(groups.items()):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in group:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = group[0]
        if len(group) > 1:
            bpy.ops.object.join()
        group[0].name = 'Runtime_'+'_'.join(key)
        runtime.append(group[0])
    bpy.ops.object.select_all(action='DESELECT')
    for obj in runtime:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'), export_format='GLB',
                             use_selection=True, export_apply=True, export_yup=True,
                             export_cameras=False, export_lights=False)
    for obj in runtime:
        bpy.data.objects.remove(obj, do_unlink=True)
    points = [obj.matrix_world @ Vector(v) for obj in objects for v in obj.bound_box]
    low = Vector([min(p[k] for p in points) for k in range(3)])
    high = Vector([max(p[k] for p in points) for k in range(3)])
    center = (low+high)/2
    extent = max(high-low)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 850
    scene.render.resolution_percentage = 100
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.22, .25, .29, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .65
    scene.view_settings.view_transform = 'AgX'
    for name, offset, energy, size in [('Key', (-4,-6,8),1800,6), ('Fill',(5,-1,6),1200,5), ('Rim',(-1,5,7),1600,4)]:
        data = bpy.data.lights.new(name,'AREA'); data.energy=energy; data.shape='DISK'; data.size=size
        obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj)
        obj.location = center+Vector(offset); point_at(obj,center)
    camera_data=bpy.data.cameras.new('ReviewCamera'); camera_data.type='ORTHO'; camera_data.ortho_scale=extent*1.48
    camera=bpy.data.objects.new('ReviewCamera',camera_data); scene.collection.objects.link(camera); scene.camera=camera
    views={'overview':(7,-11,7),'front':(0,-12,3),'rear':(0,12,4),
           'left':(-12,0,4),'right':(12,0,4),'roof':(3,-5,13)}
    camera.location=center+Vector(views['overview']);point_at(camera,center)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'source.blend'))
    metadata.update(blender_version=bpy.app.version_string, source_coordinates='Z-up, meters',
                    runtime_coordinates='glTF Y-up, meters', engine_ready=False,
                    export_sha256=hashlib.sha256((out/'model.glb').read_bytes()).hexdigest(),
                    bounds_z_up=[list(low),list(high)],source_objects=len(objects),
                    views={name:list(offset) for name,offset in views.items()})
    (out/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    if render:
        for name,offset in views.items():
            camera.location=center+Vector(offset);point_at(camera,center)
            scene.render.filepath=str(out/f'{name}.png')
            bpy.ops.render.render(write_still=True)
