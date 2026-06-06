# Changes to `agent.py`

Upgraded the AppWorld starter from a minimal ReAct loop to a planning + error-recovery
agent (Stages 1 + 2). The `main()` loop and the AppWorld run/output protocol were
intentionally left untouched so `appworld evaluate` keeps working.

## Config & env knobs
| | Before | After |
|---|---|---|
| `MODEL` default | `claude-opus-4-8` | `claude-sonnet-4-6` |
| `MAX_INTERACTIONS` | `30` | `40` |
| `max_tokens` | hardcoded `1500` | `MAX_TOKENS` env, default `4096` |
| temperature | unused (commented) | `TEMPERATURE` env, default `0.0` |

New knobs: `MAX_OBS_CHARS` (4000), `MAX_RETRIES` (3), `ENABLE_PLANNING` (true),
`VERBOSE` (false), plus a `_flag()` helper for boolean env vars.

## `SYSTEM_PROMPT` (biggest change)
Expanded from ~22 generic lines to a full operating manual:
- **Output protocol** — exactly one python block per turn; only `print()` is observed.
- **Stateful REPL** — log in once, reuse `access_token`/variables/helpers across turns.
- **Discover, never guess** — read `show_api_doc` before first use of any API.
- **Credentials + "my" = supervisor** — query the supervisor app for personal data.
- **Pagination** — don't assume page 1 is complete; loop pages.
- **Time** — the task datetime is "now", not the real clock.
- **Finishing/answer format** — concise entity/number/yes-no; `None` for action tasks.
- A generic **few-shot trace**: discover → login → paginate → recover-from-traceback →
  act → complete.

## `call_llm`
Now takes keyword args `system`, `max_tokens`, `temperature` (was fully hardcoded).
Uses the raised `MAX_TOKENS` and passes `TEMPERATURE`.

## `extract_code`
- **Before:** grabbed the first ```` ```python ```` block; on no match returned the whole
  reply — so prose got executed as code.
- **After:** collects **all** code blocks and concatenates them; returns **`None`** when
  there's no block, so the loop sends a corrective nudge instead of executing prose.

## New helpers
- `truncate_output()` — keeps head+tail of long observations (`MAX_OBS_CHARS`).
- `is_error()` — detects the `"Execution failed"` string prefix (`world.execute` returns
  errors as strings, it does not raise).
- `AgentState` dataclass — tracks `messages`, `plan`, `consecutive_errors`,
  `steps_since_success`, `no_code_count`, `last_codes`, `step`, `completed`.
- `make_plan()` — one planning LLM call before the loop (gated by `ENABLE_PLANNING`);
  returns a short sub-goal checklist; best-effort (never blocks solving).

## `solve()` (rewritten)
- **Before:** a flat 30-step loop: `call_llm → extract_code → execute → append → check`.
- **After:**
  - optional **planning phase**; the initial message includes `world.task.datetime` + plan;
  - **no-code-block handling** (nudge; abort after 3 in a row);
  - **duplicate-code detection** (warns when identical code is resubmitted);
  - **output truncation** before appending observations;
  - **error recovery** — on failure, append the traceback + targeted guidance, escalating
    to a "step back / re-read the doc" nudge at `MAX_RETRIES`; reset on success;
  - **stuck-loop guard** — abort after `2*MAX_RETRIES` steps with no successful execution;
  - `VERBOSE` per-step logging.

## `main()`
**Unchanged** — the original sequential `for task_id in task_ids:` loop, one task at a time inside
`with AppWorld(...)`, with the per-task `try/except` preserved.

> An in-process `MAX_WORKERS` parallel pool was prototyped and then **reverted**: AppWorld freezes "now"
> globally (freezegun, a process-level `ClassVar`) and a reused worker process leaks that state into the
> next task, silently corrupting date-sensitive tasks. Real parallelism belongs in **isolated shards/
> containers** (each running tasks sequentially) — tracked as a future design in the plan file, not built.

## Docstring / anti-cheat
Header rewritten to document the stateful REPL and a **hard anti-cheat rule**: never read
`data/tasks/<id>/ground_truth/`, never call `world.evaluate()` or
`load_task_ids(difficulty=...)` at solve time — only `world.task.instruction/supervisor/datetime`.

## HydraDB integration (`hydra.py` + `agent.py`)
Optional cross-task persistence/context layer (targets the README 🐉 bonus), **single-worker**,
behind `ENABLE_HYDRA` (auto-on when `HYDRADB_API_KEY` is set in `.env`). Fully **fail-safe** —
any HydraDB error degrades to the normal agent.
- **New `hydra.py`** — `httpx` client (no new dependency): `ensure_tenant()`, `ingest_memory()`,
  `query_memory()`. Never raises; never logs the API key. HydraDB indexes asynchronously, so
  retrieved memory is advisory (cross-task, not instant within a turn).
- **`agent.py`**: `main()` calls `ensure_tenant()` once; `solve()` retrieves per-supervisor memory
  at task start and injects a **"MEMORY CONTEXT — credentials/session FIRST"** block at the top of
  the prompt; `_capture()` logs API calls→results and harvests account passwords + access tokens
  from observations; at task end two records upsert per supervisor (`<sub>:creds` =
  credentials/session first; `<sub>:task:<id>` = episodic instruction/outcome/api-log).
- **Scope**: tenant `appworld_agent`, `sub_tenant_id` = supervisor email (per-person memory). The
  `solve()` loop was refactored from early `return`s to `break` + `outcome` + a `for/else`, so the
  end-of-task ingest always runs.
- **SYSTEM_PROMPT**: a MEMORY CONTEXT note — the block is advisory; always re-verify credentials via
  `show_account_passwords()`.
- **Security**: `HYDRADB_API_KEY` lives only in gitignored `.env`. Stores AppWorld's **simulated**
  account credentials/tokens per request — do NOT point this at real secrets.

> ⚠️ This automated harness HARD-BLOCKS the credential-egress pathway, so the HydraDB **ON** path is
> runnable only on your own machine (where you control permissions). With Hydra **OFF** the agent is
> unchanged (verified end-to-end). Anti-cheat is unaffected — only the agent's own observations are
> stored, never ground truth.

## LLM provider — OpenRouter (Llama 3.1 8B) + Anthropic
`call_llm` is now provider-aware. Default `MODEL` is `meta-llama/llama-3.1-8b-instruct` served via
**OpenRouter** (OpenAI-compatible `POST /chat/completions` over `httpx`, no new dependency); the system
prompt is sent as a `system` message and the reply is read from `choices[0].message.content`. Set
`MODEL=claude-*` (or `LLM_PROVIDER=anthropic`) to use the Anthropic SDK path instead. Both clients are
constructed **lazily**, so the agent runs with only the key it needs (`OPENROUTER_API_KEY` or
`ANTHROPIC_API_KEY`, in gitignored `.env`). Knobs: `LLM_PROVIDER`, `OPENROUTER_BASE_URL`,
`OPENROUTER_TIMEOUT`. Note: an 8B model scores well below frontier models on AppWorld — great for
free/fast plumbing iteration, not for top TGC.

## Deferred (Stage 3, not yet implemented)
Pre-completion verification gate (re-query final state before `complete_task`) and
heuristic difficulty adaptation (scale interactions from the instruction text only).
