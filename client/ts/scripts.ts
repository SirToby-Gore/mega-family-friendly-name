interface ServerResponse {
	type: string;
	state: Map<string, any>;
	'status-code': number;
}

class ShopUpgrade {
	private app: MegaFamilyFriendlyNameClient;

	private routeElement: HTMLDivElement;
	private levelIndicator: HTMLDivElement = document.createElement('div');
	private buttonContainer: HTMLDivElement = document.createElement('div');
	private buyNewLevelButton: HTMLButtonElement = document.createElement('button');

	private name: string;
	private level: number = 0;
	static maxLevel: number = 10;

	constructor(app: MegaFamilyFriendlyNameClient, routeElement: HTMLDivElement, name: string) {
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

		for (let i = 0; i < ShopUpgrade.maxLevel; i++) {
			const newCell = document.createElement('div');
			newCell.classList.add('cell');

			this.levelIndicator.appendChild(newCell);
		}
	}

	buyNewLevel(event: Event) {
		console.log('Buying new level...');
	}

	updateChildren() {
		let i = this.level;

		for (const cell of this.levelIndicator.children) {
			if (i <= 0) {
				break;
			}

			cell.classList.add('active');
		}
	}
}

class MegaFamilyFriendlyNameClient {
	private socket!: WebSocket;

	// UI Cache references
	private root: HTMLElement = document.createElement('div');

	private shopRoot: HTMLDivElement = document.createElement('div');
	private shopBody: HTMLDetailsElement = document.createElement('details');
	private shopUpgrades: Array<ShopUpgrade> = [];

	private dataCenterRoot: HTMLDivElement = document.createElement('div');

	private statsRoot: HTMLDivElement = document.createElement('div');

	constructor() {
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

	private connectToServer(): void {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

		this.socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

		this.socket.onopen = () => {
			console.info('Pipeline connected directly to the unified server wrapper!');
		};

		this.socket.onmessage = (event) => {
			try {
				const response: ServerResponse = jsonDecode(event.data);
				response['status-code'] = 200;
				this.handleServerMessage(response);
			} catch (err) {
				console.error('Failed to parse incoming transmission:', err);
			}
		};

		this.socket.onclose = () => {
			console.error('Pipeline disconnected');
		};
	}

	private sendToServer(request: string, payload: Record<string, any> = {}): void {
		this.socket.send(
			JSON.stringify({
				request,
				...payload,
			}),
		);
	}

	private handleServerMessage(res: ServerResponse): void {
		console.table(res);

		if (res['status-code'] >= 400) {
			alert(res.type || 'An error occurred on the server.');
			return;
		}

		switch (
			res.type
			// todo: put methods here
		) {
		}
	}
}

// Helper function to safely parse server-side layout variables
function jsonDecode(data: string): any {
	return JSON.parse(data);
}

function jsonEncode(data: any): string {
	return JSON.stringify(data);
}

// Fire up client core runtime
document.addEventListener('DOMContentLoaded', () => {
	new MegaFamilyFriendlyNameClient();
});
