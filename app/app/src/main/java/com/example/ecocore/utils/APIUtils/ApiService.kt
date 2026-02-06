package com.example.ecocore.utils.APIUtils

import com.example.ecocore.utils.Alert
import com.example.ecocore.utils.DeviceStatus
import com.example.ecocore.utils.OverrideCommand
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface ApiService {

    @GET("api/history/alerts")
    suspend fun getAlert(): List<Alert>

    @POST("api/control/override")
    suspend fun sendOverride(
        @Body command: OverrideCommand
    )

    @GET("/api/status/{roomId}")
    suspend fun getStatus(
        @Path("roomId") roomId: String
    ): DeviceStatus


}