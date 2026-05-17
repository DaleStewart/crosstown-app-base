# Lab 03 Completion Criteria

## Overview

This document defines the completion criteria for Lab 03: Spec-Driven Development. Use this checklist to verify you have successfully completed all lab objectives.

## Completion Checklist

### Exercise 03a: Write a Spec

- [ ] **Feature Specification Created**
  - [ ] Feature name and description clearly defined
  - [ ] At least 3 user stories written (student, advisor, system perspectives)
  - [ ] Minimum 5 functional requirements documented
  - [ ] Success criteria are measurable and testable
  - [ ] Constraints section identifies technical and compliance limitations

- [ ] **Constitution Document Created**
  - [ ] Core principles defined (minimum 3 principles)
  - [ ] Agent boundaries clearly established
  - [ ] Prohibited actions listed with rationale
  - [ ] FERPA compliance addressed
  - [ ] Accessibility requirements included

### Exercise 03b: Generate from Spec

- [ ] **Copilot Context Prepared**
  - [ ] Spec file is open in editor during generation
  - [ ] Constitution file is referenced appropriately
  - [ ] Initial prompt includes clear generation request

- [ ] **Code Generated Successfully**
  - [ ] At least one code file generated from spec
  - [ ] Generated code addresses core functional requirements
  - [ ] Code structure aligns with spec organization

- [ ] **Validation Completed**
  - [ ] Generated code reviewed against spec requirements
  - [ ] At least 2 iterative refinements performed
  - [ ] Final code meets minimum 80% of success criteria
  - [ ] Gaps between spec and generated code documented

## Deliverable Files

By completion, your lab directory should contain:

```
03-spec-driven-development/
  |-- your-spec.md           # Your completed feature specification
  |-- your-constitution.md   # Your completed constitution document
  |-- generated/             # Directory containing generated code
      |-- escalation_detector.py  # (or similar)
      |-- validation_notes.md     # Notes on spec compliance
```

## Quality Criteria

### Specification Quality

| Criterion | Poor | Adequate | Excellent |
|-----------|------|----------|-----------|
| Clarity | Ambiguous language | Mostly clear | Precise, unambiguous |
| Completeness | Missing sections | Core sections complete | All sections thorough |
| Testability | Unmeasurable criteria | Some measurable | All criteria testable |
| Examples | No examples | Basic examples | Edge cases included |

### Constitution Quality

| Criterion | Poor | Adequate | Excellent |
|-----------|------|----------|-----------|
| Principles | Generic/vague | Domain-relevant | Higher Ed specific |
| Boundaries | Unclear limits | Basic boundaries | Comprehensive limits |
| Prohibited Actions | Missing rationale | Actions listed | Actions + consequences |

### Generated Code Quality

| Criterion | Poor | Adequate | Excellent |
|-----------|------|----------|-----------|
| Spec Alignment | <50% match | 50-80% match | >80% match |
| Iteration | No refinement | 1-2 iterations | Multiple refinements |
| Documentation | No comments | Basic comments | Spec references in code |

## Success Indicators

You have successfully completed this lab when:

1. **You can explain** why spec-driven development improves AI code generation
2. **You have written** a specification that another developer could implement without clarification
3. **You have created** a constitution that prevents inappropriate agent behavior
4. **You have demonstrated** the iterative process of spec-to-code generation
5. **You understand** how to validate generated code against specifications

## Common Issues and Resolutions

| Issue | Resolution |
|-------|------------|
| Spec too broad | Focus on a single, specific feature |
| Copilot ignores spec | Ensure spec file is open and use Agent Mode |
| Generated code incomplete | Break spec into smaller generation requests |
| Constitution too restrictive | Balance principles with practical functionality |

## Instructor Verification

For instructor-led sessions, demonstrate:

1. Walk through your spec explaining each section
2. Show Copilot generating code with your spec as context
3. Explain one refinement iteration and why it was needed
4. Discuss how your constitution would prevent a specific harmful behavior
