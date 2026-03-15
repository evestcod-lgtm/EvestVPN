[app]
title = EveVPN
package.name = evevpn
package.domain = org.eve
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1

# ВАЖНО: Добавлены зависимости для работы сети и интерфейса
requirements = python3,flet,urllib3,certifi,chardet,idna

orientation = portrait
fullscreen = 0

# Разрешения
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, FOREGROUND_SERVICE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

# Архитектура (для большинства современных смартфонов)
android.archs = arm64-v8a

# Автоматическое принятие лицензий (БЕЗ ЭТОГО ГИТХАБ УПАДЕТ)
android.accept_sdk_license = True

# Настройки сборки
android.allow_backup = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
