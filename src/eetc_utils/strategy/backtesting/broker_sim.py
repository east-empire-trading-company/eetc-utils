import pandas as pd
from dataclasses import dataclass
import uuid


@dataclass
class Trade:
    trade_id: str
    order_id: str
    symbol: str
    side: str
    qty: float
    price: float
    timestamp: pd.Timestamp
    commission: float
    fill_cost: float


class BrokerSim:
    def __init__(
        self,
        slippage=0.0005,
        commission_per_share=0.0,
        initial_cash=10000,
    ):
        self.slippage = slippage
        self.commission_per_share = commission_per_share
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}  # symbol -> qty
        self.trades = []
        self.equity_curve = []

    def place_market_order(self, symbol, side, qty, bar, timestamp):
        ref_price = float(bar["close"])
        sign = 1 if side.upper() == "BUY" else -1
        fill_price = ref_price * (1 + sign * self.slippage)
        commission = abs(qty) * self.commission_per_share
        fill_value = fill_price * qty * sign * -1  # cash delta

        self.cash += fill_value - commission
        self.positions[symbol] = self.positions.get(symbol, 0.0) + sign * qty

        trade = Trade(
            trade_id=str(uuid.uuid4()),
            order_id=str(uuid.uuid4()),
            symbol=symbol,
            side=side.upper(),
            qty=abs(qty),
            price=fill_price,
            timestamp=timestamp,
            commission=commission,
            fill_cost=fill_value,
        )
        self.trades.append(trade)
        return trade

    def mark_to_market(self, bar, timestamp):
        """
        Compute current NAV = cash + sum(position * price)
        """
        nav = self.cash
        for sym, qty in self.positions.items():
            nav += qty * float(bar["close"])
        self.equity_curve.append(
            {
                "timestamp": timestamp,
                "cash": self.cash,
                "nav": nav,
                "positions": self.positions.copy(),
            }
        )
        return nav
