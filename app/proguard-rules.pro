# Keep JNI callback interface (called from native code)
-keep class com.guxi.sonyairplay.bridge.RaopCallbackHandler { *; }
-keep class * implements com.guxi.sonyairplay.bridge.RaopCallbackHandler { *; }
-keep class com.guxi.sonyairplay.bridge.LogListener { *; }
-keep class * implements com.guxi.sonyairplay.bridge.LogListener { *; }

# Keep NativeBridge native methods
-keep class com.guxi.sonyairplay.bridge.NativeBridge { *; }
