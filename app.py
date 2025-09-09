# Base libraries
from typing import Dict

import numpy as np
import pandas as pd
import json

# Graph and algorithm-related libraries
import networkx as nx
from sklearn.cluster import DBSCAN

# For visualization
import open3d as o3d
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    from pxr import Usd, UsdGeom, Sdf, Gf, UsdShade

    USD_AVAILABLE = True
except ImportError:
    print("USD not available. Install with: pip install usd-core")
    USD_AVAILABLE = False


def load_semantic_point_cloud(file_path, column_name='semantic_label'):
    """Load semantic point cloud DATA from ASCII formats."""

    df = pd.read_csv(file_path, delimiter=';')
    class_names = ['ceiling', 'floor', 'wall', 'chair', 'furniture', 'table']

    # Assuming the numerical labels are 0.0, 1.0, 2.0, ...
    label_map = {float(i): class_names[i] for i in range(len(class_names))}

    df[column_name] = df[column_name].map(label_map)

    # I sample here for replication goals
    return df.sample(n=70000, random_state=1)


# Let us control the output of
raw_data = load_semantic_point_cloud('./DATA/indoor_room_labelled_minimal.csv')
# I sample here for replication goals
# demo_data = raw_data.sample(n=100000, random_state=1)


def visualize_semantic_pointcloud(df, point_size=2.0):
    """Visualize semantic point cloud with flat colors per semantic label
    using Open3D."""

    # Extract coordinates
    points = df[['x', 'y', 'z']].values

    # Create Open3D point cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # Create color mapping for semantic labels
    unique_labels = df['semantic_label'].unique()
    color_map = {}

    # Generate distinct colors for each label
    for i, label in enumerate(unique_labels):
        hue = i / len(unique_labels)
        color_map[label] = plt.cm.tab10(hue)[:3]

    # Assign colors based on semantic labels
    colors = np.array([color_map[label] for label in df['semantic_label']])
    pcd.colors = o3d.utility.Vector3dVector(colors)

    # Create visualization
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Semantic Point Cloud", width=1200,
                      height=800)
    vis.add_geometry(pcd)

    # Set point size
    render_option = vis.get_render_option()
    render_option.point_size = point_size

    print(
        f"Visualizing {len(points)} points with {len(unique_labels)} "
        f"semantic classes:")
    for label in unique_labels:
        count = (df['semantic_label'] == label).sum()
        print(f"  {label}: {count} points")

    vis.run()
    vis.destroy_window()


# Time to have fun
# visualize_semantic_pointcloud(demo_data, point_size=3.0)


def extract_semantic_objects(df: pd.DataFrame, eps: float = 0.5,
                             min_samples: int = 10) -> Dict:
    """Extract individual objects from semantic point cloud using
    clustering."""
    objects = {}

    for label in df['semantic_label'].unique():
        label_points = df[df['semantic_label'] == label]

        if len(label_points) < min_samples:
            continue

        # Apply DBSCAN clustering
        coords = label_points[['x', 'y', 'z']].values
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)

        # Group by cluster
        label_points_copy = label_points.copy()
        label_points_copy['cluster'] = clustering.labels_

        for cluster_id in np.unique(clustering.labels_):
            if cluster_id == -1:  # Skip noise points
                continue

            cluster_points = label_points_copy[
                label_points_copy['cluster'] == cluster_id]
            object_key = f"{label}_{cluster_id}"

            objects[object_key] = {
                'points': cluster_points,
                'centroid': cluster_points[['x', 'y', 'z']].mean().values,
                'bounds': {
                    'min': cluster_points[['x', 'y', 'z']].min().values,
                    'max': cluster_points[['x', 'y', 'z']].max().values
                },
                'semantic_label': label,
                'point_count': len(cluster_points)
            }

    return objects


objects = extract_semantic_objects(raw_data)


def visualize_room_furniture_graph(furniture_data):
    """Builds and visualizes a graph of room furniture."""

    G = nx.Graph()
    for item, connections in furniture_data.items():
        G.add_node(item)
        for connected_item in connections:
            G.add_edge(item, connected_item)
    pos = nx.spring_layout(G, seed=42)  # For reproducible layout
    nx.draw(G, pos, with_labels=True, node_color='salmon',
            node_size=500, font_size=10, font_weight='bold')
    plt.title("Room Furniture Graph")
    plt.show()


# Example of a room description:
room_layout = {
    "bed": ["nightstand", "lamp", "rug"],
    "nightstand": ["bed", "lamp"],
    "lamp": ["bed", "nightstand"],
    "rug": ["bed", "sofa", "bookshelf"],
    "sofa": ["coffee table", "TV", "rug"],
    "coffee table": ["sofa", "TV"],
    "TV": ["sofa", "coffee table", "TV stand"],
    "TV stand": ["TV"],
    "bookshelf": ["desk"],
    "desk": ["bookshelf", "chair"],
    "chair": ["desk"]
}
visualize_room_furniture_graph(room_layout)


def estimate_surface_area(points):
    from scipy.spatial import ConvexHull
    try:
        hull = ConvexHull(points)
        return hull.area  # Surface area of convex hull
    except:
        return 0.0  # Fallback for degenerate cases


def compute_object_features(objects):
    """Compute geometric and semantic features for each object."""
    features = {}

    for obj_name, obj_data in objects.items():
        points = obj_data['points'][['x', 'y', 'z']].values

        # Geometric features
        volume = np.prod(obj_data['bounds']['max'] - obj_data['bounds']['min'])
        surface_area = estimate_surface_area(points)
        compactness = (surface_area ** 3) / (
                36 * np.pi * volume ** 2) if volume > 0 else 0

        features[obj_name] = {
            'volume': volume,
            'surface_area': surface_area,
            'compactness': compactness,
            'height': obj_data['bounds']['max'][2] - obj_data['bounds']['min'][
                2],
            'semantic_label': obj_data['semantic_label'],
            'centroid': obj_data['centroid'],
            'point_density': obj_data[
                                 'point_count'] / volume if volume > 0 else 0
        }

    return features


# Let us compute our features
features = compute_object_features(objects)

print()


def is_contained(bounds1, bounds2):
    """Check if object1 is contained within object2."""
    return (np.all(bounds1['min'] >= bounds2['min']) and
            np.all(bounds1['max'] <= bounds2['max']))


def are_adjacent(bounds1, bounds2, tolerance=0.1):
    # Check if faces are close along each axis
    for axis in range(3):  # X, Y, Z axes
        # Face-to-face proximity checks
        if (abs(bounds1['max'][axis] - bounds2['min'][axis]) < tolerance or
                abs(bounds2['max'][axis] - bounds1['min'][axis]) < tolerance):
            return True
    return False


def determine_relationship_type(obj1, obj2, threshold):
    centroid1 = obj1['centroid']
    centroid2 = obj2['centroid']

    distance = np.linalg.norm(centroid1 - centroid2)
    if distance > threshold:
        return None  # Too far apart

    # Vertical relationship analysis
    z_diff = centroid1[2] - centroid2[2]
    if abs(z_diff) > 0.5:  # Significant height difference
        return 'above' if z_diff > 0 else 'below'

    # Containment analysis
    bounds1 = obj1['bounds']
    bounds2 = obj2['bounds']

    if is_contained(bounds1, bounds2):
        return 'inside'
    elif is_contained(bounds2, bounds1):
        return 'contains'

    # Adjacency analysis
    if are_adjacent(bounds1, bounds2, tolerance=0.3):
        return 'adjacent'

    return 'near'  # Default fallback


def compute_spatial_relationships(objects, distance_threshold=2.0):
    relationships = []
    object_names = list(objects.keys())

    for i, obj1 in enumerate(object_names):
        for j, obj2 in enumerate(object_names[i + 1:],
                                 i + 1):  # Avoid duplicates
            rel_type = determine_relationship_type(objects[obj1],
                                                   objects[obj2],
                                                   distance_threshold)
            if rel_type:  # Only keep valid relationships
                relationships.append((obj1, obj2, rel_type))

    return relationships


relationships = compute_spatial_relationships(objects)


def build_scene_graph(objects, relationships, features):
    G = nx.DiGraph()

    # Add nodes with rich attributes
    for obj_name, obj_data in objects.items():
        obj_features = features.get(obj_name, {}).copy()
        obj_features.pop('semantic_label', None)  # Avoid conflicts
        obj_features.pop('centroid', None)  # Avoid conflicts

        G.add_node(obj_name,
                   semantic_label=obj_data['semantic_label'],
                   centroid=obj_data['centroid'].tolist(),
                   point_count=obj_data['point_count'],
                   **obj_features)

    # Add relationship edges
    for obj1, obj2, rel_type in relationships:
        G.add_edge(obj1, obj2, relationship=rel_type)

    return G


scene_graph = build_scene_graph(objects, relationships, features)

print()


def analyze_scene_graph(G):
    analysis = {
        'node_count': G.number_of_nodes(),
        'edge_count': G.number_of_edges(),
        'semantic_distribution': {},
        'relationship_types': {},
        'connected_components': nx.number_weakly_connected_components(G),
        'avg_degree': sum(dict(
            G.degree()).values()) / G.number_of_nodes() if
        G.number_of_nodes() > 0 else 0
    }

    # Analyze semantic distribution
    for node, data in G.nodes(data=True):
        label = data.get('semantic_label', 'unknown')
        analysis['semantic_distribution'][label] = analysis[
                                                       'semantic_distribution'].get(
            label, 0) + 1

    # Analyze relationship types
    for _, _, data in G.edges(data=True):
        rel = data.get('relationship', 'unknown')
        analysis['relationship_types'][rel] = analysis[
                                                  'relationship_types'].get(
            rel, 0) + 1

    return analysis


def create_usd_object(stage, node_name, node_data):
    """Create USD primitive for scene graph node."""
    # Create object primitive path
    obj_path = f'/Scene/Geometry/{node_name}'

    # Create cube primitive as placeholder
    cube_prim = UsdGeom.Cube.Define(stage, obj_path)

    # Set transform based on centroid
    centroid = node_data.get('centroid', [0, 0, 0])
    if isinstance(centroid, np.ndarray):
        centroid = centroid.tolist()

    # Apply transform
    xform_api = UsdGeom.XformCommonAPI(cube_prim)
    xform_api.SetTranslate(centroid)

    # Add semantic attributes
    prim = cube_prim.GetPrim()
    prim.SetCustomDataByKey('semantic_label',
                            node_data.get('semantic_label', 'unknown'))
    prim.SetCustomDataByKey('point_count', node_data.get('point_count', 0))
    prim.SetCustomDataByKey('volume', node_data.get('volume', 0.0))

    # Set size based on volume (cube root for uniform scaling)
    volume = node_data.get('volume', 1.0)
    size = max(0.1, (volume ** (1 / 3)) * 0.5)  # Scale factor
    cube_prim.GetSizeAttr().Set(size)


def add_relationships_to_stage(stage, scene_graph):
    """Add spatial relationships as custom data on root prim."""
    relationships_strings = []

    for obj1, obj2, edge_data in scene_graph.edges(data=True):
        rel_str = (f"{obj1} -> {obj2} ("
                   f"{edge_data.get('relationship', 'unknown')})")
        relationships_strings.append(rel_str)

    # Store as string array instead of complex objects
    root_prim = stage.GetPrimAtPath('/Scene')
    if root_prim.IsValid():
        root_prim.SetCustomDataByKey('spatial_relationships_count',
                                     len(relationships_strings))
        # Store first few relationships as examples
        sample_rels = relationships_strings[:10]  # First 10 relationships
        for i, rel in enumerate(sample_rels):
            root_prim.SetCustomDataByKey(f'relationship_{i}', rel)


def create_usd_stage(scene_graph: nx.DiGraph, output_path: str) -> bool:
    """Create USD stage from scene graph and export to file."""
    if not USD_AVAILABLE:
        print("USD not available. Cannot create USD stage.")
        return False

    # Create new stage
    stage = Usd.Stage.CreateNew(output_path)

    # Set up scene hierarchy
    root_prim = stage.DefinePrim('/Scene', 'Xform')
    stage.SetDefaultPrim(root_prim)

    # Create geometry scope for objects
    geom_scope = UsdGeom.Scope.Define(stage, '/Scene/Geometry')

    # Add each object as a primitive
    for node, data in scene_graph.nodes(data=True):
        create_usd_object(stage, node, data)

    # Add relationships as metadata
    add_relationships_to_stage(stage, scene_graph)

    # Save stage
    stage.Save()
    return True


def process_semantic_pointcloud_to_usd(input_path, output_usd, eps=0.8,
                                       min_samples=15, distance_threshold=3.0):
    """Complete pipeline from semantic point cloud to USD scene graph."""
    results = {'success': False, 'files_created': [], 'analysis': {}}

    try:
        # Load and validate data
        print("Loading semantic point cloud...")
        df = load_semantic_point_cloud(input_path)

        print(
            f"Loaded {len(df)} points with {df['semantic_label'].nunique()} "
            f"semantic classes")

        # Extract objects
        print("Extracting semantic objects...")
        objects = extract_semantic_objects(df, eps=eps,
                                           min_samples=min_samples)
        print(f"Found {len(objects)} objects")

        # Compute features
        print("Computing object features...")
        features = compute_object_features(objects)

        # Find relationships
        print("Computing spatial relationships...")
        relationships = compute_spatial_relationships(objects,
                                                      distance_threshold)
        print(f"Found {len(relationships)} spatial relationships")

        # Build scene graph
        print("Building scene graph...")
        scene_graph = build_scene_graph(objects, relationships, features)

        # Validate scene graph
        # validation = validate_scene_graph(scene_graph)
        # if not validation['is_valid']:
        #     print("Warning: Scene graph validation found issues:",
        #           validation['issues'])

        # Export to USD
        if USD_AVAILABLE:
            print(f"Exporting to USD: {output_usd}")
            usd_success = create_usd_stage(scene_graph, output_usd)
            if usd_success:
                results['files_created'].append(output_usd)

        # Export summary
        summary_path = output_usd.replace('.usda', '_summary.json')
        # export_scene_summary(scene_graph, summary_path)
        results['files_created'].append(summary_path)

        # Store analysis results
        results['analysis'] = analyze_scene_graph(scene_graph)
        # results['validation'] = validation
        results['success'] = True

        print("Pipeline completed successfully!")

    except Exception as e:
        print(f"Pipeline failed: {str(e)}")
        results['error'] = str(e)

    return results


# Complete pipeline execution
process_semantic_pointcloud_to_usd('./DATA/indoor_room_labelled.csv',
                                   'demo_scene_c.usda', eps=0.2,
                                   min_samples=20, distance_threshold=3.0)
