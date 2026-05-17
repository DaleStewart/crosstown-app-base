# Exercise 03b: Generate Code from Your Spec

**Duration:** 20 minutes

## Overview

In this exercise, you will use GitHub Copilot to generate code from the specification you wrote in Exercise 03a. You will learn techniques for providing specifications as context and iteratively refining generated code to match your requirements.

## Learning Objectives

- Use specifications as context for AI code generation
- Apply strategic prompting techniques with Copilot
- Validate generated code against specification criteria
- Iterate on generated code to improve spec compliance

## Prerequisites

- Completed Exercise 03a (your-spec.md and your-constitution.md exist)
- GitHub Copilot extension active in VS Code
- Copilot Chat panel accessible (Ctrl+Alt+I (Windows/Linux) or Cmd+Shift+I (macOS), or click the Copilot Chat icon in the sidebar)

## Instructions

### Part 1: Prepare Your Context (5 minutes)

Before generating code, set up your workspace to maximize Copilot's understanding of your requirements.

#### Step 1: Open Your Specification Files

Open these files in VS Code tabs:
1. `your-spec.md` - Your feature specification
2. `your-constitution.md` - Your agent constitution

**Why?** Copilot uses open files as context. Having your specs visible helps Copilot generate aligned code.

#### Step 2: Create a Target File

Create a new file for the generated code:

```
generated/escalation_detector.py
```

Add a header comment referencing your spec:

```python
"""
Escalation Detection Agent

Implementation based on:
- Specification: your-spec.md
- Constitution: your-constitution.md

This module implements the escalation detection functionality
as defined in the feature specification.
"""
```

### Part 2: Generate Initial Code (7 minutes)

Use Copilot Chat to generate code from your specification.

#### Step 1: Open Copilot Chat

Open the Copilot Chat panel (Ctrl+Alt+I (Windows/Linux) or Cmd+Shift+I (macOS), or click the Copilot Chat icon in the sidebar)

#### Step 2: Reference Your Spec

Use the `Agent Mode` command to reference your specification:

```
Agent Mode Based on the specification in your-spec.md, generate a Python class
for the Escalation Detection Agent. Include:
1. The core detection method that analyzes text for escalation signals
2. Classification into the categories defined in my spec
3. Confidence scoring for detections
Follow the constraints in your-constitution.md for what the agent must NOT do.
```

#### Step 3: Review the Generated Code

Copilot will generate an initial implementation. Before accepting, review:

- [ ] Does it address the core functional requirements?
- [ ] Does it include the detection categories from your spec?
- [ ] Does it return the output format you specified?
- [ ] Does it respect the constraints from your constitution?

#### Step 4: Insert and Annotate

Insert the generated code into your file. Add comments noting which spec requirements are addressed:

```python
def detect_escalation(self, message: str) -> EscalationResult:
    """
    Analyze message for escalation signals.

    Implements:
    - FR-001: Process incoming student communications
    - FR-002: Detect escalation keywords and patterns
    - SC-001: Return result within 500ms (target)
    """
    # Generated code here...
```

### Part 3: Iterate and Refine (5 minutes)

Generated code rarely matches specifications perfectly on the first try. Use iterative refinement to improve compliance.

#### Iteration 1: Add Missing Requirements

Review your spec's functional requirements. For any missing ones, prompt Copilot:

```
Agent Mode The current escalation_detector.py is missing FR-003 from my spec
(categorize escalations by urgency level). Add a method that assigns urgency
levels: Critical, High, Medium, Low based on the criteria in my specification.
```

#### Iteration 2: Enforce Constitution Constraints

Check if the generated code respects your constitution's prohibited actions:

```
Agent Mode Review escalation_detector.py against the prohibited actions in
your-constitution.md. Add safeguards to ensure the agent cannot:
1. [First prohibited action from your constitution]
2. [Second prohibited action from your constitution]
Add validation or guards to prevent these actions.
```

#### Iteration 3: Add Error Handling

Ensure the code handles the error conditions from your spec:

```
Agent Mode Add error handling to escalation_detector.py for the error
conditions defined in my specification. Each error should return the
user-facing message I specified.
```

### Part 4: Validate Against Success Criteria (3 minutes)

Create a validation document to track spec compliance.

#### Step 1: Create Validation Notes

Create a file `generated/validation_notes.md`:

```markdown
# Spec Validation Notes

## Success Criteria Compliance

| Criterion | Status | Notes |
|-----------|--------|-------|
| SC-001: [Your criterion] | Pass/Fail/Partial | [Explanation] |
| SC-002: [Your criterion] | Pass/Fail/Partial | [Explanation] |
| SC-003: [Your criterion] | Pass/Fail/Partial | [Explanation] |

## Functional Requirements Coverage

| Requirement | Implemented | Method/Location |
|-------------|-------------|-----------------|
| FR-001 | Yes/No/Partial | [Where in code] |
| FR-002 | Yes/No/Partial | [Where in code] |

## Constitution Compliance

| Prohibited Action | Safeguard Implemented | How |
|-------------------|----------------------|-----|
| [Action] | Yes/No | [Explanation] |

## Gaps Identified

1. [Gap between spec and implementation]
2. [Gap between spec and implementation]

## Improvement Plan

1. [What needs to be fixed/added]
2. [What needs to be fixed/added]
```

#### Step 2: Calculate Compliance Rate

Count your criteria compliance:
- Total success criteria: ___
- Criteria met: ___
- Compliance rate: ___% (target: 80%+)

### Part 5: Final Refinement (Optional)

If your compliance rate is below 80%, perform additional iterations:

```
Agent Mode I need to improve spec compliance for escalation_detector.py.
The following requirements are not yet met:
1. [Unmet requirement]
2. [Unmet requirement]
Generate the additional code needed to meet these requirements.
```

## Prompting Tips

### Effective Prompts

**Good:** "Based on FR-002 in my spec, implement detection for the specific keyword categories I defined: mental health, academic distress, discrimination, and financial emergency"

**Less Effective:** "Add keyword detection"

### Referencing Specific Sections

Use precise references:
- "According to the Success Criteria section of your-spec.md..."
- "The prohibited actions in your-constitution.md state that..."
- "User Story 2's acceptance criteria require..."

### Handling Large Specifications

If your spec is extensive:
1. Generate code for one functional requirement at a time
2. Reference specific sections rather than the whole document
3. Build incrementally, validating each piece

## Common Issues

### Copilot Ignores My Spec

- Ensure spec file is open in an editor tab
- Use `Agent Mode` to explicitly reference files
- Quote specific sections from your spec in the prompt

### Generated Code Doesn't Match My Output Format

- Provide an explicit example in your prompt:
  ```
  Return results in this format:
  {
    "escalation_detected": true,
    "category": "mental_health",
    "urgency": "critical",
    "confidence": 0.95
  }
  ```

### Code Violates Constitution

- Add explicit guards in follow-up prompts
- Request that Copilot add validation checks
- Review generated code before accepting

## Deliverables

By the end of this exercise, you should have:

```
generated/
  |-- escalation_detector.py    # Your generated and refined code
  |-- validation_notes.md       # Documentation of spec compliance
```

## Reflection Questions

After completing this exercise, consider:

1. What percentage of your spec was accurately captured in the first generation?
2. Which types of requirements were easiest/hardest for Copilot to implement?
3. How did having a constitution affect the generated code?
4. What would you do differently in your spec to improve generation quality?

## Completion Criteria

You have successfully completed this exercise when:

- [ ] Generated at least one Python file from your specification
- [ ] Performed at least 2 iteration/refinement cycles
- [ ] Created validation notes documenting spec compliance
- [ ] Achieved at least 80% compliance with success criteria
- [ ] Documented any gaps between spec and implementation

## Summary

In this lab, you have learned the spec-driven development workflow:

1. **Write specifications** before code
2. **Use specs as context** for AI code generation
3. **Validate generated code** against specifications
4. **Iterate** to improve compliance

This methodology produces more predictable, aligned AI-generated code and creates documentation that serves as both development guide and acceptance criteria.

---

**Congratulations!** You have completed Lab 03: Spec-Driven Development.

Return to the [Lab README](../README.md) to review completion criteria and prepare for the next lab.
