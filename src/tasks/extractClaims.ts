import { task } from "@trigger.dev/sdk/v3";
import { openai } from "@ai-sdk/openai";
import { generateText } from "ai";

export interface ExtractClaimsPayload {
  article: string;
}

export interface ExtractedClaim {
  id: number;
  text: string;
}

export async function extractClaimsFn(article: string): Promise<ExtractedClaim[]> {
  const messages = [
    {
      role: "system" as const,
      content:
        "Extract distinct factual claims from the news article. Return a numbered list, one claim per line.",
    },
    { role: "user" as const, content: article },
  ];

  const response = await generateText({
    model: openai("o1-mini"),
    messages,
  });

  const claims: ExtractedClaim[] = response.text
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((claim, index) => ({
      id: index + 1,
      text: claim.replace(/^[0-9]+\.\s*/, ""),
    }));

  return claims;
}

export const extractClaims = task({
  id: "extract-claims",
  run: async ({ article }: ExtractClaimsPayload) => {
    return extractClaimsFn(article);
  },
});