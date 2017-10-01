import collections
import json
import pickle
import os
import time

# Build the full dependency graph for the provided build raw (json) spec. This
# should be called after the spec has been validated.
def _build_dependency_graph(build_spec):
    dependency_graph = collections.defaultdict(set)
    for rule in build_spec["builds"]:
        dependency_graph[rule["name"]].update(rule.get("deps", []))
    return dependency_graph

# Build a map of build rule name to the rule itself.
def _build_name_rule_mapping(build_spec):
    index = {}
    for rule in build_spec["builds"]:
        index[rule["name"]] = rule
    return index

# Return a mapping of build rule to last build time. This function will attempt
# to read the pickled map from the '.sbsbt' (sbs build times) file. If the file
# is not present, an empty map will be returned.
def _get_last_build_times():
    try:
        return pickle.load(open(".sbsbt"))
    except:
        return {}

# A class representing a build spec.
class BuildSpec:
    # Validate a build spec for correctness. Will return a tuple of
    # <Error, RawSpec>. If error is None, then the file contains a valid build
    # spec and it is safe to pass the returned RawSpec to the BuildSpec
    # constructor. If error is not none, then it will contain a message
    # detailing the parse error.
    @staticmethod
    def Validate(filename):
        raw_spec = json.load(open(filename))
        if "builds" not in raw_spec:
            return "All rules must be inclosed in a 'builds' tag", None

        for rule in raw_spec["builds"]:
            if "name" not in rule:
                return ("Build rule: " + str(rule) + " does not contain a name",
                        None)
            if "command" not in rule:
                return ("Build rule: " + str(rule) + " does not contain a comamnd",
                        None)

        return None, raw_spec

    # Construct with a validated raw spec.
    def __init__(self, raw_spec):
        self._raw_spec = raw_spec
        self._dependency_graph = _build_dependency_graph(self._raw_spec)
        self._build_index = _build_name_rule_mapping(self._raw_spec)
        self._last_built = _get_last_build_times()

    # Return the full dependency graph.
    def DependencyGraph(self):
        return self._dependency_graph

    # Return a sub dependency graph for the provided rule.
    def SubDependencyGraph(self, rule):
        stack = [(rule, dep) for dep in self._dependency_graph.get(rule, [])]
        sub_graph = collections.defaultdict(set)
        while len(stack) != 0:
            r, d = stack.pop()
            sub_graph[r].add(d)
            stack.extend([(d, dd) for dd in self._dependency_graph.get(d, [])])
        return sub_graph

    # Return the full rule for the given name.
    def GetRuleFor(self, name):
        return self._build_index[name]

    # Checks if a given rule is stale, i.e. needs to be rebuilt. A rule is stale
    # if any of the following conditions are met:
    #   - No information about the last build time is available for the rule.
    #   - The rule has no input files registered
    #   - Any of the input files for the rule have been modified after the rule
    #     was last built
    #   - Any of the rules dependencies have been built after the rule was last
    #     built. Since dependencies are processed first, this will handle any
    #     modification made to dependencies.
    def IsStale(self, name):
        # If we have no record of when it was built, then call it stale.
        if name not in self._last_built:
            return True

        # Always build if it has no input files.
        if "input_files" not in self.GetRuleFor(name):
            return True

        # Check for input file changes or stale dependencies.
        input_files = self.GetRuleFor(name)["input_files"]
        last_modified_times = map(os.path.getmtime, input_files)
        any_files_changed = any(last_modified > self._last_built[name]\
                for last_modified in last_modified_times)
        any_stale_deps = any(self._last_built[dep] > self._last_built[name]\
                for dep in self._dependency_graph.get(name, []))
        return any_files_changed or any_stale_deps

    # Update the build time of a rule.
    def BuiltRule(self, name):
        self._last_built[name] = time.time()
        with open(".sbsbt", "w") as f:
            pickle.dump(self._last_built, f)
