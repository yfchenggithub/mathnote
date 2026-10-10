"""Exact population model for R028's frozen medical test example."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ScreeningModel:
    prevalence: Fraction = Fraction(1, 1000)
    sensitivity: Fraction = Fraction(99, 100)
    false_positive_rate: Fraction = Fraction(1, 100)
    population: int = 100_000

    def __post_init__(self):
        for value in (self.prevalence, self.sensitivity, self.false_positive_rate):
            if not 0 <= value <= 1:
                raise ValueError("probabilities must lie in [0, 1]")
        if self.population <= 0:
            raise ValueError("population must be positive")

    @property
    def healthy_prior(self):
        return 1 - self.prevalence

    @property
    def true_positive_mass(self):
        return self.prevalence * self.sensitivity

    @property
    def false_positive_mass(self):
        return self.healthy_prior * self.false_positive_rate

    @property
    def positive_mass(self):
        return self.true_positive_mass + self.false_positive_mass

    @property
    def posterior(self):
        if self.positive_mass == 0:
            raise ValueError("P(+) must be positive")
        return self.true_positive_mass / self.positive_mass

    def exact_counts(self):
        counts = {
            "all": Fraction(self.population),
            "diseased": self.population * self.prevalence,
            "healthy": self.population * self.healthy_prior,
            "true_positive": self.population * self.true_positive_mass,
            "false_positive": self.population * self.false_positive_mass,
            "all_positive": self.population * self.positive_mass,
        }
        if any(count.denominator != 1 for count in counts.values()):
            raise ValueError("population does not produce exact integer counts")
        return {key: int(value) for key, value in counts.items()}

    def positive_pool_widths(self, total_width):
        """Lengths in the new condition space, preserving the 99:999 ratio."""
        return (total_width * float(self.posterior),
                total_width * float(1 - self.posterior))


MODEL = ScreeningModel()
