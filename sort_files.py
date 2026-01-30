import os 
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from collections import defaultdict
import threading
from queue import Queue

# 文件类型分类字典
FILE_CATEGORIES = {
    '图片': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff'},
    '视频': {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.m3u8'},
    '文本': {'.txt', '.doc', '.docx', '.pdf', '.xlsx', '.xls', '.ppt', '.pptx', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.cpp', '.c'},
    '音频': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'},
    '压缩包': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
    '程序': {'.exe', '.msi', '.apk', '.dmg', '.deb', '.rpm'}
}

class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文件分类整理工具")
        self.root.geometry("700x600")
        self.selected_path = None
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 标题
        title = tk.Label(self.root, text="文件分类整理工具", font=("微软雅黑", 16, "bold"))
        title.pack(pady=10)
        
        # 选择文件夹按钮
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.btn_select = tk.Button(btn_frame, text="📁 选择文件夹", command=self.select_folder, 
                                     font=("微软雅黑", 12), bg="#4CAF50", fg="white", 
                                     padx=20, pady=10, cursor="hand2")
        self.btn_select.pack(side=tk.LEFT, padx=5)
        
        # 显示选中的路径
        self.path_label = tk.Label(self.root, text="未选择文件夹", font=("微软雅黑", 10), fg="gray")
        self.path_label.pack(pady=5)
        
        # 预览区域
        preview_frame = tk.LabelFrame(self.root, text="分类预览", font=("微软雅黑", 11, "bold"), padx=10, pady=10)
        preview_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, font=("Consolas", 10), 
                                                       height=15, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # 进度条
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(padx=20, pady=5, fill=tk.X)
        
        self.progress_label = tk.Label(progress_frame, text="进度: 0%", font=("微软雅黑", 9))
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 操作按钮
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        
        self.btn_restore = tk.Button(action_frame, text="↩️ 恢复分类", command=self.restore_files,
                                      font=("微软雅黑", 11), bg="#FF9800", fg="white",
                                      padx=15, pady=8, state=tk.DISABLED, cursor="hand2")
        self.btn_restore.pack(side=tk.LEFT, padx=5)
        
        self.btn_sort = tk.Button(action_frame, text="✨ 开始分类", command=self.sort_files,
                                   font=("微软雅黑", 11), bg="#2196F3", fg="white",
                                   padx=15, pady=8, state=tk.DISABLED, cursor="hand2")
        self.btn_sort.pack(side=tk.LEFT, padx=5)
        
        # 说明文字
        info = tk.Label(self.root, text="提示：选择文件夹后会显示分类预览，确认后点击'开始分类'执行", 
                       font=("微软雅黑", 9), fg="gray")
        info.pack(pady=5)
        
    def select_folder(self):
        """选择文件夹并预览分类"""
        folder = filedialog.askdirectory(title="选择要整理的文件夹")
        if folder:
            self.selected_path = Path(folder)
            self.path_label.config(text=f"已选择: {folder}", fg="green")
            self.preview_classification()
            self.btn_restore.config(state=tk.NORMAL)
            self.btn_sort.config(state=tk.NORMAL)
    
    def get_category(self, file_path):
        """根据文件扩展名返回分类"""
        ext = file_path.suffix.lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return '其他'
    
    def preview_classification(self):
        """预览文件分类情况"""
        self.preview_text.delete(1.0, tk.END)
        
        if not self.selected_path or not self.selected_path.exists():
            self.preview_text.insert(tk.END, "错误: 文件夹不存在\n")
            return
        
        # 统计文件分类
        category_files = defaultdict(list)
        total_files = 0
        
        for file in self.selected_path.iterdir():
            if file.is_file():
                total_files += 1
                category = self.get_category(file)
                category_files[category].append(file.name)
        
        # 显示预览
        self.preview_text.insert(tk.END, f"📊 文件夹: {self.selected_path.name}\n")
        self.preview_text.insert(tk.END, f"📁 共找到 {total_files} 个文件\n")
        self.preview_text.insert(tk.END, "=" * 60 + "\n\n")
        
        if total_files == 0:
            self.preview_text.insert(tk.END, "该文件夹中没有文件需要分类\n")
            return
        
        for category in sorted(category_files.keys()):
            files = category_files[category]
            self.preview_text.insert(tk.END, f"📂 {category} ({len(files)} 个文件)\n")
            for file in files[:5]:  # 只显示前5个
                self.preview_text.insert(tk.END, f"   • {file}\n")
            if len(files) > 5:
                self.preview_text.insert(tk.END, f"   ... 还有 {len(files) - 5} 个文件\n")
            self.preview_text.insert(tk.END, "\n")
    
    def restore_files(self):
        """恢复文件分类（后台线程）"""
        if not self.selected_path:
            messagebox.showwarning("警告", "请先选择文件夹")
            return
        
        if not messagebox.askyesno("确认", "确定要将所有子文件夹中的文件恢复到主文件夹吗？"):
            return
        
        # 禁用按钮，启动线程
        self.btn_restore.config(state=tk.DISABLED)
        self.btn_sort.config(state=tk.DISABLED)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "正在恢复文件...\n")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="进度: 0%")
        
        thread = threading.Thread(target=self._restore_files_thread, daemon=True)
        thread.start()
    
    def _restore_files_thread(self):
        """在后台线程中执行恢复操作"""
        try:
            # 第一步：统计总文件数
            total_files = sum(1 for folder in self.selected_path.iterdir() 
                            if folder.is_dir() 
                            for file in folder.iterdir() 
                            if file.is_file())
            
            if total_files == 0:
                self.root.after(0, lambda: messagebox.showinfo("提示", "没有文件需要恢复"))
                self.root.after(0, self._restore_buttons_enable)
                return
            
            restored_count = 0
            for folder in self.selected_path.iterdir():
                if folder.is_dir():
                    for file in folder.iterdir():
                        if file.is_file():
                            shutil.move(str(file), str(self.selected_path / file.name))
                            restored_count += 1
                            
                            # 更新进度条
                            progress = int((restored_count / total_files) * 100)
                            self.root.after(0, lambda p=progress, c=restored_count, t=total_files: 
                                           self._update_progress(p, c, t))
                    try:
                        folder.rmdir()
                    except:
                        pass
            
            # 完成后的回调
            self.root.after(0, lambda: self._restore_complete(restored_count))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"恢复失败: {str(e)}"))
            self.root.after(0, self._restore_buttons_enable)
    
    def _restore_complete(self, restored_count):
        """恢复完成后的处理"""
        messagebox.showinfo("完成", f"成功恢复 {restored_count} 个文件！")
        self.preview_classification()
        self._restore_buttons_enable()
    
    def sort_files(self):
        """执行文件分类（后台线程）"""
        if not self.selected_path:
            messagebox.showwarning("警告", "请先选择文件夹")
            return
        
        if not messagebox.askyesno("确认", "确定要开始分类整理文件吗？"):
            return
        
        # 禁用按钮，启动线程
        self.btn_restore.config(state=tk.DISABLED)
        self.btn_sort.config(state=tk.DISABLED)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "正在分类文件...\n")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="进度: 0%")
        
        thread = threading.Thread(target=self._sort_files_thread, daemon=True)
        thread.start()
    
    def _sort_files_thread(self):
        """在后台线程中执行分类操作"""
        try:
            # 第一步：统计总文件数
            total_files = sum(1 for file in self.selected_path.iterdir() if file.is_file())
            
            if total_files == 0:
                self.root.after(0, lambda: messagebox.showinfo("提示", "该文件夹中没有文件需要分类"))
                self.root.after(0, self._sort_buttons_enable)
                return
            
            sorted_count = 0
            for file in self.selected_path.iterdir():
                if file.is_file():
                    category = self.get_category(file)
                    dest_folder = self.selected_path / category
                    dest_folder.mkdir(exist_ok=True)
                    shutil.move(str(file), str(dest_folder / file.name))
                    sorted_count += 1
                    
                    # 更新进度条
                    progress = int((sorted_count / total_files) * 100)
                    self.root.after(0, lambda p=progress, c=sorted_count, t=total_files: 
                                   self._update_progress(p, c, t))
            
            # 完成后的回调
            self.root.after(0, lambda: self._sort_complete(sorted_count))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"分类失败: {str(e)}"))
            self.root.after(0, self._sort_buttons_enable)
    
    def _update_progress(self, progress, current, total):
        """更新进度条"""
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"进度: {progress}% ({current}/{total})")
    
    def _sort_complete(self, sorted_count):
        """分类完成后的处理"""
        messagebox.showinfo("完成", f"成功分类 {sorted_count} 个文件！")
        self.preview_classification()
        self._sort_buttons_enable()
    
    def _restore_buttons_enable(self):
        """启用按钮"""
        self.btn_restore.config(state=tk.NORMAL)
        self.btn_sort.config(state=tk.NORMAL)
    
    def _sort_buttons_enable(self):
        """启用按钮"""
        self.btn_restore.config(state=tk.NORMAL)
        self.btn_sort.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSorterGUI(root)
    root.mainloop()