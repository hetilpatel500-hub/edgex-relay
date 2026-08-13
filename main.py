import os
import time
import threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify
import databento as db

app = Flask(__name__)

DATABENTO_API_KEY = os.environ.get("DATABENTO_API_KEY")
RELAY_API_KEY = os.environ.get("RELAY_API_KEY")
SYMBOL = os.environ.get("SYMBOL", "MESU6")

if not DATABENTO_API_KEY or not RELAY_API_KEY:
    raise RuntimeError("Missing DATABENTO_API_KEY or RELAY_API_KEY env vars")

latest_bars = {}
lock = threading.Lock()
connection_status = {"connected": False, "last_message_at": None, "error": None}


def run_live_client():
    while True:
        try:
            client = db.Live(key=DATABENTO_API_KEY)
            client.subscribe(
                dataset="GLBX.MDP3",
                schema="ohlcv-1m",
                symbols=[SYMBOL],
                stype_in="raw_symbol",
            )
            connection_status["connected"] = True
            connection_status["error"] = None

            for record in client:
                if isinstance(record, db.OHLCVMsg):
                    with lock:
                        latest_bars[SYMBOL] = {
                            "symbol": SYMBOL,
                            "open": record.open / 1e9,
                            "high": record.high / 1e9,
                            "low": record.low / 1e9,
                            "close": record.close / 1e9,
                            "volume": record.volume,
                            "bar_ts": datetime.fromtimestamp(
                                record.ts_event / 1e9, tz=timezone.utc
                            ).isoformat(),
                            "received_at": datetime.now(timezone.utc).isoformat(),
                        }
                        connection_status["last_message_at"] = datetime.now(
                            timezone.utc
                        ).isoformat()

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

    return jsonify({
        **bar,
        "age_seconds": round(age_seconds, 1),
        "connection_status": connection_status,
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "ok" if connection_status["connected"] else "degraded",
        "connection_status": connection_status,
        "cached_symbols": list(latest_bars.keys()),
    })


if __name__ == "__main__":
    thread = threading.Thread(target=run_live_client, daemon=True)
    thread.start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
