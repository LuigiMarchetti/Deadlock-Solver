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

    def clear_all(self):
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()
        self.p_counter = 1
        self.r_counter = 1
        self.selected_node = None
        self.edge_start = None

    def getAlocatedResources(self, i, j):
        processNumber = i + 1
        resourceNumber = j + 1
        allocatedResources = 0

        for edge in self.edges:
            # When the edge starts in the Rj and ends in Pi, allocatedResources + 1
            if (edge.start.node_type == "R" and edge.start.number == resourceNumber)\
                and (edge.end.node_type == "P" and edge.end.number == processNumber):
                allocatedResources += 1

        return allocatedResources

    def getMaxResources(self, i, j):
        processNumber = i + 1
        resourceNumber = j + 1
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

        print(allocated_resources)
        print(needed_resources)

        for i in range(processes):
            for j in range(resources):
                allocated_resources[f'P{i}'][j] = self.getAlocatedResources(i, j)
                needed_resources[f'P{i}'][j] = self.getMaxResources(i, j)

        print("\n")
        for process, resources in allocated_resources.items():
            print(f"{process}: {resources}")
        print("")
        for process, resources in needed_resources.items():
            print(f"{process}: {resources}")

        total_allocated_resources = [0 for _ in range(resources)]
        max_resources = [0 for _ in range(resources)]
        for i in range(processes):
            for j in range(resources):
                total_allocated_resources[j] += allocated_resources[f'P{i}'][j]
                max_resources[j] += needed_resources[f'P{i}'][j]
        print("Total Allocated Resources: " + str(total_allocated_resources))

        total_available_resources = [0] * resources
        for node in self.nodes:
            if node.disponibilities > 0:
                real_disponibility = node.disponibilities - total_allocated_resources[node.number - 1] - max_resources[
                    node.number - 1]
                total_available_resources[node.number - 1] += real_disponibility
        print("Total Available Resources: " + str(total_available_resources))

        total_resources = [0] * resources
        for node in self.nodes:
            if node.disponibilities > 0:
                total_resources[node.number - 1] += node.disponibilities
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






        graph = self.create_graph()
        processes, resources = self.separate_processes_resources(graph)

        # Initialize data structures for Banker's Algorithm
        available = {r: graph[r]['disponibilities'] for r in resources}
        max_need = {p: {r: 0 for r in resources} for p in processes}
        allocation = {p: {r: 0 for r in resources} for p in processes}
        need = {p: {r: 0 for r in resources} for p in processes}

        # Populate max_need and allocation
        for p in processes:
            for r in graph[p]['edges']:
                max_need[p][r] = max_need[p].get(r, 0) + 1
                allocation[p][r] = allocation[p].get(r, 0) + 1
                available[r] -= 1

        # Calculate need
        for p in processes:
            for r in resources:
                need[p][r] = max_need[p][r] - allocation[p][r]

        steps = self.bankers_algorithm(processes, resources, available, max_need, allocation, need)

        if not steps:
            # If Banker's Algorithm couldn't find a solution, try to remove possible edges
            steps = self.remove_possible_edges(graph)

        self.animate_resolution(steps)

    def separate_processes_resources(self, graph):
        processes = [node for node, data in graph.items() if data['type'] == 'P']
        resources = [node for node, data in graph.items() if data['type'] == 'R']
        return processes, resources

    def bankers_algorithm(self, processes, resources, available, max_need, allocation, need):
        steps = []
        work = available.copy()
        finish = {p: False for p in processes}

        while True:
            found = False
            for p in processes:
                if not finish[p] and all(need[p][r] <= work[r] for r in resources):
                    # Process can complete
                    for r in resources:
                        work[r] += allocation[p][r]
                    finish[p] = True
                    found = True
                    # Add steps to remove edges
                    for r in resources:
                        if allocation[p][r] > 0:
                            steps.append((p, r))

            if not found:
                break

        if all(finish.values()):
            return steps
        return None

    def remove_possible_edges(self, graph):
        removed_edges = []
        for p in [node for node, data in graph.items() if data['type'] == 'P']:
            for r in list(graph[p]['edges']):  # Use list() to allow modification during iteration
                if graph[r]['disponibilities'] > 0:
                    graph[p]['edges'].remove(r)
                    graph[r]['disponibilities'] += 1
                    removed_edges.append((p, r))
        return removed_edges

    def animate_resolution(self, steps):
        if not steps:
            messagebox.showinfo("Deadlock", "It's a deadlock!")
            return

        def animate_step(step_index):
            if step_index < len(steps):
                process, resource = steps[step_index]
                edge_to_remove = next((edge for edge in self.edges
                                       if f"{edge.start.node_type}{edge.start.number}" == process
                                       and f"{edge.end.node_type}{edge.end.number}" == resource), None)
                if edge_to_remove:
                    self.canvas.itemconfig(edge_to_remove.line_id, fill='red', width=2)
                    self.root.after(2000, lambda: self.remove_edge(edge_to_remove))
                    self.root.after(2000, lambda: animate_step(step_index + 1))
                else:
                    animate_step(step_index + 1)
            else:
                self.show_resolution_result()

        animate_step(0)

    def show_resolution_result(self):
        if any(edge.start.node_type == 'P' for edge in self.edges):
            messagebox.showinfo("Partial Resolution", "Some edges were removed, but deadlock may still occur.")
        else:
            messagebox.showinfo("Resolution Complete", "Deadlock successfully avoided!")

    def remove_edge(self, edge):
        self.canvas.delete(edge.line_id)
        self.edges.remove(edge)
        self.update_resource_disponibilities(edge.end)

    def update_resource_disponibilities(self, resource_node):
        if resource_node.node_type == 'R':
            resource_node.disponibilities += 1
            self.canvas.delete(resource_node.text_id)
            resource_node.text_id = self.canvas.create_text(resource_node.x, resource_node.y,
                                                            text=f"R{resource_node.number}\n({resource_node.disponibilities})")

    def create_graph(self):
        graph = {}
        for node in self.nodes:
            graph[f'{node.node_type}{node.number}'] = {
                'type': node.node_type,
                'edges': [],
                'disponibilities': node.disponibilities if node.node_type == 'R' else 0
            }

        for edge in self.edges:
            start = f"{edge.start.node_type}{edge.start.number}"
            end = f"{edge.end.node_type}{edge.end.number}"
            graph[start]['edges'].append(end)

        return graph

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