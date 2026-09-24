// client.ts -> compiles to js/scripts.js (No import/export statements)
(function () {
    // --- Domain Interfaces ---
    // --- 1. Utilities ---
    class NumberFormatter {
        static currency(val) {
            if (val === undefined || val === null)
                return '$0';
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                maximumFractionDigits: 0,
            }).format(val);
        }
        static percent(val) {
            return `${(val || 0).toFixed(1)}%`;
        }
        static decimal(val, digits = 2) {
            return (val || 0).toFixed(digits);
        }
    }
    // --- 2. Observer Pattern State Store ---
    class GameStateStore {
        constructor() {
            this.state = null;
            this.listeners = [];
        }
        subscribe(listener) {
            this.listeners.push(listener);
        }
        update(rawPayload) {
            let extracted = rawPayload;
            // Extract nested envelope down to pure GameState object
            while (extracted && typeof extracted === 'object') {
                if ('state' in extracted && typeof extracted.state === 'object') {
                    extracted = extracted.state;
                }
                else if ('values' in extracted && typeof extracted.values === 'object') {
                    extracted = extracted.values;
                }
                else {
                    break;
                }
            }
            if (extracted && typeof extracted === 'object' && 'day' in extracted) {
                // Preserve locally added cards if incoming state doesn't carry cards
                const existingCards = this.state?.cards;
                this.state = extracted;
                if (!this.state.cards && existingCards) {
                    this.state.cards = existingCards;
                }
                this.notify();
            }
        }
        addCard(card) {
            if (!this.state)
                return;
            if (!this.state.cards) {
                this.state.cards = {};
            }
            if (Array.isArray(this.state.cards)) {
                const exists = this.state.cards.some((c) => c.id === card.id);
                if (!exists) {
                    this.state.cards.push(card);
                }
            }
            else {
                this.state.cards[card.id] = card;
            }
            this.notify();
        }
        removeCard(cardId) {
            if (!this.state || !this.state.cards)
                return;
            if (Array.isArray(this.state.cards)) {
                this.state.cards = this.state.cards.filter((c) => c.id !== cardId);
            }
            else {
                delete this.state.cards[cardId];
            }
            this.notify();
        }
        getState() {
            return this.state;
        }
        notify() {
            if (this.state) {
                this.listeners.forEach((listener) => listener(this.state));
            }
        }
    }
    // --- 3. Network Manager ---
    class NetworkManager {
        constructor(url, onMessage, onStatusChange) {
            this.ws = null;
            this.reconnectInterval = 2000;
            this.url = url;
            this.onMessageCallback = onMessage;
            this.onStatusChangeCallback = onStatusChange;
        }
        connect() {
            console.log(`[WebSocket Dev] Connecting to ${this.url}...`);
            this.onStatusChangeCallback('Connecting...', '#e6a23c');
            this.ws = new WebSocket(this.url);
            this.ws.onopen = () => {
                console.log('[WebSocket Dev] Connected.');
                this.onStatusChangeCallback('Connected', '#4ed3ff');
            };
            this.ws.onmessage = (event) => {
                try {
                    const parsed = JSON.parse(event.data);
                    console.log(`[WebSocket Dev Message]`, parsed);
                    this.onMessageCallback(parsed);
                }
                catch (error) {
                    console.error('[WebSocket Dev Error] Failed to parse payload:', error);
                }
            };
            this.ws.onclose = () => {
                this.onStatusChangeCallback('Disconnected', '#f56c6c');
                setTimeout(() => this.connect(), this.reconnectInterval);
            };
            this.ws.onerror = (error) => {
                console.error('[WebSocket Dev Error]:', error);
                this.ws?.close();
            };
        }
        sendCommand(type, payload = {}) {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                console.error(`[WebSocket Dev Outbound Error] Cannot send command '${type}'. Socket closed.`);
                return;
            }
            console.log(`[WebSocket Dev Command Sent] '${type}':`, payload);
            this.ws.send(JSON.stringify({ type, payload }));
        }
    }
    // --- 4. Component Factory ---
    class ComponentFactory {
        static createLevelIndicator(currentLevel, maxLevel = 10) {
            const container = document.createElement('div');
            container.className = 'level-indicator';
            for (let i = 0; i < maxLevel; i++) {
                const cell = document.createElement('div');
                cell.className = i < currentLevel ? 'cell active' : 'cell';
                container.appendChild(cell);
            }
            return container;
        }
        static createUpgradeCard(title, currentLevel, maxLevel, nextCost, isDisabled, onClick) {
            const card = document.createElement('div');
            card.className = 'shop-upgrade';
            // Header with Title and Level
            const header = document.createElement('div');
            header.style.display = 'flex';
            header.style.justifyContent = 'space-between';
            header.style.alignItems = 'center';
            header.style.fontWeight = 'bold';
            const titleEl = document.createElement('span');
            titleEl.innerText = title;
            const levelText = document.createElement('span');
            levelText.style.color = '#4ed3ff';
            levelText.innerText = `Lvl ${currentLevel}/${maxLevel}`;
            header.appendChild(titleEl);
            header.appendChild(levelText);
            // Meter Bar
            const indicator = this.createLevelIndicator(currentLevel, maxLevel);
            // Button Container
            const btnContainer = document.createElement('div');
            btnContainer.className = 'button-container';
            const button = document.createElement('button');
            button.disabled = isDisabled;
            if (currentLevel >= maxLevel) {
                button.innerText = 'MAX LEVEL';
            }
            else if (nextCost !== undefined) {
                button.innerText = `Upgrade (${NumberFormatter.currency(nextCost)})`;
            }
            else {
                button.innerText = 'Upgrade';
            }
            button.onclick = onClick;
            btnContainer.appendChild(button);
            card.appendChild(header);
            card.appendChild(indicator);
            card.appendChild(btnContainer);
            return card;
        }
        static createGameCard(cardData, isDisabled, onPlay) {
            const card = document.createElement('div');
            card.className = 'shop-upgrade';
            // Rarity Styling
            let rarityColor = '#8de6b8'; // Common
            const rarityLower = (cardData.rarity || '').toLowerCase();
            if (rarityLower.includes('uncommon'))
                rarityColor = '#4ed3ff';
            if (rarityLower.includes('rare'))
                rarityColor = '#ffd078';
            if (rarityLower.includes('legendary'))
                rarityColor = '#f56c6c';
            card.style.borderColor = rarityColor;
            // Header
            const header = document.createElement('div');
            header.style.display = 'flex';
            header.style.justifyContent = 'space-between';
            header.style.alignItems = 'center';
            header.style.fontWeight = 'bold';
            const titleEl = document.createElement('span');
            titleEl.innerText = cardData.name;
            const rarityBadge = document.createElement('span');
            rarityBadge.style.fontSize = '11px';
            rarityBadge.style.color = rarityColor;
            rarityBadge.innerText = rarityLower.toUpperCase();
            header.appendChild(titleEl);
            header.appendChild(rarityBadge);
            // Description
            const desc = document.createElement('div');
            desc.style.fontSize = '12px';
            desc.style.color = '#b5c1d0';
            desc.style.lineHeight = '1.3';
            desc.innerText = cardData.description;
            // Action Button Container
            const btnContainer = document.createElement('div');
            btnContainer.className = 'button-container';
            const button = document.createElement('button');
            button.innerText = 'Play Card';
            button.style.borderColor = rarityColor;
            button.style.backgroundColor = rarityColor;
            button.disabled = isDisabled;
            button.onclick = onPlay;
            btnContainer.appendChild(button);
            card.appendChild(header);
            card.appendChild(desc);
            card.appendChild(btnContainer);
            return card;
        }
    }
    // --- 5. UI Manager ---
    class UIManager {
        constructor(targetElementId) {
            // Action lock per tick
            this.isAwaitingTick = false;
            this.hasPlayedCardThisTick = false;
            this.root = document.getElementById(targetElementId) || document.body;
            this.setupBaseLayout();
        }
        updateConnectionStatus(text, color) {
            this.statusBadge.innerText = text;
            this.statusBadge.style.color = color;
        }
        unlockButtonsForNewTick() {
            this.isAwaitingTick = false;
            this.hasPlayedCardThisTick = false;
        }
        handleLossState(reason) {
            this.lossBannerPanel.style.display = 'block';
            this.lossBannerPanel.innerText = `DEFEAT / GAME OVER: ${reason || 'Grid collapsed due to critical failure.'}`;
            this.statusBadge.innerText = 'DEFEAT';
            this.statusBadge.style.color = '#f56c6c';
        }
        renderDashboard(state, onCommand, onPlayCard) {
            // 1. Defeat check
            if (state.defeat) {
                this.handleLossState(state.reason);
            }
            else {
                this.lossBannerPanel.style.display = 'none';
            }
            // 2. Render Stats Panel
            this.statsPanel.innerHTML = '';
            const title = document.createElement('div');
            title.style.fontSize = '16px';
            title.style.fontWeight = 'bold';
            title.style.marginBottom = '12px';
            title.style.borderBottom = '1px solid #58799d';
            title.style.paddingBottom = '6px';
            title.innerText = `Day ${state.day} (Tick ${state.tick})`;
            const statsGrid = document.createElement('div');
            statsGrid.style.display = 'grid';
            statsGrid.style.gridTemplateColumns = '1fr 1fr';
            statsGrid.style.gap = '8px';
            const statItems = [
                { label: 'Treasury', val: NumberFormatter.currency(state.money) },
                { label: 'Satisfaction', val: NumberFormatter.percent(state['population-satisfaction']) },
                { label: 'Reliability', val: NumberFormatter.percent(state['power-reliability']) },
                { label: 'Power Reserve', val: `${NumberFormatter.decimal(state.energy, 1)} MWh` },
                { label: 'Water Reserve', val: `${NumberFormatter.decimal(state.water, 1)} L` },
                { label: 'Requests', val: NumberFormatter.decimal(state.requests) },
                { label: 'Grid Size', val: `${state.size} / ${state['level-cap']}` },
                { label: 'Emissions', val: NumberFormatter.decimal(state.emissions) },
            ];
            statItems.forEach((item) => {
                const box = document.createElement('div');
                const lbl = document.createElement('div');
                lbl.style.fontSize = '11px';
                lbl.style.color = '#88a4c7';
                lbl.innerText = item.label;
                const v = document.createElement('div');
                v.style.fontWeight = 'bold';
                v.innerText = item.val;
                box.appendChild(lbl);
                box.appendChild(v);
                statsGrid.appendChild(box);
            });
            this.statsPanel.appendChild(title);
            this.statsPanel.appendChild(statsGrid);
            // 3. Render Upgrades Panel
            this.shopBodyPanel.innerHTML = '';
            const cap = state['level-cap'] || 10;
            const createUpgradeHandler = (cmd) => {
                return () => {
                    if (this.isAwaitingTick || state.defeat)
                        return;
                    this.isAwaitingTick = true;
                    this.disableAllActionButtons();
                    onCommand(cmd);
                };
            };
            const energyCost = state['next-energy-upgrade-cost'];
            const canAffordEnergy = energyCost !== undefined ? state.money >= energyCost : true;
            const energyDisabled = this.isAwaitingTick || state.defeat || state['energy-generation-level'] >= cap || !canAffordEnergy;
            const energyCard = ComponentFactory.createUpgradeCard('Energy Generator', state['energy-generation-level'], cap, energyCost, energyDisabled, createUpgradeHandler('buy-electric-upgrade'));
            const waterCost = state['next-water-upgrade-cost'];
            const canAffordWater = waterCost !== undefined ? state.money >= waterCost : true;
            const waterDisabled = this.isAwaitingTick || state.defeat || state['water-collection-level'] >= cap || !canAffordWater;
            const waterCard = ComponentFactory.createUpgradeCard('Water Collector', state['water-collection-level'], cap, waterCost, waterDisabled, createUpgradeHandler('buy-water-upgrade'));
            const sizeCost = state['next-size-upgrade-cost'];
            const canAffordSize = sizeCost !== undefined ? state.money >= sizeCost : true;
            const sizeDisabled = this.isAwaitingTick || state.defeat || state.size >= cap || !canAffordSize;
            const sizeCard = ComponentFactory.createUpgradeCard('District Expansion', state.size, cap, sizeCost, sizeDisabled, createUpgradeHandler('buy-size-upgrade'));
            this.shopBodyPanel.appendChild(energyCard);
            this.shopBodyPanel.appendChild(waterCard);
            this.shopBodyPanel.appendChild(sizeCard);
            // 4. Render Active Cards Hand
            this.cardsBodyPanel.innerHTML = '';
            let cardList = [];
            if (state.cards) {
                if (Array.isArray(state.cards)) {
                    cardList = state.cards;
                }
                else {
                    cardList = Object.values(state.cards);
                }
            }
            if (cardList.length === 0) {
                const emptyText = document.createElement('div');
                emptyText.style.color = '#88a4c7';
                emptyText.style.fontSize = '12px';
                emptyText.style.fontStyle = 'italic';
                emptyText.innerText = 'No cards available in hand.';
                this.cardsBodyPanel.appendChild(emptyText);
            }
            else {
                cardList.forEach((cardItem) => {
                    const isCardDisabled = this.isAwaitingTick || this.hasPlayedCardThisTick || state.defeat;
                    const cardElement = ComponentFactory.createGameCard(cardItem, isCardDisabled, () => {
                        if (this.isAwaitingTick || this.hasPlayedCardThisTick || state.defeat)
                            return;
                        this.hasPlayedCardThisTick = true;
                        this.isAwaitingTick = true;
                        this.disableAllActionButtons();
                        onPlayCard(cardItem.id);
                    });
                    this.cardsBodyPanel.appendChild(cardElement);
                });
            }
        }
        disableAllActionButtons() {
            const buttons = this.root.querySelectorAll('button');
            buttons.forEach((btn) => {
                btn.disabled = true;
            });
        }
        setupBaseLayout() {
            this.root.innerHTML = '';
            // Header (.data-center-root)
            this.headerContainer = document.createElement('div');
            this.headerContainer.className = 'data-center-root';
            this.headerContainer.style.display = 'flex';
            this.headerContainer.style.justifyContent = 'space-between';
            this.headerContainer.style.alignItems = 'center';
            const headerTitle = document.createElement('span');
            headerTitle.style.fontWeight = 'bold';
            headerTitle.innerText = 'City Grid Management';
            this.statusBadge = document.createElement('span');
            this.statusBadge.style.fontSize = '12px';
            this.headerContainer.appendChild(headerTitle);
            this.headerContainer.appendChild(this.statusBadge);
            // Defeat Banner
            this.lossBannerPanel = document.createElement('div');
            this.lossBannerPanel.className = 'data-center-root';
            this.lossBannerPanel.style.backgroundColor = '#3b0d0d';
            this.lossBannerPanel.style.borderColor = '#f56c6c';
            this.lossBannerPanel.style.color = '#ffb3b3';
            this.lossBannerPanel.style.fontWeight = 'bold';
            this.lossBannerPanel.style.display = 'none';
            // Stats Section (.stats)
            this.statsPanel = document.createElement('div');
            this.statsPanel.className = 'stats';
            // Cards Section (.shop container)
            this.cardsPanel = document.createElement('div');
            this.cardsPanel.className = 'shop';
            const cardsTitle = document.createElement('div');
            cardsTitle.style.fontWeight = 'bold';
            cardsTitle.style.marginBottom = '10px';
            cardsTitle.style.fontSize = '15px';
            cardsTitle.innerText = 'Available Cards';
            this.cardsBodyPanel = document.createElement('div');
            this.cardsBodyPanel.className = 'shop-body';
            this.cardsPanel.appendChild(cardsTitle);
            this.cardsPanel.appendChild(this.cardsBodyPanel);
            // Shop Section (.shop)
            const shopPanel = document.createElement('div');
            shopPanel.className = 'shop';
            const shopTitle = document.createElement('div');
            shopTitle.style.fontWeight = 'bold';
            shopTitle.style.marginBottom = '10px';
            shopTitle.style.fontSize = '15px';
            shopTitle.innerText = 'Upgrades & Infrastructure';
            this.shopBodyPanel = document.createElement('div');
            this.shopBodyPanel.className = 'shop-body';
            shopPanel.appendChild(shopTitle);
            shopPanel.appendChild(this.shopBodyPanel);
            // Append all elements
            this.root.appendChild(this.headerContainer);
            this.root.appendChild(this.lossBannerPanel);
            this.root.appendChild(this.statsPanel);
            this.root.appendChild(this.cardsPanel);
            this.root.appendChild(shopPanel);
        }
    }
    // --- 6. Application Orchestrator ---
    class GameClientApp {
        constructor(targetAppId = 'app') {
            this.store = new GameStateStore();
            this.uiManager = new UIManager(targetAppId);
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host || '127.0.0.1:8000';
            const wsUrl = `${protocol}//${host}/ws`;
            this.networkManager = new NetworkManager(wsUrl, (msg) => this.handleServerMessage(msg), (status, color) => this.uiManager.updateConnectionStatus(status, color));
            this.init();
        }
        init() {
            // Subscribe UI render loop to state changes
            this.store.subscribe((state) => {
                this.uiManager.unlockButtonsForNewTick();
                this.uiManager.renderDashboard(state, (cmd, payload) => this.networkManager.sendCommand(cmd, payload), (cardId) => {
                    this.networkManager.sendCommand('play-card', { id: cardId });
                    this.store.removeCard(cardId);
                });
            });
            // Connect WebSocket
            this.networkManager.connect();
        }
        handleServerMessage(msg) {
            if (!msg)
                return;
            // Handle loss / defeat message types
            if (msg.type === 'game-over' || msg.type === 'defeat' || msg.type === 'loose') {
                this.uiManager.handleLossState(msg.status?.message || msg.payload?.reason || msg.data?.description);
                return;
            }
            // Check top level or nested 'values'/'payload' for card_spawned event
            const inner = msg.values || msg.payload || msg;
            if (msg.event === 'card_spawned' || inner.event === 'card_spawned') {
                const cardObj = inner.payload || inner.data || msg.data || inner;
                if (cardObj && cardObj.id) {
                    this.store.addCard(cardObj);
                }
                return;
            }
            // Normal State Update
            if (msg.payload) {
                this.store.update(msg.payload);
            }
            else if (msg.values) {
                this.store.update(msg.values);
            }
            else {
                this.store.update(msg);
            }
        }
    }
    // Bootstrap
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => new GameClientApp('app'));
    }
    else {
        new GameClientApp('app');
    }
})();
