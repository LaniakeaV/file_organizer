import os 
import shutil
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from collections import defaultdict
import threading
import json
import darkdetect

# 文件类型分类字典
FILE_CATEGORIES = {
    '图片': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff'},
    '视频': {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.m3u8'},
    '文本': {'.txt', '.doc', '.docx', '.pdf', '.xlsx', '.xls', '.ppt', '.pptx', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.cpp', '.c'},
    '音频': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'},
    '压缩包': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
    '程序': {'.exe', '.msi', '.apk', '.dmg', '.deb', '.rpm'}
}

# 多语言翻译字典
TRANSLATIONS = {
    'zh': {
        'title': '文件分类整理工具',
        'select_folder': '📁 选择文件夹',
        'no_folder': '未选择文件夹',
        'selected': '已选择',
        'preview': '分类预览',
        'progress': '进度',
        'restore': '↩️ 恢复分类',
        'sort': '✨ 开始分类',
        'tip': '提示：选择文件夹后会显示分类预览，确认后点击\'开始分类\'执行',
        'confirm_sort': '确定要开始分类整理文件吗？',
        'confirm_restore': '确定要将所有子文件夹中的文件恢复到主文件夹吗？',
        'sorting': '正在分类文件...',
        'restoring': '正在恢复文件...',
        'success_sort': '成功分类 {} 个文件！',
        'success_restore': '成功恢复 {} 个文件！',
        'error_sort': '分类失败: {}',
        'error_restore': '恢复失败: {}',
        'no_file_sort': '该文件夹中没有文件需要分类',
        'no_file_restore': '没有文件需要恢复',
        'folder_info': '📊 文件夹: {}',
        'total_files': '📁 共找到 {} 个文件',
        'folder_error': '错误: 文件夹不存在',
        'category': '📂 {} ({} 个文件)',
        'more_files': '   ... 还有 {} 个文件',
        'theme': '主题',
        'light': '浅色',
        'dark': '深色',
        'auto': '自动',
        'language': '语言',
        'settings': '⚙️ 设置',
    },
    'en': {
        'title': 'File Sorter Tool',
        'select_folder': '📁 Select Folder',
        'no_folder': 'No folder selected',
        'selected': 'Selected',
        'preview': 'Classification Preview',
        'progress': 'Progress',
        'restore': '↩️ Restore',
        'sort': '✨ Sort Files',
        'tip': 'Tip: Select a folder to preview classification, then click \'Sort Files\' to execute',
        'confirm_sort': 'Are you sure you want to sort the files?',
        'confirm_restore': 'Are you sure you want to restore all files to the main folder?',
        'sorting': 'Sorting files...',
        'restoring': 'Restoring files...',
        'success_sort': 'Successfully sorted {} files!',
        'success_restore': 'Successfully restored {} files!',
        'error_sort': 'Sorting failed: {}',
        'error_restore': 'Restoration failed: {}',
        'no_file_sort': 'No files to sort in this folder',
        'no_file_restore': 'No files to restore',
        'folder_info': '📊 Folder: {}',
        'total_files': '📁 Found {} files',
        'folder_error': 'Error: Folder does not exist',
        'category': '📂 {} ({} files)',
        'more_files': '   ... {} more files',
        'theme': 'Theme',
        'light': 'Light',
        'dark': 'Dark',
        'auto': 'Auto',
        'language': 'Language',
        'settings': '⚙️ Settings',
    }
}

class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        self.selected_path = None
        
        # 加载配置
        self.load_config()
        
        # 设置主题
        ctk.set_appearance_mode(self.theme_mode)
        ctk.set_default_color_theme("blue")
        
        self.root.title(self.t('title'))
        self.root.geometry("900x750")
        
        # 创建界面
        self.create_widgets()
        
    def load_config(self):
        """加载用户配置"""
        config_path = Path.home() / '.file_sorter_config.json'
        default_config = {
            'language': 'zh',
            'theme': 'auto' if darkdetect.isDark() else 'light'
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.language = config.get('language', 'zh')
                    self.theme_mode = config.get('theme', 'auto')
            except:
                self.language = 'zh'
                self.theme_mode = 'auto'
        else:
            self.language = 'zh'
            self.theme_mode = 'auto'
        
        # 如果是auto模式，根据系统设置
        if self.theme_mode == 'auto':
            self.theme_mode = 'dark' if darkdetect.isDark() else 'light'
    
    def save_config(self):
        """保存用户配置"""
        config_path = Path.home() / '.file_sorter_config.json'
        config = {
            'language': self.language,
            'theme': self.theme_mode
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)
    
    def t(self, key):
        """获取翻译"""
        return TRANSLATIONS[self.language].get(key, key)
    
    def create_widgets(self):
        """创建界面"""
        # 顶部工具栏
        top_frame = ctk.CTkFrame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        title = ctk.CTkLabel(top_frame, text=self.t('title'), font=("微软雅黑", 20, "bold"))
        title.pack(side="left", padx=5)
        
        # 右侧按钮容器
        right_frame = ctk.CTkFrame(top_frame)
        right_frame.pack(side="right", padx=5)
        
        # 语言切换按钮
        lang_display = "中文" if self.language == 'zh' else "English"
        self.btn_lang = ctk.CTkButton(right_frame, text=f"🌐 {lang_display}", 
                                      command=self.toggle_language,
                                      width=100, fg_color="gray80", hover_color="gray70",
                                      font=("微软雅黑", 15))
        self.btn_lang.pack(side="left", padx=5)
        
        # 主题切换按钮
        theme_display = "☀️" if self.theme_mode == 'light' else "🌙" if self.theme_mode == 'dark' else "🔄"
        self.btn_theme = ctk.CTkButton(right_frame, text=theme_display, 
                                       command=self.cycle_theme,
                                       width=50, fg_color="gray80", hover_color="gray70",
                                       font=("微软雅黑", 12))
        self.btn_theme.pack(side="left", padx=5)
        
        # 功能描述
        desc_frame = ctk.CTkFrame(self.root)
        desc_frame.pack(fill="both", padx=20, pady=5)
        
        desc_text = "• 📂 选择文件夹进行分类  • 🔄 支持分类和恢复操作  • ⚡ 多线程后台处理，实时进度显示  • 🎨 深浅模式切换  • 🌐 中英文语言支持"
        if self.language == 'en':
            desc_text = "• 📂 Select folder to sort  • 🔄 Support sort and restore  • ⚡ Multi-threaded with progress bar  • 🎨 Dark/Light theme  • 🌐 Multi-language"
        
        self.desc_label = ctk.CTkLabel(desc_frame, text=desc_text, 
                                       text_color="gray", font=("微软雅黑", 14),
                                       justify="left")
        self.desc_label.pack(anchor="nw", padx=5, fill="both", expand=False)
        
        # 绑定窗口大小变化事件以更新换行宽度（只在第一次创建时绑定）
        if not hasattr(self, '_wraplength_bound'):
            def update_wraplength(event=None):
                try:
                    if hasattr(self, 'desc_label') and self.desc_label.winfo_exists():
                        width = self.root.winfo_width() - 60  # 减去左右padding
                        if width > 100:
                            self.desc_label.configure(wraplength=width)
                except:
                    pass  # Widget已被销毁，忽略错误
            
            self.root.bind('<Configure>', update_wraplength)
            self._wraplength_bound = True
        
        # 文件夹选择区域
        select_frame = ctk.CTkFrame(self.root)
        select_frame.pack(fill="x", padx=20, pady=10)
        self.btn_select = ctk.CTkButton(select_frame, text=self.t('select_folder'), 
                                        command=self.select_folder, 
                                        font=("微软雅黑", 12), width=180)
        self.btn_select.pack(side="left", padx=5)
        
        self.path_label = ctk.CTkLabel(select_frame, text=self.t('no_folder'), 
                                       text_color="gray", font=("微软雅黑", 11))
        self.path_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # 预览区域
        preview_frame = ctk.CTkFrame(self.root)
        preview_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        preview_label = ctk.CTkLabel(preview_frame, text=self.t('preview'), 
                                    font=("微软雅黑", 12, "bold"))
        preview_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.preview_text = ctk.CTkTextbox(preview_frame, font=("Consolas", 10))
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # 进度条
        progress_frame = ctk.CTkFrame(self.root)
        progress_frame.pack(padx=20, pady=10, fill="x")
        
        self.progress_label = ctk.CTkLabel(progress_frame, text=f"{self.t('progress')}: 0%", 
                                          font=("微软雅黑", 15))
        self.progress_label.pack(anchor="w", padx=5, pady=(0, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, mode="determinate")
        self.progress_bar.pack(fill="x", padx=5, pady=(5, 0))
        self.progress_bar.set(0)
        
        # 操作按钮
        action_frame = ctk.CTkFrame(self.root)
        action_frame.pack(pady=15)
        
        self.btn_restore = ctk.CTkButton(action_frame, text=self.t('restore'), 
                                        command=self.restore_files,
                                        font=("微软雅黑", 12), width=150,
                                        fg_color="#FF9800", hover_color="#FF7F00",
                                        state="disabled")
        self.btn_restore.pack(side="left", padx=8)
        
        self.btn_sort = ctk.CTkButton(action_frame, text=self.t('sort'), 
                                     command=self.sort_files,
                                     font=("微软雅黑", 12), width=150,
                                     state="disabled")
        self.btn_sort.pack(side="left", padx=8)
        
        # 提示信息
        info = ctk.CTkLabel(self.root, text=self.t('tip'), 
                           text_color="gray", font=("微软雅黑", 15))
        info.pack(pady=10)
    
    def toggle_language(self):
        """切换语言"""
        self.language = 'en' if self.language == 'zh' else 'zh'
        self.save_config()
        self.refresh_ui()
    
    def cycle_theme(self):
        """循环切换主题"""
        themes = ['light', 'dark', 'auto']
        current_idx = themes.index(self.theme_mode) if self.theme_mode in themes else 0
        self.theme_mode = themes[(current_idx + 1) % len(themes)]
        
        # 应用主题
        if self.theme_mode == 'auto':
            ctk.set_appearance_mode('dark' if darkdetect.isDark() else 'light')
        else:
            ctk.set_appearance_mode(self.theme_mode)
        
        self.save_config()
        self.refresh_theme_button()
    
    def refresh_theme_button(self):
        """刷新主题按钮显示"""
        theme_display = "☀️" if self.theme_mode == 'light' else "🌙" if self.theme_mode == 'dark' else "🔄"
        self.btn_theme.configure(text=theme_display)
    
    def refresh_ui(self):
        """刷新整个UI"""
        # 清空窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 重新创建界面
        self.create_widgets()
        
        # 如果有选中的路径，重新加载预览
        if self.selected_path and self.selected_path.exists():
            self.path_label.configure(text=f"{self.t('selected')}: {self.selected_path}", text_color="green")
            self.preview_classification()
            self.btn_restore.configure(state="normal")
            self.btn_sort.configure(state="normal")
    
    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title=self.t('select_folder'))
        if folder:
            self.selected_path = Path(folder)
            self.path_label.configure(text=f"{self.t('selected')}: {folder}", text_color="green")
            self.preview_classification()
            self.btn_restore.configure(state="normal")
            self.btn_sort.configure(state="normal")
    
    def get_category(self, file_path):
        """获取文件分类"""
        ext = file_path.suffix.lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return '其他' if self.language == 'zh' else 'Other'
    
    def preview_classification(self):
        """预览分类"""
        self.preview_text.delete("1.0", "end")
        
        if not self.selected_path or not self.selected_path.exists():
            self.preview_text.insert("1.0", self.t('folder_error') + "\n")
            return
        
        category_files = {}
        total_files = 0
        
        for file in self.selected_path.iterdir():
            if file.is_file():
                total_files += 1
                category = self.get_category(file)
                if category not in category_files:
                    category_files[category] = []
                category_files[category].append(file.name)
        
        self.preview_text.insert("end", self.t('folder_info').format(self.selected_path.name) + "\n")
        self.preview_text.insert("end", self.t('total_files').format(total_files) + "\n")
        self.preview_text.insert("end", "=" * 60 + "\n\n")
        
        if total_files == 0:
            self.preview_text.insert("end", self.t('no_file_sort') + "\n")
            return
        
        for category in sorted(category_files.keys()):
            files = category_files[category]
            self.preview_text.insert("end", self.t('category').format(category, len(files)) + "\n")
            for file in files[:5]:
                self.preview_text.insert("end", f"   • {file}\n")
            if len(files) > 5:
                self.preview_text.insert("end", self.t('more_files').format(len(files) - 5) + "\n")
            self.preview_text.insert("end", "\n")
    
    def sort_files(self):
        """分类文件"""
        if not self.selected_path:
            messagebox.showwarning("警告", self.t('no_folder'))
            return
        
        if not messagebox.askyesno("确认", self.t('confirm_sort')):
            return
        
        self.btn_restore.configure(state="disabled")
        self.btn_sort.configure(state="disabled")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", self.t('sorting') + "\n")
        self.progress_bar.set(0)
        self.progress_label.configure(text=f"{self.t('progress')}: 0%")
        
        thread = threading.Thread(target=self._sort_files_thread, daemon=True)
        thread.start()
    
    def _sort_files_thread(self):
        """后台分类线程"""
        try:
            total_files = sum(1 for file in self.selected_path.iterdir() if file.is_file())
            
            if total_files == 0:
                self.root.after(0, lambda: messagebox.showinfo("提示", self.t('no_file_sort')))
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
                    
                    progress = int((sorted_count / total_files) * 100)
                    self.root.after(0, lambda p=progress, c=sorted_count, t=total_files: 
                                   self._update_progress(p, c, t))
            
            self.root.after(0, lambda: self._sort_complete(sorted_count))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", self.t('error_sort').format(str(e))))
            self.root.after(0, self._sort_buttons_enable)
    
    def restore_files(self):
        """恢复文件"""
        if not self.selected_path:
            messagebox.showwarning("警告", self.t('no_folder'))
            return
        
        if not messagebox.askyesno("确认", self.t('confirm_restore')):
            return
        
        self.btn_restore.configure(state="disabled")
        self.btn_sort.configure(state="disabled")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", self.t('restoring') + "\n")
        self.progress_bar.set(0)
        self.progress_label.configure(text=f"{self.t('progress')}: 0%")
        
        thread = threading.Thread(target=self._restore_files_thread, daemon=True)
        thread.start()
    
    def _restore_files_thread(self):
        """后台恢复线程"""
        try:
            total_files = sum(1 for folder in self.selected_path.iterdir() 
                            if folder.is_dir() 
                            for file in folder.iterdir() 
                            if file.is_file())
            
            if total_files == 0:
                self.root.after(0, lambda: messagebox.showinfo("提示", self.t('no_file_restore')))
                self.root.after(0, self._restore_buttons_enable)
                return
            
            restored_count = 0
            for folder in self.selected_path.iterdir():
                if folder.is_dir():
                    for file in folder.iterdir():
                        if file.is_file():
                            shutil.move(str(file), str(self.selected_path / file.name))
                            restored_count += 1
                            
                            progress = int((restored_count / total_files) * 100)
                            self.root.after(0, lambda p=progress, c=restored_count, t=total_files: 
                                           self._update_progress(p, c, t))
                    try:
                        folder.rmdir()
                    except:
                        pass
            
            self.root.after(0, lambda: self._restore_complete(restored_count))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", self.t('error_restore').format(str(e))))
            self.root.after(0, self._restore_buttons_enable)
    
    def _update_progress(self, progress, current, total):
        """更新进度条"""
        self.progress_bar.set(progress / 100)
        self.progress_label.configure(text=f"{self.t('progress')}: {progress}% ({current}/{total})")
    
    def _sort_complete(self, sorted_count):
        """分类完成"""
        messagebox.showinfo("完成", self.t('success_sort').format(sorted_count))
        self.preview_classification()
        self._sort_buttons_enable()
    
    def _restore_complete(self, restored_count):
        """恢复完成"""
        messagebox.showinfo("完成", self.t('success_restore').format(restored_count))
        self.preview_classification()
        self._restore_buttons_enable()
    
    def _sort_buttons_enable(self):
        """启用按钮"""
        self.btn_restore.configure(state="normal")
        self.btn_sort.configure(state="normal")
    
    def _restore_buttons_enable(self):
        """启用按钮"""
        self.btn_restore.configure(state="normal")
        self.btn_sort.configure(state="normal")

if __name__ == "__main__":
    root = ctk.CTk()
    app = FileSorterGUI(root)
    root.mainloop()