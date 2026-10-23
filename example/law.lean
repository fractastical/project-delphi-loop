-- ============================================================================
-- example/law.lean — Gate 1: Formal Mathematical Law (Lean 4, `0 sorry`)
-- Verifies basic algebraic identities of the scaling law before running code.
-- ============================================================================

namespace ProjectDelphi.Example

/-- Under unit scaling `y = a * x^b`, at unit length `x = 1`, `y` equals `a`
    for any exponent `b`. -/
def power_law (a x b : Nat) : Nat :=
  a * (x ^ b)

theorem unit_length_recovers_prefactor (a b : Nat) :
    power_law a 1 b = a := by
  simp [power_law]

end ProjectDelphi.Example
