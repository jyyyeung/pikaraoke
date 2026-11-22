// The recent-searches store is pure localStorage logic, so it is tested against
// a fake storage instead of a browser: the search page's DOM wiring is one
// render pass away from these functions, not a second copy of them.

import { createRequire } from "node:module";
import { beforeEach, describe, expect, it } from "vitest";

const require = createRequire(import.meta.url);
const recentSearches = require("../../pikaraoke/static/js/recent-searches.js");

function fakeStorage() {
  const items = new Map();
  return {
    getItem: (key) => (items.has(key) ? items.get(key) : null),
    setItem: (key, value) => items.set(key, String(value)),
    removeItem: (key) => items.delete(key),
  };
}

describe("recent searches", () => {
  let storage;

  beforeEach(() => {
    storage = fakeStorage();
  });

  it("starts empty", () => {
    expect(recentSearches.load(storage)).toEqual([]);
  });

  it("puts the newest term first", () => {
    recentSearches.record("abba", storage);
    recentSearches.record("queen", storage);
    expect(recentSearches.load(storage)).toEqual(["queen", "abba"]);
  });

  it("moves a repeated term to the front without duplicating it", () => {
    recentSearches.record("abba", storage);
    recentSearches.record("queen", storage);
    recentSearches.record("ABBA", storage);
    expect(recentSearches.load(storage)).toEqual(["ABBA", "queen"]);
  });

  it("keeps at most six terms", () => {
    for (let i = 1; i <= 7; i++) {
      recentSearches.record(`term ${i}`, storage);
    }
    expect(recentSearches.load(storage)).toEqual([
      "term 7",
      "term 6",
      "term 5",
      "term 4",
      "term 3",
      "term 2",
    ]);
  });

  it("trims a term", () => {
    recentSearches.record("  abba  ", storage);
    expect(recentSearches.load(storage)).toEqual(["abba"]);
  });

  it("ignores a blank term", () => {
    recentSearches.record("   ", storage);
    expect(recentSearches.load(storage)).toEqual([]);
  });

  it("reads malformed storage as empty", () => {
    storage.setItem(recentSearches.STORAGE_KEY, "{not json");
    expect(recentSearches.load(storage)).toEqual([]);
  });

  it("drops entries that are not strings", () => {
    storage.setItem(recentSearches.STORAGE_KEY, JSON.stringify(["abba", 7, null, "queen"]));
    expect(recentSearches.load(storage)).toEqual(["abba", "queen"]);
  });

  it("clears the list", () => {
    recentSearches.record("abba", storage);
    recentSearches.clear(storage);
    expect(recentSearches.load(storage)).toEqual([]);
  });

  it("survives storage that refuses reads and writes", () => {
    const denied = {
      getItem() {
        throw new Error("denied");
      },
      setItem() {
        throw new Error("denied");
      },
      removeItem() {
        throw new Error("denied");
      },
    };
    expect(recentSearches.load(denied)).toEqual([]);
    expect(recentSearches.record("abba", denied)).toEqual(["abba"]);
    expect(() => recentSearches.clear(denied)).not.toThrow();
  });
});
