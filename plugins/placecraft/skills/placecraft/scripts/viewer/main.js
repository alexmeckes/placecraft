import * as THREE from 'three';
import {GLTFLoader} from './lib/GLTFLoader.js';
const canvas=document.querySelector('#view');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.2;
const scene=new THREE.Scene();scene.background=new THREE.Color('#20282e');
const camera=new THREE.PerspectiveCamera(36,1,.05,150);
const target=new THREE.Vector3();let radius=11,theta=.55,phi=1.05,rotating=false;
scene.add(new THREE.HemisphereLight(0xe2ecff,0x6f6248,2.5));
const key=new THREE.DirectionalLight(0xffe3bf,3.5);key.position.set(-4,8,6);key.castShadow=true;
key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-9,right:9,top:9,bottom:-9});key.shadow.normalBias=.025;scene.add(key);
const fill=new THREE.DirectionalLight(0xc7dbff,1.5);fill.position.set(6,5,-4);scene.add(fill);
function resize(){renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();}addEventListener('resize',resize);resize();
function updateCamera(){camera.position.set(target.x+radius*Math.sin(phi)*Math.sin(theta),target.y+radius*Math.cos(phi),target.z+radius*Math.sin(phi)*Math.cos(theta));camera.lookAt(target);}
const angles={overview:[.55,1.05],front:[0,1.47],rear:[Math.PI,1.4],left:[-Math.PI/2,1.4],right:[Math.PI/2,1.4],roof:[.3,.28]};
function setView(name){if(!angles[name])throw Error('Unknown view');[theta,phi]=angles[name];rotating=false;document.querySelector('#rotate').setAttribute('aria-pressed','false');updateCamera();renderer.render(scene,camera);}
for(const b of document.querySelectorAll('[data-view]'))b.onclick=()=>setView(b.dataset.view);
document.querySelector('#rotate').onclick=e=>{rotating=!rotating;e.target.setAttribute('aria-pressed',String(rotating));};
let last=null;canvas.onpointerdown=e=>{last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);};canvas.onpointerup=()=>last=null;canvas.onpointercancel=()=>last=null;
canvas.onpointermove=e=>{if(last){theta-=(e.clientX-last[0])*.007;phi=THREE.MathUtils.clamp(phi+(e.clientY-last[1])*.007,.12,1.7);last=[e.clientX,e.clientY];rotating=false;document.querySelector('#rotate').setAttribute('aria-pressed','false');}};
canvas.addEventListener('wheel',e=>{e.preventDefault();radius=THREE.MathUtils.clamp(radius*Math.exp(e.deltaY*.001),3,40);},{passive:false});
window.placecraft={ready:false,setView};
try{
 const gltf=await new GLTFLoader().loadAsync('./model.glb');
 gltf.scene.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});scene.add(gltf.scene);
 const bounds=new THREE.Box3().setFromObject(gltf.scene);bounds.getCenter(target);
 radius=bounds.getSize(new THREE.Vector3()).length()*1.6;
 window.placecraft.ready=true;document.querySelector('#status').textContent='';setView('overview');
}catch(e){document.querySelector('#status').textContent='Load failed';document.querySelector('#error').textContent=String(e);window.placecraft.error=String(e);}
let previous=performance.now();renderer.setAnimationLoop(now=>{if(rotating)theta+=(now-previous)*.00018;previous=now;updateCamera();renderer.render(scene,camera);});
