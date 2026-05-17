# 📝 Lab 03 - Spec-Driven Development

| 📋 Attribute | Value |
|-------------|-------|
| ⏱️ **Duration** | 45 minutes |
| 📊 **Difficulty** | ⭐⭐ Intermediate |
| 🎯 **Prerequisites** | Lab 01 completed |

---

## 📈 Progress Tracker

```
Lab Progress: [░░░░░░░░░░] 0% - Not Started

Checkpoints:
□ Step 1: Understand the Templates
□ Step 2: Write Your Spec (Exercise 03a)
□ Step 3: Generate Code from Spec (Exercise 03b)
□ Create Escalation Detection Agent Spec
□ Create Higher Ed Constitution
```

---

## 🌟 Overview

Spec-driven development is a methodology where you write detailed specifications *before* writing code. This approach is particularly powerful when working with AI coding assistants like GitHub Copilot, as clear specifications help the AI generate more accurate, aligned code on the first attempt.

In this lab, you will learn to write specifications that serve as contracts between human intent and AI-generated code, ensuring that generated solutions meet your exact requirements.

## 🎯 Learning Objectives

By the end of this lab, you will be able to:

1. 📋 **Write a SPEC.md** for an agent feature that clearly defines requirements, constraints, and success criteria
2. 🛡️ **Create a constitution.md** with guardrails that establish boundaries and principles for AI agent behavior
3. 💻 **Generate code from spec** using GitHub Copilot, leveraging your specifications as context

## 📋 Prerequisites

- ✅ Lab 01 completed (Development Environment Setup)
- 🤖 GitHub Copilot extension installed and authenticated
- 📝 Basic understanding of markdown formatting

## 🤔 What is Spec-Driven Development?

Spec-driven development inverts the traditional "code first, document later" approach. Instead, you:

1. 🎯 **Define the problem** - What are you trying to solve?
2. 📋 **Specify the solution** - What should the solution do, exactly?
3. 🛡️ **Establish boundaries** - What should the solution NOT do?
4. 💻 **Generate code** - Use AI assistants with full context of your spec
5. ✅ **Validate against spec** - Does the generated code meet all criteria?

### 🌟 Benefits for AI-Assisted Development

- 🚫 **Reduced hallucination** - Clear specs constrain AI output to your requirements
- ⚡ **Faster iteration** - Less back-and-forth when AI understands intent upfront
- 📊 **Verifiable output** - Success criteria provide objective measures
- 👥 **Team alignment** - Specs serve as documentation and contracts

## 📚 Lab Structure

This lab contains two exercises:

| 📋 Exercise | 📝 Title | ⏱️ Duration | 📖 Description |
|----------|-------|----------|-------------|
| 03a | Write a Spec | 25 min | Create a specification for an Escalation Detection Agent |
| 03b | Generate from Spec | 20 min | Use Copilot to generate code from your specification |

## 📝 Step-by-Step Instructions

### 🔹 Step 1: Understand the Templates (5 minutes)

Review the templates provided in the `templates/` directory:

- 📄 **spec-template.md** - Structure for writing feature specifications
- 🛡️ **constitution-template.md** - Structure for defining agent guardrails

These templates provide scaffolding for your specifications.

### 🔹 Step 2: Write Your Spec (Exercise 03a - 25 minutes)

Navigate to `exercises/03a-write-spec.md` and follow the instructions to:

1. 🎯 Define the Escalation Detection Agent feature
2. 👤 Write user stories from multiple perspectives
3. 📋 Document functional requirements
4. ✅ Establish success criteria and constraints
5. 🛡️ Create a constitution with guardrails

### 🔹 Step 3: Generate Code from Spec (Exercise 03b - 20 minutes)

Navigate to `exercises/03b-generate-from-spec.md` and follow the instructions to:

1. 📄 Prepare your spec as Copilot context
2. 💬 Use strategic prompting to generate code
3. ✅ Validate generated code against your spec
4. 🔄 Iterate and refine based on spec compliance

## ✅ Deliverables

By the end of this lab, you will have created:

### 1. 📋 Escalation Detection Agent Spec (`your-spec.md`)
   - ✅ Complete feature specification following the template
   - 👤 User stories covering student, advisor, and system perspectives
   - 📋 Detailed functional requirements
   - 📊 Measurable success criteria

### 2. 🛡️ Higher Ed Constitution (`your-constitution.md`)
   - 📜 Core principles for AI agents in educational contexts
   - 🚧 Clear agent boundaries
   - 🚫 Prohibited actions and behaviors
   - 🔐 FERPA and accessibility considerations

## 🏗️ Key Concepts

### 📊 The Specification Hierarchy

```
🏛️ Constitution (organization-wide principles)
    |
    v
📋 Feature Spec (specific feature requirements)
    |
    v
💻 Generated Code (implementation)
```

### 💡 Effective Spec Writing Tips

1. 🎯 **Be specific** - Vague specs produce vague code
2. 📝 **Include examples** - Show expected inputs and outputs
3. ⚠️ **Define edge cases** - What happens in unusual situations?
4. 🚫 **Set constraints** - What must the solution NOT do?
5. 📊 **Make success measurable** - How do you know it works?

## 🔧 Troubleshooting

### ❌ Copilot generates code that doesn't match my spec

- 📄 Ensure your spec is in an open editor tab (Copilot uses open files as context)
- 💬 Use Agent Mode in Copilot Chat, which automatically includes workspace context for your spec
- ✂️ Break down large specs into smaller, focused sections
- 📝 Add inline comments referencing specific spec sections

### ❌ My spec is too vague

- 📝 Add concrete examples with expected inputs/outputs
- ⚠️ Include error scenarios and edge cases
- 🔗 Reference existing similar features for consistency
- 👀 Have a teammate review for clarity

### ❌ Constitution principles conflict with requirements

- ⚖️ Prioritize principles (which takes precedence?)
- 📋 Add explicit exception handling in the spec
- 📝 Document the conflict resolution approach
- 🔄 Consider if the feature needs redesign

### ❌ Generated code is too complex

- ✂️ Simplify your spec to essential requirements only
- 🎯 Remove "nice to have" features for initial generation
- 📈 Generate incrementally (core first, then enhancements)
- 🔍 Use Copilot's explain feature to understand the output

## 📚 Additional Resources

- 📖 [Specification by Example](https://en.wikipedia.org/wiki/Specification_by_example) - Background on spec-driven approaches
- 🤖 [GitHub Copilot Documentation](https://docs.github.com/en/copilot) - Official Copilot guides
- 🔐 [FERPA Basics for Developers](https://studentprivacy.ed.gov/) - Understanding educational data privacy

## ➡️ Next Steps

After completing this lab, proceed to:

**[Lab 04 - Build RAG Pipeline](../04-build-rag-pipeline/README.md)** 🔍

In Lab 04, you'll build production-ready AI agents with your specs.

---

## 🚀 Ready to Begin?

Start with **[Exercise 03a: Write a Spec](exercises/03a-write-spec.md)** 📝

---

## 📊 Version Matrix

| Component | Required Version | Tested Version |
|-----------|-----------------|----------------|
| 🤖 GitHub Copilot | Latest | 1.x |
| 🖥️ VS Code | 1.96+ | 1.99+ |
| 📝 Markdown | CommonMark | 0.30 |

---

<div align="center">

[← Lab 02](../02-azure-mcp-setup/README.md) | **Lab 03** | [Lab 04 →](../04-build-rag-pipeline/README.md)

📅 Last Updated: 2026-02-04 | 📝 Version: 1.0.0

</div>
