interface ServerResponse {
	request: string;
	'status-code': number;
	message?: string;
}

class MegaFamilyFriendlyNameClient {
	private socket!: WebSocket;

	// UI Cache references
	private root: HTMLElement = document.createElement('div');
	private shopRoot: HTMLDivElement = document.createElement('div');
	private shopBody: HTMLDetailsElement = document.createElement('details');
	private dataCenterRoot: HTMLDivElement = document.createElement('div');
	private statsRoot: HTMLDivElement = document.createElement('div');

	constructor() {
		document.body.innerHTML = '';

		document.body.append(this.root);

		this.root.appendChild(this.shopRoot);
		this.root.appendChild(this.dataCenterRoot);
		this.root.appendChild(this.statsRoot);

		this.shopRoot.appendChild(this.shopBody);

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
			alert(res.message || 'An error occurred on the server.');
			return;
		}

		switch (
			res.request
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
