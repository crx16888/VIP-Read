# VIP-Read 全网VIP小说爬取

搜索、阅读、下载全网 VIP 小说。提供 **安卓版** 和 **桌面版** 两个版本。

## 下载安装

前往 [Releases](https://github.com/crx16888/VIP-Read/releases) 页面下载最新 APK，传到手机安装即可。

> 安装时如提示"未知来源"，请在手机设置中允许安装。

## 项目结构

```
├── main.py              # 安卓版 (Kivy)
├── buildozer.spec       # APK 打包配置
├── requirements.txt     # Python 依赖
├── .github/workflows/   # GitHub Actions 自动构建
└── desktop/
    └── 全网VIP小说爬取.py  # 桌面版 (tkinter)
```

## 功能

- 搜索全网 VIP 小说
- 在线阅读章节内容
- 自动保存章节到本地
- 上一章/下一章快速切换
- 批量下载（桌面版）

## 本地构建 APK

如需自行构建，推送带 `v` 前缀的 tag 即可触发 GitHub Actions 自动构建：

```bash
git tag v1.0.0
git push origin v1.0.0
```

也可手动构建：

```bash
pip install buildozer cython
buildozer android debug
```
