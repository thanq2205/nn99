
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NEXTBOT: Lost Mall",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background: #080b10; color: white; }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container { padding: 1rem 1rem 0; max-width: 1600px; }
    h1 { color: #ff4242; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 👁️ NEXTBOT: LOST MALL")
st.caption("SURVIVE THE NIGHT • COLLECT ORBS • DON'T GET CAUGHT")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* { box-sizing: border-box; }
body {
    margin: 0; background: #05070b; color: white;
    font-family: Arial, sans-serif; overflow: hidden;
}
#game { position: relative; width: 100%; height: 680px; overflow: hidden; }
canvas { display: block; width: 100%; height: 100%; }
#hud {
    position:absolute; inset:0; pointer-events:none;
    text-shadow: 0 2px 5px black;
}
#top {
    display:flex; justify-content:space-between;
    padding:18px; font-size:18px; font-weight:bold;
}
#crosshair {
    position:absolute; top:50%; left:50%;
    transform:translate(-50%,-50%); font-size:24px;
}
#message {
    position:absolute; top:43%; width:100%;
    text-align:center; font-size:22px; font-weight:bold;
}
#overlay {
    position:absolute; inset:0; display:flex;
    align-items:center; justify-content:center;
    background:rgba(0,0,0,.78); text-align:center;
}
.panel { max-width:480px; padding:25px; }
h1 { color:#ff4545; font-size:38px; }
button {
    pointer-events:auto; border:0; border-radius:8px;
    padding:14px 30px; color:white; background:#e52b3d;
    font-size:18px; font-weight:bold; cursor:pointer;
}
small { color:#c0c6d0; line-height:1.8; }
#stamina {
    position:absolute; bottom:28px; left:50%;
    transform:translateX(-50%); width:210px;
    height:9px; background:#333; border-radius:5px;
}
#bar { width:100%; height:100%; background:#64e6ff; border-radius:5px; }
</style>
</head>
<body>
<div id="game">
    <div id="hud">
        <div id="top">
            <div>ORB: <span id="score">0</span></div>
            <div id="status">THREAT: LOW</div>
        </div>
        <div id="crosshair">+</div>
        <div id="message"></div>
        <div id="stamina"><div id="bar"></div></div>
    </div>
    <div id="overlay">
        <div class="panel">
            <h1 id="title">NEXTBOT</h1>
            <p id="subtitle">LOST MALL — SURVIVE IF YOU CAN</p>
            <small>
                WASD — Move<br>
                SHIFT — Sprint<br>
                MOUSE — Look around<br><br>
                Collect glowing orbs. Don't let it catch you.
            </small>
            <p><button id="start">ENTER THE MALL</button></p>
            <small>Headphones recommended</small>
        </div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(() => {
const root = document.getElementById('game');
const overlay = document.getElementById('overlay');
const startBtn = document.getElementById('start');
const scoreEl = document.getElementById('score');
const statusEl = document.getElementById('status');
const messageEl = document.getElementById('message');
const barEl = document.getElementById('bar');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x080b12);
scene.fog = new THREE.Fog(0x080b12, 12, 48);

const camera = new THREE.PerspectiveCamera(
    76, root.clientWidth / root.clientHeight, 0.1, 100
);
camera.rotation.order = 'YXZ';
camera.position.set(0, 1.7, 12);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.7));
renderer.setSize(root.clientWidth, root.clientHeight);
renderer.outputEncoding = THREE.sRGBEncoding;
root.insertBefore(renderer.domElement, root.firstChild);

scene.add(new THREE.HemisphereLight(0xb9d8ff, 0x27202c, 1.25));

const lights = [];
for (let x=-16; x<=16; x+=8) {
    for (let z=-16; z<=16; z+=8) {
        const light = new THREE.PointLight(0xb9dfff, 1.3, 13);
        light.position.set(x, 3.7, z);
        scene.add(light);
        lights.push(light);
    }
}

const floorMat = new THREE.MeshStandardMaterial({
    color:0x242934, roughness:0.95
});
const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(42,42), floorMat
);
floor.rotation.x=-Math.PI/2;
floor.position.y=0;
scene.add(floor);

const ceiling = new THREE.Mesh(
    new THREE.PlaneGeometry(42,42),
    new THREE.MeshStandardMaterial({color:0x151922})
);
ceiling.rotation.x=Math.PI/2;
ceiling.position.y=5;
scene.add(ceiling);

const wallMat = new THREE.MeshStandardMaterial({
    color:0x414653, roughness:0.9
});
const trimMat = new THREE.MeshStandardMaterial({
    color:0x8995a6, roughness:0.6
});
const obstacles = [];

function wall(x,z,w,d,h=4.8) {
    const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(w,h,d), wallMat
    );
    mesh.position.set(x,h/2,z);
    scene.add(mesh);
    obstacles.push({x,z,w,d});
    return mesh;
}

// Outer walls
wall(0,-21,42,1);
wall(0,21,42,1);
wall(-21,0,1,42);
wall(21,0,1,42);

// Interior maze. Gaps connect the corridors.
wall(-12,-12,14,0.7);
wall(9,-12,15,0.7);
wall(-7,-5,0.7,11);
wall(5,-5,0.7,11);
wall(-12,3,12,0.7);
wall(12,3,12,0.7);
wall(-12,11,0.7,9);
wall(12,12,0.7,8);
wall(0,16,15,0.7);
wall(0,-18,0.7,5);
wall(-17,0,0.7,8);
wall(17,-4,0.7,10);
wall(0,7,0.7,5);

// Ceiling lights
for (let x=-16; x<=16; x+=8) {
    for (let z=-16; z<=16; z+=8) {
        const lamp = new THREE.Mesh(
            new THREE.BoxGeometry(2.1,0.09,0.6),
            new THREE.MeshBasicMaterial({color:0xd8edff})
        );
        lamp.position.set(x,4.8,z);
        scene.add(lamp);
    }
}

// Generic meme face texture for the chaser.
const faceCanvas = document.createElement('canvas');
faceCanvas.width=512;
faceCanvas.height=512;
const ctx=faceCanvas.getContext('2d');
ctx.fillStyle='#f3e9d7';
ctx.fillRect(0,0,512,512);
ctx.fillStyle='#171717';
ctx.beginPath();
ctx.ellipse(155,190,45,70,0,0,Math.PI*2);
ctx.ellipse(355,190,45,70,0,0,Math.PI*2);
ctx.fill();
ctx.fillStyle='#fff';
ctx.beginPath();
ctx.arc(165,175,12,0,Math.PI*2);
ctx.arc(365,175,12,0,Math.PI*2);
ctx.fill();
ctx.strokeStyle='#171717';
ctx.lineWidth=28;
ctx.beginPath();
ctx.moveTo(120,325);
ctx.quadraticCurveTo(250,440,390,325);
ctx.stroke();
ctx.fillStyle='#b72e36';
ctx.fillRect(205,355,100,23);
const faceTexture = new THREE.CanvasTexture(faceCanvas);
faceTexture.encoding=THREE.sRGBEncoding;

const enemy = new THREE.Group();
const face = new THREE.Mesh(
    new THREE.PlaneGeometry(2.3,2.3),
    new THREE.MeshBasicMaterial({
        map:faceTexture, side:THREE.DoubleSide
    })
);
face.position.y=1.65;
enemy.add(face);
const body = new THREE.Mesh(
    new THREE.BoxGeometry(1.7,2.6,0.65),
    new THREE.MeshStandardMaterial({
        color:0x1c111c, roughness:0.8
    })
);
body.position.y=0.9;
enemy.add(body);
scene.add(enemy);

// Collectible glowing orbs
let orbs=[];
function createOrbs() {
    for(const o of orbs) scene.remove(o.mesh);
    orbs=[];
    const positions=[
        [-16,-16],[-5,-16],[14,-17],[16,0],
        [-15,7],[-4,4],[8,8],[3,17],
        [-17,16],[15,15],[0,-7],[8,-5]
    ];
    for(const [x,z] of positions) {
        const mesh=new THREE.Mesh(
            new THREE.IcosahedronGeometry(0.32,1),
            new THREE.MeshStandardMaterial({
                color:0x55eaff, emissive:0x00aaff,
                emissiveIntensity:2.4, metalness:0.2,
                roughness:0.25
            })
        );
        mesh.position.set(x,1,z);
        scene.add(mesh);
        orbs.push({mesh,x,z,active:true});
    }
}

const keys={};
let yaw=0, pitch=0, score=0, stamina=100;
let running=false, playing=false, ended=false, elapsed=0;
const clock=new THREE.Clock();

function blocked(x,z) {
    const r=0.48;
    if(Math.abs(x)>19.9 || Math.abs(z)>19.9) return true;
    return obstacles.some(o =>
        x+r>o.x-o.w/2 && x-r<o.x+o.w/2 &&
        z+r>o.z-o.d/2 && z-r<o.z+o.d/2
    );
}

function reset() {
    score=0; stamina=100; elapsed=0;
    yaw=0; pitch=0;
    camera.position.set(0,1.7,12);
    enemy.position.set(-16,0,-16);
    createOrbs();
    scoreEl.textContent='0';
    barEl.style.width='100%';
    statusEl.textContent='THREAT: LOW';
    messageEl.textContent='';
    ended=false;
}

function finish(won) {
    playing=false;
    ended=true;
    if(document.pointerLockElement) document.exitPointerLock();
    overlay.style.display='flex';
    document.getElementById('title').textContent=
        won ? 'YOU SURVIVED!' : 'YOU GOT CAUGHT';
    document.getElementById('subtitle').textContent=
        won ? 'THE MALL IS QUIET... FOR NOW.' :
        'THE NEXTBOT FOUND YOU.';
    startBtn.textContent='PLAY AGAIN';
}

startBtn.addEventListener('click', () => {
    if(!ended) reset();
    overlay.style.display='none';
    renderer.domElement.requestPointerLock();
});

document.addEventListener('pointerlockchange', () => {
    if(document.pointerLockElement===renderer.domElement) {
        playing=true;
        clock.getDelta();
    } else {
        if(playing) {
            playing=false;
            overlay.style.display='flex';
            document.getElementById('title').textContent='PAUSED';
            document.getElementById('subtitle').textContent=
                'CLICK ENTER TO CONTINUE';
            startBtn.textContent='RESUME';
        }
    }
});

document.addEventListener('mousemove', e => {
    if(!playing) return;
    yaw-=e.movementX*0.0022;
    pitch-=e.movementY*0.0022;
    pitch=Math.max(-1.45,Math.min(1.45,pitch));
});

document.addEventListener('keydown', e => {
    keys[e.code]=true;
    if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))
        e.preventDefault();
});
document.addEventListener('keyup',e=>keys[e.code]=false);

function update(dt) {
    elapsed+=dt;
    camera.rotation.set(pitch,yaw,0,'YXZ');

    const forward=new THREE.Vector3(-Math.sin(yaw),0,-Math.cos(yaw));
    const right=new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw));
    const move=new THREE.Vector3();

    if(keys.KeyW) move.add(forward);
    if(keys.KeyS) move.sub(forward);
    if(keys.KeyD) move.add(right);
    if(keys.KeyA) move.sub(right);

    const sprint=(keys.ShiftLeft||keys.ShiftRight) &&
                 stamina>0 && move.lengthSq()>0;
    if(sprint) stamina=Math.max(0,stamina-30*dt);
    else stamina=Math.min(100,stamina+18*dt);
    barEl.style.width=stamina+'%';

    if(move.lengthSq()>0) {
        move.normalize().multiplyScalar((sprint?7.8:4.3)*dt);
        const p=camera.position;
        if(!blocked(p.x+move.x,p.z)) p.x+=move.x;
        if(!blocked(p.x,p.z+move.z)) p.z+=move.z;
    }

    // The bot pursues directly and may need to go around walls.
    const dx=camera.position.x-enemy.position.x;
    const dz=camera.position.z-enemy.position.z;
    const dist=Math.hypot(dx,dz);
    const speed=2.0+Math.min(score*0.12,1.4)+
                Math.min(elapsed*0.012,0.9);
    if(dist>0.001) {
        const stepX=dx/dist*speed*dt;
        const stepZ=dz/dist*speed*dt;
        if(!blocked(enemy.position.x+stepX,enemy.position.z))
            enemy.position.x+=stepX;
        if(!blocked(enemy.position.x,enemy.position.z+stepZ))
            enemy.position.z+=stepZ;
    }

    face.lookAt(camera.position.x,face.position.y,camera.position.z);
    enemy.position.y=0.06*Math.sin(elapsed*5);
    enemy.rotation.y=Math.atan2(
        camera.position.x-enemy.position.x,
        camera.position.z-enemy.position.z
    );

    statusEl.textContent=dist<7?'THREAT: HIGH':
                         dist<13?'THREAT: MEDIUM':'THREAT: LOW';
    if(dist<7) messageEl.textContent='RUN!';
    else messageEl.textContent='';

    for(const o of orbs) {
        if(!o.active) continue;
        o.mesh.rotation.y+=dt*1.8;
        o.mesh.position.y=1+Math.sin(elapsed*2+o.x)*0.15;
        if(Math.hypot(camera.position.x-o.x,camera.position.z-o.z)<1.25) {
            o.active=false;
            scene.remove(o.mesh);
            score++;
            scoreEl.textContent=score;
        }
    }

    if(dist<1.65) finish(false);
    if(score===orbs.length) finish(true);
}

function animate() {
    requestAnimationFrame(animate);
    const dt=Math.min(clock.getDelta(),0.05);
    if(playing) update(dt);
    renderer.render(scene,camera);
}
animate();

window.addEventListener('resize',()=>{
    camera.aspect=root.clientWidth/root.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(root.clientWidth,root.clientHeight);
});
})();
</script>
</body>
</html>
"""

components.html(game_html, height=690, scrolling=False)
