from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

DATA_DIR = Path(__file__).parent / "data"
PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")


def load_daily_pink_morsel_sales() -> pd.DataFrame:
    csv_paths = sorted(DATA_DIR.glob("daily_sales_data_*.csv"))

    data_frames = [pd.read_csv(path) for path in csv_paths]
    sales_data = pd.concat(data_frames, ignore_index=True)

    pink_morsel_sales = sales_data[sales_data["product"].str.lower() == "pink morsel"].copy()
    pink_morsel_sales["date"] = pd.to_datetime(pink_morsel_sales["date"])
    pink_morsel_sales["price"] = (
        pink_morsel_sales["price"].replace("[$,]", "", regex=True).astype(float)
    )
    pink_morsel_sales["sales"] = pink_morsel_sales["price"] * pink_morsel_sales["quantity"]

    daily_sales = (
        pink_morsel_sales.groupby("date", as_index=False)["sales"].sum().sort_values("date")
    )

    return daily_sales


def create_figure(daily_sales: pd.DataFrame):
    figure = px.line(
        daily_sales,
        x="date",
        y="sales",
        title="Pink Morsel Daily Sales Over Time",
        labels={"date": "Date", "sales": "Total Sales (USD)"},
    )
    max_sales = daily_sales["sales"].max()
    figure.add_shape(
        type="line",
        x0=PRICE_INCREASE_DATE,
        x1=PRICE_INCREASE_DATE,
        y0=0,
        y1=max_sales,
        line={"color": "red", "dash": "dash"},
        xref="x",
        yref="y",
    )
    figure.add_annotation(
        x=PRICE_INCREASE_DATE,
        y=max_sales,
        text="Price increase: 2021-01-15",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
    )
    return figure


daily_sales_data = load_daily_pink_morsel_sales()
figure = create_figure(daily_sales_data)

app = Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

app.layout = html.Div(
    [
        html.H1("Soul Foods Pink Morsel Sales Visualiser"),
        dcc.Graph(figure=figure),
    ]
)


if __name__ == "__main__":
    app.run(debug=True)
