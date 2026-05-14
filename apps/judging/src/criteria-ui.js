/**
 * Frontend-only UI metadata for criteria (icon, description, 1-5 anchors).
 *
 * The canonical criteria spine (id / label / weight / tieBreaker) lives in
 * /shared/criteria.js and is owned by the backend. This file augments each
 * criterion with presentation data the scorecard needs. Keyed by
 * track + criterion id from the backend.
 *
 * window.MTAHackCriteriaUI.augment(track) returns the merged array
 *   [{ id, label, weight, tieBreaker, icon, desc, anchors[5] }, ...]
 */
(function () {
  'use strict';

  // Anchor wording adapted from the reference scorecards. Concise, consistent
  // tone with the existing 1..5 progression (poor → exemplary).
  const META = {
    azure: {
      alignment: {
        icon: 'ti-train',
        desc: "Does the agent address a real MTA/transit problem with the right users, workflow, and intended outcome?",
        anchors: [
          "Vague or off-topic — no clear transit problem or stakeholder",
          "Transit connection exists but lacks specificity or evidence",
          "Clear MTA/transit problem with identifiable users and meaningful impact",
          "Well-researched problem with operational context and credible urgency",
          "Documented MTA pain point with strong stakeholder impact, scope, and context"
        ]
      },
      architecture: {
        icon: 'ti-robot',
        desc: "Does the agent execute a real loop (plan → call tools → observe → recover) using Azure AI Foundry? Tie-breaker.",
        anchors: [
          "No real agent loop — LLM used as a simple chatbot or text generator",
          "Partial agent behavior; tools called but no error handling or multi-step reasoning",
          "Working Foundry agent loop with tool calls, basic error handling, and observable output",
          "Multi-step reasoning, graceful failure recovery, and clear agent state",
          "Sophisticated orchestration — planning, tool use, self-correction, and resilience"
        ]
      },
      reliability: {
        icon: 'ti-shield-check',
        desc: "Are outputs grounded, guarded, and reliable? Does it gracefully handle bad input, missing data, and unsafe asks?",
        anchors: [
          "Hallucinates freely; no grounding, guardrails, or input validation",
          "Some grounding attempted but inconsistent; weak fallback behavior",
          "Reasonable grounding, basic safety filters, and predictable fallbacks",
          "Strong grounding in transit data, deliberate guardrails, and good edge-case handling",
          "Production-quality reliability: rigorous grounding, layered safety, observable failures"
        ]
      },
      ux: {
        icon: 'ti-microphone-2',
        desc: "Is the voice/UI experience polished, accessible, and pleasant to use under live demo conditions?",
        anchors: [
          "UI broken or confusing; voice/text interaction frustrates the user",
          "Functional but rough — latency, layout, or affordances need work",
          "Clear UI with usable voice/text loop and reasonable latency",
          "Polished UX with intentional design, low latency, and good accessibility",
          "Delightful, fast, accessible experience that elevates the agent"
        ]
      },
      demo: {
        icon: 'ti-presentation',
        desc: "Is the demo functional (not mocked)? Could this realistically pilot within MTA's operational constraints?",
        anchors: [
          "Demo is mocked, broken, or doesn't run end-to-end",
          "Works in limited scope; relies on placeholder data or has significant gaps",
          "Functional end-to-end demo; plausible path to a real MTA pilot exists",
          "Polished demo with real/realistic transit data; deployment considerations discussed",
          "Production-quality demo with credible MTA pilot roadmap and operational awareness"
        ]
      }
    },
    copilot: {
      alignment: {
        icon: 'ti-target',
        desc: "Does the agent address the assigned use case — the right users, the right workflow, and the intended business outcome?",
        anchors: [
          "Agent does not meaningfully address the assigned use case or misses the core user need",
          "Agent relates to the assigned use case but only partially addresses the intended workflow, user, or outcome",
          "Agent clearly addresses the assigned use case with appropriate users, workflow coverage, and intended value",
          "Agent strongly aligns to the assigned use case and thoughtfully interprets the business need, workflow, and users",
          "Agent is exceptionally well matched to the assigned use case, with complete coverage and a highly relevant approach"
        ]
      },
      design: {
        icon: 'ti-message-chatbot',
        desc: "Are topics, instructions, grounding, and conversation flow intentional? Tie-breaker.",
        anchors: [
          "Copilot is little more than generic Q&A with weak instructions and no meaningful orchestration",
          "Basic topics or prompts exist, but routing, instructions, or grounding are inconsistent",
          "Well-structured copilot with effective instructions, clear conversation flow, and reliable grounded responses",
          "Strong orchestration across topics, inputs, and fallback handling with a polished user experience",
          "Excellent conversational design, robust grounding and fallback strategy, and highly intentional orchestration"
        ]
      },
      actions: {
        icon: 'ti-bolt',
        desc: "Does the copilot complete real work through actions — Power Automate, connectors, or enterprise data — reliably and end-to-end?",
        anchors: [
          "No meaningful actions; copilot only answers questions without completing work",
          "An action was attempted, but execution is unreliable, incomplete, or heavily manual",
          "Working action flow that completes a useful task through Power Automate, connectors, or enterprise data",
          "Automation is well integrated, reliable, and clearly reduces effort across a real workflow",
          "Exceptional use of actions and automation with strong reliability, business impact, and extensibility"
        ]
      },
      branding: {
        icon: 'ti-palette',
        desc: "Does the agent have a clear identity — naming, personality, branding, and presentation that reinforce the use case?",
        anchors: [
          "Agent feels generic with little personality, weak naming, and minimal visual or branded identity",
          "Some creative touches are present, but the agent name, look, or personality feel only partially developed",
          "Agent has a clear identity with a fitting name, cohesive presentation, and creative elements that support the experience",
          "Strong creative execution with thoughtful branding, memorable personality, and polished visual presentation",
          "Highly distinctive agent with exceptional creativity, strong branding, and a memorable identity that enhances the solution"
        ]
      },
      demo: {
        icon: 'ti-presentation',
        desc: "Is the demo clear and end-to-end? Is there a credible path to pilot, rollout, and team adoption?",
        anchors: [
          "Demo is incomplete, unclear, or does not show the copilot working in context",
          "Demo works partially, but value story, usability, or next steps are not yet convincing",
          "Clear end-to-end demo with a plausible path to pilot, rollout, or team adoption",
          "Polished demo, strong storytelling, and practical plan for onboarding, iteration, and business use",
          "Executive-ready demo with strong adoption potential, clear next steps, and credible production path"
        ]
      }
    }
  };

  function augment(track) {
    const spine = (window.MTAHackCriteria && window.MTAHackCriteria.CRITERIA && window.MTAHackCriteria.CRITERIA[track]) || [];
    const meta = META[track] || {};
    return spine.map(function (c) {
      const m = meta[c.id] || {};
      return Object.assign({}, c, {
        icon: m.icon || 'ti-list-check',
        desc: m.desc || '',
        anchors: m.anchors || ['', '', '', '', '']
      });
    });
  }

  window.MTAHackCriteriaUI = { META: META, augment: augment };
}());
