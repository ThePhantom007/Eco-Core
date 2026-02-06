package com.example.ecocore.utils

import android.Manifest
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import androidx.annotation.RequiresPermission
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.example.ecocore.MainActivity
import com.example.ecocore.R

object AlertNotificationHelper {

    @RequiresPermission(Manifest.permission.POST_NOTIFICATIONS)
    fun show(context: Context, alert: Alert) {

        val intent = Intent(context, MainActivity::class.java).apply {
            putExtra("open_alerts", true)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            alert.id,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, "alerts_channel")
            .setSmallIcon(R.drawable.warning) // your icon
            .setContentTitle(alert.type.replace("_", " "))
            .setContentText(alert.message)
            .setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText(
                        "${alert.message}\n" +
                                "Savings ${alert.estimated_savings} • " +
                                "Confidence ${alert.probability_score}"
                    )
            )
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()

        NotificationManagerCompat.from(context)
            .notify(alert.id, notification)
    }
}
