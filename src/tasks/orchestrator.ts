import { task, batch, logger } from "@trigger.dev/sdk/v3";
import type { ExtractClaimsPayload, ExtractedClaim } from "./extractClaims";
import { extractClaims, extractClaimsFn } from "./extractClaims";
import { verifySource, verifySourceFn } from "./verifySource";
import { analyzeHistory, analyzeHistoryFn } from "./analyzeHistory";

export interface OrchestratorInput extends ExtractClaimsPayload {}

export async function newsFactCheckerFn({ article }: OrchestratorInput) {
  const claims = await extractClaimsFn(article);

  // Run verification and historical analysis in parallel per claim
  const verifications = await Promise.all(claims.map((c) => verifySourceFn(c)));
  const historicalAnalyses = await Promise.all(
    claims.map((c) => analyzeHistoryFn(c))
  );

  return { claims, verifications, historicalAnalyses };
}

export const newsFactChecker = task({
  id: "news-fact-checker",
  run: async ({ article }: OrchestratorInput) => {
    // Example using batch API to trigger sub-tasks if you deploy to Trigger.dev
    try {
      const claimsResult = await batch.triggerByTaskAndWait([
        { task: extractClaims, payload: { article } },
      ]);

      if (!claimsResult.runs[0]?.ok) {
        logger.error("Failed to extract claims", {
          error: claimsResult.runs[0]?.error,
          runId: claimsResult.runs[0]?.id,
        });
        throw new Error(`Failed to extract claims: ${claimsResult.runs[0]?.error}`);
      }

      const claims = claimsResult.runs[0].output as ExtractedClaim[];

      const parallelResults = await batch.triggerByTaskAndWait([
        ...claims.map((c) => ({ task: verifySource, payload: c })),
        ...claims.map((c) => ({ task: analyzeHistory, payload: c })),
      ]);

      const verifications = parallelResults.runs
        .filter((run) => run.ok && run.taskIdentifier === "verify-source")
        .map((run) => run.output);

      const historicalAnalyses = parallelResults.runs
        .filter((run) => run.ok && run.taskIdentifier === "analyze-history")
        .map((run) => run.output);

      return { claims, verifications, historicalAnalyses };
    } catch {
      // Fallback to pure function orchestration for local runs
      return newsFactCheckerFn({ article });
    }
  },
});