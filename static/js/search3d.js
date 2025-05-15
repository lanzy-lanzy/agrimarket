// AgriMarket 3D Search Animation with Three.js
let searchScene, searchCamera, searchRenderer;
let searchControls;
let searchAnimationId;
let searchCanvas;
let searchParticles = [];
let searchTime = 0;
let searchLight;
let searchInitialized = false;

// Colors from the AgriMarket theme
const searchColors = {
    cream: 0xFFF0D1,
    brown: 0x795757,
    darkBrown: 0x664343,
    darkerBrown: 0x3B3030,
    skyBlue: 0x87CEEB,
    grassGreen: 0x7CFC00,
    sunnyYellow: 0xFFD700
};

// Initialize the 3D search scene
function initSearchScene() {
    // Get the canvas element
    searchCanvas = document.getElementById('search-scene');
    if (!searchCanvas) return;

    // Create scene with a gradient background
    searchScene = new THREE.Scene();
    
    // Create a subtle gradient background
    const bgTexture = createGradientTexture(
        searchColors.cream, 
        searchColors.brown
    );
    searchScene.background = bgTexture;

    // Create camera
    const aspectRatio = searchCanvas.clientWidth / searchCanvas.clientHeight;
    searchCamera = new THREE.PerspectiveCamera(75, aspectRatio, 0.1, 1000);
    searchCamera.position.set(0, 0, 10);

    // Create renderer
    searchRenderer = new THREE.WebGLRenderer({
        canvas: searchCanvas,
        antialias: true,
        alpha: true
    });
    searchRenderer.setSize(searchCanvas.clientWidth, searchCanvas.clientHeight);
    searchRenderer.setPixelRatio(window.devicePixelRatio);

    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    searchScene.add(ambientLight);

    // Add directional light
    searchLight = new THREE.DirectionalLight(searchColors.cream, 1.0);
    searchLight.position.set(5, 5, 5);
    searchScene.add(searchLight);

    // Add point light for highlights
    const pointLight = new THREE.PointLight(searchColors.brown, 0.8, 20);
    pointLight.position.set(-5, 3, 5);
    searchScene.add(pointLight);

    // Create search-related 3D elements
    createSearchElements();

    // Handle window resize
    window.addEventListener('resize', onSearchWindowResize);

    // Start animation loop
    animateSearch();
    
    searchInitialized = true;
}

// Create a gradient texture for background
function createGradientTexture(colorTop, colorBottom) {
    const canvas = document.createElement('canvas');
    canvas.width = 2;
    canvas.height = 512;
    
    const context = canvas.getContext('2d');
    
    // Create gradient
    const gradient = context.createLinearGradient(0, 0, 0, 512);
    gradient.addColorStop(0, '#' + new THREE.Color(colorTop).getHexString());
    gradient.addColorStop(1, '#' + new THREE.Color(colorBottom).getHexString());
    
    context.fillStyle = gradient;
    context.fillRect(0, 0, 2, 512);
    
    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    
    return texture;
}

// Create search-related 3D elements
function createSearchElements() {
    // Create floating particles that represent search results
    createSearchParticles();
    
    // Create a magnifying glass
    createMagnifyingGlass();
    
    // Create some decorative elements
    createDecorativeElements();
}

// Create floating particles
function createSearchParticles() {
    const particleCount = 50;
    const particleGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    
    for (let i = 0; i < particleCount; i++) {
        const particleMaterial = new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(Math.random(), 0.7, 0.5),
            roughness: 0.5,
            metalness: 0.2,
            emissive: new THREE.Color().setHSL(Math.random(), 0.7, 0.3),
            emissiveIntensity: 0.3
        });
        
        const particle = new THREE.Mesh(particleGeometry, particleMaterial);
        
        // Random position in a spherical area
        const radius = 5 + Math.random() * 3;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        
        particle.position.x = radius * Math.sin(phi) * Math.cos(theta);
        particle.position.y = radius * Math.sin(phi) * Math.sin(theta);
        particle.position.z = radius * Math.cos(phi);
        
        // Store original position for animation
        particle.userData = {
            originalPosition: particle.position.clone(),
            speed: Math.random() * 0.02 + 0.01,
            amplitude: Math.random() * 0.5 + 0.5,
            phase: Math.random() * Math.PI * 2
        };
        
        searchScene.add(particle);
        searchParticles.push(particle);
    }
}

// Create a magnifying glass
function createMagnifyingGlass() {
    // Create the glass part (transparent disc)
    const glassGeometry = new THREE.CircleGeometry(1.5, 32);
    const glassMaterial = new THREE.MeshPhysicalMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0.3,
        roughness: 0.1,
        metalness: 0.1,
        clearcoat: 1.0,
        clearcoatRoughness: 0.1,
        side: THREE.DoubleSide
    });
    
    const glass = new THREE.Mesh(glassGeometry, glassMaterial);
    glass.position.set(0, 0, 0);
    searchScene.add(glass);
    
    // Create the handle
    const handleGeometry = new THREE.CylinderGeometry(0.15, 0.15, 2, 16);
    const handleMaterial = new THREE.MeshStandardMaterial({
        color: searchColors.brown,
        roughness: 0.5,
        metalness: 0.3
    });
    
    const handle = new THREE.Mesh(handleGeometry, handleMaterial);
    handle.position.set(1.2, -1.2, 0);
    handle.rotation.z = Math.PI / 4;
    searchScene.add(handle);
    
    // Create the rim
    const rimGeometry = new THREE.TorusGeometry(1.5, 0.1, 16, 100);
    const rimMaterial = new THREE.MeshStandardMaterial({
        color: searchColors.brown,
        roughness: 0.3,
        metalness: 0.7
    });
    
    const rim = new THREE.Mesh(rimGeometry, rimMaterial);
    rim.position.set(0, 0, 0);
    searchScene.add(rim);
}

// Create decorative elements
function createDecorativeElements() {
    // Add some farm-themed icons floating in the background
    const iconGeometries = [
        new THREE.BoxGeometry(0.5, 0.3, 0.2), // Cow shape (simplified)
        new THREE.SphereGeometry(0.3, 8, 8),  // Chicken shape (simplified)
        new THREE.ConeGeometry(0.3, 0.6, 4)   // Farm shape (simplified)
    ];
    
    for (let i = 0; i < 15; i++) {
        const geometry = iconGeometries[Math.floor(Math.random() * iconGeometries.length)];
        const material = new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(Math.random() * 0.1 + 0.05, 0.7, 0.5),
            roughness: 0.7,
            metalness: 0.2
        });
        
        const icon = new THREE.Mesh(geometry, material);
        
        // Position far in the background
        const radius = 8 + Math.random() * 4;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        
        icon.position.x = radius * Math.sin(phi) * Math.cos(theta);
        icon.position.y = radius * Math.sin(phi) * Math.sin(theta);
        icon.position.z = -radius * Math.cos(phi);
        
        // Random rotation
        icon.rotation.x = Math.random() * Math.PI * 2;
        icon.rotation.y = Math.random() * Math.PI * 2;
        icon.rotation.z = Math.random() * Math.PI * 2;
        
        // Store animation data
        icon.userData = {
            rotationSpeed: Math.random() * 0.01,
            floatSpeed: Math.random() * 0.005 + 0.002,
            floatAmplitude: Math.random() * 0.2 + 0.1,
            originalPosition: icon.position.clone(),
            phase: Math.random() * Math.PI * 2
        };
        
        searchScene.add(icon);
    }
}

// Handle window resize
function onSearchWindowResize() {
    if (!searchCanvas) return;
    
    const width = searchCanvas.clientWidth;
    const height = searchCanvas.clientHeight;
    
    searchCamera.aspect = width / height;
    searchCamera.updateProjectionMatrix();
    searchRenderer.setSize(width, height);
}

// Animation loop for search scene
function animateSearch() {
    searchAnimationId = requestAnimationFrame(animateSearch);
    
    // Update time
    searchTime += 0.01;
    
    // Animate particles
    searchParticles.forEach((particle, index) => {
        const userData = particle.userData;
        
        // Oscillate around original position
        particle.position.x = userData.originalPosition.x + Math.sin(searchTime * userData.speed + userData.phase) * userData.amplitude;
        particle.position.y = userData.originalPosition.y + Math.cos(searchTime * userData.speed + userData.phase) * userData.amplitude;
        particle.position.z = userData.originalPosition.z + Math.sin(searchTime * userData.speed * 0.5 + userData.phase) * userData.amplitude * 0.5;
        
        // Slowly rotate
        particle.rotation.x += 0.01;
        particle.rotation.y += 0.01;
    });
    
    // Animate decorative elements
    searchScene.children.forEach(child => {
        if (child.userData && child.userData.rotationSpeed) {
            // Rotate the object
            child.rotation.x += child.userData.rotationSpeed;
            child.rotation.y += child.userData.rotationSpeed * 0.7;
            
            // Float up and down
            if (child.userData.originalPosition) {
                child.position.y = child.userData.originalPosition.y + 
                    Math.sin(searchTime * child.userData.floatSpeed + child.userData.phase) * 
                    child.userData.floatAmplitude;
            }
        }
    });
    
    // Render scene
    searchRenderer.render(searchScene, searchCamera);
}

// Clean up resources
function cleanUpSearchScene() {
    if (searchAnimationId) {
        cancelAnimationFrame(searchAnimationId);
    }
    
    // Remove event listeners
    window.removeEventListener('resize', onSearchWindowResize);
    
    // Clear scene
    if (searchScene) {
        while (searchScene.children.length > 0) {
            const object = searchScene.children[0];
            searchScene.remove(object);
        }
    }
    
    // Dispose of renderer
    if (searchRenderer) {
        searchRenderer.dispose();
    }
    
    searchParticles = [];
}

// Initialize the search functionality
function initSearchFunctionality() {
    const searchInput = document.getElementById('featured-search');
    const itemsContainer = document.getElementById('featured-items-container');
    const noResultsMessage = document.getElementById('no-results-message');
    
    if (!searchInput || !itemsContainer) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        const items = itemsContainer.querySelectorAll('.featured-item');
        let matchCount = 0;
        
        items.forEach(item => {
            const name = item.dataset.name || '';
            const category = item.dataset.category || '';
            const description = item.dataset.description || '';
            const seller = item.dataset.seller || '';
            
            // Check if any field contains the search term
            const matches = 
                name.includes(searchTerm) || 
                category.includes(searchTerm) || 
                description.includes(searchTerm) ||
                seller.includes(searchTerm);
            
            if (matches) {
                item.classList.remove('hidden');
                matchCount++;
                
                // Add a subtle highlight animation
                item.classList.add('search-match');
                setTimeout(() => {
                    item.classList.remove('search-match');
                }, 1000);
            } else {
                item.classList.add('hidden');
            }
        });
        
        // Show/hide no results message
        if (matchCount === 0 && searchTerm !== '') {
            noResultsMessage.classList.remove('hidden');
        } else {
            noResultsMessage.classList.add('hidden');
        }
        
        // Trigger animation effect in the 3D scene
        triggerSearchAnimation(searchTerm);
    });
}

// Trigger a visual effect in the 3D scene when searching
function triggerSearchAnimation(searchTerm) {
    if (!searchScene) return;
    
    // Pulse the particles based on search term length
    const pulseIntensity = searchTerm.length > 0 ? 0.1 + (searchTerm.length * 0.05) : 0;
    
    // Animate particles to show search activity
    searchParticles.forEach(particle => {
        // Scale particles based on search intensity
        const scale = 1 + pulseIntensity;
        particle.scale.set(scale, scale, scale);
        
        // Change color intensity based on search
        if (particle.material) {
            if (searchTerm.length > 0) {
                particle.material.emissiveIntensity = 0.5 + (searchTerm.length * 0.1);
            } else {
                particle.material.emissiveIntensity = 0.3;
            }
        }
    });
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page with the search scene
    if (document.getElementById('search-scene')) {
        initSearchScene();
        initSearchFunctionality();
    }
});

// Clean up when navigating away
window.addEventListener('beforeunload', function() {
    if (searchInitialized) {
        cleanUpSearchScene();
    }
});
