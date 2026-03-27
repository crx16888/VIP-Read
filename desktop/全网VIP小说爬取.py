# import json
# import sys
# import urllib.request
# from lxml import etree
# import urllib.parse
# from prettytable import PrettyTable

# # 该代码没有写gui界面，所以无法打包成.exe文件
# # 所以应当用gui界面替代.exe文件

# book_name = input('请输入需要爬取的图书名:\n')

# q = urllib.parse.quote(book_name)
# url = f'https://www.bqgui.cc/user/search.html?q={q}'


# def get_cookie():
#     url1 = f'https://www.bqgui.cc/user/hm.html?q={q}'
#     headers = {
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
#     }
#     request = urllib.request.Request(url=url1, headers=headers)
#     response = urllib.request.urlopen(request)
#     cookie = response.getheader('Set-Cookie')
#     return cookie


# def get_book(url):
#     headers = {
#         'cookie': get_cookie(),
#         'referer': f'https://www.bqgui.cc/s?q={q}',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
#     }
#     request = urllib.request.Request(url=url, headers=headers)
#     response = urllib.request.urlopen(request)
#     content = response.read().decode('utf-8')
#     return content


# # 获取图书列表
# book_list = json.loads(get_book(url))
# if len(book_list) == 0:
#     print('图书列表为空，请重新输入!')
#     sys.exit()
# if book_list == 1:
#     print('图书获取失败！')
#     sys.exit()
# print('获取图书列表成功！')

# table = PrettyTable()
# table.field_names = [
#     '序号',
#     '图书名称',
#     '作者',
#     '背景',
# ]
# book_url_list = []
# for index in range(len(book_list)):
#     table.add_row([
#         index + 1,
#         book_list[index]['articlename'],
#         book_list[index]['author'],
#         book_list[index]['intro'],
#     ])
#     book_url_list.append('https://www.bqgui.cc/' + book_list[index]['url_list'])
# print(table)

# # 获取图书目录
# index = int(input('请输入要看的图书序号:\n')) - 1
# book_name = book_list[index]['articlename']
# book_url = book_url_list[index]
# catalogue = get_book(book_url)
# tree = etree.HTML(catalogue)

# catalogue_name = tree.xpath('//div[@class="listmain"]/dl//dd/a/text()')
# catalogue_url = tree.xpath('//div[@class="listmain"]/dl//dd/a/@href')
# chapter_list = []

# for index in range(len(catalogue_url)):
#     if catalogue_url[index] == 'javascript:dd_show()':
#         continue
#     chapter_list.append({
#         'catalogue_name': catalogue_name[index],
#         'catalogue_url': 'https://www.bqgui.cc/' + catalogue_url[index]
#     })
# print(f'获取图书目录成功，总共有{len(chapter_list)}章!')

# while True:
#     # 获取图书章节
#     start = int(input('请输入要看的起始章节序号:(输入0退出程序!)\n')) - 1
#     end = int(input('请输入要看的终止章节序号:(输入0退出程序!)\n'))
#     if start >= end:
#         print('起始章节不能大于结束章节，请重新输入!')
#         continue
#     if start == -1 or end == 0:
#         break
#     for index in range(start, end):
#         chapter_name = chapter_list[index]['catalogue_name']
#         chapter_url = chapter_list[index]['catalogue_url']
#         chapter = get_book(chapter_url)
#         tree = etree.HTML(chapter)
#         chapter_result = tree.xpath('//div[@id="chaptercontent"]/text()')
#         text = ''
#         for i in range(0, len(chapter_result) - 2):
#             text += chapter_result[i].replace('\u3000', '')
#         print(chapter_name + ':\n' + text)
#         open(f'{book_name}（{chapter_name}）.txt', 'w', encoding='utf-8').write(text)


# 以下是GUI界面版本的代码
import json
import sys
import urllib.request
from lxml import etree
import urllib.parse
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext, ttk
import os
import threading

class NovelDownloader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("全网VIP小说爬取")
        self.root.geometry("800x600")
        self.setup_ui()
        # 显示欢迎提示
        self.show_welcome_tips()
        
    def setup_ui(self):
        # 搜索框
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="请输入需要爬取的图书名:").pack(side=tk.LEFT)
        self.book_entry = tk.Entry(search_frame, width=30)
        self.book_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="搜索", command=self.search_book).pack(side=tk.LEFT)
        
        # 添加帮助按钮
        help_button = tk.Button(search_frame, text="使用帮助", command=self.show_help)
        help_button.pack(side=tk.LEFT, padx=10)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪 - 请输入图书名称并点击搜索")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建选项卡
        self.tab_control = ttk.Notebook(self.root)
        
        # 图书列表选项卡
        self.book_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.book_tab, text="图书列表")
        
        # 章节列表选项卡
        self.chapter_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.chapter_tab, text="章节列表")
        
        # 阅读内容选项卡
        self.content_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.content_tab, text="阅读内容")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # 图书列表区域
        self.book_frame = tk.Frame(self.book_tab)
        self.book_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加图书列表提示标签
        self.book_tip_label = tk.Label(self.book_frame, text="请在上方输入框中输入图书名称并点击搜索按钮\n搜索结果将显示在此处\n双击图书可查看章节列表", justify=tk.CENTER)
        self.book_tip_label.pack(expand=True)
        
        # 章节列表区域
        self.chapter_frame = tk.Frame(self.chapter_tab)
        self.chapter_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加章节列表提示标签
        self.chapter_tip_label = tk.Label(self.chapter_frame, text="请先搜索并选择一本图书\n章节列表将显示在此处\n双击章节可阅读内容\n按住Ctrl键可选择多个章节进行批量下载", justify=tk.CENTER)
        self.chapter_tip_label.pack(expand=True)
        
        # 章节内容显示区域
        self.content_tab_frame = tk.Frame(self.content_tab)
        self.content_tab_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加内容提示标签
        self.content_tip_label = tk.Label(self.content_tab_frame, text="请先选择一个章节\n章节内容将显示在此处\n内容会自动保存为txt文件", justify=tk.CENTER)
        self.content_tip_label.pack(expand=True)
        
        self.text_area = scrolledtext.ScrolledText(self.content_tab_frame, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.pack_forget()  # 初始隐藏
        
        # 下载按钮区域
        download_frame = tk.Frame(self.chapter_tab)
        download_frame.pack(fill=tk.X, pady=5)
        
        # 添加提示标签
        tk.Label(download_frame, text="提示: 选择多个章节后点击下方按钮可批量下载").pack(side=tk.LEFT, padx=5)
        tk.Button(download_frame, text="批量下载选中章节", command=self.batch_download).pack(side=tk.LEFT, padx=5)
        
    def show_welcome_tips(self):
        """显示欢迎提示"""
        messagebox.showinfo("欢迎使用", 
            "欢迎使用全网VIP小说爬取工具!\n\n"
            "使用步骤:\n"
            "1. 在搜索框输入小说名称并点击搜索\n"
            "2. 在图书列表中双击选择要阅读的书籍\n"
            "3. 在章节列表中双击选择要阅读的章节\n"
            "4. 可以选择多个章节后点击批量下载按钮\n\n"
            "所有下载的章节都会保存为txt文件\n"
            "如需帮助，请点击界面上的\"使用帮助\"按钮")
    
    def show_help(self):
        """显示帮助信息"""
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("600x400")
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
【全网VIP小说爬取工具使用指南】

1. 搜索图书
   - 在顶部输入框中输入小说名称
   - 点击"搜索"按钮
   - 搜索结果将显示在"图书列表"选项卡中

2. 查看章节
   - 在图书列表中双击您想要阅读的书籍
   - 章节列表将显示在"章节列表"选项卡中
   - 状态栏会显示当前操作的状态

3. 阅读章节
   - 在章节列表中双击您想要阅读的章节
   - 章节内容将显示在"阅读内容"选项卡中
   - 章节内容会自动保存为txt文件，保存在程序所在目录

4. 批量下载
   - 在章节列表中按住Ctrl键可选择多个章节
   - 选择完成后点击"批量下载选中章节"按钮
   - 下载进度将显示在状态栏中

5. 文件保存
   - 所有章节内容都会自动保存为txt文件
   - 文件命名格式为"书名（章节名）.txt"
   - 文件保存在程序所在的目录中

6. 操作提示
   - 界面底部的状态栏会显示当前操作的状态
   - 如果操作出错，会弹出错误提示窗口
   - 每个选项卡都有相应的操作提示

如有其他问题，请联系开发者。
        """
        
        help_text.insert(tk.END, help_content)
        help_text.configure(state='disabled')  # 设置为只读
        
        # 添加关闭按钮
        tk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=10)
    
    def search_book(self):
        book_name = self.book_entry.get()
        if not book_name:
            messagebox.showwarning("警告", "请输入图书名!")
            return
            
        self.status_var.set("正在搜索图书...")
        self.root.update()
        
        # 使用线程避免界面卡顿
        threading.Thread(target=self._search_book_thread, args=(book_name,), daemon=True).start()
    
    def _search_book_thread(self, book_name):
        try:
            q = urllib.parse.quote(book_name)
            url = f'https://www.bqgui.cc/user/search.html?q={q}'
            
            # 获取图书列表
            book_list = json.loads(self.get_book(url, q))
            if len(book_list) == 0:
                self.root.after(0, lambda: messagebox.showinfo("提示", "图书列表为空，请重新输入!"))
                self.root.after(0, lambda: self.status_var.set("搜索完成，未找到图书"))
                return
            if book_list == 1:
                self.root.after(0, lambda: messagebox.showinfo("提示", "图书获取失败！"))
                self.root.after(0, lambda: self.status_var.set("搜索失败"))
                return
                
            # 清空之前的结果
            self.root.after(0, lambda: self._clear_frame(self.book_frame))
            
            # 创建图书列表
            self.book_list = book_list
            self.book_url_list = []
            
            # 创建表格
            columns = ("序号", "图书名称", "作者", "背景")
            self.book_tree = ttk.Treeview(self.book_frame, columns=columns, show="headings")
            
            # 设置列宽
            self.book_tree.column("序号", width=50)
            self.book_tree.column("图书名称", width=200)
            self.book_tree.column("作者", width=100)
            self.book_tree.column("背景", width=400)
            
            # 设置表头
            for col in columns:
                self.book_tree.heading(col, text=col)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(self.book_frame, orient="vertical", command=self.book_tree.yview)
            self.book_tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            self.book_tree.pack(expand=True, fill="both")
            
            # 添加操作提示标签
            tip_label = tk.Label(self.book_frame, text="提示: 双击图书可查看章节列表", fg="blue")
            tip_label.pack(pady=5)
            
            # 填充数据
            for i, book in enumerate(book_list):
                self.book_tree.insert("", "end", values=(
                    i + 1,
                    book['articlename'],
                    book['author'],
                    book['intro']
                ))
                self.book_url_list.append('https://www.bqgui.cc/' + book['url_list'])
            
            # 绑定双击事件
            self.book_tree.bind("<Double-1>", self.on_book_select)
            
            self.root.after(0, lambda: self.status_var.set(f"搜索完成，找到 {len(book_list)} 本图书 - 双击图书可查看章节"))
            self.root.after(0, lambda: self.tab_control.select(self.book_tab))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"搜索图书时出错: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("搜索出错"))
    
    def on_book_select(self, event):
        selected_item = self.book_tree.selection()[0]
        book_idx = int(self.book_tree.item(selected_item)["values"][0]) - 1
        self.view_book(book_idx)
    
    def view_book(self, index):
        self.current_book_index = index
        book_name = self.book_list[index]['articlename']
        book_url = self.book_url_list[index]
        
        self.status_var.set(f"正在获取《{book_name}》的目录...")
        self.root.update()
        
        # 使用线程避免界面卡顿
        threading.Thread(target=self._view_book_thread, args=(book_name, book_url), daemon=True).start()
    
    def _view_book_thread(self, book_name, book_url):
        try:
            # 获取图书目录
            q = urllib.parse.quote(self.book_entry.get())
            catalogue = self.get_book(book_url, q)
            tree = etree.HTML(catalogue)
            
            catalogue_name = tree.xpath('//div[@class="listmain"]/dl//dd/a/text()')
            catalogue_url = tree.xpath('//div[@class="listmain"]/dl//dd/a/@href')
            self.chapter_list = []
            
            for i in range(len(catalogue_url)):
                if catalogue_url[i] == 'javascript:dd_show()':
                    continue
                self.chapter_list.append({
                    'catalogue_name': catalogue_name[i],
                    'catalogue_url': 'https://www.bqgui.cc/' + catalogue_url[i]
                })
                
            # 清空之前的结果
            self.root.after(0, lambda: self._clear_frame(self.chapter_frame))
            
            # 创建章节列表
            columns = ("序号", "章节名称")
            self.chapter_tree = ttk.Treeview(self.chapter_frame, columns=columns, show="headings")
            
            # 设置列宽
            self.chapter_tree.column("序号", width=50)
            self.chapter_tree.column("章节名称", width=700)
            
            # 设置表头
            for col in columns:
                self.chapter_tree.heading(col, text=col)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(self.chapter_frame, orient="vertical", command=self.chapter_tree.yview)
            self.chapter_tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            self.chapter_tree.pack(expand=True, fill="both")
            
            # 添加操作提示标签
            tip_frame = tk.Frame(self.chapter_frame)
            tip_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(tip_frame, text="提示: ", fg="blue").pack(side=tk.LEFT)
            tk.Label(tip_frame, text="1. 双击章节可阅读内容").pack(side=tk.LEFT)
            tk.Label(tip_frame, text="2. 按住Ctrl键可选择多个章节").pack(side=tk.LEFT, padx=10)
            
            # 填充数据
            for i, chapter in enumerate(self.chapter_list):
                self.chapter_tree.insert("", "end", values=(
                    i + 1,
                    chapter['catalogue_name']
                ))
            
            # 绑定双击事件
            self.chapter_tree.bind("<Double-1>", self.on_chapter_select)
            
            self.root.after(0, lambda: self.status_var.set(f"获取《{book_name}》目录成功，共 {len(self.chapter_list)} 章 - 双击章节可阅读内容"))
            self.root.after(0, lambda: self.tab_control.select(self.chapter_tab))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"获取图书目录时出错: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("获取目录出错"))
    
    def on_chapter_select(self, event):
        selected_item = self.chapter_tree.selection()[0]
        chapter_idx = int(self.chapter_tree.item(selected_item)["values"][0]) - 1
        self.read_chapter(chapter_idx)
    
    def read_chapter(self, index):
        chapter_name = self.chapter_list[index]['catalogue_name']
        chapter_url = self.chapter_list[index]['catalogue_url']
        book_name = self.book_list[self.current_book_index]['articlename']
        
        self.status_var.set(f"正在获取《{book_name}》的《{chapter_name}》内容...")
        self.root.update()
        
        # 使用线程避免界面卡顿
        threading.Thread(target=self._read_chapter_thread, args=(index, book_name, chapter_name, chapter_url), daemon=True).start()
    
    def _read_chapter_thread(self, index, book_name, chapter_name, chapter_url):
        try:
            q = urllib.parse.quote(self.book_entry.get())
            chapter = self.get_book(chapter_url, q)
            tree = etree.HTML(chapter)
            chapter_result = tree.xpath('//div[@id="chaptercontent"]/text()')
            
            text = ''
            for i in range(0, len(chapter_result) - 2):
                text += chapter_result[i].replace('\u3000', '')
                
            # 清空内容选项卡
            self.root.after(0, lambda: self._clear_frame(self.content_tab_frame))
            
            # 显示章节内容
            self.root.after(0, lambda: self._setup_content_view(book_name, chapter_name, text))
            
            # 保存章节内容
            save_path = f'{book_name}（{chapter_name}）.txt'
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)
                
            self.root.after(0, lambda: self.status_var.set(f"已获取并保存《{chapter_name}》到: {os.path.abspath(save_path)}"))
            self.root.after(0, lambda: self.tab_control.select(self.content_tab))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"获取章节内容时出错: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("获取章节内容出错"))
    
    def _setup_content_view(self, book_name, chapter_name, text):
        """设置内容阅读视图"""
        # 创建新的内容区域
        text_area = scrolledtext.ScrolledText(self.content_tab_frame, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)
        
        # 添加标题和保存信息
        info_frame = tk.Frame(self.content_tab_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(info_frame, text=f"《{book_name}》 - {chapter_name}", font=("黑体", 12, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(info_frame, text=f"(已保存为: {book_name}（{chapter_name}）.txt)", fg="green").pack(side=tk.LEFT, padx=5)
        
        # 显示章节内容
        text_area.insert(tk.END, text)
        text_area.configure(state='disabled')  # 设置为只读
        
        # 将内容区域放在最上面
        info_frame.pack_forget()
        info_frame.pack(fill=tk.X, pady=5, before=text_area)
    
    def batch_download(self):
        if not hasattr(self, 'chapter_list') or not self.chapter_list:
            messagebox.showwarning("警告", "请先选择一本书并加载章节列表!")
            return
            
        selected_items = self.chapter_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要下载的章节!\n(按住Ctrl键可选择多个章节)")
            return
            
        book_name = self.book_list[self.current_book_index]['articlename']
        chapter_indices = [int(self.chapter_tree.item(item)["values"][0]) - 1 for item in selected_items]
        
        if messagebox.askyesno("确认", f"确定要下载选中的 {len(chapter_indices)} 个章节吗?\n\n下载的文件将保存在程序所在目录"):
            self.status_var.set(f"正在批量下载《{book_name}》的章节...")
            self.root.update()
            
            # 使用线程避免界面卡顿
            threading.Thread(target=self._batch_download_thread, args=(book_name, chapter_indices), daemon=True).start()
    
    def _batch_download_thread(self, book_name, chapter_indices):
        try:
            q = urllib.parse.quote(self.book_entry.get())
            total = len(chapter_indices)
            
            for i, index in enumerate(chapter_indices):
                chapter_name = self.chapter_list[index]['catalogue_name']
                chapter_url = self.chapter_list[index]['catalogue_url']
                
                self.root.after(0, lambda i=i, name=chapter_name: self.status_var.set(f"正在下载 ({i+1}/{total}): {name}"))
                
                chapter = self.get_book(chapter_url, q)
                tree = etree.HTML(chapter)
                chapter_result = tree.xpath('//div[@id="chaptercontent"]/text()')
                
                text = ''
                for j in range(0, len(chapter_result) - 2):
                    text += chapter_result[j].replace('\u3000', '')
                    
                save_path = f'{book_name}（{chapter_name}）.txt'
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                    
            self.root.after(0, lambda: messagebox.showinfo("提示", f"批量下载完成!\n\n已下载 {total} 个章节\n保存在: {os.path.abspath('.')}"))
            self.root.after(0, lambda: self.status_var.set(f"批量下载完成，共 {total} 个章节"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"批量下载时出错: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("批量下载出错"))
    
    def _clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
    
    def get_cookie(self, q):
        url1 = f'https://www.bqgui.cc/user/hm.html?q={q}'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
        }
        request = urllib.request.Request(url=url1, headers=headers)
        response = urllib.request.urlopen(request)
        cookie = response.getheader('Set-Cookie')
        return cookie
    
    def get_book(self, url, q):
        headers = {
            'cookie': self.get_cookie(q),
            'referer': f'https://www.bqgui.cc/s?q={q}',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
        }
        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request)
        content = response.read().decode('utf-8')
        return content
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NovelDownloader()
    app.run()










