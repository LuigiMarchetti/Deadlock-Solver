import os
import json
from tkinter import filedialog, messagebox


class ScenarioExporter:
    def __init__(self, app):
        self.app = app

    def export_graph(self):
        # Create list of nodes with their properties
        nodes = []
        for node in self.app.nodes:
            node_data = {
                "type": node.node_type,
                "number": node.number,
                "x": node.x,
                "y": node.y
            }
            if node.node_type == "R":
                node_data["disponibilities"] = node.disponibilities
            nodes.append(node_data)

        # Create list of edges with their properties
        edges = []
        for edge in self.app.edges:
            edge_data = {
                "start_node": {
                    "type": edge.start.node_type,
                    "number": edge.start.number
                },
                "end_node": {
                    "type": edge.end.node_type,
                    "number": edge.end.number
                }
            }
            edges.append(edge_data)

        # Create the graph data dictionary
        graph_data = {
            "nodes": nodes,
            "edges": edges
        }

        try:
            # Get the current working directory
            project_directory = os.getcwd()

            # Ensure scenarios directory exists
            scenarios_dir = os.path.join(project_directory, "scenarios")
            if not os.path.exists(scenarios_dir):
                os.makedirs(scenarios_dir)

            # Open file dialog for saving
            file_path = filedialog.asksaveasfilename(
                title="Save Graph File",
                initialdir=scenarios_dir,
                defaultextension=".json",
                filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
            )

            if not file_path:
                return # User canceled the save dialog

            # Save the graph data to the selected file
            with open(file_path, 'w') as file:
                json.dump(graph_data, file, indent=2)

            messagebox.showinfo("Success", "Graph saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save graph: {str(e)}")