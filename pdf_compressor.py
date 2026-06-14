from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import fitz
import subprocess
import os
import tempfile

# Global state
original_file = ""
pdf_file = ""
preview_image = None
temp_pdf_path = None
current_pdf_doc = None

def cleanup_temp_file():
    global temp_pdf_path
    if temp_pdf_path and os.path.exists(temp_pdf_path):
        try:
            os.remove(temp_pdf_path)
        except Exception:
            pass
    temp_pdf_path = None

def cleanup_pdf_doc():
    global current_pdf_doc
    if current_pdf_doc:
        current_pdf_doc.close()
        current_pdf_doc = None

def render_preview(event=None):
    global preview_image, current_pdf_doc
    if not current_pdf_doc:
        return

    try:
        page = current_pdf_doc.load_page(0)
        
        # Get available space in the preview frame
        # Subtracting some padding
        canvas_width = left_panel.winfo_width() - 60
        canvas_height = left_panel.winfo_height() - 150
        
        if canvas_width < 50 or canvas_height < 50:
            return

        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)

        preview_image = ImageTk.PhotoImage(img)
        preview_label.config(image=preview_image, text="")
        preview_label.image = preview_image
    except Exception as e:
        print(f"Render error: {e}")

def show_preview(pdf_path):
    global current_pdf_doc
    cleanup_pdf_doc()
    try:
        import fitz
        from PIL import Image, ImageTk
        
        current_pdf_doc = fitz.open(pdf_path)
        page_count = len(current_pdf_doc)
        page_count_label.config(text=f"Pages: {page_count}")
        render_preview()
    except Exception as e:
        import traceback
        err_msg = f"Preview Error: {str(e)}\n\n{traceback.format_exc()}"
        print(err_msg)
        messagebox.showerror("Preview Error", err_msg)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

def convert_image_to_pdf(image_path):
    global temp_pdf_path
    try:
        from PIL import Image
        cleanup_temp_file()
        fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        
        img = Image.open(image_path).convert("RGB")
        img.save(temp_pdf_path, "PDF", resolution=100.0)
        return temp_pdf_path
    except Exception as e:
        import traceback
        err_msg = f"Conversion Error: {str(e)}\n\n{traceback.format_exc()}"
        print(err_msg)
        messagebox.showerror("Conversion Error", err_msg)
        return None

def handle_file_selection(file_path):
    global pdf_file, original_file
    
    if not file_path:
        return

    ext = os.path.splitext(file_path)[1].lower()
    original_file = file_path
    
    if ext in IMAGE_EXTENSIONS:
        converted_pdf = convert_image_to_pdf(file_path)
        if converted_pdf:
            pdf_file = converted_pdf
        else:
            return
    elif ext == ".pdf":
        cleanup_temp_file()
        pdf_file = file_path
    else:
        messagebox.showerror("Error", "Unsupported file type.")
        return

    file_name_label.config(text=os.path.basename(original_file))
    show_preview(pdf_file)
    update_size_estimate()
    # Reset results
    update_results_display(0, 0)

def select_pdf():
    file_types = [
        ("Supported Files", "*.pdf *.jpg *.jpeg *.png *.webp *.bmp"),
        ("PDF Files", "*.pdf"),
        ("Image Files", "*.jpg *.jpeg *.png *.webp *.bmp"),
        ("All Files", "*.*")
    ]
    path = filedialog.askopenfilename(filetypes=file_types)
    handle_file_selection(path)

def drop(event):
    on_drag_leave(event)
    path = event.data.strip("{}")
    handle_file_selection(path)

def on_drag_enter(event):
    left_panel.config(bg="#f0f7ff")
    preview_area_frame.config(highlightbackground="#1976d2", highlightthickness=2)

def on_drag_leave(event):
    left_panel.config(bg="#f8f9fa")
    preview_area_frame.config(highlightbackground="#eeeeee", highlightthickness=1)

def format_size(size_bytes):
    if size_bytes <= 0: return "--"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def update_size_estimate(*args):
    if not pdf_file or not original_file:
        return

    original_size = os.path.getsize(original_file)
    
    try:
        target_kb = float(target_size_entry.get())
        estimated = target_kb * 1024
    except ValueError:
        estimated = 0

    orig_size_val_label.config(text=format_size(original_size))
    est_size_val_label.config(text=format_size(estimated))

def update_results_display(orig_kb, comp_kb):
    if orig_kb <= 0:
        res_orig_label.config(text="--")
        res_comp_label.config(text="--")
        res_saved_label.config(text="--")
        res_percent_label.config(text="--")
        return

    saved_kb = orig_kb - comp_kb
    percent = (saved_kb / orig_kb) * 100 if orig_kb > 0 else 0
    
    res_orig_label.config(text=format_size(orig_kb * 1024))
    res_comp_label.config(text=format_size(comp_kb * 1024))
    res_saved_label.config(text=format_size(max(0, saved_kb * 1024)))
    res_percent_label.config(text=f"{max(0, percent):.1f}%")

def compress_pdf():
    if not pdf_file or not original_file:
        messagebox.showerror("Error", "Select or drop a file first.")
        return

    base_path = os.path.splitext(original_file)[0]
    output_file = f"{base_path}_compressed.pdf"
    orig_kb = os.path.getsize(original_file) / 1024

    try:
        target_kb = int(target_size_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid target size (integer).")
        return

    # Define compression attempts
    # Presets first
    attempts = [
        {"type": "preset", "val": "/prepress", "desc": "High Quality"},
        {"type": "preset", "val": "/printer", "desc": "Print Quality"},
        {"type": "preset", "val": "/ebook", "desc": "Medium Quality (150 DPI)"},
        {"type": "preset", "val": "/screen", "desc": "Screen Quality (72 DPI)"}
    ]
    
    # Extended attempts for strict mode
    if strict_mode_enabled.get():
        attempts.extend([
            {"type": "dpi", "val": 60, "desc": "Low Quality (60 DPI)"},
            {"type": "dpi", "val": 50, "desc": "Very Low Quality (50 DPI)"},
            {"type": "dpi", "val": 40, "desc": "Minimal Quality (40 DPI)"},
            {"type": "dpi", "val": 30, "desc": "Strict Minimum (30 DPI)"}
        ])

    size_kb = 0
    target_achieved = False
    
    for i, attempt in enumerate(attempts):
        progress_label.config(text=f"Attempt {i+1}/{len(attempts)}: {attempt['desc']}...", fg="#1976d2")
        root.update()
        
        if attempt["type"] == "preset":
            cmd = ["gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4", f"-dPDFSETTINGS={attempt['val']}",
                   "-dNOPAUSE", "-dQUIET", "-dBATCH", f"-sOutputFile={output_file}", pdf_file]
        else:
            dpi = attempt["val"]
            cmd = ["gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
                   f"-dColorImageResolution={dpi}", f"-dGrayImageResolution={dpi}", f"-dMonoImageResolution={dpi}",
                   "-dDownsampleColorImages=true", "-dDownsampleGrayImages=true", "-dDownsampleMonoImages=true",
                   "-dNOPAUSE", "-dQUIET", "-dBATCH", f"-sOutputFile={output_file}", pdf_file]
        
        subprocess.run(cmd)
        size_kb = os.path.getsize(output_file) / 1024
        
        if size_kb <= target_kb:
            target_achieved = True
            break

    progress_label.config(text="Compression complete", fg="#2e7d32")
    update_results_display(orig_kb, size_kb)
    
    if target_achieved:
        messagebox.showinfo("Target Achieved", 
                            f"Target Size: {target_kb} KB\n"
                            f"Actual Size: {size_kb:.1f} KB\n\n"
                            f"Saved to: {output_file}")
    else:
        messagebox.showwarning("Closest Possible Size Reached", 
                               f"Could not reach target without compromising quality too much.\n\n"
                               f"Target Size: {target_kb} KB\n"
                               f"Actual Size: {size_kb:.1f} KB\n\n"
                               f"Saved to: {output_file}")

root = TkinterDnD.Tk()
root.title("KB PDF Compressor")
root.geometry("1000x700")
root.configure(bg="#ffffff")

# Set window icon if it exists
try:
    if os.path.exists("kb-pdf-compressor.png"):
        icon_img = ImageTk.PhotoImage(file="kb-pdf-compressor.png")
        root.iconphoto(True, icon_img)
except Exception:
    pass

# Main split layout using PanedWindow
paned_window = tk.PanedWindow(root, orient="horizontal", bg="#ffffff", sashwidth=4, sashrelief="flat")
paned_window.pack(fill="both", expand=True)

# LEFT PANEL: Preview
left_panel = tk.Frame(paned_window, bg="#f8f9fa", padx=20, pady=20)
paned_window.add(left_panel, stretch="always", width=650)

tk.Label(left_panel, text="KB PDF Compressor", font=("Helvetica", 18, "bold"), bg="#f8f9fa", fg="#1976d2").pack(anchor="w", pady=(0, 10))

preview_area_frame = tk.Frame(left_panel, bg="#ffffff", highlightbackground="#eeeeee", highlightthickness=1)
preview_area_frame.pack(fill="both", expand=True)

preview_label = tk.Label(preview_area_frame, bg="#ffffff", text="Drag & Drop PDF or Image Here\nor Click to Select", fg="#999999", font=("Helvetica", 12))
preview_label.pack(expand=True, fill="both")
preview_label.bind("<Button-1>", lambda e: select_pdf())

file_info_bar = tk.Frame(left_panel, bg="#f8f9fa", pady=10)
file_info_bar.pack(fill="x")

file_name_label = tk.Label(file_info_bar, text="No File Selected", font=("Helvetica", 11, "bold"), bg="#f8f9fa", fg="#555555")
file_name_label.pack(side="left")

page_count_label = tk.Label(file_info_bar, text="", font=("Helvetica", 10), bg="#f8f9fa", fg="#777777")
page_count_label.pack(side="right")

# RIGHT PANEL: Settings
right_panel = tk.Frame(paned_window, bg="#ffffff", padx=20, pady=20)
paned_window.add(right_panel, width=350)

# Settings Section
tk.Label(right_panel, text="Compression Settings", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#333333").pack(anchor="w", pady=(0, 20))

# Size Overview
size_frame = tk.Frame(right_panel, bg="#ffffff")
size_frame.pack(fill="x", pady=(0, 20))

tk.Label(size_frame, text="Original Size:", bg="#ffffff", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w")
orig_size_val_label = tk.Label(size_frame, text="--", bg="#ffffff", font=("Helvetica", 10, "bold"))
orig_size_val_label.grid(row=0, column=1, sticky="w", padx=10)

tk.Label(size_frame, text="Target Size:", bg="#ffffff", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=5)
est_size_val_label = tk.Label(size_frame, text="--", bg="#ffffff", font=("Helvetica", 10, "bold"), fg="#2e7d32")
est_size_val_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)

# Target Size Section (Primary)
target_input_frame = tk.Frame(right_panel, bg="#ffffff")
target_input_frame.pack(anchor="w", pady=(0, 10))
tk.Label(target_input_frame, text="Set Target Size (KB):", bg="#ffffff", font=("Helvetica", 10, "bold")).pack(anchor="w")

target_entry_inner = tk.Frame(target_input_frame, bg="#ffffff")
target_entry_inner.pack(fill="x", pady=5)

target_size_entry = tk.Entry(target_entry_inner, width=15, font=("Helvetica", 10))
target_size_entry.insert(0, "100")
target_size_entry.pack(side="left")

# Bind target size changes to update estimate
target_size_entry.bind("<KeyRelease>", update_size_estimate)

strict_mode_enabled = tk.BooleanVar()
tk.Checkbutton(right_panel, text="Strict Target Size Mode", variable=strict_mode_enabled, bg="#ffffff", font=("Helvetica", 10)).pack(anchor="w", pady=(0, 10))

progress_label = tk.Label(right_panel, text="", bg="#ffffff", font=("Helvetica", 9, "italic"), fg="#666666")
progress_label.pack(fill="x", pady=(0, 10))

# Results Section
results_frame = tk.LabelFrame(right_panel, text=" Last Result ", bg="#ffffff", font=("Helvetica", 10, "bold"), padx=15, pady=10)
results_frame.pack(fill="x", pady=(0, 20))

def add_result_row(parent, row, label_text, color="#333333"):
    tk.Label(parent, text=label_text, bg="#ffffff", font=("Helvetica", 9)).grid(row=row, column=0, sticky="w")
    val_label = tk.Label(parent, text="--", bg="#ffffff", font=("Helvetica", 9, "bold"), fg=color)
    val_label.grid(row=row, column=1, sticky="w", padx=10)
    return val_label

res_orig_label = add_result_row(results_frame, 0, "Original:")
res_comp_label = add_result_row(results_frame, 1, "Compressed:")
res_saved_label = add_result_row(results_frame, 2, "Space Saved:", "#2e7d32")
res_percent_label = add_result_row(results_frame, 3, "Reduction:", "#1976d2")

# Action Button
tk.Button(right_panel, text="COMPRESS PDF", command=compress_pdf, bg="#1976d2", fg="#ffffff", font=("Helvetica", 12, "bold"), pady=12, relief="flat", cursor="hand2").pack(fill="x", side="bottom")

# Bindings
root.drop_target_register(DND_FILES)
root.dnd_bind("<<Drop>>", drop)
root.dnd_bind("<<DragEnter>>", on_drag_enter)
root.dnd_bind("<<DragLeave>>", on_drag_leave)
left_panel.drop_target_register(DND_FILES)
left_panel.dnd_bind("<<Drop>>", drop)

# Auto-resize preview
left_panel.bind("<Configure>", render_preview)

root.mainloop()
