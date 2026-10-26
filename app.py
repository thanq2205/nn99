import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NEXTBOT 3D",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background: #080b10;
        color: #f3f6fb;
    }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container { padding: 0.8rem 0.8rem 0; max-width: 1500px; }
    h1 { text-align: center; color: #ff4545; margin-bottom: 0; }
    [data-testid="stCaptionContainer"] { text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 👁️ NEXTBOT 3D")
st.caption("SURVIVE THE MALL • COLLECT ORBS • DON'T GET CAUGHT")

game_html = r"""
<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#07090e;color:#fff;font-family:Arial,sans-serif}
#game{position:relative;width:100%;height:690px;overflow:hidden;background:#07090e}
canvas{display:block;width:100%;height:100%}
#hud{position:absolute;inset:0;pointer-events:none;text-shadow:0 2px 5px #000}
#top{display:flex;justify-content:space-between;padding:16px 18px;font-size:16px;font-weight:700}
#crosshair{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);font-size:22px}
#message{position:absolute;left:0;right:0;top:39%;text-align:center;color:#ff4c55;font-size:24px;font-weight:900}
#bottom{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);width:210px;text-align:center;font-size:11px;color:#dce6f4}
#stamina{height:8px;background:#303744;border-radius:8px;overflow:hidden;margin-top:5px}
#bar{height:100%;width:100%;background:#54dcff;transition:width .08s}
#overlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(2,4,8,.82);text-align:center}
.panel{max-width:480px;padding:24px}
h2{font-size:42px;color:#ff424e;margin:0 0 8px}
small{color:#c2cad8;line-height:1.9}
button{border:0;border-radius:8px;padding:13px 24px;background:#e72d40;color:white;font-size:16px;font-weight:bold;cursor:pointer;margin-top:18px}
#toast{position:absolute;left:0;right:0;bottom:62px;text-align:center;color:#72edff;font-weight:bold}
@media(max-width:600px){#game{height:620px}h2{font-size:32px}}
</style>
</head>
<body>
<div id="game">
  <div id="hud">
    <div id="top"><div>ORB: <span id="score">0</span>/10</div><div id="threat">THREAT: LOW</div></div>
    <div id="crosshair">+</div>
    <div id="message"></div>
    <div id="toast"></div>
    <div id="bottom">STAMINA<div id="stamina"><div id="bar"></div></div></div>
  </div>
  <div id="overlay">
    <div class="panel">
      <h2 id="title">NEXTBOT 3D</h2>
      <div id="subtitle">LOST MALL — SURVIVE IF YOU CAN</div>
      <p><small>W A S D — Di chuyển<br>SHIFT — Chạy nhanh<br>CHUỘT — Nhìn xung quanh<br>Thu thập 10 orb và tránh Nextbot.</small></p>
      <button id="start">BẮT ĐẦU</button>
      <p><small>Game prototype • Three.js</small></p>
    </div>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(() => {
const root = document.getElementById('game');
const overlay = document.getElementById('overlay');
const startButton = document.getElementById('start');
const scoreNode = document.getElementById('score');
const threatNode = document.getElementById('threat');
const messageNode = document.getElementById('message');
const toastNode = document.getElementById('toast');
const staminaBar = document.getElementById('bar');

if (!window.THREE) {
  document.getElementById('subtitle').textContent =
    'Không tải được Three.js. Hãy kiểm tra kết nối Internet rồi tải lại trang.';
  startButton.style.display = 'none';
  return;
}

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x080b12);
scene.fog = new THREE.Fog(0x080b12, 10, 43);

const camera = new THREE.PerspectiveCamera(76, 1, 0.1, 90);
camera.rotation.order = 'YXZ';
camera.position.set(0, 1.65, 13);

const renderer = new THREE.WebGLRenderer({antialias:false, powerPreference:'low-power'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.35));
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.setSize(root.clientWidth, root.clientHeight);
root.insertBefore(renderer.domElement, root.firstChild);

scene.add(new THREE.HemisphereLight(0xb8d7ff, 0x27202d, 1.15));
const mainLight = new THREE.DirectionalLight(0xe1eaff, 0.65);
mainLight.position.set(3, 8, 4);
scene.add(mainLight);

const floorMat = new THREE.MeshStandardMaterial({color:0x252a34, roughness:1});
const wallMat = new THREE.MeshStandardMaterial({color:0x3d4350, roughness:1});
const darkMat = new THREE.MeshStandardMaterial({color:0x171c25, roughness:1});
const obstacles = [];

function addBox(x,y,z,w,h,d,material,solid=true) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), material);
  mesh.position.set(x,y,z);
  scene.add(mesh);
  if (solid) obstacles.push({x,z,w,d});
  return mesh;
}

const floor = new THREE.Mesh(new THREE.PlaneGeometry(42,42), floorMat);
floor.rotation.x = -Math.PI/2;
scene.add(floor);
const ceiling = new THREE.Mesh(new THREE.PlaneGeometry(42,42), darkMat);
ceiling.rotation.x = Math.PI/2;
ceiling.position.y = 4.8;
scene.add(ceiling);

// Outer walls and a compact maze with broad gaps.
addBox(0,2.4,-21,42,4.8,1,wallMat);
addBox(0,2.4,21,42,4.8,1,wallMat);
addBox(-21,2.4,0,1,4.8,42,wallMat);
addBox(21,2.4,0,1,4.8,42,wallMat);
addBox(-12,2.1,-12,14,4.2,.65,wallMat);
addBox(9,2.1,-12,15,4.2,.65,wallMat);
addBox(-7,2.1,-5,.65,4.2,11,wallMat);
addBox(5,2.1,-5,.65,4.2,11,wallMat);
addBox(-12,2.1,3,12,4.2,.65,wallMat);
addBox(12,2.1,3,12,4.2,.65,wallMat);
addBox(-12,2.1,11,.65,4.2,9,wallMat);
addBox(12,2.1,12,.65,4.2,8,wallMat);
addBox(0,2.1,16,15,4.2,.65,wallMat);
addBox(0,2.1,-18,.65,4.2,5,wallMat);
addBox(-17,2.1,0,.65,4.2,8,wallMat);
addBox(17,2.1,-4,.65,4.2,10,wallMat);

// Ceiling panels: emissive materials, no extra dynamic lights.
const lampMat = new THREE.MeshBasicMaterial({color:0xc9e8ff});
for(let x=-16;x<=16;x+=8){
  for(let z=-16;z<=16;z+=8){
    addBox(x,4.72,z,2,.07,.55,lampMat,false);
  }
}

// Draw a simple meme face locally; no external image assets needed.
const fc = document.createElement('canvas');
fc.width = fc.height = 256;
const cx = fc.getContext('2d');
cx.fillStyle = '#f1e8d7'; cx.fillRect(0,0,256,256);
cx.fillStyle = '#151515';
cx.beginPath(); cx.ellipse(78,91,22,34,0,0,Math.PI*2); cx.ellipse(178,91,22,34,0,0,Math.PI*2); cx.fill();
cx.fillStyle = '#fff';
cx.beginPath(); cx.arc(83,84,6,0,Math.PI*2); cx.arc(183,84,6,0,Math.PI*2); cx.fill();
cx.strokeStyle = '#171717'; cx.lineWidth = 14;
cx.beginPath(); cx.moveTo(57,166); cx.quadraticCurveTo(128,226,202,166); cx.stroke();
cx.fillStyle = '#ad2732'; cx.fillRect(100,184,56,12);
const faceTexture = new THREE.CanvasTexture(fc);
faceTexture.encoding = THREE.sRGBEncoding;

const bot = new THREE.Group();
const botBody = new THREE.Mesh(
  new THREE.BoxGeometry(1.45,2.25,.6),
  new THREE.MeshStandardMaterial({color:0x171019,roughness:1})
);
botBody.position.y = 1.05;
bot.add(botBody);
const botFace = new THREE.Mesh(
  new THREE.PlaneGeometry(1.85,1.85),
  new THREE.MeshBasicMaterial({map:faceTexture,side:THREE.DoubleSide})
);
botFace.position.set(0,1.7,.34);
bot.add(botFace);
scene.add(bot);

const orbLocations = [
  [-16,-16],[-5,-16],[14,-17],[16,0],[-15,7],
  [-4,4],[8,8],[3,17],[-17,16],[15,15]
];
let orbs = [];
function createOrbs(){
  for(const orb of orbs) scene.remove(orb.mesh);
  orbs = [];
  for(const [x,z] of orbLocations){
    const mesh = new THREE.Mesh(
      new THREE.IcosahedronGeometry(.29,1),
      new THREE.MeshBasicMaterial({color:0x58eaff})
    );
    mesh.position.set(x,.95,z);
    scene.add(mesh);
    orbs.push({mesh,x,z,active:true});
  }
}

const keys = Object.create(null);
let yaw = 0, pitch = 0, score = 0, stamina = 100;
let playing = false, ended = false, elapsed = 0;
const clock = new THREE.Clock();

function isBlocked(x,z,r=.43){
  if(Math.abs(x)>19.8 || Math.abs(z)>19.8) return true;
  return obstacles.some(o =>
    x+r > o.x-o.w/2 && x-r < o.x+o.w/2 &&
    z+r > o.z-o.d/2 && z-r < o.z+o.d/2
  );
}

function resetGame(){
  score=0; stamina=100; elapsed=0; yaw=0; pitch=0;
  camera.position.set(0,1.65,13);
  bot.position.set(-16,0,-16);
  createOrbs();
  scoreNode.textContent='0';
  staminaBar.style.width='100%';
  threatNode.textContent='THREAT: LOW';
  messageNode.textContent='';
  toastNode.textContent='';
  ended=false;
}

function showEnd(won){
  playing=false; ended=true;
  if(document.pointerLockElement) document.exitPointerLock();
  overlay.style.display='flex';
  document.getElementById('title').textContent=won?'YOU SURVIVED':'YOU GOT CAUGHT';
  document.getElementById('subtitle').textContent=won
    ? 'Bạn đã thu thập đủ orb. Giỏi lắm!'
    : 'Nextbot đã bắt được bạn. Thử lại nhé!';
  startButton.textContent='CHƠI LẠI';
}

startButton.addEventListener('click',()=>{
  if(ended || startButton.textContent==='BẮT ĐẦU') resetGame();
  overlay.style.display='none';
  renderer.domElement.requestPointerLock();
});

document.addEventListener('pointerlockchange',()=>{
  if(document.pointerLockElement===renderer.domElement){
    playing=true;
    clock.getDelta();
  } else if(playing){
    playing=false;
    overlay.style.display='flex';
    document.getElementById('title').textContent='TẠM DỪNG';
    document.getElementById('subtitle').textContent='Bấm tiếp tục để chơi tiếp.';
    startButton.textContent='TIẾP TỤC';
  }
});

document.addEventListener('mousemove',e=>{
  if(!playing) return;
  yaw -= e.movementX*.0022;
  pitch -= e.movementY*.0022;
  pitch = Math.max(-1.4,Math.min(1.4,pitch));
});

document.addEventListener('keydown',e=>{
  keys[e.code]=true;
  if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)) e.preventDefault();
});
document.addEventListener('keyup',e=>{keys[e.code]=false;});
window.addEventListener('blur',()=>{for(const k in keys) keys[k]=false;});

function update(dt){
  elapsed += dt;
  camera.rotation.set(pitch,yaw,0,'YXZ');

  const forward = new THREE.Vector3(-Math.sin(yaw),0,-Math.cos(yaw));
  const right = new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw));
  const move = new THREE.Vector3();
  if(keys.KeyW || keys.ArrowUp) move.add(forward);
  if(keys.KeyS || keys.ArrowDown) move.sub(forward);
  if(keys.KeyD || keys.ArrowRight) move.add(right);
  if(keys.KeyA || keys.ArrowLeft) move.sub(right);

  const sprint = (keys.ShiftLeft || keys.ShiftRight) && stamina>0 && move.lengthSq()>0;
  if(sprint) stamina=Math.max(0,stamina-32*dt);
  else stamina=Math.min(100,stamina+20*dt);
  staminaBar.style.width=stamina+'%';

  if(move.lengthSq()>0){
    move.normalize().multiplyScalar((sprint?7.2:4.1)*dt);
    const p=camera.position;
    if(!isBlocked(p.x+move.x,p.z)) p.x+=move.x;
    if(!isBlocked(p.x,p.z+move.z)) p.z+=move.z;
  }

  const dx=camera.position.x-bot.position.x;
  const dz=camera.position.z-bot.position.z;
  const distance=Math.hypot(dx,dz);
  const speed=1.9+Math.min(score*.1,1.1)+Math.min(elapsed*.008,.7);
  if(distance>.001){
    const sx=dx/distance*speed*dt;
    const sz=dz/distance*speed*dt;
    if(!isBlocked(bot.position.x+sx,bot.position.z)) bot.position.x+=sx;
    if(!isBlocked(bot.position.x,bot.position.z+sz)) bot.position.z+=sz;
  }
  bot.position.y=.05*Math.sin(elapsed*5);
  bot.rotation.y=Math.atan2(dx,dz);

  if(distance<6.5){
    threatNode.textContent='THREAT: HIGH';
    messageNode.textContent='CHẠY ĐI!';
  }else if(distance<12){
    threatNode.textContent='THREAT: MEDIUM';
    messageNode.textContent='';
  }else{
    threatNode.textContent='THREAT: LOW';
    messageNode.textContent='';
  }

  for(const orb of orbs){
    if(!orb.active) continue;
    orb.mesh.rotation.y += dt*1.8;
    orb.mesh.position.y = .95 + Math.sin(elapsed*2+orb.x)*.13;
    if(Math.hypot(camera.position.x-orb.x,camera.position.z-orb.z)<1.15){
      orb.active=false;
      scene.remove(orb.mesh);
      score++;
      scoreNode.textContent=String(score);
      toastNode.textContent='+1 ORB';
    }
  }

  if(distance<1.45){showEnd(false);return;}
  if(score===orbLocations.length){showEnd(true);}
}

function resize(){
  const w=Math.max(1,root.clientWidth), h=Math.max(1,root.clientHeight);
  camera.aspect=w/h;
  camera.updateProjectionMatrix();
  renderer.setSize(w,h);
}
window.addEventListener('resize',resize);
resize();

function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),.05);
  if(playing) update(dt);
  renderer.render(scene,camera);
}
createOrbs();
animate();
})();
</script>
</body>
</html>
"""

components.html(game_html, height=700, scrolling=False)
