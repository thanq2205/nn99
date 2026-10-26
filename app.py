import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Verity Escape 3D", page_icon="👾", layout="wide")
st.title("👾 Verity Escape 3D")
st.caption("Bấm vào khung game trước, rồi dùng W A S D hoặc phím mũi tên để di chuyển.")

GAME_HTML = """
<div id="wrap" style="position:relative;width:100%;height:600px;font-family:sans-serif;color:#fff;overflow:hidden;border-radius:12px;background:#10131f">
  <canvas id="c" style="width:100%;height:600px;display:block;outline:none" tabindex="0"></canvas>
  <div id="hud" style="position:absolute;top:8px;left:12px;right:12px;font-size:15px;line-height:1.6;text-shadow:0 0 4px #000;pointer-events:none"></div>
  <div id="toast" style="position:absolute;top:110px;left:0;right:0;text-align:center;font-size:20px;font-weight:bold;text-shadow:0 0 6px #000;pointer-events:none"></div>
  <div id="panel" style="display:none;position:absolute;bottom:20px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.8);padding:14px 18px;border-radius:10px;text-align:center">
    <div id="ptext" style="margin-bottom:8px"></div>
    <input id="inp" autocomplete="off" style="padding:6px 10px;font-size:16px;border-radius:6px;border:none;text-transform:uppercase">
    <button id="ok" style="padding:6px 14px;font-size:16px;border-radius:6px;border:none;background:#22c55e;color:#fff;cursor:pointer">Mở khóa 🔓</button>
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

const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({canvas, antialias: true});
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x10131f);
scene.fog = new THREE.Fog(0x10131f, 15, 45);
const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);

function resize() {
  const w = canvas.parentElement.clientWidth, h = 600;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);
resize();

scene.add(new THREE.AmbientLight(0x9999bb, 0.9));
const sun = new THREE.DirectionalLight(0xffffff, 0.6);
sun.position.set(10, 20, 10);
scene.add(sun);

// Sàn và tường
const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 40),
  new THREE.MeshStandardMaterial({color: 0x3a3f55}));
floor.rotation.x = -Math.PI / 2;
scene.add(floor);
scene.add(new THREE.GridHelper(40, 40, 0x555a75, 0x444964));
const wallMat = new THREE.MeshStandardMaterial({color: 0x6b7280});
[[0, -20, 40, 1], [0, 20, 40, 1], [-20, 0, 1, 40], [20, 0, 1, 40]].forEach(([x, z, w, d]) => {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, 3, d), wallMat);
  m.position.set(x, 1.5, z);
  scene.add(m);
});

// Bàn học trang trí
const deskMat = new THREE.MeshStandardMaterial({color: 0x92643a});
for (let i = -2; i <= 2; i++) {
  [-12, 12].forEach(z => {
    const d = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.8, 1.2), deskMat);
    d.position.set(i * 6, 0.4, z);
    scene.add(d);
  });
}

// Nhân vật học sinh
const player = new THREE.Group();
const pBody = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.2, 0.5), new THREE.MeshStandardMaterial({color: 0x3b82f6}));
pBody.position.y = 0.6;
const pHead = new THREE.Mesh(new THREE.SphereGeometry(0.32, 16, 16), new THREE.MeshStandardMaterial({color: 0xffd9b3}));
pHead.position.y = 1.5;
player.add(pBody, pHead);
scene.add(player);

// Quái vật Verity
const monster = new THREE.Group();
const mBody = new THREE.Mesh(new THREE.BoxGeometry(1.3, 2, 1.1), new THREE.MeshStandardMaterial({color: 0xb91c1c, emissive: 0x440000}));
mBody.position.y = 1;
monster.add(mBody);
[-0.3, 0.3].forEach(x => {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.17, 12, 12), new THREE.MeshBasicMaterial({color: 0xffffff}));
  eye.position.set(x, 1.5, 0.55);
  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), new THREE.MeshBasicMaterial({color: 0x000000}));
  pupil.position.set(x, 1.5, 0.7);
  monster.add(eye, pupil);
});
const mLight = new THREE.PointLight(0xff0000, 1.2, 10);
mLight.position.y = 1.5;
monster.add(mLight);
scene.add(monster);

// Mảnh ghép (chữ cái)
let pickups = [];
function letterMesh(ch) {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const g = c.getContext('2d');
  g.fillStyle = '#facc15'; g.fillRect(0, 0, 128, 128);
  g.fillStyle = '#1f2937'; g.font = 'bold 90px sans-serif';
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(ch, 64, 70);
  const mat = new THREE.MeshStandardMaterial({map: new THREE.CanvasTexture(c), emissive: 0x665500});
  const m = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.9, 0.9), mat);
  m.position.y = 0.9;
  return m;
}

// Trạng thái game
let level = 0, hearts = MAX_HEARTS, wrong = 0, timeLeft = TIME_LIMIT;
let collected = [], state = 'play', freeze = 0;
const keys = {};

const $ = id => document.getElementById(id);
function toast(msg) {
  $('toast').textContent = msg;
  setTimeout(() => { if ($('toast').textContent === msg) $('toast').textContent = ''; }, 2500);
}

function startLevel() {
  pickups.forEach(p => scene.remove(p));
  pickups = [];
  collected = [];
  wrong = 0;
  timeLeft = TIME_LIMIT;
  state = 'play';
  freeze = 2;
  player.position.set(0, 0, 0);
  const a = Math.random() * Math.PI * 2;
  monster.position.set(Math.cos(a) * 16, 0, Math.sin(a) * 16);
  LEVELS[level].word.split('').forEach(ch => {
    const m = letterMesh(ch);
    m.userData.ch = ch;
    let x, z;
    do {
      x = (Math.random() * 2 - 1) * AREA;
      z = (Math.random() * 2 - 1) * AREA;
    } while (Math.hypot(x, z) < 5);
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
      toast('✅ Đúng rồi! Bạn thoát khỏi Verity, qua màn ' + (level + 1));
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
$('again').onclick = newGame;

window.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  keys[e.key.toLowerCase()] = true;
  if (e.key.startsWith('Arrow')) e.preventDefault();
});
window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });
canvas.addEventListener('click', () => canvas.focus());

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

  if (state === 'play') {
    timeLeft -= dt;
    if (timeLeft <= 0) { loseHeart('Hết giờ!'); }

    // di chuyển người chơi
    let dx = 0, dz = 0;
    if (keys['w'] || keys['arrowup']) dz -= 1;
    if (keys['s'] || keys['arrowdown']) dz += 1;
    if (keys['a'] || keys['arrowleft']) dx -= 1;
    if (keys['d'] || keys['arrowright']) dx += 1;
    if (dx || dz) {
      const len = Math.hypot(dx, dz);
      player.position.x = Math.max(-AREA, Math.min(AREA, player.position.x + dx / len * 6 * dt));
      player.position.z = Math.max(-AREA, Math.min(AREA, player.position.z + dz / len * 6 * dt));
      player.rotation.y = Math.atan2(dx, dz);
    }

    // Verity đuổi theo, càng lên màn cao càng nhanh
    freeze = Math.max(0, freeze - dt);
    const mx = player.position.x - monster.position.x;
    const mz = player.position.z - monster.position.z;
    const dist = Math.hypot(mx, mz);
    monster.rotation.y = Math.atan2(mx, mz);
    if (freeze <= 0 && dist > 0.01) {
      const sp = 2.0 + 0.45 * level;
      monster.position.x += mx / dist * sp * dt;
      monster.position.z += mz / dist * sp * dt;
    }
    if (freeze <= 0 && dist < 1.3) loseHeart('Verity bắt được bạn!');

    // nhặt mảnh ghép
    for (let i = pickups.length - 1; i >= 0; i--) {
      const p = pickups[i];
      p.rotation.y += dt * 2;
      if (Math.hypot(p.position.x - player.position.x, p.position.z - player.position.z) < 1.2) {
        collected.push(p.userData.ch);
        scene.remove(p);
        pickups.splice(i, 1);
        if (pickups.length === 0) {
          $('ptext').textContent = 'Ghép các mảnh ' + collected.join(' ') + ' thành từ khóa (' + LEVELS[level].word.length + ' ô):';
          $('panel').style.display = 'block';
          $('inp').focus();
        }
      }
    }
  }

  // camera bám theo người chơi
  const target = new THREE.Vector3(player.position.x, 0, player.position.z);
  camera.position.lerp(new THREE.Vector3(target.x, 11, target.z + 11), 0.1);
  camera.lookAt(target);
  updateHud();
  renderer.render(scene, camera);
}

newGame();
requestAnimationFrame(loop);
</script>
"""

components.html(GAME_HTML, height=620)
