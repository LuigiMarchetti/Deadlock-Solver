import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import math

from ScenarioImporter import ScenarioImporter


class DeadlockApp:
    def __init__(self, root):
        self.root = root
        self.importer = ScenarioImporter(self)  # Create instance of ScenarioImporter
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()
        self.root.title("Deadlock Analyzer")
        self.root.resizable(False, False)
        self.root.attributes("-fullscreen", False)
        self.p_counter = 0
        self.r_counter = 0
        self.nodes = []
        self.edges = []
        self.dot_ids = []
        self.dot_positions = []  # List of (x, y) tuples for each dot
        self.occupied_dots = []  # List of booleans, True if dot is occupied
        self.selected_node = None
        self.edge_start = None
        self.setup_ui()
        self.add_attribution()
        self.canvas.bind("<Button-1>", self.on_click) # Event listener
        self.canvas.bind("<B1-Motion>", self.on_drag) # Event listener
        self.canvas.bind("<Button-3>", self.change_disponibilities) # Event listener

    def setup_ui(self):
        import_button = tk.Button(self.root, text="Import Graph", command=self.importer.import_graph)
        import_button.pack(side=tk.RIGHT)

        add_p_button = tk.Button(self.root, text="Add Process (P)", command=self.add_process)
        add_p_button.pack(side=tk.LEFT)

        add_r_button = tk.Button(self.root, text="Add Resource (R)", command=self.add_resource)
        add_r_button.pack(side=tk.LEFT)

        remove_button = tk.Button(self.root, text="Remove Node", command=self.remove_node)
        remove_button.pack(side=tk.LEFT)

        add_edge_button = tk.Button(self.root, text="Add Edge", command=self.start_add_edge)
        add_edge_button.pack(side=tk.LEFT)

        solve_button = tk.Button(self.root, text="Avoid Deadlock", command=self.avoid_deadlock)
        solve_button.pack(side=tk.LEFT)

        clear_button = tk.Button(self.root, text="Clear All", command=self.clear_all)
        clear_button.pack(side=tk.LEFT)

    def add_attribution(self):
        # anchor="e" aligns text to the right (east)
        self.canvas.create_text(780, 20, text="By Luigi G. Marchetti", anchor="e", font=("Arial", 10))

    def add_process(self, x=None, y=None):
        if not x or not y: # if x or y don't have value
            x, y = self.get_random_position()
        node_id = self.canvas.create_rectangle(x - 25, y - 25, x + 25, y + 25, fill="white", outline="black")
        text_id = self.canvas.create_text(x, y, text=f"P{self.p_counter}")

        node = Node(node_id, text_id, "P", self.p_counter, x, y)
        self.nodes.append(node)

        self.p_counter += 1

    def add_resource(self):
        x, y = self.get_random_position()
        node_id = self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill="white", outline="black")
        text_id = self.canvas.create_text(x, y, text=f"R{self.r_counter}")

        disponibilities = simpledialog.askinteger("Resource Disponibilities",
                                                  f"Enter number of disponibilities for R{self.r_counter}:",
                                                  minvalue=1, maxvalue=10)

        if disponibilities is None:  # User canceled the dialog
            self.canvas.delete(node_id)
            self.canvas.delete(text_id)
            return

        node = Node(node_id, text_id, "R", self.r_counter, x, y, disponibilities)
        self.nodes.append(node)
        self.draw_disponibilities(node)

        self.r_counter += 1

    def get_random_position(self):
        return random.randint(50, 750), random.randint(50, 550)

    def draw_disponibilities(self, node):
        x, y = node.x, node.y
        node.dot_positions = []
        node.occupied_dots = [False] * node.disponibilities
        for i in range(node.disponibilities):
            angle = 2 * math.pi * i / node.disponibilities
            dot_x = x + 20 * math.cos(angle)
            dot_y = y + 20 * math.sin(angle)
            dot_id = self.canvas.create_oval(dot_x - 3, dot_y - 3, dot_x + 3, dot_y + 3, fill="black")
            node.dot_ids.append(dot_id)
            node.dot_positions.append((dot_x, dot_y))

    def change_disponibilities(self, event):
        # Only is enabled if there are no edges in canvas
        if len(self.edges) == 0:
            node = self.find_node_at_position(event.x, event.y)
            if node and node.node_type == "R":
                new_disponibilities = simpledialog.askinteger("Change Disponibilities",
                                                              f"Enter new number of disponibilities for R{node.number}:",
                                                              minvalue=1, maxvalue=10)
                if new_disponibilities is not None:
                    node.disponibilities = new_disponibilities
                    for dot_id in node.dot_ids:
                        self.canvas.delete(dot_id)
                    node.dot_ids.clear()
                    self.draw_disponibilities(node)

    def add_resource_with_disponibilities(self, disponibilities, x=None, y=None):
        if not x or not y:  # if x or y don't have value
            x, y = self.get_random_position()
        node_id = self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill="white", outline="black")
        text_id = self.canvas.create_text(x, y, text=f"R{self.r_counter}")

        node = Node(node_id, text_id, "R", self.r_counter, x, y, disponibilities)
        self.nodes.append(node)
        self.draw_disponibilities(node)

        self.r_counter += 1

    def remove_node(self):
        if self.selected_node:
            self.canvas.delete(self.selected_node.id)
            self.canvas.delete(self.selected_node.text_id)
            for dot_id in self.selected_node.dot_ids:
                self.canvas.delete(dot_id)
            self.nodes.remove(self.selected_node)
            self.remove_connected_edges(self.selected_node)
            self.selected_node = None
            self.recalculate_indices()

    def remove_connected_edges(self, node):
        edges_to_remove = [edge for edge in self.edges if edge.start == node or edge.end == node]

        # Delete the graphical representation of the edges from the canvas
        for edge in edges_to_remove:
            self.canvas.delete(edge.line_id)

        # Remove the edges from the edges list
        self.edges = [edge for edge in self.edges if edge.start != node and edge.end != node]

        self.redraw_edges()

    def recalculate_indices(self):
        p_counter = 0
        r_counter = 0
        for node in self.nodes:
            if node.node_type == "P":
                node.number = p_counter
                self.canvas.itemconfig(node.text_id, text=f"P{p_counter}")
                p_counter += 1
            else:
                node.number = r_counter
                self.canvas.itemconfig(node.text_id, text=f"R{r_counter}")
                r_counter += 1
        self.p_counter = p_counter
        self.r_counter = r_counter

    def start_add_edge(self):
        self.canvas.bind("<Button-1>", self.on_edge_click)

    def on_edge_click(self, event):
        self.selected_node = None # cleans selected node
        clicked_node = self.find_node_at_position(event.x, event.y)
        if clicked_node:
            if not self.edge_start:
                self.edge_start = clicked_node
            else:
                self.add_edge(self.edge_start, clicked_node)
                self.edge_start = None
                self.canvas.bind("<Button-1>", self.on_click)

    def add_edge(self, start, end):
        if start.node_type == "R" and end.node_type == "P":
            available_dot = next((i for i, occupied in enumerate(start.occupied_dots) if not occupied), None)
            if available_dot is not None:
                edge = Edge(start, end, dot_index=available_dot)
                self.edges.append(edge)
                self.draw_edge(edge, start, end)
                start.occupied_dots[available_dot] = True
            else:
                messagebox.showerror("Error", "No available resources.")
        elif start.node_type == "P" and end.node_type == "R":
            edge = Edge(start, end)
            self.edges.append(edge)
            self.draw_edge(edge, start, end)
        else:
            messagebox.showerror("Error", "Invalid edge connection.")

    def draw_edge(self, edge, start, end):
        if start.node_type == "R":
            # For edges starting from a resource, use the dot position
            start_x, start_y = self.get_dot_position(start, edge.dot_index)
            end_x, end_y = self.get_border_point(end, start.x, start.y)
        else:
            # For edges starting from a process, use border points for both ends
            start_x, start_y = self.get_border_point(start, end.x, end.y)
            end_x, end_y = self.get_border_point(end, start.x, start.y)

        # Count existing edges between these nodes
        existing_edges = sum(1 for e in self.edges if
                             e.start.node_type == "P" and
                             (e.start == edge.start and e.end == edge.end))

        if start.node_type == "P" and existing_edges > 1:
            # Draw curved edge
            curve = 0.2 * (existing_edges - 1)
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            control_x = mid_x - (start_y - end_y) * curve
            control_y = mid_y + (start_x - end_x) * curve

            # Creates a curved (smooth) line with 32 intermediate points and an arrow at the end of it
            edge.line_id = self.canvas.create_line(start_x, start_y, control_x, control_y, end_x, end_y,
                                                   smooth=True, arrow=tk.LAST, splinesteps=32)
        else:
            # Draw straight edge with an arrow at the end of it
            edge.line_id = self.canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.LAST)

    def get_dot_position(self, node, dot_index):
        """Retrieve the position of the specified dot for a given node."""
        if dot_index is not None and 0 <= dot_index < len(node.dot_positions):
            return node.dot_positions[dot_index]
        return node.x, node.y  # Fallback to the node's center if no dot is specified

    def get_border_point(self, node, x2, y2):
        """Calculate the point on the border of a node's boundary where the edge should connect."""
        x1, y1 = node.x, node.y
        dx = x2 - x1
        dy = y2 - y1
        if node.node_type == "P":  # For processes (rectangles)
            half_width = 25  # Half the size of the rectangle
            half_height = 25  # Half the size of the rectangle
            # Find the largest scaling factor for either the x or y direction
            scale = min(half_width / abs(dx), half_height / abs(dy)) if dx != 0 and dy != 0 else 1
            return x1 + dx * scale, y1 + dy * scale
        elif node.node_type == "R":  # For resources (circles)
            radius = 25  # Radius of the circle
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist == 0:  # Prevent division by zero if nodes overlap
                return x1, y1
            scale = radius / dist
            return x1 + dx * scale, y1 + dy * scale

    def redraw_edges(self):
        for edge in self.edges:
            self.update_edge_position(edge)

    def update_edge_position(self, edge):
        if edge.start.node_type == "R":
            # For edges starting from a resource, use the dot position
            start_x, start_y = self.get_dot_position(edge.start, edge.dot_index)
            end_x, end_y = self.get_border_point(edge.end, edge.start.x, edge.start.y)

            self.canvas.coords(edge.line_id, start_x, start_y, end_x, end_y)
            self.canvas.itemconfig(edge.line_id, smooth=False)

            return
        else:
            # For edges starting from a process, use border points for both ends
            start_x, start_y = self.get_border_point(edge.start, edge.end.x, edge.end.y)
            end_x, end_y = self.get_border_point(edge.end, edge.start.x, edge.start.y)

        # Count existing edges between these nodes
        existing_edges = [e for e in self.edges if
                          e.start.node_type == "P" and
                          (e.start == edge.start and e.end == edge.end)]
        edge_count = len(existing_edges)

        if edge_count == 1:
            # For single edge, draw a straight line
            self.canvas.coords(edge.line_id, start_x, start_y, end_x, end_y)
            self.canvas.itemconfig(edge.line_id, smooth=False)
        else:
            # For multiple edges, calculate the curvature
            edge_index = existing_edges.index(edge)
            curve_factor = 0.2 * (edge_index - (edge_count - 1) / 2)

            # Calculate the midpoint and perpendicular vector
            mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
            dx, dy = end_x - start_x, end_y - start_y
            length = math.sqrt(dx * dx + dy * dy)
            if length == 0:  # Prevent division by zero
                return
            perpendicular_x, perpendicular_y = -dy / length, dx / length

            # Calculate control point
            control_x = mid_x + perpendicular_x * curve_factor * length
            control_y = mid_y + perpendicular_y * curve_factor * length

            # Update the edge to be a curved line
            self.canvas.coords(edge.line_id, start_x, start_y, control_x, control_y, end_x, end_y)
            self.canvas.itemconfig(edge.line_id, smooth=True, splinesteps=32)

    def on_click(self, event):
        self.selected_node = self.find_node_at_position(event.x, event.y)

    def on_drag(self, event):
        if self.selected_node:
            dx = event.x - self.selected_node.x
            dy = event.y - self.selected_node.y
            self.canvas.move(self.selected_node.id, dx, dy)
            self.canvas.move(self.selected_node.text_id, dx, dy)

            # Update the node's position
            self.selected_node.x = event.x
            self.selected_node.y = event.y

            # Update edge positions if the node is a resource
            if self.selected_node.node_type == "R":
                self.update_node_disponibilities(self.selected_node)

            # Redraw edges connected to the moved node
            for edge in self.edges:
                if edge.start == self.selected_node or edge.end == self.selected_node:
                    self.update_edge_position(edge)

    def update_node_disponibilities(self, node):
        if node.node_type == "R":
            for dot_id in node.dot_ids:
                self.canvas.delete(dot_id)
            node.dot_ids.clear()
            node.dot_positions.clear()
            self.draw_disponibilities(node)
            # Update edge positions
            for edge in self.edges:
                if edge.start == node:
                    self.update_edge_position(edge)

    def find_node_at_position(self, x, y):
        for node in self.nodes:
            # Ensures that the user can click anywhere in the circle
            if (node.x - 25 <= x <= node.x + 25) and (node.y - 25 <= y <= node.y + 25):
                return node
        return None

    def clear_all(self):
        # Delete only nodes and edges, not the entire canvas
        for node in self.nodes:
            self.canvas.delete(node.id)
            self.canvas.delete(node.text_id)
            for dot_id in node.dot_ids:
                self.canvas.delete(dot_id)

        for edge in self.edges:
            self.canvas.delete(edge.line_id)

        self.nodes.clear()
        self.edges.clear()
        self.p_counter = 0
        self.r_counter = 0
        self.selected_node = None
        self.edge_start = None

    def get_allocated_resources(self, i, j):
        process_number = i
        resource_number = j
        allocated_resources = 0

        for edge in self.edges:
            # When the edge starts in the Rj and ends in Pi, allocatedResources + 1
            if (edge.start.node_type == "R" and edge.start.number == resource_number)\
                and (edge.end.node_type == "P" and edge.end.number == process_number):
                allocated_resources += 1

        return allocated_resources

    def get_needed_resources(self, i, j):
        process_number = i
        resource_number = j
        needed_resources = 0

        for edge in self.edges:
            # When the edge starts in the Pi and ends in Rj, maxResources + 1
            if (edge.start.node_type == "P" and edge.start.number == process_number)\
                and (edge.end.node_type == "R" and edge.end.number == resource_number):
                needed_resources += 1

        return needed_resources

    def avoid_deadlock(self):
        resources = 0
        processes = 0
        for node in self.nodes:
            if node.node_type == "R":
                resources += 1
            else:
                processes += 1

        allocated_resources = {f'P{i}': [0] * resources for i in range(processes)}
        needed_resources = {f'P{i}': [0] * resources for i in range(processes)}

        for i in range(processes):
            for j in range(resources):
                allocated_resources[f'P{i}'][j] = self.get_allocated_resources(i, j)
                needed_resources[f'P{i}'][j] = self.get_needed_resources(i, j)

        print("\nAllocated Resources Table:")
        for proc, res in allocated_resources.items():
            print(f"{proc}: {res}")
        print("\nNeeded Resources Table:")
        for proc, res in needed_resources.items():
            print(f"{proc}: {res}")

        total_allocated_resources = [0 for _ in range(resources)]
        for i in range(processes):
            for j in range(resources):
                total_allocated_resources[j] += allocated_resources[f'P{i}'][j]
        print("\nTotal Allocated Resources: " + str(total_allocated_resources))

        total_available_resources = [0] * resources
        for node in self.nodes:
            if node.disponibilities > 0:
                real_disponibility = node.disponibilities - total_allocated_resources[node.number]
                total_available_resources[node.number] += real_disponibility
        print("Total Available Resources: " + str(total_available_resources))

        total_resources = [0] * resources
        for node in self.nodes:
            if node.disponibilities > 0:
                total_resources[node.number] += node.disponibilities
        print("Total Resources: " + str(total_resources))

        steps = []
        while allocated_resources:
            for process in list(allocated_resources.keys()):
                count = 0
                new_total_available_resources = total_available_resources.copy()
                for j in range(resources):
                    if total_available_resources[j] >= needed_resources[process][j]:
                        new_total_available_resources[j] += allocated_resources[process][j]
                        count += 1
                if count == resources:
                    total_available_resources = new_total_available_resources
                    del allocated_resources[process]
                    del needed_resources[process]
                    steps.append(int(process[1:]))  # Converts using substring the 'P0', 'P1', etc. to 0, 1, etc.
                    break
            else:
                # If we've gone through all processes without finding a safe one, exit the loop
                break

        self.animate_step(steps)

    def animate_step(self, steps):
        if not steps:
            self.show_result_message()
            return

        step = steps.pop(0) # Gets the first element and remove it from the list

        edges_to_remove = []
        for edge in self.edges:
            if (edge.start.node_type == 'P' and edge.start.number == step) or (edge.end.node_type == 'P' and edge.end.number == step):
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            self.canvas.itemconfig(edge.line_id, fill='red', width=2)

        self.root.after(2000, self.remove_edges_and_continue, edges_to_remove, steps)

    def remove_edges_and_continue(self, edges_to_remove, remaining_steps):
        for edge in edges_to_remove:
            self.canvas.delete(edge.line_id)
            self.edges.remove(edge)

        self.animate_step(remaining_steps)

    def show_result_message(self):
        if any(self.edges):
            messagebox.showinfo("DEADLOCK!!!", "Deadlock could not be avoided.")
        else:
            messagebox.showinfo("Resolution Complete", "Deadlock successfully avoided!")

class Node:
    def __init__(self, id, text_id, node_type, number, x, y, disponibilities=0):
        self.id = id
        self.text_id = text_id
        self.node_type = node_type
        self.number = number
        self.x = x
        self.y = y
        self.disponibilities = disponibilities
        self.dot_ids = []


class Edge:
    def __init__(self, start, end, dot_index=None):
        self.start = start
        self.end = end
        self.dot_index = dot_index  # Store which dot the edge starts from (if applicable)
        self.line_id = None


if __name__ == "__main__": # Only runs the app when the user runs this class
    root = tk.Tk() # Creates the Tkinter's GUI (window)
    app = DeadlockApp(root)
    root.mainloop() # Start event loop (event listening)