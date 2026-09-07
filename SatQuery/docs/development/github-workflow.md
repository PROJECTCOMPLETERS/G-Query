# SatQuery AI

## Git Workflow

**Task:** NIAN-P1-007
**Phase:** Phase 1 — Foundation & Input
**Owner:** Nian — Tech Lead / System Architect
**Status:** Finalized

---

## 1. Purpose

This document defines the Git and GitHub workflow for the SatQuery AI development team.

The objective is to:

* Protect the stable `main` branch
* Allow developers to work independently
* Maintain clean integration
* Review changes before merging
* Reduce merge conflicts
* Maintain traceability between tasks and code
* Prevent accidental commits of secrets or large satellite data

---

# 2. Repository Structure

The repository uses:

```text
main
```

as the primary stable branch.

Developers work on their own branches and integrate their changes into `main` through Pull Requests.

```text
Developer
    │
    ▼
Personal Development Branch
    │
    ▼
Pull Request
    │
    ▼
Code Review
    │
    ▼
main
```

---

# 3. Main Branch Policy

The `main` branch is the protected and stable branch of SatQuery.

### Rules

```text
Direct push to main       ❌
Pull Request required     ✅
Code review required      ✅
Force push                ❌
Branch deletion           ❌
```

The purpose of `main` is to contain code that has passed the team's integration and review process.

---

# 4. Development Branches

Each developer should create a separate branch for their work.

There is **no mandatory branch naming convention**.

Developers may choose branch names according to their own preference.

For example:

```text
dataset-api
upload-feature
raster-validation
chat-ui
testing
p1-work
```

All of these are acceptable as long as the branch name clearly communicates its purpose.

### Principle

> **Branch naming is a developer preference; branch purpose must remain clear.**

---

# 5. Creating a Branch

Before starting new work, developers should update their local `main`.

```bash
git checkout main
git pull origin main
```

Then create a development branch:

```bash
git checkout -b <branch-name>
```

Example:

```bash
git checkout -b dataset-api
```

---

# 6. Development Workflow

The standard development cycle is:

```text
Update main
    ↓
Create development branch
    ↓
Implement task
    ↓
Test locally
    ↓
Commit changes
    ↓
Push branch
    ↓
Create Pull Request
    ↓
Code review
    ↓
Fix review comments
    ↓
Run checks/tests
    ↓
Merge into main
    ↓
Delete branch
```

---

# 7. Commit Guidelines

Commits should represent meaningful changes.

Avoid unclear commit messages such as:

```text
update
changes
final
test
new
```

Prefer descriptive messages such as:

```text
feat: add dataset creation endpoint
fix: validate unsupported raster files
docs: update dataset API documentation
test: add upload validation tests
```

Recommended commit categories:

```text
feat:
fix:
docs:
test:
refactor:
chore:
```

The team may use these conventions consistently, but commit messages should primarily remain clear and understandable.

---

# 8. Push Workflow

After completing a logical portion of work:

```bash
git status
git add .
git commit -m "feat: add dataset upload endpoint"
git push -u origin <branch-name>
```

Example:

```bash
git push -u origin dataset-api
```

---

# 9. Pull Requests

Changes should be integrated into `main` through Pull Requests.

A Pull Request should communicate:

* What was changed
* Why it was changed
* Which task it addresses
* How it was tested
* Whether architecture or shared contracts were affected

Recommended PR structure:

```markdown
## Summary

Describe the change.

## Related Task

Mention the relevant project task.

## Changes

- Change 1
- Change 2
- Change 3

## Testing

- [ ] Manual testing
- [ ] Unit tests
- [ ] Integration tests

## Architecture Impact

Mention whether the change affects:

- Module boundaries
- API contracts
- Common data structures
- Database structures
- Storage

## Checklist

- [ ] Code tested
- [ ] No unrelated changes
- [ ] No secrets committed
- [ ] Documentation updated if required
```

---

# 10. Code Review

At least one team member should review a Pull Request before it is merged.

Reviewers should consider:

### Functionality

Does the implementation satisfy the task?

### Architecture

Is the implementation located in the correct module?

For example:

```text
Raster processing
      ↓
data_engine/
```

rather than placing raster-processing logic inside API routes.

### Module boundaries

The implementation must respect the finalized SatQuery module boundaries.

For example:

```text
Frontend → Backend → Orchestration → Engines → Storage
```

The following should not occur:

```text
Frontend → MongoDB
Frontend → GridFS
Frontend → GDAL
Frontend → ML models
```

### Contracts

Reviewers should verify that changes follow the finalized:

* API contracts
* Common data structures
* Dataset schema
* Storage abstraction

---

# 11. Architecture-Sensitive Changes

Some changes have a larger impact on the project architecture.

Examples:

```text
API contracts
Common data structures
MongoDB schema
Storage architecture
Module boundaries
Technology decisions
Orchestration interfaces
```

These changes should receive Tech Lead review.

If an implementation requires changing an already finalized contract, the team should discuss and agree on the change before merging it.

---

# 12. Keeping Development Branches Updated

Other developers may merge changes into `main` while work is in progress.

Developers should periodically update their branch.

Example:

```bash
git checkout main
git pull origin main

git checkout <branch-name>
git merge main
```

After resolving any conflicts:

```bash
git add .
git commit -m "merge main into development branch"
git push
```

The team should avoid force-pushing shared branches.

---

# 13. Conflict Resolution

When a merge conflict occurs:

```text
Development Branch
        +
Latest main
        ↓
     Conflict
        ↓
Understand changes
        ↓
Resolve manually
        ↓
Run tests
        ↓
Commit
        ↓
Push
```

Developers should not blindly choose one side of a conflict.

For architecture, API, database, or shared-contract conflicts, the Tech Lead should make the final architectural decision.

---

# 14. Merge Strategy

The recommended merge strategy is:

> **Squash and merge**

Example:

```text
Development branch

● commit
● commit
● fix
● test
● final fix
       │
       ▼
 Pull Request
       │
       ▼
 Squash and Merge
       │
       ▼
     main
```

This keeps the `main` branch history relatively clean and focused on completed pieces of work.

---

# 15. What Must Not Be Committed

The following must not be committed to Git:

```text
.env
.env.local
API keys
Passwords
Database credentials
Authentication tokens
Private certificates
Large temporary files
node_modules/
Python virtual environments
Generated caches
IDE-specific files
```

The repository may contain:

```text
.env.example
```

with placeholder values.

Example:

```text
MONGODB_URI=<your-mongodb-uri>
```

Actual credentials remain local.

---

# 16. Satellite Data Policy

Satellite imagery must **not** be stored in Git.

Examples:

```text
❌ image.tif
❌ sentinel_image.tif
❌ SAR imagery
❌ large GeoTIFF files
❌ uploaded datasets
❌ generated analysis results
```

Git is used for:

```text
Source code
Documentation
Configuration
Tests
Model manifests
Dataset manifests
```

SatQuery satellite files are stored through:

```text
Application
    ↓
Storage Layer
    ↓
GridFS
    ↓
MongoDB
```

---

# 17. Task Traceability

Development should connect project tasks to Git work.

The general relationship is:

```text
Project Task
     ↓
Development Branch
     ↓
Commits
     ↓
Pull Request
     ↓
Code Review
     ↓
main
```

For example:

```text
Task:
Implement dataset upload

        ↓

Branch:
upload-feature

        ↓

Commits:
feat: add upload endpoint
test: validate uploaded files

        ↓

Pull Request

        ↓

Review

        ↓

main
```

The exact branch name remains the developer's choice.

---

# 18. Team Collaboration Rule

A developer should communicate with affected teammates when their change modifies a shared contract or another team's interface.

Example:

```text
Leo changes Dataset API
        ↓
Backend contract changes
        ↓
Frontend integration may be affected
        ↓
Prithi should be informed
```

Similarly:

```text
Rubin changes Data Engine output
        ↓
Another module consumes that output
        ↓
Affected developer should be informed
```

This reduces unexpected integration failures.

---

# 19. Repository Protection

The GitHub repository should eventually enforce the agreed rules through branch protection.

Recommended `main` configuration:

```text
┌───────────────────────────────┐
│          main                 │
├───────────────────────────────┤
│ Protected                     │
│ PR required                   │
│ Approval required             │
│ Force push disabled           │
│ Deletion disabled             │
│ CI checks when available      │
└───────────────────────────────┘
```

---

# 20. Responsibilities

### Tech Lead — Nian

Responsible for:

* Repository architecture
* `main` protection
* Architecture-sensitive reviews
* Resolving architectural conflicts
* Final decisions on shared contracts

### Developers

Responsible for:

* Working on development branches
* Testing their changes
* Creating Pull Requests
* Responding to review comments
* Avoiding secrets and large data files
* Keeping their work compatible with the agreed architecture

### All Team Members

Responsible for:

* Reviewing when requested
* Communicating breaking changes
* Respecting module boundaries
* Keeping `main` stable

---

# 21. Git Workflow Rules

The team's core rules are:

```text
1. main is protected.

2. Developers work on separate branches.

3. Branch names are the developer's preference.

4. Branches should have a clear purpose.

5. Changes reach main through Pull Requests.

6. Pull Requests require review.

7. Architecture-sensitive changes require Tech Lead review.

8. Do not force-push shared branches.

9. Do not commit secrets.

10. Do not commit satellite imagery or large datasets.

11. Keep commits meaningful.

12. Keep main stable.
```

---

# 22. Final Git Workflow

```text
                    ┌───────────────┐
                    │     main      │
                    │   Protected   │
                    └───────▲───────┘
                            │
                       Pull Request
                            │
                      Code Review
                            │
                     Developer Branch
                            │
                    ┌───────┴───────┐
                    │               │
                  Commit          Test
                    │               │
                    └───────┬───────┘
                            │
                         Push
                            │
                       GitHub Repo
```

---

# 23. Completion Criteria

NIAN-P1-007 is complete when:

* [x] `main` branch policy is defined
* [x] Development branch workflow is defined
* [x] Branch naming is left to developer preference
* [x] Pull Request workflow is defined
* [x] Code review requirement is defined
* [x] Merge strategy is defined
* [x] Conflict resolution process is defined
* [x] Commit guidelines are defined
* [x] Secret protection rules are defined
* [x] Satellite-data Git policy is defined
* [x] Architecture-sensitive review rules are defined
* [x] Team responsibilities are defined

**Status: COMPLETE**

