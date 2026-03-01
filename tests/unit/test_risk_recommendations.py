"""
Unit tests for risk recommendations service
"""
import pytest
from app.services.risk.recommendations import (
    get_recommendations,
    get_improvement_suggestions,
    RECOMMENDATION_TEMPLATES
)


class TestGetRecommendations:
    """Test get_recommendations function"""

    def test_critical_risk_level_adds_critical_recommendations(self):
        """Test that critical risk level adds critical recommendations"""
        scores = {"entropy": 0.5, "correlation": 0.5, "temporal": 0.5, "uniqueness": 0.5}
        recommendations = get_recommendations(scores, "critical")

        assert len(recommendations) >= 3
        # Should include critical recommendations
        critical_found = any(
            "privacy-focused RPC providers" in rec
            for rec in recommendations
        )
        assert critical_found

    def test_low_entropy_adds_entropy_recommendations(self):
        """Test that low entropy score adds entropy recommendations"""
        scores = {"entropy": 0.2, "correlation": 0.5, "temporal": 0.5, "uniqueness": 0.5}
        recommendations = get_recommendations(scores, "medium")

        assert any(
            "Increase request method diversity" in rec
            for rec in recommendations
        )

    def test_high_correlation_adds_correlation_recommendations(self):
        """Test that high correlation adds correlation recommendations"""
        scores = {"entropy": 0.5, "correlation": 0.8, "temporal": 0.5, "uniqueness": 0.5}
        recommendations = get_recommendations(scores, "high")

        assert any(
            "address rotation" in rec or "separate addresses" in rec
            for rec in recommendations
        )

    def test_high_temporal_adds_temporal_recommendations(self):
        """Test that high temporal score adds temporal recommendations"""
        scores = {"entropy": 0.5, "correlation": 0.5, "temporal": 0.8, "uniqueness": 0.5}
        recommendations = get_recommendations(scores, "high")

        assert any(
            "timing jitter" in rec or "random delays" in rec
            for rec in recommendations
        )

    def test_high_uniqueness_adds_uniqueness_recommendations(self):
        """Test that high uniqueness adds uniqueness recommendations"""
        scores = {"entropy": 0.5, "correlation": 0.5, "temporal": 0.5, "uniqueness": 0.8}
        recommendations = get_recommendations(scores, "high")

        assert any(
            "blend in" in rec or "typical users" in rec
            for rec in recommendations
        )

    def test_all_good_scores_returns_minimum_recommendations(self):
        """Test that good scores return minimum 3 default recommendations"""
        scores = {"entropy": 0.8, "correlation": 0.2, "temporal": 0.2, "uniqueness": 0.3}
        recommendations = get_recommendations(scores, "low")

        assert len(recommendations) == 3
        assert all(
            "Review privacy settings" in rec or "best practices" in rec
            for rec in recommendations
        )

    def test_recommendations_limited_to_five(self):
        """Test that recommendations are limited to maximum 5"""
        scores = {"entropy": 0.1, "correlation": 0.9, "temporal": 0.9, "uniqueness": 0.9}
        recommendations = get_recommendations(scores, "critical")

        assert len(recommendations) <= 5

    def test_empty_scores_uses_defaults(self):
        """Test that empty scores dict uses default values"""
        scores = {}
        recommendations = get_recommendations(scores, "low")

        assert len(recommendations) >= 3

    def test_multiple_issues_combined_recommendations(self):
        """Test that multiple low scores combine recommendations"""
        scores = {"entropy": 0.2, "correlation": 0.8, "temporal": 0.8, "uniqueness": 0.2}
        recommendations = get_recommendations(scores, "high")

        # Should have recommendations for multiple issues
        assert len(recommendations) >= 3
        has_entropy = any("method diversity" in rec for rec in recommendations)
        has_correlation = any("address" in rec for rec in recommendations)
        has_temporal = any("timing" in rec or "delay" in rec for rec in recommendations)

        assert has_entropy or has_correlation or has_temporal


class TestGetImprovementSuggestions:
    """Test get_improvement_suggestions function"""

    def test_low_entropy_returns_entropy_suggestion(self):
        """Test that low entropy returns entropy improvement suggestion"""
        scores = {"entropy": 0.2, "correlation": 0.5, "temporal": 0.5, "uniqueness": 0.5}
        suggestions = get_improvement_suggestions(50, scores)

        assert "entropy" in suggestions
        assert "method diversity" in suggestions["entropy"].lower()

    def test_high_uniqueness_returns_uniqueness_suggestion(self):
        """Test that high uniqueness returns uniqueness improvement suggestion"""
        scores = {"entropy": 0.5, "correlation": 0.5, "temporal": 0.5, "uniqueness": 0.8}
        suggestions = get_improvement_suggestions(50, scores)

        assert "uniqueness" in suggestions
        assert "typical user" in suggestions["uniqueness"].lower()

    def test_high_correlation_returns_correlation_suggestion(self):
        """Test that high correlation returns correlation improvement suggestion"""
        scores = {"entropy": 0.5, "correlation": 0.8, "temporal": 0.5, "uniqueness": 0.5}
        suggestions = get_improvement_suggestions(50, scores)

        assert "correlation" in suggestions
        assert "separate addresses" in suggestions["correlation"].lower()

    def test_high_temporal_returns_temporal_suggestion(self):
        """Test that high temporal score returns temporal improvement suggestion"""
        scores = {"entropy": 0.5, "correlation": 0.5, "temporal": 0.8, "uniqueness": 0.5}
        suggestions = get_improvement_suggestions(50, scores)

        assert "temporal" in suggestions
        assert "timing jitter" in suggestions["temporal"].lower()

    def test_all_good_scores_returns_empty_dict(self):
        """Test that good scores return empty suggestions dict"""
        scores = {"entropy": 0.8, "correlation": 0.2, "temporal": 0.2, "uniqueness": 0.3}
        suggestions = get_improvement_suggestions(20, scores)

        assert len(suggestions) == 0

    def test_empty_scores_returns_entropy_suggestion(self):
        """Test that empty scores dict defaults to 0, triggering entropy suggestion"""
        scores = {}
        suggestions = get_improvement_suggestions(50, scores)

        # Empty dict means get returns default 0, which is < 0.3
        assert "entropy" in suggestions
        # assert "method diversity" in suggestions["entropy"].lower()
        """Test that multiple low scores return multiple suggestions"""
        scores = {"entropy": 0.2, "correlation": 0.8, "temporal": 0.2, "uniqueness": 0.5}
        suggestions = get_improvement_suggestions(50, scores)

        assert len(suggestions) >= 2
        assert "entropy" in suggestions
        assert "correlation" in suggestions


class TestRecommendationTemplates:
    """Test RECOMMENDATION_TEMPLATES structure"""

    def test_all_template_keys_exist(self):
        """Test that all expected template keys exist"""
        expected_keys = ["low_entropy", "high_correlation", "high_temporal", "high_uniqueness", "critical_risk"]

        for key in expected_keys:
            assert key in RECOMMENDATION_TEMPLATES
            assert isinstance(RECOMMENDATION_TEMPLATES[key], list)
            assert len(RECOMMENDATION_TEMPLATES[key]) > 0
            assert all(isinstance(rec, str) for rec in RECOMMENDATION_TEMPLATES[key])

    def test_templates_are_not_empty_strings(self):
        """Test that all template strings are non-empty"""
        for key, templates in RECOMMENDATION_TEMPLATES.items():
            for template in templates:
                assert len(template.strip()) > 0
