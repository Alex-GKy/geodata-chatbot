"""Point cloud viewer component for Streamlit."""

import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from utils.config import is_mining_case_enabled


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

    # Load HTML template from file
    template_path = os.path.join(os.path.dirname(__file__), 'templates',
                                 'point_cloud_viewer.html')

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()

        # Format the template with dynamic values
        html_template = html_template.format(
            height=height,
            csv_data=csv_data if csv_data else 'null'
        )
    except FileNotFoundError:
        st.error(f"HTML template not found at: {template_path}")
        return
    except Exception as e:
        st.error(f"Error loading HTML template: {e}")
        return

    # Render the component
    components.html(html_template, height=height + 50)


def show_available_files():
    """Show list of files available in the temporary workspace."""
    try:
        # Import here to avoid circular imports
        from agent.graph import TEMP_WORKSPACE

        if os.path.exists(TEMP_WORKSPACE):
            files = [f for f in os.listdir(TEMP_WORKSPACE)
                     if os.path.isfile(os.path.join(TEMP_WORKSPACE, f))]

            if files:
                st.markdown("### 📁 Available Files")

                for file in sorted(files):
                    file_path = os.path.join(TEMP_WORKSPACE, file)
                    file_size = os.path.getsize(file_path)

                    # Format file size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                    # Choose icon based on file extension
                    if file.endswith(('.usd', '.usda', '.usdc')):
                        icon = "🎭"  # USD/3D files
                    elif file.endswith(('.csv', '.tsv')):
                        icon = "📊"  # Data files
                    elif file.endswith(('.txt', '.log')):
                        icon = "📄"  # Text files
                    else:
                        icon = "📁"  # Generic file

                    st.markdown(f"{icon} **{file}** `({size_str})`")
            else:
                st.markdown("### 📁 Available Files")
                st.info("No files currently loaded in workspace")
        else:
            st.warning("⚠️ Workspace not initialized")

    except ImportError:
        st.error("Unable to access workspace information")
    except Exception as e:
        st.error(f"Error listing files: {e}")


def show_point_cloud_viewer():
    """Show the point cloud viewer permanently in the sidebar."""
    """Show the point cloud viewer permanently in the sidebar."""

    # Select dataset based on secret
    if is_mining_case_enabled():
        st.markdown("# Underground mine dataset ⚒")
        selected_dataset = "Mining (100k points)"
        csv_filename = "3D_point_cloud_GT-100k.csv"
    else:
        selected_dataset = "Indoor Room (sparse)"
        csv_filename = "indoor_room_labelled_sparse.csv"

    # Only show available files when indoor room dataset is selected
    if selected_dataset == "Indoor Room (sparse)":
        show_available_files()
        st.markdown("---")

    csv_path = os.path.join(os.getcwd(), "DATA", csv_filename)

    if os.path.exists(csv_path):
        # Use larger height for mining dataset, smaller for indoor room
        height = 600 if is_mining_case_enabled() else 450
        render_point_cloud_viewer(csv_path, height=height)
    else:
        st.warning(f"⚠️ Point cloud data not found: {csv_filename}")
        st.info("Make sure the DATA folder contains the selected dataset")
