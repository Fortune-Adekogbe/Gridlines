"""Shared chart presentation for Gridlines."""

import plotly.graph_objects as go
import streamlit as st


CYAN = "#57D8DC"
AMBER = "#F2B866"
BLUE = "#849EF3"
GREEN = "#80CBA8"
PINK = "#DB9AC5"
COLORS = [CYAN, AMBER, BLUE, GREEN, PINK, "#BCC8D5", "#D7907F"]
TECH_COLORS = {"Hydro": CYAN, "Gas": AMBER, "Gas / steam": BLUE, "Steam": PINK, "Unclassified": "#9EACBC"}


def styled(figure, y_title=None, height=360, hovermode="x unified"):
    figure.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", colorway=COLORS,
        font=dict(family="Inter, sans-serif", color="#BCC8D5", size=12),
        height=height, margin=dict(l=12, r=18, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, x=0),
        hoverlabel=dict(bgcolor="#202E3E", font_size=12),
        hovermode=hovermode, dragmode="zoom",
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(title_text=y_title, gridcolor="#263342", zeroline=False)
    return figure


def render(figure, key, selectable=False, alt=None):
    if selectable:
        figure.update_layout(clickmode="event+select")
    return st.plotly_chart(
        figure, width="stretch", theme=None, key=key,
        on_select="rerun" if selectable else "ignore", selection_mode="points",
        config={"displaylogo": False, "scrollZoom": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
        alt=alt,
    )


def line_trace(frame, x, y, label, color, source=None, dashed=False, markers=False, unit="MW"):
    custom = None if source is None else frame[source].fillna("Unavailable").astype(str).to_numpy().reshape(-1, 1)
    x_label = "%{x:02d}:00 WAT" if x == "hour" else "%{x|%d %b %Y}"
    hover = x_label + "<br>%{y:,.2f} " + unit
    if custom is not None:
        hover += "<br>Source: %{customdata[0]}"
    return go.Scatter(
        x=frame[x], y=frame[y], name=label, connectgaps=False,
        mode="lines+markers" if markers else "lines",
        line=dict(color=color, width=2, dash="dash" if dashed else "solid"),
        marker=dict(size=5), customdata=custom, hovertemplate=hover + "<extra>%{fullData.name}</extra>",
    )
