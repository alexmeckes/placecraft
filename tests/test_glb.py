import copy
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'plugins/placecraft/skills/placecraft/scripts/check_glb.py'
spec=importlib.util.spec_from_file_location('check_glb',SCRIPT)
glb=importlib.util.module_from_spec(spec);spec.loader.exec_module(glb)


def fixture():
    binary=struct.pack('<18f3I',0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,0,0,1,0,1,2)
    doc={'asset':{'version':'2.0','generator':'fixture'},'buffers':[{'byteLength':len(binary)}],
         'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':36},{'buffer':0,'byteOffset':36,'byteLength':36},{'buffer':0,'byteOffset':72,'byteLength':12}],
         'accessors':[{'bufferView':0,'componentType':5126,'count':3,'type':'VEC3'}, {'bufferView':1,'componentType':5126,'count':3,'type':'VEC3'}, {'bufferView':2,'componentType':5125,'count':3,'type':'SCALAR'}],
         'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1},'indices':2}]}],
         'nodes':[{'mesh':0}],'scenes':[{'nodes':[0]}],'scene':0}
    return doc,binary


def encode(doc,binary):
    data=json.dumps(doc).encode();data+=b' '*((-len(data))%4);binary+=b'\0'*((-len(binary))%4)
    return struct.pack('<4sII',b'glTF',2,28+len(data)+len(binary))+struct.pack('<I4s',len(data),b'JSON')+data+struct.pack('<I4s',len(binary),b'BIN\0')+binary


class GLBTests(unittest.TestCase):
    def check(self,doc,binary):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'test.glb';path.write_bytes(encode(doc,binary));return glb.check(path)

    def test_valid_triangle(self):
        report,_=self.check(*fixture());self.assertEqual(report['triangles_in_mesh_definitions'],1)

    def test_bad_indices_fail(self):
        d,b=fixture();b=b[:-4]+struct.pack('<I',90)
        with self.assertRaisesRegex(ValueError,'triangle indices'):self.check(d,b)

    def test_nonfinite_positions_fail(self):
        d,b=fixture();b=struct.pack('<f',float('nan'))+b[4:]
        with self.assertRaisesRegex(ValueError,'Nonfinite'):self.check(d,b)

    def test_nonunit_normals_fail(self):
        d,b=fixture();b=b[:44]+struct.pack('<f',0)+b[48:]
        with self.assertRaisesRegex(ValueError,'Non-unit'):self.check(d,b)

    def test_accessor_overrun_fails(self):
        d,b=fixture();d['accessors'][0]['count']=4
        with self.assertRaisesRegex(ValueError,'extends past'):self.check(d,b)

    def test_external_buffer_fails(self):
        d,b=fixture();d['buffers'][0]['uri']='hidden.bin'
        with self.assertRaisesRegex(ValueError,'embedded buffer'):self.check(d,b)

    def test_sparse_fails(self):
        d,b=fixture();d['accessors'][0]['sparse']={}
        with self.assertRaisesRegex(ValueError,'Sparse'):self.check(d,b)

    def test_animation_fails(self):
        d,b=fixture();d['animations']=[{}]
        with self.assertRaisesRegex(ValueError,'animations'):self.check(d,b)

    def test_morph_targets_fail(self):
        d,b=fixture();d['meshes'][0]['primitives'][0]['targets']=[{'POSITION':0}]
        with self.assertRaisesRegex(ValueError,'static'):self.check(d,b)

    def test_interleaved_attributes(self):
        d,b=fixture();d['bufferViews']=[{'buffer':0,'byteLength':72,'byteStride':24},{'buffer':0,'byteOffset':72,'byteLength':12}]
        d['accessors'][1].update(bufferView=0,byteOffset=12);d['accessors'][2]['bufferView']=1
        b=struct.pack('<18f3I',0,0,0,0,0,1,1,0,0,0,0,1,0,1,0,0,0,1,0,1,2)
        report,_=self.check(d,b);self.assertTrue(report['unit_normals'])

    def test_payload_change_fails_comparison(self):
        d,b=fixture();changed=bytearray(b);changed[3]^=1
        with self.assertRaisesRegex(ValueError,'buffer differs'):glb.compare((d,b),(copy.deepcopy(d),bytes(changed)))

    def test_transform_change_fails_comparison(self):
        d,b=fixture();other=copy.deepcopy(d);other['nodes'][0]['translation']=[0,1,0]
        with self.assertRaisesRegex(ValueError,'JSON content differs'):glb.compare((d,b),(other,b))

    def test_generator_metadata_does_not_change_render_content(self):
        d,b=fixture();other=copy.deepcopy(d);other['asset']['generator']='another exporter'
        self.assertTrue(glb.compare((d,b),(other,b))['strict_render_content_identical'])

    def test_truncated_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'bad.glb';path.write_bytes(encode(*fixture())[:-3])
            with self.assertRaisesRegex(ValueError,'header/length'):glb.check(path)

if __name__=='__main__':unittest.main()
