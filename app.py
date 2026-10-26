import streamlit as st

st.set_page_config(
    page_title="School Escape 3D - Truy Đuổi Trong Trường Học",
    page_icon="🏃‍♂️",
    layout="wide",
)

# Ẩn header/footer mặc định của Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🏫 School Escape 3D: Night Chase")
st.markdown(
    "**Nhiệm vụ:** Tìm **3 chiếc chìa khóa** màu vàng ẩn giấu trong các hành lang trường học và chạy trốn khỏi con quái vật đang truy đuổi! Tránh xa màu đỏ."
)

# Đóng gói HTML an toàn hơn
game_html = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>School Escape 3D</title>
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: monospace; user-select: none; }
        #ui {
            position: absolute; top: 10px; left: 10px; color: white;
            font-size: 18px; text-shadow: 2px 2px 4px #000; pointer-events: none;
        }
        #crosshair {
            position: absolute; top: 50%; left: 50%; width: 10px; height: 10px;
            transform: translate(-50%, -50%); border: 2px solid rgba(255,255,255,0.7);
            border-radius: 50%; pointer-events: none;
        }
        #instruction {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.8); color: white; padding: 20px; text-align: center;
            border-radius: 10px; border: 2px solid #fff; cursor: pointer;
        }
        #gameover, #win {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: none; flex-direction: column; justify-content: center; align-items: center;
            font-size: 32px; z-index: 10; color: white;
        }
        #gameover { background: rgba(100,0,0,0.85); }
        #win { background: rgba(0,100,0,0.85); }
        .btn {
            padding: 10px 20px; background: #ff4757; color: white; border: none;
            font-size: 20px; border-radius: 5px; cursor: pointer; margin-top: 15px; font-weight: bold;
        }
        .btn:hover { background: #ff6b81; }
    </style>
</head>
<body>
    <div id="ui">
        Chìa khóa đã nhặt: <span id="keysCount">0</span>/3<br>
        Trạng thái: <span id="status" style="color: yellow;">Tránh quái vật và tìm chìa khóa!</span>
    </div>
    <div id="crosshair"></div>
    
    <div id="instruction">
        <h2>TRƯỜNG HỌC BỊ NGƯỀN RỦA</h2>
        <p><b>W, A, S, D</b> để di chuyển | <b>Chuột</b> để xoay nhìn</p>
        <p>Click vào đây để bắt đầu chơi!</p>
    </div>

    <div id="gameover">
        <h1>BẠN ĐÃ BỊ BẮT!</h1>
        <p>Quái vật đã tóm được bạn trong bóng tối.</p>
        <button class="btn" onclick="location.reload()">Chơi Lại</button>
    </div>

    <div id="win">
        <h1>CHIẾN THẮNG!</h1>
        <p>Bạn đã thu thập đủ chìa khóa và trốn thoát khỏi trường học!</p>
        <button class="btn" onclick="location.reload()">Chơi Lại</button>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer;
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
        let prevTime = performance.now();
        let velocity = new THREE.Vector3();
        let direction = new THREE.Vector3();
        
        let keysCollected = 0;
        let totalKeys = 3;
        let keyObjects = [];
        let monster, monsterSpeed = 0.035;
        let isGameOver = false;
        let isGameWon = false;

        const blocker = document.getElementById('instruction');

        blocker.addEventListener('click', function () {
            document.body.requestPointerLock();
        });

        document.addEventListener('pointerlockchange', function () {
            if (document.pointerLockElement === document.body) {
                blocker.style.display = 'none';
            } else {
                if (!isGameOver && !isGameWon) blocker.style.display = 'block';
            }
        });

        document.addEventListener('mousemove', (event) => {
            if (document.pointerLockElement !== document.body) return;
            let movementX = event.movementX || event.mozMovementX || event.webkitMovementX || 0;
            camera.rotation.y -= movementX * 0.002;
        });

        window.addEventListener('keydown', (e) => {
            if (e.code === 'KeyW') moveForward = true;
            if (e.code === 'KeyS') moveBackward = true;
            if (e.code === 'KeyA') moveLeft = true;
            if (e.code === 'KeyD') moveRight = true;
        });
        window.addEventListener('keyup', (e) => {
            if (e.code === 'KeyW') moveForward = false;
            if (e.code === 'KeyS') moveBackward = false;
            if (e.code === 'KeyA') moveLeft = false;
            if (e.code === 'KeyD') moveRight = false;
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

            const ambientLight = new THREE.AmbientLight(0x222233);
            scene.add(ambientLight);

            const pointLight = new THREE.PointLight(0xffaa44, 1.5, 15);
            camera.add(pointLight);
            scene.add(camera);

            createSchoolMap();
            createMonster();
            spawnKeys();

            window.addEventListener('resize', onWindowResize);
        }

        function createSchoolMap() {
            const floorGeo = new THREE.PlaneGeometry(60, 60);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.8 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            const ceiling = new THREE.Mesh(floorGeo, floorMat);
            ceiling.rotation.x = Math.PI / 2;
            ceiling.position.y = 4;
            scene.add(ceiling);

            const wallMat = new THREE.MeshStandardMaterial({ color: 0x4a5568, roughness: 0.5 });
            const walls = [
                {w: 60, h: 4, d: 1, x: 0, y: 2, z: -30},
                {w: 60, h: 4, d: 1, x: 0, y: 2, z: 30},
                {w: 1, h: 4, d: 60, x: -30, y: 2, z: 0},
                {w: 1, h: 4, d: 60, x: 30, y: 2, z: 0},
                {w: 20, h: 4, d: 1, x: -10, y: 2, z: -10},
                {w: 20, h: 4, d: 1, x: 10, y: 2, z: -10},
                {w: 1, h: 4, d: 20, x: -15, y: 2, z: 10},
                {w: 20, h: 4, d: 1, x: 10, y: 2, z: 15},
            ];

            walls.forEach(data => {
                const wallGeo = new THREE.BoxGeometry(data.w, data.h, data.d);
                const wall = new THREE.Mesh(wallGeo, wallMat);
                wall.position.set(data.x, data.y, data.z);
                scene.add(wall);
            });
        }

        function createMonster() {
            const monsterGeo = new THREE.BoxGeometry(1, 2.2, 1);
            const monsterMat = new THREE.MeshStandardMaterial({ color: 0xff0000, emissive: 0x550000 });
            monster = new THREE.Mesh(monsterGeo, monsterMat);
            monster.position.set(20, 1.1, 20);
            scene.add(monster);
        }

        function spawnKeys() {
            const keyPositions = [{x: -25, z: -25}, {x: 25, z: -25}, {x: -25, z: 25}];
            keyPositions.forEach(pos => {
                const keyGeo = new THREE.OctahedronGeometry(0.5);
                const keyMat = new THREE.MeshStandardMaterial({ color: 0xffd700, emissive: 0xffaa00 });
                const keyMesh = new THREE.Mesh(keyGeo, keyMat);
                keyMesh.position.set(pos.x, 1, pos.z);
                scene.add(keyMesh);
                keyObjects.push(keyMesh);
            });
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function animate() {
            requestAnimationFrame(animate);
            if (isGameOver || isGameWon) return;

            const time = performance.now();
            const
