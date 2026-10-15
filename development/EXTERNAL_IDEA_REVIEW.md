# External Idea Review for Margin and Lore Control

Review date: 2026-09-22

## Purpose

This document turns the Reddit posts and GitHub repositories reviewed for the
project into an explicit intake plan. These sources are references, not bundled
dependencies and not approved feature scope by themselves.

The governing rule is: preserve the working Margin editor, establish a tested
baseline, and adopt one bounded improvement at a time. Joe retains all product,
manuscript, KEEP/FIX/REWRITE, and canon authority.

## Non-negotiable product behavior

- Direct chapter editing happens in Margin's main text editor. Prompt boxes are
  optional AI-assistance controls, not the primary editing interface.
- Protected Pilot Mode edits a disposable or protected working copy. It must
  not silently modify the source chapter, approved lore, or the Obsidian vault.
- AI may extract, diagnose, compare, and propose. It may not approve manuscript
  prose or canon.
- Lore Control is a separate Margin module with book and universe scope.
- Obsidian remains the human-readable canon vault. Word remains the authoritative
  final-revision environment.
- Every user-facing addition requires acceptance criteria, automated tests where
  practical, independent verification, and a small manual Windows check.

## Adoption gates

1. **Recover** the working DARC Pilot source without changing the installation.
2. **Reproduce** the working behavior from a clean GitHub clone.
3. **Verify** direct editing, reset, export, finish, source protection, startup,
   shutdown, and error recovery.
4. **Pilot** three chapters and freeze the known-good Margin baseline.
5. **Intake** one external idea at a time through a feature branch.
6. **Build Lore Control** as a separate module after Margin is functionally
   complete.
7. **Connect Obsidian** only after Lore Control's proposal, conflict, approval,
   provenance, and rollback behavior is stable.

## Candidate review

| Source | Useful idea | Margin/Lore application | Decision | Earliest gate |
|---|---|---|---|---|
| [Margin upstream](https://github.com/prxshetty/margin) and [DarcRanger fork](https://github.com/DarcRanger/margin) | Markdown editor, local workspace, prompt assets, harness support, AI diff workflow | Preserve as the product base; finish and test existing behavior before expansion | **Core baseline** | Now |
| [Claude Mission Control](https://github.com/nemss/claude-mission-control) | Supervisor/Builder/Verifier roles, persistent project state, task queue, decision and lesson logs, bounded repair loop | Development supervision only; no manuscript or canon authority | **Adopted selectively** | Already implemented |
| [Story-Film-Skills](https://github.com/badgids/Story-Film-Skills) | Typed reference authority, stable IDs, deterministic validators, checkpoints, recoverable workflows | Source-register rules, canon authority types, stable character/event IDs, validation reports | **Adopt pattern; do not install wholesale** | Baseline design; implementation after freeze |
| [fiction-forge](https://github.com/geobond13/fiction-forge) | Timeline-scoped context, cold-read ledger, knowledge/prop/promise registers, append-only issues, scanners as regression fences | Lore context packets, continuity review, reader-state and temporal-knowledge checks | **High-value Lore reference** | Lore Control design |
| [Ownstate](https://github.com/aibunny/ownstate) | Evidence, provenance, scoped context contracts, candidate knowledge, human approval, versioned state | Evidence -> candidate lore -> conflict review -> Joe approval -> versioned canon | **Architectural reference only**; too young for a foundation dependency | Lore Control design |
| [NoteMesh](https://github.com/ChangeNode/notemesh) | Obsidian/Git Markdown access through MCP, sync-independent indexing, path-security boundary | Possible adapter between Lore Control and the vault; copy no code without license and security review | **Evaluate as adapter/reference** | After Lore workflow is stable |
| [Linked Particles](https://linkedparticles.org/) | Linked concepts and graph-style knowledge navigation | Optional relationship view for characters, events, organizations, places, and evidence | **Defer**; navigation is not required for canon correctness | Later Lore UI |
| [agi-memory](https://github.com/kdbhalala/agi-memory) | Lightweight local decisions, bug-fix, lesson, and session memory | The useful development-memory pattern is already covered by project Markdown files and Git | **Do not add another memory database now** | Revisit only if current retrieval fails |
| [Understand Anything](https://github.com/Egonex-AI/Understand-Anything) | Code graph, guided architecture tours, dependency and diff-impact analysis | Optional developer audit when Margin becomes difficult to understand | **Tooling experiment only**; potentially high token cost and not a user feature | After source recovery, if needed |
| Graphify candidate from the Hermes roundup | Knowledge-graph generation | Could visualize approved lore relationships, but does not replace authority, provenance, or conflict review | **Unverified/defer** until the exact repository, license, and output quality are reviewed | Later Lore UI |
| [Hermes JEV approvals](https://github.com/anpicasso/hermes-jev-approvals) and related JEV routing ideas | Fast bounded classification with confidence and escalation | Future provider-neutral Decision Service for routing checks or flagging uncertain findings | **Do not depend on the proof of concept**; never allow it to approve canon | Post-baseline research |
| Storycraft [skills/workflows Reddit post](https://www.reddit.com/r/BookWritingAI/comments/1wdrxvp/skills_workflows_free/) | Modular character, developmental-editing, line-editing, psychology, voice, and project-setup skills | A selectable audit palette inside Margin; outputs remain suggestions linked to evidence | **Review individual skills only**; do not import the whole library | After baseline freeze |
| “Less AI-like writing” skill concept | Detection of repetitive or synthetic-sounding prose habits | Optional `AI Prose Pattern` diagnostic alongside user-approved guides | **Diagnostic only**; no automatic rewriting or generic style normalization | Later Margin audit |
| Context-engineering/Ownstate Reddit discussions | Small task-specific context packets, explicit update/invalidate/replace rules | Context Router selects only relevant approved lore, recent state, and task rules | **Adopt as a design principle** | Lore Control design |
| `last30days`, agent skill directories, and similar roundup tools | Discover current research, repositories, and reusable skills | External research and candidate discovery only | **Keep outside Margin runtime** | As needed |
| Superpowers and general coding-skill collections | Spec-first development, debugging, test discipline, review workflows | Mine individual development practices only when they improve the existing supervisor loop | **No wholesale installation** | As needed |

## Source and license verification boundary

- Margin is already licensed under GNU AGPL v3 with the repository's stated
  additional permission. External code still needs compatibility, attribution,
  provenance, and security review before copying.
- Story-Film-Skills identifies Apache-2.0 licensing, and fiction-forge identifies
  MIT licensing. Their useful concepts can be implemented independently; code
  reuse would still preserve required notices.
- NoteMesh identifies AGPL-3.0 licensing. Its path-security and adapter patterns
  are useful, but integrating its code or operating it as a service requires a
  dedicated technical and license review.
- Claude Mission Control's reviewed repository page did not establish a license.
  Margin has therefore adopted only general workflow concepts, not copied code.
- Ownstate, Graphify, JEV experiments, skill roundups, and other fast-moving
  candidates must be rechecked at an exact pinned revision before any code,
  prompt, or dependency is admitted.
- Reddit claims and repository self-reported benchmarks are leads, not proof.
  Margin's own disposable-fixture tests and Windows acceptance evidence control
  every adoption decision.

## Ordered possible changes

### A. Finish before importing product ideas

1. Recover and commit the installed DARC Pilot source.
2. Add an explicit direct-editor acceptance test.
3. Create a source manifest for protected-pilot files and behavior.
4. Test start, direct edit, reset, approved export, finish, failure recovery,
   and proof that the original chapter is unchanged.
5. Verify a clean Windows clone can launch, close, and relaunch without orphaned
   processes.
6. Complete the three-chapter pilot and tag/freeze the baseline.

### B. First post-baseline Margin improvements

1. **Audit palette:** expose named, individually selectable audits rather than
   requiring users to write prompts for routine checks.
2. **Evidence-linked findings:** every finding records rule, passage, rationale,
   confidence, and source guide; findings do not silently edit prose.
3. **Issue lifecycle:** proposed -> accepted for edit -> resolved/dismissed,
   with a durable issue log and no repeated rediscovery of dismissed findings.
4. **Bounded context packets:** load only the chapter, nearby state, selected
   guides, and relevant approved lore for the current task.
5. **Regression fences:** rerun deterministic checks after an edit to catch
   reintroduced patterns or continuity errors.
6. **Optional prose-pattern report:** measure against Darc-specific targets
   before recommending changes; generic “de-AI” rules cannot control voice.

### C. Lore Control module

1. Separate workspace/navigation for universe, series, book, and chapter scope.
2. Stable IDs and typed authority for characters, events, organizations,
   locations, mechanics, source documents, and rulings.
3. Search and retrieval that distinguishes approved canon, candidate lore,
   superseded claims, conflicts, and unknowns.
4. Proposal inbox for additions and modifications with provenance and evidence.
5. Conflict comparison showing existing claim, proposed claim, both sources,
   affected books/chapters, and confidence without choosing the winner.
6. Temporal knowledge and reader-state ledgers so a character or reader cannot
   know information before the relevant event.
7. Joe-controlled approve, edit, reject, defer, and supersede actions.
8. Versioned commit, diff, rollback, and audit history.
9. Obsidian adapter only after all preceding behavior passes with disposable
   fixtures; approved-only synchronization by default.
10. Optional graph view after the list/search/review workflow proves usable.

### D. Development tooling experiments, not product features

1. Run Understand Anything against the recovered repository only if the normal
   source manifest cannot explain dependencies or change impact.
2. Keep a provider-neutral decision interface so a future classifier such as
   JEV can be benchmarked without redesigning Margin around it.
3. Evaluate external skills in temporary fixtures at pinned revisions; promote
   only the instruction or test that survives review.

## Explicit exclusions

- No wholesale repository merges or “install everything” skill collections.
- No automatic canon approval, silent vault writes, or AI-authored rulings.
- No automatic manuscript rewriting or bulk style normalization.
- No second memory database unless the Markdown/Git/Obsidian approach fails a
  documented retrieval requirement.
- No graph UI before reliable search, provenance, conflict review, and approval.
- No dependence on an early proof of concept for security or approval decisions.
- No feature may bypass the protected-source, test, verifier, and manual
  acceptance gates.

## Verification conclusion

The approach is coherent if it remains staged. Mission Control-style development
governance is already useful and low-risk. Story-Film-Skills and fiction-forge
offer the strongest patterns for authority, ledgers, context, and verification.
Ownstate reinforces the evidence-to-approved-state model but is not mature enough
to become a dependency. NoteMesh may eventually reduce Obsidian integration work,
but its interface, path security, and license obligations require a separate
review. Graph and fast-routing tools are optimizations, not foundations.

The next product action remains recovery and verification of the working Pilot
Mode. This document authorizes no external integration by itself; each adopted
change still requires a bounded backlog item and acceptance criteria.
