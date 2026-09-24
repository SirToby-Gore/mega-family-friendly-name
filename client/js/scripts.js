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
var ShopUpgrade = /** @class */ (function () {
    function ShopUpgrade(app, routeElement, name) {
        this.levelIndicator = document.createElement('div');
        this.buttonContainer = document.createElement('div');
        this.buyNewLevelButton = document.createElement('button');
        this.level = 0;
        this.app = app;
        this.routeElement = routeElement;
        this.name = name;
        this.routeElement.classList.add('shop-upgrade');
        this.routeElement.appendChild(this.levelIndicator);
        this.levelIndicator.classList.add('level-indicator');
        this.routeElement.appendChild(this.buttonContainer);
        this.buttonContainer.classList.add('button-container');
        this.buttonContainer.appendChild(this.buyNewLevelButton);
        this.buttonContainer.classList.add('new-level-button');
        this.buyNewLevelButton.onclick = this.buyNewLevel;
        for (var i = 0; i < ShopUpgrade.maxLevel; i++) {
            var newCell = document.createElement('div');
            newCell.classList.add('cell');
            this.levelIndicator.appendChild(newCell);
        }
    }
    ShopUpgrade.prototype.buyNewLevel = function (event) {
        console.log('Buying new level...');
    };
    ShopUpgrade.prototype.updateChildren = function () {
        var i = this.level;
        for (var _i = 0, _a = this.levelIndicator.children; _i < _a.length; _i++) {
            var cell = _a[_i];
            if (i <= 0) {
                break;
            }
            cell.classList.add('active');
        }
    };
    ShopUpgrade.maxLevel = 10;
    return ShopUpgrade;
}());
var MegaFamilyFriendlyNameClient = /** @class */ (function () {
    function MegaFamilyFriendlyNameClient() {
        // UI Cache references
        this.root = document.createElement('div');
        this.shopRoot = document.createElement('div');
        this.shopBody = document.createElement('details');
        this.shopUpgrades = [];
        this.dataCenterRoot = document.createElement('div');
        this.statsRoot = document.createElement('div');
        document.body.innerHTML = '';
        document.body.append(this.root);
        this.root.appendChild(this.shopRoot);
        this.shopRoot.classList.add('shop');
        this.shopRoot.appendChild(this.shopBody);
        this.shopBody.classList.add('shop-body');
        this.root.appendChild(this.dataCenterRoot);
        this.dataCenterRoot.classList.add('data-center-root');
        this.root.appendChild(this.statsRoot);
        this.statsRoot.classList.add('stats');
        this.connectToServer();
    }
    MegaFamilyFriendlyNameClient.prototype.connectToServer = function () {
        var _this = this;
        var protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.socket = new WebSocket("".concat(protocol, "//").concat(window.location.host, "/ws"));
        this.socket.onopen = function () {
            console.info('Pipeline connected directly to the unified server wrapper!');
        };
        this.socket.onmessage = function (event) {
            try {
                var response = jsonDecode(event.data);
                response['status-code'] = 200;
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
    MegaFamilyFriendlyNameClient.prototype.handleServerMessage = function (res) {
        console.table(res);
        if (res['status-code'] >= 400) {
            alert(res.type || 'An error occurred on the server.');
            return;
        }
        switch (res.type
        // todo: put methods here
        ) {
        }
    };
    return MegaFamilyFriendlyNameClient;
}());
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
