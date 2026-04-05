# TODOS

## Layer C: Screenshot Annotation Replay
**Status:** Planned (Week 4)
**What:** Build `cradle/memory/visual_flashcards.py` for per-environment flashcard storage, add annotation rendering to `image_utils.py`, integrate few-shot injection into information-gathering preprocess.
**Why:** Few-shot visual examples are the most reliable way to improve LLM vision without fine-tuning. Layer A collects the correction data; Layer C converts it into visual teaching examples.
**Pros:** Compounding improvement over time. Human-reviewable annotated screenshot artifacts. Naturally adapts per environment.
**Cons:** Token-heavy (extra images in context window). Cold start until Layer A accumulates 20+ corrections. Needs occasional human review for ground-truth accuracy.
**Context:** Design doc: `~/.gstack/projects/cradle/root-claude-add-office-hours-page-U5djJ-design-20260405-050457.md`. Layer A must be live and validated (Week 3) before starting. Need 20+ corrections accumulated across environments.
**Depends on:** Layer A live + validation phase complete + 20+ corrections accumulated.
