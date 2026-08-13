import os
import time
import threading
from collections import deque
from datetime import datetime, timezone
from flask import Flask, request, jsonify
import databento as db

app = Flask(__name__)

DATABENTO_API_KEY = os.environ.get("DATABENTO_API_KEY")
RELAY_API_KEY = os.environ.get("RELAY_API_KEY")
SYMBOL = os.environ.get("SYMBOL", "MESU6")
BUFFER_SIZE = 500

latest_bars = {}
bar_buffer = {SYMBOL: deque(maxlen=BUFFER_SIZE)}
lock = threading.Lock()
connection_status = {"connected": False, "last_message_at": None, "error": None}

if not DATABENTO_API_KEY or not RELAY_API_KEY:
    raise RuntimeError("Missing DATABENTO_API_KEY or RELAY_API_KEY env vars")


def run_live_client():
    while True:
        try:
            print("[relay] connecting to Databento...")
            client = db.Live(key=DATABENTO_API_KEY)
            client.subscribe(
                dataset="GLBX.MDP3",
                schema="ohlcv-1m",
                symbols=[SYMBOL],
                stype_in="raw_symbol",
            )
            connection_status["connected"] = True
            connection_status["error"] = None
            print("[relay] connected, waiting for bars...")

            for record in client:
                if isinstance(record, db.OHLCVMsg):
                    with lock:
                        bar = {
                            "ts": datetime.fromtimestamp(
                                record.ts_event / 1e9, tz=timezone.utc
                            ).isoformat(),
                            "open": record.open / 1e9,
                            "high": record.high / 1e9,
                            "low": record.low / 1e9,
                            "close": record.close / 1e9,
                            "volume": record.volume,
                        }
                        latest_bars[SYMBOL] = {
                            "symbol": SYMBOL,
                            **bar,
                            "bar_ts": bar["ts"],
                            "received_at": datetime.now(timezone.utc).isoformat(),
                        }
                        if SYMBOL not in bar_buffer:
                            bar_buffer[SYMBOL] = deque(maxlen=BUFFER_SIZE)
                        # avoid duplicate bar for same timestamp
                        if not bar_buffer[SYMBOL] or bar_buffer[SYMBOL][-1]["ts"] != bar["ts"]:
                            bar_buffer[SYMBOL].append(bar)
                        connection_status["last_message_at"] = datetime.now(
                            timezone.utc
                        ).isoformat()
                        print(f"[relay] got bar: {bar['ts']} close={bar['close']}")

        except Exception as e:
            connection_status["connected"] = False
            connection_status["error"] = str(e)
            print(f"[relay] connection error: {e}, retrying in 10s")
            time.sleep(10)


def check_auth():
    key = request.headers.get("X-API-Key") or request.args.get("api_key")
    return key == RELAY_API_KEY


@app.route("/latest-bar")
def latest_bar():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    symbol = request.args.get("symbol", SYMBOL)
    with lock:
        bar = latest_bars.get(symbol)
    if not bar:
        return jsonify({"error": "no data yet", "connected": connection_status["connected"]}), 503
    bar_time = datetime.fromisoformat(bar["bar_ts"])
    age_seconds = (datetime.now(timezone.utc) - bar_time).total_seconds()
    return jsonify({**bar, "age_seconds": round(age_seconds, 1), "connection_status": connection_status})


@app.route("/candles")
def candles():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    symbol = request.args.get("symbol", SYMBOL)
    limit = int(request.args.get("limit", 500))
    with lock:
        buf = list(bar_buffer.get(symbol, []))
    # newest first
    bars = list(reversed(buf))[:limit]
    return jsonify({"symbol": symbol, "count": len(bars), "bars": bars})


@app.route("/health")
def health():
    with lock:
        buffered = len(bar_buffer.get(SYMBOL, []))
    return jsonify({
        "status": "ok" if connection_status["connected"] else "degraded",
        "connection_status": connection_status,
        "cached_symbols": list(latest_bars.keys()),
        "buffered_bars": buffered,
    })


_thread = threading.Thread(target=run_live_client, daemon=True)
_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
