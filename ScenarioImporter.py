import os
import json
from tkinter import filedialog


class ScenarioImporter:
    def __init__(self, app):
        self.app = app

    def import_graph(self):
        # Get the current working directory (project directory)
        project_directory = os.getcwd()

        # Open file dialog, defaulting to the project's root directory
        file_path = filedialog.askopenfilename(
            title="Select Graph File",
            initialdir=project_directory + "/scenarios",  # Set the initial directory to the project directory
            filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
        )
        if not file_path:
            return  # User canceled file selection

        with open(file_path, 'r') as file:
            graph_data = json.load(file)

        # Clear the current graph and canvas before importing
        self.app.clear_all()

        # Add processes and resources (including disponibilities for resources)
        for node_data in graph_data['nodes']:
            x = node_data.get('x', 0)  # Default to 0 if not provided
            y = node_data.get('y', 0)  # Default to 0 if not provided

            if node_data['type'] == 'P':
                self.app.p_counter = node_data['number']
                self.app.add_process(x, y)  # Adjust this method to accept x, y
            elif node_data['type'] == 'R':
                self.app.r_counter = node_data['number']
                self.app.add_resource_with_disponibilities(node_data['disponibilities'], x,
                                                                           y)  # Adjust this method to accept x, y

        # Add edges
        for edge_data in graph_data['edges']:
            # Accessing start_node and end_node correctly as dictionaries
            start_type = edge_data['start_node']['type']
            start_number = edge_data['start_node']['number']
            end_type = edge_data['end_node']['type']
            end_number = edge_data['end_node']['number']

            # Find the corresponding nodes by their type and number
            start_node = next(
                node for node in self.app.nodes if node.node_type == start_type and node.number == start_number)
            end_node = next(node for node in self.app.nodes if node.node_type == end_type and node.number == end_number)

            self.app.add_edge(start_node, end_node)
