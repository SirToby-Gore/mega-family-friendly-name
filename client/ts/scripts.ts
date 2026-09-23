interface ServerResponse {
	request: string;
	'status-code': number;
	message?: string;
}

class MegaFamilyFriendlyNameClient {
	private socket!: WebSocket;

	// UI Cache references

	constructor() {}

	private connectToServer(): void {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

		this.socket = new WebSocket(`${protocol}//${window.location.host}`);

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

	/// todo: change me
	private joinGame(): void {
		const input = document.getElementById('username-input') as HTMLInputElement;
		const name = input.value.trim();
		this.sendToServer('join-game', { name });
	}

	private handleServerMessage(res: ServerResponse): void {
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

// Global window event safely preventing disconnect alerts
window.addEventListener('beforeunload', (event) => {
	event.preventDefault();
	event.returnValue = 'Are you sure you want to leave the game session?';
	return event.returnValue;
});

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
