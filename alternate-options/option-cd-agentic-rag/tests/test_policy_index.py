"""Section inventory behavior on the real Leitfaden — no LLM, no network."""

from src import config
from src.policy_index import PolicyIndex, section_chunks


def index():
    return PolicyIndex.from_file(config.LEITFADEN_MD)


def test_all_sections_cover_the_whole_document():
    idx = index()
    assert len(idx.all_sections) > 100  # ~142 headings in the January-2025 Leitfaden
    # Non-overlapping, ordered spans that reconstruct the document after the preamble.
    for a, b in zip(idx.all_sections, idx.all_sections[1:]):
        assert a.end == b.start
    preamble_end = idx.all_sections[0].start
    rebuilt = idx.text[:preamble_end] + "".join(
        idx.text[s.start:s.end] for s in idx.all_sections
    )
    assert rebuilt == idx.text


def test_inventory_drops_only_heading_only_shells():
    idx = index()
    dropped = [s for s in idx.all_sections if s not in idx.sections]
    assert dropped  # the Leitfaden has heading-only ## chapters (e.g. ACCESS TO THE BACHELOR...)
    for s in dropped:
        assert s.level == 2
        assert idx.text_of(s).strip() == f"## {s.title}"


def test_subsections_carry_their_chapter_breadcrumb():
    idx = index()
    s004 = idx._by_id["s004"]
    assert s004.breadcrumb == "ACCESS TO THE BACHELOR STUDY PROGRAM"
    assert s004.full_title.startswith("ACCESS TO THE BACHELOR STUDY PROGRAM › ")
    # Childless ## chapters stay in the inventory as breadcrumb-less sections.
    titles = {s.title for s in idx.sections if s.level == 2}
    assert "BACHELOR ENTRANCE EXAMINATION (BACHELOR ZUGANGSPRÜFUNG)" in titles


def test_fetch_resolves_known_ids_and_isolates_unknown_ones():
    idx = index()
    first = idx.sections[0].section_id
    found, missing = idx.fetch([first, "s999", "not-an-id"])
    assert [s.section_id for s in found] == [first]
    assert missing == ["s999", "not-an-id"]


def test_toc_lists_every_section_id_with_breadcrumbed_title():
    idx = index()
    toc = idx.toc()
    for s in idx.sections:
        assert s.section_id in toc
    assert "ACCESS TO THE BACHELOR STUDY PROGRAM › Studying with" in toc


def test_render_tags_sections_with_id_and_breadcrumb():
    idx = index()
    section = idx._by_id["s004"]
    rendered = idx.render([section])
    assert rendered.startswith(f"[{section.section_id}] {section.full_title}\n")
    assert "Admission requirement" in rendered


def test_section_chunks_split_at_level_4_and_resolve_to_parent():
    idx = index()
    chunks = section_chunks(idx, idx._by_id["s004"])
    assert len(chunks) > 4  # preamble + one chunk per #### route
    assert all(cid.split("#")[0] == "s004" for cid, _, _ in chunks)
    headings = [h for _, h, _ in chunks]
    assert any("Abitur (German school-leaving qualification)" in h for h in headings)
    # ##### variants stay inside their parent #### chunk, not as chunks of their own.
    abitur_text = next(t for _, h, t in chunks if "1. Abitur" in h)
    assert "Allgemeine Hochschulreife" in abitur_text
    assert not any("Allgemeine Hochschulreife" in h for h in headings)
    # Chunk texts reassemble the section (whitespace aside).
    assert sum(len(t) for _, _, t in chunks) > 0.9 * len(idx.text_of(idx._by_id["s004"]))


def test_section_without_subheadings_is_a_single_chunk():
    idx = index()
    s013 = idx._by_id["s013"]
    chunks = section_chunks(idx, s013)
    assert chunks == [(s013.section_id, s013.full_title, idx.text_of(s013))]
