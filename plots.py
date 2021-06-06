import pandas

from plotly import graph_objects as go
from plotly.graph_objs._figure import Figure


def draw_price_and_volume_candle_chart(
    df: pandas.DataFrame,
    symbol: str,
    sma_column: str = None,
    export_picture: bool = False,
):
    """
    Draw Price & Volume Candle Chart for OHLC data with an optional SMA line using Plotly.
    """

    t1 = go.Ohlc(
        name="OHLC",
        x=df.index,
        yaxis="y2",
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
    )

    t2 = go.Bar(name="Volume", x=df.index, y=df["Volume"], yaxis="y",)

    if sma_column:
        t3 = go.Scatter(name=sma_column, x=df.index, yaxis="y2", y=df[sma_column],)
        fig = Figure([t1, t2, t3])
    else:
        fig = Figure([t1, t2])

    layout_params = {
        "title_text": f"{symbol} - Price & Volume",
        "height": 800,
        "yaxis": {"domain": [0, 0.2], "showticklabels": True},
        "yaxis2": {"domain": [0.2, 1]},
    }

    if export_picture:
        layout_params["width"] = 1200

    fig.update_layout(layout_params)

    fig.show()
