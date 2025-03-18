"use strict";

var NotificationManager = function () {
    var socket;

    var initWebSocket = function () {
        socket = new WebSocket("ws://10.65.11.68/ws/notifications/");

        socket.onopen = function () {
            console.log("✅ WebSocket Connected");
        };

        socket.onmessage = function (event) {
            var data = JSON.parse(event.data);
            if (data.notification) {
                showNotification(data.notification);
            }
        };

        socket.onerror = function (error) {
            console.error("❌ WebSocket Error:", error);
        };

        socket.onclose = function (event) {
            console.log("🔴 WebSocket Closed:", event);
        };
    };

    var showNotification = function (message) {
        Swal.fire({
            title: "🔔 Notification",
            text: message,
            icon: "info",
            toast: true,
            position: "top-end",
            showConfirmButton: false,
            timer: 5000,
            timerProgressBar: true
        });
    };

    return {
        init: function () {
            initWebSocket();
        }
    };
}();

// Initialize when the page loads
KTUtil.onDOMContentLoaded(function () {
    NotificationManager.init();
});
