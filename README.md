# YTPM

Stands for "Yaron tmux project manager".
This is a TUI application for fast navigation between projects in tmux sessions
so no need to open new terminal for each project.

## Goals

Design and implement a TUI.
Use clean and scalable architecture.
Use Python for backend and Go for TUI frontend.
Work in small steps, fast iterations.
Extend later.

## Features:

- list open sessions
- navigate between open sessions
- create new sessions

In later versions:

- config file
- support stdin 
- support for input file

## Architecture

TUI -> CLI -> Core -> Multiplexer Adapter -> Multiplexer (Tmux, for now)
