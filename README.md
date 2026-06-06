# ://agent_arena

Build an **autonomous AI agent** that completes everyday-app tasks in
[AppWorld](https://appworld.dev). You are ranked by **Task Goal Completion (TGC)** —
the percentage of tasks your agent fully completes.

## What AppWorld is
A simulated world of **9 apps** (Spotify, Gmail, Venmo, Amazon, Splitwise, Phone,
File System, Simple Note, + `supervisor`/`api_docs`), **457 APIs**, and ~100
simulated people. Your agent reads a natural-language instruction from its
"supervisor" and acts by **writing Python code** that calls the apps' APIs.

## 1. Setup (~3 min) — needs Python 3.11
```bash
git clone https://github.com/interface4agi/hack_agent_arena.git
cd hack_agent_arena
bash setup.sh                 # installs uv+py3.11, appworld + data, creates .env; verifies
source .venv/bin/activate
```
Then add your LLM key to **`.env`**:
```
ANTHROPIC_API_KEY=sk-...
```
> **No key? You can run a local model.** AppWorld itself needs no API key — you can
> explore tasks (`appworld play`) and hand-solve them fully offline. Only the agent's
> "brain" needs a model. The starter uses Anthropic by default, but `call_llm` in
> `agent.py` is swappable: point it at any provider, including a local model via
> [Ollama](https://ollama.com) (its OpenAI-compatible endpoint, or `litellm`). Small
> local models score well below frontier models on AppWorld, but they're great for
> building and debugging your agent loop for free.

## 2. Smoke-test the starter agent (2 tasks)
```bash
export APPWORLD_EXPERIMENT=team_<yourname>     # your UNIQUE team id
export APPWORLD_DATASET=dev MAX_TASKS=2
python agent.py
```
`agent.py` is a working ReAct code agent — read it, then make it smarter
(planning, error recovery, better prompts, retrieval over `apis.api_docs`, …).

Explore a task world by hand: `appworld play`

## 3. The rules your agent plays by
- One Python code block per turn; whatever you `print()` comes back as the next observation.
- Discover APIs at runtime:
  `apis.api_docs.show_api_descriptions(app_name='spotify')`, then
  `apis.api_docs.show_api_doc(app_name='spotify', api_name='login')`.
- Get credentials: `apis.supervisor.show_account_passwords()`, then log into each app.
- Finish a task: `apis.supervisor.complete_task(answer=<answer or None>)`.

## 4. Submit (at each checkpoint)
1. Run your agent on the **official split** the organizers announce
   (default `test_normal`, 168 tasks):
   ```bash
   export APPWORLD_DATASET=test_normal MAX_TASKS=0
   python agent.py
   ```
2. Self-evaluate:
   ```bash
   appworld evaluate $APPWORLD_EXPERIMENT test_normal
   ```
3. Zip and submit your whole output folder:
   `experiments/outputs/$APPWORLD_EXPERIMENT/`
   It must include `evaluations/test_normal.json` and the `tasks/<id>/dbs/` folders.

## Scoring
- **TGC** (primary) — % of tasks fully completed. **SGC** (scenario goal completion) breaks ties.
- 🐉 **Bonus:** teams that integrate **HydraDB** into their agent's architecture
  earn extra credit (ask organizers for details).
- Reference baseline on `test_normal`: ReAct + GPT-4o ≈ **48.8 TGC**. Beat it.

---
Built for **://agent_arena** · benchmark: [AppWorld](https://github.com/StonyBrookNLP/appworld) (ACL'24 Best Resource Paper)
