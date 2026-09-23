# BACKEND DESIGN RULES - Data Center Tycoon (demo)

1. THE SERVER OWNS THE TRUTH
   The Python server holds the only real game state. The TypeScript client
   draws what the server says and sends _intents_ ("build rack at 3,4"),
   never results ("money is now 900"). The client may animate or predict,
   but the server's snapshot always wins.

2. THE SIMULATION RUNS ON A FIXED TICK
   Game time moves in fixed steps (e.g. 1 tick = 1 in-game second), not per
   HTTP request and not by wall clock inside game logic. The core is one
   function: step(state, commands) -> new state.
   Same state + same commands = same result. That makes bugs reproducible
   and lets us fast-forward, pause, and test.

3. LAYERS ONLY CALL DOWNWARD
   api/ HTTP/WebSocket routes: parse, validate, call a command
   commands/ player actions: build, upgrade, sell, hire, set_price
   sim/ tick logic: power, heat, uptime, revenue, events
   models/ plain data classes for state (no logic, no I/O)
   sim/ and models/ must not import the web framework, files, or network.

4. BALANCE LIVES IN DATA, NOT CODE
   Costs, power draw, heat output, capacity, and upgrade trees for racks,
   servers, cooling, and generators (aka any item) go in config files (e.g.
   server/data/\*.json). Designers tune numbers without touching Python.
   No magic numbers in sim code.

5. MONEY AND UNITS ARE EXPLICIT
   Money is stored as integers (whole cents or whole credits) - never
   floats. Name fields with units: power*kw, heat_btu, temp_c,
   bandwidth_gbps. Every resource flow (power, cooling, cash) must balance
   each tick, so we can show the player \_why* a number changed.

6. COMMANDS VALIDATE, THEN APPLY - OR REJECT CLEANLY
   Each command checks all rules first (enough money? tile free? power
   available?) and either applies fully or changes nothing, returning a
   clear reason code (e.g. "INSUFFICIENT_FUNDS"). No half-applied actions.

7. ONE SERIALISABLE STATE OBJECT
   The whole game is one tree of models that serialises to JSON. That
   single object is used for: API snapshots, save/load, and test fixtures.
   Include a "version" field so old saves can be migrated or rejected.

8. KEEP IT DEMO-SIZED
   In-memory state, one player/session, save to a JSON file. No database,
   auth, or multiplayer until the core loop is fun. Prefer deleting a
   feature over adding infrastructure.

9. TEST THE SIM, NOT THE ENDPOINTS
   Every sim rule (overheating, outages, revenue) gets a small unit test
   built from a JSON fixture. Endpoint tests stay minimal - the API is
   just a thin wrapper.

API SHAPE (suggested)

```
   GET  /state            -> full snapshot
   POST /command          -> {
				"type": "...",
				"http-code": 400,
				"body": "...",
			     }
   POST /tick?n=1         -> advance time (or run ticks on a server loop and
                             push snapshots over a WebSocket)
```

### Stacky mc stackface

- server run logic
- new state is created
- new state is encoded into json
- json is stirngified
- json is wrapped in a WS handler
- WS is sent
- client receives
- unwraps, decodes, json
- handles game logic client side

### Rules for commits

- modular code e.g. all the shop logic goes in the `shop.py` file
- one file per commit
- only one person to edit a file at a time

======

 REALTIME PROTOCOL
   Each  JSON begins with a 'type' field which can be as follows:
       'command':
       'command_result':
       'event':
       'snapshot':
       TBC