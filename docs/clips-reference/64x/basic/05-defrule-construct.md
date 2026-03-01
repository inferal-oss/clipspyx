# Section 5: Defrule Construct

One of the primary methods of representing knowledge in CLIPS are rules. A **rule** is a collec­tion of conditions and the actions to be taken if the conditions are satisfied. The developer of an expert system defines the rules that describe how to solve a problem. Rules execute (or **fire**) based on the existence or non‑existence of facts or instances of user‑defined classes. CLIPS provides the mechanism (the **inference engine**) which attempts to match the rules to the cur­rent state of the system (as represented by the fact‑list and instance‑list) and applies the actions.

Throughout this section, the term **pattern entity** will be used to refer to either a fact or an instance of a user‑defined class.

## 5.1 Defining Rules

Rules are defined using the **defrule** construct.

Syntax

(defrule \<rule-name\> \[\<comment\>\]

\[\<declaration\>\] ; Rule Properties

\<conditional-element\>\* ; Left-Hand Side (LHS)\
=\>\
\<action\>\*) ; Right-Hand Side (RHS)

Redefining a currently existing defrule causes the previous defrule with the same name to be removed even if the new definition has errors in it. The LHS is made up of a series of conditional elements (CEs) that typically consist of pattern conditional elements (or just simply patterns) to be matched against pattern entities. An implicit **and** conditional element always surrounds all the patterns on the LHS. The RHS contains a list of actions to be per­formed when the LHS of the rule is sat­isfied. In addition, the LHS of a rule may also contain declarations about the rule's properties immediately following the rule's name and comment. The arrow (**=\>**) separates the LHS from the RHS. Actions are performed sequentially if, and only if, all condi­tional elements on the LHS are satisfied.

If no conditional elements are on the LHS, the rule will automatically be activated. If no ac­tions are on the RHS, the rule can be activated and fired but nothing will happen.

As rules are defined, they are incrementally reset. This means that CEs in newly defined rules can be satisfied by pattern entities at the time the rule is defined, in addition to pattern entities created after the rule is defined.

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate oav

(slot object)

(slot attribute)

(slot value))

CLIPS\>

(defrule example-rule \"This is an example of a simple rule\"

(oav (object refrigerator)

(attribute light)

(value on))

(oav (object refrigerator)

(attribute door)

(value open))

=\>

(assert (oav (object refrigerator)

(attribute food)

(value spoiled))))

CLIPS\>

(assert (oav (object refrigerator)

(attribute light)

(value on))

(oav (object refrigerator)

(attribute door)

(value open)))

\<Fact-2\>

CLIPS\> (agenda)

0 example-rule: f-1,f-2

For a total of 1 activation.

CLIPS\> (run)

CLIPS\> (facts)

f-1 (oav (object refrigerator) (attribute light) (value on))

f-2 (oav (object refrigerator) (attribute door) (value open))

f-3 (oav (object refrigerator) (attribute food) (value spoiled))

For a total of 3 facts.

CLIPS\>

## 5.2 Basic Cycle Of Rule Execution

Once a knowledge base (in the form of rules) is built and the fact‑list and instance‑list is prepared, CLIPS is ready to execute rules. In a conventional language the programmer explicitly defines the starting point, the stopping point, and the sequence of operations. With CLIPS, the program flow does not need to be defined explicitly. The knowledge (rules) and the data (facts and instances) are separated, and the inference engine pro­vided by CLIPS is used to apply the knowledge to the data. The basic execution cycle is as follows:

a\) If the rule firing limit has been reached or there is no current focus, then execution is halted. Otherwise, the top rule on the agenda of the module that is the current focus is selected for execution. If there are no rules on that agenda, then the current focus is removed from the focus stack and the current focus becomes the next module on the focus stack. If the focus stack is empty, then execution is halted, otherwise step *a* is executed again.

b\) The right‑hand side (RHS) actions of the selected rule are executed. The use of the **return** function on the RHS of a rule may remove the current focus from the focus stack. The number of rules fired is incremented for use with the rule firing limit.

c\) As a result of step b, rules may be **activated** or **deactivated**. Activated rules (those rules whose conditions are currently satisfied) are placed on the **agenda** of the module in which they are defined. The placement on the agenda is determined by the **salience** of the rule and the current **conflict resolution strategy**. Deactivated rules are removed from the agenda. If the activations item is being watched (as a result of the **watch** command), then an informational message will be displayed each time a rule is activated or deactivated.

d\) If **dynamic salience** is being used (see the **set-salience-evaluation** command), the salience values for all rules on the agenda are reevaluated. Repeat the cycle beginning with step a.

## 5.3 Conflict Resolution Strategies

The **agenda** is the list of all rules that have their conditions satisfied (and have not yet been executed). Each module has its own agenda. The agenda acts similar to a stack (the top rule on the agenda is the first one to be executed). When a rule is newly activated, its placement on the agenda is based (in order) on the following factors:

a\) Newly activated rules are placed above all rules of lower salience and below all rules of higher salience.

b\) Among rules of equal salience, the current conflict resolution strategy is used to determine the placement among the other rules of equal salience.

c\) If a rule is activated (along with several other rules) by the same assertion or retraction of a fact, and steps a and b are unable to specify an ordering, then the rule is arbitrarily (*not randomly*) ordered in relation to the other rules with which it was activated. Note, in this respect, the order in which rules are defined has an arbitrary effect on conflict resolution (which is highly dependent upon the current underlying implementation of rules). *Do not* depend upon this arbitrary ordering for the proper execution of your rules.

CLIPS provides seven conflict resolution strategies: depth, breadth, simplicity, complexity, lex, mea, and random. The default strategy is depth. The current strategy can be set by using the **set‑strategy** command (which will reorder the agenda based upon the new strategy).

### 5.3.1 Depth Strategy

Newly activated rules are placed above all rules of the same salience. For example, given that fact‑a activates rule‑1 and rule‑2 and fact‑b activates rule‑3 and rule‑4, then if fact‑a is asserted before fact‑b, rule‑3 and rule‑4 will be above rule‑1 and rule‑2 on the agenda. However, the position of rule‑1 relative to rule‑2 and rule‑3 relative to rule‑4 will be arbitrary.

### 5.3.2 Breadth Strategy

Newly activated rules are placed below all rules of the same salience. For example, given that fact‑a activates rule‑1 and rule‑2 and fact‑b activates rule‑3 and rule‑4, then if fact‑a is asserted before fact‑b, rule‑1 and rule‑2 will be above rule‑3 and rule‑4 on the agenda. However, the position of rule‑1 relative to rule‑2 and rule‑3 relative to rule‑4 will be arbitrary.

### 5.3.3 Simplicity Strategy

Among rules of the same salience, newly activated rules are placed above all activations of rules with equal or higher specificity. The **specificity** of a rule is determined by the number of comparisons that must be performed on the LHS of the rule. Each comparison to a constant or previously bound variable adds one to the specificity. Each function call made on the LHS of a rule as part of the :, =, or test conditional element adds one to the specificity. The boolean functions **and**, **or**, and **not** do not add to the specificity of a rule, but their arguments do. Function calls made within a function call do not add to the specificity of a rule. For example, the following rule

(deftemplate point\
(slot x)\
(slot y)\
(slot z))

(defrule example\
(point (x ?x) (y ?y) (z ?x))\
(test (and (numberp ?x) (\> ?x (+ 10 ?y)) (\< ?x 100)))\
=\>)

has a specificity of 5. The comparison to the constant item, the comparison of ?x to its previous binding, and the calls to the **numberp**, **\<**, and **\>** functions each add one to the specificity for a total of 5. The calls to the **and** and **+** functions do not add to the specificity of the rule.

### 5.3.4 Complexity Strategy

Among rules of the same salience, newly activated rules are placed above all activations of rules with equal or lower specificity.

### 5.3.5 LEX Strategy

Among rules of the same salience, newly activated rules are placed using the OPS5 (an early expert system tool) strategy of the same name. First the recency of the pattern entities that activated the rule is used to determine where to place the activation. Every fact and instance is marked internally with a "time tag" to indicate its relative recency with respect to every other fact and instance in the system. The pattern entities associated with each rule activation are sorted in descending order for determining placement. An activation with a more recent pattern entities is placed before activations with less recent pattern entities. To determine the placement order of two activations, compare the sorted time tags of the two activations one by one starting with the largest time tags. The comparison should continue until one activation's time tag is greater than the other activation's corresponding time tag. The activation with the greater time tag is placed before the other activation on the agenda.

If one activation has more pattern entities than the other activation and the compared time tags are all identical, then the activation with more time tags is placed before the other activation on the agenda. If two activations have the exact same recency, the activation with the higher specificity is placed above the activation with the lower specificity. Unlike OPS5, the *not* conditional elements in CLIPS have pseudo time tags that are used by the LEX conflict resolution strategy. The time tag of a *not* CE is always less than the time tag of a pattern entity, but greater than the time tag of a *not* CE that was instantiated after the *not* CE in question.

As an example, the following six activations have been listed in their LEX ordering (where the \* indicates the presence of a *not* CE). Note that a fact's time tag is not necessarily the same as it's index (since instances are also assigned time tags), but if one fact's index is greater than another facts's index, then it's time tag is also greater. For this example, assume that the time tags and indices are the same.

rule-6: f-1,f-4

rule-5: f-1,f-2,f-3,\*

rule-1: f-1,f-2,f-3

rule-2: f-3,f-1

rule-4: f-1,f-2,\*

rule-3: f-2,f-1

Shown following are the same activations with the fact indices sorted as they would be by the LEX strategy for comparison.

rule-6: f-4,f-1

rule-5: f-3,f-2,f-1,\*

rule-1: f-3,f-2,f-1

rule-2: f-3,f-1

rule-4: f-2,f-1,\*

rule-3: f-2,f-1

### 5.3.6 MEA Strategy

Among rules of the same salience, newly activated rules are placed using the OPS5 strategy of the same name. First the time tag of the pattern entity associated with the first pattern is used to determine where to place the activation. An activation that has a first pattern with a time tag that is greater than time tag of the first pattern of another activation is placed before the other activation on the agenda. If both activations have the same time tag associated with the first pattern, then the LEX strategy is used to determine placement of the activation. Again, as with the CLIPS LEX strategy, negated patterns have pseudo time tags.

As an example, the following six activations have been listed in their MEA ordering (where the \* indicates the presence of a negated pattern).

rule-2: f-3,f-1

rule-3: f-2,f-1

rule-6: f-1,f-4

rule-5: f-1,f-2,f-3,\*

rule-1: f-1,f-2,f-3

rule-4: f-1,f-2,\*

### 5.3.7 Random Strategy

Each activation is assigned a random number that is used to determine its placement among activations of equal salience. This random number is preserved when the strategy is changed so that the same ordering is reproduced when the random strategy is selected again (among activations that were on the agenda when the strategy was originally changed).

 Usage Note

A conflict resolution strategy is an implicit mechanism for specifying the order in which rules of equal salience should be executed. In early expert system tools, this was often the only mechanism provided to specify the order. Because the mechanism is implicit, it's not possible to determine the programmer's original intent simply by looking at the code. Rather than explicitly indicating that rule A should be executed before rule B, the order of execution is implicitly determined by the order in which facts are asserted and the complexity of the rules. The assumption one must make when examining the code is that the original programmer carefully analyzed the rules and followed the necessary conventions so that the rules execute in the appropriate sequence.

Because they require explicit declarations, the preferred mechanisms in CLIPS for ordering the execution of rules are salience and modules. Salience allows one to explicitly specify that one rule should be executed before another rule. Modules allow one to explicitly specify that all of the rules in a particular group (module) should be executed before all of the rules in a different group. Thus, when designing a program the following convention should be followed: if two rules have the same salience, are in the same module, and are activated concurrently, then the order in which they are executed should not matter. For example, the following two rules need correction because they can be activated at the same time, but the order in which they execute matters:

(defrule print-schedules

(classes-scheduled)

=\>

(assert (print-schedules)))

(defrule retry-scheduling

?f \<- (classes-scheduled)

(scheduling-errors)

=\>

(retract ?f)

(assert (retry-scheduling)))

Programmers should also be careful to avoid overusing salience. Trying to unravel the relationships between dozens of salience values can be just as confusing as the implicit use of a conflict resolution strategy in determining rule execution order. It's rarely necessary to use more than five to ten salience values in a well-designed program.

Most programs should use the default conflict resolution strategy of depth. The breadth, simplicity, and complexity strategies are provided largely for academic reasons (i.e. the study of conflict resolution strategies). The lex and mea strategies are provided to help in converting OPS5 programs to CLIPS.

The random strategy is useful for testing. Because this strategy randomly orders activations having the same salience, it is useful in detecting whether the execution order of rules with the same salience effects the program behavior. Before running a program with the random strategy, first seed the random number generator using the **seed**[]{.indexref entry="seed"} function. The same seed value can be subsequently be used if it is necessary to replicate the results of the program run.

## 5.4 LHS Syntax

This section describes the syntax used on the LHS of a rule. The LHS of a CLIPS rule is made up of a series of conditional elements (CEs) that must be satisfied for the rule to be placed on the agenda. There are eight types of conditional elements: **pattern** CEs, **test** CEs, **and** CEs, **or** CEs, **not** CEs, **exists** CEs, **forall** CEs, and **logical** CEs. The **pattern** CE is the most basic and commonly used conditional element. **Pattern** CEs contain constraints that are used to determine if any pattern entities (facts or instances) satisfy the pattern. The **test** CE is used to evaluate expressions as part of the pattern‑matching process. The **and** CE is used to specify that an entire group of CEs must all be satisfied. The **or** CE is used to specify that only one of a group of CEs must be satisfied. The **not** CE is used to specify that a CE must not be satisfied. The **exists** CE is used to test for the occurence of at least one partial match for a set of CEs. The **forall** CE is used to test that a set of CEs is satisfied for every partial match of a specified CE. Finally, the **logical** CE allows assertions of facts and the creation of instances on the RHS of a rule to be logically dependent upon pattern entities matching patterns on the LHS of a rule (truth maintenance).

Syntax

\<conditional-element\> ::= \<pattern-CE\> \|

\<assigned-pattern-CE\> \|

\<not-CE\> \|

\<and-CE\> \|

\<or-CE\> \|

\<logical-CE\> \|

\<test-CE\> \|

\<exists-CE\> \|

\<forall-CE\>

### 5.4.1 Pattern Conditional Element

**Pattern conditional elements** consist of a collection of field constraints, wildcards, and variables which are used to constrain the set of facts or instances which match the pattern CE. A pattern CE is satisfied by each and every pattern entity that satisfies its constraints. **Field constraints** are a set of constraints that are used to test a single field or slot of a pattern entity. A field constraint may consist of only a single literal constraint:literal;, however, it may also consist of several constraints connected together. In addition to literal constraints, CLIPS provides three other types of constraints: connective constraints, predicate constraints, and return value constraints. Wildcards are used within pattern CEs to indicate that a single field or group of fields can be matched by anything. Variables are used to store the value of a field so that it can be used later on the LHS of a rule in other conditional elements or on the RHS of a rule as an argument to an action.

The first field of any pattern *must* be a symbol and can not use any other constraints. This first field is used by CLIPS to determine if the pattern applies to an ordered fact, a template fact, or an instance. The symbol *object* is reserved to indicate an object pattern. Any other symbol used must correspond to a deftemplate name (or an implied deftemplate will be created). Slot names must also be symbols and cannot contain any other constraints.

For object and deftemplate patterns, a single field slot can only contain one field constraint and that field constraint must only be able to match a single field (no multifield wildcards or variables). A multifield slot can contain any number of field constraints.

#### 5.4.1.1 Literal Constraints

The most basic constraint that can be used in a pattern CE is one which precisely defines the exact value that will match a field. This is called a **literal constraint**. A **literal pattern CE** consists entirely of constants such as floats, integers, symbols, strings, and instance names. It does not contain any variables or wildcards. All constraints in a literal pattern must be matched exactly by all fields of a pattern entity.

Syntax

An ordered pattern conditional element containing only literals has the following basic syntax:

(\<constant-1\> \... \<constant-n\>)

A deftemplate pattern conditional element containing only literals has the following basic syntax:

(\<deftemplate-name\> (\<slot-name-1\> \<constant-1\>)\
•\
•\
•\
(\<slot-name-n\> \<constant-n\>))

Example 1

CLIPS\> (clear)

CLIPS\>

(defrule rgb-primary

(colors rgb primary red green blue)

=\>)

CLIPS\> (assert (colors ryb secondary purple orange green))

\<Fact-1\>

CLIPS\> (assert (colors rgb primary red green blue))

\<Fact-2\>

CLIPS\> (agenda)

0 rgb-primary: f-2

For a total of 1 activation.

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(multislot name)

(slot age))

CLIPS\>

(defrule Find-Joe-Bob

(person (name Joe Bob Green) (age 20))

=\>)

CLIPS\> (assert (person (name Joe Bob Green) (age 20)))

\<Fact-1\>

CLIPS\> (assert (person (name Ann Green) (age 34)))

\<Fact-2\>

CLIPS\> (agenda)

0 Find-Joe-Bob: f-1

For a total of 1 activation.

CLIPS\>

Example 3

CLIPS\> (clear)

CLIPS\>

(defrule approved

(credit-score at-least 720)

(down-payment-percent at-least 0.20)

(monthly-debt-percent no-more-than 0.36)

=\>

(assert (loan-approved)))

CLIPS\> (watch activations)

CLIPS\> (assert (down-payment-percent at-least 0.20))

\<Fact-1\>

CLIPS\> (assert (credit-score at-least 720))

\<Fact-2\>

CLIPS\> (assert (monthly-debt-percent no-more-than 0.36))

==\> Activation 0 approved: f-2,f-1,f-3

\<Fact-3\>

CLIPS\> (watch facts)

CLIPS\> (run)

==\> f-4 (loan-approved)

CLIPS\> (unwatch all)

CLIPS\>

#### 5.4.1.2 Wildcards Single‑ and Multifield

CLIPS has two **wildcard** symbols that may be used to match fields in a pat­tern. CLIPS in­terprets these wildcard symbols as standing in place of some part of a pattern entity. The **single‑field wild­card**, denoted by a question mark character (?), matches any value stored in exactly one field in the pattern entity. The **multifield wildcard**, denoted by a dollar sign followed by a question mark (\$?), matches any value in *zero* or more fields in a pattern entity. Single‑field and multifield wildcards may be combined in a single pattern in any combination. It is illegal to use a multifield wildcard in a single field slot of a deftemplate or object pattern. By default, an unspecified single‑field slot in a deftemplate/object pattern is matched against an implied single‑field wildcard. Similarly, an unspecified multifield slot in a deftemplate/object pattern is matched against an implied multifield‑wildcard.

Syntax

An ordered pattern conditional element containing only literals and wildcards has the following basic syntax:

(\<constraint-1\> \... \<constraint-n\>)

where

\<constraint\> ::= \<constant\> \| ? \| \$?

A deftemplate pattern conditional element containing only literals and wildcards has the following basic syntax:

> (\<deftemplate-name\> (\<slot-name-1\> \<constraint-1\>)\
> •\
> •\
> •\
> (\<slot-name-n\> \<constraint-n\>))

Example 1

CLIPS\> (clear)

CLIPS\>

(defrule grocery-list-has-milk

(grocery-list \$? milk \$?)

=\>)

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (assert (grocery-list bread onions tomatoes cheese))

\<Fact-2\>

CLIPS\> (agenda)

0 grocery-list-has-milk: f-1

For a total of 1 activation.

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(defrule at-least-3-items

(grocery-list ? ? ? \$?)

=\>)

CLIPS\> (assert (grocery-list apple pears))

\<Fact-1\>

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-2\>

CLIPS\> (assert (grocery-list bread onions tomatoes cheese))

\<Fact-3\>

CLIPS\> (agenda)

0 at-least-3-items: f-3

0 at-least-3-items: f-2

For a total of 2 activations.

CLIPS\>

Example 3

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(multislot name)

(slot age))

CLIPS\>

(defrule match-all-persons

(person)

=\>)

CLIPS\> (assert (person (name Joe Bob Green) (age 20)))

\<Fact-1\>

CLIPS\> (assert (person (name Ann Green) (age 34)))

\<Fact-2\>

CLIPS\> (agenda)

0 match-all-persons: f-2

0 match-all-persons: f-1

For a total of 2 activations.

CLIPS\>

Example 4

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(multislot name)

(slot age))

CLIPS\>

(defrule match-two-names

(person (name ? ?))

=\>)

CLIPS\>

(defrule match-three-names

(person (name ? ? ?))

=\>)

CLIPS\> (assert (person (name Joe Bob Green) (age 20)))

\<Fact-1\>

CLIPS\> (assert (person (name Martin Brown) (age 20)))

\<Fact-2\>

CLIPS\> (assert (person (name Frank Samuel Jones Jr.) (age 28)))

\<Fact-3\>

CLIPS\> (agenda)

0 match-two-names: f-2

0 match-three-names: f-1

For a total of 2 activations.

CLIPS\>

Example 5

CLIPS\> (clear)

CLIPS\>

(deftemplate person\
(multislot name)

(slot age))

CLIPS\>

(defrule last-name-brown

(person (name \$? Brown))

=\>)

CLIPS\>

(defrule name-contains-ann

(person (name \$? Ann \$?))

=\>)

CLIPS\> (assert (person (name Martin Brown) (age 20)))

\<Fact-1\>

CLIPS\> (assert (person (name Ann Green) (age 34)))

\<Fact-2\>

CLIPS\> (assert (person (name Sue Ann Brown) (age 20)))

\<Fact-3\>

CLIPS\> (agenda)

0 last-name-brown: f-3

0 name-contains-ann: f-3

0 name-contains-ann: f-2

0 last-name-brown: f-1

For a total of 4 activations.

CLIPS\>

#### 5.4.1.3 Variables Single‑ and Multifield

Wildcard symbols replace portions of a pattern and accept any value. The value of the field being replaced may be captured in a **variable** for comparison, display, or other manipulations. This is done by directly following the wildcard symbol with a variable name.

Syntax

Expanding on the syntax definition given in section 5.4.1.2 now gives:

\<constraint\> ::= \<constant\> \| ? \| \$? \|

\<single-field-variable\> \|

\<multifield-variable\>

\<single-field-variable\> ::= ?\<variable-symbol\>

\<multifield-variable\> ::= \$?\<variable-symbol\>

The term \<variable‑symbol\> is similar to a symbol, except that it must start with an alphabetic char­acter. Double quotes are not allowed as part of a variable name; i.e. a string cannot be used for a variable name. The rules for pattern‑matching are similar to those for wildcard symbols. On its first appearance, a variable acts just like a wildcard in that it will bind to any value in the field(s). However, later appearances of the variable require the field(s) to match the binding of the variable. The binding will only be true within the scope of the rule in which it occurs. Each rule has its own list of variable names with their associated values; thus, variables are local to a rule. Bound vari­ables can be passed to external functions. The \$ operator has special significance on the LHS as a pattern‑matching operator to indicate that zero or more fields need to be matched. In other places (such as the RHS of a rule), the \$ in front of a variable indicates that sequence expansion should take place before calling the function. Thus, when passed as parameters in function calls (either on the LHS or RHS of a rule), multifield variables should not be preceded by the \$ (unless sequence expansion is desired). All other uses of a multifield variable on the LHS of a rule, however, should use the \$. It is illegal to use a multifield variable in a single field slot of a deftemplate/object pattern.

Example 1

CLIPS\> (clear)

CLIPS\>

(defrule grocery-list-has-milk

(grocery-list ?id \$?b milk \$?e)

=\>

(println \"List \" ?id \" has milk and \" (create\$ ?b ?e)))

CLIPS\> (assert (grocery-list #1 milk eggs cheese))

\<Fact-1\>

CLIPS\> (assert (grocery-list #2 bread onions tomatoes cheese))

\<Fact-2\>

CLIPS\> (run)

List #1 has milk and (eggs cheese)

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(multislot name)

(slot age))

CLIPS\>

(defrule print-person

(person (name \$?name) (age ?age))

=\>

(println (implode\$ ?name) \" is \" ?age \" years old\"))

CLIPS\> (assert (person (name Ann Green) (age 34)))

\<Fact-1\>

CLIPS\> (assert (person (name Sue Ann Brown) (age 20)))

\<Fact-2\>

CLIPS\> (run)

Sue Ann Brown is 20 years old

Ann Green is 34 years old

CLIPS\>

Example 3

CLIPS\> (clear)

CLIPS\>

(defrule down-payment-percent

(loan-amount ?la)

(available-down-payment ?adp)

=\>

(bind ?dpp (/ ?adp ?la))

(assert (down-payment-percent ?dpp)))

CLIPS\> (assert (loan-amount 100000))

\<Fact-1\>

CLIPS\> (assert (available-down-payment 25000))

\<Fact-2\>

CLIPS\> (agenda)

0 down-payment-percent: f-1,f-2

For a total of 1 activation.

CLIPS\> (watch rules)

CLIPS\> (watch facts)

CLIPS\> (run)

FIRE 1 down-payment-percent: f-1,f-2

==\> f-3 (down-payment-percent 0.25)

CLIPS\> (unwatch all)

CLIPS\>

Once the initial binding of a variable occurs, all references to that variable have to match the value that the first binding matched. This applies to both single‑ and multi­field variables. It also applies across patterns.

Example 4

CLIPS\> (clear)

CLIPS\>

(defrule duplicate-item

(grocery-list ?id \$? ?item \$? ?item \$?)

=\>

(println \"List \" ?id \" has duplicate item \" ?item))

CLIPS\> (assert (grocery-list #1 milk eggs cheese))

\<Fact-1\>

CLIPS\> (assert (grocery-list #2 bread onions bread cheese cheese))

\<Fact-2\>

CLIPS\> (run)

List #2 has duplicate item bread

List #2 has duplicate item cheese

CLIPS\>

#### 5.4.1.4 Connective Constraints

Three **connective constraints** are available for connecting individual constraints and variables to each other. These are the **&** (and), **\|** (or), and **\~** (not) connective constraints. The **&** constraint is satisfied if the two adjoining constraints are satisfied. The **\|** constraint is satisfied if either of the two adjoining constraints is satisfied. The **\~** constraint is satisfied if the following constraint is not satisfied. Multiple connective constraints can be chained together. The **\~** constraint has highest precedence, followed by the **&** constraint, followed by the **\|** constraint. Otherwise, evaluation of multiple constraints can be considered to occur from left to right. There is one exception to the precedence rules that applies to the binding occurrence of a variable. If the first constraint is a variable followed by an **&** connective constraint, then the first constraint is treated as a separate constraint which also must be satisified. Thus the constraint ?x&red\|blue is treated as *?x &* *red\|blue* rather than *?x&red \| blue* as the normal precedence rules would indicate.

Syntax

Expanding on the syntax definition given in section 5.4.1.3 now gives:

\<constraint\> ::= ? \| \$? \| \<connected-constraint\>

\<connected-constraint\>\
::= \<single-constraint\> \|\
\<single-constraint\> & \<connected-constraint\> \|\
\<single-constraint\> **\|** \<connected-constraint\>

\<single-constraint\> ::= \<term\> \| \~\<term\>

\<term\> ::= \<constant\> \|\
\<single-field-variable\> \|\
\<multifield-variable\>

Note that the vertical bar in the \"\<single-constraint\> \| \<connected-constraint\>\" non-terminal choice is the **\|** character (which must be included in the text of the constraint) and does not indicate a choice between multiple BNF terms.

The **&** constraint typically is used only in conjunction with other constraints or variable bindings. Notice that connective constraints may be used together and/or with variable bindings. If the first term of a connective constraint is the first occurrence of a variable name, then the field will be constrained only by the remaining field constraints. The variable will be bound to the value of the field. If the variable has been bound previously, it is considered an additional con­straint along with the remaining field constraints; i.e., the field must have the same value already bound to the variable and must satisfy the field constraints.

Example 1

CLIPS\> (clear)

CLIPS\>

(defrule dairy-product

(grocery-list \$? milk \| butter \| cream \$?)

=\>

(println \"Grocery list contains dairy product\"))

CLIPS\>

(defrule non-dairy-product

(grocery-list \$? \~milk&\~butter&\~cream \$?)

=\>

(println \"Grocery list contains non-dairy product\"))

CLIPS\> (assert (grocery-list butter eggs cream bread salt))

\<Fact-1\>

CLIPS\> (agenda)

0 non-dairy-product: f-1

0 non-dairy-product: f-1

0 non-dairy-product: f-1

0 dairy-product: f-1

0 dairy-product: f-1

For a total of 5 activations.

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(defrule dairy-product

(grocery-list \$? ?product&milk\|butter\|cream \$?)

=\>

(println \"Dairy product: \" ?product))

CLIPS\>

(defrule non-dairy-product

(grocery-list \$? ?product&\~milk&\~butter&\~cream \$?)

=\>

(println \"Non-dairy product: \" ?product))

CLIPS\> (assert (grocery-list butter eggs cream bread salt))

\<Fact-1\>

CLIPS\> (agenda)

0 dairy-product: f-1

0 non-dairy-product: f-1

0 dairy-product: f-1

0 non-dairy-product: f-1

0 non-dairy-product: f-1

For a total of 5 activations.

CLIPS\> (run)

Dairy product: butter

Non-dairy product: eggs

Dairy product: cream

Non-dairy product: bread

Non-dairy product: salt

CLIPS\>

Example 3

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(multislot name))

CLIPS\>

(defrule may-be-related

(person (name \$?first1 ?last))

(person (name \$?first2&\~\$?first1 ?last))

=\>

(println (implode\$ ?first1) \" \" ?last \" may be related to \"

(implode\$ ?first2) \" \" ?last \".\"))

CLIPS\> (assert (person (name Joe Bob Green)))

\<Fact-1\>

CLIPS\> (assert (person (name Martin Brown)))

\<Fact-2\>

CLIPS\> (assert (person (name Sue Ann Brown)))

\<Fact-3\>

CLIPS\> (agenda)

0 may-be-related: f-3,f-2

0 may-be-related: f-2,f-3

For a total of 2 activations.

CLIPS\> (run)

Sue Ann Brown may be related to Martin Brown.

Martin Brown may be related to Sue Ann Brown.

CLIPS\>

#### 5.4.1.5 Predicate Constraints

CLIPS allows the use of a **predicate constraint** to restrict a field based on the value returned by a function call. The predicate constraint allows a **predicate function** (one returning the symbol FALSE for unsatisfied and a non‑FALSE value for satisfied) to be called during the pattern‑matching process. If the predicate function returns a non‑FALSE value, the constraint is satisfied. If the predicate function returns the symbol FALSE, the constraint is not satisfied. A predicate constraint is invoked by following a colon with a function call to a predicate function. Typically, predicate constraints are used in conjunction with a connective constraint and a variable binding (i.e. you have to bind the variable to be tested and then connect it to the predicate constraint).

Basic Syntax

:\<function-call\>

Syntax

Expanding on the syntax definition given in section 5.4.1.4 now gives:

\<term\> ::= \<constant\> \|

\<single-field-variable\> \|

\<multifield-variable\> \|

:\<function-call\>

Multiple predicate constraints may be used to constrain a single field. CLIPS provides several predefined predicate functions and users may also create their own. Although any function may be called by the predicate constraint, unless the function returns FALSE for some arguments and a non-FALSE value for other arguments, the predicate constraint will either always fail or always succeed.

Example 1

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age))

CLIPS\>

(defrule adult

(person (age ?age&:(\>= ?age 18)))

=\>)

CLIPS\>

(assert (person (name John) (age 20)) ; f-1

(person (name Sally) (age 18)) ; f-2

(person (name Bill) (age 14))) ; f-3

\<Fact-3\>

CLIPS\> (agenda)

0 adult: f-2

0 adult: f-1

For a total of 2 activations.

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(multislot attributes))

CLIPS\>

(defrule not-tall

(person (attributes \$?a&\~:(member\$ tall ?a)))

=\>)

CLIPS\>

(assert (person (name John) (attributes tall thin)) ; f-1

(person (name Greg) (attributes short stout)) ; f-2

(person (name Jill) (attributes young tall))) ; f-3

\<Fact-3\>

CLIPS\> (agenda)

0 not-tall: f-2

For a total of 1 activation.

CLIPS\>

Example 3

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age))

CLIPS\>

(defrule teenager

(person (age ?age&:(\>= ?age 13)&:(\<= ?age 19)))

=\>)

CLIPS\>

(assert (person (name John) (age 20)) ; f-1

(person (name Sally) (age 18)) ; f-2

(person (name Bill) (age 14))) ; f-3

\<Fact-3\>

CLIPS\> (agenda)

0 teenager: f-3

0 teenager: f-2

For a total of 2 activations.

CLIPS\>

Example 4

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age))

CLIPS\>

(defrule older

(person (age ?age1))

(person (age ?age2&:(\> ?age1 ?age2)))

=\>)

CLIPS\>

(assert (person (name John) (age 20)) ; f-1

(person (name Sally) (age 18)) ; f-2

(person (name Bill) (age 14))) ; f-3

\<Fact-3\>

CLIPS\> (agenda)

0 older: f-1,f-3

0 older: f-2,f-3

0 older: f-1,f-2

For a total of 3 activations.

CLIPS\>

Example 5

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(multislot siblings))

CLIPS\>

(defrule large-family

(person (siblings \$?s&:(\> (length\$ ?s) 4)))

=\>)

CLIPS\>

(assert (person (name John) (siblings Fred Gwen)) ; f-1

(person (name Greg)) ; f-2

(person (name Jill) (siblings Joe Sue Lou Mark Dot))) ; f-3

\<Fact-3\>

CLIPS\> (agenda)

0 large-family: f-3

For a total of 1 activation.

CLIPS\>

Example 6

CLIPS\> (clear)

CLIPS\>

(defrule sort

?f \<- (numbers \$?b ?v1 ?v2&:(\> ?v1 ?v2) \$?e)

=\>

(retract ?f)

(assert (numbers ?b ?v2 ?v1 ?e)))

CLIPS\> (assert (numbers 8 3 6 9 2 3 7))

\<Fact-1\>

CLIPS\> (run)

CLIPS\> (facts)

f-12 (numbers 2 3 3 6 7 8 9)

For a total of 1 fact.

CLIPS\>

Example 7

CLIPS\> (clear)

CLIPS\>

(defrule at-least-3-items

(grocery-list \$?list&:(\>= (length\$ ?list) 3))

(test (\>= (length\$ ?list) 3))

=\>)

CLIPS\> (assert (grocery-list apple pears))

\<Fact-1\>

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-2\>

CLIPS\> (assert (grocery-list bread onions tomatoes cheese))

\<Fact-3\>

CLIPS\> (agenda)

0 at-least-3-items: f-3

0 at-least-3-items: f-2

For a total of 2 activations.

CLIPS\>

Example 8

CLIPS\> (clear)

CLIPS\>

(defrule approved

(credit-score ?cs&:(\>= ?cs 720))

(down-payment-percent ?dpp&:(\>= ?dpp 0.20))

(monthly-debt-percent ?mdp&:(\<= ?mdp 0.36))

=\>

(assert (loan-approved)))

CLIPS\> (assert (monthly-debt-percent 0.3))

\<Fact-1\>

CLIPS\> (assert (down-payment-percent 0.25))

\<Fact-2\>

CLIPS\> (assert (credit-score 800))

\<Fact-3\>

CLIPS\> (agenda)

0 approved: f-3,f-2,f-1

For a total of 1 activation.

CLIPS\> (watch facts)

CLIPS\> (run)

==\> f-4 (loan-approved)

CLIPS\> (unwatch facts)

CLIPS\>

#### 5.4.1.6 Return Value Constraints

The **return value constraint** (=) allows constraining the value of field to the return value of a function. (This constraint is different from the numeric com­parison function that uses the same symbol. The difference can be determined from context.) The return value must be one of the single field primitive data types. This value is incorporated directly into the pattern at the position at which the function was called as if it were a literal constraint, and any matching pat­terns must match this value as though the rule was defined with that value. Note that the function is evaluated each time the constraint is checked (not just once when the rule is defined).

Basic Syntax

=\<function-call\>

Syntax

Expanding on the syntax definition given in section 5.4.1.5 now gives:

\<term\> ::= \<constant\> \|

\<single-field-variable\> \|

\<multifield-variable\> \|

:\<function-call\> \|

=\<function-call\>

Example 1

CLIPS\> (clear)

CLIPS\>

(defrule ask-question

=\>

(bind ?length (random 1 10))

(bind ?width (random 1 10))

(println \"A rectangle has length \" ?length \" and width \" ?width)

(print \"What is the area of this rectangle? \")

(assert (response ?length ?width (read))))

CLIPS\>

(defrule correct-area

(response ?length ?width =(\* ?length ?width))

=\>

(println \"You are correct!\"))

CLIPS\>

(defrule incorrect-area

(response ?length ?width \~=(\* ?length ?width))

=\>

(println \"You are incorrect!\"))

CLIPS\> (run)

A rectangle has length 8 and width 10

What is the area of this rectangle? 80

You are correct!

CLIPS\> (reset)

CLIPS\> (run)

A rectangle has length 4 and width 4

What is the area of this rectangle? 8

You are incorrect!

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(deftemplate hoo \"hours of operation\"

(slot day)

(slot open)

(slot close))

CLIPS\>

(deffacts hoos

(hoo (day Monday) (open \"8:00 am\") (close \"6:00 pm\"))

(hoo (day Tuesday) (open \"8:00 am\") (close \"7:00 pm\"))

(hoo (day Wednesday) (open \"8:00 am\") (close \"6:00 pm\"))

(hoo (day Thursday) (open \"8:00 am\") (close \"5:00 pm\"))

(hoo (day Friday) (open \"8:00 am\") (close \"12:00 pm\"))

(hoo (day Saturday) (open \"8:30 am\") (close \"11:30 am\")))

CLIPS\>

(deffunction weekday ()

(nth\$ 7 (local-time)))

CLIPS\>

(defrule today\'s-hours\
(hoo (day =(weekday)) (open ?open) (close ?close))

=\>

(println \"We are open today from \" ?open \" to \" ?close \".\"))

CLIPS\>

(defrule closed-today

(not (hoo (day =(weekday))))

=\>

(println \"We are closed today.\"))

CLIPS\> (reset)

CLIPS\> (run)

We are open today from 8:00 am to 6:00 pm.

CLIPS\>

#### 5.4.1.7 Pattern‑Matching with Object Patterns

Instances of user‑defined classes in COOL can be pattern‑matched on the left‑hand side of rules. Patterns can only match objects for which the object's most specific class is defined before the pattern and which are in scope for the current module. Any classes that could have objects that match the pattern cannot be deleted or changed until the pattern is deleted. Even if a rule is deleted by its RHS, the classes bound to its patterns cannot be changed until after the RHS finishes executing.

When an instance is created or deleted, all patterns applicable to that object are updated. However, when a slot is changed, only those patterns that explicitly match on that slot are affected. Thus, one could use logical dependencies to hook to a change to a particular slot (rather than a change to any slot, which is all that is possible with deftemplates).

Changes to non‑reactive slots or instances of non‑reactive classes will have no effect on rules. Also Rete network activity will not be immediately apparent after changes to slots are made if pattern‑matching is being delayed through the use of the **make‑instance**, i.**initialize‑instance**;, i.**modify‑instance**;, i.**message‑modify‑instance**;, i.**duplicate‑instance**;, i.**message‑duplicate‑instance**; or **object‑pattern‑match‑delay** functions.

Syntax

\<object-pattern\> ::= (object \<attribute-constraint\>\*)

\<attribute-constraint\> ::= (is-a \<constraint\>) \|

(name \<constraint\>) \|

(\<slot-name\> \<constraint\>\*)

The **is‑a** constraint is used for specifying class constraints such as "Is this object a member of class PERSON?". The is‑a constraint also encompasses subclasses of the matching classes unless specifically excluded by the pattern. The **name** constraint is used for specifying a specific instance on which to pattern‑match. The evaluation of the name constraint must be of primitive type **instance‑name**, not **symbol**. Multifield constraints (such as \$?) cannot be used with the is‑a or name constraints. Other than these special cases, constraints used in object slots work similarly to constraints used in deftemplate slots. As with deftemplate patterns, slot names for object patterns must be symbols and can not contain any other constraints.

Example 1

The following rules illustrate pattern‑matching on an object\'s class.

(defrule class-match-1

(object)

=\>)

(defrule class-match-2

(object (is-a PERSON))

=\>)

(defrule class-match-3

(object (is-a MAN \| WOMAN))

=\>)

(defrule class-match-4

(object (is-a ?x))

(object (is-a \~?x))

=\>)

Rule *class‑match‑1* is satisified by all instances of any reactive class. Rule *class‑match‑2* is satisfied by all instances of class PERSON. Rule *class‑match‑3* is satisfied by all instances of class MAN or WOMAN. Rule *class‑match‑4* will be satisfied by any two instances of mutually exclusive classes.

Example 2

The following rules illustrate pattern‑matching on various attributes of an object\'s slots.

(defrule slot-match-1

(object (width))

=\>)

(defrule slot-match-2

(object (width ?))

=\>)

(defrule slot-match-3

(object (width \$?))

=\>)

Rule *slot‑match‑1* is satisfied by all instances of reactive classes that contain a reactive *width* slot with a zero length multifield value. Rule *slot‑match‑2* is satisfied by all instances of reactive classes that contain a reactive single or multifield *width* slot that is bound to a single value. Rule *slot‑match‑3* is satisfied by all instances of reactive classes that contain a reactive single or multifield *width* slot that is bound to any number of values. Note that a slot containing a zero length multifield value would satisfy rules *slot‑match‑1* and *slot‑match‑3*, but not rule *slot‑match‑2* (because the value\'s cardinality is zero).

Example 3

The following rules illustrate pattern‑matching on the slot values of an object.

(defrule value-match-1

(object (width 10)

=\>)

(defrule value-match-2

(object (width ?x&:(\> ?x 20)))

=\>)

(defrule value-match-3

(object (width ?x) (height ?x))

=\>)

Rule *value‑match‑1* is satisified by all instances of reactive classes that contain a reactive *width* slot with value 10. Rule *value‑match‑2* is satisfied by all instances of reactive classes that contain a reactive *width* slot that has a value greater than 20. Rule *value‑match‑3* is satisfied by all instances of reactive classes that contain a reactive *width* and *height* slots with the same value.

#### 5.4.1.8 Pattern‑Addresses

Certain RHS actions, such as **retract** and **unmake‑instance**, operate on an entire pattern CE. To signify which fact or instance they are to act upon, a variable can be bound to the **fact‑address** or **instance‑address** of a pattern CE. Collectively, fact‑addresses and instance‑addresses bound on the LHS of a rule are referred to as **pattern‑addresses**.

Syntax

\<assigned-pattern-CE\> ::= ?\<variable-symbol\> **\<-** \<pattern-CE\>

The left arrow, **\<‑**, is a required part of the syntax. A variable bound to a fact‑address or instance‑address can be compared to other variables or passed to functions. Variables bound to a fact or instance‑address may later be used to constrain fields within a pattern CE, however, the reverse is not allowed. It is an error to bind a varible to a **not** CE.

Example 1

CLIPS\> (clear)

CLIPS\>

(defrule print-grocery-list

?f \<- (grocery-list \$?items)

=\>

(retract ?f)

(println \"groceries: \" (implode\$ ?items)))

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (run)

groceries: milk eggs cheese

CLIPS\> (facts)

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(multislot name))

CLIPS\>

(defrule may-be-related

?p1 \<- (person (name \$?first1 ?last))

?p2 \<- (person (name \$?first2 ?last))

(test (neq ?p1 ?p2))

=\>

(println (implode\$ ?first1) \" \" ?last \" may be related to \"

(implode\$ ?first2) \" \" ?last \".\"))

CLIPS\> (assert (person (name Joe Bob Green)))

\<Fact-1\>

CLIPS\> (assert (person (name Martin Brown)))

\<Fact-2\>

CLIPS\> (assert (person (name Sue Ann Brown)))

\<Fact-3\>

CLIPS\> (agenda)

0 may-be-related: f-3,f-2

0 may-be-related: f-2,f-3

For a total of 2 activations.

CLIPS\> (run)

Sue Ann Brown may be related to Martin Brown.

Martin Brown may be related to Sue Ann Brown.

CLIPS\>

Example 3

CLIPS\> (clear)

CLIPS\>

(defclass PERSON

(is-a USER)

(slot sname)

(slot age))

CLIPS\> (make-instance \[p1\] of PERSON (sname \"Sam Jones\") (age 77))

\[p1\]

CLIPS\> (make-instance \[p2\] of PERSON (sname \"Sally Smith\") (age 25))

\[p2\]

CLIPS\>

(defrule print-and-delete-all-objects

?ins \<- (object)

=\>

(send ?ins print)

(unmake-instance ?ins))

CLIPS\> (run)

\[p2\] of PERSON

(sname \"Sally Smith\")

(age 25)

\[p1\] of PERSON

(sname \"Sam Jones\")

(age 77)

CLIPS\> (instances)

CLIPS\>

### 5.4.2 Test Conditional Element

The **test** **conditional element** is used to evaluate a function call. The test CE is unsatisfied if the associated function call returns the symbol FALSE and satisfied if any other value is returned. As with predicate constraints, the user can reference variables that were previously bound.

Syntax

\<test-CE\> ::= (test \<function-call\>)

Since the symbol **test** is used to indicate this type of conditional element, rules may not use the symbol test as the first field in a pattern CE. A **test** CE is evaluated when all proceeding CEs are satisfied. This means that a **test** CE will be evaluated more than once if the proceeding CEs can be satisfied by more than one group of pattern entities. In order to cause the reevaluation of a **test** CE, a pattern entity matching a CE prior to the **test** CE must be changed.

Example 1

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age))

CLIPS\>

(defrule older

(person (name ?name1) (age ?age1))

(person (name ?name2) (age ?age2))

(test (\> ?age1 ?age2))

=\>

(println ?name1 \" is older than \" ?name2))

CLIPS\> (assert (person (name \"John Smith\") (age 15)))

\<Fact-1\>

CLIPS\> (assert (person (name \"Jane Farmer\") (age 23)))

\<Fact-2\>

CLIPS\> (assert (person (name \"Jake Jones\") (age 37)))

\<Fact-3\>

CLIPS\> (run)

Jake Jones is older than Jane Farmer

Jake Jones is older than John Smith

Jane Farmer is older than John Smith

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(defrule at-least-3-items

(grocery-list \$?list)

(test (\>= (length\$ ?list) 3))

=\>)

CLIPS\> (assert (grocery-list apple pears))

\<Fact-1\>

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-2\>

CLIPS\> (assert (grocery-list bread onions tomatoes cheese))

\<Fact-3\>

CLIPS\> (agenda)

0 at-least-3-items: f-3

0 at-least-3-items: f-2

For a total of 2 activations.

CLIPS\>

### 5.4.3 Or Conditional Element

The **or conditional element** allows any one of several conditional elements to activate a rule. If any of the conditional elements inside of the **or** CE is satisfied, then the **or** CE is satisfied. If all other LHS condi­tional elements are satisfied, the rule will be activated. Note that a rule will be activated for each conditional element with an **or** CE that is satisfied (assuming the other conditional elements of the rule are also satisfied). Any number of conditional elements may appear within an **or** CE. The **or** CE produces the identical effect of writing several rules with sim­ilar LHS's and RHS's.

Syntax

\<or-CE\> ::= (or \<conditional-element\>+)

Again, if more than one of the conditional elements in the **or** CE can be met, the rule will fire *multiple times*, once for each satisfied combination of conditions.

Example

CLIPS\> (clear)

CLIPS\>

(defrule system-fault

(error-status unknown)

(or (temp high)

(valve broken)

(pump off))

=\>

(println \"The system has a fault.\"))

CLIPS\> (assert (error-status unknown))

\<Fact-1\>

CLIPS\> (assert (temp high))

\<Fact-2\>

CLIPS\> (assert (pump off))

\<Fact-3\>

CLIPS\> (agenda)

0 system-fault: f-1,f-3

0 system-fault: f-1,f-2

For a total of 2 activations.

CLIPS\> (run)

The system has a fault.

The system has a fault.

CLIPS\>

Note that the above example is exactly equivalent to the following three (separate) rules:

(defrule system-fault\
(error-status unknown)\
(temp high)\
=\>\
(println \"The system has a fault.\"))

(defrule system-fault\
(error-status unknown)\
(valve broken)\
=\>\
(println \"The system has a fault.\"))

(defrule system-fault\
(error-status unknown)\
(pump off)\
=\>\
(println \"The system has a fault.\"))

### 5.4.4 And Conditional Element

CLIPS assumes that all rules have an implicit **and** **conditional element** surrounding the conditional elements on the LHS. This means that all conditional elements on the LHS must be satisfied before the rule can be activated. An explicit **and** conditional element is provided to allow the mixing of **and** CEs and **or** CEs. This allows other types of conditional elements to be grouped together within **or** and **not** CEs. The **and** CE is satisfied if *all* of the CEs inside of the explicit **and** CE are satisfied. If all other LHS condi­tions are true, the rule will be activated. Any number of conditional elements may be placed within an **and** CE. Note that the LHS of any rule is enclosed within an implied **and** CE.

Syntax

\<and-CE\> ::= (and \<conditional-element\>+)

Example

CLIPS\> (clear)

CLIPS\>

(defrule system-flow

(error-status confirmed)

(or (and (temp high)

(valve closed))

(and (temp low)

(valve open)))

=\>

(println \"The system is having a flow problem.\"))

CLIPS\> (assert (error-status confirmed))

\<Fact-1\>

CLIPS\> (assert (temp high))

\<Fact-2\>

CLIPS\> (assert (valve closed))

\<Fact-3\>

CLIPS\> (agenda)

0 system-flow: f-1,f-2,f-3

For a total of 1 activation.

CLIPS\>

### 5.4.5 Not Conditional Element

Sometimes the *lack* of information is meaningful; i.e., one wishes to fire a rule if a pattern entity or other CE does *not* exist. The **not** **conditional element** provides this capability. The **not** CE is satisfied only if the conditional element contained within it is not satisfied. As with other conditional elements, any number of additional CEs may be on the LHS of the rule and field con­straints may be used within the negated pattern.

Syntax

\<not-CE\> ::= (not \<conditional-element\>)

Only one CE may be negated at a time. Multiple patterns may be negated by using multiple **not** CEs. The same holds true for variable bindings within a **not** CE. Previously bound variables may be used freely inside of a **not** CE. However, variables bound for the first time within a **not** CE can be used only in that pattern.

Example 1

CLIPS\> (clear)

CLIPS\>

(defrule no-milk

(not (grocery-list \$? milk \$?))

=\>

(println \"No grocery list contains milk\"))

CLIPS\> (assert (grocery-list bread turkey cheese))

\<Fact-1\>

CLIPS\> (assert (grocery-list chips salsa))

\<Fact-2\>

CLIPS\> (agenda)

0 no-milk: \*

For a total of 1 activation.

CLIPS\> (assert (grocery-list flour eggs milk))

\<Fact-3\>

CLIPS\> (agenda)

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(defrule highest-number

(number ?n)

(not (number ?n2&:(\> ?n2 ?n)))

=\>

(println \"Highest number is \" ?n))

CLIPS\> (assert (number 3))

\<Fact-1\>

CLIPS\> (assert (number 15))

\<Fact-2\>

CLIPS\> (assert (number 7))

\<Fact-3\>

CLIPS\> (agenda)

0 highest-number: f-2,\*

For a total of 1 activation.

CLIPS\> (run)

Highest number is 15

CLIPS\>

Example 3

CLIPS\> (clear)

CLIPS\>

(defrule check-valve

(check-status ?valve)

(not (valve-broken ?valve))

=\>

(println \"Valve \" ?valve \" is OK\"))

CLIPS\>

(assert (check-status v1)

(check-status v2)

(check-status v3)

(check-status v4))

\<Fact-4\>

CLIPS\>

(assert (valve-broken v2)

(valve-broken v4))

\<Fact-6\>

CLIPS\> (run)

Valve v3 is OK

Valve v1 is OK

CLIPS\>

Example 4

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age))

CLIPS\>

(defrule oldest

(person (name ?name1) (age ?age1))

(not (person (age ?age2&:(\> ?age2 ?age1))))

=\>

(println ?name1 \" is the oldest person\"))

CLIPS\> (assert (person (name \"John Smith\") (age 20)))

\<Fact-1\>

CLIPS\> (assert (person (name \"Sally Jones\") (age 18)))

\<Fact-2\>

CLIPS\> (assert (person (name \"Bill White\") (age 14)))

\<Fact-3\>

CLIPS\> (agenda)

0 oldest: f-1,\*

For a total of 1 activation.

CLIPS\> (run)

John Smith is the oldest person

CLIPS\>

### 5.4.6 Exists Conditional Element

The **exists** **conditional element** provides a mechanism for determining if a group of specified CEs is satisfied by a least one set of pattern entities.

Syntax

\<exists-CE\> ::= (exists \<conditional-element\>+)

The **exists** CE is implemented by replacing the **exists** keyword with two nested **not** CEs. For example, the following rule

(defrule example

(exists (a ?x) (b ?x))

=\>)

is equivalent to the rule below

(defrule example

(not (not (and (a ?x) (b ?x))))

=\>)

Because of the way the **exists** CE is implemented using **not** CEs, the restrictions which apply to CEs found within **not** CEs (such as binding a pattern CE to a fact‑address) also apply to the CEs found within an **exists** CE.

Example 1

CLIPS\> (clear)

CLIPS\>

(deftemplate hero

(slot name)

(slot status (default unoccupied)))

CLIPS\> (assert (goal save-the-day))

\<Fact-1\>

CLIPS\> (assert (hero (name \"Death Defying Man\")))

\<Fact-2\>

CLIPS\> (assert (hero (name \"Stupendous Man\")))

\<Fact-3\>

CLIPS\> (assert (hero (name \"Incredible Woman\")))

\<Fact-4\>

CLIPS\>

(defrule save-the-day

(goal save-the-day)

(exists (hero (status unoccupied)))

=\>

(println \"The day is saved\"))

CLIPS\> (agenda)

0 save-the-day: f-1,\*

For a total of 1 activation.

CLIPS\> (matches save-the-day)

Matches for Pattern 1

f-1

Matches for Pattern 2

f-2

f-3

f-4

Partial matches for CEs 1 - 2

f-1,\*

Activations

f-1,\*

(4 1 1)

CLIPS\> (run)

The day is saved

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(defrule system-fault

(error-status unknown)

(exists (or (temp high)

(valve broken)

(pump off)))

=\>

(println \"The system has a fault.\"))

CLIPS\> (assert (error-status unknown))

\<Fact-1\>

CLIPS\> (assert (temp high))

\<Fact-2\>

CLIPS\> (assert (pump off))

\<Fact-3\>

CLIPS\> (agenda)

0 system-fault: f-1,\*

For a total of 1 activation.

CLIPS\> (run)

The system has a fault.

CLIPS\>

Example 3

CLIPS\> (clear)

CLIPS\>

(defrule valve-broken

(exists (check-status ?valve)

(valve-broken ?valve))

=\>

(println \"There is a broken valve\"))

CLIPS\>

(assert (check-status v1)\
(check-status v2)\
(check-status v3)\
(check-status v4))

\<Fact-4\>

CLIPS\>

(assert (valve-broken v2)

(valve-broken v4))

\<Fact-6\>

CLIPS\> (agenda)

0 valve-broken: \*

For a total of 1 activation.

CLIPS\> (run)

There is a broken valve

CLIPS\>

### 5.4.7 Forall Conditional Element

The **forall** **conditional element** provides a mechanism for determining if a group of specified CEs is satisfied for every occurence of another specified CE.

Syntax

\<forall-CE\> ::= (forall \<conditional-element\>

\<conditional-element\>+)

The **forall** CE is implemented by replacing the **forall** keyword with combinations of **not** and **and** CEs. For example, the following rule

(defrule example

(forall (a ?x) (b ?x) (c ?x))

=\>)

is equivalent to the rule below

(defrule example

(not (and (a ?x)

(not (and (b ?x) (c ?x)))))

=\>)

Because of the way the **forall** CE is implemented using **not** CEs, the restrictions which apply to CE found within **not** CEs (such as binding a pattern CE to a fact‑address) also apply to the CEs found within an **forall** CE.

Example

The following rule determines if every student has passed in reading, writing, and arithmetic by using the **forall** CE.

CLIPS\> (clear)\
CLIPS\>

(deftemplate student

(slot name))

CLIPS\>

(deftemplate passed

(slot name)

(slot subject))

CLIPS\>

(defrule all-students-passed

(forall

(student (name ?name))

(passed (name ?name) (subject reading))

(passed (name ?name) (subject writing))

(passed (name ?name) (subject arithmetic)))

=\>

(println \"All students passed.\"))

CLIPS\>

The following commands illustrate how the **forall** CE works in the *all‑students‑passed* rule. Note that initially the *all‑students‑passed* rule is satisfied because there are no students.

CLIPS\> (agenda)

0 all-students-passed: \*

For a total of 1 activation.

CLIPS\>

After the (student Bob) fact is asserted, the rule is no longer satisfied since Bob has not passed reading, writing, and arithmetic.

CLIPS\> (assert (student (name Bob)))

\<Fact-1\>

CLIPS\> (agenda)

CLIPS\>

The rule is still not satisfied after Bob has passed reading and writing, since he still has not passed arithmetic.

CLIPS\> (assert (passed (name Bob) (subject reading)))

\<Fact-2\>

CLIPS\> (assert (passed (name Bob) (subject writing)))

\<Fact-3\>

CLIPS\> (agenda)

CLIPS\>

Once Bob has passed arithmetic, the all‑students‑passed rule is reactivated.

> CLIPS\> (assert (passed (name Bob) (subject arithmetic)))
>
> \<Fact-4\>
>
> CLIPS\> (agenda)
>
> 0 all-students-passed: \*
>
> For a total of 1 activation.
>
> CLIPS\>

If a new student is asserted, then the rule is taken off the agenda, since John has not passed reading, writing, and arithmetic.

CLIPS\> (assert (student (name John)))

\<Fact-5\>

CLIPS\> (agenda)

CLIPS\> (matches all-students-passed)

Matches for Pattern 1

f-1

f-5

Matches for Pattern 2

f-2

Matches for Pattern 3

f-3

Matches for Pattern 4

f-4

Partial matches for CEs 1 - 2

f-1,f-2

Partial matches for CEs 1 - 3

f-1,f-2,f-3

Partial matches for CEs 1 - 4

f-1,f-2,f-3,f-4

Partial matches for CEs 1 (P1) , 2 (P2 - P4)

f-5,\*

Partial matches for CEs 1 (P1 - P4)

None

Activations

None

(5 4 0)

CLIPS\>

Removing both *student* facts reactivates the rule again.

CLIPS\> (retract 1 5)

CLIPS\> (agenda)

0 all-students-passed: \*

For a total of 1 activation.

CLIPS\>

### 5.4.8 Logical Conditional Element

The **logical** **conditional element** provides a **truth maintenance** capability for pattern entities (facts or instances) created by rules that use the **logical** CE. A pattern entity created on the RHS (or as a result of actions performed from the RHS) can be made logically dependent upon the pattern entities that matched the patterns enclosed with the **logical** CE on the LHS of the rule. The pattern entities matching the LHS **logical** patterns provide **logical support** to the facts and instance created by the RHS of the rule. A pattern entity can be logically supported by more than one group of pattern entities from the same or different rules. If any one supporting pattern entities is removed from a group of supporting pattern entities (and there are no other supporting groups), then the pattern entity is removed.

If a pattern entity is created without logical support (e.g., from a deffacts, definstaces, as a top‑level command, or from a rule without any logical patterns), then the pattern entity has **unconditional support**. Unconditionally supporting a pattern entity removes all logical support (without causing the removal of the pattern entity). In addition, further logical support for an unconditionally supported pattern entity is ignored. Removing a rule that generated logical support for a pattern entity, removes the logical support generated by that rule (but does not cause the removal of the pattern entity if no logical support remains).

Syntax

\<logical-CE\> ::= (logical \<conditional-element\>+)

The **logical** CE groups patterns together exactly as the explicit **and** CE does. It may be used in conjunction with the **and**, **or**, and **not** CEs. However, only the first N patterns of a rule can have the logical CE applied to them. For example, the following rule is legal.

(defrule ok

(logical (credit-score ?person good))

(logical (debt-and-income ?person good))

?f \<- (assessing-loan)

=\>

(retract ?f)

(assert (loan-approved ?person)))

Whereas the following rules are illegal.

(defrule not-ok-1

(logical (credit-score ?person good))

?f \<- (assessing-loan)

(logical (debt-and-income ?person good))

=\>

(assert (loan-approved ?person)))

(defrule not-ok-2

?f \<- (assessing-loan)

(logical (credit-score ?person good))

(logical (debt-and-income ?person good))

=\>

(assert (loan-approved ?person)))

(defrule not-ok-3

(or (credit-score-waver ?person)

(logical (credit-score ?person good)))

(logical (debt-and-income ?person good))

?f \<- (assessing-loan)

=\>

(retract ?f)

(assert (loan-approved ?person)))

Example 1

This example demonstrates facts receiving support from multiple rules.

CLIPS\> (clear)

CLIPS\>

(defrule good-scores

(logical (credit-score good))

(logical (debt-and-income good))

(assessing-loan)

=\>

(assert (loan-assessed))

(assert (loan-approved)))

CLIPS\>

(defrule wavers

(logical (credit-score-waver))

(logical (debt-and-income-waver))

(assessing-loan)

=\>

(assert (loan-assessed))

(assert (loan-approved)))

CLIPS\>

(assert (credit-score good)

(debt-and-income good)

(assessing-loan)

(credit-score-waver)

(debt-and-income-waver))

\<Fact-5\>

CLIPS\> (facts)

f-1 (credit-score good)

f-2 (debt-and-income good)

f-3 (assessing-loan)

f-4 (credit-score-waver)

f-5 (debt-and-income-waver)

For a total of 5 facts.

CLIPS\> (agenda)

0 wavers: f-4,f-5,f-3

0 good-scores: f-1,f-2,f-3

For a total of 2 activations.

CLIPS\>

The **wavers** rule executes asserting and providing logical support for the **loan-assessed** and **loan-approved** facts. The **good-scores** rule executes next asserting the same two facts which adds additional logical support.

CLIPS\> (watch rules)

CLIPS\> (watch facts)

CLIPS\> (run)

FIRE 1 wavers: f-4,f-5,f-3

==\> f-6 (loan-assessed)

==\> f-7 (loan-approved)

FIRE 2 good-scores: f-1,f-2,f-3

CLIPS\>

Retracting the **credit-score** fact removes the logical support for the **loan-assessed** and **loan-approved** facts asserted by the **good-scores** rule. The logical support provided by the **wavers** rule still exists, so these facts are not retracted.

CLIPS\> (retract 1)

\<== f-1 (credit-score good)

CLIPS\>

Asserting the **loan-approved** fact without the restrictions of a **logical** conditional element gives it unconditional support.

CLIPS\> (assert (loan-approved))

\<Fact-7\>

CLIPS\>

Retracting the **credit-score-waver** fact removes the remaining logical support for the **loan-assessed** and **loan-approved** facts provided by the **wavers** rule. This causes the **loan-assessed** fact to be retracted since it has no remaining logical support, but the **loan-approved** fact is not retracted since it is now unconditionally supported.

CLIPS\> (retract 4)

\<== f-4 (credit-score-waver)

\<== f-6 (loan-assessed)

CLIPS\> (unwatch all)

CLIPS\>

Example 2

The logical CE can be used with an object pattern to create pattern entities that are logically dependent on changes to specific slots in the matching instance(s) rather than all slots. This cannot be accomplished with template facts because a change to a template fact slot actually involves the retraction of the old template fact and the assertion of a new one, whereas a change to an instance slot is done in place. The example below illustrates this behavior:

CLIPS\> (clear)

CLIPS\>

(defclass PERSON (is-a USER)

(slot full-name)

(slot age)

(slot credit-score))

CLIPS\>

(deftemplate person

(slot full-name)

(slot age)

(slot credit-score))

CLIPS\>

(defrule credit-check-instance

(logical (object (is-a PERSON)

(full-name ?name)

(credit-score ?cs&:(\< ?cs 580))))

=\>

(assert (reject-loan ?name)))

CLIPS\>

(defrule credit-check-fact

(logical (person (full-name ?name)

(credit-score ?cs&:(\< ?cs 580))))

=\>

(assert (reject-loan ?name)))

CLIPS\>

(make-instance p1 of PERSON

(full-name \"Jack Jones\")

(age 37)

(credit-score 500))

\[p1\]

CLIPS\>

(assert (person (full-name \"Sally Smith\")

(age 37)

(credit-score 500)))

\<Fact-1\>

CLIPS\> (watch facts)

CLIPS\> (run)

==\> f-2 (reject-loan \"Sally Smith\")

==\> f-3 (reject-loan \"Jack Jones\")

CLIPS\> (send \[p1\] put-age 38)

38

CLIPS\> (modify 1 (age 38))

\<== f-1 (person \... (age 37) \...)

\<== f-2 (reject-loan \"Sally Smith\")

==\> f-1 (person \... (age 38) \...)

\<Fact-1\>

CLIPS\> (agenda)

0 credit-check-fact: f-1

For a total of 1 activation.

CLIPS\> (unwatch facts)

CLIPS\>

Example 3

CLIPS\> (clear)

CLIPS\> (unwatch all)

CLIPS\>

(defrule down-payment-percent

(logical (loan-amount ?la)

(available-down-payment ?adp))

=\>

(bind ?dpp (/ ?adp ?la))

(assert (down-payment-percent ?dpp)))

CLIPS\>

(defrule monthly-debt-percent

(logical (monthly-house-payment ?mhp)

(other-monthly-debt ?omd)

(gross-monthly-income ?gmi))

=\>

(bind ?mdp (/ (+ ?mhp ?omd) ?gmi))

(assert (monthly-debt-percent ?mdp)))

CLIPS\>

(defrule approved

(logical (credit-score ?cs&:(\>= ?cs 720))

(down-payment-percent ?dpp&:(\>= ?dpp 0.20))

(monthly-debt-percent ?mdp&:(\<= ?mdp 0.36)))

=\>

(assert (loan-approved)))

CLIPS\> (assert (loan-amount 100000))

\<Fact-1\>

CLIPS\> (assert (available-down-payment 25000))

\<Fact-2\>

CLIPS\> (assert (monthly-house-payment 1000))

\<Fact-3\>

CLIPS\> (assert (other-monthly-debt 800))

\<Fact-4\>

CLIPS\> (assert (gross-monthly-income 6000))

\<Fact-5\>

CLIPS\> (assert (credit-score 800))

\<Fact-6\>

CLIPS\> (agenda)

0 monthly-debt-percent: f-3,f-4,f-5

0 down-payment-percent: f-1,f-2

For a total of 2 activations.

CLIPS\> (watch rules)

CLIPS\> (watch facts)

CLIPS\> (run)

FIRE 1 monthly-debt-percent: f-3,f-4,f-5

==\> f-7 (monthly-debt-percent 0.3)

FIRE 2 down-payment-percent: f-1,f-2

==\> f-8 (down-payment-percent 0.25)

FIRE 3 approved: f-6,f-8,f-7

==\> f-9 (loan-approved)

CLIPS\> (retract 2)

\<== f-2 (available-down-payment 25000)

\<== f-8 (down-payment-percent 0.25)

\<== f-9 (loan-approved)

CLIPS\> (assert (available-down-payment 15000))

==\> f-10 (available-down-payment 15000)

\<Fact-10\>

CLIPS\> (run)

FIRE 1 down-payment-percent: f-1,f-10

==\> f-11 (down-payment-percent 0.15)

CLIPS\>

### 5.4.9 Automatic Replacement of LHS CEs

Under certain circumstances, CLIPS will change the CEs specified in the rule LHS.

#### 5.4.9.1 Or CEs Following Not CEs

If an *or* CE immediately follows a *not* CE, then the *not*/*or* CE combination is replaced with an *and*/*not* CE combination where each of the CEs contained in the original *or* CE is enclosed within a *not* CE and then all of the *not* CEs are enclosed within a single *and* CE. For example, the following rule

(defrule example

(a ?x)

(not (or (b ?x)

(c ?x)))

=\>)

would be changed as follows.

(defrule example

(a ?x)

(and (not (b ?x))

(not (c ?x)))

=\>)

### 5.4.10 Declaring Rule Properties

This feature allows the properties or characteristics of a rule to be defined. The char­acter­istics are declared on the LHS of a rule using the **declare** keyword. A rule may only have one **declare** statement and it must appear be­fore the first conditional element on the LHS.

Syntax

\<declaration\> ::= (declare \<rule-property\>+)

\<rule-property\> ::= (salience \<integer-expression\>) \|

(auto-focus \<boolean-symbol\>)

\<boolean-symbol\> ::= TRUE \| FALSE

#### 5.4.10.1 The Salience Rule Property

The **salience** rule property allows the user to assign a priority to a rule. When multiple rules are in the agenda, the rule with the highest priority will fire first. The declared salience value should be an expression that evaluates to an an integer in the range ‑10000 to +10000. Salience expressions may freely reference global variables and other functions (however, you should avoid using functions with side‑effects). If unspecified, the salience value for a rule defaults to zero.

Example

CLIPS\> (clear)

CLIPS\> (defglobal ?\*s1\* = -10)

CLIPS\> (deffunction s2 () 50)

CLIPS\>

(defrule r1

=\>)

CLIPS\>

(defrule r2

(declare (salience 20))

=\>)

CLIPS\>

(defrule r3

(declare (salience (s2)))

=\>)

CLIPS\>

(defrule r4

(declare (salience ?\*s1\*))

=\>)

CLIPS\>

(defrule r5

(declare (salience (+ ?\*s1\* (s2))))

=\>)

CLIPS\> (agenda)

50 r3: \*

40 r5: \*

20 r2: \*

0 r1: \*

-10 r4: \*

For a total of 5 activations.

CLIPS\>

Salience values can be evaluated at one of three times: when a rule is defined, when a rule is activated, and every cycle of execution (the latter two situations are referred to as **dynamic salience**). By default, salience values are only evaluated when a rule is defined. The **set‑salience‑evaluation** command can be used to change this behavior. Note that each salience evaluation method encompasses the previous method (i.e. if saliences are evaluated every cycle, then they are also evaluated when rules are activated or defined).

 Usage Note

Despite the large number of possible values, with good design there's rarely a need for more than five salience values in a simple program and ten salience values in a complex program. Defining the salience values as global variables allows you to specify and document the values used by your program in a centralized location and also makes it easier to change the salience of a group of rules sharing the same salience value:

(defglobal ?\*high-priority\* = 100)

(defglobal ?\*low-priority\* = -100)

(defrule rule-1

(declare (salience ?\*high-priority\*))

=\>)

(defrule rule-2

(declare (salience ?\*low-priority\*))

=\>)

#### 5.4.10.2 The Auto‑Focus Rule Property

The **auto‑focus** rule property allows an automatic **focus** command to be executed whenever a rule becomes activated. If the auto‑focus property for a rule is TRUE, then a focus command on the module in which the rule is defined is automatically executed whenever the rule is activated. If the auto‑focus property for a rule is FALSE, then no action is taken when the rule is activated. If unspecified, the auto‑focus value for a rule defaults to FALSE.

Example

CLIPS\> (clear)

CLIPS\> (defmodule MAIN (export ?ALL))

CLIPS\>

(deftemplate person

(slot name)

(slot age))

CLIPS\>

(defrule get-person\
=\>\
(print \"What is your name? \")

(bind ?name (readline))

(print \"What is your age? \")

(bind ?age (read))

(assert (person (name ?name) (age ?age))))

CLIPS\> (defmodule VIOLATIONS (import MAIN ?ALL))

CLIPS\>

(defrule bad-age

(declare (auto-focus TRUE))

(person (name ?name) (age ?age&:(\< ?age 0)))

=\>

(println ?name \" has a bad age value.\"))

CLIPS\> (reset)

CLIPS\> (watch focus)

CLIPS\> (watch rules)

CLIPS\> (run)

FIRE 1 get-person: \*

What is your name? Sam Jones

What is your age? -9

==\> Focus VIOLATIONS from MAIN

FIRE 2 bad-age: f-1

Sam Jones has a bad age value.

\<== Focus VIOLATIONS to MAIN

\<== Focus MAIN

CLIPS\> (unwatch all)

CLIPS\>

#
