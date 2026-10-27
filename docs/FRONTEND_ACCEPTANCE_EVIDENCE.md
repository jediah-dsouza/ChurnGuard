# Frontend acceptance evidence

Status values: `PASS`, `FAIL`, `BLOCKED`, `NOT APPLICABLE`.

## Scope and gate

First vertical slice: sample selection → input → validation → deterministic service → probability and label → top three drivers → plain-English explanation → retention recommendation → recoverable failure/retry.

**Gate: PASS — first frontend vertical slice proven.**

## 1. Foundation — PASS

- Clean local virtual-environment install completed from `requirements.txt`.
- `python -m compileall -q frontend tests`: PASS.
- Streamlit server started on port 8501 and returned HTTP 200.
- Browser run reported zero console/page errors.
- Secret-pattern scan returned no findings; fixtures contain no real PII.

## 2. Architecture — PASS

- Streamlit is the only frontend.
- Pydantic request/response models and `PredictionService` protocol define the boundary.
- `MockPredictionService` exclusively owns deterministic fixture lookup and failure simulation.
- Presentation components do not know the data source or transport.
- No real ML, SHAP, backend, database, production auth, or monitoring code was added.
- No `any` type or state-management dependency is present.

## 3. Application shell — PASS

- Persistent command rail at 1440px; compact top identity at 1024px and below.
- Page title/context, content regions, focus treatment, and accessible Streamlit alerts verified.

## 4. First vertical slice — PASS

- Sample selector loads form values.
- Valid submit shows a visible loading state and deterministic result.
- Result includes customer, probability, risk band, threshold, three ranked signed drivers, explanations, recommendation, fixture version, and demo labeling.
- Edit/re-run and retry paths work.

## 5. Required fixtures — PASS

| Fixture | Probability | Label | Drivers | Recommendation |
|---|---:|---|---|---|
| `CUST-LOW-001` | 11% | Low | 3 rendered | Rendered |
| `CUST-HIGH-001` | 87% | High | 3 rendered | Rendered |
| `CUST-BORDERLINE-001` | 52% | Medium / Review | 3 rendered | Rendered |
| `CUST-HARD-001` | 61% | High / review-worthy | 3 conflicting signals rendered | Human review wording rendered |

## 6. Validation — PASS

- Visible labels and field-specific inline messages.
- Missing customer ID, missing fields, invalid range, and unseen category reject without prediction.
- Input remains available after errors.
- Native controls support keyboard completion.

## 7. Error and recovery — PASS

- One-shot service failure is intentionally simulated.
- User receives a non-technical error, preserved input, and Retry.
- Retry returns the same deterministic hard-case result.
- Submit is unavailable while Streamlit is processing.

## 8. Visual design / Anti-Slop — PASS

- Retention-control-room identity uses a dark command rail, mineral canvas, fine rules, tabular risk data, and a signal → reasons → action composition.
- Removed template dashboard patterns: no KPI grid, gradient, glass, fake chart, fake metric, sparkle, testimonial, or nested-card maze.
- All displayed product values come from the supplied fixtures.

## 9. Responsive verification — PASS

- Browser-tested at 375, 768, 1024, and 1440px.
- 375px: single column, compact identity, full-width controls, stacked result.
- 768px: stacked sections and controls; no sidebar overlay.
- 1024px: compact identity with balanced two-column analysis.
- 1440px: persistent rail and 45/55 form-result composition.
- Automated width checks found no horizontal page overflow.

## 10. Accessibility — PASS

- Logical H1/H2/H3 structure; visible native labels; keyboard-operable controls.
- Visible `:focus-visible` outline and 44px minimum primary targets.
- Risk uses percentage, text label, symbol, direction words, and color.
- Reduced-motion media query disables transitions/animation.
- Browser semantic audit found zero visible unnamed interactive controls.
- Verified text color pairs meet WCAG AA; lowest checked semantic pair is 4.52:1.

## 11. Testing — PASS

Command: `.venv/bin/pytest -q`

Result: `17 passed`.

Coverage includes validation, missing input, invalid range, unseen category, sample loading, four deterministic fixtures, known input/output regression, response content, edited-input rejection, service failure/retry, app idle/success/error flows, and explicit frontend authentication deferral.

## 12. Runtime verification — PASS

- Actual Streamlit app run and primary journey executed.
- Navigation/identity, form, fixture loading, valid submit, validation, error, retry, and edit/re-run exercised.
- No broken imports or assets; runtime log contained no application exception during final run.

## 13. Visual verification — PASS

Command: `node scripts/visual_qa.mjs`

Result: 12 captured states, zero console/page errors, zero horizontal-overflow findings, zero visible unnamed controls.

Inspected: idle, loading, validation, service error, retry success, low, high, borderline, hard case, and all four target widths.

Defects found and fixed:

1. Mobile sidebar intercepted controls → replaced with compact mobile/tablet identity.
2. 768/1024 layouts were cramped → changed rail and stacking breakpoints.
3. Fixture selector did not refresh widget state → moved loading to a state-safe callback.
4. Retry used an overemphasized red primary button → changed to a restrained secondary action.
5. Numeric steppers exposed unnamed auxiliary buttons → replaced with labeled numeric text entry plus typed validation.
6. Validation feedback appeared below the form → added field-specific inline feedback.
7. Accent/watch colors missed small-text AA → darkened semantic tokens.

## 14. Sample data integrity — PASS

- `CHURNGUARD_SAMPLE_DATA.json` is loaded directly.
- Stable IDs and exact deterministic outputs are regression-tested.
- UI calls the values demo fixtures and explicitly disclaims model/calibration/causal meaning.

## 15. Backend boundary — PASS

- Typed request and response.
- UI consumes the protocol, not fixture internals.
- Future HTTP/FastAPI adapter can replace the mock without presentation changes.

## 16. Documentation — PASS

- Setup, run, test, architecture, sample usage, limitations, and deferred scope are documented.
- `design-system/DESIGN.md` is the visual source of truth.

## 17. Git — PASS

- Repository initialized locally after source inspection.
- Generated environments, caches, secrets, and visual artifacts are ignored.
- Logical checkpoint recorded in the final handoff.

## 18. Deferred / not applicable

- Production authentication: **NOT APPLICABLE** to this frontend-only mock adapter; capability contract explicitly reports that authentication is not required.
- Real FastAPI authentication behavior: **BLOCKED by approved stage boundary**, with the future ownership documented in `docs/ARCHITECTURE.md`.
- Separate production bundle build: **NOT APPLICABLE** to Streamlit; Python compile plus live runtime verification is the build gate.

No blocker remains for this first frontend slice. Later frontend slices and all real ML/backend work remain out of scope.