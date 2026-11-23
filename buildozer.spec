[app]
title = Jahider Nur
package.name = jahidernur
package.domain = org.jahidernur
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.accept_sdk_license = True
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO,BLUETOOTH,BLUETOOTH_CONNECT,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
p4a.bootstrap = sdl2
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
