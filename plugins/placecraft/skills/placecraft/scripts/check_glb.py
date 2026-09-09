"""Validate a static uncompressed GLB and optionally compare strict render content.

This is a deliberately bounded checker, not the Khronos conformance validator.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import struct


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    raw = Path(path).read_bytes()
    require(len(raw) >= 20, 'Truncated GLB header')
    magic, version, size = struct.unpack_from('<4sII', raw)
    require(magic == b'glTF' and version == 2 and size == len(raw), 'Invalid GLB header/length')
    chunks = []; pos = 12
    while pos < size:
        require(pos+8 <= size, 'Truncated chunk header')
        length, kind = struct.unpack_from('<I4s', raw, pos)
        require(length % 4 == 0 and pos+8+length <= size, 'Invalid chunk length')
        chunks.append((kind, raw[pos+8:pos+8+length])); pos += 8+length
    require([kind for kind, _ in chunks] == [b'JSON', b'BIN\0'], 'Expected JSON then one embedded BIN chunk')
    doc = json.loads(chunks[0][1]); binary = chunks[1][1]
    require(doc.get('asset', {}).get('version') == '2.0', 'Expected glTF 2.0 asset')
    require(not doc.get('skins') and not doc.get('animations'), 'Skins/animations unsupported')
    buffers = doc.get('buffers', [])
    require(len(buffers) == 1 and 'uri' not in buffers[0], 'Only one embedded buffer is supported')
    require(0 <= len(binary)-buffers[0]['byteLength'] <= 3, 'BIN length does not match buffer')
    used_extensions = set(doc.get('extensionsUsed', []))
    require(not ({'KHR_draco_mesh_compression', 'EXT_meshopt_compression', 'EXT_mesh_gpu_instancing'} & used_extensions), 'Compressed/instanced geometry unsupported')
    for view in doc.get('bufferViews', []):
        require(view.get('buffer') == 0, 'Unexpected buffer reference')
        require(view.get('byteOffset', 0) >= 0 and view['byteLength'] >= 0 and
                view.get('byteOffset', 0)+view['byteLength'] <= buffers[0]['byteLength'], 'Buffer view out of bounds')
    for image in doc.get('images', []):
        require('uri' not in image and 'bufferView' in image, 'Only embedded images supported')
        require(0 <= image['bufferView'] < len(doc.get('bufferViews', [])), 'Image buffer view missing')
    return doc, binary, raw


def values(doc, binary, index):
    require(isinstance(index, int) and 0 <= index < len(doc.get('accessors', [])), 'Invalid accessor index')
    a = doc['accessors'][index]
    require('sparse' not in a and 'bufferView' in a, 'Sparse/unbuffered accessors unsupported')
    require(0 <= a['bufferView'] < len(doc.get('bufferViews', [])), 'Invalid buffer view index')
    view = doc['bufferViews'][a['bufferView']]
    formats = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
    counts = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
    require(a['componentType'] in formats and a['type'] in counts, 'Unsupported accessor type')
    fmt, width = formats[a['componentType']]; n = counts[a['type']]
    stride = view.get('byteStride', width*n); offset = a.get('byteOffset', 0)
    require(stride >= width*n and stride % width == 0 and offset >= 0 and a['count'] > 0, 'Invalid accessor stride/count/offset')
    require(offset+(a['count']-1)*stride+width*n <= view['byteLength'], 'Accessor extends past buffer view')
    start = view.get('byteOffset', 0)+offset
    result = [struct.unpack_from('<'+fmt*n, binary, start+i*stride) for i in range(a['count'])]
    require(all(math.isfinite(x) for row in result for x in row), 'Nonfinite accessor values')
    if a.get('normalized'):
        require(a['componentType'] in {5120, 5121, 5122, 5123}, 'Invalid normalized component type')
        scale = {5120:127,5121:255,5122:32767,5123:65535}[a['componentType']]
        result = [tuple(max(-1, v/scale) for v in row) for row in result]
    return result


def check(path):
    doc, binary, raw = load(path)
    # Validate every accessor, including ones not reachable from a mesh.
    decoded = [values(doc, binary, i) for i in range(len(doc.get('accessors', [])))]
    require(doc.get('meshes'), 'No meshes')
    triangles = 0; primitives = 0
    for mesh in doc['meshes']:
        require(mesh.get('primitives'), 'Mesh without primitives')
        for p in mesh['primitives']:
            require(p.get('mode', 4) == 4 and not p.get('targets'), 'Only static triangle primitives supported')
            require(not p.get('extensions'), 'Primitive extensions unsupported')
            attrs = p['attributes']; require({'POSITION', 'NORMAL'} <= attrs.keys(), 'Missing positions or normals')
            pos = decoded[attrs['POSITION']]; normals = decoded[attrs['NORMAL']]
            require(doc['accessors'][attrs['POSITION']]['type'] == 'VEC3', 'Positions must be VEC3')
            require(len(normals) == len(pos), 'Position/normal count mismatch')
            require(all(len(n) == 3 and .98 < sum(v*v for v in n) < 1.02 for n in normals), 'Non-unit normals')
            for attribute in attrs.values():
                require(len(decoded[attribute]) == len(pos), 'Attribute count mismatch')
            if 'indices' in p:
                ia = doc['accessors'][p['indices']]
                require(ia['type'] == 'SCALAR' and ia['componentType'] in {5121,5123,5125} and not ia.get('normalized'), 'Invalid index accessor')
                indices = [v[0] for v in decoded[p['indices']]]
            else:
                indices = list(range(len(pos)))
            require(len(indices) % 3 == 0 and all(0 <= i < len(pos) for i in indices), 'Invalid triangle indices')
            if 'material' in p:
                require(0 <= p['material'] < len(doc.get('materials', [])), 'Material missing')
            triangles += len(indices)//3; primitives += 1
    for node in doc.get('nodes', []):
        if 'mesh' in node:
            require(0 <= node['mesh'] < len(doc['meshes']), 'Node mesh missing')
        for key in ['matrix', 'translation', 'rotation', 'scale']:
            if key in node:
                require(all(math.isfinite(v) for v in node[key]), 'Nonfinite node transform')
    report = {'file':Path(path).name, 'sha256':hashlib.sha256(raw).hexdigest(),
              'triangles_in_mesh_definitions':triangles, 'primitives':primitives,
              'finite_attributes':True, 'unit_normals':True, 'valid_indices':True,
              'engine_ready':False}
    return report, (doc, binary)


def compare(left, right):
    a, ba = left; b, bb = right
    a = copy.deepcopy(a); b = copy.deepcopy(b)
    # Generator string is exporter metadata, not scene content. Nothing else is ignored.
    a.get('asset', {}).pop('generator', None); b.get('asset', {}).pop('generator', None)
    require(a == b, 'GLB JSON content differs (strict, ordering-sensitive comparison)')
    require(ba == bb, 'Embedded geometry/texture buffer differs')
    return {'strict_render_content_identical':True, 'comparison':'JSON excluding generator metadata + exact embedded BIN bytes'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('model', type=Path); p.add_argument('--compare', type=Path); p.add_argument('--report', type=Path)
    a = p.parse_args()
    try:
        report, content = check(a.model)
        if a.compare:
            _, other = check(a.compare); report.update(compare(content, other))
    except (ValueError, KeyError, IndexError, struct.error, OSError) as e:
        p.exit(1, f'GLB CHECK FAILED: {e}\n')
    text = json.dumps(report, indent=2)+'\n'; print(text, end='')
    if a.report:
        a.report.write_text(text)


if __name__ == '__main__':
    main()
