# ChurnGuard Design System

## Product personality

ChurnGuard is a **retention control room** for retention and customer-success operators. It is analytical, calm, precise, trustworthy, human, and information-rich. It is not a generic admin dashboard and it never implies that a demo prediction is a validated model conclusion.

## Information hierarchy

1. Customer identity and operating context
2. Churn probability and explicit risk label
3. The three signed drivers
4. Recommended retention action
5. Supporting account and service facts

The result should read as a decision brief: **signal → reasons → action**.

## Visual identity

- Light mineral canvas with dark navy ink.
- A narrow navy command rail gives the product an operational frame.
- Warm amber is the product accent; it marks current context and human review.
- Semantic colors are reserved for risk meaning.
- Fine rules and compact labels create an instrument-panel rhythm without decorative chrome.
- No gradients, glassmorphism, glows, illustrations, fake metrics, or repetitive KPI cards.

## Typography

Use the system sans stack: `Inter` where available, then `Segoe UI`, `Arial`, sans-serif. No external font request is required.

| Token | Size / line height | Weight | Use |
|---|---:|---:|---|
| Display | 32 / 38 px | 700 | Page title |
| H2 | 22 / 29 px | 700 | Primary regions |
| H3 | 17 / 24 px | 650 | Component headings |
| Body | 15 / 23 px | 400 | Interface copy |
| Small | 13 / 19 px | 500 | Supporting copy |
| Label | 12 / 16 px | 700 | Uppercase operational labels |
| Data XL | 52 / 52 px | 750 | Risk probability |

Numbers use `font-variant-numeric: tabular-nums`.

## Color system

| Role | Token | Value |
|---|---|---|
| Canvas | `--cg-canvas` | `#F4F5F2` |
| Surface | `--cg-surface` | `#FFFFFF` |
| Surface muted | `--cg-surface-muted` | `#EAEEE9` |
| Ink | `--cg-ink` | `#122028` |
| Ink muted | `--cg-ink-muted` | `#56636A` |
| Border | `--cg-border` | `#CFD7D3` |
| Rail | `--cg-rail` | `#10232B` |
| Accent | `--cg-accent` | `#A55F16` |
| Focus | `--cg-focus` | `#126E82` |
| Low | `--cg-low` | `#247A55` |
| Low soft | `--cg-low-soft` | `#E3F1E9` |
| Watch | `--cg-watch` | `#855708` |
| Watch soft | `--cg-watch-soft` | `#F7ECD4` |
| High | `--cg-high` | `#B13A32` |
| High soft | `--cg-high-soft` | `#F8E5E2` |
| Error | `--cg-error` | `#A52F2F` |

All normal text/background pairs must meet WCAG AA. Risk is always paired with a text label, symbol, and sentence—not color alone.

## Spacing and sizing

- Base spacing scale: `4, 8, 12, 16, 24, 32, 48, 64`.
- Main content maximum: `1280px`.
- Desktop gutters: `32–48px`; tablet: `24px`; mobile: `16px`.
- Interactive targets: at least `44px`.
- Dense fact rows use `8–12px`; decision regions use `24–32px`.

## Borders, radii, and elevation

- Use `1px` borders before shadows.
- Controls: `6px` radius.
- Panels: `8px` radius.
- Status lozenges may use a pill shape because the shape encodes status.
- Default surfaces have no shadow. Floating alerts may use `0 4px 16px rgba(16,35,43,.10)`.

## Component principles

- **Application shell:** persistent rail on desktop; compact top identity on mobile.
- **Command Center:** use a status line, segmented metric ledger, priority queue, direct-count distribution, review register, activity ledger, and honest model state. Avoid interchangeable metric cards.
- **Forms:** grouped by Profile, Account, and Services. Every field has a visible label.
- **Risk brief:** one dominant probability, explicit band, threshold context, and uncertainty wording.
- **Drivers:** ranked rows with direction arrow, signed impact, and explanation.
- **Recommendation:** visually follows drivers and uses an action list, not promotional copy.
- **States:** replace the result region coherently; do not stack contradictory states.

## Iconography

Use familiar text symbols sparingly: `↑` raises risk, `↓` lowers risk, `!` error, `✓` confirmation. Never use decorative icons or sparkles. Every icon repeats meaning already available in text.

## Risk visualization

- Probability is shown as a percentage and a labeled horizontal meter.
- Threshold is marked on the meter and stated in text.
- Low: stable signal; Medium: review/watch; High: prioritize.
- Borderline results explicitly state proximity to the decision threshold.
- Hard cases explicitly describe conflicting signals and recommend human review.
- Never use “will churn”; use “predicted churn risk” or “demo risk signal.”

## Explanation and driver styling

- Rank drivers 01–03.
- Show direction in words and with `↑/↓`.
- Signed impact is a fixture contribution, never called SHAP or causal evidence in this frontend-only stage.
- Explanations use the exact deterministic fixture copy.

## Charts

Do not add a chart unless it enables comparison, trend, distribution, or prioritization. The first slice needs only a probability meter. Future charts must use direct labels, accessible summaries, tabular alternatives, and semantic colors consistently.

## Motion

- 120–180 ms for hover/focus feedback.
- 220 ms for result reveal via opacity and small vertical transform.
- Loading may use Streamlit’s progress feedback; no indefinite decorative animation.
- No bounce, pulse, flashing, or delayed access to results.
- Under `prefers-reduced-motion: reduce`, animations and smooth scrolling are disabled.

## Responsive behavior

- **≥1200px:** persistent rail; form and result split approximately 45/55.
- **768–1199px:** compact navigation; two columns where space permits.
- **<768px:** single-column reading order: context, sample, form, action, result.
- **375px:** 16px gutters, full-width controls, no horizontal page scroll.
- Long labels wrap; tables are avoided in this slice.

## Accessibility

- Logical page heading order.
- Native Streamlit labels remain visible.
- Keyboard-operable native controls.
- `:focus-visible` uses a 3px teal outline with 2px offset.
- Error and status copy includes text, not color alone.
- Minimum normal text contrast is 4.5:1; meaningful boundaries target 3:1.
- Validation points to the field and explains the correction.

## State rules

- **Idle:** concise instruction and no fabricated result.
- **Loading:** “Scoring demo fixture…” plus a progress indicator.
- **Success:** customer, probability, band, drivers, explanation, action.
- **Validation:** inline field-specific messages; input remains intact.
- **Service error:** recoverable explanation and Retry; no stack trace.
- **Empty:** explains how to select or enter a customer.
- **Disabled:** submit is disabled only while processing.

## Data density

Use compact fact summaries and dense driver rows, with additional breathing room around the risk and action decision. Do not solve density by adding more cards.

### Command Center density

- The queue is the primary operational surface and appears before supporting analysis.
- Desktop rows use a ruled eight-column ledger; mobile rows become labeled two-column records.
- KPI values are one connected strip rather than four floating cards.
- Small sample distributions use direct counts and horizontal bars, never pie charts.
- “Recent” activity explicitly identifies the fixed fixture snapshot and never implies live production history.
- Model health shows available metadata and an intentional pending state instead of invented evaluation metrics.

### Customer History density

- The history ledger is the primary visual object; search and filters form a compact operational preface, not a dashboard.
- Desktop uses a ruled semantic table with nine fixture-backed fields and a named inspection action.
- At 1024px and below, records intentionally become vertical summaries instead of forcing horizontal table overflow.
- Mobile summaries preserve customer identity, risk label, probability, top driver, and inspection action; supporting fixture metadata is disclosed on demand.
- Risk, contract, tenure, fixture date, and sort controls may be combined. Tenure buckets are fixed as 0–12, 13–36, and 37+ months.
- Empty history, search-empty, filter-empty, and recoverable service-error states remain distinct and never introduce fake activity.

### Customer Detail hierarchy

- Customer Detail follows **customer → risk → why → action → context → metadata**.
- The risk brief, ranked driver ledger, and recommendation are the primary decision surfaces; demographic and service facts remain supporting evidence.
- Customer context uses ruled definition lists grouped as Customer, Account, and Services rather than a generic profile card or editable form.
- Detail navigation provides explicit routes back to Customer History and into the existing Prediction Workspace.
- At mobile widths, identity and risk remain first, followed by explanation, drivers, recommendation, customer context, and prediction metadata.

### Batch Prediction workflow

- Batch follows **dataset → validation → run → summary → priority queue → inspect**.
- Validation is a first-class operational surface with total, valid, and invalid counts plus row-level recovery messages.
- Batch metrics form one connected ledger; small risk distributions use direct labeled counts and restrained bars.
- Desktop results use a ruled semantic table. At 1024px and below, records become vertical summaries preserving identity, textual risk, probability, top driver, and inspection.
- Upload controls remain compact and native; never substitute a giant illustrated drop zone.
