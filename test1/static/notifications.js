const $logMessages = $('#log-messages');

    if ($logMessages.length === 0) {
        console.warn('jQuery: Element with ID "log-messages" not found. Messages will not be displayed.');
        // Optionally, create the element if it doesn't exist
        // $('body').append('<div id="log-messages" style="border: 1px solid #ccc; padding: 10px; margin-top: 10px; height: 200px; overflow-y: scroll;"></div>');
        // $logMessages = $('#log-messages'); // Re-select
    }

    // Determine WebSocket protocol (ws or wss)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsHost = window.location.host;
    const socketUrl = wsProtocol + wsHost + '/ws/logging/'; // Matches the path in routing.py

    console.log('Attempting to connect to WebSocket at: ' + socketUrl);
    const loggingSocket = new WebSocket(socketUrl);

    loggingSocket.onopen = function(e) {
        console.log("WebSocket connection established successfully.");
        $logMessages.append('<p><em>Connection opened. Waiting for logs...</em></p>');
    };

    loggingSocket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);
            const message = data.message;
            console.log("Message from server: ", message);
            // Append the message to the log display area
            $logMessages.append('<p>' + escapeHtml(message) + '</p>');
            // Scroll to the bottom of the log display
        } catch (error) {
            console.error("Error parsing message from server or updating DOM:", error);
        }
    };

    loggingSocket.onclose = function(e) {
        if (e.wasClean) {
            console.log(`WebSocket connection closed cleanly, code=${e.code} reason=${e.reason}`);
            $logMessages.append('<p><em>Connection closed by server.</em></p>');
        } else {
            // e.g. server process killed or network down
            // event.code is usually 1006 in this case
            console.error('WebSocket connection died unexpectedly.');
            $logMessages.append('<p><em>Connection died unexpectedly. Refresh to try again.</em></p>');
        }
    };

    loggingSocket.onerror = function(error) {
        console.error(`WebSocket Error: ${error.message || 'Unknown error'}`);
        console.error(error); // Log the full error object for more details
        $logMessages.append('<p><em>WebSocket error. See console for details.</em></p>');
    };

    // Helper function to escape HTML to prevent XSS
    function escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') {
            return '';
        }
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }


// "use strict";
//
// var NotificationManager = function () {
//     var socket;
//
//     var initWebSocket = function () {
//         socket = new WebSocket("ws://10.65.11.68/ws/notifications/");
//
//         socket.onopen = function () {
//             console.log("✅ WebSocket Connected");
//         };
//
//         socket.onmessage = function (event) {
//             var data = JSON.parse(event.data);
//
//             if (data.notification) {
//                 handleNotification(data.notification);
//             }
//         };
//
//         socket.onerror = function (error) {
//             console.error("❌ WebSocket Error:", error);
//         };
//
//         socket.onclose = function (event) {
//             console.log("🔴 WebSocket Closed:", event);
//         };
//     };
//
//     var handleNotification = function (message) {
//         if (message.includes("🛠️ A new block")) {
//             showNotification("📦 New Block Created!", message);
//         } else {
//             showNotification("🔔 Notification", message);
//         }
//     };
//
//     var showNotification = function (title, message) {
//         Swal.fire({
//             title: title,
//             text: message,
//             icon: "info",
//             toast: true,
//             position: "top-end",
//             showConfirmButton: false,
//             timer: 5000,
//             timerProgressBar: true
//         });
//     };
//
//     return {
//         init: function () {
//             initWebSocket();
//         }
//     };
// }();
//
// // Initialize when the page loads
// KTUtil.onDOMContentLoaded(function () {
//     NotificationManager.init();
// });
