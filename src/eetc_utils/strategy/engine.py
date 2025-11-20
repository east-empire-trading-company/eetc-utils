import os, json
import pandas as pd
from src.eetc_utils.clients.eetc_data import EETCDataClient
from src.eetc_utils.strategy.backtesting.broker_sim import BrokerSim
from src.eetc_utils.strategy.backtesting.metrics import compute_perf_stats


class Engine:
    def __init__(self, eetc_api_key=None, output_dir="results", broker_sim=None):
        self._eetc_api_key = os.getenv("EETC_API_KEY", eetc_api_key)
        self.client = EETCDataClient(api_key=self._eetc_api_key)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.broker = broker_sim or BrokerSim()

    def run(self, strategy, symbol, start, end):
        output = {
            "trades": [],
            "equity": pd.DataFrame(),
            "perf": pd.DataFrame(),
        }  # output

        # fetch input data
        price_df = self.client.get_price_data(
            symbol=symbol, from_date=start, to_date=end
        )
        context = {
            "engine": self,
            "symbol": symbol,
            "place_order": lambda side, qty, **kwargs: output["trades"].append(
                self.broker.place_market_order(
                    symbol, side, qty, kwargs.get("data"), kwargs.get("timestamp")
                ),
            ),
        }

        strategy.on_start(context)

        for row in price_df.itertuples(index=False):
            bar = row._asdict()
            strategy.on_data(bar, bar["date"], context)
            self.broker.mark_to_market(bar, bar["date"])

        strategy.on_stop(context)

        # Save results
        trades_path = os.path.join(
            self.output_dir, f"{strategy.name}__{symbol}__trades.json"
        )
        with open(trades_path, "w") as f:
            json.dump([t.__dict__ for t in output["trades"]], f, indent=2)

        equity_df = pd.DataFrame(self.broker.equity_curve)
        equity_csv = os.path.join(
            self.output_dir, f"{strategy.name}__{symbol}__equity.csv"
        )
        equity_df.to_csv(equity_csv, index=False)
        output["equity"] = equity_df

        perf = compute_perf_stats(equity_df["nav"])
        perf_path = os.path.join(
            self.output_dir, f"{strategy.name}__{symbol}__perf.json"
        )
        with open(perf_path, "w") as f:
            json.dump(perf, f, indent=2)
        output["perf"] = perf

        return output
