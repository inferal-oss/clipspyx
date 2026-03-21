from collections import defaultdict


class OrderingError(Exception):
    pass


class OrderingCycleError(OrderingError):
    pass


class _UnionFind:
    """Union-Find for building concurrent equivalence classes."""

    def __init__(self):
        self._parent = {}

    def find(self, x):
        if x not in self._parent:
            self._parent[x] = x
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]
            x = self._parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[rb] = ra

    def groups(self):
        result = defaultdict(set)
        for x in self._parent:
            result[self.find(x)].add(x)
        return dict(result)


def compute_ordering_salience(pending, leaf_names=frozenset()):
    """Compute salience values from ordering constraints.

    Args:
        pending: mapping of qualified_name -> (cls, rdef) for all
                 ordering-participating rules
        leaf_names: set of qualified names for rules already built in CLIPS
                    (their computed salience must match their existing value)

    Returns:
        mapping of qualified_name -> salience_value

    Raises:
        OrderingCycleError: if a cycle is detected
        OrderingError: if a target cannot be resolved
    """
    if not pending:
        return {}

    # Build lookup from short class name to qualified name
    short_to_qualified = {}
    for qname, (cls, rdef) in pending.items():
        short = cls.__name__
        if short in short_to_qualified:
            raise OrderingError(
                f"Ambiguous ordering target '{short}': "
                f"both {short_to_qualified[short]} and {qname}")
        short_to_qualified[short] = qname

    def _resolve_target(oc, source_qname):
        """Resolve an OrderingConstraint target to a qualified name."""
        if isinstance(oc.target, str):
            if oc.target in short_to_qualified:
                return short_to_qualified[oc.target]
            raise OrderingError(
                f"Rule {source_qname}: ordering target '{oc.target}' "
                f"not found among defined rules")
        # target is a class reference
        target_qname = f"{oc.target.__module__}.{oc.target.__name__}"
        if target_qname not in pending:
            # Check by short name as fallback
            short = oc.target.__name__
            if short in short_to_qualified:
                return short_to_qualified[short]
            raise OrderingError(
                f"Rule {source_qname}: ordering target "
                f"'{oc.target.__name__}' not found among defined rules")
        return target_qname

    # Step 1: Build concurrent groups
    uf = _UnionFind()
    for qname in pending:
        uf.find(qname)  # ensure every rule is in the union-find

    for qname, (cls, rdef) in pending.items():
        for oc in rdef.ordering:
            if oc.kind == 'concurrent':
                target_qname = _resolve_target(oc, qname)
                uf.union(qname, target_qname)

    # Step 2: Validate no rule is both concurrent and before/after same target
    for qname, (cls, rdef) in pending.items():
        for oc in rdef.ordering:
            if oc.kind in ('before', 'after'):
                target_qname = _resolve_target(oc, qname)
                if uf.find(qname) == uf.find(target_qname):
                    raise OrderingError(
                        f"Rule {qname}: cannot be both concurrent with "
                        f"and {oc.kind} '{target_qname}'")

    # Step 3: Build DAG on contracted nodes (concurrent group representatives)
    # Edge: rep_a -> rep_b means "group a fires before group b" (higher salience)
    edges = defaultdict(set)
    all_reps = set()
    for qname in pending:
        all_reps.add(uf.find(qname))

    for qname, (cls, rdef) in pending.items():
        for oc in rdef.ordering:
            if oc.kind == 'concurrent':
                continue
            target_qname = _resolve_target(oc, qname)
            src_rep = uf.find(qname)
            tgt_rep = uf.find(target_qname)
            if oc.kind == 'before':
                # "this rule fires before target" -> src has higher salience
                edges[src_rep].add(tgt_rep)
            elif oc.kind == 'after':
                # "this rule fires after target" -> target has higher salience
                edges[tgt_rep].add(src_rep)

    # Step 4: Detect cycles and topological sort (Kahn's algorithm)
    in_degree = defaultdict(int)
    for rep in all_reps:
        in_degree.setdefault(rep, 0)
    for src, targets in edges.items():
        for tgt in targets:
            in_degree[tgt] += 1

    queue = [rep for rep in all_reps if in_degree[rep] == 0]
    layers = {}  # rep -> layer index (0 = fires first = highest salience)
    processed = 0

    current_layer = 0
    while queue:
        next_queue = []
        for rep in queue:
            layers[rep] = current_layer
            processed += 1
            for tgt in edges.get(rep, ()):
                in_degree[tgt] -= 1
                if in_degree[tgt] == 0:
                    next_queue.append(tgt)
        queue = next_queue
        if queue:
            current_layer += 1

    if processed < len(all_reps):
        # Find the cycle for error reporting
        remaining = [rep for rep in all_reps if rep not in layers]
        cycle_path = _find_cycle(remaining, edges)
        raise OrderingCycleError(
            f"Ordering cycle detected: {' -> '.join(cycle_path)}")

    # Step 5: Assign salience values
    # Anchor to leaf nodes (already-built rules whose CLIPS salience
    # cannot change). Formula: salience = offset - layer.
    # For a leaf at layer L with existing salience S: offset = S + L.
    # Use the max offset across all leaves so all values stay consistent.
    offset = 0
    for qname in leaf_names:
        if qname in pending:
            cls, rdef = pending[qname]
            existing = rdef.salience if rdef.salience is not None else 0
            rep = uf.find(qname)
            candidate = existing + layers[rep]
            if candidate > offset:
                offset = candidate

    result = {}
    for qname in pending:
        rep = uf.find(qname)
        result[qname] = offset - layers[rep]

    return result


def _find_cycle(nodes, edges):
    """Find a cycle among the given nodes for error reporting."""
    node_set = set(nodes)
    visited = set()
    path = []
    path_set = set()

    def dfs(node):
        if node in path_set:
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        if node in visited:
            return None
        visited.add(node)
        path.append(node)
        path_set.add(node)
        for neighbor in edges.get(node, ()):
            if neighbor in node_set:
                result = dfs(neighbor)
                if result is not None:
                    return result
        path.pop()
        path_set.discard(node)
        return None

    for node in nodes:
        if node not in visited:
            cycle = dfs(node)
            if cycle is not None:
                return cycle

    return nodes[:2] + [nodes[0]]  # fallback
