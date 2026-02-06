package com.example.ecocore.utils

object DeviceStateStore {

    // ---- state ----
    var pumpOn: Boolean = false
        private set

    var powerOn: Boolean = false
        private set

    // ---- listeners ----
    private val listeners = mutableListOf<() -> Unit>()

    // ---- update from API ----
    fun update(pump: Boolean, power: Boolean) {
        val changed = (pumpOn != pump) || (powerOn != power)

        pumpOn = pump
        powerOn = power

        if (changed) notifyListeners()
    }

    // ---- observe ----
    fun observe(listener: () -> Unit) {
        listeners.add(listener)
        listener() // send current immediately
    }

    fun remove(listener: () -> Unit) {
        listeners.remove(listener)
    }

    private fun notifyListeners() {
        listeners.forEach { it() }
    }
}
