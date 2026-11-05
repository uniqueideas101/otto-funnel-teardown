# OTTO — Ecommerce Funnel Teardown

A behavioral analytics and UX teardown of the OTTO ecommerce experience, combining large-scale event data analysis, a review of the current website experience, and data-informed product recommendations.

## Project Overview

This project investigates how shoppers interact with the OTTO ecommerce platform, how recorded shopping journeys progress from product clicks to carts and orders, and where the shopping experience could be improved.

The project has two complementary parts:

1. **Behavioral analysis:** SQL-based analysis of the OTTO Recommender Systems Dataset to examine session journeys, funnel progression, article interactions, and shopping patterns.
2. **UX audit:** An exploratory review of the current OTTO website across desktop and mobile, identifying usability strengths, friction points, and opportunities for improvement.

The goal is to translate behavioral patterns and UX observations into practical product opportunities and testable experiments.

---

## Dataset

**Source:** [OTTO Recommender Systems Dataset](https://github.com/otto-de/recsys-dataset)

The analysis uses the training dataset, containing approximately:

| Dataset measure | Volume |
|---|---:|
| Sessions | 12.9 million |
| Recorded events | 216.7 million |
| Click events | 194.7 million |
| Cart events | 16.9 million |
| Order events | 5.1 million |
| Unique articles | 1.8 million |

**Observation period:** July 31 – August 28, 2022.

Each record contains a session identifier and a sequence of events. Events include an article ID (`aid`), timestamp (`ts`), and event type (`click`, `cart`, or `order`).

### Important dataset considerations

- A session represents a recorded activity sequence, not a unique customer.
- Article IDs are anonymized; product names, categories, prices, and customer attributes are not available.
- Timestamps are Unix epoch milliseconds and are converted to UTC for temporal analysis.
- Event order is preserved using the original event sequence.
- The training dataset is used for descriptive behavioral analysis. The truncated test data is not used to establish the baseline.
- The dataset does not reveal why a shopper behaved in a particular way.

---

## Behavioral Analysis

The behavioral analysis examines five areas:

- Funnel progression from clicks to carts and orders.
- Session journey patterns and interaction depth.
- Article-level attention and same-article progression.
- Article switching across recorded shopping journeys.
- Temporal patterns and differences between cart-reaching and no-cart sessions.

### Key Findings

#### 1. Most sessions did not record a cart event

- 29.25% of sessions recorded a chronological click-to-cart journey.
- 11.94% recorded a complete click-to-cart-to-order journey.
- 40.81% of click-to-cart sessions subsequently recorded an order.

#### 2. Recorded shopping journeys were not strictly linear

Among sessions with a chronological click-to-cart-to-order journey, 81.34% involved at least one change in article ID across the first recorded click, cart, and order milestones.

This suggests that many recorded journeys involved multiple articles rather than a single article throughout.

#### 3. High article attention did not guarantee progression

Some articles received substantial click attention but recorded no complete same-article click-to-cart-to-order journeys.

Article popularity and progression therefore need to be examined separately.

#### 4. Interaction volume alone did not distinguish cart-reaching sessions

Average click volume was similar between cart-reaching and no-cart sessions.

Repeat-click prevalence was actually higher among no-cart sessions:

- Cart-reaching sessions: 48.23%
- No-cart sessions: 56.65%

These are descriptive differences, not evidence that repeat clicks cause or prevent cart activity.

#### 5. Shopping activity varied over time

Recorded activity varied by hour and day.

19:00 UTC had the highest hourly volume across sessions, clicks, carts, and orders. Temporal patterns provide useful context for understanding activity distribution, but do not establish why those patterns occurred.

### Interpretation

The recorded journeys were often multi-article and did not follow a simple linear path. Neither article attention nor interaction volume alone explains whether a session progressed to a cart or order.

---

## UX Audit

An exploratory review of the current OTTO website was conducted across desktop and mobile experiences.

The review focused on homepage hierarchy, navigation, search, product information, filters, wishlist functionality, and the cart experience.

### Observed Strengths

- Mobile experience felt polished and easy to navigate.
- Navigation supports both product exploration and locating known products.
- Contextual category navigation helps narrow broad categories without leaving the page.
- Promotions are visible without feeling excessively intrusive.
- Product filters are useful and straightforward.
- Wishlist functionality provides a convenient way to collect products.
- Newsletter incentives provide an additional purchase incentive.

### Areas for Improvement

- **Desktop homepage:** Multiple categories and product themes compete for attention, making the homepage feel visually crowded.
- **Product information:** Product specifications are comprehensive but presented in dense, lengthy lists that are harder to scan.
- **Search:** Ambiguous queries can return loosely related products instead of clarifying the shopper's intent.
- **Stock transparency:** Limited quantity options are displayed without clearly explaining availability.
- **Cart recommendations:** Similar-product recommendations after adding an item could be evaluated for relevance and their impact on checkout progression.

The UX audit is exploratory and reflects observations from the reviewed website experience. It is not a multi-participant usability study.

---

## Product Opportunities & Experiments

The analysis and UX review suggest several opportunities for further investigation.

| Opportunity | Proposed experiment | Example success metric |
|---|---|---|
| Improve desktop homepage hierarchy | Test clearer grouping and prioritization of homepage content | Homepage-to-category click-through rate |
| Improve search intent handling | Test query suggestions and clarification for ambiguous searches | Search-to-product click-through rate |
| Improve product information scanning | Test grouped specifications and progressive disclosure | Product-page-to-cart rate |
| Improve stock transparency | Test clearer explanations of quantity limits and availability | Quantity-selector errors |
| Improve contextual navigation | Test extending contextual navigation to more categories | Category-to-product progression |
| Improve cart recommendations | Test recommendation relevance after add-to-cart | Recommendation click-through and add-to-cart rate |

These are proposed experiments, not completed or validated tests.

Success metrics should be evaluated alongside guardrails such as checkout progression, cart abandonment, and customer support contacts where relevant.

---

## Technical Workflow

The project uses SQL and Python to transform and analyze the event-level dataset.

### Tools

- **DuckDB** — querying and aggregating large event datasets.
- **SQL** — session-level, article-level, funnel, and temporal analysis.
- **Python** — data preparation, analysis, and visualization.
- **Pandas** — data manipulation.
- **Matplotlib** — chart creation.
- **PowerPoint** — presentation of findings and recommendations.

### Analytical workflow

1. Load the raw JSONL training data.
2. Parse nested session event records.
3. Build an event-level analytical table.
4. Preserve event sequence using event numbers.
5. Convert Unix timestamps into UTC timestamps.
6. Aggregate session-level and article-level metrics.
7. Analyze chronological funnel progression.
8. Examine temporal patterns and interaction behavior.
9. Create visualizations and interpret findings.
10. Translate findings into UX opportunities and proposed experiments.

---

## Repository Structure

```text
otto_funnel_teardown/
│
├── data/
│   └── raw/                  # Raw dataset (not committed)
│
├── sql/                      # SQL analysis queries
│
├── src/                      # Python scripts
│
├── outputs/                  # Charts and analytical outputs
│
├── README.md
