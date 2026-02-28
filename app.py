from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

DATA_DIR = Path(__file__).parent / "data"
PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")


def load_pink_morsel_sales() -> pd.DataFrame:
    csv_paths = sorted(DATA_DIR.glob("daily_sales_data_*.csv"))

    data_frames = [pd.read_csv(path) for path in csv_paths]
    sales_data = pd.concat(data_frames, ignore_index=True)

    pink_morsel_sales = sales_data[sales_data["product"].str.lower() == "pink morsel"].copy()
    pink_morsel_sales["date"] = pd.to_datetime(pink_morsel_sales["date"])
    pink_morsel_sales["price"] = (
        pink_morsel_sales["price"].replace("[$,]", "", regex=True).astype(float)
    )
    pink_morsel_sales["sales"] = pink_morsel_sales["price"] * pink_morsel_sales["quantity"]

    return pink_morsel_sales


def build_daily_sales(pink_morsel_sales: pd.DataFrame, region: str) -> pd.DataFrame:
    filtered_sales = pink_morsel_sales
    if region != "all":
        filtered_sales = pink_morsel_sales[pink_morsel_sales["region"].str.lower() == region]

    daily_sales = filtered_sales.groupby("date", as_index=False)["sales"].sum().sort_values("date")
    return daily_sales


def create_figure(daily_sales: pd.DataFrame, region: str):
    region_label = "All Regions" if region == "all" else region.capitalize()
    figure = px.line(
        daily_sales,
        x="date",
        y="sales",
        title=f"Pink Morsel Daily Sales Over Time ({region_label})",
        labels={"date": "Date", "sales": "Total Sales (USD)"},
    )

    figure.update_traces(line={"width": 3}, mode="lines")
    figure.update_layout(
        margin={"l": 40, "r": 20, "t": 70, "b": 40},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.92)",
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


pink_morsel_sales_data = load_pink_morsel_sales()
initial_figure = create_figure(build_daily_sales(pink_morsel_sales_data, "all"), "all")

app = Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

app.layout = html.Div(
    children=[
        html.Div(
            className="card",
            children=[
                html.H1("Soul Foods Pink Morsel Sales Visualiser", className="title"),
                html.P(
                    "Filter by region to compare sales before and after the 15 Jan 2021 price increase.",
                    className="subtitle",
                ),
                dcc.RadioItems(
                    id="region-filter",
                    options=[
                        {"label": "north", "value": "north"},
                        {"label": "east", "value": "east"},
                        {"label": "south", "value": "south"},
                        {"label": "west", "value": "west"},
                        {"label": "all", "value": "all"},
                    ],
                    value="all",
                    inline=True,
                    className="region-filter",
                    labelClassName="radio-label",
                    inputClassName="radio-input",
                ),
                dcc.Graph(id="sales-chart", figure=initial_figure, className="chart"),
            ],
        ),
    ],
    className="page",
)


@app.callback(Output("sales-chart", "figure"), Input("region-filter", "value"))
def update_chart(region: str):
    daily_sales = build_daily_sales(pink_morsel_sales_data, region)
    return create_figure(daily_sales, region)


if __name__ == "__main__":
    app.run(debug=True)
