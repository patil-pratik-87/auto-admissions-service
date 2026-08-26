"""Evaluation math: modal verdict, flip detection, accuracy."""

from src.evaluate import accuracy, flipped, modal, normalize_title


def test_modal_picks_majority():
    assert modal(["ELIGIBLE", "INELIGIBLE", "ELIGIBLE"]) == "ELIGIBLE"


def test_modal_tie_breaks_deterministically():
    assert modal(["B", "A"]) == modal(["A", "B"]) == "A"


def test_modal_of_no_runs_is_none():
    assert modal([]) is None


def test_flipped_detects_disagreement_across_repeats():
    assert flipped(["ELIGIBLE", "MANUAL_REVIEW", "ELIGIBLE"]) is True
    assert flipped(["ELIGIBLE", "ELIGIBLE", "ELIGIBLE"]) is False
    assert flipped(["ELIGIBLE"]) is None  # a single run cannot flip


def test_accuracy_scores_only_pairs_with_both_sides():
    pairs = [("ELIGIBLE", "ELIGIBLE"), ("INELIGIBLE", "ELIGIBLE"),
             (None, "ELIGIBLE"), ("ELIGIBLE", None)]
    assert accuracy(pairs) == 0.5
    assert accuracy([]) is None
    assert accuracy([(None, "X")]) is None


def test_normalize_title_matches_ground_truth_variants():
    assert normalize_title("BACHELOR ENTRANCE EXAMINATION (BACHELOR ZUGANGSPRÜFUNG)") == \
        normalize_title("Bachelor Entrance Examination (Bachelor Zugangsprüfung)")
