# Taste Skill — Design Reference

## Purpose

This document distills the frontend design principles of **Taste Skill** for ChurnGuard.

Source:
https://github.com/Leonxlnx/taste-skill

Taste Skill focuses on improving AI-built interfaces through stronger layout, typography, motion, spacing, and overall visual quality instead of boilerplate-looking UI.

## Core Principle

A technically correct interface can still have poor taste.

ChurnGuard should therefore be evaluated not only for correctness but also for:

- composition
- restraint
- visual rhythm
- hierarchy
- typography
- spacing
- motion
- specificity

## 1. Layout Has Character

Do not automatically center everything or produce a repetitive grid of equal cards.

Use composition to establish hierarchy.

For ChurnGuard:

- risk should have visual priority
- explanation should support the risk signal
- recommendations should feel actionable
- secondary customer attributes should remain secondary

## 2. Typography Is a Structural Tool

Typography should communicate:

- hierarchy
- urgency
- density
- grouping
- confidence
- operational importance

Avoid using large text simply to make a page look impressive.

Create a deliberate type scale and use it consistently.

## 3. Spacing Creates Rhythm

Use a coherent spacing system.

Avoid:

- arbitrary gaps
- cramped forms
- giant empty areas
- every component having the same padding regardless of importance

Dense analytical areas can be compact; decision-critical content should have enough breathing room.

## 4. Visual Density Is Intentional

ChurnGuard is an operational analytics product.

It should be information-rich without becoming visually noisy.

Use density where operators need to scan many facts, while preserving emphasis around:

- risk
- drivers
- recommended action

## 5. Controlled Design Variance

The interface can use asymmetry, hierarchy, and distinctive composition when useful.

Do not add unusual layouts simply to appear creative.

Every deviation from a conventional layout should improve:

- scanning
- understanding
- focus
- actionability
- product identity

## 6. Motion Has a Role

Motion can reinforce:

- transition
- feedback
- hierarchy
- progress
- state change

It should remain restrained and respect reduced-motion preferences.

## 7. ChurnGuard Visual Dial

Use these conceptual dials:

### Design variance
Moderate.

Distinctive enough to avoid generic SaaS dashboards, but still appropriate for a professional retention team.

### Motion intensity
Low-to-moderate.

Motion should be useful rather than ornamental.

### Visual density
Moderate-to-high on analytical screens, with clear hierarchy around risk and action.

## Agent Instructions

Before adding a visual treatment, ask:

> Does this improve hierarchy, comprehension, interaction, or product identity?

If not, remove it.

Do not copy Taste Skill examples. Extract the design intent and create an original ChurnGuard system.
