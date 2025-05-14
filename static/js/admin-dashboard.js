// Admin Dashboard JavaScript

// Initialize dashboard components
document.addEventListener('DOMContentLoaded', function() {
    initDashboardCharts();
    initDashboardAnimations();
});

// Initialize dashboard charts and visualizations
function initDashboardCharts() {
    // Check if we have the stats-overview element
    const statsOverview = document.getElementById('stats-overview');
    if (!statsOverview) return;

    // Get the stats data from the data attributes
    const totalUsers = parseInt(statsOverview.getAttribute('data-users') || '0');
    const totalSellers = parseInt(statsOverview.getAttribute('data-sellers') || '0');
    const totalBuyers = parseInt(statsOverview.getAttribute('data-buyers') || '0');
    const totalItems = parseInt(statsOverview.getAttribute('data-items') || '0');
    
    // Create a simple 3D visualization for the dashboard header
    createDashboardVisualization(totalUsers, totalSellers, totalBuyers, totalItems);
}

// Create a simple 3D visualization using Three.js
function createDashboardVisualization(users, sellers, buyers, items) {
    const container = document.getElementById('dashboard-visualization');
    if (!container) return;
    
    // Set up scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xFFF0D1);
    
    // Set up camera
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.z = 5;
    
    // Set up renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    
    // Create a group to hold all objects
    const group = new THREE.Group();
    scene.add(group);
    
    // Create objects representing stats
    // Users pyramid
    const usersGeometry = new THREE.ConeGeometry(0.8, 1.6, 4);
    const usersMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x795757,
        roughness: 0.7,
        metalness: 0.2
    });
    const usersPyramid = new THREE.Mesh(usersGeometry, usersMaterial);
    usersPyramid.position.x = -3;
    group.add(usersPyramid);
    
    // Sellers sphere
    const sellersGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const sellersMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x664343,
        roughness: 0.5,
        metalness: 0.3
    });
    const sellersSphere = new THREE.Mesh(sellersGeometry, sellersMaterial);
    sellersSphere.position.x = -1;
    group.add(sellersSphere);
    
    // Buyers torus
    const buyersGeometry = new THREE.TorusGeometry(0.5, 0.2, 16, 32);
    const buyersMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x3B3030,
        roughness: 0.6,
        metalness: 0.4
    });
    const buyersTorus = new THREE.Mesh(buyersGeometry, buyersMaterial);
    buyersTorus.position.x = 1;
    group.add(buyersTorus);
    
    // Items cylinder
    const itemsGeometry = new THREE.CylinderGeometry(0.5, 0.5, 1, 32);
    const itemsMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x795757,
        roughness: 0.4,
        metalness: 0.5
    });
    const itemsCylinder = new THREE.Mesh(itemsGeometry, itemsMaterial);
    itemsCylinder.position.x = 3;
    group.add(itemsCylinder);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Scale objects based on data
    const maxValue = Math.max(users, sellers, buyers, items);
    const scaleFactor = 1 / Math.max(1, maxValue / 100);
    
    usersPyramid.scale.y = Math.max(0.2, users * scaleFactor);
    sellersSphere.scale.setScalar(Math.max(0.2, sellers * scaleFactor * 0.5));
    buyersTorus.scale.setScalar(Math.max(0.2, buyers * scaleFactor * 0.5));
    itemsCylinder.scale.y = Math.max(0.2, items * scaleFactor);
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        // Rotate the group
        group.rotation.y += 0.005;
        
        // Rotate individual objects
        usersPyramid.rotation.y += 0.01;
        sellersSphere.rotation.y += 0.01;
        buyersTorus.rotation.x += 0.01;
        buyersTorus.rotation.y += 0.01;
        itemsCylinder.rotation.y += 0.01;
        
        // Gentle floating animation
        const time = Date.now() * 0.001;
        usersPyramid.position.y = Math.sin(time) * 0.1;
        sellersSphere.position.y = Math.sin(time + 1) * 0.1;
        buyersTorus.position.y = Math.sin(time + 2) * 0.1;
        itemsCylinder.position.y = Math.sin(time + 3) * 0.1;
        
        renderer.render(scene, camera);
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
    
    // Start animation
    animate();
}

// Initialize dashboard animations and interactions
function initDashboardAnimations() {
    // Add entrance animations to dashboard cards
    const cards = document.querySelectorAll('.dashboard-card');
    
    cards.forEach((card, index) => {
        // Add a staggered entrance animation
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

// Handle sidebar toggle for mobile
function toggleMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('mobile-open');
}
