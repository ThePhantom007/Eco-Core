package com.example.ecocore.utils.data

data class Alert(
    val id: Int,
    val time: String,
    val type: String,
    val message: String,
    val probable_wastage: String,
    val estimated_savings: String,
    val probability_score: String,
    val action: String,
    val status: String
)