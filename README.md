# Trigger.dev AI Agent Sample

A minimal sample that follows the Trigger.dev AI Agents overview to:
- Extract claims from an article
- Verify claims against recent sources (LLM-only scaffold)
- Analyze historical context
- Orchestrate the workflow with parallel tasks

## Prerequisites
- Node.js 18+
- Environment variables for models you use (e.g. `OPENAI_API_KEY`)

## Install

```bash
npm install --save-dev typescript tsx @tsconfig/strictest
npm install @trigger.dev/sdk ai @ai-sdk/openai
```

Set your API key(s):

```bash
export OPENAI_API_KEY=your_key_here
```

## Run locally

```bash
npm run dev
```

You can edit `src/index.ts` to pass your own article text.

## Files
- `src/tasks/extractClaims.ts`
- `src/tasks/verifySource.ts`
- `src/tasks/analyzeHistory.ts`
- `src/tasks/orchestrator.ts`
- `src/index.ts`

## Notes
- The verification/history steps are LLM-powered scaffolds. Replace with real web/retrieval logic as needed.
- See the Trigger.dev guide for deeper orchestration patterns: [AI Agents Overview](https://trigger.dev/docs/guides/ai-agents/overview).