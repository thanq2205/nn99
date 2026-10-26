import streamlit as st

st.set_page_config(
    page_title="School Escape 3D",
    page_icon="🏃‍♂️",
    layout="wide",
)

# Ẩn giao diện mặc định của Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0rem;}
    </style>
""", unsafe_allow_html=True)

# Tách nội dung HTML/JS thành các phần hoặc đọc trực tiếp an toàn
GAME_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>School Escape 3D</title>
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: monospace; user-select: none; }
        #ui { position: absolute; top: 10px; left: 10px; color: white; font-size: 18px; text-shadow: 2px 2px 4px #000; pointer-events: none; }
        #crosshair { position: absolute; top: 50%; left: 50%; width: 10px; height: 10px; transform: translate(-50%, -50%); border: 2px solid rgba(255,255,255,0.7); border-radius: 50%; pointer-events: none; }
        #instruction { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.85); color: white; padding: 25px; text-align: center; border-radius: 10px; border: 2px solid #fff; cursor: pointer; }
        #gameover, #win { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: none; flex-direction: column; justify-content: center; align-items: center; font-size: 32px; z-index: 10; color: white; }
        #gameover { background: rgba(100,0,0,0.9); }
        #win { background: rgba(0,100,0,0.9); }
        .btn { padding: 10px 20px; background: #ff4757; color: white; border: none; font-size: 20px; border-radius: 5px; cursor: pointer; margin-top: 15px; font-weight: bold; }
        .btn:hover { background: #ff6b81; }
    </style>
</head>
<body>
    <div id="ui">Chìa khóa: <span id="keysCount">0</span>/3</div>
    <div id="crosshair"></div>
    <div id="instruction">
        <h2>TRƯỜNG HỌC KINH DỊ 3D</h2>
        <p><b>W, A, S, D</b> để di chuyển | <b>Chuột</b> để nhìn xung quanh</p>
        <p style="color: #ff4757;"><b>Click vào đây để bắt đầu chơi!</b></p>
    </div>
    <div id="gameover">
        <h1>BẠN ĐÃ BỊ BẮT!</h1>
        <button class="btn" onclick="location.reload()">Chơi Lại</button>
    </div>
    <div id="win">
        <h1>CHIẾN THẮNG!</h1>
        <button class="btn" onclick="location.reload()">Chơi Lại</button>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer;
        let moveF = false, moveB = false, moveL = false, moveR = false;
        let prevTime = performance.now();
        let velocity = new THREE.Vector3();
        let direction = new THREE.Vector3();
        let keysCollected = 0, keyObjects = [], monster;
        let isOver = false, isWon = false;

        const blocker = document.getElementById('instruction');
        blocker.addEventListener('click', () => document.body.requestPointerLock());

        document.addEventListener('pointerlockchange', () => {
            if (document.pointerLockElement === document.body) {
                blocker.style.display = 'none';
            } else if (!isOver && !isWon) {
                blocker.style.display = 'block';
            }
        });

        document.addEventListener('mousemove', (e) => {
            if (document.pointerLockElement !== document.body) return;
            camera.rotation.y -= (e.movementX || 0) * 0.002;
        });

        window.addEventListener('keydown', (e) => {
            if (e.code === 'KeyW') moveF = true;
            if (e.code === 'KeyS') moveB = true;
            if (e.code === 'KeyA') moveL = true;
            if (e.code === 'KeyD') moveR = true;
        });
        window.addEventListener('keyup', (e) => {
            if (e.code === 'KeyW') moveF = false;
            if (e.code === 'KeyS') moveB = false;
            if (e.code === 'KeyA') moveL = false;
            if (e.code === 'KeyD') moveR = false;
        });

        init();
        animate();

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x050505);
            scene.fog = new THREE.FogExp2(0x050505, 0.08);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 5);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0x222233));
            let light = new THREE.PointLight(0xffaa44, 1.5, 15);
            camera.add(light);
            scene.add(camera);

            // Tạo môi trường trường học đơn giản
            let floor = new THREE.Mesh(new THREE.PlaneGeometry(50, 50), new THREE.MeshStandardMaterial({color: 0x111}));
            floor.rotation.x = -Math.PI/2;
            scene.add(floor);

            let wallMat = new THREE.MeshStandardMaterial({color: 0x444857});
            [
              [50, 4, 1, 0, 2, -25], [50, 4, 1, 0, 2, 25],
              [1, 4, 50, -25, 2, 0], [1, 4, 50, 25, 2, 0]
            ].forEach(w => {
                let mesh = new THREE.Mesh(new THREE.BoxGeometry(w[0], w[1], w[2]), wallMat);
                mesh.position.set(w[3], w[4], w[5]);
                scene.add(mesh);
            });

            // Quái vật
            monster = new THREE.Mesh(new THREE.BoxGeometry(1, 2, 1), new THREE.MeshStandardMaterial({color: 0xff0000, emissive: 0x400}));
            monster.position.set(15, 1, 15);
            scene.add(monster);

            // Chìa khóa
            [[-20, -20], [20, -20], [-20, 20]].forEach(p => {
                let k = new THREE.Mesh(new THREE.OctahedronGeometry(0.5), new THREE.MeshStandardMaterial({color: 0xffd700, emissive: 0x55400}));
                k.position.set(p[0], 1, p[1]);
                scene.add(k);
                keyObjects.push(k);
            });

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        }

        function animate() {
            requestAnimationFrame(animate);
            if (isOver || isWon) return;

            let time = performance.now();
            let delta = (time - prevTime) / 1000;

            velocity.x -= velocity.x * 10.0 * delta;
            velocity.z -= velocity.z * 10.0 * delta;

            direction.z = Number(moveF) - Number(moveB);
            direction.x = Number(moveR) - Number(moveL);
            direction.normalize();

            if (moveF || moveB) velocity.z -= direction.z * 35.0 * delta;
            if (moveL || moveR) velocity.x -= direction.x * 35.0 * delta;

            camera.translateX(-velocity.x * delta);
            camera.translateZ(-velocity.z * delta);
            camera.position.x = Math.max(-23, Math.min(23, camera.position.x));
            camera.position.z = Math.max(-23, Math.min(23, camera.position.z));

            // Quái vật đuổi theo
            let mDir = new THREE.Vector3().subVectors(camera.position, monster.position);
            mDir.y = 0;
            mDir.normalize();
            monster.position.add
