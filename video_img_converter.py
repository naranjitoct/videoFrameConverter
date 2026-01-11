import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import os
from pathlib import Path

class VideoFrameExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Extractor de Frames de Video. R.Serón")        
        self.root.geometry("550x350") #Ancho x Alto
        self.root.resizable(False, False)
        
        self.video_path = ""
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Selección de video
        tk.Label(main_frame, text="Seleccionar Video:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        file_frame = tk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_label = tk.Label(file_frame, text="Ningún archivo seleccionado", 
                                    bg="white", relief=tk.SUNKEN, anchor=tk.W)
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(file_frame, text="Buscar", command=self.select_video, 
                 width=10).pack(side=tk.RIGHT)
        
        # Opciones de extracción
        tk.Label(main_frame, text="Modo de Extracción:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        self.extraction_mode = tk.StringVar(value="all")
        
        tk.Radiobutton(main_frame, text="Todos los frames", 
                      variable=self.extraction_mode, value="all").pack(anchor=tk.W)
        
        interval_frame = tk.Frame(main_frame)
        interval_frame.pack(anchor=tk.W, pady=5)
        
        tk.Radiobutton(interval_frame, text="Cada", 
                      variable=self.extraction_mode, value="interval").pack(side=tk.LEFT)
        
        self.interval_entry = tk.Entry(interval_frame, width=8)
        self.interval_entry.insert(0, "1000")
        self.interval_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(interval_frame, text="milisegundos").pack(side=tk.LEFT)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=20)
        
        self.status_label = tk.Label(main_frame, text="", fg="blue")
        self.status_label.pack(pady=5)
        
        # Botón extraer - Frame separado para mejor control
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.extract_button = tk.Button(
            button_frame, 
            text="EXTRAER FRAMES", 
            command=self.extract_frames,
            bg="#4CAF50", 
            fg="white", 
            font=("Arial", 14, "bold"),
            relief=tk.RAISED,
            bd=3,
            cursor="hand2"
        )
        self.extract_button.pack(fill=tk.BOTH, ipady=10)
    
    def select_video(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar video",
            filetypes=[("Videos", "*.mp4 *.avi *.mov *.mkv *.flv"), ("Todos", "*.*")]
        )
        if filename:
            self.video_path = filename
            self.file_label.config(text=os.path.basename(filename))
    
    def extract_frames(self):
        if not self.video_path:
            messagebox.showwarning("Advertencia", "Por favor selecciona un video primero")
            return
        
        try:
            # Abrir video
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                messagebox.showerror("Error", "No se pudo abrir el video")
                return
            
            # Crear carpeta de salida
            video_name = Path(self.video_path).stem
            output_folder = os.path.join(os.path.dirname(self.video_path), f"{video_name}_frames")
            os.makedirs(output_folder, exist_ok=True)
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            self.progress['maximum'] = total_frames
            self.progress['value'] = 0
            
            frame_count = 0
            saved_count = 0
            
            if self.extraction_mode.get() == "all":
                # Extraer todos los frames
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    filename = os.path.join(output_folder, f"frame_{frame_count:06d}.jpg")
                    cv2.imwrite(filename, frame)
                    
                    frame_count += 1
                    saved_count += 1
                    self.progress['value'] = frame_count
                    self.status_label.config(text=f"Procesando: {frame_count}/{total_frames}")
                    self.root.update()
            else:
                # Extraer cada X milisegundos
                interval_ms = int(self.interval_entry.get())
                interval_frames = int((interval_ms / 1000.0) * fps)
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if frame_count % interval_frames == 0:
                        filename = os.path.join(output_folder, f"frame_{saved_count:06d}.jpg")
                        cv2.imwrite(filename, frame)
                        saved_count += 1
                    
                    frame_count += 1
                    self.progress['value'] = frame_count
                    self.status_label.config(text=f"Procesando: {frame_count}/{total_frames}")
                    self.root.update()
            
            cap.release()
            self.status_label.config(text=f"¡Completado! {saved_count} frames guardados", fg="green")
            messagebox.showinfo("Éxito", f"Se extrajeron {saved_count} frames\nCarpeta: {output_folder}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
            self.status_label.config(text="Error en la extracción", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoFrameExtractor(root)
    root.mainloop()