"""The section inventory and both retrieval tools.

The inventory is the shared substrate of the experiment: non-overlapping spans
between consecutive `##`/`###` headings of the Leitfaden markdown. Hierarchy is
kept as breadcrumbs: `###` sections carry their parent `##` chapter title;
childless `##` chapters are sections themselves; heading-only `##` shells are
dropped from the inventory and live on only as breadcrumbs. Section IDs still
number ALL headings in document order, so IDs stay stable across this change.
The two arms differ only in how sections are *selected*:

- ARM_TOC  — the agent sees the table of contents and opens sections by ID.
- ARM_RAG  — the agent emits search queries; a Chroma collection over the same
             sections (text-embedding-3-small) returns the top-k per query.
             Sections with `####` sub-headings are embedded as one vector per
             sub-block (multi-vector); hits always resolve to whole sections.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from . import config
from .observability import embed_texts, sha256_text

HEADING_RE = re.compile(r"^(#{2,3}) (.+?)\s*$", re.MULTILINE)
SUBHEADING_RE = re.compile(r"^#### (.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Section:
    section_id: str  # "s001", stable within one policy version (document order)
    level: int       # 2 or 3
    title: str
    start: int       # char offset of the heading line
    end: int         # char offset where the next heading starts (or EOF)
    breadcrumb: str | None = None  # parent ## chapter title, for ### sections

    @property
    def full_title(self) -> str:
        return f"{self.breadcrumb} › {self.title}" if self.breadcrumb else self.title


class PolicyIndex:
    def __init__(self, text: str):
        self.text = text
        self.sha = sha256_text(text)
        matches = list(HEADING_RE.finditer(text))
        self.all_sections: list[Section] = []
        chapter_title = None
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            level = len(m.group(1))
            title = m.group(2)
            if level == 2:
                chapter_title = title
            self.all_sections.append(Section(
                section_id=f"s{i + 1:03d}",
                level=level,
                title=title,
                start=m.start(),
                end=end,
                breadcrumb=chapter_title if level == 3 else None,
            ))
        # Retrieval inventory: drop heading-only ## shells (nothing to retrieve —
        # they survive as their children's breadcrumbs).
        self.sections = [
            s for s in self.all_sections
            if not (s.level == 2 and self.text_of(s).strip() == f"## {s.title}")
        ]
        self._by_id = {s.section_id: s for s in self.all_sections}

    @classmethod
    def from_file(cls, path: Path | None = None) -> "PolicyIndex":
        return cls((path or config.require_leitfaden()).read_text())

    def text_of(self, section: Section) -> str:
        return self.text[section.start:section.end].rstrip()

    def toc(self) -> str:
        """Compact table of contents shown to agents: id + breadcrumbed title."""
        return "\n".join(f"{s.section_id}  {s.full_title}" for s in self.sections)

    def fetch(self, section_ids: list[str]) -> tuple[list[Section], list[str]]:
        """Resolve requested IDs; unknown IDs are returned separately, never fatal
        (the model may hallucinate an ID — that is data, not a crash)."""
        found, missing = [], []
        for sid in section_ids:
            if sid in self._by_id:
                found.append(self._by_id[sid])
            else:
                missing.append(sid)
        return found, missing

    def render(self, sections: list[Section]) -> str:
        """Sections as retrieval-tool output: ID tag + breadcrumbed title + full text."""
        return "\n\n".join(f"[{s.section_id}] {s.full_title}\n{self.text_of(s)}"
                           for s in sections)


def section_chunks(index: PolicyIndex, section: Section) -> list[tuple[str, str, str]]:
    """(chunk_id, heading, text) — one chunk per `####` block, or the whole section.

    ARM_RAG's multi-vector embedding unit: `#####` variants stay inside their parent
    `####` chunk; chunk ids like "s004#2" resolve back to the whole section at query
    time, so the retrieval unit is unchanged — only the ranking gets finer vectors.
    """
    text = index.text_of(section)
    marks = list(SUBHEADING_RE.finditer(text))
    if not marks:
        return [(section.section_id, section.full_title, text)]
    chunks = []
    preamble = text[:marks[0].start()].strip()
    if preamble:
        chunks.append((f"{section.section_id}#0", section.full_title, preamble))
    for j, m in enumerate(marks):
        end = marks[j + 1].start() if j + 1 < len(marks) else len(text)
        chunks.append((f"{section.section_id}#{j + 1}",
                       f"{section.full_title} › {m.group(1)}",
                       text[m.start():end].strip()))
    return chunks


class RagStore:
    """Chroma vector store over the section inventory (ARM_RAG's selection tool).

    Persisted under runs/chroma/; the collection name carries the policy hash and
    the index schema version, so a changed policy or embedding scheme re-embeds
    automatically. Embeddings are computed via the ledgered client (embed once,
    one vector per chunk), never through Chroma's own embedder.
    """

    def __init__(self, index: PolicyIndex):
        import chromadb

        self.index = index
        self.chunks = [c for s in index.sections for c in section_chunks(index, s)]
        config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
        name = f"leitfaden-{index.sha[:12]}-{config.INDEX_SCHEMA}"
        self.collection = client.get_or_create_collection(name, metadata={"hnsw:space": "cosine"})
        if self.collection.count() != len(self.chunks):
            # Recreate from scratch so a partially-built store never collides on IDs.
            client.delete_collection(name)
            self.collection = client.get_or_create_collection(name, metadata={"hnsw:space": "cosine"})
            self._build()

    def _build(self) -> None:
        # The breadcrumbed heading is prepended so every vector carries its place in
        # the hierarchy. The embedded text is truncated to stay under the embedding
        # model's 8192-token input limit (~4 chars/token); retrieval always returns
        # the FULL section text regardless.
        docs = [f"{heading}\n{text}"[:24_000] for _, heading, text in self.chunks]
        embeddings = []
        for i in range(0, len(docs), 64):  # embedding API batch limit headroom
            embeddings += embed_texts(docs[i:i + 64], run_id="rag-store-build")
        self.collection.add(
            ids=[chunk_id for chunk_id, _, _ in self.chunks],
            embeddings=embeddings,
            documents=docs,
            metadatas=[{"section_id": chunk_id.split("#")[0], "title": heading}
                       for chunk_id, heading, _ in self.chunks],
        )

    def query(self, queries: list[str], *, run_id: str, top_k: int = config.TOP_K) -> list[Section]:
        """Top-k chunks per query, resolved to whole sections, deduplicated, document order."""
        queries = [q for q in queries if q.strip()][: config.MAX_QUERIES_PER_TURN]
        if not queries:
            return []
        embeddings = embed_texts(queries, run_id=run_id, node="embed_query")
        result = self.collection.query(query_embeddings=embeddings, n_results=top_k)
        hit_ids = {chunk_id.split("#")[0] for ids in result["ids"] for chunk_id in ids}
        sections, _ = self.index.fetch(sorted(hit_ids))
        return sections
