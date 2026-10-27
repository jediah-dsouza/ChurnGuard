# UI UX Pro Max — Design Reference

## Purpose

This document distills the design principles from the **UI UX Pro Max** reference for use during ChurnGuard frontend development.

Source:
https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

The source describes UI UX Pro Max as an AI skill for professional UI/UX design across platforms and frameworks, with a major emphasis on generating tailored design systems rather than relying on generic templates.

## ChurnGuard Application

Use this reference to make design decisions intentionally from product requirements, audience, context, information hierarchy, and interaction needs.

### 1. Start from Product Context

Before styling a surface, establish:

- who is using it
- what decision they need to make
- what information matters most
- what action should happen next
- what constraints exist
- what states the interface must communicate

For ChurnGuard, the primary context is a retention operator triaging customer churn risk.

### 2. Build a Product-Specific Design System

Create and maintain a ChurnGuard `DESIGN.md` containing:

- typography system
- color tokens
- semantic risk colors
- spacing scale
- sizing rules
- borders and radii
- elevation
- component rules
- chart rules
- iconography
- motion
- responsive behavior
- accessibility states

Do not let individual pages invent their own visual language.

### 3. Use Information Hierarchy Deliberately

Prioritize:

1. customer identity/context
2. churn probability and risk level
3. reasons behind the risk
4. recommended retention action
5. supporting customer attributes

The visual hierarchy should reflect operational importance, not decorative preference.

### 4. Data Visualization Must Have a Job

Use a chart only when it helps the operator understand:

- risk
- comparison
- trend
- distribution
- model explanation
- operational prioritization

Never add charts merely because a dashboard appears incomplete without them.

### 5. Responsive Design Is Part of the Design

Design layouts deliberately for desktop, tablet, and mobile.

Do not treat mobile as a shrunken desktop.

### 6. Accessibility Is a Design Requirement

Include:

- visible focus
- semantic structure
- readable contrast
- meaningful labels
- keyboard usability
- clear error states
- non-color-only communication
- reduced-motion support

### 7. Avoid Generic Template Convergence

Do not default to:

- generic SaaS dashboard layouts
- arbitrary gradients
- repetitive card grids
- interchangeable component arrangements
- decorative widgets

Every major composition should make sense specifically for ChurnGuard.

## Agent Instructions

Before implementation, explain internally:

- What is the user trying to accomplish?
- What information has the highest decision value?
- What should attract attention first?
- What can be removed?
- What interaction reduces operator effort?

Then implement the simplest strong solution.

Do not copy the reference's visual output. Extract its design reasoning and apply it to ChurnGuard.
