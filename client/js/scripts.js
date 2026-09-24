class ShopUpgrade {
    constructor(routeElement, name) {
        this.levelIndicator = document.createElement('div');
        this.buttonContainer = document.createElement('div');
        this.buyNewLevelButton = document.createElement('button');
        this.level = 0;
        this.buyNewLevel = (event) => {
            console.log(`Buying new level for ${this.name}...`);
        };
        this.routeElement = routeElement;
        this.name = name;
        this.routeElement.classList.add('shop-upgrade');
        this.routeElement.appendChild(this.levelIndicator);
        this.levelIndicator.classList.add('level-indicator');
        this.routeElement.appendChild(this.buttonContainer);
        this.buttonContainer.classList.add('button-container');
        this.buttonContainer.appendChild(this.buyNewLevelButton);
        this.buyNewLevelButton.classList.add('new-level-button');
        this.buyNewLevelButton.innerText = `Upgrade ${this.name}`;
        this.buyNewLevelButton.onclick = this.buyNewLevel;
        for (let i = 0; i < ShopUpgrade.maxLevel; i++) {
            const newCell = document.createElement('div');
            newCell.classList.add('cell');
            this.levelIndicator.appendChild(newCell);
        }
    }
    setLevel(level) {
        this.level = Math.min(level, ShopUpgrade.maxLevel);
        this.updateChildren();
    }
    updateChildren() {
        const cells = Array.from(this.levelIndicator.children);
        cells.forEach((cell, index) => {
            if (index < this.level) {
                cell.classList.add('active');
            }
            else {
                cell.classList.remove('active');
            }
        });
    }
}
ShopUpgrade.maxLevel = 10;
class MegaFamilyFriendlyNameClient {
    constructor() {
        this.root = document.createElement('div');
        this.statsRoot = document.createElement('div');
        this.shopRoot = document.createElement('div');
        this.shopBody = document.createElement('details');
        this.shopSummary = document.createElement('summary');
        this.shopUpgrades = {};
        this.dataCenterRoot = document.createElement('div');
        this.messageHandlers = {};
        this.handleSnapshot = (res) => {
            const stateData = res.values?.state?.state;
            if (!stateData)
                return;
            this.statsRoot.innerHTML = `
            <div><strong>Day:</strong> ${stateData.day}</div>
            <div><strong>Money:</strong> $${(stateData.money / 100).toFixed(2)}</div>
            <div><strong>Water:</strong> ${stateData.water.toFixed(1)} (${stateData.water_collection_rate.toFixed(2)} in / ${stateData.water_consumption_rate.toFixed(2)} out)</div>
            <div><strong>Energy:</strong> ${stateData.energy.toFixed(1)} (${stateData.energy_generation_rate.toFixed(2)} in / ${stateData.energy_consumption_rate.toFixed(2)} out)</div>
            <div><strong>Satisfaction:</strong> ${stateData.population_satisfaction.toFixed(1)}%</div>
            <div><strong>Reliability:</strong> ${stateData.power_reliability.toFixed(1)}%</div>
        `;
            if (stateData.upgrades) {
                this.shopBody.open = true;
                for (const [key, upgradeData] of Object.entries(stateData.upgrades)) {
                    if (!this.shopUpgrades[key]) {
                        const upgradeDiv = document.createElement('div');
                        this.shopBody.appendChild(upgradeDiv);
                        this.shopUpgrades[key] = new ShopUpgrade(upgradeDiv, upgradeData.name || key);
                    }
                    this.shopUpgrades[key].setLevel(upgradeData.level || 0);
                }
            }
        };
        this.handleServerError = (res) => {
            console.error('Server Error:', res);
        };
        this.handleCardSpawned = (res) => {
            console.log('Card Spawn Event:', res);
        };
        document.body.innerHTML = '';
        document.body.append(this.root);
        this.root.appendChild(this.statsRoot);
        this.statsRoot.classList.add('stats');
        this.root.appendChild(this.shopRoot);
        this.shopRoot.classList.add('shop');
        this.shopSummary.innerText = 'Shop Upgrades';
        this.shopBody.appendChild(this.shopSummary);
        this.shopRoot.appendChild(this.shopBody);
        this.shopBody.classList.add('shop-body');
        this.root.appendChild(this.dataCenterRoot);
        this.dataCenterRoot.classList.add('data-center-root');
        this.registerHandlers();
        this.connectToServer();
    }
    registerHandlers() {
        this.messageHandlers = {
            snapshot: this.handleSnapshot,
            error: this.handleServerError,
            card_spawned: this.handleCardSpawned,
        };
    }
    registerHandler(type, handler) {
        this.messageHandlers[type] = handler;
    }
    connectToServer() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.socket = new WebSocket(`${protocol}//${window.location.host}/ws`);
        this.socket.onmessage = (event) => {
            try {
                const response = JSON.parse(event.data);
                this.handleServerMessage(response);
            }
            catch (err) {
                console.error('Failed to parse incoming transmission:', err);
            }
        };
    }
    sendToServer(request, payload = {}) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ request, ...payload }));
        }
    }
    handleServerMessage(res) {
        const handler = this.messageHandlers[res.type];
        if (handler) {
            handler(res);
        }
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new MegaFamilyFriendlyNameClient();
});
