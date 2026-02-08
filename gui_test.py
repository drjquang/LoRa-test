import tkinter as tk
import random

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Random Grid")
        self.root.configure(bg="lime")
        self.root.attributes("-fullscreen", True)

        # Layout: 10% / 80% / 10%
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=8)
        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # ---------- Top ----------
        top = tk.Frame(root, bg="lime")
        top.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            top,
            text="Random Number Grid",
            bg="lime",
            fg="black",
            font=("Arial", 32, "bold")
        ).pack(expand=True)

        # ---------- Middle ----------
        self.middle = tk.Frame(root, bg="lime")
        self.middle.grid(row=1, column=0, sticky="nsew")

        # ---------- Bottom ----------
        bottom = tk.Frame(root, bg="lime")
        bottom.grid(row=2, column=0, sticky="nsew")

        tk.Button(
            bottom,
            text="Generate",
            font=("Arial", 16),
            command=self.add_number
        ).pack(side="right", padx=20, pady=20)

        # Storage
        self.labels = []

        # Grid configuration
        self.max_columns = 10
        self.square_size_px = 80

        # Exit fullscreen
        root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

    def clear_middle(self):
        for lbl in self.labels:
            lbl.destroy()
        self.labels.clear()

    def add_number(self):
        self.middle.update_idletasks()

        # Calculate how many rows fit in middle frame
        middle_height = self.middle.winfo_height()
        max_rows = max(1, middle_height // (self.square_size_px + 10))

        max_items = max_rows * self.max_columns

        # Clear if full
        if len(self.labels) >= max_items:
            self.clear_middle()

        number = random.randint(0, 36)
        bg_color = random.choice(["red", "black", "green"])

        lbl = tk.Label(
            self.middle,
            text=str(number),
            width=6,
            height=3,
            bg=bg_color,
            fg="white",
            font=("Arial", 20, "bold"),
            relief="solid",
            borderwidth=2
        )

        # Newest first
        self.labels.insert(0, lbl)

        # Re-layout
        for index, label in enumerate(self.labels):
            row = index // self.max_columns
            col = index % self.max_columns
            label.grid(row=row, column=col, padx=5, pady=5, sticky="nw")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
