package com.example.ecocore.fragments

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.appcompat.widget.SwitchCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.example.ecocore.R
import com.example.ecocore.utils.APIUtils.ApiClient
import com.example.ecocore.utils.data.DeviceStateStore
import com.example.ecocore.utils.data.OverrideCommand
import kotlinx.coroutines.launch

class ControlFragment(): Fragment(){

    private lateinit var waterStatus: TextView
    private lateinit var powerStatus: TextView
    private lateinit var waterToggleButton: SwitchCompat
    private lateinit var powerToggleButton: SwitchCompat

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.control_fragment, container, false)

        waterStatus = view.findViewById(R.id.tvWaterStatus)
        powerStatus = view.findViewById(R.id.tvPowerStatus)

        waterToggleButton = view.findViewById(R.id.switchWater)
        powerToggleButton = view.findViewById(R.id.switchPower)

        val api = ApiClient.api
        DeviceStateStore.observe {

            waterToggleButton.isChecked = DeviceStateStore.pumpOn
            powerToggleButton.isChecked = DeviceStateStore.powerOn

            if (DeviceStateStore.pumpOn){
                waterStatus.setTextColor(Color.GREEN)
                waterStatus.text = "Status: ON"
            }
            if (DeviceStateStore.powerOn){
                powerStatus.setTextColor(Color.GREEN)
                powerStatus.text = "Status: ON"
            }
        }


        waterToggleButton.setOnCheckedChangeListener { _, isChecked ->
            val cmd = OverrideCommand(
                user = "User",
                utility = "WATER",
                action = "OFF",
                room_id = "Demo Room A"
            )
            if (isChecked){
                lifecycleScope.launch {
                    cmd.action = "ON"
                    api.sendOverride(cmd)
                    waterStatus.text = "Status: ON"
                    waterStatus.setTextColor(Color.GREEN)
                }
            }else{
                lifecycleScope.launch {
                    cmd.action="OFF"
                    api.sendOverride(cmd)
                    waterStatus.text = "Status: OFF"
                    waterStatus.setTextColor(Color.RED)
                }
            }
        }

        powerToggleButton.setOnCheckedChangeListener { _, isChecked ->
            val cmd = OverrideCommand(
                user = "User",
                utility = "POWER",
                action = "OFF",
                room_id = "Demo Room A"
            )
            if (isChecked){
                lifecycleScope.launch {
                    cmd.action = "ON"
                    api.sendOverride(cmd)
                    powerStatus.text = "Status: ON"
                    powerStatus.setTextColor(Color.GREEN)
                }
            }else{
                lifecycleScope.launch {
                    cmd.action="OFF"
                    api.sendOverride(cmd)
                    powerStatus.text = "Status: OFF"
                    powerStatus.setTextColor(Color.RED)
                }
            }
        }

        return view
    }
}