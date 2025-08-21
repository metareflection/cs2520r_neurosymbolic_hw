from typing import List, Tuple, Iterable, Optional, Set
from automata.pda.dpda import DPDA

class DPDAInteractor:
    """
    Incremental, interactive wrapper for automata-lib's DPDA.
    Maintains (state, stack), exposes allowed inputs, and applies one transition per call.
    """
    def __init__(self, dpda: DPDA):
        self.dpda = dpda
        self.state: str = dpda.initial_state
        # Represent stack as a list: bottom at index 0, top at the end.
        self.stack: List[str] = [dpda.initial_stack_symbol]

    def _stack_top(self) -> Optional[str]:
        return self.stack[-1] if self.stack else None

    def _lookup(self, state: str, symbol: str, stack_top: str) -> Optional[Tuple[str, Tuple[str, ...]]]:
        """
        Return δ(q, symbol, stack_top) = (q', push_tuple) if defined; else None.
        Normalize push spec: "" -> (), tuple -> itself.
        """
        if state not in self.dpda.transitions:
            return None
        state_block = self.dpda.transitions[state]
        if symbol not in state_block:
            return None
        stack_block = state_block[symbol]
        if stack_top not in stack_block:
            return None
        next_state, push_spec = stack_block[stack_top]
        push_tuple: Tuple[str, ...] = tuple() if push_spec == "" else tuple(push_spec)
        return next_state, push_tuple

    def allowed_inputs(self) -> Set[str]:
        """
        Legal next input symbols (including "" for ε) at the current configuration.
        """
        top = self._stack_top()
        if top is None:
            return set()
        allowed: Set[str] = set()
        trans_state = self.dpda.transitions.get(self.state, {})
        for symbol, stack_case in trans_state.items():
            if top in stack_case:
                allowed.add(symbol)
        return allowed

    def step(self, symbol: str) -> None:
        """
        Apply exactly one transition using 'symbol' ("" means ε). Raises if undefined.
        """
        top = self._stack_top()
        if top is None:
            raise ValueError("Stack is empty; no transition possible.")

        lookup = self._lookup(self.state, symbol, top)
        if lookup is None:
            raise ValueError(
                f"No transition from state {self.state} with input '{symbol}' and stack top '{top}'. "
                f"Allowed inputs: {sorted(self.allowed_inputs())}"
            )

        next_state, push_tuple = lookup

        # Pop matched top
        self.stack.pop()

        # IMPORTANT: push in REVERSE so the LEFTMOST of push_tuple becomes the NEW TOP
        for s in reversed(push_tuple):
            self.stack.append(s)

        # Move to next state
        self.state = next_state

    def configuration(self) -> Tuple[str, Tuple[str, ...]]:
        return self.state, tuple(self.stack)

    def is_accepting(self) -> bool:
        if self.dpda.acceptance_mode == "final_state":
            return self.state in self.dpda.final_states
        elif self.dpda.acceptance_mode == "empty_stack":
            return len(self.stack) == 0
        else:
            # Fallback (rarely needed)
            return self.dpda.accepts_input([])