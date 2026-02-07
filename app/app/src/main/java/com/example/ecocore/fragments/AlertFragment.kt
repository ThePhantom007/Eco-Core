package com.example.ecocore.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.ecocore.R
import com.example.ecocore.databinding.AlertFragmentBinding
import com.example.ecocore.utils.data.Alert
import com.example.ecocore.utils.AlertAdapter
import com.example.ecocore.utils.AlertStore

class AlertFragment(): Fragment() {
    private lateinit var adapter: AlertAdapter
    private var _binding: AlertFragmentBinding? = null
    private val binding get() = _binding!!

    private lateinit var alertListener: (List<Alert>) -> Unit

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        _binding = AlertFragmentBinding.inflate(inflater, container, false)

        adapter = AlertAdapter()

        binding.alertRc.layoutManager = LinearLayoutManager(requireContext())
        binding.alertRc.adapter = adapter
        alertListener = { alerts ->
            adapter.submitList(alerts.toList())
        }
        AlertStore.observe(alertListener)

        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        AlertStore.remove(alertListener)
    }
}