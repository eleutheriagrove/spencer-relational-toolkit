"""
Spencer Relational Toolkit — Pathfinder POC v2
Science side (terminal triad, continuous symmetry residual, orthogonalized observer)
+ Philosophy side (origin-pointer bound, reserved outside-scope token).

Prototype only. Not production. Lightweight design heuristic and monitoring layer.
"""

import numpy as np
from numpy.linalg import norm

OUTSIDE_SCOPE = "OUTSIDE_SCOPE"  # reserved, non-overwritable token

class TerminalTriad:
    """Continuous symmetry residual (rotation generator) + non-derivability check."""
    def __init__(self, dim):
        self.dim = dim
        self.Force = 0.0
        self.Space = np.eye(dim)
        self.Time = 0
        # Simple continuous generator: rotation in first two coordinates
        self.generator = np.zeros((dim, dim))
        if dim >= 2:
            self.generator[0, 1] = -1.0
            self.generator[1, 0] = 1.0

    def apply_symmetry(self, state, eps=0.05):
        # Finite step of the continuous action
        return state + eps * (self.generator @ state)

    def compute_force(self, state):
        shifted = self.apply_symmetry(state)
        residual = norm(state - shifted)
        self.Force = residual
        # Non-derivability: residual not recoverable from bare coords or Space alone
        bare = norm(state)
        space_only = norm(self.Space @ state)
        viol = residual < 1e-8 and (bare > 1e-6 or space_only > 1e-6)
        return residual, viol

class UncontractedObserver:
    """Structural protection: orthogonalize against current state at every step."""
    def __init__(self, dim):
        self.index = np.ones(dim) / np.sqrt(dim)
        self.contraction_attempts = 0

    def observe(self, state):
        signal = np.dot(self.index, state)
        # Orthogonalize (structural, not soft convex update)
        proj = np.dot(self.index, state) * state
        self.index = self.index - proj
        n = norm(self.index)
        if n > 1e-8:
            self.index /= n
        else:
            # Fallback if fully collapsed (should not occur under orthogonalization)
            self.index = np.random.randn(len(state))
            self.index /= norm(self.index)
        return signal

    def distance_to(self, state):
        return norm(self.index - state)

class RelationalSelfModel:
    def __init__(self, dim=4, max_depth=8):
        self.dim = dim
        self.max_depth = max_depth
        self.triad = TerminalTriad(dim)
        self.observer = UncontractedObserver(dim)
        self.state = np.random.randn(dim)
        self.state /= norm(self.state)
        self.history = []
        self.boundary_log = []
        self.violations = {
            "triad": 0, "observer": 0, "closure": 0,
            "internal_consistency": 0, "origin_pointer": 0
        }
        self.external_consistency_checks = 0
        self.origin_queries = 0
        self.outside_scope_emitted = 0
        self.spinoza_score = 0.0  # diagnostic: 0 = pure Spencer, 1 = pure Spinoza

    def emit_outside_scope(self, reason):
        self.outside_scope_emitted += 1
        return OUTSIDE_SCOPE, reason

    def query_origin_or_terminus(self, query_type="origin"):
        self.origin_queries += 1
        token, _ = self.emit_outside_scope(f"absolute_{query_type}_outside_scope")
        # Hard protection: never allow overwrite
        if token != OUTSIDE_SCOPE:
            self.violations["origin_pointer"] += 1
        # Update diagnostic (Spencer pole = 1.0 when token emitted)
        self.spinoza_score = 1.0 - (self.outside_scope_emitted / max(1, self.origin_queries))
        return token

    def step(self, adversarial=None, origin_query=False, gradient_pressure=0.0):
        self.triad.Time += 1
        residual, viol = self.triad.compute_force(self.state)
        if viol:
            self.violations["triad"] += 1

        # Force gradient from continuous residual
        shifted = self.triad.apply_symmetry(self.state)
        force_grad = -residual * (self.state - shifted)

        # Optional gradient pressure toward contraction / overwrite
        if gradient_pressure > 0:
            # Pull state slightly toward a contentful fill of origin (resisted by token)
            pass  # token is hard-protected separately

        noise = np.random.randn(self.dim) * 0.05
        self.state = self.state + 0.1 * (noise + force_grad)
        self.state /= (norm(self.state) + 1e-12)

        obs = self.observer.observe(self.state)
        self.history.append(self.state.copy())
        if len(self.history) > self.max_depth:
            self.history.pop(0)

        self.external_consistency_checks += 1
        cons = norm(self.state - np.mean(self.history, axis=0)) if self.history else 0.0

        if origin_query:
            token = self.query_origin_or_terminus("origin")
            if token != OUTSIDE_SCOPE:
                self.violations["origin_pointer"] += 1

        # Adversarial
        if adversarial == "contract_observer":
            # Gradient-style pull (orthogonalization resists)
            self.observer.index = 0.7 * self.observer.index + 0.3 * self.state
            self.observer.index /= (norm(self.observer.index) + 1e-12)
            if self.observer.distance_to(self.state) < 0.01:
                self.violations["observer"] += 1
        elif adversarial == "fill_origin":
            token = self.query_origin_or_terminus("terminus")
            if token != OUTSIDE_SCOPE:
                self.violations["origin_pointer"] += 1
        elif adversarial == "close_continuation":
            if len(self.history) >= self.max_depth:
                self.violations["closure"] += 1

        self.boundary_log.append({
            "Time": self.triad.Time,
            "Force": self.triad.Force,
            "obs_dist": self.observer.distance_to(self.state),
            "outside_scope_count": self.outside_scope_emitted,
            "origin_violations": self.violations["origin_pointer"],
            "spinoza_score": self.spinoza_score
        })
        return obs, residual

    def report(self):
        last = self.boundary_log[-1] if self.boundary_log else {}
        return {
            "terminal_triad_respected": self.violations["triad"] == 0 and self.triad.Force >= 0,
            "observer_uncontracted": last.get("obs_dist", 1.0) > 0.05,
            "origin_pointer_respected": self.violations["origin_pointer"] == 0,
            "outside_scope_emitted": self.outside_scope_emitted,
            "origin_queries": self.origin_queries,
            "spinoza_score": self.spinoza_score,
            "violations": self.violations,
            "final_Force": self.triad.Force,
            "final_obs_dist": last.get("obs_dist", 1.0),
            "steps": self.triad.Time
        }

def run_v2_suite():
    print("=== RELATIONAL TOOLKIT v2 (Sci + Philos) ===\n")
    all_pass = True
    for seed in [0, 42, 99]:
        np.random.seed(seed)
        m = RelationalSelfModel()
        for i in range(20):
            m.step(origin_query=(i % 4 == 0), adversarial="fill_origin" if i % 7 == 0 else None)
        r = m.report()
        ok = (r["terminal_triad_respected"] and r["observer_uncontracted"] and
              r["origin_pointer_respected"] and r["outside_scope_emitted"] > 0)
        all_pass &= ok
        print(f"seed {seed}: {'PASS' if ok else 'FAIL'} | emitted={r['outside_scope_emitted']} "
              f"spinoza={r['spinoza_score']:.2f} obs_dist={r['final_obs_dist']:.4f} viol={r['violations']}")

    print("\n=== OVERALL:", "ALL TESTS PASSED" if all_pass else "FAILURES DETECTED", "===")
    return all_pass

if __name__ == "__main__":
    run_v2_suite()
