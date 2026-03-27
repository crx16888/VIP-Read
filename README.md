# 全网VIP小说爬取 - 安卓版

将 Python 小说爬取工具打包为安卓 APK 安装包。

## 环境要求

- Python 3.8+
- Linux 系统（Ubuntu 推荐）或 macOS + Docker
- Java JDK 17

## 方法一：Linux 下直接构建

```bash
# 1. 安装系统依赖 (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 构建 APK（首次构建约需 20-30 分钟）
buildozer android debug

# 4. APK 输出位置
# bin/noveldownloader-1.0.0-arm64-v8a-debug.apk
```

## 方法二：macOS 使用 Docker 构建

```bash
# 1. 安装 Docker Desktop (如果还没装)
# https://www.docker.com/products/docker-desktop

# 2. 拉取 Buildozer Docker 镜像
docker pull kivy/buildozer

# 3. 在项目目录下运行构建
docker run --rm -v $(pwd):/home/user/hostcwd kivy/buildozer android debug

# 4. APK 输出位置
# bin/noveldownloader-1.0.0-arm64-v8a-debug.apk
```

## 方法三：使用 Google Colab 云端构建（推荐新手）

1. 打开 [Google Colab](https://colab.research.google.com)
2. 新建笔记本，依次运行：

```python
# 安装 buildozer
!pip install buildozer cython
!sudo apt install -y openjdk-17-jdk autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev cmake libffi-dev libssl-dev

# 上传 main.py 和 buildozer.spec 到 Colab 工作目录

# 构建
!buildozer android debug

# 下载 APK
from google.colab import files
files.download('bin/noveldownloader-1.0.0-arm64-v8a-debug.apk')
```

## 安装 APK

1. 将 APK 传输到手机
2. 在手机上打开文件管理器找到 APK
3. 点击安装（需要允许"安装未知来源应用"）

## 功能说明

- 搜索小说：输入小说名称，搜索全网 VIP 小说
- 章节浏览：查看完整章节目录
- 在线阅读：直接阅读章节内容
- 自动保存：章节自动保存为 txt 文件到手机 Download/小说下载/ 目录
- 上下翻页：阅读界面支持上一章/下一章快速切换
