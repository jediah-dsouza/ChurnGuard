# Anti-Slop — Design Reference

## Purpose

This document distills the **Anti-Slop** rules and philosophy for ChurnGuard frontend development.

Source:
https://github.com/miqdadbadjuber/anti-slop/

Anti-Slop explicitly describes itself as a filter rather than a style guide. It does not prescribe colors, fonts, or layouts; instead, it filters generic AI-generated UI, copy, and code. The project's central distinction is that `DESIGN.md` provides direction while Anti-Slop provides quality gates.

## Core Principle

Anti-Slop does not decide what ChurnGuard should look like.

Instead:

- `DESIGN.md` defines the ChurnGuard visual direction.
- Anti-Slop principles reject generic, unjustified, or low-quality AI output.
- The combination produces a specific and honest interface.

## 1. Do Not Invent Product Reality

Never invent:

- fake statistics
- fake customers
- fake testimonials
- fake logos
- fake performance claims
- fake integrations
- fake activity
- fake ML metrics

When sample data is used, clearly identify it as demo data.

## 2. Every Decorative Technique Needs a Reason

Do not add a visual technique because it is fashionable.

Examples requiring justification:

- gradients
- glow
- glassmorphism
- bento grids
- oversized icons
- colored stripes
- dot grids
- decorative illustrations
- animated backgrounds
- floating objects

The question is:

> What does this contribute to the product?

If the answer is nothing, remove it.

## 3. Avoid AI-Slop Signatures

Explicitly avoid generic patterns such as:

- sparkle/AI branding without product reason
- meaningless beta pills
- fake terminal windows
- repetitive card grids
- excessive rounded rectangles
- excessive gradients
- arbitrary decorative patterns
- generic hero copy
- vague AI-generated marketing language
- dashboards full of fabricated numbers

## 4. Keep Copy Human and Specific

ChurnGuard copy should describe actual product behavior.

Prefer:

> “High churn risk — prioritize retention outreach.”

over vague statements such as:

> “Unlock intelligent insights and transform your customer journey.”

Use concrete operational language.

## 5. Purpose-Gate Components

Before introducing a component, ask:

1. What user problem does it solve?
2. What information does it communicate?
3. Why is this representation better than a simpler one?
4. Is it consistent with the design system?

If there is no clear answer, do not add it.

## 6. Liveliness Without Slop

The interface should not become sterile.

Use controlled:

- energy
- rhythm
- motion

These should come from the product's own identity rather than decoration.

For ChurnGuard:

- Energy: calm and confident
- Rhythm: structured and operational
- Motion: subtle and purposeful

## 7. Delivery Gate

Before shipping a frontend slice, perform a final filter:

### Honesty
- [ ] No fabricated claims.
- [ ] Demo data is identifiable.
- [ ] No pretend backend functionality.

### Specificity
- [ ] The composition feels like ChurnGuard.
- [ ] An unrelated SaaS product could not use the screen unchanged.

### Purpose
- [ ] Major components have a reason.
- [ ] Decorative techniques have a reason.

### Quality
- [ ] Responsive.
- [ ] Accessible.
- [ ] States are complete.
- [ ] Copy is clear.
- [ ] No obvious AI-generated filler.

## 8. Interaction With DESIGN.md

`DESIGN.md` is the source of visual direction.

Anti-Slop is the filter.

Therefore:

```text
DESIGN.md
    ↓
defines what ChurnGuard should be
    ↓
Implementation
    ↓
Anti-Slop review
    ↓
remove unjustified/generic output
    ↓
Impeccable/Taste review
    ↓
polish and refine
```

## Agent Instructions

Do not make ChurnGuard beautiful by adding more decoration.

Make it better by:

- improving hierarchy
- improving specificity
- improving typography
- improving spacing
- improving interaction
- improving clarity
- removing unnecessary elements
- making the product feel intentional

A clean result is not automatically a good result. It must also have a clear ChurnGuard-specific design direction.
