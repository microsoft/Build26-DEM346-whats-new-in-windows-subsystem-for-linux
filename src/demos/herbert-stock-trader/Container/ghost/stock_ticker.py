#!/usr/bin/env python3
"""Fake stock trading terminal — displays a live-updating stock ticker
and broadcasts trade events via the ws_server FIFO."""

import random
import time
import sys
import os
import json

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

STOCKS = [
    ("AAPL",  189.50),
    ("GOOGL", 178.30),
    ("MSFT",  420.15),
    ("AMZN",  185.60),
    ("TSLA",  175.20),
    ("NVDA",  890.40),
    ("META",  505.75),
    ("NFLX",  628.90),
    ("AMD",   178.50),
    ("BTC",   68420.00),
    ("ETH",   3850.50),
    ("SPY",   520.30),
]

def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def draw_mini_chart(history, width=20):
    """Draw a tiny ASCII sparkline chart."""
    if len(history) < 2:
        return " " * width
    mn = min(history)
    mx = max(history)
    rng = mx - mn if mx != mn else 1
    blocks = " ▁▂▃▄▅▆▇█"
    chart = ""
    for val in history[-width:]:
        idx = int((val - mn) / rng * (len(blocks) - 1))
        chart += blocks[idx]
    return chart.ljust(width)

def format_price(price):
    if price > 1000:
        return f"{price:>10,.2f}"
    return f"{price:>10.2f}"

# --- FIFO writer for ws_server ---
_fifo = None

def _open_fifo():
    global _fifo
    try:
        _fifo = open('/tmp/ws_server.fifo', 'w')
    except Exception:
        _fifo = None

def broadcast(message_dict):
    """Send a JSON message to the ws_server via FIFO."""
    global _fifo
    if _fifo is None:
        _open_fifo()
    if _fifo is None:
        return
    try:
        _fifo.write(json.dumps(message_dict) + '\n')
        _fifo.flush()
    except Exception:
        _fifo = None

def main():
    # Initialize price histories
    prices = {s[0]: s[1] for s in STOCKS}
    histories = {s[0]: [s[1]] for s in STOCKS}
    volumes = {s[0]: random.randint(100000, 5000000) for s in STOCKS}

    portfolio_value = 1000000.00
    portfolio_history = [portfolio_value]
    trade_log = []

    iteration = 0
    while True:
        clear_screen()
        now = time.strftime("%H:%M:%S")

        # Header
        print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{CYAN}║  📈 GHOST CAPITAL TRADING TERMINAL          {DIM}{now}{RESET}{BOLD}{CYAN}          ║{RESET}")
        print(f"{BOLD}{CYAN}╠══════════════════════════════════════════════════════════════════╣{RESET}")

        # Portfolio summary
        pnl = portfolio_value - 1000000
        pnl_color = GREEN if pnl >= 0 else RED
        pnl_sign = "+" if pnl >= 0 else ""
        print(f"{CYAN}║{RESET}  Portfolio: {WHITE}{BOLD}${portfolio_value:>14,.2f}{RESET}  "
              f"P&L: {pnl_color}{pnl_sign}${pnl:>12,.2f}{RESET}        {CYAN}║{RESET}")
        print(f"{CYAN}╠══════════════════════════════════════════════════════════════════╣{RESET}")

        # Column headers
        print(f"{CYAN}║{RESET} {DIM}{'TICKER':<7} {'PRICE':>10} {'CHG':>8} {'CHG%':>7}  {'CHART':<20} {'VOL':>8}{RESET} {CYAN}║{RESET}")
        print(f"{CYAN}║{RESET} {DIM}{'─'*7} {'─'*10} {'─'*8} {'─'*7}  {'─'*20} {'─'*8}{RESET} {CYAN}║{RESET}")

        # Update prices
        for symbol, _ in STOCKS:
            old_price = prices[symbol]
            # Random walk with slight upward bias
            volatility = 0.003 if symbol not in ("BTC", "ETH") else 0.008
            change_pct = random.gauss(0.0001, volatility)
            new_price = old_price * (1 + change_pct)
            prices[symbol] = new_price
            histories[symbol].append(new_price)
            if len(histories[symbol]) > 30:
                histories[symbol] = histories[symbol][-30:]

            # Update volume
            volumes[symbol] += random.randint(-50000, 80000)
            volumes[symbol] = max(10000, volumes[symbol])

            change = new_price - old_price
            change_pct_val = (change / old_price) * 100
            color = GREEN if change >= 0 else RED
            arrow = "▲" if change >= 0 else "▼"
            sign = "+" if change >= 0 else ""

            chart = draw_mini_chart(histories[symbol])
            chart_color = GREEN if histories[symbol][-1] >= histories[symbol][0] else RED

            vol_str = f"{volumes[symbol]/1000:.0f}K"

            print(f"{CYAN}║{RESET} {WHITE}{BOLD}{symbol:<7}{RESET}"
                  f"{WHITE}{format_price(new_price)}{RESET} "
                  f"{color}{sign}{change:>7.2f}{RESET} "
                  f"{color}{sign}{change_pct_val:>5.2f}%{RESET}  "
                  f"{chart_color}{chart}{RESET} "
                  f"{DIM}{vol_str:>8}{RESET} {CYAN}║{RESET}")

        print(f"{CYAN}╠══════════════════════════════════════════════════════════════════╣{RESET}")

        # Recent trades
        if iteration % 3 == 0:
            action = random.choice(["BUY", "SELL"])
            sym = random.choice([s[0] for s in STOCKS])
            qty = random.randint(10, 500)
            price = prices[sym]
            trade_log.append((now, action, sym, qty, price))
            if len(trade_log) > 4:
                trade_log = trade_log[-4:]

            if action == "BUY":
                portfolio_value -= qty * price * 0.001
            else:
                portfolio_value += qty * price * 0.001

            # Broadcast trade over WebSocket
            broadcast({
                "type": "trade",
                "timestamp": now,
                "action": action,
                "symbol": sym,
                "quantity": qty,
                "price": round(price, 2),
                "total": round(qty * price, 2),
                "portfolio_value": round(portfolio_value, 2),
                "pnl": round(portfolio_value - 1000000, 2)
            })

        print(f"{CYAN}║{RESET} {BOLD}RECENT TRADES:{RESET}")
        for t in trade_log[-4:]:
            t_time, t_action, t_sym, t_qty, t_price = t
            t_color = GREEN if t_action == "BUY" else RED
            total = t_qty * t_price
            print(f"{CYAN}║{RESET}  {DIM}{t_time}{RESET} "
                  f"{t_color}{t_action:<4}{RESET} "
                  f"{WHITE}{t_sym:<6}{RESET} "
                  f"x{t_qty:<4} @ {format_price(t_price)} "
                  f"= ${total:>12,.2f}")

        # Pad remaining lines
        for _ in range(4 - len(trade_log[-4:])):
            print(f"{CYAN}║{RESET}")

        print(f"{CYAN}╚══════════════════════════════════════════════════════════════════╝{RESET}")
        print(f"{DIM}  Ghost Capital LLC • Not Financial Advice • 👻{RESET}")

        portfolio_history.append(portfolio_value)
        iteration += 1
        sys.stdout.flush()
        time.sleep(1.0)

if __name__ == "__main__":
    main()
