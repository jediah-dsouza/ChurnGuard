# Emil Kowalski Skills — Design & Motion Reference

## Purpose

This document distills the relevant design and animation principles from **Emil Kowalski's skills** for ChurnGuard.

Source:
https://github.com/emilkowalski/skills

The reference focuses on helping designers and engineers make better interface and animation decisions, particularly around motion curves, durations, properties, interaction quality, and review.

## Core Principle

Small interaction decisions compound.

A good interface is not merely static styling; timing, easing, transition behavior, feedback, and interaction details contribute to perceived quality.

## 1. Animate With Intent

Use animation when it explains:

- entering/leaving
- state changes
- feedback
- hierarchy
- continuity
- progress

Do not animate everything.

## 2. Choose the Right Motion Characteristics

For each animation consider:

- property being animated
- duration
- easing/curve
- delay
- trigger
- interruption behavior

Avoid defaulting to the same animation for every interaction.

## 3. Prefer Appropriate Properties

Favor performant, visually appropriate properties such as:

- transform
- opacity

Avoid motion that causes unnecessary layout work.

## 4. Risk Results Need Restraint

ChurnGuard handles potentially consequential customer-retention decisions.

Do not use:

- flashing warnings
- aggressive pulsing
- dramatic transitions
- distracting celebratory animations

A high-risk state should feel clear and important, not sensational.

## 5. Micro-interactions

Good candidates include:

- button feedback
- form validation
- sample selection
- result reveal
- driver expansion
- recommendation confirmation
- loading transitions

Keep these interactions fast and understandable.

## 6. Loading and State Transitions

A loading state should communicate that work is happening without creating uncertainty.

Transitions between:

- idle
- loading
- success
- error

should be coherent and not visually jarring.

## 7. Reduced Motion

Respect:

`prefers-reduced-motion`

When reduced motion is enabled, preserve state clarity without requiring animation.

## 8. Animation Review

Before shipping motion, ask:

- Does it communicate something?
- Is the timing appropriate?
- Is the easing appropriate?
- Can the user interrupt it?
- Does it delay the task?
- Does it distract from risk or action?
- Does it work with reduced motion?

If the answer is no, remove or simplify it.

## Agent Instructions

Do not import an animation style wholesale from the reference.

Use its decision-making principles to make ChurnGuard feel refined without becoming flashy.
