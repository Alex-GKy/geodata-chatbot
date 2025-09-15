"""Point cloud viewer component for Streamlit."""

import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


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
        <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/controls/TrackballControls.js"></script>
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
                outline: none;
            }}

            #container:focus {{
                border: 2px solid #4CAF50;
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
        <div id="container" tabindex="0">
            <div id="info">
                🖱️ Left drag: Full 6-DOF rotation<br/>
                🖱️ Right drag: Pan<br/>
                🔄 Wheel: Zoom<br/>
                💡 Try rotating near edges for roll
            </div>
            <div id="controls">
                <button class="btn" onclick="resetView()">Reset View</button>
                <button class="btn" onclick="toggleColors()">Toggle 
                Colors</button>
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
                1.0: [0.8, 0.2, 0.2], 2.0: [0.2, 0.8, 0.2], 3.0: [0.2, 0.2, 
                0.8],
                4.0: [0.8, 0.8, 0.2], 5.0: [0.8, 0.2, 0.8], 6.0: [0.2, 0.8, 
                0.8],
                7.0: [0.8, 0.5, 0.2], 8.0: [0.5, 0.8, 0.2], 9.0: [0.2, 0.5, 
                0.8],
                10.0: [0.8, 0.2, 0.5]
            }};

            function init() {{
                if (typeof THREE === 'undefined') {{
                    console.error('THREE.js not loaded properly');
                    document.getElementById('container').innerHTML = '<div style="color: white; padding: 20px; text-align: center;">❌ Three.js library failed to load</div>';
                    return;
                }}

                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x0e1117);

                camera = new THREE.PerspectiveCamera(75,
                    document.getElementById('container').clientWidth / 
{height}, 0.1, 1000);
                camera.position.set(0, 0, 10);

                renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(
                    document.getElementById('container').clientWidth,
                    {height}
                );
                document.getElementById('container').appendChild(
                renderer.domElement);

                // Use TrackballControls for full 6-DOF rotation including roll
                controls = new THREE.TrackballControls(camera, 
                renderer.domElement);
                controls.rotateSpeed = 2.0;
                controls.zoomSpeed = 1.2;
                controls.panSpeed = 0.8;
                controls.noZoom = false;
                controls.noPan = false;
                controls.staticMoving = true;
                controls.dynamicDampingFactor = 0.3;

                const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                scene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(
                0xffffff, 0.8);
                directionalLight.position.set(1, 1, 1);
                scene.add(directionalLight);

                animate();

                // Auto focus the container
                const container = document.getElementById('container');
                container.focus();

                // Add keyboard controls for roll
                container.addEventListener('keydown', function(event) {{
                    console.log('Key pressed:', event.code);
                    if (event.code === 'KeyQ') {{
                        // Roll left (rotate around camera's forward axis)
                        camera.rotateZ(0.1);
                        console.log('Rolling left');
                        event.preventDefault();
                    }} else if (event.code === 'KeyE') {{
                        // Roll right
                        camera.rotateZ(-0.1);
                        console.log('Rolling right');
                        event.preventDefault();
                    }}
                }});

                // Also listen on document as fallback
                document.addEventListener('keydown', function(event) {{
                    if (event.code === 'KeyQ' || event.code === 'KeyE') {{
                        container.dispatchEvent(new KeyboardEvent('keydown', 
                        event));
                    }}
                }});

                // Load data if provided
                const csvDataString = `{csv_data if csv_data else 'null'}`;
                if (csvDataString !== 'null') {{
                    const csvData = JSON.parse(csvDataString);
                    console.log('Loaded data:', csvData.length, 'points');
                    loadPointCloudData(csvData);
                }} else {{
                    console.log('No CSV data provided');
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
                console.log('createPointCloud called with:', points);
                if (pointCloud) {{
                    scene.remove(pointCloud);
                }}

                if (!points || points.length === 0) {{
                    console.log('No points provided or empty array');
                    return;
                }}

                if (!Array.isArray(points)) {{
                    console.error('Points is not an array:', typeof points);
                    return;
                }}

                const geometry = new THREE.BufferGeometry();
                const positions = new Float32Array(points.length * 3);
                const colors = new Float32Array(points.length * 3);

                const uniqueLabels = [...new Set(points.map(p => 
                p.semantic_label))];
                document.getElementById('labelInfo').textContent =
                    `Labels: ${{uniqueLabels.sort().join(', ')}}`;

                for (let i = 0; i < points.length; i++) {{
                    const point = points[i];

                    positions[i * 3] = point.x;
                    positions[i * 3 + 1] = point.y;
                    positions[i * 3 + 2] = point.z;

                    if (useSemanticColors && labelColors[
                    point.semantic_label]) {{
                        colors[i * 3] = labelColors[point.semantic_label][0];
                        colors[i * 3 + 1] = labelColors[
                        point.semantic_label][1];
                        colors[i * 3 + 2] = labelColors[
                        point.semantic_label][2];
                    }} else {{
                        colors[i * 3] = point.R / 255;
                        colors[i * 3 + 1] = point.G / 255;
                        colors[i * 3 + 2] = point.B / 255;
                    }}
                }}

                geometry.setAttribute('position', new THREE.BufferAttribute(
                positions, 3));
                geometry.setAttribute('color', new THREE.BufferAttribute(
                colors, 3));

                const material = new THREE.PointsMaterial({{
                    size: 0.02,
                    vertexColors: true,
                    sizeAttenuation: true
                }});

                pointCloud = new THREE.Points(geometry, material);
                scene.add(pointCloud);

                geometry.computeBoundingBox();
                const center = geometry.boundingBox.getCenter(new 
                THREE.Vector3());
                controls.target.copy(center);

                document.getElementById('pointCount').textContent = `Points: 
                ${{points.length}}`;

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
                    const center = geometry.boundingBox.getCenter(new 
                    THREE.Vector3());
                    const size = geometry.boundingBox.getSize(new 
                    THREE.Vector3());
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


def show_point_cloud_viewer():
    """Show the point cloud viewer permanently in the sidebar."""
    # Use relative path from project root
    csv_path = os.path.join(os.getcwd(), "DATA",
                            "indoor_room_labelled_minimal.csv")

    st.markdown("*Interactive 3D viewer with semantic labels*")

    if os.path.exists(csv_path):
        render_point_cloud_viewer(csv_path, height=600)
    else:
        # Try alternative paths
        alt_path = os.path.join("DATA", "indoor_room_labelled_minimal.csv")
        if os.path.exists(alt_path):
            render_point_cloud_viewer(alt_path, height=600)
        else:
            st.warning("⚠️ Point cloud data not found")
            st.info("Make sure the DATA folder contains 'indoor_room_labelled_minimal.csv'")
