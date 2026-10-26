import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXTBOT ESCAPE", page_icon="👁️", layout="wide")

st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"]{background:#07090d;color:white}
[data-testid="stHeader"],footer{visibility:hidden}
.block-container{padding:1rem;max-width:1600px}
h1{text-align:center;color:#ff3b57;letter-spacing:5px}
</style>
<h1>NEXTBOT ESCAPE</h1>
<p style="text-align:center;color:#aaa">THU THẬP 8 PIN • TRÁNH NEXTBOT • TÌM CỬA THOÁT</p>
""", unsafe_allow_html=True)

game = r"""
<div id="wrap" style="position:relative;width:100%;height:78vh;min-height:520px;background:#05070a;overflow:hidden;border-radius:10px">
<canvas id="game" style="width:100%;height:100%;display:block"></canvas>

<div style="position:absolute;top:15px;left:15px;color:white;font: bold 15px Arial;background:#090d16cc;padding:12px;border-radius:8px">
<div style="color:#ff405a">MISSION</div>
<div id="count">PIN: 0 / 8</div>
<div style="margin-top:8px">STAMINA</div>
<div style="width:140px;height:7px;background:#333">
<div id="stamina" style="height:100%;width:100%;background:#50e59a"></div>
</div>
</div>

<div id="danger" style="position:absolute;top:18px;right:18px;color:#ff405a;font:bold 14px Arial"></div>
<div id="message" style="position:absolute;top:20%;width:100%;text-align:center;color:white;font:bold 20px Arial"></div>
<div style="position:absolute;top:50%;left:50%;color:white;pointer-events:none">+</div>

<div id="overlay" style="position:absolute;inset:0;background:#05070ae8;display:flex;align-items:center;justify-content:center;text-align:center;color:white;font-family:Arial">
<div>
<div style="color:#ff405a;letter-spacing:5px">SURVIVE THE MAZE</div>
<h1 id="title" style="font-size:45px">DON'T GET CAUGHT</h1>
<p id="desc">Thu thập đủ 8 pin rồi tìm cửa thoát màu xanh.<br>Đừng để Nextbot bắt được!</p>
<button id="start" style="padding:15px 35px;background:#ff304e;color:white;border:0;border-radius:6px;font-weight:bold;cursor:pointer">BẮT ĐẦU</button>
<p style="color:#aaa;font-size:12px">WASD di chuyển • SHIFT chạy • Chuột nhìn</p>
</div>
</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
(()=>{
const canvas=document.getElementById('game');
const overlay=document.getElementById('overlay');
const countEl=document.getElementById('count');
const staminaEl=document.getElementById('stamina');
const message=document.getElementById('message');
const danger=document.getElementById('danger');

let scene,camera,renderer,clock;
let active=false,pins=0,stamina=100,yaw=0,pitch=0;
const keys={},walls=[],pickups=[];
const N=15,CELL=4,HALF=N*CELL/2;
let player={x:-HALF+6,z:-HALF+6};
let bot,exitObj;

function rng(seed){
 let s=seed;
 return ()=>((s=(s*1664525+1013904223)>>>0)/4294967296);
}
const rand=rng(22);

function material(color,emissive=0){
 return new THREE.MeshStandardMaterial({
  color,roughness:.9,emissive,emissiveIntensity:.8
 });
}

function addWall(x,z,w,d){
 const mesh=new THREE.Mesh(
  new THREE.BoxGeometry(w,3.5,d),
  material(0x222936)
 );
 mesh.position.set(x,1.75,z);
 scene.add(mesh);
 walls.push({x,z,w,d});
}

function makeMaze(){
 const floor=new THREE.Mesh(
  new THREE.PlaneGeometry(N*CELL,N*CELL),
  material(0x171c25)
 );
 floor.rotation.x=-Math.PI/2;
 scene.add(floor);

 const grid=Array.from({length:N},()=>Array(N).fill(0));

 for(let i=0;i<N;i++){
  grid[0][i]=grid[N-1][i]=1;
  grid[i][0]=grid[i][N-1]=1;
 }

 for(let z=2;z<N-2;z++){
  for(let x=2;x<N-2;x++){
   if(rand()<.22 && !(x<4&&z<4) && !(x>10&&z>10)){
    grid[z][x]=1;
   }
  }
 }

 for(let x=1;x<N-1;x++){
  grid[4][x]=0;
  grid[9][x]=0;
 }

 for(let z=1;z<N-1;z++){
  grid[z][5]=0;
  grid[z][10]=0;
 }

 for(let z=0;z<N;z++){
  for(let x=0;x<N;x++){
   if(grid[z][x]){
    addWall((x-7)*CELL,(z-7)*CELL,CELL,CELL);
   }
  }
 }

 const ceiling=new THREE.Mesh(
  new THREE.PlaneGeometry(N*CELL,N*CELL),
  material(0x0b0e15)
 );
 ceiling.rotation.x=Math.PI/2;
 ceiling.position.y=3.55;
 scene.add(ceiling);

 for(let i=0;i<20;i++){
  const light=new THREE.Mesh(
   new THREE.BoxGeometry(1.5,.05,.12),
   new THREE.MeshBasicMaterial({
    color:i%3===0?0xff334d:0x92baff
   })
  );
  light.position.set(
   (rand()-.5)*N*CELL*.85,
   3.48,
   (rand()-.5)*N*CELL*.85
  );
  scene.add(light);
 }

 exitObj=new THREE.Group();
 exitObj.position.set(HALF-6,0,HALF-6);

 const gate=new THREE.Mesh(
  new THREE.BoxGeometry(2.4,2.8,.25),
  new THREE.MeshStandardMaterial({
   color:0x1be6a2,
   emissive:0x087c50,
   emissiveIntensity:1.5
  })
 );
 gate.position.y=1.4;
 exitObj.add(gate);
 scene.add(exitObj);

 const glow=new THREE.PointLight(0x13ffad,3,12);
 glow.position.set(HALF-6,2,HALF-6);
 scene.add(glow);
}

function makePin(x,z){
 const group=new THREE.Group();
 group.position.set(x,.8,z);

 const core=new THREE.Mesh(
  new THREE.OctahedronGeometry(.35),
  new THREE.MeshStandardMaterial({
   color:0x55eaff,
   emissive:0x1689bd,
   emissiveIntensity:2
  })
 );
 group.add(core);

 const ring=new THREE.Mesh(
  new THREE.TorusGeometry(.48,.045,8,24),
  new THREE.MeshBasicMaterial({color:0x70f5ff})
 );
 ring.rotation.x=Math.PI/2;
 group.add(ring);
 scene.add(group);
 pickups.push({obj:group,x,z,got:false});
}

function makeBot(){
 const c=document.createElement('canvas');
 c.width=c.height=256;
 const ctx=c.getContext('2d');

 ctx.fillStyle='#f7f7f7';
 ctx.fillRect(0,0,256,256);

 ctx.fillStyle='#111';
 ctx.beginPath();
 ctx.ellipse(76,93,22,34,0,0,Math.PI*2);
 ctx.ellipse(180,93,22,34,0,0,Math.PI*2);
 ctx.fill();

 ctx.strokeStyle='#111';
 ctx.lineWidth=13;
 ctx.beginPath();
 ctx.arc(128,145,62,.15*Math.PI,.85*Math.PI);
 ctx.stroke();

 const tex=new THREE.CanvasTexture(c);
 const face=new THREE.Mesh(
  new THREE.PlaneGeometry(2.4,2.4),
  new THREE.MeshBasicMaterial({map:tex,side:THREE.DoubleSide})
 );

 bot=new THREE.Group();
 bot.add(face);
 bot.position.set(HALF-12,1.8,-HALF+12);
 scene.add(bot);

 const light=new THREE.PointLight(0xff123d,2.5,10);
 light.position.z=1;
 bot.add(light);
}

function blocked(x,z){
 const r=.42;
 if(x < -HALF+1 || x > HALF-1 ||
    z < -HALF+1 || z > HALF-1) return true;

 return walls.some(w=>
  Math.abs(x-w.x)<w.w/2+r &&
  Math.abs(z-w.z)<w.d/2+r
 );
}

function resize(){
 if(!renderer)return;
 const r=canvas.getBoundingClientRect();
 renderer.setSize(r.width,r.height,false);
 camera.aspect=r.width/r.height;
 camera.updateProjectionMatrix();
}

function init(){
 scene=new THREE.Scene();
 scene.background=new THREE.Color(0x070a11);
 scene.fog=new THREE.FogExp2(0x070a11,.026);

 camera=new THREE.PerspectiveCamera(76,1,.1,180);
 camera.position.set(player.x,1.65,player.z);

 renderer=new THREE.WebGLRenderer({canvas,antialias:true});
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));
 renderer.outputColorSpace=THREE.SRGBColorSpace;

 scene.add(new THREE.HemisphereLight(0x8395b9,0x161923,1.2));

 const light=new THREE.PointLight(0x93b8ff,30,28);
 light.position.set(player.x,2.7,player.z);
 scene.add(light);

 makeMaze();
 makeBot();

 let made=0,attempt=0;
 while(made<8&&attempt++<500){
  const x=(Math.floor(rand()*(N-2))+1-7)*CELL;
  const z=(Math.floor(rand()*(N-2))+1-7)*CELL;

  if(Math.hypot(x-player.x,z-player.z)>8 &&
     Math.hypot(x-(HALF-6),z-(HALF-6))>5 &&
     !walls.some(w=>
      Math.abs(x-w.x)<w.w/2+1 &&
      Math.abs(z-w.z)<w.d/2+1
     )){
   makePin(x,z);
   made++;
  }
 }

 clock=new THREE.Clock();
 resize();
 window.addEventListener('resize',resize);
 renderer.setAnimationLoop(tick);
}

function start(){
 if(!renderer)init();

 player={x:-HALF+6,z:-HALF+6};
 pins=0;
 stamina=100;
 yaw=0;
 pitch=0;
 countEl.textContent='PIN: 0 / 8';
 staminaEl.style.width='100%';
 active=true;
 overlay.style.display='none';
 message.textContent='';
 canvas.requestPointerLock?.();
}

function finish(win){
 active=false;
 overlay.style.display='flex';

 document.getElementById('title').textContent=
  win?'YOU ESCAPED':'YOU GOT CAUGHT';

 document.getElementById('title').style.color=
  win?'#4df5b1':'#ff304e';

 document.getElementById('desc').textContent=
  win?'Bạn đã thoát khỏi mê cung!':
  'Nextbot đã bắt được bạn. Thử lại nhé!';

 document.getElementById('start').textContent='CHƠI LẠI';
 document.exitPointerLock?.();
}

document.getElementById('start').addEventListener('click',start);

document.addEventListener('keydown',e=>{
 keys[e.code]=true;
 if(e.code==='KeyE'&&!active)start();
});

document.addEventListener('keyup',e=>keys[e.code]=false);

document.addEventListener('mousemove',e=>{
 if(document.pointerLockElement===canvas&&active){
  yaw-=e.movementX*.0022;
  pitch-=e.movementY*.0022;
  pitch=Math.max(-1.25,Math.min(1.25,pitch));
 }
});

canvas.addEventListener('click',()=>{
 if(active)canvas.requestPointerLock?.();
});

function tick(){
 if(!renderer)return;
 const dt=Math.min(clock.getDelta(),.04);

 if(active){
  const fx=-Math.sin(yaw),fz=-Math.cos(yaw);
  const rx=Math.cos(yaw),rz=-Math.sin(yaw);
  let dx=0,dz=0;

  if(keys.KeyW||keys.ArrowUp){dx+=fx;dz+=fz}
  if(keys.KeyS||keys.ArrowDown){dx-=fx;dz-=fz}
  if(keys.KeyD||keys.ArrowRight){dx+=rx;dz+=rz}
  if(keys.KeyA||keys.ArrowLeft){dx-=rx;dz-=rz}

  const moving=Math.hypot(dx,dz)>0;
  const sprint=(keys.ShiftLeft||keys.ShiftRight)&&stamina>1&&moving;

  if(moving){
   const n=Math.hypot(dx,dz);
   dx/=n;dz/=n;

   const speed=sprint?7.5:4.4;
   if(sprint)stamina=Math.max(0,stamina-29*dt);
   else stamina=Math.min(100,stamina+17*dt);

   const nx=player.x+dx*speed*dt;
   const nz=player.z+dz*speed*dt;

   if(!blocked(nx,player.z))player.x=nx;
   if(!blocked(player.x,nz))player.z=nz;
  }else{
   stamina=Math.min(100,stamina+20*dt);
  }

  camera.position.set(player.x,1.65,player.z);
  camera.rotation.order='YXZ';
  camera.rotation.y=yaw;
  camera.rotation.x=pitch;

  staminaEl.style.width=stamina+'%';
  staminaEl.style.background=stamina<25?'#ff405a':'#50e59a';

  const dist=Math.hypot(
   bot.position.x-player.x,
   bot.position.z-player.z
  );

  const speed=2.35+Math.min(pins*.13,1.1)+(dist<8?1:0);
  const a=Math.atan2(
   player.x-bot.position.x,
   player.z-bot.position.z
  );

  bot.position.x+=Math.sin(a)*speed*dt;
  bot.position.z+=Math.cos(a)*speed*dt;
  bot.position.y=1.8+Math.sin(performance.now()*.006)*.12;
  bot.rotation.y=a;

  if(blocked(bot.position.x,bot.position.z)){
   bot.position.x-=Math.sin(a)*speed*dt*1.5;
   bot.position.z-=Math.cos(a)*speed*dt*1.5;
  }

  for(const p of pickups){
   if(!p.got){
    p.obj.rotation.y+=dt*1.6;
    p.obj.position.y=.8+Math.sin(performance.now()*.003+p.x)*.12;

    if(Math.hypot(p.x-player.x,p.z-player.z)<1.35){
     p.got=true;
     scene.remove(p.obj);
     pins++;
     countEl.textContent='PIN: '+pins+' / 8';
     message.textContent='ĐÃ NHẶT PIN!';
    }
   }
  }

  const exitDist=Math.hypot(
   exitObj.position.x-player.x,
   exitObj.position.z-player.z
  );

  if(exitDist<2.1){
   if(pins>=8){finish(true)}
   else{message.textContent='CẦN ĐỦ 8 PIN ĐỂ MỞ CỬA'}
  }else if(message.textContent==='CẦN ĐỦ 8 PIN ĐỂ MỞ CỬA'){
   message.textContent='';
  }

  danger.textContent=dist<13?'⚠ NEXTBOT ĐANG ĐẾN GẦN':'';
  if(dist<1.55)finish(false);
 }

 renderer.render(scene,camera);
}

init();
})();
</script>
"""
components.html(game,height=650,scrolling=False)
st.caption("Game cần internet để tải Three.js. Dùng máy tính và chuột để chơi.")
