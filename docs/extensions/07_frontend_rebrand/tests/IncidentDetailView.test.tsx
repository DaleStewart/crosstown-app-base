/**
 * Extension 07 — Frontend Rebrand
 * Failing tests: theme.ts and IncidentDetailView.tsx do not exist yet.
 *
 * Run with: npx vitest run docs/extensions/07_frontend_rebrand/tests/
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Theme token tests
// These imports WILL FAIL until apps/frontend/src/theme.ts is created.
// ---------------------------------------------------------------------------

describe("Brand theme tokens", () => {
  it("theme.ts exports brandTokens with required colour fields", async () => {
    // Dynamic import so vitest reports a clear failure rather than a parse error
    const mod = await import("../../../apps/frontend/src/theme");
    const tokens = mod.brandTokens ?? mod.default;

    expect(tokens, "theme.ts must export brandTokens (named or default)").toBeTruthy();
    expect(tokens.brandPrimary, "brandPrimary must be defined").toBeTruthy();
    expect(tokens.brandSecondary, "brandSecondary must be defined").toBeTruthy();
    expect(tokens.brandBackground, "brandBackground must be defined").toBeTruthy();

    // Validate they look like colour values (hex, rgb, hsl, or a CSS named colour)
    const colourPattern = /^(#[0-9a-fA-F]{3,8}|rgb|hsl|[a-z]+)$/;
    expect(tokens.brandPrimary).toMatch(colourPattern);
    expect(tokens.brandSecondary).toMatch(colourPattern);
    expect(tokens.brandBackground).toMatch(colourPattern);
  });
});

// ---------------------------------------------------------------------------
// IncidentDetailView component tests
// These imports WILL FAIL until apps/frontend/src/components/IncidentDetailView.tsx is created.
// ---------------------------------------------------------------------------

describe("IncidentDetailView component", () => {
  it("IncidentDetailView.tsx has a default export", async () => {
    const mod = await import(
      "../../../apps/frontend/src/components/IncidentDetailView"
    );
    expect(
      mod.default,
      "IncidentDetailView.tsx must have a default export (the React component)"
    ).toBeTruthy();
    expect(typeof mod.default).toBe("function");
  });

  it("IncidentDetailView renders id, line, description, status, and citations", async () => {
    const { default: IncidentDetailView } = await import(
      "../../../apps/frontend/src/components/IncidentDetailView"
    );
    const { render, screen } = await import("@testing-library/react");

    const mockProps = {
      id: 42,
      line: "L2",
      description: "SCADA timeout on bridge-7",
      status: "open",
      citations: ["log-entry-001", "log-entry-002"],
    };

    render(<IncidentDetailView {...mockProps} />);

    expect(screen.getByText(/42/)).toBeTruthy();
    expect(screen.getByText(/L2/)).toBeTruthy();
    expect(screen.getByText(/SCADA timeout/i)).toBeTruthy();
    expect(screen.getByText(/open/i)).toBeTruthy();
    expect(screen.getByText(/log-entry-001/)).toBeTruthy();
  });
});
