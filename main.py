import json
import urllib.request
import urllib.parse
import os
import threading
from bs4 import BeautifulSoup

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.properties import StringProperty, ListProperty

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.INTERNET, Permission.WRITE_EXTERNAL_STORAGE,
                         Permission.READ_EXTERNAL_STORAGE])

HEADERS_UA = ('Mozilla/5.0 (Linux; Android 13; Pixel 7) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/116.0.0.0 Mobile Safari/537.36')


class SearchScreen(Screen):
    status_text = StringProperty("请输入图书名称并点击搜索")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        title = Label(text="[b]全网VIP小说爬取[/b]", markup=True,
                      font_size=sp(22), size_hint_y=None, height=dp(48))
        root.add_widget(title)

        search_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.book_input = TextInput(hint_text="输入小说名称...", multiline=False,
                                    font_size=sp(16), size_hint_x=0.7)
        self.book_input.bind(on_text_validate=lambda *_: self.search())
        search_btn = Button(text="搜索", font_size=sp(16), size_hint_x=0.3,
                            background_color=(0.2, 0.6, 1, 1))
        search_btn.bind(on_release=lambda *_: self.search())
        search_row.add_widget(self.book_input)
        search_row.add_widget(search_btn)
        root.add_widget(search_row)

        scroll = ScrollView()
        self.results_layout = GridLayout(cols=1, spacing=dp(6),
                                         size_hint_y=None, padding=[0, dp(4)])
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        scroll.add_widget(self.results_layout)
        root.add_widget(scroll)

        self.status_label = Label(text=self.status_text, font_size=sp(13),
                                  size_hint_y=None, height=dp(32),
                                  color=(0.5, 0.5, 0.5, 1))
        self.bind(status_text=self.status_label.setter('text'))
        root.add_widget(self.status_label)

        self.add_widget(root)

    def search(self):
        book_name = self.book_input.text.strip()
        if not book_name:
            self.show_popup("提示", "请输入图书名!")
            return
        self.status_text = "正在搜索..."
        self.results_layout.clear_widgets()
        threading.Thread(target=self._search_thread, args=(book_name,), daemon=True).start()

    def _search_thread(self, book_name):
        try:
            q = urllib.parse.quote(book_name)
            url = f'https://www.bqgui.cc/user/search.html?q={q}'
            data = json.loads(NetHelper.get_page(url, q))
            if not data or data == 1:
                Clock.schedule_once(lambda dt: self._on_search_empty())
                return
            Clock.schedule_once(lambda dt: self._on_search_done(data, book_name))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_popup("错误", str(e)))
            Clock.schedule_once(lambda dt: setattr(self, 'status_text', "搜索出错"))

    def _on_search_empty(self):
        self.status_text = "未找到相关图书"
        self.show_popup("提示", "未找到相关图书，请换个关键词试试")

    def _on_search_done(self, data, book_name):
        app = App.get_running_app()
        app.book_list = data
        app.book_url_list = ['https://www.bqgui.cc/' + b['url_list'] for b in data]
        app.search_query = book_name

        self.results_layout.clear_widgets()
        for i, book in enumerate(data):
            btn = Button(
                text=f"[b]{book['articlename']}[/b]  作者: {book['author']}\n{book.get('intro', '')[:60]}",
                markup=True, font_size=sp(14), size_hint_y=None, height=dp(72),
                background_color=(0.15, 0.15, 0.2, 1),
                halign='left', valign='middle', text_size=(Window.width - dp(40), None)
            )
            btn.idx = i
            btn.bind(on_release=self._on_book_tap)
            self.results_layout.add_widget(btn)

        self.status_text = f"找到 {len(data)} 本图书，点击查看章节"

    def _on_book_tap(self, btn):
        app = App.get_running_app()
        app.current_book_index = btn.idx
        chapter_screen = app.sm.get_screen('chapters')
        chapter_screen.load_chapters()
        app.sm.transition = SlideTransition(direction='left')
        app.sm.current = 'chapters'

    def show_popup(self, title, msg):
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=msg, font_size=sp(15)))
        close_btn = Button(text="确定", size_hint_y=None, height=dp(44))
        content.add_widget(close_btn)
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.4))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()


class ChapterScreen(Screen):
    status_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        top_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        back_btn = Button(text="← 返回", size_hint_x=0.25, font_size=sp(14))
        back_btn.bind(on_release=lambda *_: self.go_back())
        self.title_label = Label(text="章节列表", font_size=sp(17),
                                 markup=True, size_hint_x=0.75)
        top_row.add_widget(back_btn)
        top_row.add_widget(self.title_label)
        root.add_widget(top_row)

        scroll = ScrollView()
        self.chapter_layout = GridLayout(cols=1, spacing=dp(4),
                                          size_hint_y=None, padding=[0, dp(4)])
        self.chapter_layout.bind(minimum_height=self.chapter_layout.setter('height'))
        scroll.add_widget(self.chapter_layout)
        root.add_widget(scroll)

        self.status_label = Label(text="", font_size=sp(13),
                                  size_hint_y=None, height=dp(32),
                                  color=(0.5, 0.5, 0.5, 1))
        self.bind(status_text=self.status_label.setter('text'))
        root.add_widget(self.status_label)

        self.add_widget(root)

    def go_back(self):
        app = App.get_running_app()
        app.sm.transition = SlideTransition(direction='right')
        app.sm.current = 'search'

    def load_chapters(self):
        app = App.get_running_app()
        idx = app.current_book_index
        book = app.book_list[idx]
        self.title_label.text = f"[b]《{book['articlename']}》[/b]"
        self.status_text = "正在加载章节列表..."
        self.chapter_layout.clear_widgets()
        threading.Thread(target=self._load_thread, args=(app,), daemon=True).start()

    def _load_thread(self, app):
        try:
            idx = app.current_book_index
            book_url = app.book_url_list[idx]
            q = urllib.parse.quote(app.search_query)
            html = NetHelper.get_page(book_url, q)
            soup = BeautifulSoup(html, 'html.parser')
            listmain = soup.find('div', class_='listmain')
            links = listmain.find_all('a') if listmain else []

            chapter_list = []
            for a in links:
                href = a.get('href', '')
                if href == 'javascript:dd_show()':
                    continue
                chapter_list.append({
                    'catalogue_name': a.get_text(strip=True),
                    'catalogue_url': 'https://www.bqgui.cc/' + href
                })

            app.chapter_list = chapter_list
            Clock.schedule_once(lambda dt: self._on_loaded(chapter_list))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_err(str(e)))

    def _on_loaded(self, chapter_list):
        self.chapter_layout.clear_widgets()
        for i, ch in enumerate(chapter_list):
            btn = Button(
                text=f"{i+1}. {ch['catalogue_name']}",
                font_size=sp(14), size_hint_y=None, height=dp(48),
                background_color=(0.12, 0.12, 0.18, 1),
                halign='left', valign='middle',
                text_size=(Window.width - dp(40), None)
            )
            btn.idx = i
            btn.bind(on_release=self._on_chapter_tap)
            self.chapter_layout.add_widget(btn)
        self.status_text = f"共 {len(chapter_list)} 章，点击阅读"

    def _on_chapter_tap(self, btn):
        app = App.get_running_app()
        reader = app.sm.get_screen('reader')
        reader.load_content(btn.idx)
        app.sm.transition = SlideTransition(direction='left')
        app.sm.current = 'reader'

    def _show_err(self, msg):
        self.status_text = "加载出错"
        screen = App.get_running_app().sm.get_screen('search')
        screen.show_popup("错误", msg)


class ReaderScreen(Screen):
    status_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        top_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        back_btn = Button(text="← 返回", size_hint_x=0.2, font_size=sp(14))
        back_btn.bind(on_release=lambda *_: self.go_back())
        self.ch_title = Label(text="", font_size=sp(16), markup=True, size_hint_x=0.6)

        nav_row = BoxLayout(size_hint_x=0.2, spacing=dp(4))
        prev_btn = Button(text="上", font_size=sp(14))
        next_btn = Button(text="下", font_size=sp(14))
        prev_btn.bind(on_release=lambda *_: self.prev_chapter())
        next_btn.bind(on_release=lambda *_: self.next_chapter())
        nav_row.add_widget(prev_btn)
        nav_row.add_widget(next_btn)

        top_row.add_widget(back_btn)
        top_row.add_widget(self.ch_title)
        top_row.add_widget(nav_row)
        root.add_widget(top_row)

        self.scroll = ScrollView()
        self.content_label = Label(
            text="", font_size=sp(16), markup=False,
            size_hint_y=None, halign='left', valign='top',
            padding=[dp(8), dp(8)],
            text_size=(Window.width - dp(40), None)
        )
        self.content_label.bind(texture_size=self.content_label.setter('size'))
        self.scroll.add_widget(self.content_label)
        root.add_widget(self.scroll)

        self.status_label = Label(text="", font_size=sp(13),
                                  size_hint_y=None, height=dp(28),
                                  color=(0.5, 0.5, 0.5, 1))
        self.bind(status_text=self.status_label.setter('text'))
        root.add_widget(self.status_label)

        self.add_widget(root)
        self.current_idx = 0

    def go_back(self):
        app = App.get_running_app()
        app.sm.transition = SlideTransition(direction='right')
        app.sm.current = 'chapters'

    def prev_chapter(self):
        if self.current_idx > 0:
            self.load_content(self.current_idx - 1)

    def next_chapter(self):
        app = App.get_running_app()
        if self.current_idx < len(app.chapter_list) - 1:
            self.load_content(self.current_idx + 1)

    def load_content(self, idx):
        self.current_idx = idx
        app = App.get_running_app()
        ch = app.chapter_list[idx]
        self.ch_title.text = f"[b]{ch['catalogue_name']}[/b]"
        self.content_label.text = "正在加载..."
        self.scroll.scroll_y = 1
        self.status_text = "加载中..."
        threading.Thread(target=self._load_thread, args=(app, idx), daemon=True).start()

    def _load_thread(self, app, idx):
        try:
            ch = app.chapter_list[idx]
            q = urllib.parse.quote(app.search_query)
            html = NetHelper.get_page(ch['catalogue_url'], q)
            soup = BeautifulSoup(html, 'html.parser')
            div = soup.find('div', id='chaptercontent')
            if div:
                for br in div.find_all('br'):
                    br.replace_with('\n')
                text = div.get_text().replace('\u3000', '')
                lines = [l for l in text.splitlines() if l.strip()]
                text = '\n\n'.join(lines)
            else:
                text = "无法获取章节内容"

            book_name = app.book_list[app.current_book_index]['articlename']
            chapter_name = ch['catalogue_name']

            save_dir = self._get_save_dir(book_name)
            os.makedirs(save_dir, exist_ok=True)
            safe_name = chapter_name.replace('/', '_').replace('\\', '_')
            save_path = os.path.join(save_dir, f'{safe_name}.txt')
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)

            Clock.schedule_once(lambda dt: self._on_loaded(text, save_path, idx, app))
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self, 'status_text', f"加载出错: {e}"))
            Clock.schedule_once(
                lambda dt: setattr(self.content_label, 'text', f"加载出错:\n{e}"))

    def _get_save_dir(self, book_name):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            base = primary_external_storage_path()
            return os.path.join(base, 'Download', '小说下载', book_name)
        return os.path.join(os.path.expanduser('~'), '小说下载', book_name)

    def _on_loaded(self, text, save_path, idx, app):
        self.content_label.text = text
        total = len(app.chapter_list)
        self.status_text = f"第 {idx+1}/{total} 章 | 已保存到: {save_path}"


class NetHelper:
    @staticmethod
    def get_cookie(q):
        url = f'https://www.bqgui.cc/user/hm.html?q={q}'
        headers = {'User-Agent': HEADERS_UA}
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.getheader('Set-Cookie') or ''

    @staticmethod
    def get_page(url, q):
        cookie = NetHelper.get_cookie(q)
        headers = {
            'Cookie': cookie,
            'Referer': f'https://www.bqgui.cc/s?q={q}',
            'User-Agent': HEADERS_UA,
        }
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.read().decode('utf-8')


class NovelApp(App):
    book_list = ListProperty([])
    book_url_list = ListProperty([])
    chapter_list = ListProperty([])
    search_query = StringProperty('')
    current_book_index = 0

    def build(self):
        self.title = '全网VIP小说爬取'
        Window.clearcolor = (0.08, 0.08, 0.1, 1)
        self.sm = ScreenManager()
        self.sm.add_widget(SearchScreen(name='search'))
        self.sm.add_widget(ChapterScreen(name='chapters'))
        self.sm.add_widget(ReaderScreen(name='reader'))
        return self.sm


if __name__ == '__main__':
    NovelApp().run()
