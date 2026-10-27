# ChurnGuard Frontend Acceptance Checklist

**Purpose:** Mandatory completion gate for the frontend-only development stage.

> **DO NOT MOVE FORWARD BECAUSE THE CODE EXISTS. MOVE FORWARD BECAUSE THE CURRENT SLICE IS PROVEN.**

## 1. Foundation

- [ ] Clean install succeeds.
- [ ] Development server starts.
- [ ] Production build succeeds.
- [ ] No blocking TypeScript/compiler errors.
- [ ] No broken imports/assets.
- [ ] No blocking runtime errors.
- [ ] No secrets/API keys.
- [ ] No real customer PII.

## 2. Architecture

- [ ] Approved frontend architecture is followed.
- [ ] Real ML/backend work is not prematurely implemented.
- [ ] Prediction access uses a typed service boundary.
- [ ] Mock logic is not scattered through components.
- [ ] Mock service can later be replaced by an HTTP/FastAPI implementation.
- [ ] No `any` shortcut for missing types.
- [ ] State ownership is clear.
- [ ] No unnecessary state-management dependency.

## 3. Application Shell

- [ ] Navigation works.
- [ ] Responsive navigation works.
- [ ] Page context/title is clear.
- [ ] Main content spacing is consistent.
- [ ] Focus states are visible.
- [ ] Status/toast messaging is accessible where used.

## 4. First Vertical Slice — Mandatory

- [ ] Sample customer can be selected/loaded.
- [ ] Form populates correctly.
- [ ] Valid customer can be submitted.
- [ ] Loading state appears.
- [ ] Mock prediction executes.
- [ ] Risk probability is displayed.
- [ ] Risk label is displayed.
- [ ] Top three drivers are displayed.
- [ ] Driver direction/impact is understandable.
- [ ] Plain-English explanations are displayed.
- [ ] Retention recommendation is displayed.
- [ ] Result experience is polished.
- [ ] User can return/edit/re-run.
- [ ] Fixture behavior is deterministic.

## 5. Required Fixtures

### `CUST-LOW-001`
- [ ] Loads correctly.
- [ ] Low-risk result is correct.
- [ ] Drivers render.
- [ ] Recommendation renders.

### `CUST-HIGH-001`
- [ ] Loads correctly.
- [ ] High-risk result is correct.
- [ ] Drivers render.
- [ ] Recommendation renders.

### `CUST-BORDERLINE-001`
- [ ] Loads correctly.
- [ ] Medium/borderline result is understandable.
- [ ] UI does not imply false certainty.
- [ ] Drivers render.
- [ ] Recommendation renders.

### `CUST-HARD-001`
- [ ] Loads correctly.
- [ ] Conflicting signals are understandable.
- [ ] Explanation hierarchy remains clear.
- [ ] Recommendation communicates review/uncertainty appropriately.

## 6. Validation

- [ ] Required fields have labels.
- [ ] Missing fields are rejected.
- [ ] Invalid numeric values are rejected.
- [ ] Messages explain what to fix.
- [ ] Validation is not color-only.
- [ ] User input is preserved where possible.
- [ ] Invalid submission does not predict.
- [ ] Keyboard completion works.

## 7. Error and Recovery

- [ ] Mock service failure can be simulated.
- [ ] Service error is clear.
- [ ] Error does not expose unnecessary technical details.
- [ ] Retry is available.
- [ ] Retry recovers successfully.
- [ ] Empty states are meaningful.
- [ ] Disabled states are understandable.
- [ ] Loading prevents confusing duplicate actions where appropriate.

## 8. Visual Design / Anti-Slop

- [ ] ChurnGuard has a deliberate visual identity.
- [ ] UI does not look like an untouched generic dashboard template.
- [ ] Typography hierarchy is intentional.
- [ ] Spacing is consistent.
- [ ] Risk information is visually prioritized.
- [ ] Important actions are clear.
- [ ] No meaningless charts/widgets.
- [ ] No placeholder/lorem ipsum copy.
- [ ] No fake testimonials or business claims.
- [ ] No fabricated ML metrics.
- [ ] No excessive gradients/glassmorphism.
- [ ] No excessive nested cards.
- [ ] Icons have purpose.
- [ ] Motion is purposeful and restrained.

## 9. Responsive Verification

### Desktop
- [ ] Layout balanced.
- [ ] Navigation works.
- [ ] Form/result areas align.
- [ ] No unexpected overflow.

### Tablet
- [ ] Navigation adapts.
- [ ] Content remains readable.
- [ ] Controls remain usable.
- [ ] No clipping.

### Mobile
- [ ] Navigation works.
- [ ] Form is usable.
- [ ] Results stack correctly.
- [ ] Risk score remains understandable.
- [ ] Drivers remain readable.
- [ ] Buttons remain usable.
- [ ] No horizontal scrolling required.

## 10. Accessibility

- [ ] Semantic HTML.
- [ ] Logical heading hierarchy.
- [ ] Associated form labels.
- [ ] Meaningful accessible button names.
- [ ] Keyboard navigation.
- [ ] Visible focus.
- [ ] Logical tab order.
- [ ] Accessible error/status messages.
- [ ] No color-only information.
- [ ] Adequate contrast.
- [ ] Reduced-motion preference respected.

## 11. Testing

### Unit/component/logic
- [ ] Form validation test.
- [ ] Sample selection test.
- [ ] Mock prediction service test.
- [ ] Risk label rendering test.
- [ ] Driver rendering test.
- [ ] Error handling test.

### Integration/user flow
- [ ] Sample selection.
- [ ] Valid submission.
- [ ] Loading.
- [ ] Successful prediction.
- [ ] Result presentation.
- [ ] Invalid input.
- [ ] Service failure.
- [ ] Retry.

Record exact commands and results.

## 12. Runtime Verification

- [ ] Application was actually run.
- [ ] First vertical slice was executed in the running app.
- [ ] Console/runtime errors were checked where tooling permits.
- [ ] Navigation manually exercised.
- [ ] Form manually exercised.

## 13. Visual Verification

Inspect the running application:

- [ ] Overview/dashboard.
- [ ] Customer input.
- [ ] Loading state.
- [ ] Success result.
- [ ] Validation error.
- [ ] Service error.
- [ ] Retry state.
- [ ] Low-risk result.
- [ ] High-risk result.
- [ ] Borderline result.
- [ ] Hard-case result.
- [ ] Desktop.
- [ ] Tablet.
- [ ] Mobile.

If browser/screenshot tooling is unavailable:
- [ ] Limitation is explicitly documented.
- [ ] No false claim of screenshot-level verification.

## 14. Sample Data Integrity

- [ ] JSON fixture loads.
- [ ] IDs are stable.
- [ ] Outputs are deterministic.
- [ ] Tests do not depend on random output.
- [ ] Fixtures are clearly demo data.
- [ ] Fixtures are not described as model metrics.
- [ ] No real customer data.

## 15. Backend Boundary

- [ ] Prediction request shape is typed.
- [ ] Prediction response shape is typed.
- [ ] UI consumes the contract, not mock implementation details.
- [ ] HTTP concerns are not scattered through presentation components.
- [ ] Mock → FastAPI replacement is architecturally straightforward.

## 16. Documentation

- [ ] Setup instructions documented where appropriate.
- [ ] Run command documented.
- [ ] Test command documented.
- [ ] Sample-data usage documented.
- [ ] Known limitations documented.
- [ ] Frontend scope distinguished from later ML/backend work.

## 17. Git

- [ ] Changes are organized into logical commits.
- [ ] No secrets committed.
- [ ] No unnecessary build junk committed.
- [ ] Working tree is understood.
- [ ] Checkpoint/commit recorded.

## 18. Final Evidence Report

The agent must report:

```text
Install:
Run:
Build:
Test:

Fixture:
Input:
Prediction:
Result:
```

Repeat for all four fixtures.

Also record:
- viewports inspected
- routes/states inspected
- defects found
- defects fixed
- remaining limitations

## 19. Final Gate

### PASS

```text
PASS — frontend stage proven.
```

Only when all mandatory criteria are satisfied.

### BLOCKED

```text
BLOCKED — frontend stage not yet proven.
```

Then list the failed criterion, evidence, required fix and retest.

## 20. Non-Negotiable Rule

> A successful build is not proof of a successful frontend.

The stage passes only when the application has been:

**designed → implemented → run → tested → visually verified → debugged → checked for responsive/accessibility quality → proven with deterministic sample data.**

Only then may the project advance.
