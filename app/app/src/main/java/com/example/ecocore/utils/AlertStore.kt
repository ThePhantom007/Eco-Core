package com.example.ecocore.utils

import android.content.Context

object AlertStore {

    private val _alerts = mutableListOf<Alert>()
    val alerts: List<Alert> get() = _alerts

    private val seenIds = mutableSetOf<Int>()

    private val listeners = mutableListOf<(List<Alert>) -> Unit>()


    fun update(newAlerts: List<Alert>, context: Context? = null) {

        var changed = false

        for (alert in newAlerts) {
            if (!seenIds.contains(alert.id)) {

                seenIds.add(alert.id)
                _alerts.add(0, alert)

                // 🔥 notify immediately
                context?.let {
                    AlertNotificationHelper.show(it, alert)
                }

                changed = true
            }
        }

        if (changed) notifyListeners()
    }

    fun observe(listener: (List<Alert>) -> Unit) {
        listeners.add(listener)
        listener(_alerts) // send current data immediately
    }

    fun remove(listener: (List<Alert>) -> Unit) {
        listeners.remove(listener)
    }

    private fun notifyListeners() {
        listeners.forEach { it(_alerts) }
    }
}

