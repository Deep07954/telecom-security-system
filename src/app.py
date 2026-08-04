import os
import time
import requests
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- Configuration & Telemetry Setup ---
st.set_page_config(page_title="Telecom SOC Dashboard", page_icon="🛡️", layout="wide")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# --- UI Theme Customization ---
st.markdown("""
    <style>
    /* Animated background gradient */
    @keyframes bg-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #0a0f25, #120b2e, #0d1b2a, #001219);
        background-size: 400% 400%;
        animation: bg-shift 15s ease infinite;
        background-attachment: fixed;
    }
    
    /* Gradient Typography for Headers (Multi-color fonts) */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 30, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(0, 255, 255, 0.15);
    }
    
    /* Tab typography */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #e0e0e0; 
        font-size: 14px; 
        letter-spacing: 1px; 
        text-transform: uppercase;
    }
    
    /* KPI Metrics */
    [data-testid="stMetricValue"] {
        color: #00ffff !important;
        text-shadow: 0px 0px 10px rgba(0, 255, 255, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

def get_api_status() -> bool:
    """Checks the health of the FastAPI backend."""
    try:
        return requests.get(f"{API_URL}/", timeout=2).status_code == 200
    except requests.exceptions.RequestException:
        return False

# --- Application Header ---
st.title("Network Security Operations Center")
st.markdown("Distributed Intrusion Detection and Geospatial Anomaly Visualization")

with st.sidebar:
    st.header("Control Panel")
    api_online = get_api_status()
    st.markdown(f"**Backend Status:** {'🟢 Connected' if api_online else '🔴 Disconnected'}")
    live_monitoring = st.toggle("Enable Network Intercept", value=False)
    st.markdown("---")
    st.markdown("**Active Models:**\n- `RandomForestClassifier`\n- `IsolationForest`")

# --- Module Routing ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🔴 Live Feed", 
    "🌐 Local Topology", 
    "🌍 Global Origins", 
    "📊 Dataset"
])

# --- TAB 1: Real-time Event Log ---
with tab1:
    if 'event_stream' not in st.session_state:
        st.session_state.event_stream = []

    m1, m2, m3 = st.columns(3)
    metric_analyzed = m1.empty()
    metric_blocked = m2.empty()
    metric_severity = m3.empty()

    chart_area = st.empty()
    st.subheader("Event Telemetry")
    log_area = st.empty() # Placeholder defined correctly

    if live_monitoring:
        if not api_online:
            st.error("Backend unreachable. Verify API service is running.")
        else:
            while live_monitoring:
                try:
                    res = requests.get(f"{API_URL}/api/v1/simulate", timeout=2).json()
                    st.session_state.event_stream.append(res)
                    
                    if len(st.session_state.event_stream) > 50: 
                        st.session_state.event_stream.pop(0)
                    
                    events = st.session_state.event_stream
                    threats = sum(1 for e in events if e['severity_score'] > 50)
                    peak_sev = max(e['severity_score'] for e in events)
                    
                    metric_analyzed.metric("Packets Inspected", f"{len(events) * 1024:,}")
                    metric_blocked.metric("Anomalies Flagged", threats)
                    metric_severity.metric("Peak Severity", f"{peak_sev}/100")
                    
                    df_events = pd.DataFrame(events)
                    chart_area.line_chart(df_events['severity_score'], height=250, use_container_width=True)
                    
                    # BUG FIX: Calling .container() on the correctly defined placeholder
                    with log_area.container():
                        for event in reversed(events[-10:]):
                            score = event['severity_score']
                            timestamp = event['timestamp']
                            status = event['status']
                            if score >= 95: 
                                st.error(f"[{timestamp}] CRITICAL ({score}) - {status}")
                            elif score >= 80: 
                                st.warning(f"[{timestamp}] WARNING ({score}) - {status}")
                            else: 
                                st.success(f"[{timestamp}] OK ({score}) - {status}")
                    time.sleep(1)
                except Exception as e:
                    st.warning(f"Connection unstable: {e}")
                    time.sleep(2)

# --- TAB 2: Local Network Topology ---
with tab2:
    st.markdown("### Active Node Trajectories")
    
    topology_js = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; overflow: hidden; background: transparent; font-family: monospace; }
            canvas { display: block; width: 100vw; height: 100vh; }
            .node-label {
                position: absolute; color: #fff; font-size: 11px;
                background: rgba(10, 15, 30, 0.8); border: 1px solid;
                padding: 4px 6px; pointer-events: none; border-radius: 3px;
                transform: translate(-50%, -150%); white-space: nowrap;
                transition: opacity 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.5);
            }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <script>
            const scene = new THREE.Scene(); 
            const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000); 
            camera.position.set(0, 25, 45);
            
            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); 
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement); 
            controls.enableDamping = true; controls.dampingFactor = 0.05; controls.maxPolarAngle = Math.PI / 2 - 0.05;

            const grid = new THREE.GridHelper(200, 100, 0x005555, 0x002222); 
            grid.position.y = -2; scene.add(grid); 
            
            const towerGroup = new THREE.Group(); scene.add(towerGroup);
            for(let i=0; i<3; i++) {
                const ring = new THREE.Mesh(new THREE.TorusGeometry(3 - i*0.5, 0.1, 16, 50), new THREE.MeshBasicMaterial({ color: 0x00ffff, wireframe: true, transparent: true, opacity: 0.5 }));
                ring.rotation.x = Math.PI / 2; ring.position.y = i * 2; towerGroup.add(ring);
            }
            const core = new THREE.Mesh(new THREE.OctahedronGeometry(2, 0), new THREE.MeshBasicMaterial({ color: 0x00ffff, wireframe: true, blending: THREE.AdditiveBlending, transparent: true })); core.position.y = 5; towerGroup.add(core);

            const nodes = []; const curves = []; const radius = 25;
            const nodeConfigs = [
                { type: 'DDoS Vector', color: 0xff0055 },
                { type: 'SIM Anomaly', color: 0xffaa00 },
                { type: 'Standard Tx', color: 0x00ffff },
                { type: 'Standard Tx', color: 0x00ffff },
                { type: 'Standard Tx', color: 0x00ffff }
            ];

            nodeConfigs.forEach((config, i) => {
                const angle = (i / nodeConfigs.length) * Math.PI * 2;
                const pos = new THREE.Vector3(Math.cos(angle) * radius + (Math.random()*5-2.5), Math.random()*5+1, Math.sin(angle) * radius + (Math.random()*5-2.5));
                
                const node = new THREE.Mesh(new THREE.OctahedronGeometry(1, 0), new THREE.MeshBasicMaterial({ color: 0x888888, wireframe: true }));
                node.position.copy(pos);
                scene.add(node);
                
                const label = document.createElement('div');
                label.className = 'node-label';
                label.style.borderColor = '#' + config.color.toString(16).padStart(6, '0');
                label.innerHTML = `<span style="color:#${config.color.toString(16).padStart(6, '0')}">●</span> ${config.type}`;
                document.body.appendChild(label);

                const end = core.position; 
                const mid = new THREE.Vector3((pos.x + end.x)/2, Math.max(pos.y, end.y) + 10, (pos.z + end.z)/2);
                const curve = new THREE.QuadraticBezierCurve3(pos, mid, end);
                
                scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(50)), new THREE.LineBasicMaterial({ color: 0x00ffff, transparent: true, opacity: 0.1 })));
                
                nodes.push({ mesh: node, curve: curve, config: config, label: label });
            });

            const particles = []; 
            function spawnPacket(nodeObj) {
                const isDDoS = nodeObj.config.type === 'DDoS Vector';
                const mat = new THREE.MeshBasicMaterial({ color: nodeObj.config.color, blending: THREE.AdditiveBlending, transparent: true, opacity: 0.8 });
                const mesh = new THREE.Mesh(isDDoS ? new THREE.TetrahedronGeometry(1.5, 0) : new THREE.SphereGeometry(0.3, 8, 8), mat);
                if(isDDoS) mesh.scale.setScalar(1 + Math.random()*0.5); 
                scene.add(mesh);
                particles.push({ mesh: mesh, curve: nodeObj.curve, progress: 0, speed: 0.01 + Math.random() * 0.015, type: nodeObj.config.type });
            }

            let clock = new THREE.Clock();
            function animate() {
                requestAnimationFrame(animate); 
                const time = clock.getElapsedTime(); controls.update();
                core.rotation.y = time * 0.5;
                
                nodes.forEach((n, i) => { 
                    n.mesh.position.y += Math.sin(time * 2 + i) * 0.02; 
                    n.mesh.rotation.y += 0.01; 
                    
                    const vector = n.mesh.position.clone().project(camera);
                    if (vector.z < 1) {
                        const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
                        const y = (vector.y * -0.5 + 0.5) * window.innerHeight;
                        n.label.style.left = `${x}px`;
                        n.label.style.top = `${y}px`;
                        n.label.style.opacity = 1;
                    } else {
                        n.label.style.opacity = 0;
                    }
                });

                if(Math.random() < 0.1) spawnPacket(nodes[2]);
                if(Math.random() < 0.05) { 
                    nodes[1].mesh.position.x = Math.cos(time * 5) * radius; 
                    nodes[1].mesh.position.z = Math.sin(time * 5) * radius; 
                    nodes[1].curve.v0.copy(nodes[1].mesh.position); 
                    spawnPacket(nodes[1]); 
                }
                if(Math.random() < 0.3) { 
                    spawnPacket(nodes[0]); 
                    core.material.color.setHex(0xff0055); 
                    setTimeout(() => core.material.color.setHex(0x00ffff), 50); 
                }

                for(let i = particles.length - 1; i >= 0; i--) {
                    let p = particles[i]; p.progress += p.speed;
                    if(p.progress >= 1) { 
                        scene.remove(p.mesh); p.mesh.geometry.dispose(); p.mesh.material.dispose(); particles.splice(i, 1); 
                    } else { 
                        p.mesh.position.copy(p.curve.getPoint(p.progress)); 
                        if(p.type==='DDoS Vector') { p.mesh.rotation.x+=0.1; p.mesh.rotation.y+=0.1; } 
                    }
                }
                camera.position.x = Math.sin(time * 0.1) * 45; camera.position.z = Math.cos(time * 0.1) * 45; camera.lookAt(towerGroup.position); 
                renderer.render(scene, camera);
            }
            animate();
            window.addEventListener('resize', () => { camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight); });
        </script>
    </body>
    </html>
    """
    components.html(topology_js, height=550)

    st.markdown("---")
    st.markdown("### Threat Classification Matrix (K-Means)")
    
    try:
        from src.threat_intelligence import AdvancedThreatAnalyzer
        with st.spinner('Aggregating vector data...'):
            analyzer = AdvancedThreatAnalyzer()
            fig = analyzer.generate_3d_network_graph()
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, height=600)
    except Exception as e:
        try:
            from threat_intelligence import AdvancedThreatAnalyzer
            analyzer = AdvancedThreatAnalyzer()
            fig = analyzer.generate_3d_network_graph()
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, height=600)
        except Exception as inner_e:
            st.error(f"Intelligence module failed to load. Ensure model binaries exist. [{inner_e}]")

# --- TAB 3: Global Geospatial Tracking ---
with tab3:
    st.markdown("### Global Anomaly Origins")
    
    global_tracking_js = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; overflow: hidden; background: transparent; font-family: monospace; }
            canvas { display: block; width: 100vw; height: 100vh; }
            
            /* Enhanced Geo-Labels */
            .geo-label {
                position: absolute; color: white; font-size: 11px;
                background: rgba(5, 10, 20, 0.9); border: 1px solid;
                padding: 8px; pointer-events: none; border-radius: 4px;
                transform: translate(-50%, -100%); white-space: nowrap;
                transition: opacity 0.2s; box-shadow: 0 0 10px rgba(0,0,0,0.8);
                line-height: 1.4;
            }
            
            /* HUD Control Panel */
            #control-panel {
                position: absolute; bottom: 30px; left: 30px;
                background: rgba(10, 15, 30, 0.85); border: 1px solid #00ffff;
                color: #fff; padding: 15px; border-radius: 5px;
                font-family: monospace; width: 280px; box-shadow: 0 4px 15px rgba(0,0,0,0.7);
                pointer-events: none;
            }
            .threat-bar { width: 100%; height: 12px; background: #1a1a1a; margin: 10px 0; border-radius: 6px; overflow: hidden; border: 1px solid #333; }
            .threat-fill { height: 100%; width: 88%; background: linear-gradient(90deg, #ffaa00, #ff0055); animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="control-panel">
            <h3 style="margin:0 0 10px 0; color:#00ffff; font-size:15px; letter-spacing:1px;">SYS_DEF_CTRL</h3>
            <div style="font-size: 12px;">GLOBAL THREAT LEVEL: <span style="color:#ff0055; font-weight:bold;">CRITICAL</span></div>
            <div class="threat-bar"><div class="threat-fill"></div></div>
            <div id="active-vectors" style="font-size:11px; color:#aaa;">Tracking 4 active vectors...</div>
        </div>

        <script>
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 180;
            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;

            const earth = new THREE.Group(); scene.add(earth);
            earth.add(new THREE.Mesh(new THREE.SphereGeometry(50, 64, 64), new THREE.MeshBasicMaterial({ color: 0x00050a })));
            earth.add(new THREE.Mesh(new THREE.SphereGeometry(50.5, 64, 64), new THREE.MeshBasicMaterial({ color: 0x003344, wireframe: true, transparent: true, opacity: 0.3 })));

            // Advanced Dataset with Origins and Destinations
            const threatData = [
                { from: [-23.5, -46.6], to: [40.7, -74.0], type: 'DDoS Swarm', color: 0xff0055, source: 'Sao Paulo, BR', dest: 'New York, US', level: 98 },
                { from: [55.7, 37.6], to: [51.5, -0.1], type: 'SIM Clone', color: 0xffaa00, source: 'Moscow, RU', dest: 'London, UK', level: 85 },
                { from: [31.2, 121.4], to: [1.3, 103.8], type: 'BGP Hijack', color: 0xb19cd9, source: 'Shanghai, CN', dest: 'Singapore, SG', level: 92 },
                { from: [52.3, 4.9], to: [35.6, 139.6], type: 'Brute Force', color: 0x00ffff, source: 'Amsterdam, NL', dest: 'Tokyo, JP', level: 76 }
            ];

            const arcs = [];
            function latLonToVector3(lat, lon, radius) {
                const phi = (90 - lat) * (Math.PI / 180); const theta = (lon + 180) * (Math.PI / 180);
                return new THREE.Vector3(-radius * Math.sin(phi) * Math.cos(theta), radius * Math.cos(phi), radius * Math.sin(phi) * Math.sin(theta));
            }

            threatData.forEach(data => {
                const start = latLonToVector3(data.from[0], data.from[1], 50);
                const end = latLonToVector3(data.to[0], data.to[1], 50);
                
                // HTML Label
                const label = document.createElement('div'); label.className = 'geo-label';
                const colorHex = '#' + data.color.toString(16).padStart(6, '0');
                label.style.borderColor = colorHex;
                label.innerHTML = `
                    <span style="color:${colorHex}; font-weight:bold;">[${data.type}]</span><br>
                    <span style="color:#aaa;">SRC:</span> ${data.source}<br>
                    <span style="color:#aaa;">TGT:</span> ${data.dest}<br>
                    <span style="color:${colorHex}; font-size:10px;">SEV: ${data.level}/100</span>
                `;
                document.body.appendChild(label);
                
                // Draw Tower at Destination
                const towerGeo = new THREE.CylinderGeometry(0.3, 0.7, 3, 8);
                const towerMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, wireframe: true });
                const tower = new THREE.Mesh(towerGeo, towerMat);
                tower.position.copy(end);
                tower.lookAt(new THREE.Vector3(0,0,0));
                tower.rotateX(Math.PI / 2);
                earth.add(tower);
                
                // Origin marker
                const originDot = new THREE.Mesh(new THREE.SphereGeometry(0.6), new THREE.MeshBasicMaterial({ color: data.color }));
                originDot.position.copy(start);
                earth.add(originDot);

                const mid = start.clone().lerp(end, 0.5).multiplyScalar(1.4);
                const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
                earth.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(50)), new THREE.LineBasicMaterial({ color: data.color, transparent: true, opacity: 0.2 })));
                
                const dot = new THREE.Mesh(new THREE.SphereGeometry(1.0), new THREE.MeshBasicMaterial({ color: data.color }));
                earth.add(dot);
                arcs.push({ dot, curve, progress: Math.random(), label: label, startPos: start });
            });

            function animate() {
                requestAnimationFrame(animate); earth.rotation.y += 0.0015;
                arcs.forEach(a => {
                    a.progress += 0.003; if(a.progress > 1) a.progress = 0;
                    a.dot.position.copy(a.curve.getPoint(a.progress));

                    const worldPos = a.startPos.clone().applyMatrix4(earth.matrixWorld);
                    const vector = worldPos.clone().project(camera);
                    if (vector.z < 1 && worldPos.z > 0) {
                        a.label.style.opacity = '1';
                        a.label.style.left = `${(vector.x * .5 + .5) * window.innerWidth}px`;
                        a.label.style.top = `${(vector.y * -.5 + .5) * window.innerHeight - 20}px`;
                    } else { a.label.style.opacity = '0'; }
                });
                controls.update(); renderer.render(scene, camera);
            }
            animate();
            window.addEventListener('resize', () => { camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight); });
        </script>
    </body>
    </html>
    """
    components.html(global_tracking_js, height=750)

# --- TAB 4: Data Explorer ---
with tab4:
    st.markdown("### Training Data Repository")
    st.markdown("Raw feature space for model training and validation.")
    
    paths = ["telecom_security_data.csv", "data/telecom_security_data.csv", "../telecom_security_data.csv", "src/telecom_security_data.csv"]
    loaded = False
    
    for path in paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, nrows=10000)
                st.success(f"Source connected: `{path}`")
                st.dataframe(df, use_container_width=True, height=500)
                loaded = True
                break
            except Exception as e:
                st.warning(f"File found but parsing failed: {e}")
                
    if not loaded:
        st.error("Dataset missing. Execute data generation pipeline prior to launching dashboard.")
        
 