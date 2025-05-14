// Seller Dashboard JavaScript

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
    const totalItems = parseInt(statsOverview.getAttribute('data-items') || '0');
    const totalSales = parseInt(statsOverview.getAttribute('data-sales') || '0');
    const totalRevenue = parseFloat(statsOverview.getAttribute('data-revenue') || '0');
    
    // Create a simple 3D visualization for the dashboard header
    createDashboardVisualization(totalItems, totalSales, totalRevenue);
}

// Create a simple 3D visualization using Three.js
function createDashboardVisualization(items, sales, revenue) {
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
    // Items cube
    const itemsGeometry = new THREE.BoxGeometry(1, 1, 1);
    const itemsMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x795757,
        roughness: 0.7,
        metalness: 0.2
    });
    const itemsCube = new THREE.Mesh(itemsGeometry, itemsMaterial);
    itemsCube.position.x = -2;
    group.add(itemsCube);
    
    // Sales sphere
    const salesGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const salesMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x664343,
        roughness: 0.5,
        metalness: 0.3
    });
    const salesSphere = new THREE.Mesh(salesGeometry, salesMaterial);
    salesSphere.position.x = 0;
    group.add(salesSphere);
    
    // Revenue cylinder
    const revenueGeometry = new THREE.CylinderGeometry(0.5, 0.5, 1, 32);
    const revenueMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x3B3030,
        roughness: 0.3,
        metalness: 0.5
    });
    const revenueCylinder = new THREE.Mesh(revenueGeometry, revenueMaterial);
    revenueCylinder.position.x = 2;
    group.add(revenueCylinder);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Scale objects based on data
    const maxValue = Math.max(items, sales, revenue / 1000);
    const scaleFactor = 1 / maxValue;
    
    itemsCube.scale.y = Math.max(0.2, items * scaleFactor);
    salesSphere.scale.setScalar(Math.max(0.2, sales * scaleFactor * 0.5));
    revenueCylinder.scale.y = Math.max(0.2, (revenue / 1000) * scaleFactor);
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        // Rotate the group
        group.rotation.y += 0.005;
        
        // Gentle floating animation
        const time = Date.now() * 0.001;
        itemsCube.position.y = Math.sin(time) * 0.1;
        salesSphere.position.y = Math.sin(time + 1) * 0.1;
        revenueCylinder.position.y = Math.sin(time + 2) * 0.1;
        
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
