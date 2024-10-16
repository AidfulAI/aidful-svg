import tkinter as tk
from tkinter import filedialog, messagebox
from svgpathtools import svg2paths2, wsvg
from svgpathtools import Path as SVGPath
import os

class AidfulSVGApp:
    def __init__(self, master):
        self.master = master
        master.title("Aidful-SVG")

        self.filename = None
        self.original_paths = []
        self.original_attributes = []
        self.svg_attributes = {}
        self.preview_paths = []
        self.min_length = 0

        # Create UI elements
        self.load_button = tk.Button(master, text="Load SVG", command=self.load_svg)
        self.load_button.pack(pady=5)

        self.slider_label = tk.Label(master, text="Minimum Path Length:")
        self.slider = tk.Scale(master, from_=0, to=1000, orient=tk.HORIZONTAL, command=self.update_preview)
        self.slider_label.pack()
        self.slider.pack(fill=tk.X, padx=20)

        self.save_button = tk.Button(master, text="Save SVG", command=self.save_svg, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.canvas = tk.Canvas(master, width=1000, height=800, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def load_svg(self):
        self.filename = filedialog.askopenfilename(filetypes=[("SVG files", "*.svg")])
        if not self.filename:
            return

        try:
            self.original_paths, self.original_attributes, self.svg_attributes = svg2paths2(self.filename)
            self.slider.config(to=max(self.get_path_lengths()))
            self.update_preview()
            self.save_button.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "SVG file loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load SVG file:\n{e}")

    def get_path_lengths(self):
        return [path.length() for path in self.original_paths]

    def update_preview(self, event=None):
        if not self.original_paths:
            return

        self.min_length = self.slider.get()
        self.preview_paths = [
            path for path in self.original_paths if path.length() >= self.min_length
        ]

        self.render_preview()

    def render_preview(self):
        self.canvas.delete("all")

        # Calculate bounding box of all paths
        xmin = ymin = float('inf')
        xmax = ymax = float('-inf')
        for path in self.preview_paths:
            for seg in path:
                xmin = min(xmin, seg.start.real, seg.end.real)
                ymin = min(ymin, seg.start.imag, seg.end.imag)
                xmax = max(xmax, seg.start.real, seg.end.real)
                ymax = max(ymax, seg.start.imag, seg.end.imag)

        # Calculate scaling factors
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        scale_x = width / (xmax - xmin) if xmax > xmin else 1
        scale_y = height / (ymax - ymin) if ymax > ymin else 1
        scale = min(scale_x, scale_y) * 0.9  # 90% of the available space

        # Calculate offset to center the image
        offset_x = (width - (xmax - xmin) * scale) / 2 - xmin * scale
        offset_y = (height - (ymax - ymin) * scale) / 2 - ymin * scale

        for path in self.preview_paths:
            points = []
            for seg in path:
                start = seg.start.real * scale + offset_x, seg.start.imag * scale + offset_y
                end = seg.end.real * scale + offset_x, seg.end.imag * scale + offset_y
                points.extend([start, end])
            if points:
                self.canvas.create_line(*points, fill="black")

    def save_svg(self):
        save_filename = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")])
        if not save_filename:
            return

        try:
            wsvg(
                self.preview_paths,
                attributes=self.original_attributes,
                svg_attributes=self.svg_attributes,
                filename=save_filename
            )
            messagebox.showinfo("Success", "SVG file saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save SVG file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AidfulSVGApp(root)
    root.mainloop()
