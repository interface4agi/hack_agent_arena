"""
hydra.py — thin, fail-safe HydraDB client for the AppWorld agent.

HydraDB (https://docs.hydradb.com) is a context/memory substrate. We use it for
cross-task/run PERSISTENCE:
  - store per-supervisor memories (credentials/session first, then episodic task summaries),
  - retrieve relevant context at task start to inject into the prompt.

Design rules:
  - EVERY function is best-effort: on ANY error (missing key, network, auth, timeout, bad
    JSON) it returns a safe default so HydraDB problems never break task solving.
  - The API key is read from $HYDRADB_API_KEY and is NEVER logged or printed.
  - HydraDB indexes ASYNCHRONOUSLY — freshly ingested memory may not be searchable right
    away. Treat retrieved context as advisory; the agent must still fetch live credentials.

API (verified from docs): base https://api.hydradb.com, headers
`Authorization: Bearer <key>` + `API-Version: 2`.
  POST /tenants                {tenant_id}
  GET  /tenants/status         ?tenant_id=...      -> data.infra.ready_for_ingestion
  POST /context/ingest         {type, tenant_id, sub_tenant_id, memories:"[{id,text,infer}]"}
  POST /query                  {tenant_id, sub_tenant_id, query, type, max_results} -> data.chunks
Responses use an envelope {success, data, error, meta}; we read `data`.
"""

import json
import os
import time

try:
    import httpx
except Exception:  # pragma: no cover - httpx ships with anthropic, but degrade anyway
    httpx = None

API_KEY = os.environ.get("HYDRADB_API_KEY", "")
BASE_URL = os.environ.get("HYDRA_BASE_URL", "https://api.hydradb.com").rstrip("/")
TENANT_ID = os.environ.get("HYDRA_TENANT_ID", "appworld_agent")
TIMEOUT = float(os.environ.get("HYDRA_TIMEOUT", "10"))
VERBOSE = os.environ.get("VERBOSE", "false").strip().lower() in {"1", "true", "yes", "on"}

_client = None
_tenant_ready = False


def available() -> bool:
    """True if we have a key and an HTTP client library — i.e. HydraDB can be used."""
    return bool(API_KEY) and httpx is not None


def _log(msg: str) -> None:
    if VERBOSE:
        print(f"  [hydra] {msg}")  # never includes the API key


def _http():
    global _client
    if not available():
        return None
    if _client is None:
        _client = httpx.Client(
            base_url=BASE_URL,
            timeout=TIMEOUT,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "API-Version": "2",
                "Content-Type": "application/json",
            },
        )
    return _client


def _data(resp) -> dict:
    """Unwrap the {success, data, error, meta} envelope; tolerate plain bodies."""
    try:
        body = resp.json()
    except Exception:
        return {}
    if isinstance(body, dict):
        inner = body.get("data", body)
        return inner if isinstance(inner, dict) else {}
    return {}


def ensure_tenant(max_wait: float = 20.0) -> bool:
    """Create the tenant (idempotent) and wait until it's ready for ingestion.

    Runs the network flow at most once per process (result cached in _tenant_ready).
    Returns False on any failure so the caller can disable HydraDB for the run.
    Call this from main() BEFORE entering any AppWorld context (it may sleep while polling).
    """
    global _tenant_ready
    if _tenant_ready:
        return True
    http = _http()
    if http is None:
        return False
    try:
        try:  # create — tolerate "already exists"
            http.post("/tenants", json={"tenant_id": TENANT_ID})
        except Exception as e:
            _log(f"create-tenant warning: {type(e).__name__}")
        waited = 0.0
        while waited < max_wait:
            try:
                r = http.get("/tenants/status", params={"tenant_id": TENANT_ID})
                if (_data(r).get("infra") or {}).get("ready_for_ingestion"):
                    _tenant_ready = True
                    break
            except Exception as e:
                _log(f"status warning: {type(e).__name__}")
            time.sleep(2)
            waited += 2
    except Exception as e:
        _log(f"ensure_tenant failed: {type(e).__name__}")
    _log(f"tenant ready={_tenant_ready}")
    return _tenant_ready


def ingest_memory(sub_tenant_id: str, text: str, mem_id: str) -> str | None:
    """Store one memory verbatim (infer=False) under (tenant, sub_tenant); upserts by mem_id.

    Returns the ingest id, or None on any failure.
    """
    http = _http()
    if http is None or not sub_tenant_id or not text:
        return None
    try:
        payload = {
            "type": "memory",
            "tenant_id": TENANT_ID,
            "sub_tenant_id": sub_tenant_id,
            "memories": json.dumps([{"id": mem_id, "text": text, "infer": False}]),
        }
        r = http.post("/context/ingest", json=payload)
        results = _data(r).get("results") or []
        rid = results[0].get("id") if results and isinstance(results[0], dict) else None
        _log(f"ingest {mem_id} -> {rid}")
        return rid
    except Exception as e:
        _log(f"ingest failed: {type(e).__name__}")
        return None


def query_memory(sub_tenant_id: str, query: str, max_results: int = 6) -> list[str]:
    """Retrieve memory chunk texts for (tenant, sub_tenant). Returns [] on any failure."""
    http = _http()
    if http is None or not sub_tenant_id or not query:
        return []
    try:
        payload = {
            "tenant_id": TENANT_ID,
            "sub_tenant_id": sub_tenant_id,
            "query": query,
            "type": "memory",
            "max_results": max_results,
        }
        r = http.post("/query", json=payload)
        out: list[str] = []
        for c in _data(r).get("chunks") or []:
            if isinstance(c, dict):
                txt = c.get("chunk_content") or c.get("content") or c.get("text")
                if txt:
                    out.append(str(txt))
        _log(f"query '{query[:40]}…' -> {len(out)} chunks")
        return out
    except Exception as e:
        _log(f"query failed: {type(e).__name__}")
        return []
