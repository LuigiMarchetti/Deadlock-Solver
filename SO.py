import tkinter as tk
from tkinter import messagebox
import random

# Helper class to represent a node (either a Process or a Resource)
class Node:
    def __init__(self, canvas, x, y, text):
        self.canvas = canvas
        self.id = self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="lightblue", tags="node")
        self.text_id = self.canvas.create_text(x, y, text=text)
        self.x = x
        self.y = y
        self.text = text
        self.edges = []

    def move(self, x, y):
        self.canvas.move(self.id, x - self.x, y - self.y)
        self.canvas.move(self.text_id, x - self.x, y - self.y)
        self.x = x
        self.y = y
        for edge in self.edges:
            edge.update()

class Edge:
    def __init__(self, canvas, from_node, to_node):
        self.canvas = canvas
        self.from_node = from_node
        self.to_node = to_node
        self.line_id = self.canvas.create_line(from_node.x, from_node.y, to_node.x, to_node.y, arrow=tk.LAST)
        from_node.edges.append(self)
        to_node.edges.append(self)

    def update(self):
        self.canvas.coords(self.line_id, self.from_node.x, self.from_node.y, self.to_node.x, self.to_node.y)

class DeadlockApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack()

        self.nodes = []
        self.edges = []
        self.selected_node = None

        # Buttons for adding/removing processes/resources and resolving deadlock
        control_frame = tk.Frame(root)
        control_frame.pack()

        tk.Button(control_frame, text="Add Process", command=self.add_process).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Add Resource", command=self.add_resource).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Remove", command=self.remove_selected).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Resolve Deadlock", command=self.resolve_deadlock).pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def add_process(self):
        # Add a process (P) at a random location
        x, y = random.randint(50, 550), random.randint(50, 350)
        node = Node(self.canvas, x, y, text=f'P{len(self.nodes)+1}')
        self.nodes.append(node)

    def add_resource(self):
        # Add a resource (R) at a random location
        x, y = random.randint(50, 550), random.randint(50, 350)
        node = Node(self.canvas, x, y, text=f'R{len(self.nodes)+1}')
        self.nodes.append(node)

    def remove_selected(self):
        if self.selected_node:
            for edge in self.selected_node.edges:
                self.canvas.delete(edge.line_id)
            self.nodes.remove(self.selected_node)
            self.canvas.delete(self.selected_node.id)
            self.canvas.delete(self.selected_node.text_id)
            self.selected_node = None
            if len([n for n in self.nodes if n.text.startswith("P")]) == 0:
                messagebox.showerror("Error", "You cannot remove all processes!")

    def on_click(self, event):
        closest_item = self.canvas.find_closest(event.x, event.y)
        if closest_item:
            clicked_item = closest_item[0]
            for node in self.nodes:
                if clicked_item == node.id or clicked_item == node.text_id:
                    self.selected_node = node
                    return
        self.selected_node = None  # Deselect if nothing is clicked

    def on_drag(self, event):
        if self.selected_node:
            self.selected_node.move(event.x, event.y)

    def resolve_deadlock(self):
        # Simple deadlock detection (detects circular dependencies)
        if self.detect_deadlock():
            messagebox.showinfo("Deadlock", "Deadlock detected! Please remove some edges.")
        else:
            messagebox.showinfo("No Deadlock", "No deadlock detected.")

    def detect_deadlock(self):
        # Basic deadlock detection algorithm (cycle detection in the graph)
        visited = set()
        stack = set()

        def visit(node):
            if node in stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            stack.add(node)
            for edge in node.edges:
                target_node = edge.to_node if edge.from_node == node else edge.from_node
                if visit(target_node):
                    return True
            stack.remove(node)
            return False

        for node in self.nodes:
            if node.text.startswith("P"):  # Only start from processes
                if visit(node):
                    return True
        return False

# Create and run the application
root = tk.Tk()
root.title("Deadlock Simulator")
app = DeadlockApp(root)
root.mainloop()
