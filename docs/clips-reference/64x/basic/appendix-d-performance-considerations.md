# Appendix D: Performance Considerations

This appendix explains various techniques that the user can apply to a CLIPS program to maximize performance. Included are discussions of pattern ordering in rules, use of deffunctions in lieu of non‑overloaded generic functions, parameter restriction ordering in generic function methods, and various approaches to improving the speed of message‑passing and reading slots of instances.

## D.1 Ordering of Patterns on the LHS

The issues which affect performance of a rule‑based system are considerably different from those which affect conventional programs. This section discusses the single most important issue: the ordering of patterns on the LHS of a rule.

CLIPS is a rule language based on the RETE algorithm which was de­signed to provide very efficient pattern‑matching. In optimizing rules, it is beneficial to have some under­stand­ing of how the pattern‑matcher works.

Prior to initiating execution, each rule is loaded and a network of all patterns that appear on the LHS of any rule is constructed. As facts and instances of reactive classes (referred to collectively as pattern entities) are created, they are filtered through the pattern network. If the pattern entities match any of the patterns in the network, the rules associated with those patterns are partially instantiated. When pattern entities exist that match multiple sequential patterns on the LHS of the rule beginning with the first pattern, variable bindings (if any) across patterns are considered. They are considered from the top to the bottom; i.e., the first pattern on the LHS of a rule is con­sidered, then the second, and so on. If the variable bindings for all patterns are consis­tent with the constraints applied to the variables, the rules are activated and placed on the agenda.

This is a very simple description of what occurs in CLIPS, but it gives the basic idea. A number of important considerations come out of this. Basic pattern‑matching is done by filtering through the pattern network. The time involved in doing this is fairly constant. The slow portion of basic pattern‑matching comes from comparing variable bindings across patterns. Therefore, the single most important performance factor is the ordering of patterns on the LHS of the rule. Unfortunately, there are no hard and fast methods that will al­ways order the patterns properly. There are a few general rules for ordering the patterns.

1\) Most specific to most general. The more wildcards or unbound variables there are in a pattern, the lower it should go. If the rule firing can be controlled by a single pattern, place that pattern first. This technique often is used to provide control structure in an expert system; e.g., some kind of "phase" fact. Putting this kind of pattern first will guarantee that the rest of the rule will not be considered until that pattern exists. This is most effective if the single pattern consists only of literal constraints. If multiple patterns with variable bindings control rule firing, arrange the patterns so the most important variables are bound first and compared as soon as possible to the other pattern constraints. The use of phase facts is not recommended for large programs if they are used solely for controlling the flow of execution (use defmodules instead).

2\) Patterns with the lowest number of occurrences in the fact‑list or instance‑list should go near the top. A large number of patterns of a particular form in the fact‑list or instance‑list can cause numerous partial instantiations of a rule that have to be eliminated by comparing the variable bindings, a slower operation.

3\) Volatile patterns (ones that are retracted and asserted continuously) should go last, particularly if the rest of the patterns are mostly independent. Every time a pattern entity is created, it must be filtered through the network. If a pattern entity causes a partial rule instan­tiation, the variable bindings must be considered. By putting volatile patterns last, the variable bindings only will be checked if all of the rest of the patterns already exist.

These rules are not independent and commonly conflict with each other. At best, they provide some rough guidelines. Since all systems have these characteristics in different proportions, at a glance the most efficient manner of ordering patterns for a given system is not evident. The best approach is to develop the rules with some consideration of ordering, but delay optimization until later in development.

## D.2 Deffunctions versus Generic Functions

Deffunctions execute more quickly than generic function because generic functions must first examine their arguments to determine which methods are applicable. If a generic function has only one method, a deffunction probably would be better. Care should be taken when determining if a particular function truly needs to be overloaded. In addition, if recompiling and relinking CLIPS is not prohibitive, user‑defined external functions are even more efficient than deffunctions. This is because deffunction are interpreted whereas external functions are directly executed.

## D.3 Ordering of Method Parameter Restrictions

When the generic dispatch examines a generic function's method to determine if it is applicable to a particular set of arguments, it examines that method's parameter restrictions from left to right. The programmer can take advantage of this by placing parameter restrictions which are less frequently satisfied than others first in the list. Thus, the generic dispatch can conclude as quickly as possible when a method is not applicable to a generic function call. If a group of restrictions are all equally likely to be satisfied, placing the simpler restrictions first, such as those without queries, will also allow the generic dispatch to conclude more quickly for a method that is not applicable.

## D.4 Instance‑Addresses versus Instance‑Names

COOL allows instances of user‑defined classes to be referenced either by address or by name in functions which manipulate instances, such as message‑passing with the **send** function. However, when an instance is referenced by name, CLIPS must perform an internal lookup to find the instance‑address anyway. If the same instance is going to be manipulated many times, it might be advantageous to store the instance‑address and use that as a reference. This will allow CLIPS to always go directly to the instance.

## D.5 Reading Instance Slots Directly

Normally, message‑passing must be used to read or set a slot of an instance. However, slots can be read directly within instance‑set queries and message‑handlers, and they can be set directly within message‑handlers. Accessing slots directly is significantly faster than message‑passing. Unless message‑passing is required (because of slot daemons), direct access should be used when allowed.
