import unittest
from datetime import date

from learning_path import (
    INTERESTS,
    build_final_feedback,
    build_final_report,
    build_second_suggestion,
    build_suggestion,
    research_deadline,
)
from progress_store import ProgressStore


class LearningPathTests(unittest.TestCase):
    def test_suggestion_uses_selected_interest(self):
        result = build_suggestion([INTERESTS[5]], ["Libro o dispensa"], [])
        self.assertIn("investigatore", result.title.lower())
        self.assertIn("libro", result.first_step.lower())

    def test_activity_has_priority_for_first_step(self):
        result = build_suggestion(
            [INTERESTS[0]],
            ["Video o animazioni"],
            ["Fare una ricerca in gruppo"],
        )
        self.assertIn("ricerca in gruppo", result.first_step.lower())

    def test_storage_is_namespaced_and_stable(self):
        store = ProgressStore("https://example.supabase.co", "test")
        first = store._storage_code("AMIR-TEST1")
        second = store._storage_code("AMIR-TEST1")
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("B-"))
        self.assertNotEqual(first, "AMIR-TEST1")

    def test_research_deadline(self):
        iso_date, italian_date = research_deadline(7, date(2026, 9, 20))
        self.assertEqual(iso_date, "2026-09-27")
        self.assertEqual(italian_date, "27 settembre 2026")

    def test_research_deadline_rejects_other_values(self):
        with self.assertRaises(ValueError):
            research_deadline(5, date(2026, 9, 20))

    def test_second_suggestion_checks_uncertain_sources(self):
        result = build_second_suggestion(
            [INTERESTS[6]],
            "Non so ancora valutarle",
            "Non avevo ancora un'idea chiara",
            "No, non ancora",
        )
        self.assertIn("controlla", result.title.lower())
        self.assertIn("due fonti", result.mission.lower())

    def test_second_suggestion_challenges_confirmed_idea(self):
        result = build_second_suggestion(
            [INTERESTS[0]],
            "Abbastanza",
            "La mia idea iniziale si è rafforzata",
            "Ho un'idea",
        )
        self.assertIn("eccezione", result.title.lower())

    def test_lower_confidence_is_treated_as_awareness(self):
        result = build_final_feedback(80, 55, "Un calcolo", ["Sicurezza"], "")
        self.assertIn("consapevolezza", result.headline.lower())
        self.assertNotIn("fallimento", result.headline.lower())

    def test_intuition_is_turned_into_testable_hypothesis(self):
        result = build_final_feedback(
            30,
            60,
            "Per ora soprattutto la mia intuizione",
            ["Costo"],
            "",
        )
        self.assertIn("ipotesi", result.next_habit.lower())
        self.assertIn("smentirla", result.next_habit.lower())

    def test_final_report_contains_decision_and_limits(self):
        report = build_final_report(
            "AMIR-TEST1",
            {
                "interests": [INTERESTS[6]],
                "first_mission": "Scegli senza indovinare",
                "final_decision": "Uso un cuscinetto radiale",
                "limitation_area": "Carico incerto",
                "system_impacts": ["Sicurezza", "Manutenzione"],
            },
        )
        self.assertIn("Uso un cuscinetto radiale", report)
        self.assertIn("Carico incerto", report)
        self.assertIn("AMIR-TEST1", report)


if __name__ == "__main__":
    unittest.main()
