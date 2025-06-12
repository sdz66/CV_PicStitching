import cv2
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from final import stitch_images, process_video, process_images

# 注意：保留了原有的import语句，确保核心功能不变
# from final import stitch_images, process_video, process_images

class ImageStitchingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片拼接工具")
        self.root.geometry("900x750")
        self.root.resizable(False, False)
        
        # 创建主框架
        main_frame = Frame(root, padx=20, pady=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 图片显示区域 - 使用带边框的LabelFrame
        display_frame = LabelFrame(main_frame, text="预览区域", padx=10, pady=10)
        display_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        self.canvas = Canvas(display_frame, width=600, height=400, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(padx=5, pady=5)
        self.canvas.create_text(300, 200, text="处理后图片将显示在这里", 
                               fill="#aaa", font=("Arial", 12))
        
        # 输入源选择 - 使用带边框的LabelFrame
        source_frame = LabelFrame(main_frame, text="输入源选择", padx=10, pady=10)
        source_frame.pack(fill=X, pady=(0, 10))
        
        self.source_var = IntVar(value=1)
        Radiobutton(source_frame, text="图片目录", variable=self.source_var, 
                   value=1, command=self.toggle_controls).pack(side=LEFT, padx=20)
        Radiobutton(source_frame, text="视频文件", variable=self.source_var, 
                   value=2, command=self.toggle_controls).pack(side=LEFT, padx=20)
        
        # 参数设置 - 使用带边框的LabelFrame
        params_frame = LabelFrame(main_frame, text="参数设置", padx=10, pady=10)
        params_frame.pack(fill=X, pady=(0, 10))
        
        # 视频帧间隔设置（默认隐藏）
        self.interval_frame = Frame(params_frame)
        Label(self.interval_frame, text="视频帧间隔(秒):").pack(side=LEFT, padx=(0, 5))
        self.interval_entry = Entry(self.interval_frame, width=8)
        self.interval_entry.insert(0, "0.3")
        self.interval_entry.pack(side=LEFT)
        self.interval_frame.pack(fill=X, pady=(0, 10))
        
        # 输出路径设置
        output_frame = Frame(params_frame)
        output_frame.pack(fill=X)
        
        Label(output_frame, text="输出文件路径:").pack(side=LEFT, padx=(0, 5))
        self.output_entry = Entry(output_frame)
        self.output_entry.insert(0, "output.png")
        self.output_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        Button(output_frame, text="浏览...", command=self.browse_output, 
              width=8).pack(side=RIGHT)
        
        # 按钮区域
        button_frame = Frame(main_frame)
        button_frame.pack(fill=X, pady=(10, 0))
        
        Button(button_frame, text="开始处理", command=self.process, 
              bg="#4CAF50", fg="white", height=2, width=15,
              font=("Arial", 10, "bold")).pack(pady=10)
        
        # 状态栏
        self.status_var = StringVar(value="就绪")
        status_bar = Label(root, textvariable=self.status_var, bd=1, relief=SUNKEN, 
                         anchor=W, padx=10, bg="#e0e0e0")
        status_bar.pack(side=BOTTOM, fill=X)
        
        # 初始化控件状态
        self.toggle_controls()
    
    def toggle_controls(self):
        """根据选择的输入源显示/隐藏相关控件"""
        if self.source_var.get() == 1:  # 图片目录
            self.interval_frame.pack_forget()
        else:  # 视频文件
            self.interval_frame.pack(fill=X, pady=(0, 10))
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg"), ("所有文件", "*.*")]
        )
        if filename:
            self.output_entry.delete(0, END)
            self.output_entry.insert(0, filename)
    
    def show_image(self, img):
        """在Canvas上显示图片"""
        self.canvas.delete("all")
        if img is not None:
            # 缩放图片以适应Canvas大小
            h, w = img.shape[:2]
            ratio = min(600/w, 400/h)
            new_w, new_h = int(w*ratio), int(h*ratio)
            img = cv2.resize(img, (new_w, new_h))
            
            # 转换颜色空间并显示
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(300, 200, image=img_tk)
            self.canvas.image = img_tk
    
    def process(self):
        source = self.source_var.get()
        output_path = self.output_entry.get()
        
        self.status_var.set("处理中...")
        self.root.update()
        
        try:
            if source == 1:  # 图片目录
                dir_path = filedialog.askdirectory(title="选择图片目录")
                if dir_path:
                    result = process_images(dir_path)
                    self.show_image(result)
                    messagebox.showinfo("完成", "图片拼接完成!")
                    self.status_var.set("图片拼接完成")

            elif source == 2:  # 视频文件
                interval = float(self.interval_entry.get())
                video_path = filedialog.askopenfilename(
                    title="选择视频文件", 
                    filetypes=[("视频文件", "*.mp4;*.avi;*.mov"), ("所有文件", "*.*")]
                )
                if video_path:
                    result = process_video(video_path, interval)
                    if result is not None:
                        self.show_image(result)
                    messagebox.showinfo("完成", "视频处理完成!")
                    self.status_var.set("视频处理完成")
        except Exception as e:
            messagebox.showerror("错误", f"处理时出错: {str(e)}")
            self.status_var.set(f"错误: {str(e)}")
        finally:
            if self.status_var.get().startswith("错误"):
                pass
            else:
                self.status_var.set("就绪")

if __name__ == "__main__":
    root = Tk()
    app = ImageStitchingApp(root)
    root.mainloop()