var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var MegaFamilyFriendlyNameClient = /** @class */ (function () {
    // UI Cache references
    function MegaFamilyFriendlyNameClient() {
    }
    MegaFamilyFriendlyNameClient.prototype.connectToServer = function () {
        var _this = this;
        var protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.socket = new WebSocket("".concat(protocol, "//").concat(window.location.host));
        this.socket.onopen = function () {
            console.info('Pipeline connected directly to the unified server wrapper!');
        };
        this.socket.onmessage = function (event) {
            try {
                var response = jsonDecode(event.data);
                _this.handleServerMessage(response);
            }
            catch (err) {
                console.error('Failed to parse incoming transmission:', err);
            }
        };
        this.socket.onclose = function () {
            console.error('Pipeline disconnected');
        };
    };
    MegaFamilyFriendlyNameClient.prototype.sendToServer = function (request, payload) {
        if (payload === void 0) { payload = {}; }
        this.socket.send(JSON.stringify(__assign({ request: request }, payload)));
    };
    /// todo: change me
    MegaFamilyFriendlyNameClient.prototype.joinGame = function () {
        var input = document.getElementById('username-input');
        var name = input.value.trim();
        this.sendToServer('join-game', { name: name });
    };
    MegaFamilyFriendlyNameClient.prototype.handleServerMessage = function (res) {
        if (res['status-code'] >= 400) {
            alert(res.message || 'An error occurred on the server.');
            return;
        }
        switch (res.request
        // todo: put methods here
        ) {
        }
    };
    return MegaFamilyFriendlyNameClient;
}());
// Global window event safely preventing disconnect alerts
window.addEventListener('beforeunload', function (event) {
    event.preventDefault();
    event.returnValue = 'Are you sure you want to leave the game session?';
    return event.returnValue;
});
// Helper function to safely parse server-side layout variables
function jsonDecode(data) {
    return JSON.parse(data);
}
function jsonEncode(data) {
    return JSON.stringify(data);
}
// Fire up client core runtime
document.addEventListener('DOMContentLoaded', function () {
    new MegaFamilyFriendlyNameClient();
});
