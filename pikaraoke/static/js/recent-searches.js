// Recent YouTube searches, kept on this device only: localStorage is never sent
// to the server, so one phone's history is not shared with the room.
//
// A classic script rather than a module: the search page has no bundler and
// reads the API off window. The CommonJS guard lets vitest load the same file.
(function (global) {
  const STORAGE_KEY = "recent-searches";
  const LIMIT = 6;

  function load(storage = global.localStorage) {
    try {
      const stored = JSON.parse(storage.getItem(STORAGE_KEY) || "[]");
      if (!Array.isArray(stored)) return [];
      return stored.filter((term) => typeof term === "string").slice(0, LIMIT);
    } catch {
      // Malformed JSON or denied storage (private mode) reads as a first visit,
      // and the rest of the search page keeps working.
      return [];
    }
  }

  function record(term, storage = global.localStorage) {
    const trimmed = term.trim();
    const terms = load(storage);
    if (!trimmed) return terms;
    const folded = trimmed.toLowerCase();
    const updated = [trimmed, ...terms.filter((item) => item.toLowerCase() !== folded)].slice(
      0,
      LIMIT,
    );
    save(updated, storage);
    return updated;
  }

  function clear(storage = global.localStorage) {
    try {
      storage.removeItem(STORAGE_KEY);
    } catch {
      // Nothing to clear when the browser refuses storage.
    }
  }

  function save(terms, storage) {
    try {
      storage.setItem(STORAGE_KEY, JSON.stringify(terms));
    } catch {
      // Keep the list for this page even when it cannot persist.
    }
  }

  const api = { STORAGE_KEY, LIMIT, load, record, clear };
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    global.RecentSearches = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
