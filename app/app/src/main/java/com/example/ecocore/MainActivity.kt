package com.example.ecocore

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.lifecycle.lifecycleScope
import com.example.ecocore.fragments.AlertFragment
import com.example.ecocore.fragments.ControlFragment
import com.example.ecocore.utils.APIUtils.ApiClient
import com.example.ecocore.utils.APIUtils.ApiService
import com.example.ecocore.utils.AlertStore
import com.example.ecocore.utils.data.DeviceStateStore
import com.google.android.material.bottomnavigation.BottomNavigationView
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var bottomNavigationView: BottomNavigationView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        bottomNavigationView = findViewById(R.id.bottom_navigation)
        supportFragmentManager.beginTransaction().replace(R.id.fragment_container, AlertFragment()).commit()
        createAlertChannel()

        val api = ApiClient.api
        startPollingAlert(api)

        bottomNavigationView.setOnItemSelectedListener { item ->
            when(item.itemId){
                R.id.alerts -> {
                    supportFragmentManager.beginTransaction().replace(R.id.fragment_container,
                        AlertFragment())
                        .commit()
                }

                R.id.control ->{
                    supportFragmentManager.beginTransaction().replace(R.id.fragment_container,
                        ControlFragment()).commit()
                }
            }

            return@setOnItemSelectedListener true
        }

    }

    private fun startPollingAlert(api: ApiService){
        lifecycleScope.launch{
            while (true){
                val alerts = api.getAlert()
                AlertStore.update(alerts, this@MainActivity)
                val status = api.getStatus("Demo Room A")
                //for debugging
                Log.d("RESPONSE STATUS", status.toString())
                DeviceStateStore.update(
                    pump = status.pump_on,
                    power = status.power_on
                )
                delay(3000)
            }
        }
    }

    private fun createAlertChannel() {

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {

            val channel = NotificationChannel(
                "alerts_channel",
                "System Alerts",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Critical system alerts"
                enableVibration(true)
                enableLights(true)
            }

            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }



}