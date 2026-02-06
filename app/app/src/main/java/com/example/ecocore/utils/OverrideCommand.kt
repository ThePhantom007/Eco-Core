package com.example.ecocore.utils

data class OverrideCommand(
    val user: String,
    val utility: String,
    var action: String,
    val room_id: String
)

