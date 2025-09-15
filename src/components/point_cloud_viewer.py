"""Point cloud viewer component for Streamlit."""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os

def render_point_cloud_viewer(csv_file_path=None, height=800):
    """
    Render an interactive 3D point cloud viewer in Streamlit.

    Args:
        csv_file_path: Path to CSV file with point cloud data
        height: Height of the viewer in pixels
    """

    # Read CSV data if provided
    csv_data = None
    if csv_file_path and os.path.exists(csv_file_path):
        try:
            df = pd.read_csv(csv_file_path, delimiter=';')
            # Convert to JSON for JavaScript
            csv_data = df.to_json(orient='records')
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            return

    # HTML template with embedded Three.js viewer
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background: #0e1117;
                color: white;
            }}
            #container {{
                width: 100%;
                height: {height}px;
                position: relative;
                border-radius: 8px;
                overflow: hidden;
            }}
            #info {{
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 11px;
                z-index: 100;
                font-family: monospace;
            }}
            #controls {{
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 100;
            }}
            .btn {{
                background: #ff4b4b;
                color: white;
                border: none;
                padding: 6px 12px;
                margin: 2px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 11px;
            }}
            .btn:hover {{
                background: #ff6b6b;
            }}
            #stats {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 11px;
                z-index: 100;
                font-family: monospace;
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div id="info">
                🖱️ Left drag: Rotate<br/>
                🖱️ Right drag: Pan<br/>
                🔄 Wheel: Zoom
            </div>
            <div id="controls">
                <button class="btn" onclick="resetView()">Reset View</button>
                <button class="btn" onclick="toggleColors()">Toggle Colors</button>
            </div>
            <div id="stats">
                <div id="pointCount">Points: 0</div>
                <div id="labelInfo">Labels: None</div>
            </div>
        </div>

        <script>
            let scene, camera, renderer, controls, pointCloud;
            let useSemanticColors = true;
            let pointsData = [];

            const labelColors = {{
                1.0: [0.8, 0.2, 0.2], 2.0: [0.2, 0.8, 0.2], 3.0: [0.2, 0.2, 0.8],
                4.0: [0.8, 0.8, 0.2], 5.0: [0.8, 0.2, 0.8], 6.0: [0.2, 0.8, 0.8],
                7.0: [0.8, 0.5, 0.2], 8.0: [0.5, 0.8, 0.2], 9.0: [0.2, 0.5, 0.8],
                10.0: [0.8, 0.2, 0.5]
            }};

            function init() {{
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x0e1117);

                camera = new THREE.PerspectiveCamera(75,
                    document.getElementById('container').clientWidth / {height}, 0.1, 1000);
                camera.position.set(0, 0, 10);

                renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(
                    document.getElementById('container').clientWidth,
                    {height}
                );
                document.getElementById('container').appendChild(renderer.domElement);

                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.1;

                const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                scene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                directionalLight.position.set(1, 1, 1);
                scene.add(directionalLight);

                animate();

                // Load data if provided
                const csvData = {json.dumps(csv_data) if csv_data else 'null'};
                if (csvData) {{
                    loadPointCloudData(csvData);
                }}
            }}

            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}

            function loadPointCloudData(data) {{
                pointsData = data;
                createPointCloud(data);
            }}

            function createPointCloud(points) {{
                if (pointCloud) {{
                    scene.remove(pointCloud);
                }}

                if (!points || points.length === 0) return;

                const geometry = new THREE.BufferGeometry();
                const positions = new Float32Array(points.length * 3);
                const colors = new Float32Array(points.length * 3);

                const uniqueLabels = [...new Set(points.map(p => p.semantic_label))];
                document.getElementById('labelInfo').textContent =
                    `Labels: ${{uniqueLabels.sort().join(', ')}}`;

                for (let i = 0; i < points.length; i++) {{
                    const point = points[i];

                    positions[i * 3] = point.x;
                    positions[i * 3 + 1] = point.y;
                    positions[i * 3 + 2] = point.z;

                    if (useSemanticColors && labelColors[point.semantic_label]) {{
                        colors[i * 3] = labelColors[point.semantic_label][0];
                        colors[i * 3 + 1] = labelColors[point.semantic_label][1];
                        colors[i * 3 + 2] = labelColors[point.semantic_label][2];
                    }} else {{
                        colors[i * 3] = point.R / 255;
                        colors[i * 3 + 1] = point.G / 255;
                        colors[i * 3 + 2] = point.B / 255;
                    }}
                }}

                geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

                const material = new THREE.PointsMaterial({{
                    size: 0.02,
                    vertexColors: true,
                    sizeAttenuation: true
                }});

                pointCloud = new THREE.Points(geometry, material);
                scene.add(pointCloud);

                geometry.computeBoundingBox();
                const center = geometry.boundingBox.getCenter(new THREE.Vector3());
                controls.target.copy(center);

                document.getElementById('pointCount').textContent = `Points: ${{points.length}}`;

                const size = geometry.boundingBox.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                camera.position.copy(center);
                camera.position.z += maxDim * 2;
                controls.update();
            }}

            function resetView() {{
                if (pointCloud) {{
                    const geometry = pointCloud.geometry;
                    geometry.computeBoundingBox();
                    const center = geometry.boundingBox.getCenter(new THREE.Vector3());
                    const size = geometry.boundingBox.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);

                    camera.position.copy(center);
                    camera.position.z += maxDim * 2;
                    controls.target.copy(center);
                    controls.update();
                }}
            }}

            function toggleColors() {{
                useSemanticColors = !useSemanticColors;
                if (pointsData.length > 0) {{
                    createPointCloud(pointsData);
                }}
            }}

            init();
        </script>
    </body>
    </html>
    """

    # Render the component
    components.html(html_template, height=height + 50)

def show_point_cloud_button():
    """Show a button to display the point cloud viewer."""
    # Use relative path from project root
    csv_path = os.path.join(os.getcwd(), "DATA", "indoor_room_labelled_minimal.csv")

    if st.button("🌐 View Point Cloud", help="Open 3D point cloud visualization"):
        st.markdown("### 🏠 Indoor Room Point Cloud Visualization")
        st.markdown("*Interactive 3D viewer with semantic labels*")

        if os.path.exists(csv_path):
            render_point_cloud_viewer(csv_path, height=900)
        else:
            st.error(f"Point cloud file not found: {csv_path}")
            st.info("Make sure the DATA folder contains 'indoor_room_labelled_minimal.csv'")