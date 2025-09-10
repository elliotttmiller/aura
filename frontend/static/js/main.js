import * as THREE from 'https://cdn.skypack.dev/three@0.129.0';
import { STLLoader } from 'https://cdn.skypack.dev/three@0.129.0/examples/jsm/loaders/STLLoader.js';
import { OrbitControls } from 'https://cdn.skypack.dev/three@0.129.0/examples/jsm/controls/OrbitControls.js';

class Viewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with id "${containerId}" not found.`);
            return;
        }
        this.init();
    }

    init() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x23262F);
        this.camera = new THREE.PerspectiveCamera(45, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
        this.camera.position.set(0, 70, 70);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.container.appendChild(this.renderer.domElement);
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1.5));
        const dirLight = new THREE.DirectionalLight(0xffffff, 1);
        dirLight.position.set(100, 100, 100);
        this.scene.add(dirLight);
        this.animate = this.animate.bind(this);
        this.animate();
        window.addEventListener('resize', () => {
            this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        });
    }

    animate() {
        requestAnimationFrame(this.animate);
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    loadSTL(url, metalType) {
        if (this.currentModel) {
            this.scene.remove(this.currentModel);
        }
        this.displayMessage('Loading 3D model...', false);
        const loader = new STLLoader();
        const material = new THREE.MeshStandardMaterial({ metalness: 1.0, roughness: 0.2 });
        if (metalType === 'GOLD') material.color.set(0xFFD700);
        else if (metalType === 'SILVER') material.color.set(0xC0C0C0);
        else if (metalType === 'PLATINUM') material.color.set(0xE5E4E2);
        loader.load(url, (geometry) => {
            this.displayMessage('', false);
            const mesh = new THREE.Mesh(geometry, material);
            mesh.rotation.x = -Math.PI / 2;
            const box = new THREE.Box3().setFromObject(mesh);
            const center = box.getCenter(new THREE.Vector3());
            mesh.position.sub(center);
            this.scene.add(mesh);
            this.currentModel = mesh;
        }, undefined, (error) => {
            console.error('Error loading STL:', error);
            this.displayMessage('Error: Could not load 3D model.', true);
        });
    }

    displayMessage(text, isError = false) {
        let messageDiv = this.container.querySelector('.message');
        if (!messageDiv) {
            messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            this.container.appendChild(messageDiv);
        }
        messageDiv.innerText = text;
        messageDiv.style.color = isError ? '#FF6B6B' : '#A5A7B2';
        messageDiv.style.display = text ? 'block' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const viewer = new Viewer('viewer');
    const form = document.getElementById('jewelry-form');
    const refineForm = document.getElementById('refine-form');
    const refineSection = document.getElementById('refine-section');
    const reasoningDisplay = document.getElementById('reasoning-display');
    const reasoningText = document.getElementById('reasoning-text');
    const resultDiv = document.getElementById('result');
    
    // V6.0 State Management for Cognitive Loop
    let lastGenerationData = null;
    let currentSpecs = null;
    
    // Initial Design Generation
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        viewer.displayMessage('Generating initial design...', false);
        resultDiv.innerHTML = '';
        hideRefinementUI();
        
        const formData = {
            prompt: document.getElementById('prompt').value,
            metal: document.getElementById('metal').value,
            ring_size: parseFloat(document.getElementById('ring_size').value),
            stone_shape: document.getElementById('stone_shape').value,
            stone_carat: parseFloat(document.getElementById('stone_carat').value),
        };
        
        currentSpecs = formData;
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            if (data.file) {
                lastGenerationData = data;
                displayGenerationResults(data, formData);
                showRefinementUI();
            } else {
                throw new Error(data.error || 'Unknown error occurred in backend.');
            }
        } catch (err) {
            console.error('Generation error:', err);
            viewer.displayMessage(`Error: ${err.message}`, true);
        }
    });
    
    // V6.0 Refinement Process
    refineForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        if (!lastGenerationData) {
            alert('Please generate an initial design first.');
            return;
        }
        
        viewer.displayMessage('Refining design...', false);
        resultDiv.innerHTML = '';
        
        const refinementPrompt = document.getElementById('refinement-prompt').value;
        
        const refineData = {
            refinement_prompt: refinementPrompt,
            previous_blueprint: lastGenerationData.blueprint_used,
            previous_stl_file: lastGenerationData.file,
            ...currentSpecs
        };
        
        try {
            const response = await fetch('/refine', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(refineData)
            });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            if (data.file) {
                lastGenerationData = {
                    file: data.file,
                    blueprint_used: data.refined_blueprint
                };
                displayRefinementResults(data, currentSpecs);
                document.getElementById('refinement-prompt').value = '';
            } else {
                throw new Error(data.error || 'Unknown error occurred during refinement.');
            }
        } catch (err) {
            console.error('Refinement error:', err);
            viewer.displayMessage(`Refinement Error: ${err.message}`, true);
        }
    });
    
    function displayGenerationResults(data, formData) {
        // Display result
        resultDiv.innerHTML = `<b>Initial Design:</b> <span style='color:#6C47FF'>${data.file}</span>`;
        
        // Load 3D model
        viewer.loadSTL(`/output/${data.file}`, formData.metal);
        
        // Display AI reasoning if available
        if (data.blueprint_used && data.blueprint_used.reasoning) {
            displayReasoning(data.blueprint_used.reasoning);
        }
    }
    
    function displayRefinementResults(data, formData) {
        // Display result
        resultDiv.innerHTML = `<b>Refined Design:</b> <span style='color:#00C6FB'>${data.file}</span>`;
        
        // Load 3D model
        viewer.loadSTL(`/output/${data.file}`, formData.metal);
        
        // Display refined AI reasoning
        if (data.refined_blueprint && data.refined_blueprint.reasoning) {
            displayReasoning(data.refined_blueprint.reasoning);
        }
        
        // Show analysis data if available
        if (data.geometric_analysis) {
            console.log('Geometric Analysis:', data.geometric_analysis);
        }
    }
    
    function displayReasoning(reasoning) {
        if (reasoning) {
            reasoningText.textContent = reasoning;
            reasoningDisplay.style.display = 'block';
        }
    }
    
    function showRefinementUI() {
        refineSection.classList.add('visible');
    }
    
    function hideRefinementUI() {
        refineSection.classList.remove('visible');
        reasoningDisplay.style.display = 'none';
        lastGenerationData = null;
    }
});
