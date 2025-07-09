"use strict";

var NotificationManager = function () {
    var socket;

    var initWebSocket = function () {
        socket = new WebSocket("ws://10.91.62.76/ws/notifications/");

        socket.onopen = function () {
            console.log("✅ WebSocket Connected");
        };

        socket.onmessage = function (event) {
            var data = JSON.parse(event.data);

            if (data.notification) {
                handleNotification(data.notification);
            }
        };

        socket.onerror = function (error) {
            console.error("❌ WebSocket Error:", error);
        };

        socket.onclose = function (event) {
            console.log("🔴 WebSocket Closed:", event);
        };
    };

    var handleNotification = function (message) {
        if (message.includes("🛠️ A new block")) {
            showNotification("📦 New Block Created!", message);
        } else {
            showNotification("🔔 Notification", message);
        }
    };

    var showNotification = function (title, message) {
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
