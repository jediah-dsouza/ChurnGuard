# Impeccable — Design Reference

## Purpose

This document distills the design-review and frontend-quality principles from **Impeccable** for ChurnGuard.

Source:
https://github.com/pbakaus/impeccable

Impeccable describes itself as design guidance for AI coding agents with workflows for shaping, critiquing, auditing, polishing, hardening, animating, typesetting, improving layout, and reviewing frontend interfaces.

## Core Principle

Do not treat implementation completion as design completion.

The interface must be repeatedly reviewed and improved through visual and UX iteration.

## 1. Shape Before Building

Before writing a substantial UI surface, clarify:

- information architecture
- hierarchy
- layout
- interaction model
- states
- responsive behavior
- emotional/operational context

For ChurnGuard, high-risk results should feel clear and actionable rather than alarming or theatrical.

## 2. Critique the Whole Experience

Review:

- design specificity
- visual hierarchy
- information architecture
- discoverability
- composition
- typography
- color
- accessibility
- states
- copy
- edge cases
- cognitive load
- emotional journey

Ask:

> Could this interface belong to a completely different product without changing anything?

If yes, it is probably too generic.

## 3. Audit Technical UX Quality

Check:

- accessibility
- responsive behavior
- performance
- interaction states
- error handling
- text overflow
- edge cases
- loading behavior
- empty states

A visually attractive screen with broken keyboard navigation or poor error handling is not finished.

## 4. Polish as a Dedicated Stage

After functionality works:

- improve spacing
- refine typography
- correct alignment
- strengthen hierarchy
- remove visual noise
- tune color usage
- refine component consistency
- improve micro-interactions
- verify responsive behavior

Do not introduce decorative complexity just to make a screen look more impressive.

## 5. Purposeful Motion

Motion should clarify:

- state change
- navigation
- hierarchy
- feedback
- loading
- completion

Avoid animation that delays important information or distracts from the retention workflow.

## 6. ChurnGuard Review Loop

For each major frontend slice:

1. build
2. run
3. visually inspect
4. critique
5. audit
6. fix
7. retest
8. re-inspect

Only then mark the slice complete.

## Suggested Review Vocabulary

When reviewing ChurnGuard, explicitly consider:

- `shape` — is the experience structured correctly?
- `critique` — is the design clear and specific?
- `audit` — does it work technically?
- `polish` — what prevents it from feeling finished?
- `typeset` — are typography and hierarchy correct?
- `layout` — is spacing and composition intentional?
- `animate` — does motion communicate something useful?
- `harden` — what happens at the edges?

Do not copy Impeccable's commands mechanically. Use the underlying review discipline.
