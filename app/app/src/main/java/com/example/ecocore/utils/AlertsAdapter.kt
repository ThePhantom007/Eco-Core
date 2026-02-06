package com.example.ecocore.utils

import android.os.Build
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.ecocore.R

class AlertAdapter(
    private val onClick: ((Alert) -> Unit)? = null
) : ListAdapter<Alert, AlertAdapter.AlertViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AlertViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.alert_card, parent, false)

        return AlertViewHolder(view)
    }

    override fun onBindViewHolder(holder: AlertViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class AlertViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {

        private val tvTime = itemView.findViewById<TextView>(R.id.tvTime)
        private val tvType = itemView.findViewById<TextView>(R.id.tvType)
        private val tvMessage = itemView.findViewById<TextView>(R.id.tvMessage)
        private val tvImpact = itemView.findViewById<TextView>(R.id.tvImpact)
        private val tvSavings = itemView.findViewById<TextView>(R.id.tvSavings)
        private val tvConfidence = itemView.findViewById<TextView>(R.id.tvConfidence)
        private val tvStatus = itemView.findViewById<TextView>(R.id.tvStatus)

        fun bind(alert: Alert) {

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                tvTime.text = TimeUtils.formatAlertTime(alert.time)
            }else{
                tvTime.text = alert.time
            }
            tvType.text = alert.type
            tvMessage.text = alert.message

            tvImpact.text = alert.probable_wastage ?: "-"
            tvSavings.text = alert.estimated_savings ?: "-"
            tvConfidence.text = alert.probability_score ?: "-"
            tvStatus.text = alert.action ?: alert.status ?: "-"

            setColors(alert)

            itemView.setOnClickListener {
                onClick?.invoke(alert)
            }
        }

        private fun setColors(alert: Alert) {
            val ctx = itemView.context

            when {
                alert.type.contains("CRITICAL") -> {
                    tvType.setTextColor(ctx.getColor(R.color.alert_red))
                    tvImpact.setTextColor(ctx.getColor(R.color.alert_red))
                }

                alert.type.contains("ENERGY") -> {
                    tvType.setTextColor(ctx.getColor(R.color.alert_yellow))
                }

                else -> {
                    tvType.setTextColor(ctx.getColor(R.color.alert_green))
                }
            }
        }
    }

    class DiffCallback : DiffUtil.ItemCallback<Alert>() {
        override fun areItemsTheSame(oldItem: Alert, newItem: Alert) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Alert, newItem: Alert) =
            oldItem == newItem
    }
}
