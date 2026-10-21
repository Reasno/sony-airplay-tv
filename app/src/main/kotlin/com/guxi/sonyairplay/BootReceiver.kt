package com.guxi.sonyairplay

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.core.content.ContextCompat
import com.guxi.sonyairplay.service.AirPlayService

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val supportedAction = intent.action == Intent.ACTION_BOOT_COMPLETED ||
            intent.action == Intent.ACTION_MY_PACKAGE_REPLACED ||
            intent.action == "android.intent.action.QUICKBOOT_POWERON"
        if (!supportedAction) return

        val prefs = context.getSharedPreferences(Prefs.NAME, Context.MODE_PRIVATE)
        if (!prefs[Prefs.BOOT_AUTO_START]) return
        if (!prefs.getBoolean(AirPlayService.RECEIVER_ENABLED, true)) return

        val serviceIntent = Intent(context, AirPlayService::class.java)
            .setAction(AirPlayService.ACTION_START_SERVER)
        try {
            ContextCompat.startForegroundService(context, serviceIntent)
        } catch (e: IllegalStateException) {
            Log.w("AirPlayService", "System blocked background startup; open Sony AirPlay to start", e)
        } catch (e: SecurityException) {
            Log.w("AirPlayService", "Permission required for background startup", e)
        }
    }
}
