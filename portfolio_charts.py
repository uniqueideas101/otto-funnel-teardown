
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


OUTPUT_DIR = Path("outputs/charts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (10, 6),
    "figure.dpi": 120,
    "savefig.dpi": 180,
    "font.size": 11,
    "axes.titlesize": 15,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def save_chart(filename):
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, bbox_inches="tight")
    plt.close()


#observed ecommerce funnel

stages = [
    "All sessions",
    "Sessions with cart",
    "Sessions with order",
]

sessions = [
    12_899_779,
    3_810_706,
    1_626_338,
]

percentages = [
    100.0,
    29.54,
    12.61,
]

plt.figure()

bars = plt.barh(stages[::-1], sessions[::-1])

plt.title("Observed ecommerce funnel")
plt.xlabel("Number of sessions")
plt.gca().xaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{x / 1e6:.1f}M")
)

for bar, count, pct in zip(
    bars,
    sessions[::-1],
    percentages[::-1]
):
    plt.text(
        bar.get_width(),
        bar.get_y() + bar.get_height() / 2,
        f"  {count / 1e6:.2f}M ({pct:.2f}%)",
        va="center"
    )

save_chart("01_observed_funnel.png")

RED = "#C51F18"
DARK_RED = "#981A15"
BLACK = "#111111"
WHITE = "#FFFFFF"
GREY = "#666666"
#session journey distribution

journeys = [
    "Click only",
    "Click → cart, no order",
    "Click → cart → order",
    "Click → order, no cart",
    "Other",
]

journey_pct = [
    (70.18, RED),
    (17.08, DARK_RED),
    (11.94, BLACK),
    (0.22, GREY),
    (0.58, WHITE),
]

plt.figure()

bars = plt.barh(journeys[::-1], [pct for pct, _ in journey_pct])

plt.title("Distribution of recorded session journeys")
plt.xlabel("Share of all sessions")
plt.xlim(0, 80)

for bar, (value, color) in zip(bars, journey_pct[::-1]):
    plt.text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.2f}%",
        va="center"
    )

save_chart("02_session_journeys.png")


#article attention vs complete journeys

articles = [
    "108125",
    "1460571",
    "29735",
    "1733943",
    "231487",
]

click_sessions = [
    68256,
    59685,
    53461,
    48539,
    43810,
]

complete_journeys = [
    479,
    1373,
    1649,
    2621,
    3400,
]

x = np.arange(len(articles))
width = 0.36

fig, ax = plt.subplots(figsize=(10, 6))

ax.bar(
    x - width / 2,
    np.array(click_sessions) / 1000,
    width,
    label="Click sessions (thousands)"
)

ax.bar(
    x + width / 2,
    complete_journeys,
    width,
    label="Complete journeys"
)

ax.set_title("Article attention does not equal purchase progression")
ax.set_xlabel("Article ID")
ax.set_ylabel("Count (different scales)")
ax.set_xticks(x)
ax.set_xticklabels(articles)
ax.legend()


save_chart("03_article_attention_and_journeys.png")


progression_articles = [
    "231487",
    "166037",
    "1733943",
    "450505",
    "1025795",
    "258353",
]

progression_rates = [
    7.76,
    8.21,
    5.40,
    10.70,
    14.34,
    15.13,
]

plt.figure()

bars = plt.barh(
    progression_articles[::-1],
    progression_rates[::-1]
)

plt.title("Full same-article journey progression")
plt.xlabel("Complete journeys / click sessions (%)")
plt.xlim(0, 18)

for bar, value in zip(bars, progression_rates[::-1]):
    plt.text(
        bar.get_width() + 0.2,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.2f}%",
        va="center"
    )

save_chart("03b_article_progression_rates.png")


#article switching in complete funnel sessions

categories = [
    "Same article across all milestones",
    "Switched at least once",
]

switch_pct = [
    18.66,
    81.34,
]

plt.figure()

bars = plt.barh(categories[::-1], switch_pct[::-1])

plt.title("Article switching in complete funnel sessions")
plt.xlabel("Share of complete funnel sessions")
plt.xlim(0, 100)

for bar, value in zip(bars, switch_pct[::-1]):
    plt.text(
        bar.get_width() + 1,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.2f}%",
        va="center"
    )

save_chart("04_article_switching.png")


# Transition-specific article matching
transitions = [
    "Click → cart",
    "Cart → order",
]

same_article = [
    27.66,
    53.45,
]

different_article = [
    72.34,
    46.55,
]

x = np.arange(len(transitions))

plt.figure()

plt.bar(
    x,
    same_article,
    label="Same article"
)

plt.bar(
    x,
    different_article,
    bottom=same_article,
    label="Different article"
)

plt.xticks(x, transitions)
plt.ylabel("Share of transition sessions (%)")
plt.title("Article identity across funnel transitions")
plt.ylim(0, 110)
plt.legend()

save_chart("04b_transition_article_matching.png")


#hourly activity volumes

hours = list(range(24))

active_sessions = [
    12293, 8444, 8680, 13863, 27216, 48397,
    65205, 79573, 86210, 89440, 96222, 100159,
    101462, 103870, 107311, 108389, 109065,
    116647, 124502, 128372, 111873, 68419,
    40907, 21728
]

click_events = [
    56316, 37274, 35559, 49762, 93174, 165333,
    228077, 284625, 313593, 330393, 356857,
    379770, 390611, 401315, 417294, 422855,
    423894, 461186, 501073, 534151, 481783,
    306178, 183370, 99879
]

cart_events = [
    4209, 2800, 2630, 3804, 8009, 14904,
    20938, 28023, 29806, 31235, 32928, 34715,
    34924, 35357, 36342, 36645, 36650, 39374,
    42897, 44026, 38117, 24068, 13598, 7437
]

order_events = [
    881, 581, 557, 938, 2179, 4269,
    6269, 8171, 9518, 10163, 10397, 10737,
    10850, 10838, 11224, 11493, 11311,
    11968, 13317, 13394, 11262, 6847,
    3283, 1659
]


hourly_series = [
    ("Active sessions", active_sessions, "05_hourly_active_sessions.png"),
    ("Click events", click_events, "05b_hourly_clicks.png"),
    ("Cart events", cart_events, "05c_hourly_carts.png"),
    ("Order events", order_events, "05d_hourly_orders.png"),
]

for label, values, filename in hourly_series:
    plt.figure()
    plt.plot(hours, values, marker="o")
    plt.title(f"Average hourly {label.lower()} (UTC)")
    plt.xlabel("Hour of day (UTC)")
    plt.ylabel(f"Average {label.lower()}")
    plt.xticks(range(0, 24, 2))
    plt.grid(axis="y", alpha=0.25)
    save_chart(filename)


#hourly session participation percentages

cart_session_pct = [
    15.47, 14.94, 14.00, 13.45, 14.04, 14.57,
    15.11, 16.07, 16.34, 16.50, 16.25, 16.29,
    16.18, 16.05, 16.02, 16.01, 15.99, 15.87,
    15.93, 15.60, 15.45, 16.00, 15.20, 15.62
]

order_session_pct = [
    3.56, 3.37, 3.17, 3.24, 3.66, 4.04,
    4.51, 4.93, 5.35, 5.49, 5.27, 5.16,
    5.13, 5.08, 5.12, 5.17, 5.06, 4.93,
    4.91, 4.59, 4.34, 4.41, 3.65, 3.69
]

plt.figure()

plt.plot(
    hours,
    cart_session_pct,
    marker="o",
    label="Cart-session percentage"
)

plt.plot(
    hours,
    order_session_pct,
    marker="o",
    label="Order-session percentage"
)

plt.title("Hourly cart and order session percentages")
plt.xlabel("Hour of day (UTC)")
plt.ylabel("Average percentage (%)")
plt.xticks(range(0, 24, 2))
plt.legend()
plt.grid(axis="y", alpha=0.25)

save_chart("06_hourly_session_percentages.png")


#cart-reaching vs no-cart sessions

groups = [
    "Cart-reaching",
    "No-cart",
]

average_clicks = [8.02, 8.13]
average_articles = [5.86, 5.95]
average_repeat_clicks = [2.16, 2.18]

metrics = [
    ("Average click events", average_clicks,
     "07a_average_clicks.png"),
    ("Average distinct articles", average_articles,
     "07b_average_articles.png"),
    ("Average repeat clicks", average_repeat_clicks,
     "07c_average_repeat_clicks.png"),
]

for title, values, filename in metrics:
    plt.figure()
    bars = plt.bar(groups, values)
    plt.title(title)
    plt.ylabel("Average per session")

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom"
        )

    save_chart(filename)


# Repeat-click prevalence
repeat_click_prevalence = [48.23, 56.65]

plt.figure()

bars = plt.bar(groups, repeat_click_prevalence)

plt.title("Sessions with at least one repeat click")
plt.ylabel("Share of sessions (%)")
plt.ylim(0, 70)

for bar, value in zip(bars, repeat_click_prevalence):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.2f}%",
        ha="center",
        va="bottom"
    )

save_chart("07d_repeat_click_prevalence.png")


#repeat cart distribution before first cart

repeat_groups = [
    "No repeats",
    "1 repeat",
    "2–4 repeats",
    "5–9 repeats",
    "10+ repeats",
]

repeat_pct = [
    51.77,
    18.49,
    17.39,
    7.26,
    5.09,
]

plt.figure()

bars = plt.bar(repeat_groups, repeat_pct)

plt.title("Repeat-click distribution before first cart")
plt.ylabel("Share of eligible cart-reaching sessions (%)")
plt.xticks(rotation=20, ha="right")

for bar, value in zip(bars, repeat_pct):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.2f}%",
        ha="center",
        va="bottom"
    )

save_chart("08_repeat_click_distribution.png")


#session duration distribution

percentiles = [
    "P25",
    "P50",
    "P75",
    "P90",
    "P95",
    "P99",
]

# Approximate elapsed session spans in days.
# P25: 8.7 minutes converted to days.
duration_days = [
    8.7 / (60 * 24),
    2.15,
    12.9,
    21.2,
    24.2,
    26.9,
]

plt.figure()

plt.plot(
    percentiles,
    duration_days,
    marker="o"
)

plt.yscale("log")
plt.title("Observed session span distribution")
plt.xlabel("Percentile")
plt.ylabel("Elapsed time (days, logarithmic scale)")
plt.grid(axis="y", alpha=0.25)

save_chart("09_session_duration_percentiles.png")

#session_depth before order
depth_percentiles = ["Median", "P75", "P90", "P95"]

click_depth = [11, 25, 51, 77]
cart_depth = [2, 4, 8, 12]
total_event_depth = [13, 30, 59, 86]

series = [
    ("Clicks", click_depth),
    ("Carts", cart_depth),
    ("Total events", total_event_depth),
]

for label, values in series:
    plt.figure()

    plt.plot(
        depth_percentiles,
        values,
        marker="o"
    )

    plt.title(f"{label} before first order")
    plt.xlabel("Percentile")
    plt.ylabel("Event count")
    plt.grid(axis="y", alpha=0.25)

    save_chart(f"10_{label.lower().replace(' ', '_')}_before_order.png")


print(f"Charts saved to: {OUTPUT_DIR.resolve()}")
print("Portfolio chart generation complete.")
