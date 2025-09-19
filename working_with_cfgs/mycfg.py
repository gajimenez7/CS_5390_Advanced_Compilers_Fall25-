import json
import sys
import argparse
from collections import deque
from collections.abc import Iterator

# cfg generation program


def form_blocks(instructions, debug=False) -> Iterator[list[dict]]:
    if debug:
        print(f"I am passing these instructions\n{instructions}\n")
    if not instructions:
        if debug:
            print("Instructions is empty")
        return

    current_block = []
    # indicates end of a block when last instruction had a terminator
    terminators = {"br", "jmp", "ret"}
    first_inst = instructions[0]
    current_block.append(first_inst)
    for i in range(1, len(instructions)):
        last_inst = instructions[i - 1]
        curr_inst = instructions[i]
        if debug:
            print(f"Last instruction:\n{last_inst}\n")
            print(f"Current instruction:\n{curr_inst}\n")

        # label starts a new block
        # currently a leader(new block)
        if "label" in curr_inst.keys():
            if debug:
                print(f"{curr_inst.keys()}")
                print(
                    "\nLabel found in current instruction...RETURNING CURRENT_BLOCK\n"
                )
            yield current_block
            current_block = [curr_inst]
        # last instruction had a terminator(new block)
        elif "op" in last_inst.keys() and last_inst["op"] in terminators:
            if debug:
                print(f"{last_inst.keys()}")
                print(
                    "\nTerminator found in last instruction...RETURNING CURRENT_BLOCK\n"
                )
            yield current_block
            current_block = [curr_inst]
        else:
            current_block.append(curr_inst)
    if debug:
        print("\nFINISHED CREATING BASIC BLOCKS, NO MORE INSTRUCTIONS\n")
    yield current_block


def map_blocks(basic_blocks, debug=False) -> dict:
    unamed_block_label = "b"
    ntb_map = {}

    for i, block in enumerate(basic_blocks):
        # start of basic block
        if debug:
            print(f"\nBlock # {i + 1}:\n")
        for inst in block:
            # instruction within basic block
            if debug:
                print(f"{inst}")

            # check for label first
            if "label" in inst.keys():
                if debug:
                    print(f"\nBlock contains a label: {inst['label']}\n")
                ntb_map[inst["label"]] = block
                break
            # if there is a branch operation instruction
            elif "op" in inst.keys() and inst["op"] == "br":
                if debug:
                    print(f"\nThere is a branch instruction: {inst['args'][0]}")
                ntb_map[inst["args"][0]] = block
                break
            else:
                label_name = unamed_block_label + str(i)
                if debug:
                    print(f"\nThis is an unamed block: {label_name}")
                ntb_map[label_name] = block
                break

        # new line end of block formatting
        if debug:
            print("\n")
    if debug:
        print(f"The finished mapping:\n{ntb_map}")
    return ntb_map


def get_cfg(block_map, debug=False) -> dict:
    the_cfg = {}
    block_names = list(block_map.keys())
    if debug:
        print(f"The block names:\n'{block_names}'\n")
    for index, current_label in enumerate(block_names):
        block = block_map[current_label]
        last_instruction = block[-1]

        if debug:
            print(f"The block for '{current_label}':\n{block}\n")

        # if "op" in last_instruction:
        if debug:
            print(
                f"Operator in the last instruction...\nLast Instruction:\n{last_instruction}"
            )
        match last_instruction["op"]:
            # branch instruction
            case "br":
                if debug:
                    print("Branch case...")
                    print(
                        f"Adding '{current_label}' key to '{last_instruction.get('labels', [])}' value\n"
                    )
                the_cfg[current_label] = last_instruction.get("labels", [])
            # return instruction
            case "ret":
                if debug:
                    print("Return case...\n")
                the_cfg[current_label] = []
            # no terminating operations, next block succeeds current label
            case _:
                # is there a next basic block
                if index + 1 < len(block_names):
                    if debug:
                        print("No terminators...")
                        print(
                            f"Adding '{current_label}' key to '{block_names[index + 1]}' value\n"
                        )
                    next_label = block_names[index + 1]
                    the_cfg[current_label] = [next_label]
                # no more basic blocks, we are the last basic block
                else:
                    if debug:
                        print(
                            f"Nothing comes next! Adding empty list to '{current_label}'\n"
                        )
                    the_cfg[current_label] = []

    if debug:
        print(f"The final cfg:\n{the_cfg}\n")
    return the_cfg


def gen_dot(cfg, debug=False) -> str:
    dot_script = "digraph {\n"
    # define nodes based on cfg
    for name in cfg.keys():
        dot_script += f'     "{name}";\n'

    # define edges based on cfg
    for name, successors in cfg.items():
        if debug:
            print(
                f"\nName in cfg_map:\n{name}\n\nSuccessors in cfg_map:\n{successors}\n"
            )
        for successor in successors:
            if debug:
                print(f"\nSuccessor in successors:\n{successor}\n")
            dot_script += f'     "{name}" -> "{successor}";\n'

    dot_script += "}\n"
    return dot_script


# working with cfgs


def get_path_length(cfg, entry, debug=False) -> tuple[dict, dict]:
    """
    desc: computes shortest path length (in edges)
          from entry node to each node in CFG BFS

    param: cfg(dict)  = mapping{node: [successors]}
    param: entry(str) = starting node

    returns: dict {node:distance from entry}
    """

    dist_map = {}
    dist_map = {i: -1 for i in cfg}
    preds = {}
    preds = {i: None for i in cfg}
    dist_map[entry] = 0
    node_queue = deque()
    visited = set()

    node_queue.append(entry)
    visited.add(entry)

    if debug:
        print(f"Entry param:\n{entry}\n\nItems:\n{cfg.items()}\n")
        print(f"Node queue:\n{node_queue}\n\nVisited set:\n{visited}\n")

    while len(node_queue) != 0:
        current_node = node_queue.popleft()
        if debug:
            print(f"Node queue:\n{node_queue}\n\nVisited set:\n{visited}\n")

        for successor in cfg[current_node]:
            if dist_map[successor] == -1:
                dist_map[successor] = dist_map[current_node] + 1
                preds[successor] = current_node
                node_queue.append(successor)
            if debug:
                print(f"The successor:\n{successor}\n")
            if successor not in visited:
                visited.add(successor)
                node_queue.append(successor)
        if debug:
            print(f"The distance map so far:\n{dist_map}\n")

    return dist_map, preds


def reverse_postorder(cfg, entry, debug=False) -> list[str]:
    """
    desc: compute RPO for a CFG

    param: cfg(dict)  = mapping{node: [successors]}
    param: entry(str) = starting node

    returns: list[nodes in reverse post order]
    """

    visited = set()
    po_list = []

    def depth_first_search_helper(a_node):
        visited.add(a_node)
        if a_node in cfg:
            for successor in cfg[a_node]:
                if successor not in visited:
                    depth_first_search_helper(successor)
        po_list.append(a_node)
        if debug:
            print(f"The node:\n{a_node}\n\nThe po list:\n{po_list}\n")

    # post order traveresal first
    depth_first_search_helper(entry)
    rpo_list = po_list[::-1]
    if debug:
        print(f"The rpo list:\n{rpo_list}\n")

    return rpo_list


def find_back_edges(cfg, entry, debug=False) -> list[str]:
    """
    desc: find back edges of a CFG using DFS

    param: cfg(dict)  = mapping{node: [successors]}
    param: entry(str) = starting node

    returns: list of edges(u,v) where u -> v is a back edge
    """

    back_edges = []
    visited = set()
    visiting = set()
    unvisited = set(cfg.keys())

    def depth_first_search_helper(a_node):
        unvisited.discard(a_node)
        visiting.add(a_node)
        if a_node in cfg:
            for successor in cfg[a_node]:
                if successor in visiting:
                    if debug:
                        print(f"Found back edge:\n{successor}\n")
                    back_edges.append([a_node, successor])
                elif successor in unvisited:
                    depth_first_search_helper(successor)
            visiting.discard(a_node)
            visited.add(a_node)
        if debug:
            print(f"The node:\n{a_node}\n\nThe back edges list:\n{back_edges}\n")

    depth_first_search_helper(entry)

    return back_edges


def is_reducable(cfg, entry, debug=False) -> bool:
    """
    desc: determine whether a cfg is reducable

    param: cfg(dict)  = mapping{node: [successors]}
    param: entry(str) = starting node

    returns: True/False if cfg is reducable or not

    requires: find_back_edges and reverse_postorder functions
    """
    back_edges = find_back_edges(cfg, entry)

    dominators = find_dominators(cfg, entry)

    if debug:
        print(f"Back edges:\n{back_edges}\n\nDominators:\n{dominators}\n")

    for u, v in back_edges:
        if v not in dominators[u]:
            return False

    return True


def find_dominators(cfg, entry_node, debug=False) -> dict:
    dominators = {}
    dominators[entry_node] = {entry_node}

    for a_node in cfg:
        if a_node != entry_node:
            dominators[a_node] = set(cfg.keys())

    while True:
        changed = False

        for a_node in reverse_postorder(cfg, entry_node):
            if a_node == entry_node:
                pass
            new_doms = set(cfg.keys())

            for predecessor in get_path_length(cfg, entry_node)[-1]:
                new_doms = new_doms.intersection(dominators[predecessor])

            new_doms.add(a_node)

            if new_doms != dominators[a_node]:
                dominators[a_node] = new_doms
                changed = True

        if not changed:
            break

    return dominators


def mycfg(debug_mode: bool, file_path: str = "") -> None:
    # load JSON from stdin
    prog = json.load(sys.stdin)
    funcs = prog["functions"]
    # loading the just the first function, for now
    func_instrs = funcs[0]["instrs"]

    # basic blocks generator
    basic_blocks_gen = form_blocks(func_instrs, debug_mode)

    # mapping blocks from label/ branch to succsessor
    name_to_block = map_blocks(basic_blocks_gen, debug_mode)

    # create cfg
    new_cfg = get_cfg(name_to_block, debug_mode)

    if debug_mode:
        print(f"The cfg:\n{new_cfg}\n\n")

    entry_node = list(new_cfg.keys())[0]
    # get shortest path length
    # get_path_length(new_cfg, new_cfg.keys()[0], debug_mode)
    get_path_length(new_cfg, entry_node, debug_mode)

    # reverse post order
    reverse_postorder(new_cfg, entry_node, debug_mode)

    # find back edges
    find_back_edges(new_cfg, entry_node, debug_mode)

    # is reducable
    reduceable = is_reducable(new_cfg, entry_node, True)

    if True:
        print(f"Is reducable: {reduceable}\n")

    dot_string = gen_dot(new_cfg, debug_mode)
    print(dot_string)

    if debug_mode:
        print(f"\nThe digraph:\n{dot_string}")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a CFG from bril JSON input")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose output.",
    )
    parser.add_argument(
        "-r",
        "--reduceable",
        action="store_true",
        help="Check if a bril program is reduceable.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Input file to proccess. If not provided, reads from stdin",
    )
    args = parser.parse_args()
    mycfg(args.debug, args.file)
