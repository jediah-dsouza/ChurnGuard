# ChurnGuard Frontend Build Specification

**File:** `CHURNGUARD_FRONTEND_BUILD_SPEC.md`  
**Stage:** Frontend-only development  
**Authority:** Stage-specific scope under `MASTER-WEB-DEV-WORKFLOW.md` and `ChurnGuard_Master_JSON_Prompt.json`

## 1. Purpose

This document is the **authoritative scope for the frontend-only development stage** of ChurnGuard.

The goal is to produce a polished, responsive, accessible, testable frontend that is fully functional with deterministic sample data and architecturally ready to connect to the future FastAPI backend.

> **DO NOT MOVE FORWARD BECAUSE THE CODE EXISTS. MOVE FORWARD BECAUSE THE CURRENT SLICE IS PROVEN.**

## 2. Authority and Priority

When instructions conflict:

1. `MASTER-WEB-DEV-WORKFLOW.md`
2. `ChurnGuard_Master_JSON_Prompt.json`
3. This frontend build specification
4. Current frontend phase/slice requirements
5. `CHURNGUARD_FRONTEND_ACCEPTANCE_CHECKLIST.md`
6. `CHURNGUARD_SAMPLE_DATA.json`

This file narrows the master specification to the current frontend-only stage.

## 3. Frontend-Only Boundary

### Build now

- Frontend application shell and responsive navigation
- Overview/dashboard experience
- Customer analysis workflow
- Customer input form and client-side validation
- Sample customer selection
- Loading, success, empty, validation-error and service-error states
- Prediction result presentation
- Risk probability and risk classification
- Top-driver explanations
- Plain-English insights
- Retention recommendations
- Reusable components
- Typed frontend models/contracts
- Replaceable prediction-service boundary
- Deterministic mock prediction service
- Frontend tests
- Responsive/accessibility behavior
- Visual verification

### Do not build yet

Do **not** implement the real:

- ML training pipeline
- Logistic Regression / Random Forest / XGBoost training
- SHAP computation
- model calibration
- MLflow pipeline
- FastAPI backend
- database
- production authentication backend
- API-key infrastructure
- Docker deployment
- Hugging Face/Render deployment
- production monitoring infrastructure
- real external AI provider

These belong to later stages.

### Architecture rule

Use:

```text
UI
 ↓
Typed Application / Service Layer
 ↓
Prediction Service Contract
 ↓
Mock Prediction Service
```

Later:

```text
UI
 ↓
Typed Application / Service Layer
 ↓
FastAPI
 ↓
ML Pipeline
 ↓
Serialized Model + Explainability
```

The UI must not contain pretend ML calculations or scattered mock responses.

## 4. Product Identity

**ChurnGuard — A Customer Churn Prediction & Retention Support System**

The product should feel like a focused **retention control room**, not a generic SaaS admin dashboard.

Primary operator goals:

1. Identify a customer.
2. Assess churn risk.
3. Understand why the customer is at risk.
4. Decide what deserves attention.
5. Take an informed retention action.

Prioritize risk clarity, explanation, actionability, information hierarchy, operational speed and trust.

## 5. Design Direction

The interface must actively avoid generic AI-generated UI.

Avoid:

- purple/pink gradient templates
- excessive glassmorphism
- decorative blobs
- meaningless charts
- excessive rounded cards
- nested card-in-card layouts
- random icons
- giant headings with weak hierarchy
- excessive shadows
- placeholder copy
- lorem ipsum
- fake testimonials
- fabricated metrics
- excessive animation

Aim for a visual identity that is:

- analytical
- operational
- modern
- precise
- restrained
- trustworthy
- distinctive

Use external design references as **principles and review criteria**, not templates to copy.

## 6. Information Architecture

Support the approved ChurnGuard route/view inventory. At minimum establish a coherent experience for:

- Overview / Dashboard
- Analyze Customer
- Analysis / Prediction Result
- Customer detail/history context where applicable
- Settings/product information where required by the approved specification

Do not invent unrelated functionality merely to fill pages.

## 7. Global Shell

Use reusable shell elements as appropriate:

- primary navigation
- responsive navigation
- page header/context
- main content region
- notification/status region
- accessible focus handling
- consistent spacing and typography

No mobile trapping or unintended horizontal overflow.

## 8. Core Component Architecture

Create reusable components with clear responsibilities.

Expected categories:

### Navigation
- AppShell
- Sidebar/Navigation
- MobileNavigation
- Breadcrumbs where justified
- PageHeader

### Risk
- RiskScore
- RiskBadge
- RiskMeter
- RiskSummary

### Customer
- CustomerSummary
- CustomerInputForm
- CustomerField
- CustomerAttributeGroup
- SampleCustomerSelector

### Explanation
- TopDrivers
- DriverItem
- ExplanationCard
- PlainEnglishInsight
- RecommendationPanel

### States
- LoadingState
- EmptyState
- ErrorState
- ValidationState
- SuccessState
- RetryAction

### Shared UI
- Buttons
- Inputs
- Selects
- Dialog/modal where justified
- Toast/status UI where useful
- Skeleton/loading treatment where useful

Do not abstract purely for abstraction's sake.

## 9. First Vertical Slice

This is the primary proof:

```text
Sample Customer
      ↓
Customer Input Form
      ↓
Client Validation
      ↓
Prediction Service
      ↓
Deterministic Mock Prediction
      ↓
Risk Probability
      ↓
Risk Label
      ↓
Top 3 Drivers
      ↓
Plain-English Explanations
      ↓
Retention Recommendation
      ↓
Polished Result Experience
```

Prove this slice before expanding secondary experiences.

## 10. Sample Data

Use `CHURNGUARD_SAMPLE_DATA.json`.

Fixtures must be:

- deterministic
- local
- version-controlled
- realistic enough for UI testing
- clearly demo/sample data
- free of secrets
- free of real customer PII

Required scenarios:

1. Low risk
2. High risk
3. Borderline
4. Hard/ambiguous

Provide a practical development-time way to select/load them.

## 11. Mock Prediction Contract

Use a typed request/response boundary. Equivalent structures are acceptable, but the response must expose at least:

```ts
type PredictionResponse = {
  predictionId: string;
  customerId: string;
  riskProbability: number;
  riskLabel: "Low" | "Medium" | "High";
  threshold: number;
  topDrivers: Array<{
    feature: string;
    direction: "increases_risk" | "decreases_risk";
    impact: number;
    explanation: string;
  }>;
  recommendation: {
    priority: "low" | "medium" | "high";
    summary: string;
    actions: string[];
  };
  generatedAt: string;
  modelVersion: string;
  isDemoData: boolean;
};
```

Do not use `any` as a shortcut.

Mock behavior belongs in the service layer, not visual components.

## 12. Required UX States

For meaningful interactive/async operations support:

- idle
- focused
- validation error
- loading
- success
- service error
- retry
- empty
- disabled
- responsive/mobile

Prediction flow must clearly distinguish validation failures from service failures.

The hard-case fixture should exercise uncertainty/ambiguous interpretation rather than looking identical to an obvious high-risk case.

## 13. Forms and Validation

- Use visible labels.
- Validate required fields.
- Validate numeric ranges.
- Provide actionable messages.
- Preserve input after recoverable errors.
- Support keyboard use.
- Do not silently accept obviously invalid input.

## 14. Responsive Requirements

Verify at minimum:

- desktop
- tablet
- mobile

Check navigation, forms, risk score, driver presentation, recommendation panel, controls, typography, spacing and overflow.

Normal use must not require horizontal scrolling.

## 15. Accessibility

At minimum:

- semantic HTML
- accessible labels
- keyboard navigation
- visible focus
- meaningful button names
- logical heading hierarchy
- adequate contrast
- accessible status/error messaging
- no information communicated by color alone
- reduced-motion support
- logical tab order

## 16. Motion

Animation should communicate state, hierarchy, loading, navigation or feedback.

Avoid bounce-heavy interfaces, excessive decorative motion, long blocking animations and motion that harms scanability.

Respect `prefers-reduced-motion`.

## 17. State Management

Use the smallest state solution that satisfies the requirements.

Keep UI state, form state, prediction state and service state appropriately separated.

Avoid duplicated sources of truth.

## 18. Testing

At minimum test:

- form validation
- sample selection
- mock prediction service
- risk label rendering
- driver rendering
- error handling
- valid submission flow
- loading state
- successful result
- service failure
- retry recovery

Tests must be deterministic and not depend on arbitrary timing.

## 19. Visual Verification

A passing build is not sufficient.

Visually inspect the running app for:

- alignment
- spacing
- typography
- hierarchy
- risk presentation
- loading/error/success states
- navigation
- forms
- responsive behavior
- accessibility cues
- accidental overflow
- placeholder/demo artifacts

If browser/screenshot tooling is unavailable, state the limitation rather than falsely claiming screenshot-level verification.

## 20. Runtime Verification

Before passing:

- dependencies install
- development server starts
- production build succeeds
- tests pass
- no blocking runtime errors
- sample flow works
- navigation works
- responsive behavior is checked
- no broken imports/assets
- no TypeScript errors where applicable

## 21. Production-Oriented Quality

Even at this stage:

- no secrets/API keys
- no real customer data
- no production credentials
- no unsafe HTML injection
- no unnecessary dependencies
- no fake ML performance claims
- demo values must be clearly distinguishable from real metrics

## 22. Future Backend Compatibility

The eventual replacement should be:

```text
Mock Prediction Service
        ↓
HTTP Prediction Service
        ↓
FastAPI
```

without rewriting the UI.

Prediction request/response contracts must be typed and presentation components must not know mock implementation details.

## 23. Git

Use incremental, logical commits rather than one giant unreviewable change.

Suggested checkpoints:

- `feat: establish churnguard frontend foundation`
- `feat: implement customer analysis vertical slice`
- `feat: add prediction result experience`
- `feat: add frontend validation and error states`
- `test: verify churnguard frontend flows`
- `refactor: polish frontend architecture`
- `docs: record frontend verification`

## 24. Stage Completion Rule

The stage passes only when:

1. Required frontend scope exists.
2. First vertical slice works end-to-end with sample data.
3. Required states exist.
4. Service boundary is replaceable.
5. Tests pass.
6. Build succeeds.
7. App runs.
8. Responsive behavior is checked.
9. Accessibility is checked.
10. Visual verification is performed.
11. No known blocking defects remain.
12. Acceptance checklist is satisfied.
13. Agent provides evidence.

Only then may the next stage begin.

## 25. Forbidden Shortcuts

Do not:

- skip testing because the UI looks right
- skip visual verification because the build passes
- invent ML metrics
- pretend mock predictions are trained-model outputs
- add backend code merely to make the frontend appear complete
- replace approved architecture without justification
- create unnecessary pages
- fill empty space with meaningless widgets
- use fake testimonials/business claims
- mark unfinished functionality complete
- advance because code compiles

## 26. Final Agent Report

Report:

### Implemented
What was built.

### Tests
Exact commands and results.

### Build
Exact command and result.

### Runtime
How the app was run and verified.

### Visual verification
Screens, states and viewports inspected.

### Sample scenarios
Four fixture scenarios tested.

### Known issues
Anything remaining or unverified.

### Gate decision

`PASS — frontend stage proven`

or

`BLOCKED — frontend stage not yet proven`

Never report PASS while a mandatory acceptance criterion is unverified.
