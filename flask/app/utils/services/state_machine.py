from transitions import Machine, MachineError
from typing import Optional, List
from flask import current_app


class GenericStateMachine(Machine):

    def __init__(self, entity, property_name='status', initial_state = None, transitions = [], states = [], allow_self_transition=True):
        super().__init__(
            model=self,
            states=states,
            transitions=transitions,
            initial=initial_state
        )
        self.entity = entity
        self.property_name = property_name
        self.transitions = transitions
        self.allow_self_transition = allow_self_transition  # Control variable for allowing self-transitions


        # build conditions functions
        for transition in self.transitions:
            condition = transition.get("conditions")
            if condition is not None:
                setattr(self, condition, getattr(self, "condition_func"))
    
    
    def condition_func(self):
        return True
    

    def log_status(self):
        print(f"Status changed to {self.state}", flush=True)

    def export_as_dot(self, name: Optional[str] = "InboundOrder_machine"):
        from transitions.extensions import GraphMachine


        graph = GraphMachine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial=self.initial,
            show_conditions=True,
        )


        return graph.get_graph().draw(f"{name}.png", prog="dot")

    def get_matching_triggers(self, new_state: str) -> List[str]:
        matching_triggers = []
        for transition in self.transitions:

            if (
                transition.get("source") == getattr(self.entity, self.property_name).value
                or getattr(self.entity, self.property_name).value in transition.get("source")
            ) and (
                transition.get("dest") == new_state
                or new_state in transition.get("dest")
            ):
                trigger = transition.get("trigger")
                matching_triggers.append(trigger)
        return matching_triggers

    def validate_state_change(self, new_state) -> bool:

        current_state_value = getattr(self.entity, self.property_name).value
        new_state_value = new_state.value

        if current_state_value == new_state_value:
            if self.allow_self_transition:
                self.log_status()  # Log the status or perform other side effects
                return True
            else:
                return False  # Return false if self-transitions are disabled

        for trigger in self.get_matching_triggers(new_state_value):
            trigger_func = getattr(self, trigger, None)
            if trigger_func is not None:
                trigger_func()  # Assuming the trigger function does not require order as a parameter
                self.set_state(new_state_value)
                if self.state == new_state_value:
                    return True
        return False

    def check_conditions(self, transition: dict) -> bool:
        conditions = transition.get("conditions")
        if conditions is None:
            return True
        condition_func = getattr(self, conditions, None)
        if condition_func is not None:
            return condition_func(self.entity)
        return False
