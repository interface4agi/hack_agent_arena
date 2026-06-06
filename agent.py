"""
://agent_arena — AppWorld ReAct code agent (planning + error recovery).

This agent completes a supervisor's task by writing Python code that the AppWorld
environment executes. The loop and every AppWorld API call were verified against
appworld==0.1.3.

How AppWorld works (the rules the agent plays by):
  - Each task gives a natural-language instruction from a "supervisor".
  - The agent acts by writing PYTHON code. The env runs it and returns whatever you
    print(). A preloaded object `apis` is the only interface to the 9 apps.
  - The Python REPL is STATEFUL across turns: variables, imports, and helper
    functions persist, including the access_token returned by login.
  - Discover APIs at runtime:
        apis.api_docs.show_app_descriptions()
        apis.api_docs.show_api_descriptions(app_name='spotify')
        apis.api_docs.show_api_doc(app_name='spotify', api_name='login')
  - Get credentials:  apis.supervisor.show_account_passwords()
  - Finish with:      apis.supervisor.complete_task(answer=<answer or None>)

⚠️ ANTI-CHEAT — HARD RULE:
  This agent must NEVER read anything under data/tasks/<id>/ground_truth/
  (answer.json, metadata.json, evaluation.py, solution.py, ...), never call
  world.evaluate(), and never call load_task_ids(difficulty=...) at solve time.
  Those are the answer / evaluation material. The ONLY task inputs allowed are
  world.task.instruction, world.task.supervisor, and world.task.datetime.

Run:
  export ANTHROPIC_API_KEY=sk-...            # or put it in .env
  export APPWORLD_EXPERIMENT=team_<yourname>  # your unique team id
  export MODEL=claude-sonnet-4-6
  export APPWORLD_DATASET=smoke               # dev | smoke | testplan | test_normal
  python agent.py
"""

import os
import re
from dataclasses import dataclass, field

try:  # optional: load ANTHROPIC_API_KEY etc. from a local .env
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

import anthropic
import httpx
from appworld import AppWorld, load_task_ids

try:
    import hydra  # optional HydraDB persistence/context layer (fail-safe; see hydra.py)
except Exception:
    hydra = None

# ---- config (env-driven knobs) -------------------------------------------
MODEL = os.environ.get("MODEL", "meta-llama/llama-3.1-8b-instruct")  # claude-*, or any OpenRouter model
DATASET = os.environ.get("APPWORLD_DATASET", "dev")  # dev|smoke|testplan|test_normal
EXPERIMENT = os.environ.get("APPWORLD_EXPERIMENT", "team_demo")
MAX_INTERACTIONS = int(os.environ.get("MAX_INTERACTIONS", "40"))
MAX_TASKS = int(os.environ.get("MAX_TASKS", "0"))  # 0 = all tasks in split
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "4096"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.0"))
MAX_OBS_CHARS = int(os.environ.get("MAX_OBS_CHARS", "4000"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))

# HydraDB (optional persistence/context). Key lives in .env (gitignored). See hydra.py.
HYDRADB_API_KEY = os.environ.get("HYDRADB_API_KEY", "")
HYDRA_MAX_CONTEXT = int(os.environ.get("HYDRA_MAX_CONTEXT", "6"))

# LLM provider: "anthropic" for claude-* models, else OpenRouter (OpenAI-compatible).
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_TIMEOUT = float(os.environ.get("OPENROUTER_TIMEOUT", "120"))
LLM_PROVIDER = os.environ.get(
    "LLM_PROVIDER", "anthropic" if MODEL.lower().startswith("claude") else "openrouter"
)


def _flag(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


ENABLE_PLANNING = _flag("ENABLE_PLANNING", True)
ENABLE_HYDRA = _flag("ENABLE_HYDRA", bool(HYDRADB_API_KEY)) and hydra is not None
VERBOSE = _flag("VERBOSE", False)

_anthropic_client = None
_openrouter_client = None


def _anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    return _anthropic_client


def _openrouter():
    global _openrouter_client
    if _openrouter_client is None:
        if not OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY is not set (put it in .env)")
        _openrouter_client = httpx.Client(
            base_url=OPENROUTER_BASE_URL,
            timeout=OPENROUTER_TIMEOUT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/interface4agi/hack_agent_arena",
                "X-Title": "agent_arena",
            },
        )
    return _openrouter_client

SYSTEM_PROMPT = r"""You are an autonomous coding agent operating inside AppWorld.
You complete the supervisor's task by writing Python code that the environment runs.

OUTPUT PROTOCOL
- Reply with EXACTLY ONE Python code block per turn and nothing else:
  ```python
  # your code
  ```
- Only what you print() comes back as the next observation. To see anything, print it.
- The preloaded object `apis` is the ONLY way to interact with the apps.

STATEFUL REPL — this matters a lot
- Your code runs in ONE persistent Python session. Variables, imports, and functions
  you define PERSIST across turns. Reuse them. In particular, log in ONCE and reuse the
  returned access_token; never re-login or recompute data you already have.

DISCOVER, NEVER GUESS
- You do NOT know the APIs in advance. Before the FIRST use of any API, read its doc:
    print(apis.api_docs.show_app_descriptions())
    print(apis.api_docs.show_api_descriptions(app_name='<app>'))
    print(apis.api_docs.show_api_doc(app_name='<app>', api_name='<api>'))
- Never invent API names, parameter names, or response fields. Look them up.

CREDENTIALS
- Get passwords, then call each app's login to get an access_token:
    print(apis.supervisor.show_account_passwords())
- "my"/"me"/"I" refer to the SUPERVISOR. Their profile, contacts, payment cards,
  addresses, etc. are queryable via the `supervisor` app — look there for personal data.

PAGINATION & COMPLETENESS (a common cause of failure)
- List endpoints are usually paginated/filtered (page_index, page_limit, and filters).
  Do NOT assume the first page is everything. Loop pages until exhausted, or pass a
  large page_limit, when you need the full set.

TIME
- "today"/"now" means the task's datetime given below, NOT the real-world clock.

MEMORY CONTEXT
- A "MEMORY CONTEXT (HydraDB)" block may appear at the very top of the task with known
  credentials/session and lessons from earlier tasks. Use it to act faster, but treat it
  as ADVISORY — always re-verify credentials via show_account_passwords() (it can be stale).

WORK STYLE
- Inspect results before the next action. Take small steps; print and read each result.
- On an error, read the traceback, diagnose the real cause (wrong API/param? missing
  field? need to read the doc? unhandled pagination?), and fix it. Don't repeat the same
  failing call unchanged.

FINISHING
- When AND ONLY WHEN the task is fully done, call:
    apis.supervisor.complete_task(answer=<answer>)
- Pass `answer` only when the task asks a question; otherwise answer=None.
- An answer must be CONCISE — a number, a yes/no, or a specific entity — NOT a sentence.

------------------------------------------------------------------------------
EXAMPLE (generic — shows the PATTERN, not the actual apps you'll use):

Turn — discover, then read the doc before using it:
```python
print(apis.api_docs.show_api_descriptions(app_name='phone'))
```
Observation: [... lists 'login', 'search_contacts', 'send_text_message', ...]

Turn — log in once, store the token:
```python
creds = apis.supervisor.show_account_passwords()
pw = next(c for c in creds if c['account_name'] == 'phone')['password']
phone_no = apis.supervisor.show_profile()['phone_number']
token = apis.phone.login(username=phone_no, password=pw)['access_token']
print('logged in')
```
Observation: logged in

Turn — query (paginate), reusing the token from the previous turn:
```python
contacts, page = [], 0
while True:
    batch = apis.phone.search_contacts(access_token=token, page_index=page, page_limit=50)
    if not batch:
        break
    contacts += batch
    page += 1
print(len(contacts), contacts[:2])
```
Observation: 37 [{'first_name': 'Ada', ...}, ...]

Turn — recover from an error (read the doc, fix the call):
```python
print(apis.api_docs.show_api_doc(app_name='phone', api_name='send_text_message'))
```
Observation: [... shows required params: access_token, phone_number, message ...]

Turn — act, then finish (answer=None because this was an action, not a question):
```python
apis.phone.send_text_message(access_token=token, phone_number=contacts[0]['phone_number'], message='Hi')
apis.supervisor.complete_task(answer=None)
```
------------------------------------------------------------------------------
"""

PLANNING_PROMPT = """Before writing any code, think through this task.

In a SHORT numbered checklist (no code yet), outline how you'll solve it:
1) which app(s) and what data are involved,
2) which account(s) you must log into,
3) the ordered sub-goals (queries first, then any actions/mutations),
4) what the final answer should be (a concise entity/number/yes-no) or None if it's an
   action task.

Keep it under ~8 lines. This is your plan; you'll execute it step by step next."""


@dataclass
class AgentState:
    messages: list[dict] = field(default_factory=list)
    plan: str | None = None
    consecutive_errors: int = 0
    steps_since_success: int = 0
    no_code_count: int = 0
    last_codes: list[str] = field(default_factory=list)
    step: int = 0
    completed: bool = False


# ---- LLM ------------------------------------------------------------------
def call_llm(
    messages: list[dict],
    *,
    system: str = SYSTEM_PROMPT,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
) -> str:
    if LLM_PROVIDER == "anthropic":
        resp = _anthropic().messages.create(
            model=MODEL,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return "".join(b.text for b in resp.content if b.type == "text")
    # OpenRouter / OpenAI-compatible: the system prompt is a message, not a separate field.
    resp = _openrouter().post(
        "/chat/completions",
        json={
            "model": MODEL,
            "messages": [{"role": "system", "content": system}, *messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )
    resp.raise_for_status()
    choices = resp.json().get("choices") or [{}]
    return (choices[0].get("message") or {}).get("content") or ""


# ---- code / output handling ----------------------------------------------
_CODE_BLOCK = re.compile(r"```(?:python)?\s*\n(.*?)```", re.S)


def extract_code(text: str) -> str | None:
    """Return runnable code from the reply, or None if there's no code block.

    Concatenates multiple blocks in order (models sometimes split setup + action).
    Returns None rather than executing prose, so the loop can send a corrective nudge.
    """
    blocks = [m.group(1).strip() for m in _CODE_BLOCK.finditer(text)]
    blocks = [b for b in blocks if b]
    if blocks:
        return "\n\n".join(blocks)
    return None


def truncate_output(text: str, limit: int = MAX_OBS_CHARS) -> str:
    """Keep head+tail of a long observation so context doesn't blow up."""
    if len(text) <= limit:
        return text
    head = limit * 2 // 3
    tail = limit - head
    omitted = len(text) - head - tail
    return f"{text[:head]}\n...[{omitted} chars omitted]...\n{text[-tail:]}"


def is_error(output: str) -> bool:
    """AppWorld returns failures as a string prefixed 'Execution failed.'."""
    return output.startswith("Execution failed")


# ---- phases ---------------------------------------------------------------
def make_plan(world: AppWorld) -> str | None:
    """One planning LLM call (no code execution). Returns a short checklist or None."""
    try:
        plan = call_llm(
            [
                {
                    "role": "user",
                    "content": (
                        f"Supervisor: {world.task.supervisor}\n"
                        f"Current datetime: {world.task.datetime}\n\n"
                        f"Task: {world.task.instruction}\n\n"
                        f"{PLANNING_PROMPT}"
                    ),
                }
            ],
            max_tokens=600,
        )
        return plan.strip() or None
    except Exception as e:  # planning is best-effort; never block solving
        if VERBOSE:
            print(f"    (planning skipped: {e})")
        return None


def supervisor_key(world: AppWorld) -> str:
    """Stable per-supervisor id for HydraDB sub_tenant scoping (derived from the email)."""
    sup = world.task.supervisor
    email = (getattr(sup, "email", "") or "").strip()
    if not email:
        email = f"{getattr(sup, 'first_name', '')}_{getattr(sup, 'last_name', '')}"
    return re.sub(r"[^A-Za-z0-9_]", "_", email) or "unknown"


_API_CALL_RE = re.compile(r"apis\.([a-z_]+)\.([a-z_]+)\s*\(")
_ACCT_RE = re.compile(r'"account_name"\s*:\s*"([^"]+)"\s*,\s*"password"\s*:\s*"([^"]*)"')
_TOKEN_RE = re.compile(r'"access_token"\s*:\s*"([^"]+)"')


def _capture(code: str, output: str, api_log: list[str], captured: dict) -> None:
    """Best-effort: log API calls→results and capture creds/tokens from observations.

    NOTE: AppWorld accounts are SIMULATED benchmark data. This persists them to the user's
    own HydraDB tenant per the requested design — do NOT point this at real secrets.
    """
    snippet = " ".join(output.split())[:120]
    for app, api in _API_CALL_RE.findall(code):
        captured["apps"].add(app)
        api_log.append(f"{app}.{api} -> {snippet}")
    for acct, pw in _ACCT_RE.findall(output):
        captured["accounts"][acct] = pw
    for tok in _TOKEN_RE.findall(output):
        captured["tokens"].add(tok)


def _ingest_task_memory(
    sub: str, world: AppWorld, outcome: str, api_log: list[str], captured: dict
) -> None:
    """Persist a credentials/session record (creds FIRST) + an episodic task record."""
    if hydra is None:
        return
    accts = captured["accounts"]
    creds = (
        "CREDENTIALS/SESSION (AppWorld simulated accounts) — verify via show_account_passwords:\n"
        + ("\n".join(f"{a}: password={p}" for a, p in accts.items()) or "(none captured)")
        + ("\napps_logged_in: " + ", ".join(sorted(captured["apps"])) if captured["apps"] else "")
        + ("\naccess_tokens: " + " | ".join(list(captured["tokens"])[:9]) if captured["tokens"] else "")
        + "\nLogin recipe: username = supervisor email (phone app uses phone_number); "
        "password = show_account_passwords[account_name == app]; never invent credentials."
    )
    hydra.ingest_memory(sub, creds, f"{sub}:creds")
    episodic = (
        f"TASK {world.task.id} [{outcome}]: {world.task.instruction}\n"
        f"apps: {', '.join(sorted(captured['apps'])) or '-'}\n"
        "api calls/responses:\n" + "\n".join(f"- {x}" for x in api_log[:40])
    )
    hydra.ingest_memory(sub, episodic, f"{sub}:task:{world.task.id}")


def solve(world: AppWorld) -> None:
    state = AgentState()
    sub = supervisor_key(world) if ENABLE_HYDRA else None

    # Retrieve prior context (credentials/session + lessons) BEFORE acting.
    memory_chunks = (
        hydra.query_memory(
            sub,
            "account credentials, passwords, access tokens and login/session details; "
            f"plus prior steps relevant to: {world.task.instruction}",
            HYDRA_MAX_CONTEXT,
        )
        if ENABLE_HYDRA
        else []
    )

    if ENABLE_PLANNING:
        state.plan = make_plan(world)

    initial = (
        f"Supervisor: {world.task.supervisor}\n"
        f"Current datetime: {world.task.datetime}\n\n"
        f"Task: {world.task.instruction}\n\n"
    )
    if memory_chunks:
        initial = (
            "MEMORY CONTEXT (HydraDB) — KNOWN CREDENTIALS/SESSION FIRST "
            "(advisory; always re-verify with show_account_passwords):\n"
            + "\n".join(f"- {c}" for c in memory_chunks)
            + "\n\n"
            + initial
        )
    if state.plan:
        initial += f"Your plan:\n{state.plan}\n\nExecute it step by step. "
    initial += "Begin. Remember: exactly one python code block per turn."
    state.messages.append({"role": "user", "content": initial})

    api_log: list[str] = []
    captured = {"accounts": {}, "tokens": set(), "apps": set()}
    outcome = "max_interactions"

    for state.step in range(1, MAX_INTERACTIONS + 1):
        reply = call_llm(state.messages)
        state.messages.append({"role": "assistant", "content": reply})
        code = extract_code(reply)

        # No code block: nudge instead of executing prose.
        if code is None:
            state.no_code_count += 1
            if state.no_code_count >= 3:
                print("  ✗ no code block 3x — aborting task")
                outcome = "no_code"
                break
            state.messages.append(
                {
                    "role": "user",
                    "content": "I didn't find a python code block. Reply with EXACTLY "
                    "one ```python ...``` block and nothing else.",
                }
            )
            continue
        state.no_code_count = 0

        repeated = bool(state.last_codes) and code == state.last_codes[-1]
        state.last_codes.append(code)

        output = world.execute(code)
        obs = truncate_output(str(output))
        if ENABLE_HYDRA:
            _capture(code, str(output), api_log, captured)
        if VERBOSE:
            print(f"  step {state.step}: ran {len(code)} chars -> {obs[:120]!r}")

        if world.task_completed():
            print(f"  ✓ task_completed (step {state.step})")
            state.completed = True
            outcome = "completed"
            break

        # Build the next observation turn, with recovery guidance on failure.
        user_turn = f"Execution output:\n{obs}"
        if is_error(output):
            state.consecutive_errors += 1
            state.steps_since_success += 1
            user_turn += (
                "\n\n[The code above FAILED. Diagnose the root cause (wrong API/param "
                "name? missing field? need to read show_api_doc? unhandled pagination?) "
                "and fix it. Do NOT repeat the same call unchanged.]"
            )
            if state.consecutive_errors >= MAX_RETRIES:
                user_turn += (
                    f"\n[You've failed {state.consecutive_errors} times in a row. Step "
                    "back: re-read the relevant api_doc from scratch and try a clearly "
                    "different approach.]"
                )
        else:
            state.consecutive_errors = 0
            state.steps_since_success = 0
        if repeated:
            user_turn += (
                "\n[You submitted code identical to the previous turn — it won't behave "
                "differently. Change your approach.]"
            )
        state.messages.append({"role": "user", "content": user_turn})

        # Stuck guard: too many turns with no successful execution.
        if state.steps_since_success >= 2 * MAX_RETRIES:
            print(f"  ✗ stuck: {state.steps_since_success} steps without success — aborting")
            outcome = "stuck"
            break
    else:
        print("  ✗ hit MAX_INTERACTIONS without completion")

    if ENABLE_HYDRA:
        _ingest_task_memory(sub, world, outcome, api_log, captured)


def main() -> None:
    global ENABLE_HYDRA
    task_ids = load_task_ids(DATASET)
    if MAX_TASKS:
        task_ids = task_ids[:MAX_TASKS]
    if ENABLE_HYDRA:
        if hydra.ensure_tenant():
            print(f"HydraDB: tenant '{hydra.TENANT_ID}' ready — persistence/context ON")
        else:
            print("HydraDB: unavailable — continuing without it")
            ENABLE_HYDRA = False
    print(f"Running '{EXPERIMENT}' on {len(task_ids)} '{DATASET}' tasks with {MODEL}")
    for i, task_id in enumerate(task_ids, 1):
        print(f"[{i}/{len(task_ids)}] {task_id}")
        with AppWorld(task_id=task_id, experiment_name=EXPERIMENT) as world:
            try:
                solve(world)
            except Exception as e:  # never let one task kill the whole run
                print(f"  ! error: {e}")
    print(f"\nDone. Outputs in ./experiments/outputs/{EXPERIMENT}/")
    print("Hand that folder to the organizers (or zip and submit per instructions).")


if __name__ == "__main__":
    main()
