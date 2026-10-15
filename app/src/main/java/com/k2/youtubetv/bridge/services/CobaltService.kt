package com.k2.youtubetv.bridge.services

interface CobaltService {
    val serviceName: String

    fun onOpen(serviceId: Int, sender: (String) -> Unit)
    fun onReceive(serviceId: Int, data: String)
    fun onClose(serviceId: Int)
}
