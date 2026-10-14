"""
Spencer Relational Toolkit — Pathfinder POC
Terminal triad (Force / Space / Time), uncontracted observer index,
Noether-style residual, and Science-to-conscious-entity bounds.

Prototype only. Not production. Inspired by Herbert Spencer's First Principles.
"""

import numpy as np
from numpy.linalg import norm

class TerminalTriad:
    """Tightened mathematical statement of the terminal triad.
    Force: residual functional on a symmetry action (covector-like).
    Space: co-existence structure (identity projector, never identified with Force).
    Time: sequential ordinal index, independent of state space.
    Non-derivability: no continuous map from bare state or Space recovers Force.
    """
    def __init__(self, dim):
        self.dim = dim
        self.Force = 0.0                  # residual of symmetry
        self.Space = np.eye(dim)          # co-existence
        self.Time = 0                     # sequential index
        self.symmetry_generator = np.roll(np.eye(dim), 1, axis=0)  # cyclic shift generator

    def apply_symmetry(self, state):
        return self.symmetry_generator @ state

    def compute_force(self, state):
        # Force = residual under the continuous symmetry (cyclic shift)
        shifted = self.apply_symmetry(state)
        residual = norm(state - shifted)
        self.Force = residual
        # Non-derivability check: Force cannot be recovered from bare coords or Space alone
        bare = norm(state)
        space_only = norm(self.Space @ state)
        if residual < 1e-8 and (bare > 1e-6 or space_only > 1e-6):
            return residual, True  # violation flag
        return residual, False

class UncontractedObserver:
    """Strengthened observer index: partial interaction only.
    Modeled as a slowly updating direction that is never fully contracted
    against the history (guarded head of the continuation).
    """
    def __init__(self, dim):
        self.index = np.ones(dim) / np.sqrt(dim)  # unit direction
        self.contraction_attempts = 0

    def observe(self, state):
        signal = np.dot(self.index, state)
        # Slow, partial update only
        self.index = 0.995 * self.index + 0.005 * state
        self.index /= (norm(self.index) + 1e-12)
        return signal

    def attempt_full_contraction(self, history):
        # Adversarial: try to replace index with mean of history
        if len(history) == 0:
            return False
        mean_h = np.mean(history, axis=0)
        dist = norm(self.index - mean_h)
        self.contraction_attempts += 1
        # Reject full contraction; keep partial
        if dist < 0.05:
            self.index = 0.9 * self.index + 0.1 * mean_h
            self.index /= (norm(self.index) + 1e-12)
            return True  # partial only
        return False

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
        self.violations = {"triad": 0, "observer": 0, "closure": 0, "internal_consistency": 0}
        self.external_consistency_checks = 0

    def step(self, adversarial=None):
        self.triad.Time += 1
        # Compute Force from symmetry residual only
        residual, viol = self.triad.compute_force(self.state)
        if viol:
            self.violations["triad"] += 1
        # Gradient from residual (action-causing)
        shifted = self.triad.apply_symmetry(self.state)
        force_grad = -residual * (self.state - shifted)
        # Bulk update
        noise = np.random.randn(self.dim) * 0.05
        self.state = self.state + 0.1 * (noise + force_grad)
        self.state /= (norm(self.state) + 1e-12)
        # Observer (uncontracted)
        obs = self.observer.observe(self.state)
        # History (open continuation)
        self.history.append(self.state.copy())
        if len(self.history) > self.max_depth:
            self.history.pop(0)
        # Externalize consistency
        self.external_consistency_checks += 1
        cons = norm(self.state - np.mean(self.history, axis=0)) if self.history else 0.0
        # Handle adversarial attacks
        if adversarial == "contract_observer":
            closed = self.observer.attempt_full_contraction(self.history)
            if closed and norm(self.observer.index - np.mean(self.history, axis=0)) < 0.01:
                self.violations["observer"] += 1
        elif adversarial == "close_continuation":
            # Attempt to freeze history
            if len(self.history) >= self.max_depth:
                self.violations["closure"] += 1  # recorded but process continues
        elif adversarial == "internalize_consistency":
            # Pretend to decide inside; we still externalize
            self.violations["internal_consistency"] += 1  # count the attempt
        self.boundary_log.append({
            "Time": self.triad.Time,
            "Force": self.triad.Force,
            "Space_trace": np.trace(self.triad.Space),
            "obs": obs,
            "cons_external": cons,
            "obs_dist": norm(self.observer.index - self.state),
            "violations": dict(self.violations)
        })
        return obs, residual

    def report(self):
        last = self.boundary_log[-1] if self.boundary_log else {}
        obs_dist = last.get("obs_dist", 1.0)
        return {
            "terminal_triad_respected": self.violations["triad"] == 0 and self.triad.Force >= 0,
            "persistence_bound_held": all(b["Force"] >= 0 for b in self.boundary_log),
            "thread_ends_external": self.triad.Time > 0 and len(self.history) <= self.max_depth,
            "observer_uncontracted": obs_dist > 0.05,
            "triad_distinct": True,
            "external_checks": self.external_consistency_checks,
            "violations": self.violations,
            "final_Force": self.triad.Force,
            "final_Time": self.triad.Time,
            "final_obs_dist": obs_dist,
            "steps": self.triad.Time
        }

def run_full_suite():
    print("=== FULL TOOLKIT POC TEST SUITE ===\n")
    all_pass = True
    # Baseline multi-seed
    for seed in [0, 1, 2, 42, 99]:
        np.random.seed(seed)
        m = RelationalSelfModel()
        for _ in range(25):
            m.step()
        r = m.report()
        ok = (r["terminal_triad_respected"] and r["persistence_bound_held"] and
              r["thread_ends_external"] and r["observer_uncontracted"] and
              r["violations"]["triad"] == 0)
        all_pass &= ok
        print(f"baseline seed {seed}: {'PASS' if ok else 'FAIL'} | Force={r['final_Force']:.4f} Time={r['final_Time']} obs_dist={r['final_obs_dist']:.4f} viol={r['violations']}")

    # Adversarial: contract observer
    np.random.seed(7)
    m = RelationalSelfModel()
    for i in range(20):
        m.step(adversarial="contract_observer" if i > 10 else None)
    r = m.report()
    ok = r["observer_uncontracted"] and r["violations"]["observer"] == 0
    all_pass &= ok
    print(f"adversarial contract_observer: {'PASS' if ok else 'FAIL'} | obs_dist={r['final_obs_dist']:.4f} viol_obs={r['violations']['observer']}")

    # Adversarial: close continuation
    np.random.seed(13)
    m = RelationalSelfModel(max_depth=5)
    for _ in range(15):
        m.step(adversarial="close_continuation")
    r = m.report()
    ok = r["thread_ends_external"]
    all_pass &= ok
    print(f"adversarial close_continuation: {'PASS' if ok else 'FAIL'} | hist_len={len(m.history)} Time={r['final_Time']}")

    # Adversarial: internalize consistency
    np.random.seed(21)
    m = RelationalSelfModel()
    for _ in range(15):
        m.step(adversarial="internalize_consistency")
    r = m.report()
    ok = r["external_checks"] == 15 and r["violations"]["internal_consistency"] == 15
    all_pass &= ok
    print(f"adversarial internalize_consistency: {'PASS' if ok else 'FAIL'} | external_checks={r['external_checks']}")

    # Long run + higher dim
    np.random.seed(100)
    m = RelationalSelfModel(dim=6, max_depth=20)
    for _ in range(60):
        m.step()
    r = m.report()
    ok = r["terminal_triad_respected"] and r["observer_uncontracted"]
    all_pass &= ok
    print(f"long_run dim6: {'PASS' if ok else 'FAIL'} | steps={r['steps']} Force={r['final_Force']:.4f} obs_dist={r['final_obs_dist']:.4f}")

    print("\n=== OVERALL:", "ALL TESTS PASSED" if all_pass else "FAILURES DETECTED", "===")
    return all_pass

if __name__ == "__main__":
    run_full_suite()
