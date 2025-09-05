import json
import sys


def form_blocks(instructions) -> list:
    if not instructions:
        # print("Instructions is empty")
        return

    current_block = []
    # indicates end of a block when last instruction had a terminator
    terminators = {"br", "ret"}
    first_inst = instructions[0]
    current_block.append(first_inst)
    for i in range(1, len(instructions)):
        last_inst = instructions[i - 1]
        curr_inst = instructions[i]
        # label starts a new block
        # currently a leader(new block) or last instruction was a terminator(new block)
        if "label" in curr_inst or (
            "op" in last_inst and last_inst["op"] in terminators
        ):
            yield current_block
            current_block = [curr_inst]
        else:
            current_block.append(curr_inst)
    yield current_block


def get_cfg(block_map) -> dict:
    the_cfg = {}
    block_names = list(block_map.keys())
    for index, current_label in enumerate(block_names):
        block = block_map[current_label]
        last = block[-1]
        if "op" in last:
            match last["op"]:
                case "br":
                    the_cfg[current_label] = last.get("labels", [])
                case "ret":
                    the_cfg[current_label] = []
                case _:
                    if index + 1 < len(block_names):
                        next_label = block_names[index + 1]
                        the_cfg[current_label] = [next_label]
                    else:
                        the_cfg[current_label] = []
        else:
            if index + 1 < len(block_names):
                next_label = block_names[index + 1]
                the_cfg[current_label] = [next_label]
            else:
                the_cfg[current_label] = []

    return the_cfg


def gen_dot(func_name, cfg_map, block_map) -> str:
    dot_script = f'digraph "{func_name}"{{\n'
    # squares maybe
    # dot_script += "     node [shape=box];\n"

    # define nodes for basic blocks
    for name in block_map:
        dot_script += f'     "{name}";\n'

    # define edges based on cfg
    for name, successors in cfg_map.items():
        # print(f"\nName in cfg_map:\n{name}\n\nSuccessors in cfg_map:\n{successors}\n")
        for successor in successors:
            # print(f"\nSuccessor in successors:\n{successor}\n")
            dot_script += f'     "{name}" -> "{successor}";\n'

    dot_script += "}\n"
    return dot_script


def mycfg() -> None:
    # load JSON from stdin
    prog = json.load(sys.stdin)
    funcs = prog["functions"]
    # loading the first function, for now
    func_instrs = funcs[0]["instrs"]
    # name of the function (default main)
    func_name = funcs[0]["name"]

    # basic blocks generator
    basic_blocks_gen = form_blocks(func_instrs)

    blocks_map = {}

    try:
        first_block = next(basic_blocks_gen)
        blocks_map[func_name] = first_block
    except StopIteration:
        pass

    for block in basic_blocks_gen:
        first_inst = block[0]
        if "label" in first_inst:
            blocks_map[first_inst["label"]] = [block]

    # print("Block mapping:\n")
    # for label, block in blocks_map.items():
    # print(f"--- Block for label '{label}' ---")
    # for instr in block:
    # print(f"{instr}\n")

    # create cfg
    new_cfg = get_cfg(blocks_map)
    # print("Control Flow Graph (CFG):\n")
    # for label, next_inst in new_cfg.items():
    # print(f"Block '{label}' -> Next Instruction: {next_inst}")

    dot_string = gen_dot(func_name, new_cfg, blocks_map)
    print(dot_string)

    # print(f"\nThe digraph:\n{dot_string}")
    return


if __name__ == "__main__":
    mycfg()
