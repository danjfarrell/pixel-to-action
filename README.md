# pixel-to-action

A modular autonomous agent framework that uses visual input from a game or simulation to drive real-time control actions through perception, state estimation, and policy-based decision-making.

## Overview

This project is designed as an autonomy-focused framework, using a video game as a controlled environment for developing and testing closed-loop perception and control. The system begins with direct screen capture and can later be extended to camera-based input to simulate real-world sensing constraints such as distortion, lighting variation, and latency.

The goal is not just to build a game bot, but to build a reusable autonomy stack with clear separation between sensing, interpretation, decision-making, and actuation.

## Core Concepts

The framework is organized around the standard autonomy loop:

1. **Capture**
   - Acquire frames from a screen, emulator, video file, or camera

2. **Perception**
   - Detect important objects, UI features, prompts, and events

3. **State Estimation**
   - Convert raw detections into a simplified world state

4. **Decision-Making**
   - Choose the next action using rules, finite-state logic, or learned policies

5. **Control**
   - Send keyboard, mouse, or controller actions back to the environment

6. **Logging / Replay**
   - Record observations, states, actions, and outcomes for debugging and improvement

## Initial Scope

The first implementation targets a single game with:

- screen capture input
- lightweight computer vision
- simple rule-based behavior
- keyboard input control
- structured logging

Later phases may add:

- camera-based perception
- temporal tracking
- behavior trees or planners
- local ML models
- imitation learning or reinforcement learning
- support for multiple games

## Project Goals

- Build a reusable perception-to-action framework
- Keep the real-time loop self-contained and fast
- Create clear module boundaries for experimentation
- Demonstrate autonomy concepts in a practical, testable environment
- Evolve from deterministic screen-based sensing to noisier camera-based sensing

## Architecture

```text
Frame Source -> Perception -> State Builder -> Policy -> Controller
                    |              |             |
                    +-------> Logger / Replay <-+
