package com.example.ecocore.utils

import android.os.Build
import androidx.annotation.RequiresApi
import java.time.format.DateTimeFormatter
import java.util.Locale

import java.time.LocalDateTime

object TimeUtils {

    @RequiresApi(Build.VERSION_CODES.O)
    fun formatAlertTime(raw: String): String {
        return try {
            val parser = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS")

            val dateTime = LocalDateTime.parse(raw, parser)

            val output = DateTimeFormatter.ofPattern("hh:mm a", Locale.getDefault())

            dateTime.format(output)

        } catch (e: Exception) {
            raw // fallback so app doesn't crash
        }
    }
}
