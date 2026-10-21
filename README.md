# Sony AirPlay TV

运行在 Sony Android TV / Google TV 上的 AirPlay 接收项目，应用包名为 `com.guxi.sonyairplay`。

相关项目：[Sony TV Home](https://github.com/Reasno/sony-tv-home) · [Sony HA Voice](https://github.com/Reasno/sony-ha-voice)。

默认以后台前台服务接收连接，空闲时退出显示页；镜像、视频播放和 PIN 配对期间显示全屏画面。系统要求的服务通知保持存在。电视必须处于开机、联网状态，手机和电视处于同一可互通子网，路由器允许 mDNS 多播。应用不能保证唤醒处于深度待机的电视。

## 接收能力

| 内容 | 实现 |
| --- | --- |
| iPhone / iPad / Mac 屏幕镜像 | UxPlay 解密接收，MediaCodec 解码 H.264 / H.265，SurfaceView 显示 |
| App 内 AirPlay 视频 | UxPlay 视频会话与 HLS 播放列表代理，Media3 ExoPlayer 播放 |
| 镜像声音 | AAC 解码和 Oboe 音频输出 |
| PIN 配对 | 可配置 PIN 验证，全屏显示验证码 |

DRM 受保护内容（例如 Apple TV App 的受保护节目）不支持。App 内视频是否可投取决于发送端是否提供接收器可访问的视频地址 / HLS 会话及其编码；本项目不承诺所有 App、全部 AirPlay 2 能力或 Apple 官方认证。Sony 具体型号、系统版本和 Apple 发送端版本需真机验证。

## 构建

使用 JDK 21、Android SDK platform 37、NDK `27.0.12077973` 和 CMake `3.22.1`。Gradle Wrapper 与库版本在仓库中固定。

```bash
git submodule update --init --recursive
./gradlew assembleDebug lintDebug
```

APK：`app/build/outputs/apk/debug/app-debug.apk`。包含 `armeabi-v7a`、`arm64-v8a`、`x86_64`，兼顾使用 32 位 Android 系统的电视。

`.github/workflows/apk.yml` 在 push、PR 或手动运行时构建 APK 并运行 Android lint，构建产物名为 `sony-airplay-tv-debug`，不依赖发布签名密钥。含原生 C/C++ 的编译在 CI 或 Linux 开发机进行。

已提供 `dist/sony-airplay-tv-0.1.0-debug.apk`，包含三个架构。电视安装、发现、镜像和 App 内投屏按下方步骤验收。

## 安装到电视

在电视开发者选项中启用 ADB 调试。电脑需要 Android SDK platform-tools，电视需要允许电脑的调试连接。旧版 Android TV 常用端口为 5555；支持无线配对的系统需先按电视界面的端口执行 `adb pair`。

```bash
python3 scripts/tv.py connect 192.168.1.20:5555
python3 scripts/tv.py --serial 192.168.1.20:5555 install
```

将地址换成电视地址。安装脚本安装 APK、授予“显示在其他应用上层”权限、设置后台接收和自动启动，然后打开应用启动服务。Android 13+ 如出现通知授权提示，在电视上接受；Android 17+ 还需要本地网络权限。权限未获得时应用保留管理界面，便于授权。

服务启动后，电视显示页空闲两秒退出。发送端选择 `Sony TV AirPlay`，镜像或播放开始后自动显示画面；结束后显示页退出，服务继续监听。Android / Sony 系统对后台 Activity 的限制仍需真机检查。用户强行停止应用后，需要再次手动打开；后台恢复不等同于深度待机唤醒。

## 管理

```bash
python3 scripts/tv.py --serial 192.168.1.20:5555 settings
python3 scripts/tv.py --serial 192.168.1.20:5555 status
python3 scripts/tv.py --serial 192.168.1.20:5555 logs
python3 scripts/tv.py --serial 192.168.1.20:5555 set server_name 'Living Room Sony'
python3 scripts/tv.py --serial 192.168.1.20:5555 set require_pin true
python3 scripts/tv.py --serial 192.168.1.20:5555 set headless false
```

`settings` 保持管理页打开，可在 Overview 中停止 / 启动服务，在 Settings 中配置参数。`headless=false` 使用带播放控制和设置的界面。接收器需要重启的配置会触发服务自动重启，当前会话会中断。默认 `require_pin=false`。

## 真机验收

1. 确认发送端发现 `Sony TV AirPlay`，电视桌面上无需常驻接收界面。
2. iPhone 控制中心开启屏幕镜像，检查画面、横竖屏、声音和连续播放。
3. 在支持 AirPlay 的 App 中投非 DRM 视频，检查 HLS / 直接链接播放、手机暂停和拖动进度。
4. 结束镜像 / 播放，确认显示页退出且可重新连接；切换镜像与视频，确认画面显示正确。
5. 开启 `require_pin` 后重新连接，检查电视 PIN 显示和发送端配对。
6. 电视重启后检查可发现性，再单独检查遥控待机和唤醒后的网络 / 服务行为。

## 协议与许可证

项目基于 [jqssun/android-airplay-server](https://github.com/jqssun/android-airplay-server)，基线 commit 为 `a46cca0a6a1274e9e33c0e750f0f1c1eb1d881ea`，协议底座为 [UxPlay](https://github.com/FDH2/UxPlay)。原生依赖通过 Git 子模块固定。许可证为 GPL-3.0，见 `LICENSE`；各第三方依赖保留各自许可证。FFmpeg 提供软件音频解码，上游播放器参考 Next Player。

本项目与 Apple 或 Sony 无官方关联。
