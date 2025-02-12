"""Python functions used in remapped G/M codes

See onefinity.ini for the actual remapping
Note: as far as I can tell, this file has to be called remap.
"""

import inspect

from interpreter import INTERP_OK, INTERP_EXECUTE_FINISH  # type: ignore
import linuxcnc  # type: ignore
import emccanon  # type: ignore


def _lineno():
    return inspect.currentframe().f_back.f_lineno  # type: ignore


COORDINATE_SYSTEMS = [{"name": "Shelves", "x": 1039.758, "y": 292.721, "z": -112.744}]


def sync_interpreter(self):
    c = linuxcnc.command()
    c.task_plan_sync()


def change_prolog(self, **words):
    try:
        if self.selected_pocket < 0:
            return "M6: no tool prepared"

        if self.cutter_comp_side:
            return "Cannot change tools with cutter radius compensation on"

        self.params["tool_in_spindle"] = self.current_tool
        self.params["selected_tool"] = self.selected_tool
        self.params["current_pocket"] = self.current_pocket
        self.params["selected_pocket"] = self.selected_pocket
        return INTERP_OK
    except Exception as e:
        return "M6/change_prolog: {}".format(e)


def change_epilog(self, **words):
    try:
        if self.return_value == 0.0:
            # commit change
            self.selected_pocket = int(self.params["selected_pocket"])
            emccanon.CHANGE_TOOL(self.selected_pocket)
            # cause a sync()
            self.tool_change_flag = True
            self.set_tool_parameters()
            return INTERP_OK
        else:
            return f"M6 aborted (return code {self.return_value})"

    except Exception as e:
        return f"M6/change_epilog: {e}"


def activate_custom_coordinate_system(self, *, p: str):
    coordinate_system = COORDINATE_SYSTEMS[int(p)]

    self.execute("G59.3", _lineno())
    self.execute(
        f"G10 L2 P9 X{coordinate_system['x']} Y{coordinate_system['y']}",
        # no z coordiante for now until tool setting works
        # f"G10 L2 P9 X{coordinate_system['x']} Y{coordinate_system['y']} Z{coordinate_system['z']}",
        _lineno(),
    )

    return INTERP_OK


def persist_loaded_tool(self):
    """Persist currently loaded tool."""
    s = linuxcnc.stat()
    s.poll()

    with open("linuxcnc-loaded-tool.txt", "w") as f:
        f.write(str(s.tool_in_spindle))


def load_persisted_tool(self):
    """Load the persisted tool - without running tool change logic."""
    try:
        with open("linuxcnc-loaded-tool.txt") as f:
            tool = int(f.read().strip())
            self.execute(f"M61 Q{tool}", _lineno())
            self.set_tool_parameters()
            self.toolchange_flag = True

            self.execute("G43", _lineno())  # activate tool length compensation

            # NOTE: this is needed to make sure the _current_tool variable has a chance to update
            # when this is used in the context of another subroutine - namely the toolchange one
            yield INTERP_EXECUTE_FINISH
    except Exception as e:
        return str(e)
