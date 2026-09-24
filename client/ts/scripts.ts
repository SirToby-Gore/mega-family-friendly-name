interface GameState {
	tick: number;
	day: number;
	money: number;
	water: number;
	energy: number;
	requests: number;
	population_satisfaction: number;
	energy_generation_rate: number;
	energy_consumption_rate: number;
	water_consumption_rate: number;
	water_collection_rate: number;
	power_reliability: number;
	size: number;
	emissions: number;
	defeat: boolean;
	upgrades?: Record<string, any>;
}

interface ServerResponse {
	type: string;
	values?: {
		state?: {
			version: number;
			state: GameState;
		};
	};
}

class ShopUpgrade {
	private routeElement: HTMLDivElement;
	private levelIndicator: HTMLDivElement = document.createElement('div');
	private buttonContainer: HTMLDivElement = document.createElement('div');
	private buyNewLevelButton: HTMLButtonElement = document.createElement('button');

	private name: string;
	private level: number = 0;
	static maxLevel: number = 10;

	constructor(routeElement: HTMLDivElement, name: string) {
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

	buyNewLevel = (event: Event) => {
		console.log(`Buying new level for ${this.name}...`);
	};

	setLevel(level: number) {
		this.level = Math.min(level, ShopUpgrade.maxLevel);
		this.updateChildren();
	}

	updateChildren() {
		const cells = Array.from(this.levelIndicator.children);
		cells.forEach((cell, index) => {
			if (index < this.level) {
				cell.classList.add('active');
			} else {
				cell.classList.remove('active');
			}
		});
	}
}

class MegaFamilyFriendlyNameClient {
	private socket!: WebSocket;

	private root: HTMLElement = document.createElement('div');
	private statsRoot: HTMLDivElement = document.createElement('div');
	private shopRoot: HTMLDivElement = document.createElement('div');
	private shopBody: HTMLDetailsElement = document.createElement('details');
	private shopSummary: HTMLElement = document.createElement('summary');
	private shopUpgrades: Record<string, ShopUpgrade> = {};
	private dataCenterRoot: HTMLDivElement = document.createElement('div');

	private messageHandlers: Record<string, (res: ServerResponse) => void> = {};

	constructor() {
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

	private registerHandlers(): void {
		this.messageHandlers = {
			snapshot: this.handleSnapshot,
			error: this.handleServerError,
			card_spawned: this.handleCardSpawned,
		};
	}

	private handleSnapshot = (res: ServerResponse): void => {
		const stateData = res.values?.state?.state;
		if (!stateData) return;

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

	private handleServerError = (res: ServerResponse): void => {
		console.error('Server Error:', res);
	};

	private handleCardSpawned = (res: ServerResponse): void => {
		console.log('Card Spawn Event:', res);
	};

	public registerHandler(type: string, handler: (res: ServerResponse) => void): void {
		this.messageHandlers[type] = handler;
	}

	private connectToServer(): void {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		this.socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

		this.socket.onmessage = (event) => {
			try {
				const response: ServerResponse = JSON.parse(event.data);
				this.handleServerMessage(response);
			} catch (err) {
				console.error('Failed to parse incoming transmission:', err);
			}
		};
	}

	private sendToServer(request: string, payload: Record<string, any> = {}): void {
		if (this.socket.readyState === WebSocket.OPEN) {
			this.socket.send(JSON.stringify({ request, ...payload }));
		}
	}

	private handleServerMessage(res: ServerResponse): void {
		const handler = this.messageHandlers[res.type];
		if (handler) {
			handler(res);
		}
	}
}

document.addEventListener('DOMContentLoaded', () => {
	new MegaFamilyFriendlyNameClient();
});
