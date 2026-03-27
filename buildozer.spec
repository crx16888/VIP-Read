[app]

title = VIP Novel
package.name = noveldownloader
package.domain = org.crx

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = desktop,.github,.git

version = 1.0.0

requirements = python3,kivy,beautifulsoup4,soupsieve,certifi,hostpython3

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

android.arch = arm64-v8a

android.allow_backup = True

p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
