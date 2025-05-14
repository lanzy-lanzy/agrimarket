// AgriMarket 3D Animation with Three.js
let scene, camera, renderer, controls;
let farmScene = {};
let animationId;
let canvas;
let clouds = [];
let sunLight;
let time = 0;

// Colors from the AgriMarket theme
const colors = {
    cream: 0xFFF0D1,
    brown: 0x795757,
    darkBrown: 0x664343,
    darkerBrown: 0x3B3030,
    skyBlue: 0x87CEEB,
    grassGreen: 0x7CFC00,
    sunnyYellow: 0xFFD700
};

// Initialize the 3D scene
function init() {
    // Get the canvas element
    canvas = document.getElementById('farm-scene');
    if (!canvas) return;

    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(colors.skyBlue);
    scene.fog = new THREE.FogExp2(0xE6F7FF, 0.01);

    // Create camera
    const aspectRatio = canvas.clientWidth / canvas.clientHeight;
    camera = new THREE.PerspectiveCamera(75, aspectRatio, 0.1, 1000);
    camera.position.set(0, 5, 15);

    // Create renderer with better quality
    renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        alpha: true
    });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;

    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    // Add hemisphere light for better sky/ground lighting
    const hemisphereLight = new THREE.HemisphereLight(0x87CEEB, 0x7CFC00, 0.6);
    scene.add(hemisphereLight);

    // Add directional light (sunlight)
    sunLight = new THREE.DirectionalLight(colors.sunnyYellow, 1.0);
    sunLight.position.set(10, 15, 8);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 50;
    sunLight.shadow.camera.left = -20;
    sunLight.shadow.camera.right = 20;
    sunLight.shadow.camera.top = 20;
    sunLight.shadow.camera.bottom = -20;
    sunLight.shadow.bias = -0.0005;
    scene.add(sunLight);

    // Add a subtle point light for additional dimension
    const pointLight = new THREE.PointLight(0xFFFFFF, 0.5, 20);
    pointLight.position.set(0, 8, 0);
    scene.add(pointLight);

    // Add controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2;
    controls.minDistance = 5;
    controls.maxDistance = 20;

    // Create the farm scene
    createFarmScene();

    // Handle window resize
    window.addEventListener('resize', onWindowResize);

    // Start animation loop
    animate();
}

// Create the farm scene with various elements
function createFarmScene() {
    // Create ground with texture
    const groundSize = 100;
    const groundGeometry = new THREE.PlaneGeometry(groundSize, groundSize, 32, 32);

    // Create a grass texture
    const grassTexture = createGrassTexture();

    const groundMaterial = new THREE.MeshStandardMaterial({
        color: colors.grassGreen,
        roughness: 0.8,
        metalness: 0.1,
        map: grassTexture,
        bumpMap: grassTexture,
        bumpScale: 0.1
    });

    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);
    farmScene.ground = ground;

    // Add sky with clouds
    createClouds();

    // Create water feature
    createWaterFeature();

    // Create barn
    createBarn();

    // Create fence
    createFence();

    // Add some animals (simplified shapes)
    createAnimals();

    // Add some trees
    createTrees();

    // Add some flowers
    createFlowers();
}

// Create a procedural grass texture
function createGrassTexture() {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const context = canvas.getContext('2d');

    // Fill with base green
    context.fillStyle = '#7CFC00';
    context.fillRect(0, 0, canvas.width, canvas.height);

    // Add some texture variation
    for (let i = 0; i < 5000; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const size = Math.random() * 3 + 1;
        const hue = 80 + Math.random() * 40; // Green hues
        const lightness = 40 + Math.random() * 30;

        context.fillStyle = `hsl(${hue}, 80%, ${lightness}%)`;
        context.beginPath();
        context.arc(x, y, size, 0, Math.PI * 2);
        context.fill();
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(10, 10);

    return texture;
}

// Create clouds in the sky
function createClouds() {
    for (let i = 0; i < 20; i++) {
        const cloudGroup = new THREE.Group();

        // Create 3-5 cloud puffs per cloud
        const puffCount = Math.floor(Math.random() * 3) + 3;

        for (let j = 0; j < puffCount; j++) {
            const puffGeometry = new THREE.SphereGeometry(
                Math.random() * 2 + 1.5, // Random size
                8, 8
            );
            const puffMaterial = new THREE.MeshStandardMaterial({
                color: 0xFFFFFF,
                roughness: 0.9,
                metalness: 0.1,
                transparent: true,
                opacity: 0.9
            });

            const puff = new THREE.Mesh(puffGeometry, puffMaterial);

            // Position puffs to form a cloud shape
            puff.position.x = j * (Math.random() * 2 + 1);
            puff.position.y = Math.random() * 0.5;
            puff.position.z = Math.random() * 2 - 1;

            cloudGroup.add(puff);
        }

        // Position the cloud in the sky
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * 40 + 30;
        const height = Math.random() * 15 + 20;

        cloudGroup.position.set(
            Math.cos(angle) * radius,
            height,
            Math.sin(angle) * radius
        );

        // Random rotation
        cloudGroup.rotation.y = Math.random() * Math.PI * 2;

        // Add to scene and store reference
        scene.add(cloudGroup);
        clouds.push({
            mesh: cloudGroup,
            speed: Math.random() * 0.02 + 0.01,
            rotationSpeed: Math.random() * 0.001,
            initialAngle: angle
        });
    }
}

// Create a small water feature
function createWaterFeature() {
    // Create a small pond
    const pondGeometry = new THREE.CircleGeometry(5, 32);
    const pondMaterial = new THREE.MeshStandardMaterial({
        color: 0x4B9CD3,
        roughness: 0.1,
        metalness: 0.8,
        transparent: true,
        opacity: 0.8
    });

    const pond = new THREE.Mesh(pondGeometry, pondMaterial);
    pond.rotation.x = -Math.PI / 2;
    pond.position.set(8, 0.05, 8);
    pond.receiveShadow = true;
    scene.add(pond);
    farmScene.pond = pond;

    // Add a stone border around the pond
    const stoneBorder = new THREE.Group();
    const stoneCount = 20;

    for (let i = 0; i < stoneCount; i++) {
        const angle = (i / stoneCount) * Math.PI * 2;
        const radius = 5.2 + Math.random() * 0.3;

        const stoneGeometry = new THREE.SphereGeometry(
            Math.random() * 0.3 + 0.2,
            6, 6
        );
        const stoneMaterial = new THREE.MeshStandardMaterial({
            color: 0x888888,
            roughness: 0.9,
            metalness: 0.1
        });

        const stone = new THREE.Mesh(stoneGeometry, stoneMaterial);
        stone.position.set(
            8 + Math.cos(angle) * radius,
            Math.random() * 0.1 + 0.1,
            8 + Math.sin(angle) * radius
        );
        stone.scale.y = 0.5;
        stone.castShadow = true;
        stone.receiveShadow = true;

        stoneBorder.add(stone);
    }

    scene.add(stoneBorder);
    farmScene.stoneBorder = stoneBorder;
}

// Create a simple barn
function createBarn() {
    // Barn body
    const barnGeometry = new THREE.BoxGeometry(5, 4, 6);
    const barnMaterial = new THREE.MeshStandardMaterial({ color: colors.brown });
    const barn = new THREE.Mesh(barnGeometry, barnMaterial);
    barn.position.set(-5, 2, -5);
    barn.castShadow = true;
    barn.receiveShadow = true;
    scene.add(barn);
    farmScene.barn = barn;

    // Barn roof
    const roofGeometry = new THREE.ConeGeometry(4, 2, 4);
    const roofMaterial = new THREE.MeshStandardMaterial({ color: colors.darkerBrown });
    const roof = new THREE.Mesh(roofGeometry, roofMaterial);
    roof.position.set(-5, 5, -5);
    roof.castShadow = true;
    scene.add(roof);
    farmScene.roof = roof;
}

// Create a fence around the farm
function createFence() {
    const fencePosts = [];
    const fenceSegments = [];

    // Create fence posts and segments in a square
    const fenceSize = 15;
    const postCount = 20;
    const postSpacing = (fenceSize * 2) / postCount;

    for (let i = 0; i < postCount + 1; i++) {
        // Front fence
        createFencePost(-fenceSize + i * postSpacing, 0, fenceSize, fencePosts);
        if (i < postCount) {
            createFenceSegment(
                -fenceSize + i * postSpacing, 0, fenceSize,
                -fenceSize + (i + 1) * postSpacing, 0, fenceSize,
                fenceSegments
            );
        }

        // Back fence
        createFencePost(-fenceSize + i * postSpacing, 0, -fenceSize, fencePosts);
        if (i < postCount) {
            createFenceSegment(
                -fenceSize + i * postSpacing, 0, -fenceSize,
                -fenceSize + (i + 1) * postSpacing, 0, -fenceSize,
                fenceSegments
            );
        }
    }

    // Side fences
    for (let i = 1; i < postCount; i++) {
        // Left fence
        createFencePost(-fenceSize, 0, fenceSize - i * postSpacing, fencePosts);
        createFenceSegment(
            -fenceSize, 0, fenceSize - (i - 1) * postSpacing,
            -fenceSize, 0, fenceSize - i * postSpacing,
            fenceSegments
        );

        // Right fence
        createFencePost(fenceSize, 0, fenceSize - i * postSpacing, fencePosts);
        createFenceSegment(
            fenceSize, 0, fenceSize - (i - 1) * postSpacing,
            fenceSize, 0, fenceSize - i * postSpacing,
            fenceSegments
        );
    }

    farmScene.fencePosts = fencePosts;
    farmScene.fenceSegments = fenceSegments;
}

// Create a fence post at the specified position
function createFencePost(x, y, z, postsArray) {
    const postGeometry = new THREE.CylinderGeometry(0.1, 0.1, 1.5, 8);
    const postMaterial = new THREE.MeshStandardMaterial({ color: colors.darkBrown });
    const post = new THREE.Mesh(postGeometry, postMaterial);
    post.position.set(x, 0.75, z);
    post.castShadow = true;
    scene.add(post);
    postsArray.push(post);
}

// Create a fence segment between two posts
function createFenceSegment(x1, y1, z1, x2, y2, z2, segmentsArray) {
    const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(z2 - z1, 2));
    const segmentGeometry = new THREE.BoxGeometry(length, 0.1, 0.05);
    const segmentMaterial = new THREE.MeshStandardMaterial({ color: colors.darkBrown });
    const segment = new THREE.Mesh(segmentGeometry, segmentMaterial);

    // Position at midpoint
    segment.position.set((x1 + x2) / 2, 0.6, (z1 + z2) / 2);

    // Rotate to align with posts
    const angle = Math.atan2(z2 - z1, x2 - x1);
    segment.rotation.y = angle;

    segment.castShadow = true;
    scene.add(segment);
    segmentsArray.push(segment);

    // Add a second rail
    const segment2 = segment.clone();
    segment2.position.y = 1.0;
    scene.add(segment2);
    segmentsArray.push(segment2);
}

// Create simplified animal shapes
function createAnimals() {
    const animals = [];

    // Create some cows (simplified as boxes with legs)
    for (let i = 0; i < 5; i++) {
        const cow = createCow();
        cow.position.set(
            Math.random() * 10 - 5,
            0,
            Math.random() * 10 - 5
        );
        animals.push(cow);
    }

    // Create some chickens (simplified as small boxes)
    for (let i = 0; i < 8; i++) {
        const chicken = createChicken();
        chicken.position.set(
            Math.random() * 6 - 3 + 5,
            0,
            Math.random() * 6 - 3
        );
        animals.push(chicken);
    }

    farmScene.animals = animals;
}

// Create a simplified cow
function createCow() {
    const cowGroup = new THREE.Group();

    // Body
    const bodyGeometry = new THREE.BoxGeometry(1.5, 0.8, 0.8);
    const bodyMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFFFFF,
        roughness: 0.7
    });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 0.8;
    body.castShadow = true;
    cowGroup.add(body);

    // Head
    const headGeometry = new THREE.BoxGeometry(0.6, 0.6, 0.5);
    const head = new THREE.Mesh(headGeometry, bodyMaterial);
    head.position.set(0.9, 1.0, 0);
    head.castShadow = true;
    cowGroup.add(head);

    // Legs
    const legGeometry = new THREE.BoxGeometry(0.2, 0.6, 0.2);
    const legMaterial = new THREE.MeshStandardMaterial({ color: 0xEEEEEE });

    // Front legs
    const frontLegL = new THREE.Mesh(legGeometry, legMaterial);
    frontLegL.position.set(0.5, 0.3, 0.25);
    frontLegL.castShadow = true;
    cowGroup.add(frontLegL);

    const frontLegR = new THREE.Mesh(legGeometry, legMaterial);
    frontLegR.position.set(0.5, 0.3, -0.25);
    frontLegR.castShadow = true;
    cowGroup.add(frontLegR);

    // Back legs
    const backLegL = new THREE.Mesh(legGeometry, legMaterial);
    backLegL.position.set(-0.5, 0.3, 0.25);
    backLegL.castShadow = true;
    cowGroup.add(backLegL);

    const backLegR = new THREE.Mesh(legGeometry, legMaterial);
    backLegR.position.set(-0.5, 0.3, -0.25);
    backLegR.castShadow = true;
    cowGroup.add(backLegR);

    // Add some black spots
    addCowSpots(body);

    scene.add(cowGroup);
    return cowGroup;
}

// Add spots to the cow
function addCowSpots(cowBody) {
    const spotsMaterial = new THREE.MeshStandardMaterial({ color: 0x000000 });

    for (let i = 0; i < 5; i++) {
        const spotSize = Math.random() * 0.2 + 0.1;
        const spotGeometry = new THREE.CircleGeometry(spotSize, 8);
        const spot = new THREE.Mesh(spotGeometry, spotsMaterial);

        // Position on the cow's body
        const u = Math.random() * 2 - 1;
        const v = Math.random() * 2 - 1;
        const w = Math.random() * 2 - 1;

        // Determine which face to put the spot on
        const face = Math.floor(Math.random() * 6);

        switch (face) {
            case 0: // top
                spot.position.set(u * 0.75, 0.41, v * 0.4);
                spot.rotation.x = -Math.PI / 2;
                break;
            case 1: // bottom
                spot.position.set(u * 0.75, -0.41, v * 0.4);
                spot.rotation.x = Math.PI / 2;
                break;
            case 2: // front
                spot.position.set(0.76, u * 0.4, v * 0.4);
                spot.rotation.y = Math.PI / 2;
                break;
            case 3: // back
                spot.position.set(-0.76, u * 0.4, v * 0.4);
                spot.rotation.y = -Math.PI / 2;
                break;
            case 4: // left
                spot.position.set(u * 0.75, v * 0.4, 0.41);
                break;
            case 5: // right
                spot.position.set(u * 0.75, v * 0.4, -0.41);
                spot.rotation.y = Math.PI;
                break;
        }

        cowBody.add(spot);
    }
}

// Create a simplified chicken
function createChicken() {
    const chickenGroup = new THREE.Group();

    // Body
    const bodyGeometry = new THREE.SphereGeometry(0.2, 8, 8);
    const bodyMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFFFFF,
        roughness: 0.7
    });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 0.2;
    body.scale.set(1, 0.8, 1.2);
    body.castShadow = true;
    chickenGroup.add(body);

    // Head
    const headGeometry = new THREE.SphereGeometry(0.12, 8, 8);
    const headMaterial = new THREE.MeshStandardMaterial({ color: 0xFFFFFF });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.set(0.15, 0.35, 0);
    head.castShadow = true;
    chickenGroup.add(head);

    // Beak
    const beakGeometry = new THREE.ConeGeometry(0.05, 0.1, 4);
    const beakMaterial = new THREE.MeshStandardMaterial({ color: 0xFFA500 });
    const beak = new THREE.Mesh(beakGeometry, beakMaterial);
    beak.position.set(0.25, 0.35, 0);
    beak.rotation.z = -Math.PI / 2;
    beak.castShadow = true;
    chickenGroup.add(beak);

    // Legs
    const legGeometry = new THREE.CylinderGeometry(0.01, 0.01, 0.15, 4);
    const legMaterial = new THREE.MeshStandardMaterial({ color: 0xFFA500 });

    const legL = new THREE.Mesh(legGeometry, legMaterial);
    legL.position.set(0, 0.075, 0.05);
    legL.castShadow = true;
    chickenGroup.add(legL);

    const legR = new THREE.Mesh(legGeometry, legMaterial);
    legR.position.set(0, 0.075, -0.05);
    legR.castShadow = true;
    chickenGroup.add(legR);

    scene.add(chickenGroup);
    return chickenGroup;
}

// Create trees for the farm
function createTrees() {
    const trees = [];

    // Create several trees around the farm
    for (let i = 0; i < 10; i++) {
        const tree = createTree();

        // Position trees around the perimeter
        const angle = Math.random() * Math.PI * 2;
        const radius = 12 + Math.random() * 3;
        tree.position.set(
            Math.cos(angle) * radius,
            0,
            Math.sin(angle) * radius
        );

        trees.push(tree);
    }

    farmScene.trees = trees;
}

// Create a single tree
function createTree() {
    const treeGroup = new THREE.Group();

    // Trunk
    const trunkGeometry = new THREE.CylinderGeometry(0.2, 0.3, 1.5, 8);
    const trunkMaterial = new THREE.MeshStandardMaterial({
        color: 0x8B4513,
        roughness: 0.9
    });
    const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
    trunk.position.y = 0.75;
    trunk.castShadow = true;
    treeGroup.add(trunk);

    // Foliage (multiple layers)
    const foliageMaterial = new THREE.MeshStandardMaterial({
        color: 0x228B22,
        roughness: 0.8
    });

    const foliage1 = new THREE.Mesh(
        new THREE.ConeGeometry(1.2, 1.5, 8),
        foliageMaterial
    );
    foliage1.position.y = 1.5;
    foliage1.castShadow = true;
    treeGroup.add(foliage1);

    const foliage2 = new THREE.Mesh(
        new THREE.ConeGeometry(0.9, 1.2, 8),
        foliageMaterial
    );
    foliage2.position.y = 2.2;
    foliage2.castShadow = true;
    treeGroup.add(foliage2);

    const foliage3 = new THREE.Mesh(
        new THREE.ConeGeometry(0.6, 1.0, 8),
        foliageMaterial
    );
    foliage3.position.y = 2.8;
    foliage3.castShadow = true;
    treeGroup.add(foliage3);

    scene.add(treeGroup);
    return treeGroup;
}

// Handle window resize
function onWindowResize() {
    if (!canvas) return;

    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}

// Create flowers around the farm
function createFlowers() {
    const flowerGroup = new THREE.Group();
    const flowerCount = 100;

    // Define flower colors
    const flowerColors = [
        0xFF5555, // Red
        0xFFFF55, // Yellow
        0xFF55FF, // Pink
        0x5555FF, // Blue
        0xFFAA55  // Orange
    ];

    for (let i = 0; i < flowerCount; i++) {
        // Random position within the farm area
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * 20 + 5;
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;

        // Skip if too close to the pond
        const distToPond = Math.sqrt(Math.pow(x - 8, 2) + Math.pow(z - 8, 2));
        if (distToPond < 6) continue;

        // Create flower
        const flowerColor = flowerColors[Math.floor(Math.random() * flowerColors.length)];
        const flower = createFlower(flowerColor);

        // Position and add to group
        flower.position.set(x, 0, z);
        flower.rotation.y = Math.random() * Math.PI * 2;
        flowerGroup.add(flower);
    }

    scene.add(flowerGroup);
    farmScene.flowers = flowerGroup;
}

// Create a single flower
function createFlower(color) {
    const flowerGroup = new THREE.Group();

    // Stem
    const stemGeometry = new THREE.CylinderGeometry(0.05, 0.05, 0.5, 8);
    const stemMaterial = new THREE.MeshStandardMaterial({
        color: 0x00AA00,
        roughness: 0.8
    });
    const stem = new THREE.Mesh(stemGeometry, stemMaterial);
    stem.position.y = 0.25;
    stem.castShadow = true;
    flowerGroup.add(stem);

    // Petals
    const petalCount = 5 + Math.floor(Math.random() * 3);
    const petalGeometry = new THREE.CircleGeometry(0.15, 8);
    const petalMaterial = new THREE.MeshStandardMaterial({
        color: color,
        roughness: 0.7,
        side: THREE.DoubleSide
    });

    for (let i = 0; i < petalCount; i++) {
        const petal = new THREE.Mesh(petalGeometry, petalMaterial);
        const angle = (i / petalCount) * Math.PI * 2;

        petal.position.set(
            Math.cos(angle) * 0.1,
            0.5,
            Math.sin(angle) * 0.1
        );

        petal.rotation.x = Math.PI / 2;
        petal.rotation.y = angle;
        petal.rotation.z = Math.PI / 4;

        petal.castShadow = true;
        flowerGroup.add(petal);
    }

    // Center of flower
    const centerGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const centerMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFFF00,
        roughness: 0.5
    });
    const center = new THREE.Mesh(centerGeometry, centerMaterial);
    center.position.y = 0.5;
    center.castShadow = true;
    flowerGroup.add(center);

    return flowerGroup;
}

// Animation loop
function animate() {
    animationId = requestAnimationFrame(animate);

    // Update time
    time += 0.005;

    // Animate clouds
    clouds.forEach(cloud => {
        const angle = cloud.initialAngle + time * cloud.speed;
        const radius = cloud.mesh.position.length();

        cloud.mesh.position.x = Math.cos(angle) * radius;
        cloud.mesh.position.z = Math.sin(angle) * radius;
        cloud.mesh.rotation.y += cloud.rotationSpeed;
    });

    // Animate water
    if (farmScene.pond) {
        farmScene.pond.material.color.r = 0.294 + Math.sin(time * 0.5) * 0.05;
        farmScene.pond.material.color.g = 0.612 + Math.sin(time * 0.5) * 0.05;
        farmScene.pond.material.color.b = 0.824 + Math.sin(time * 0.5) * 0.05;
    }

    // Animate sunlight
    if (sunLight) {
        // Subtle movement of the sun
        const sunAngle = time * 0.1;
        sunLight.position.x = Math.cos(sunAngle) * 15;
        sunLight.position.z = Math.sin(sunAngle) * 15;
        sunLight.position.y = 15 + Math.sin(time * 0.2) * 2;

        // Update light intensity based on position
        sunLight.intensity = 0.8 + Math.sin(time * 0.2) * 0.2;
    }

    // Rotate animals slightly for simple animation
    if (farmScene.animals) {
        farmScene.animals.forEach((animal, index) => {
            animal.rotation.y = Math.sin(time + index) * 0.2;

            // Add subtle bobbing motion
            animal.position.y = Math.sin(time * 2 + index * 0.5) * 0.05;
        });
    }

    // Animate flowers
    if (farmScene.flowers) {
        farmScene.flowers.children.forEach((flower, index) => {
            // Gentle swaying motion
            flower.rotation.z = Math.sin(time * 2 + index * 0.1) * 0.05;
        });
    }

    // Update controls
    if (controls) controls.update();

    // Render scene
    renderer.render(scene, camera);
}

// Clean up resources when the scene is no longer needed
function cleanUp() {
    if (animationId) {
        cancelAnimationFrame(animationId);
    }

    if (controls) {
        controls.dispose();
    }

    // Remove event listeners
    window.removeEventListener('resize', onWindowResize);

    // Clear scene
    if (scene) {
        while (scene.children.length > 0) {
            const object = scene.children[0];
            scene.remove(object);
        }
    }

    // Dispose of renderer
    if (renderer) {
        renderer.dispose();
    }
}

// Initialize the scene when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the home page (has the farm-scene canvas)
    if (document.getElementById('farm-scene')) {
        init();
    }
});

// Clean up when navigating away
window.addEventListener('beforeunload', cleanUp);
