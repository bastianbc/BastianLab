"use strict";

var NotificationManager = (function () {
    var notifSocket;
    var logSocket;

    // ──────── Initialization ────────
    function init() {
        initNotificationSocket();
        initLogSocket();
    }

    // ──────── Notification WS ────────
    function initNotificationSocket() {
        notifSocket = new WebSocket("ws://10.65.11.68:8000/ws/notifications/");

        notifSocket.onopen = function () {
            console.log("✅ Notification WS Connected");
        };

        notifSocket.onmessage = function (event) {
            var data = JSON.parse(event.data);
            if (data.notification) {
                handleNotification(data.notification);
            }
        };

        notifSocket.onerror = function (error) {
            console.error("❌ Notification WS Error:", error);
        };

        notifSocket.onclose = function (event) {
            console.log("🔴 Notification WS Closed:", event);
        };
    }

    function handleNotification(message) {
        if (message.includes("🛠️ A new block")) {
            showNotification("📦 New Block Created!", message);
        } else {
            showNotification("🔔 Notification", message);
        }
    }

    function showNotification(title, message) {
        Swal.fire({
            title: title,
            text: message,
            icon: "info",
            toast: true,
            position: "top-end",
            showConfirmButton: false,
            timer: 5000,
            timerProgressBar: true
        });
    }

    // ──────── Log‐Streaming WS ────────
    function initLogSocket() {
        logSocket = new WebSocket("ws://10.65.11.68:8000/ws/logs/");

        logSocket.onopen = function () {
            console.log("✅ Log WS Connected");
        };

        logSocket.onmessage = function (event) {
            // event.data is your raw log line
            outputLog(event.data);
        };

        logSocket.onerror = function (error) {
            console.error("❌ Log WS Error:", error);
        };

        logSocket.onclose = function (event) {
            console.log("🔴 Log WS Closed:", event);
        };
    }

    // Stub for handling incoming log lines—
    // swap console.log for appending into your DOM as needed.
    function outputLog(logLine) {
        console.log("📜 LOG:", logLine);
        // e.g. to dump into a <pre id="log-output">:
        // document.getElementById("log-output").textContent += logLine + "\n";
    }

    return {
        init: init
    };
}());

// Initialize when the page loads
KTUtil.onDOMContentLoaded(function () {
    NotificationManager.init();
});
