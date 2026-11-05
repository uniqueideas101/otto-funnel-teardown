
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

from explore_duckdb import BLACK, RED



OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Consistent portfolio palette
NAVY = "#172B4D"
BLUE = "#287DB5"
TEAL = "#20A39E"
LIGHT = "#EAF0F5"
GREY = "#65758B"
DARK = "#253247"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
    "axes.titlesize": 17,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})




def create_funnel_cone():

    stages = [
        {
            "name": "CLICK",
            "count": 12_899_779,
            "share": 100.00,
            "width": 1.000,
        },
        {
            "name": "CLICK → CART",
            "count": 3_772_601,
            "share": 29.25,
            "width": 0.2925,
        },
        {
            "name": "CLICK → CART → ORDER",
            "count": 1_539_798,
            "share": 11.94,
            "width": 0.1194,
        },
    ]

    fig, ax = plt.subplots(figsize=(12, 8))

    # Funnel segment boundaries
    y_levels = [3, 2, 1, 0]
    colors = [BLUE, TEAL, NAVY]

    for i, stage in enumerate(stages):

        top_width = stage["width"]
        bottom_width = stage["width"] 

        y_top = y_levels[i]
        y_bottom = y_levels[i + 1]

        polygon = Polygon(
            [
                (-top_width / 2, y_top),
                (top_width / 2, y_top),
                (bottom_width / 2, y_bottom),
                (-bottom_width / 2, y_bottom),
            ],
            closed=True,
            facecolor=colors[i],
            edgecolor="white",
            linewidth=2,
        )

        ax.add_patch(polygon)

        center_y = (y_top + y_bottom) / 2

        # Labels inside the cone
        ax.text(
            0,
            center_y + 0.10,
            stage["name"],
            ha="center",
            va="center",
            color="white",
            fontsize=11,
            fontweight="bold",
        )

        ax.text(
            0,
            center_y - 0.12,
            f'{stage["count"] / 1_000_000:.2f}M',
            ha="center",
            va="center",
            color="white",
            fontsize=15,
            fontweight="bold",
        )

        # Percentage labels to the right
        ax.text(
            0.62,
            center_y,
            f'{stage["share"]:.2f}% of all sessions',
            ha="left",
            va="center",
            color=DARK,
            fontsize=11,
        )

    ax.text(
        0,
        -0.42,
        "40.81% of click → cart sessions subsequently recorded an order",
        ha="center",
        va="center",
        color=TEAL,
        fontsize=11,
        fontweight="bold",
    )

    ax.set_title(
        "Observed chronological ecommerce funnel",
        color=NAVY,
        pad=22,
    )

    ax.text(
        0,
        3.28,
        "12.90M recorded sessions",
        ha="center",
        color=GREY,
        fontsize=10,
    )

    ax.set_xlim(-0.75, 1.65)
    ax.set_ylim(-0.65, 3.55)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "01_chronological_funnel_cone.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()



def create_article_performance():

    # Complete same-article journey metrics.
    # Progression rate = complete same-article journeys / click sessions.

    articles = [
        # aid, click sessions, complete journeys
        (231487, 43810, 3400),
        (166037, 38463, 3157),
        (1733943, 48539, 2621),
        (450505, 16817, 1800),
        (1025795, 11266, 1615),
        (258353, 10321, 1562),

        # High-attention examples with zero complete journeys
        (95488, 50260, 0),
        (1502122, 50114, 0),
        (322370, 45664, 0),
    ]

    aids = [str(x[0]) for x in articles]
    clicks = np.array([x[1] for x in articles])
    journeys = np.array([x[2] for x in articles])

    rates = np.divide(
        journeys,
        clicks,
        out=np.zeros(len(articles), dtype=float),
        where=clicks != 0,
    ) * 100

    fig, ax = plt.subplots(figsize=(12, 7))

    # Marker size reflects completed same-article journey volume
    sizes = 90 + np.sqrt(journeys) * 5

    colors = [
        TEAL if journey > 0 else "#C66B64"
        for journey in journeys
    ]

    ax.scatter(
        clicks,
        rates,
        s=sizes,
        c=colors,
        alpha=0.85,
        edgecolors="white",
        linewidth=1.5,
    )

    # Label article IDs
    offsets = {
        "231487": (8, 8),
        "166037": (8, 8),
        "1733943": (8, -16),
        "450505": (8, 8),
        "1025795": (8, 8),
        "258353": (8, 8),
        "95488": (8, 8),
        "1502122": (8, -16),
        "322370": (8, 8),
    }

    for i, aid in enumerate(aids):
        ax.annotate(
            aid,
            (clicks[i], rates[i]),
            xytext=offsets[aid],
            textcoords="offset points",
            fontsize=9,
            color=DARK,
        )

    ax.set_title(
        "High article attention does not guarantee progression",
        color=NAVY,
        pad=18,
    )

    ax.set_xlabel("Sessions with at least one click on the article")
    ax.set_ylabel("Same-article click → cart → order progression (%)")

    ax.grid(axis="both", alpha=0.20)
    ax.spines[["top", "right"]].set_visible(False)

    ax.text(
        0.02,
        0.97,
        "Bubble size represents completed same-article journeys",
        transform=ax.transAxes,
        va="top",
        color=GREY,
        fontsize=9,
    )

    ax.text(
        0.02,
        0.90,
        "Red markers = zero recorded complete same-article journeys",
        transform=ax.transAxes,
        va="top",
        color="#A84F49",
        fontsize=9,
    )

    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "03_article_attention_vs_progression.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()




def create_interaction_comparison():

    metrics = [
        "Average clicks",
        "Average distinct articles",
        "Average repeat clicks",
    ]

    cart_reaching = [8.02, 5.86, 2.16]
    no_cart = [8.13, 5.95, 2.18]

    fig, ax = plt.subplots(figsize=(10, 5.5))

    y = np.arange(len(metrics))
    gap = 0.13

    ax.barh(
        y + gap,
        cart_reaching,
        height=0.22,
        color=RED,
        label="Cart-reaching",
    )

    ax.barh(
        y - gap,
        no_cart,
        height=0.22,
        color=BLACK,
        label="No-cart",
    )

    for i, value in enumerate(cart_reaching):
        ax.text(
            value + 0.08,
            y[i] + gap,
            f"{value:.2f}",
            va="center",
            fontsize=11,
            color=DARK,
        )

    for i, value in enumerate(no_cart):
        ax.text(
            value + 0.08,
            y[i] - gap,
            f"{value:.2f}",
            va="center",
            fontsize=11,
            color=DARK,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(metrics)
    ax.invert_yaxis()

    ax.set_xlim(0, 9.3)
    ax.set_xlabel("Average events / distinct articles per session")

   
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.20)
    ax.spines[["top", "right", "left"]].set_visible(False)

    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "07_interaction_comparison.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()



def create_repeat_click_comparison():

    groups = ["Cart-reaching", "No-cart"]
    values = [48.23, 56.65]

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(
        groups,
        values,
        color=[BLUE, TEAL],
        width=0.48,
    )

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1.1,
            f"{value:.2f}%",
            ha="center",
            fontsize=13,
            fontweight="bold",
            color=NAVY,
        )

    ax.set_ylim(0, 68)
    ax.set_ylabel("Sessions with at least one repeat click (%)")

    ax.set_title(
        "Repeat clicks are more prevalent in no-cart sessions",
        color=NAVY,
        pad=18,
    )

    ax.grid(axis="y", alpha=0.20)
    ax.spines[["top", "right"]].set_visible(False)

    ax.text(
        0.5,
        -0.20,
        "Descriptive comparison; observation windows differ between groups.",
        transform=ax.transAxes,
        ha="center",
        color=GREY,
        fontsize=9,
    )

    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "07d_repeat_click_prevalence_redesigned.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()



if __name__ == "__main__":

    create_funnel_cone()
    create_article_performance()
    create_interaction_comparison()
    create_repeat_click_comparison()

    print("Redesigned charts saved to:", OUTPUT_DIR.resolve())
