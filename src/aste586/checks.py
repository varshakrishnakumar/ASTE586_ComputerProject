"""Per-function checks of the dynamics backend -- provided.

``aste586 check`` runs these. Each function you implement is exercised in
isolation with small hand-picked inputs, so you get feedback on one function
at a time -- *before* the whole state derivative is assembled and integrated
by ``aste586 run``.

Two kinds of check are used:

* **known values** -- a few inputs whose correct outputs were computed once
  and stored here as plain numbers;
* **physical properties** -- relations that any correct implementation must
  satisfy (a torque-free rigid body neither gains nor loses kinetic energy,
  a quaternion derivative never changes the quaternion's length, ...).
  When one of these fails its hint tells you *what kind* of mistake to look
  for.

Nothing here spells out the equations of motion themselves.
"""

from __future__ import annotations

from types import ModuleType
from typing import Callable

import numpy as np

from .model import IDX_OMEGA_D, IDX_Q, IDX_THETA_D, IDX_W, Params
from .report import FAIL, PASS, SKIP, TODO, Check, describe_exception

# ---------------------------------------------------------------------------
# Fixed inputs
# ---------------------------------------------------------------------------

_A_PART1 = np.array([[0, 2, 0, 0], [-2, 0, 0, 0], [0, 0, 0, 200], [0, 0, -200, 0]], float)
_X0_PART1 = np.array([1.0, 0.0, 1.0, 0.0])
_J345 = np.diag([3.0, 4.0, 5.0])
_Q_ID = np.array([0.0, 0.0, 0.0, 1.0])

_FILES = {
    "linear_ivp_rhs": "part1.py", "analytical_solution": "part1.py",
    "quaternion_derivative": "kinematics.py", "euler_eqs": "rigid_body.py",
    "damper_eom": "damper.py", "state_derivative": "derivatives.py",
}
_PARTS = {
    "linear_ivp_rhs": 1, "analytical_solution": 1, "quaternion_derivative": 2,
    "euler_eqs": 2, "state_derivative": 2, "damper_eom": 4,
}


def _unit(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, float)
    return q / np.linalg.norm(q)


def _fmt(a) -> str:
    return np.array2string(np.asarray(a, float), precision=5, suppress_small=True,
                           max_line_width=200)


def _rand(seed: int):
    return np.random.default_rng(seed)


def _expect(got, want, *, rtol=1e-8, atol=1e-9, what="value") -> tuple[bool, str]:
    got = np.asarray(got, float)
    want = np.asarray(want, float)
    if got.shape != want.shape:
        return False, f"{what}: expected shape {want.shape}, got {got.shape}"
    if np.allclose(got, want, rtol=rtol, atol=atol):
        return True, "ok"
    return False, f"{what}: expected {_fmt(want)}, got {_fmt(got)}"


class _Suite:
    """Collects checks for one backend; wraps exceptions into statuses."""

    def __init__(self, backend: ModuleType):
        self.backend = backend
        self.checks: list[Check] = []
        self._todo: set[str] = set()

    def fn(self, name: str) -> Callable:
        return getattr(self.backend, name)

    def run(self, function: str, name: str, thunk: Callable[[], tuple[bool, str]],
            hint: str = "", needs: tuple[str, ...] = ()) -> None:
        group = f"{function}  [{_FILES[function]}]"
        blocked = [n for n in needs if n in self._todo]
        if function in self._todo or blocked:
            what = function if function in self._todo else ", ".join(blocked)
            self.checks.append(Check(name, SKIP, f"waiting on {what}", group=group))
            return
        try:
            ok, detail = thunk()
        except NotImplementedError:
            self._todo.add(function)
            self.checks.append(Check(
                name, TODO, f"not implemented yet -- src/aste586/dynamics/{_FILES[function]}",
                group=group))
            return
        except Exception as exc:  # noqa: BLE001 -- report student errors, don't crash
            self.checks.append(Check(name, FAIL, describe_exception(exc), hint=hint, group=group))
            return
        self.checks.append(Check(name, PASS if ok else FAIL, detail,
                                 hint="" if ok else hint, group=group))


# ---------------------------------------------------------------------------
# Part 1
# ---------------------------------------------------------------------------

def _check_part1(s: _Suite) -> None:
    rhs, sol = "linear_ivp_rhs", "analytical_solution"

    def rhs_known():
        x = np.array([0.3, -1.2, 0.7, 0.4])
        return _expect(s.fn(rhs)(0.0, x, _A_PART1), [-2.4, -0.6, 80.0, -140.0])

    def rhs_random():
        rng = _rand(1)
        for _ in range(5):
            A = rng.normal(size=(4, 4))
            x = rng.normal(size=4)
            ok, d = _expect(s.fn(rhs)(0.3, x, A), A @ x)
            if not ok:
                return ok, d
        return True, "ok"

    s.run(rhs, "known value", rhs_known,
          hint="dx/dt = A x -- a matrix-vector product, not element-wise.")
    s.run(rhs, "works for any 4x4 A", rhs_random,
          hint="do not hard-code the handout matrix; use the A that is passed in.")

    def sol_shape():
        t = np.linspace(0.0, 1.0, 11)
        x = np.asarray(s.fn(sol)(t), float)
        if x.shape == (4, 11):
            return False, "got shape (4, 11): transpose it (time along the first axis)"
        if x.shape != (11, 4):
            return False, f"expected shape (11, 4) for 11 times, got {x.shape}"
        return True, "ok"

    def sol_ic():
        x0 = np.asarray(s.fn(sol)(np.array([0.0])), float)[0]
        return _expect(x0, _X0_PART1, what="x(0)")

    def sol_ode():
        t = np.array([0.0, 0.137, 0.5, 1.3, 2.9, 7.7, 10.0])
        h = 1e-5
        x = np.asarray(s.fn(sol)(t), float)
        xp = np.asarray(s.fn(sol)(t + h), float)
        xm = np.asarray(s.fn(sol)(t - h), float)
        deriv = (xp - xm) / (2 * h)
        want = x @ _A_PART1.T
        err = np.abs(deriv - want).max()
        scale = max(np.abs(want).max(), 1.0)
        return err <= 1e-4 * scale, (
            "ok" if err <= 1e-4 * scale else
            f"max |dx/dt - A x| = {err:.2e}: the closed form does not satisfy the ODE")

    def sol_conserved():
        t = np.linspace(0.0, 10.0, 1001)
        x = np.asarray(s.fn(sol)(t), float)
        c = np.abs(np.sum(x**2, axis=1) - 2.0).max()
        return c <= 1e-9, ("ok" if c <= 1e-9 else
                           f"max |sum x_i^2 - 2| = {c:.2e}, should be 0 for all t")

    s.run(sol, "returns an (N, 4) array", sol_shape,
          hint="build the result with np.column_stack([...]) of the four components.")
    s.run(sol, "matches x(0) = [1, 0, 1, 0]", sol_ic,
          hint="apply the initial condition to your general solution.")
    s.run(sol, "satisfies dx/dt = A x", sol_ode,
          hint="check the sign of each sine term and the frequencies (2 and 200 rad/s).")
    s.run(sol, "conserves x1^2 + x2^2 + x3^2 + x4^2", sol_conserved,
          hint="each 2x2 block is a pure rotation, so each pair keeps its length.")


# ---------------------------------------------------------------------------
# Part 2: kinematics and Euler's equations
# ---------------------------------------------------------------------------

def _check_kinematics(s: _Suite) -> None:
    f = "quaternion_derivative"

    def identity():
        got = s.fn(f)(_Q_ID.copy(), np.array([1.0, 0.0, 0.0]))
        return _expect(got, [0.5, 0.0, 0.0, 0.0], what="dq/dt at q = identity, omega = [1,0,0]")

    def known():
        cases = [
            ([0.1, -0.2, 0.3, 0.927361849549570], [0.5, -1.0, 2.0],
             [0.18184046238739257, -0.48868092477478514, 0.9273618495495703, -0.42500000000000016]),
            ([0.5, 0.5, 0.5, 0.5], [0.0, 0.0, 3.0], [0.75, -0.75, 0.75, -0.75]),
        ]
        for q, w, want in cases:
            ok, d = _expect(s.fn(f)(_unit(q), np.array(w)), want)
            if not ok:
                return ok, d
        return True, "ok"

    def norm_preserving():
        rng = _rand(2)
        for _ in range(6):
            q = _unit(rng.normal(size=4))
            w = rng.normal(size=3)
            dq = np.asarray(s.fn(f)(q, w), float)
            if abs(np.dot(q, dq)) > 1e-9:
                return False, f"q . dq/dt = {np.dot(q, dq):.2e} (should be 0)"
        return True, "ok"

    def magnitude():
        rng = _rand(3)
        for _ in range(6):
            q = _unit(rng.normal(size=4))
            w = rng.normal(size=3)
            dq = np.asarray(s.fn(f)(q, w), float)
            if not np.isclose(np.linalg.norm(dq), 0.5 * np.linalg.norm(w), rtol=1e-9):
                return False, f"|dq/dt| = {np.linalg.norm(dq):.5f}, |omega|/2 = {0.5*np.linalg.norm(w):.5f}"
        return True, "ok"

    s.run(f, "dq/dt at the identity attitude", identity,
          hint="at q = [0,0,0,1] you must get 0.5*[omega, 0]; check the scalar-LAST order and the factor 1/2.")
    s.run(f, "known values", known,
          hint="the identity case is fine but a general one is not: the quaternion product is in the wrong order for the body->inertial convention (q (x) omega, not omega (x) q).")
    s.run(f, "keeps |q| constant (q . dq/dt = 0)", norm_preserving,
          hint="a correct kinematic equation never changes the quaternion's length; look for a sign error in a component.")
    s.run(f, "|dq/dt| = |omega| / 2", magnitude,
          hint="check the factor of 1/2.")


def _check_rigid_body(s: _Suite) -> None:
    f = "euler_eqs"

    def known():
        cases = [
            ([1.0, -2.0, 0.5], [0.0, 0.0, 0.0], [0.3333333333333333, 0.25, 0.4]),
            ([0.3, 0.7, -1.1], [0.1, -0.2, 0.05],
             [0.29, -0.21500000000000002, -0.031999999999999994]),
        ]
        for w, M, want in cases:
            ok, d = _expect(s.fn(f)(np.array(w), _J345, np.array(M)), want)
            if not ok:
                return ok, d
        return True, "ok"

    def spherical():
        J = 2.0 * np.eye(3)
        w = np.array([0.4, -1.3, 2.2])
        ok, d = _expect(s.fn(f)(w, J, np.zeros(3)), np.zeros(3), what="alpha (spherical, torque-free)")
        if not ok:
            return ok, d
        M = np.array([0.5, 1.0, -2.0])
        return _expect(s.fn(f)(w, J, M), M / 2.0, what="alpha (spherical, with torque)")

    def energy():
        rng = _rand(4)
        for _ in range(6):
            w = rng.normal(size=3)
            J = np.diag(rng.uniform(1.0, 10.0, size=3))
            a = np.asarray(s.fn(f)(w, J, np.zeros(3)), float)
            power = float(w @ J @ a)          # dT/dt for torque-free motion
            if abs(power) > 1e-9:
                return False, f"dT/dt = omega . J alpha = {power:.2e} (should be 0)"
        return True, "ok"

    def momentum():
        rng = _rand(5)
        for _ in range(6):
            w = rng.normal(size=3)
            J = np.diag(rng.uniform(1.0, 10.0, size=3))
            a = np.asarray(s.fn(f)(w, J, np.zeros(3)), float)
            H = J @ w
            if abs(H @ (J @ a)) > 1e-9:
                return False, f"d|H|^2/dt = {2*H @ (J @ a):.2e} (should be 0)"
        return True, "ok"

    s.run(f, "known values", known,
          hint="check which pair of inertias multiplies which pair of omega components in each row.")
    s.run(f, "spherical body: alpha = torque / I", spherical,
          hint="with I1 = I2 = I3 every gyroscopic term vanishes; make sure you divide by the inertia.")
    s.run(f, "torque-free: kinetic energy conserved", energy,
          hint="omega . J alpha must vanish -- the sign of at least one (I_j - I_k) w_j w_k term is wrong.")
    s.run(f, "torque-free: |H| conserved", momentum,
          hint="H . J alpha must vanish -- the components are paired with the wrong inertia differences.")


def _check_derivatives(s: _Suite) -> None:
    f = "state_derivative"
    z7 = np.array([1.0, -2.0, 0.5, 0.10000000000000003, -0.20000000000000007,
                   0.3000000000000001, 0.9273618495495703])
    dz7 = [0.3333333333333333, 0.25, 0.4, 0.7136809247747853, -0.8023618495495703,
           0.2318404623873926, -0.3250000000000001]
    rigid = Params(J=_J345, model="rigid")

    def rigid_shape():
        out = np.asarray(s.fn(f)(0.0, z7.copy(), rigid), float)
        return out.shape == (7,), ("ok" if out.shape == (7,) else
                                   f"expected shape (7,), got {out.shape}")

    def rigid_known():
        return _expect(s.fn(f)(0.0, z7.copy(), rigid), dz7)

    def rigid_glue():
        out = np.asarray(s.fn(f)(0.0, z7.copy(), rigid), float)
        alpha = np.asarray(s.fn("euler_eqs")(z7[IDX_W], _J345, np.zeros(3)), float)
        dq = np.asarray(s.fn("quaternion_derivative")(z7[IDX_Q], z7[IDX_W]), float)
        return _expect(out, np.concatenate([alpha, dq]), what="dz (from your own euler_eqs/quaternion_derivative)")

    def no_mutation():
        z = z7.copy()
        s.fn(f)(0.0, z, rigid)
        return np.array_equal(z, z7), ("ok" if np.array_equal(z, z7) else
                                       "state_derivative modified its input z in place")

    s.run(f, "rigid: returns 7 values", rigid_shape,
          hint="dz has the same length as z: 3 (alpha) + 4 (dq/dt).")
    s.run(f, "rigid: packs [alpha, dq/dt] in order", rigid_glue,
          needs=("euler_eqs", "quaternion_derivative"),
          hint="dz = concatenate([alpha, dq]) -- same layout as z (IDX_W then IDX_Q).")
    s.run(f, "rigid: known value", rigid_known,
          needs=("euler_eqs", "quaternion_derivative"),
          hint="this fails only if euler_eqs or quaternion_derivative is wrong -- fix those first.")
    s.run(f, "does not modify z in place", no_mutation,
          hint="build a new array for dz; never assign into z.")

    z9 = np.array([14.0, 0.0, 50.0, 0.10000000000000003, -0.20000000000000007,
                   0.3000000000000001, 0.9273618495495703, 0.02, -0.3])
    dz9 = [-0.025, 2103.3857095158596, 0.00175, 1.4915329468469904, -0.40000000000000036,
           24.584046238739262, -8.200000000000003, -0.3, -2031.4257095158596]
    damped = Params(J=np.diag([300.0, 300.0, 1200.0]), model="damped", Id=0.5, D=120.0, K=1.0)

    def damped_shape():
        out = np.asarray(s.fn(f)(0.0, z9.copy(), damped), float)
        return out.shape == (9,), ("ok" if out.shape == (9,) else
                                   f"expected shape (9,), got {out.shape}")

    def damped_glue():
        out = np.asarray(s.fn(f)(0.0, z9.copy(), damped), float)
        a, td, od = s.fn("damper_eom")(z9[IDX_W], damped.J, damped.Id, damped.D, damped.K,
                                        z9[IDX_THETA_D], z9[IDX_OMEGA_D])
        dq = np.asarray(s.fn("quaternion_derivative")(z9[IDX_Q], z9[IDX_W]), float)
        want = np.concatenate([np.asarray(a, float), dq, [float(td), float(od)]])
        return _expect(out, want, what="dz (from your own damper_eom/quaternion_derivative)")

    def damped_known():
        return _expect(s.fn(f)(0.0, z9.copy(), damped), dz9, rtol=1e-8, atol=1e-6)

    s.run(f, "damped: returns 9 values", damped_shape,
          hint="for params.model == 'damped' append [theta_d_dot, omega_d_dot] to dz.")
    s.run(f, "damped: packs [alpha, dq/dt, theta_d', omega_d']", damped_glue,
          needs=("damper_eom", "quaternion_derivative"),
          hint="use damper_eom (not euler_eqs) for alpha when the model is damped, and keep the order theta_d then omega_d.")
    s.run(f, "damped: known value", damped_known,
          needs=("damper_eom", "quaternion_derivative"),
          hint="this fails only if damper_eom or quaternion_derivative is wrong -- fix those first.")


# ---------------------------------------------------------------------------
# Part 4: damper
# ---------------------------------------------------------------------------

def _check_damper(s: _Suite) -> None:
    f = "damper_eom"

    def known():
        cases = [
            ((300.0, 300.0, 1200.0), 0.5, 120.0, 1.0, [14.0, 0.0, 50.0], 0.02, -0.3,
             [-0.025, 2103.3857095158596, 0.00175], -0.3, -2031.4257095158596),
            ((45.0, 60.0, 31.0), 0.5, 540.0, 20.0, [0.4, 40.0, 70.0], -0.01, 0.05,
             [1804.4833333333333, -6.13781512605042, -7.742258064516129], 0.05, -47.46218487394958),
        ]
        for Jd, Id, D, K, w, th, om, a_want, td_want, od_want in cases:
            out = s.fn(f)(np.array(w), np.diag(Jd), Id, D, K, th, om)
            if not (isinstance(out, tuple) and len(out) == 3):
                return False, "must return a 3-tuple (alpha, theta_d_dot, omega_d_dot)"
            a, td, od = out
            for got, want, what in ((a, a_want, "alpha"), (td, td_want, "theta_d_dot"),
                                    (od, od_want, "omega_d_dot")):
                ok, d = _expect(got, want, rtol=1e-8, atol=1e-6, what=what)
                if not ok:
                    return ok, d
        return True, "ok"

    def wheel_angle_rate():
        _, td, _ = s.fn(f)(np.array([1.0, 2.0, 3.0]), _J345, 0.1, 0.5, 0.2, 0.3, -0.7)
        return np.isclose(float(td), -0.7), ("ok" if np.isclose(float(td), -0.7) else
                                             f"theta_d_dot = {float(td)}, expected omega_d = -0.7")

    def momentum():
        # Total angular momentum in body coords, H = J w + Id Omega_d e2, obeys
        # dH/dt + w x H = 0 for a torque-free body -- whatever is inside the box.
        rng = _rand(6)
        for _ in range(6):
            w = rng.normal(size=3)
            I = rng.uniform(2.0, 10.0, size=3)
            Id = rng.uniform(0.05, 0.5)
            D, K = rng.uniform(0.1, 5.0), rng.uniform(0.1, 5.0)
            th, om = rng.normal(), rng.normal()
            a, _, od = s.fn(f)(w, np.diag(I), Id, D, K, th, om)
            a = np.asarray(a, float)
            H = I * w + np.array([0.0, Id * om, 0.0])
            Hdot = I * a + np.array([0.0, Id * float(od), 0.0])
            resid = Hdot + np.cross(w, H)
            if np.abs(resid).max() > 1e-7 * max(1.0, np.abs(H).max()):
                return False, f"dH/dt + omega x H = {_fmt(resid)} (should be 0)"
        return True, "ok"

    def energy():
        # Total kinetic + spring energy can only be lost through the dashpot:
        # dT/dt = -D Omega_d^2.
        rng = _rand(7)
        for _ in range(6):
            w = rng.normal(size=3)
            I = rng.uniform(2.0, 10.0, size=3)
            Id = rng.uniform(0.05, 0.5)
            D, K = rng.uniform(0.1, 5.0), rng.uniform(0.1, 5.0)
            th, om = rng.normal(), rng.normal()
            a, td, od = s.fn(f)(w, np.diag(I), Id, D, K, th, om)
            a = np.asarray(a, float)
            dT = (float(w @ (I * a)) + Id * om * float(od)
                  + Id * (a[1] * om + w[1] * float(od)) + K * th * float(td))
            if not np.isclose(dT, -D * om**2, rtol=1e-7, atol=1e-9):
                return False, f"dT/dt = {dT:.5f}, expected -D Omega_d^2 = {-D*om**2:.5f}"
        return True, "ok"

    s.run(f, "known values", known,
          hint="compare each of the five equations with the handout; the wheel is on body axis 2 and the body-2 equation uses (I2 - Id).")
    s.run(f, "theta_d_dot equals omega_d (Eq 4)", wheel_angle_rate,
          hint="the wheel angle's rate is just the wheel rate.")
    s.run(f, "angular momentum conserved", momentum,
          hint="the wheel momentum Id*Omega_d must appear in the body-1 and body-3 gyroscopic terms with the right signs.")
    s.run(f, "energy lost only through the dashpot", energy,
          hint="the spring/dashpot torque enters Eq 2 and Eq 5 with opposite signs (action/reaction); check them.")


# ---------------------------------------------------------------------------

def run_checks(part: int | None = None, backend: ModuleType | None = None) -> list[Check]:
    """Run every check (or only those for ``part``) and return the results.

    ``backend`` defaults to the student backend ``aste586.dynamics``.
    """
    if backend is None:
        from . import dynamics as backend
    s = _Suite(backend)
    sections = [(1, _check_part1), (2, _check_kinematics), (2, _check_rigid_body),
                (2, _check_derivatives), (4, _check_damper)]
    for p, section in sections:
        if part is None or p == part or (part == 3 and p == 2):
            section(s)
    if part == 2:
        # Part 2 does not need the damper; hide the damped-model glue checks.
        s.checks = [c for c in s.checks if "damped" not in c.name]
    return s.checks
