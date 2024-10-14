import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import math

class DeadlockApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()
        self.root.title("Deadlock Analyzer")
        self.root.resizable(False, False)
        self.root.attributes("-fullscreen", False)
        self.p_counter = 0
        self.r_counter = 0
        self.nodes = []
        self.edges = []
        self.selected_node = None
        self.edge_start = None
        self.setup_ui()
        self.add_attribution()
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def setup_ui(self):
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
        self.canvas.create_text(780, 20, text="By Luigi G. Marchetti", anchor="e", font=("Arial", 10))

    def add_process(self):
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
        for i in range(node.disponibilities):
            angle = 2 * math.pi * i / node.disponibilities
            dot_x = x + 20 * math.cos(angle)
            dot_y = y + 20 * math.sin(angle)
            dot_id = self.canvas.create_oval(dot_x - 3, dot_y - 3, dot_x + 3, dot_y + 3, fill="black")
            node.dot_ids.append(dot_id)

    def remove_node(self):
        if self.selected_node:
            self.canvas.delete(self.selected_node.id)
            self.canvas.delete(self.selected_node.text_id)
            for dot_id in self.selected_node.dot_ids:
                self.canvas.delete(dot_id)
            self.nodes.remove(self.selected_node)
            self.remove_connected_edges(self.selected_node)
            self.selected_node = None

    def remove_connected_edges(self, node):
        edges_to_remove = [edge for edge in self.edges if edge.start == node or edge.end == node]

        # Delete the graphical representation of the edges from the canvas
        for edge in edges_to_remove:
            self.canvas.delete(edge.line_id)

        # Remove the edges from the edges list
        self.edges = [edge for edge in self.edges if edge.start != node and edge.end != node]

        self.redraw_edges()

    def start_add_edge(self):
        self.canvas.bind("<Button-1>", self.on_edge_click)

    def on_edge_click(self, event):
        clicked_node = self.find_node_at_position(event.x, event.y)
        if clicked_node:
            if not self.edge_start:
                self.edge_start = clicked_node
            else:
                self.add_edge(self.edge_start, clicked_node)
                self.edge_start = None
                self.canvas.bind("<Button-1>", self.on_click)

    def add_edge(self, start, end):
        self.selected_node = None
        if (start.node_type == "P" and end.node_type == "R") or (start.node_type == "R" and end.node_type == "P"):
            edge = Edge(start, end)
            self.edges.append(edge)
            self.draw_edge(edge)

    def draw_edge(self, edge):
        start_x, start_y = edge.start.x, edge.start.y
        end_x, end_y = edge.end.x, edge.end.y

        # Count existing edges between these nodes
        existing_edges = sum(1 for e in self.edges if
                             (e.start == edge.start and e.end == edge.end) or
                             (e.start == edge.end and e.end == edge.start))

        if existing_edges > 1:
            # Draw curved edge if multiple edges exist between the same nodes
            curve = 0.2 * (existing_edges - 1)
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            control_x = mid_x - (start_y - end_y) * curve
            control_y = mid_y + (start_x - end_x) * curve

            if edge.line_id:
                self.canvas.coords(edge.line_id, start_x, start_y, control_x, control_y, end_x, end_y)
            else:
                edge.line_id = self.canvas.create_line(start_x, start_y, control_x, control_y, end_x, end_y,
                                                       smooth=True, arrow=tk.LAST, splinesteps=32)
        else:
            # Draw straight edge
            if edge.line_id:
                self.canvas.coords(edge.line_id, start_x, start_y, end_x, end_y)
            else:
                edge.line_id = self.canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.LAST)

    def redraw_edges(self):
        for edge in self.edges:
            self.update_edge_position(edge)

    def update_edge_position(self, edge):
        start_x, start_y = edge.start.x, edge.start.y
        end_x, end_y = edge.end.x, edge.end.y

        # Count existing edges between these nodes to determine if curvature is needed
        existing_edges = sum(1 for e in self.edges if
                             (e.start == edge.start and e.end == edge.end) or
                             (e.start == edge.end and e.end == edge.start))

        if existing_edges > 1:
            # Draw curved edge if multiple edges exist between the same nodes
            curve = 0.2 * (existing_edges - 1)
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            control_x = mid_x - (start_y - end_y) * curve
            control_y = mid_y + (start_x - end_x) * curve
            self.canvas.coords(edge.line_id, start_x, start_y, control_x, control_y, end_x, end_y)
        else:
            # Draw straight edge
            self.canvas.coords(edge.line_id, start_x, start_y, end_x, end_y)

    def on_click(self, event):
        self.selected_node = self.find_node_at_position(event.x, event.y)

    def on_drag(self, event):
        if self.selected_node:
            dx = event.x - self.selected_node.x
            dy = event.y - self.selected_node.y
            self.canvas.move(self.selected_node.id, dx, dy)
            self.canvas.move(self.selected_node.text_id, dx, dy)
            self.selected_node.x = event.x
            self.selected_node.y = event.y
            self.update_node_disponibilities(self.selected_node)

            # Update edge positions instead of redrawing
            for edge in self.edges:
                if edge.start == self.selected_node or edge.end == self.selected_node:
                    self.update_edge_position(edge)

    def update_node_disponibilities(self, node):
        if node.node_type == "R":
            for dot_id in node.dot_ids:
                self.canvas.delete(dot_id)
            node.dot_ids.clear()
            self.draw_disponibilities(node)

    def find_node_at_position(self, x, y):
        for node in self.nodes:
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

    def getAlocatedResources(self, i, j):
        processNumber = i
        resourceNumber = j
        allocatedResources = 0

        for edge in self.edges:
            # When the edge starts in the Rj and ends in Pi, allocatedResources + 1
            if (edge.start.node_type == "R" and edge.start.number == resourceNumber)\
                and (edge.end.node_type == "P" and edge.end.number == processNumber):
                allocatedResources += 1

        return allocatedResources

    def getMaxResources(self, i, j):
        processNumber = i
        resourceNumber = j
        maxResources = 0

        for edge in self.edges:
            # When the edge starts in the Pi and ends in Rj, maxResources + 1
            if (edge.start.node_type == "P" and edge.start.number == processNumber)\
                and (edge.end.node_type == "R" and edge.end.number == resourceNumber):
                maxResources += 1

        return maxResources

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
                allocated_resources[f'P{i}'][j] = self.getAlocatedResources(i, j)
                needed_resources[f'P{i}'][j] = self.getMaxResources(i, j)

        print("\nAllocated Resources Table:")
        for proc, res in allocated_resources.items():
            print(f"{proc}: {res}")
        print("\nNeeded Resources Table:")
        for proc, res in needed_resources.items():
            print(f"{proc}: {res}")

        total_allocated_resources = [0 for _ in range(resources)]
        max_resources = [0 for _ in range(resources)]
        for i in range(processes):
            for j in range(resources):
                total_allocated_resources[j] += allocated_resources[f'P{i}'][j]
                max_resources[j] += needed_resources[f'P{i}'][j]
        print("\nTotal Allocated Resources: " + str(total_allocated_resources))

        total_available_resources = [0] * resources
        for node in self.nodes:
            if node.disponibilities > 0:
                real_disponibility = node.disponibilities - total_allocated_resources[node.number] #- max_resources[node.number]
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
                    steps.append(int(process[1:]))  # Convert 'P0', 'P1', etc. to 0, 1, etc.
                    break
            else:
                # If we've gone through all processes without finding a safe one, exit the loop
                break

        self.animate_step(steps)

    def animate_step(self, steps):
        if not steps:
            self.show_result_message()
            return

        step = steps.pop(0)
        edges_to_remove = [edge for edge in self.edges if edge.start.number == step or edge.end.number == step]

        for edge in edges_to_remove:
            self.canvas.itemconfig(edge.line_id, fill='red', width=2)

        self.root.after(2000, self.remove_edges_and_continue, edges_to_remove, steps)

    def remove_edges_and_continue(self, edges_to_remove, remaining_steps):
        for edge in edges_to_remove:
            self.canvas.delete(edge.line_id)
            self.edges.remove(edge)
            if edge.end.node_type == 'R':
                self.update_resource_disponibilities(edge.end)

        self.animate_step(remaining_steps)

    def show_result_message(self):
        if any(self.edges):
            messagebox.showinfo("DEADLOCK!!!", "Deadlock could not be avoided.")
        else:
            messagebox.showinfo("Resolution Complete", "Deadlock successfully avoided!")

    def update_resource_disponibilities(self, resource_node):
        if resource_node.node_type == 'R':
            resource_node.disponibilities += 1
            self.canvas.delete(resource_node.text_id)
            resource_node.text_id = self.canvas.create_text(resource_node.x, resource_node.y,
                                                            text = f"R{resource_node.number}\n({resource_node.disponibilities})")


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
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.line_id = None


if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockApp(root)
    root.mainloop()