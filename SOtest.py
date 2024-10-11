import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import math


class DeadlockApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()
        self.p_counter = 1
        self.r_counter = 1
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

        solve_button = tk.Button(self.root, text="Solve Deadlock", command=self.solve_deadlock)
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
            # Draw curved edge
            curve = 0.2 * (existing_edges - 1)
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            control_x = mid_x - (start_y - end_y) * curve
            control_y = mid_y + (start_x - end_x) * curve

            edge.line_id = self.canvas.create_line(start_x, start_y, control_x, control_y, end_x, end_y,
                                                   smooth=True, arrow=tk.LAST, splinesteps=32)
        else:
            # Draw straight edge
            edge.line_id = self.canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.LAST)

    def redraw_edges(self):
        for edge in self.edges:
            self.canvas.delete(edge.line_id)
        for edge in self.edges:
            self.draw_edge(edge)

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
            self.redraw_edges()

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

    def solve_deadlock(self):
        graph = self.create_graph()
        is_deadlock, cycle = self.detect_deadlock(graph)
        if is_deadlock:
            self.highlight_deadlock_cycle(cycle)
            messagebox.showinfo("Deadlock Detected", f"DEADLOCK!!! Cycle detected: {' -> '.join(cycle)}")
        else:
            messagebox.showinfo("No Deadlock", "No deadlock detected in the current configuration.")

    def create_graph(self):
        graph = {}
        for node in self.nodes:
            graph[f'{node.node_type}{node.number}'] = {'type': node.node_type, 'edges': []}
            if node.node_type == 'R':
                graph[f'{node.node_type}{node.number}']['disponibilities'] = node.disponibilities

        for edge in self.edges:
            start = f"{edge.start.node_type}{edge.start.number}"
            end = f"{edge.end.node_type}{edge.end.number}"
            graph[start]['edges'].append(end)

        return graph

    def detect_deadlock(self, graph):
        def dfs(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph[node]['edges']:
                if neighbor not in visited:
                    cycle = dfs(neighbor, visited, rec_stack)
                    if cycle:
                        return [node] + cycle
                elif neighbor in rec_stack:
                    return [node, neighbor]

            rec_stack.remove(node)
            return None

        visited = set()
        rec_stack = set()

        for node in graph:
            if node not in visited:
                cycle = dfs(node, visited, rec_stack)
                if cycle:
                    return True, cycle

        return False, None

    def highlight_deadlock_cycle(self, cycle):
        for i in range(len(cycle) - 1):
            start = cycle[i]
            end = cycle[i + 1]
            edge = next(edge for edge in self.edges
                        if f"{edge.start.node_type}{edge.start.number}" == start
                        and f"{edge.end.node_type}{edge.end.number}" == end)
            self.canvas.itemconfig(edge.line_id, fill='red', width=2)

    def clear_all(self):
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()
        self.p_counter = 1
        self.r_counter = 1
        self.selected_node = None
        self.edge_start = None


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