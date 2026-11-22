import { defineConfig } from "vitest/config";

// First-party JS files, listed by name so a vendored file cannot silently
// enter the coverage denominator.
const FIRST_PARTY_JS = [
  "pikaraoke/static/js/recent-searches.js",
  "pikaraoke/static/js/splash.js",
];

export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["tests/js/**/*.test.js"],
    coverage: {
      provider: "v8",
      include: FIRST_PARTY_JS,
      reporter: ["text", "html"],
      reportsDirectory: "coverage/js",
    },
  },
});
