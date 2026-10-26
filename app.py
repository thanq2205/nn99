import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Verity Escape 3D", page_icon="👾", layout="wide")
st.title("👾 Verity Escape 3D")
st.caption("Bấm vào khung game để bắt đầu. W A S D: đi | Chuột hoặc ← →: xoay | ESC: thả chuột")

GAME_HTML = """
<div id="wrap" style="position:relative;width:100%;height:600px;font-family:sans-serif;color:#fff;overflow:hidden;border-radius:12px;background:#000">
  <canvas id="c" style="width:100%;height:600px;display:block;outline:none;cursor:crosshair" tabindex="0"></canvas>
  <div id="vig" style="position:absolute;inset:0;pointer-events:none;box-shadow:inset 0 0 160px 40px rgba(255,0,0,.9);opacity:0"></div>
  <div style="position:absolute;top:50%;left:50%;width:6px;height:6px;margin:-3px 0 0 -3px;border-radius:50%;background:rgba(255,255,255,.8);pointer-events:none"></div>
  <div id="hud" style="position:absolute;top:8px;left:12px;right:12px;font-size:15px;line-height:1.6;text-shadow:0 0 4px #000;pointer-events:none"></div>
  <div id="toast" style="position:absolute;top:120px;left:0;right:0;text-align:center;font-size:20px;font-weight:bold;text-shadow:0 0 6px #000;pointer-events:none"></div>
  <div id="panel" style="display:none;position:absolute;bottom:20px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.85);padding:14px 18px;border-radius:10px;text-align:center">
    <div id="ptext" style="margin-bottom:8px"></div>
    <input id="inp" autocomplete="off" style="padding:6px 10px;font-size:16px;border-radius:6px;border:none;text-transform:uppercase">
    <button id="ok" style="padding:6px 14px;font-size:16px;border-radius:6px;border:none;background:#22c55e;color:#fff;cursor:pointer">Mở khóa 🔓</button>
  </div>
  <div id="start" style="position:absolute;inset:0;background:rgba(0,0,0,.75);text-align:center;padding-top:200px;font-size:24px;cursor:pointer">
    👾 VERITY ESCAPE<br><br>Bấm vào đây để vào game<br>
    <span style="font-size:16px">W A S D: đi &nbsp;|&nbsp; Chuột hoặc ← →: xoay &nbsp;|&nbsp; Nhặt các chữ cái vàng, tránh Verity!</span>
  </div>
  <div id="end" style="display:none;position:absolute;inset:0;background:rgba(0,0,0,.85);text-align:center;padding-top:200px;font-size:28px">
    🎉 Bạn đã thoát khỏi trường học và cắt đuôi Verity!<br><br>
    <button id="again" style="padding:8px 20px;font-size:18px;border-radius:8px;border:none;background:#3b82f6;color:#fff;cursor:pointer">Chơi lại</button>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const LEVELS = [
  {name: "Sân trường",        hint: "✏️ viết chữ",              word: "BUT"},
  {name: "Hành lang",         hint: "📖 đọc, học bài",          word: "SACH"},
  {name: "Lớp học",           hint: "📏 đo độ dài",             word: "THUOC"},
  {name: "Thư viện",          hint: "🏫 nơi bạn học mỗi ngày",  word: "LOPHOC"},
  {name: "Phòng tin học",     hint: "🖍️ thầy cô viết lên đây",  word: "BANGDEN"},
  {name: "Phòng hiệu trưởng", hint: "👩‍🏫 người dạy bạn",        word: "GIAOVIEN"}
];
const TIME_LIMIT = 120, MAX_WRONG = 3, MAX_HEARTS = 3, AREA = 18;
const $ = id => document.getElementById(id);

const canvas = $('c');
const renderer = new THREE.WebGLRenderer({canvas, antialias: true});
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x05060c);
scene.fog = new THREE.Fog(0x05060c, 8, 40);
const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 100);
camera.rotation.order = 'YXZ';
scene.add(camera);

function resize() {
  const w = canvas.parentElement.clientWidth, h = 600;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);
resize();

// Ánh sáng: đèn pin gắn vào camera
scene.add(new THREE.AmbientLight(0x6666aa, 0.7));
const flash = new THREE.SpotLight(0xfff2cc, 1.6, 30, Math.PI / 5, 0.4);
flash.position.set(0, 0, 0);
flash.target.position.set(0, 0, -1);
camera.add(flash);
camera.add(flash.target);

// Sàn, trần, tường
const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.MeshStandardMaterial({color: 0x3a3f55}));
floor.rotation.x = -Math.PI / 2;
scene.add(floor);
const ceil = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.MeshStandardMaterial({color: 0x20222e}));
ceil.rotation.x = Math.PI / 2;
ceil.position.y = 3.5;
scene.add(ceil);
const wallMat = new THREE.MeshStandardMaterial({color: 0x7b8294});
[[0, -20, 40, 1], [0, 20, 40, 1], [-20, 0, 1, 40], [20, 0, 1, 40]].forEach(([x, z, w, d]) => {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, 3.5, d), wallMat);
  m.position.set(x, 1.75, z);
  scene.add(m);
});

// Bàn học (có va chạm)
const desks = [];
const deskMat = new THREE.MeshStandardMaterial({color: 0x92643a});
for (let i = -2; i <= 2; i++) {
  [-12, -4, 4, 12].forEach(z => {
    const x = i * 6;
    const d = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.9, 1.2), deskMat);
    d.position.set(x, 0.45, z);
    scene.add(d);
    desks.push({x, z, hx: 1.1, hz: 0.6});
  });
}

// Quái vật Verity
const monster = new THREE.Group();
const mBody = new THREE.Mesh(new THREE.BoxGeometry(1.3, 2.2, 1.1), new THREE.MeshStandardMaterial({color: 0xb91c1c, emissive: 0x550000}));
mBody.position.y = 1.1;
monster.add(mBody);
[-0.3, 0.3].forEach(x => {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.17, 12, 12), new THREE.MeshBasicMaterial({color: 0xffffff}));
  eye.position.set(x, 1.7, 0.55);
  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), new THREE.MeshBasicMaterial({color: 0x000000}));
  pupil.position.set(x, 1.7, 0.7);
  monster.add(eye, pupil);
});
const mLight = new THREE.PointLight(0xff0000, 1.4, 12);
mLight.position.y = 1.6;
monster.add(mLight);
scene.add(monster);

// Mảnh ghép (chữ cái) có cột sáng để dễ thấy từ xa
let pickups = [];
function letterMesh(ch) {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const g = c.getContext('2d');
  g.fillStyle = '#facc15'; g.fillRect(0, 0, 128, 128);
  g.fillStyle = '#1f2937'; g.font = 'bold 90px sans-serif';
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(ch, 64, 70);
  const mat = new THREE.MeshStandardMaterial({map: new THREE.CanvasTexture(c), emissive: 0x887700});
  const m = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.8, 0.8), mat);
  m.position.y = 1.2;
  const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 3.5, 8),
    new THREE.MeshBasicMaterial({color: 0xfacc15, transparent: true, opacity: 0.35}));
  beam.position.y = 1.2;
  const grp = new THREE.Group();
  grp.add(m, beam);
  grp.userData.cube = m;
  return grp;
}

// Trạng thái
const P = {x: 0, z: 0, yaw: 0, pitch: 0};
let level = 0, hearts = MAX_HEARTS, wrong = 0, timeLeft = TIME_LIMIT;
let collected = [], state = 'play', freeze = 0, started = false, panelOpen = false;
const keys = {};

function toast(msg) {
  $('toast').textContent = msg;
  setTimeout(() => { if ($('toast').textContent === msg) $('toast').textContent = ''; }, 2800);
}

function startLevel() {
  pickups.forEach(p => scene.remove(p));
  pickups = [];
  collected = [];
  wrong = 0;
  timeLeft = TIME_LIMIT;
  state = 'play';
  panelOpen = false;
  freeze = 2.5;
  P.x = 0; P.z = 0; P.yaw = 0; P.pitch = 0;
  const a = Math.random() * Math.PI * 2;
  monster.position.set(Math.cos(a) * 16, 0, Math.sin(a) * 16);
  LEVELS[level].word.split('').forEach(ch => {
    const m = letterMesh(ch);
    m.userData.ch = ch;
    let x, z, bad;
    do {
      x = (Math.random() * 2 - 1) * (AREA - 1);
      z = (Math.random() * 2 - 1) * (AREA - 1);
      bad = Math.hypot(x, z) < 5 || desks.some(d => Math.abs(x - d.x) < d.hx + 0.8 && Math.abs(z - d.z) < d.hz + 0.8);
    } while (bad);
    m.position.x = x;
    m.position.z = z;
    scene.add(m);
    pickups.push(m);
  });
  $('panel').style.display = 'none';
}

function newGame() {
  level = 0;
  hearts = MAX_HEARTS;
  $('end').style.display = 'none';
  startLevel();
}

function loseHeart(reason) {
  hearts--;
  if (hearts <= 0) {
    toast('💀 Verity bắt được bạn! Quay lại màn 1.');
    level = 0;
    hearts = MAX_HEARTS;
  } else {
    toast('💔 ' + reason + ' Mất 1 tim.');
  }
  startLevel();
}

function norm(s) {
  return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/đ/gi, 'd').replace(/\\s+/g, '').toUpperCase();
}

function submit() {
  const guess = norm($('inp').value);
  $('inp').value = '';
  if (guess === LEVELS[level].word) {
    level++;
    if (level >= LEVELS.length) {
      state = 'end';
      $('panel').style.display = 'none';
      $('end').style.display = 'block';
    } else {
      toast('✅ Đúng rồi! Bạn thoát khỏi Verity, qua màn ' + (level + 1) + ' (bấm vào màn hình để chơi tiếp)');
      startLevel();
    }
  } else {
    wrong++;
    if (wrong > MAX_WRONG) loseHeart('Sai quá 3 lần!');
    else toast('❌ Sai rồi! (' + wrong + '/' + MAX_WRONG + ' lần sai)');
  }
}
$('ok').onclick = submit;
$('inp').addEventListener('keydown', e => { if (e.key === 'Enter') submit(); e.stopPropagation(); });
$('again').onclick = () => { newGame(); lockMouse(); };

// Điều khiển
function lockMouse() {
  canvas.focus();
  try { canvas.requestPointerLock(); } catch (e) {}
}
$('start').onclick = () => { started = true; $('start').style.display = 'none'; lockMouse(); };
canvas.addEventListener('click', () => { if (started && !panelOpen) lockMouse(); });

window.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  keys[e.key.toLowerCase()] = true;
  if (e.key.startsWith('Arrow') || e.key === ' ') e.preventDefault();
});
window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

let dragging = false;
canvas.addEventListener('mousedown', () => { dragging = true; });
window.addEventListener('mouseup', () => { dragging = false; });
window.addEventListener('mousemove', e => {
  const locked = document.pointerLockElement === canvas;
  if (locked || dragging) {
    P.yaw -= e.movementX * 0.0025;
    P.pitch = Math.max(-1.2, Math.min(1.2, P.pitch - e.movementY * 0.0025));
  }
});

function blocked(x, z) {
  return desks.some(d => Math.abs(x - d.x) < d.hx + 0.3 && Math.abs(z - d.z) < d.hz + 0.3);
}

function updateHud() {
  const L = LEVELS[level];
  $('hud').innerHTML =
    'Màn ' + (level + 1) + '/' + LEVELS.length + ' – ' + L.name +
    ' &nbsp; ' + '❤️'.repeat(hearts) + '🖤'.repeat(MAX_HEARTS - hearts) +
    ' &nbsp; ⏱️ ' + Math.max(0, Math.ceil(timeLeft)) + 's<br>' +
    'Gợi ý: ' + L.hint + '<br>' +
    'Mảnh ghép (' + collected.length + '/' + L.word.length + '): ' + collected.join(' ');
}

let last = performance.now();
function loop(now) {
  requestAnimationFrame(loop);
  const dt = Math.min((now - last) / 1000, 0.1);
  last = now;
  let danger = 0;

  if (started && state === 'play') {
    timeLeft -= dt;
    if (timeLeft <= 0) loseHeart('Hết giờ!');

    // xoay bằng phím mũi tên
    if (keys['arrowleft'] || keys['q']) P.yaw += 2 * dt;
    if (keys['arrowright'] || keys['e']) P.yaw -= 2 * dt;
    if (keys['arrowup']) P.pitch = Math.min(1.2, P.pitch + 1.5 * dt);
    if (keys['arrowdown']) P.pitch = Math.max(-1.2, P.pitch - 1.5 * dt);

    // đi theo hướng nhìn
    const fx = -Math.sin(P.yaw), fz = -Math.cos(P.yaw);
    const rx = Math.cos(P.yaw), rz = -Math.sin(P.yaw);
    let mx = 0, mz = 0;
    if (keys['w']) { mx += fx; mz += fz; }
    if (keys['s']) { mx -= fx; mz -= fz; }
    if (keys['d']) { mx += rx; mz += rz; }
    if (keys['a']) { mx -= rx; mz -= rz; }
    const len = Math.hypot(mx, mz);
    if (len > 0) {
      const nx = P.x + mx / len * 5 * dt, nz = P.z + mz / len * 5 * dt;
      if (!blocked(nx, P.z)) P.x = Math.max(-AREA, Math.min(AREA, nx));
      if (!blocked(P.x, nz)) P.z = Math.max(-AREA, Math.min(AREA, nz));
    }

    // Verity đuổi theo (đứng yên khi đang nhập từ khóa)
    freeze = Math.max(0, freeze - dt);
    const dx = P.x - monster.position.x, dz = P.z - monster.position.z;
    const dist = Math.hypot(dx, dz);
    monster.rotation.y = Math.atan2(dx, dz);
    danger = Math.max(0, 1 - dist / 9);
    if (freeze <= 0 && !panelOpen && dist > 0.01) {
      const sp = 2.0 + 0.45 * level;
      monster.position.x += dx / dist * sp * dt;
      monster.position.z += dz / dist * sp * dt;
    }
    if (freeze <= 0 && dist < 1.4) loseHeart('Verity bắt được bạn!');

    // nhặt mảnh ghép
    for (let i = pickups.length - 1; i >= 0; i--) {
      const p = pickups[i];
      p.userData.cube.rotation.y += dt * 2;
      if (Math.hypot(p.position.x - P.x, p.position.z - P.z) < 1.3) {
        collected.push(p.userData.ch);
        scene.remove(p);
        pickups.splice(i, 1);
        if (pickups.length === 0) {
          panelOpen = true;
          if (document.exitPointerLock) document.exitPointerLock();
          $('ptext').textContent = 'Ghép các mảnh ' + collected.join(' ') + ' thành từ khóa (' + LEVELS[level].word.length + ' ô):';
          $('panel').style.display = 'block';
          $('inp').focus();
        }
      }
    }
  }

  $('vig').style.opacity = danger;
  camera.position.set(P.x, 1.6, P.z);
  camera.rotation.set(P.pitch, P.yaw, 0);
  updateHud();
  renderer.render(scene, camera);
}

newGame();
requestAnimationFrame(loop);
</script>
"""

components.html(GAME_HTML, height=620)
