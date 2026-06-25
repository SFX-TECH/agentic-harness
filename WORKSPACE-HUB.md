# The Workspace Hub

The most distinctive piece of my harness is a local, fully offline semantic hub over my entire multi-project workspace, exposed to coding agents over the Model Context Protocol. Any session, in any project, can retrieve the right context from any other project, and nothing ever leaves the machine.

## Why it exists
I run many projects at once. Context that lives in one project's docs is invisible to an agent working in another. Cloud retrieval would mean shipping proprietary source and client material to a third party. The hub solves both: one local index over everything, queryable by any agent, fully private.

## What it does
- **Semantic search across every project.** Ask where something lives or how it works, and get the most relevant chunks back with their project and file path, cited.
- **Ask, answered locally.** A local chat model answers a question across projects and cites its sources, with no cloud call.
- **A live project map.** Every project, its type, path, and a status line read fresh from disk.
- **Image search.** Screenshots and design assets are indexed too.
- **A knowledge graph** over the workspace for relationship queries.

## How it is built
- **Embeddings:** a local embedding model indexes the workspace into tens of thousands of chunks, text and images.
- **Chat:** a local instruction model serves the "ask" answers, through a local server's OpenAI-compatible API.
- **Two interfaces, one index:** the hub is exposed as an HTTP API for apps and as an MCP server for coding agents at the same time, so the same index serves a dashboard and a Claude Code session.
- **Freshness:** the index refreshes on a schedule, so answers track the working tree.
- **Local only:** the embedding model, the chat model, and the index all run on the build machine. No project data is sent anywhere.

## Why it matters for the harness
Durable context (see `CONTEXT-AS-CODE.md`) keeps one project's brain alive across sessions. The hub does the same across the whole workspace: it is the retrieval layer that lets any agent session start from everything I have built, not just the project it happens to be in, while keeping every byte of it local. It is the difference between an agent that knows this repo and an agent that knows my entire body of work.

This document describes the architecture and the role it plays. The running implementation and its index are private; the pattern is here for anyone who wants to build their own.
