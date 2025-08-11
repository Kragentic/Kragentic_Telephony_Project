import { newsFactCheckerFn } from "./tasks/orchestrator";

async function main() {
  const sampleArticle = `OpenAI released a new model today that can run on edge devices. The company also announced partnerships with several universities. The model reportedly achieves state-of-the-art performance on multiple benchmarks.`;

  const result = await newsFactCheckerFn({ article: sampleArticle });
  console.log("Result:", JSON.stringify(result, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});