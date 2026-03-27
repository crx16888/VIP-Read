[app]

title = VIP小说爬取
package.name = noveldownloader
package.domain = org.crx

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,beautifulsoup4,urllib3,certifi

icon.filename = %(source.dir)s/icon.png

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

android.arch = arm64-v8a

android.allow_backup = True

# 使用 Python 3
osx.python_version = 3
osx.kivy_version = 2.3.0

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
