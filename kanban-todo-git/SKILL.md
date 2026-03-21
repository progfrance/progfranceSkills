# kanban-todo-git

   A hybrid TODO scanner and Kanban board that uses Git history to track work item flow and calculate metrics. Scans for BUG/TODO/IMPROVEMENT markers, organizes them into feature groups, and maintains a
   Markdown Kanban board (To Do, In Progress, Review, Done) with WIP limits, lead/cycle time metrics, and bottleneck analysis.

   ## When to Use This Skill
   - You want to track technical debt, feature requests, and improvements discovered in your codebase
   - You prefer a lightweight, Git-integrated system over external tools (Jira, Trello, etc.)
   - You work solo or with AI agents and need visualization of work-in-progress limits
   - You want metrics (lead time, cycle time, throughput) to improve your delivery predictability
   - You maintain a Marcel JeuxConcours-style project and discovered IPSOS typos/scheduler issues manually

   ## Core Concepts
   This skill combines two approaches:
   1. **TODO Scanner**: Discovers work items from code comments (BUG:/TODO:/IMPROVEMENT:)
   2. **Kanban Board**: Visualizes workflow with WIP limits and flow metrics

   Unlike pure TODO scanners, this skill tracks state changes of each item over time via Git history of the generated TODO.md file, enabling true flow metrics.

   ## Prerequisites
   - Git repository (initialized or existing)
   - Standard Unix tools: `find`, `grep`, `sed`, `awk` (available in Hermes environment)
   - No external dependencies

   ## Step-by-Step Workflow

   ### Step 0 — Initialize or Update TODO.md (called automatically)
   If `TODO.md` does not exist:
   - Create it with standard Kanban columns (To Do, In Progress, Review, Done)
   - Set WIP limits: To Do=3, In Progress=2, Review=1, Done=∞
   - Add header with timestamp

   If `TODO.md` exists:
   - Read last updated timestamp from header
   - Prepare to compare current codebase state with last known state

   ### Step 1 — Scan Codebase for Work Items
   Search for these exact markers in all non-binary, non-excluded files:
   - `BUG:`  → represents defects to fix
   - `TODO:` → represents features or improvements to implement
   - `IMPROVEMENT:` → represents refactoring or optimization opportunities

   Exclude these directories by default:
   - `node_modules/`, `.git/`, `dist/`, `build/`, `coverage/`, `.next/`, `out/`, `.cache/`

   For each match, record:
   - Full marker line (e.g., `// TODO: add Reddit RSS monitoring`)
   - File path and line number (normalized to forward slashes)
   - Marker type (BUG/TODO/IMPROVEMENT)

   ### Step 2 — Group into Feature Clusters
   Organize discovered items by:
   1. **Directory structure**: Items under `marcel/scheduler/` → "Scheduler" group
   2. **Explicit PRD files**: If `docs/` or `tasks/` contains `prd-*.md` files, use those as group names
   3. **Fallback**: Use top-level directory name (e.g., `marcel/` → "Marcel" group)

   Each group name should be concise and suitable for feeding into a PRD input process.

   ### Step 3 — Update TODO.md Columns
   For each discovered item:
   - If **new** (not found in previous TODO.md or code no longer contains the marker):
     - Add to **To Do** column as `- [ ] [BUG/TODO/IMPROVEMENT]: description (file:line)`
   - If **existing** and marker still present in code:
     - Keep current column state (do not auto-advance based on code changes alone)
     - Update file:line if location changed
   - If **existing** but marker **no longer found in code**:
     - Treat as resolved → move to **Done** column as `- [x] [BUG/TODO/IMPROVEMENT]: description (file:line)`
     - Preserve original timestamp and add resolution commit hash if detectable

   **Important**: Never remove unchecked items that still exist in the codebase (additive-only principle).

   ### Step 4 — Apply WIP Limits Advisory
   After populating columns:
   - Calculate current count per column
   - Compare to WIP limits (To Do:3, In Progress:2, Review:1)
   - If any column exceeds its limit, flag in output:
     ```
     ⚠️ WIP Advisory: In Progress has 3 items (limit: 2)
     ```

   ### Step 5 — Calculate Flow Metrics
   For each item in **Done** column:
   - Extract its full description string from TODO.md line
   - Use `git log` to find all commits where this line appeared in TODO.md
   - **Lead Time** = (first commit timestamp where item appeared in To Do) → (commit timestamp where it moved to Done)
   - **Cycle Time** = (first commit timestamp where item appeared in In Progress) → (commit timestamp where it moved to Done)
     - Detected by syntax change: `[ ]` → `[~]` → `[x]`

   Aggregate metrics:
   - **Average Lead Time** = mean of all completed items' lead times
   - **Average Cycle Time** = mean of all completed items' cycle times
   - **Throughput** = number of items completed in last 7 days
   - **Current WIP** = total items in To Do + In Progress + Review columns

   ### Step 6 — Detect Bottlenecks
   Analyze column accumulation:
   - If **Review** column has ≥2 items (exceeds WIP limit of 1) → bottleneck candidate
   - If **In Progress** has items stagnant > average cycle time → bottleneck candidate
   - If **To Do** grows steadily while Done throughput low → input bottleneck

   For each bottleneck, suggest:
   - **Root cause**: e.g., "Review column exceeds WIP limit due to slow manual validation"
   - **Action plan**: e.g., "Reduce WIP in In Progress to 1, automate basic validation checks"

   ### Step 7 — Generate Output Report
   Write to project root `TODO.md` with these sections:

   
   # TODO Board > Last updated: YYYY-MM-DD via /kanban-todo-git

   ## To Do (WIP limit: 3)
   - [ ] BUG: fix IPSOS timestamp handling in scheduler (marcel/scheduler.py:42)
   - [ ] TODO: add Reddit RSS monitoring for agent comparisons (docs/ideas/reddit-rss.md:1)
   - [ ] IMPROVEMENT: refactor state_scheduler.py Lancer maintenant feature (marcel/state_scheduler.py:88)

   ## In Progress (WIP limit: 2)
   - [~] TODO: review page_scheduler.py UI switch change (marlet/page_scheduler.py:17)

   ## Review (WIP limit: 1)
   - [~] TODO: base_filler.py credential refactor (marcel/base_filler.py:31)

   ## Done
   - [x] TODO: initial scheduler module setup (commit a1b2c3d)
   - [x] BUG: corrected typo in IPSOS API endpoint (commit d4e5f6g)

   ### Overall Progress
   \`\`\`
   [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 25.0% 5 / 20
   \`\`\`

   ### Current Metrics
   | Metric   | Current | Target |
   |----------|---------|--------|
   | Lead Time | 2.3 days | < 2.0 days |
   | Cycle Time | 1.1 days | < 1.0 day |
   | Throughput | 3/week | ≥ 5/week |
   | WIP | 4 | ≤ 4 (To Do:3 + In Progress:2 + Review:1) |

   ### Bottleneck Analysis
   **Current bottleneck:** Review
   **Root cause:** 2 items in Review column exceeds WIP limit of 1
   **Action plan:**
   1. Reduce In Progress WIP limit to 1 to decrease flow into Review
   2. Add automated credential validation to base_filler.py to speed up review

   ### Improvement Experiments
   | Experiment | Hypothesis | Measure | Duration |
   |------------|------------|---------|----------|
   | Try pairing review with Léo | Reduces Review time by 50% | Cycle Time | 3 days |
   | Automate IPSOS typo detection | Prevents BUG introduction | BUG count in To Do | 1 week |

   ---

   ## Rules
   - **Idempotent**: Running twice with no code changes produces identical TODO.md
   - **Additive only**: Never removes unchecked items still present in codebase
   - **State-driven**: Item column changes only via explicit TODO.md edits (not auto-detected from code)
   - **Source locations**: Includes file:line for every item (e.g., `marcel/scheduler.py:42`)
   - **Self-contained items**: Each `- [ ]` entry must represent a standalone unit of work
   - **PRD-aware**: Annotates groups with `> PRD exists: ` if corresponding PRD file found
   - **Always timestamp**: Updates `Last updated` on every run
   - **WIP advisory**: Flags limit exceedances but does not block execution

   ## Example Usage
   1. Install the skill in your project:
      ```
      npx skills add https://github.com/progfrance/progfranceKanban --skill kanban-todo-git
      ```

   2. Run it to initialize/scan:
      ```
      npx skills run kanban-todo-git
      ```
      Output shows the TODO.md content and metrics. Review, then:
      ```
      git add TODO.md
      git commit -m "chore(todo): update Kanban board (WIP: 2/2, 1 completed)"
      ```

   3. For continuous monitoring, set up a cron job:
         ```
         hermes cronjob create --name "marcel-kanban-update" --skill kanban-todo-git --schedule "every 4h" --deliver origin
         ```

   ## Expected Output
   After running, you should see:
   - Updated TODO.md in project root with Kanban columns
   - Metrics section showing lead/cycle time/throughput/WIP
   - Bottleneck analysis if WIP limits exceeded
   - Improvement experiments section for process tweaks
   - Git diff showing only TODO.md changes (no code modifications)

   ## Verification Steps
   To confirm the skill worked correctly:
   1. Check that TODO.md contains all four columns with correct headers
   2. Verify new BUG/TODO/IMPROVEMENT markers from code appear in To Do column
   3. Confirm resolved markers (no longer in code) appear in Done column with `[x]`
   4. Ensure file:line references point to actual locations in your project
   5. Validate that metrics change logically after completing work (e.g., cycle time decreases after fixing a bottleneck)

   ## Pitfalls and Troubleshooting
   - **Markers not detected**: Ensure markers are exactly `BUG:`, `TODO:`, or `IMPROVEMENT:` (case-sensitive, no variations like `bug:` or `TODO - `)
   - **Wrong file paths**: If using Windows, paths in TODO.md will show backslashes; skill normalizes to forward slashes for consistency but Git history tracking remains accurate
   - **Metrics not calculating**: Requires Git history of TODO.md; first run will show N/A for lead/cycle time until items transition columns
   - **WIP limits feel too strict**: Adjust limits in the skill header comment (To Do:3, In Progress:2, Review:1) if your workflow differs
   - **False resolved items**: If you temporarily comment out a TODO marker, skill may mark it as done; avoid commenting markers, use proper resolution instead

   ## Customization
   To adapt this skill for your specific Marcel JeuxConcours workflow:
   1. **Change WIP limits**: Edit the numbers in Step 4 description and column headers
   2. **Add columns**: Insert new sections (e.g., "Testing", "Deployed") and update metric calculations
   3. **Modify markers**: Change the grep patterns in Step 1 to include `FIXME:` or `HACK:` if needed
   4. **Adjust exclusions**: Add project-specific paths to exclude list (e.g., `marcel/archive/`)

   The skill is designed to be a living process — tune the WIP limits and experiment duration based on your team's (human + agent) capacity and feedback from retrospectives.