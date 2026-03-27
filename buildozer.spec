[app]

title = VIP Novel
package.name = noveldownloader
package.domain = org.crx

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = desktop,.github,.git

version = 1.0.0

requirements = python3,kivy==2.3.0,beautifulsoup4,soupsieve

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a

android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
