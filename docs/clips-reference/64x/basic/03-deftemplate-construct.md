# Section 3: Deftemplate Construct

Ordered facts encode information positionally. To access that information, a user must know not only what data is stored in a fact but also which field contains the data. Non‑ordered (or deftemplate) facts provide the user with the ability to abstract the structure of a fact by assign­ing names to each field found within the fact. The **deftemplate** construct is used to create a template that can then be used by non‑ordered facts to access fields of the fact by name. The deftemplate construct is analogous to a record or structure definition in programming languages such as C.

Syntax

(deftemplate \<deftemplate-name\> \[\<comment\>\]

\<slot-definition\>\*)

\<slot-definition\> ::= \<single-slot-definition\> \|

\<multislot-definition\>

\<single-slot-definition\>

::= (slot \<slot-name\>

\<template-attribute\>\*)

\<multislot-definition\>

::= (multislot \<slot-name\>

\<template-attribute\>\*)

\<template-attribute\> ::= \<default-attribute\> \|

\<constraint-attribute\>

\<default-attribute\>

::= (default ?DERIVE \| ?NONE \| \<expression\>\*) \|

(default-dynamic \<expression\>\*)

Redefining a deftemplate will result in the previous definition being discarded. A deftemplate can not be redefined while it is being used (for example, by a fact or pattern in a rule). A deftemplate can have any number of single or multifield slots. CLIPS always enforces the single and multifield definitions of the deftemplate. For example, it is an error to store (or match) multiple values in a single-field slot.

Example

(deftemplate thing

(slot name)

(slot location)

(slot on-top-of)

(slot weight)

(multislot contents))

## 3.1 Slot Default Values

The \<default‑attribute\> specifies the value to be used for unspecified slots of a template fact when an **assert** action is performed. One of two types of default selections can be chosen: default or dynamic‑default.

The **default** attribute specifies a static default value. The specified expressions are evaluated once when the deftemplate is defined and the result is stored with the deftemplate. The result is assigned to the appropriate slot when a new template fact is asserted. If the keyword ?DERIVE is used for the default value, then a default value is derived from the constraints for the slot (see section 11.5 for more details). By default, the default attribute for a slot is (default ?DERIVE). If the keyword ?NONE is used for the default value, then a value must explicitly be assigned for a slot when an assert is performed. It is an error to assert a template fact without specifying the values for the (default ?NONE) slots.

The **default‑dynamic** attribute is a dynamic default. The specified expressions are evaluated every time a template fact is asserted, and the result is assigned to the appropriate slot.

A single‑field slot may only have a single value for its default. Any number of values may be specified as the default for a multifield slot (as long as the number of values satisfies the cardinality attribute for the slot).

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate point

(slot x (default ?NONE))

(slot y (type INTEGER) (default ?DERIVE))

(slot id (default (gensym\*)))

(slot uid (default-dynamic (gensym\*))))

CLIPS\> (assert (point))

\[TMPLTRHS1\] Slot \'x\' requires a value because of its (default ?NONE) attribute.

CLIPS\> (assert (point (x 3)))

\<Fact-1\>

CLIPS\> (assert (point (x 4)))

\<Fact-2\>

CLIPS\> (facts)

f-1 (point (x 3) (y 0) (id gen1) (uid gen2))

f-2 (point (x 4) (y 0) (id gen1) (uid gen3))

For a total of 2 facts.

CLIPS\>

## 3.2 Slot Default Constraints for Pattern‑Matching

Single‑field slots that are not specified in a pattern on the LHS of a rule are defaulted to single‑field wildcards (?) and multifield slots are defaulted to multifield wildcards (\$?).

## 3.3 Slot Value Constraint Attributes

The syntax and functionality of single and multifield constraint attributes are described in detail in Section 11. Static and dynamic constraint checking for deftemplates is supported. Static checking is performed when constructs or commands using deftemplates slots are being parsed (and the specific deftemplate associated with the construct or command can be immediately determined). Template patterns used on the LHS of a rule are also checked to determine if constraint conflicts exist among variables used in more than one slot. Errors for inappropriate values are immediately signaled. References to fact‑indexes made in commands such as **modify** and **duplicate** are considered to be ambiguous and are never checked using static checking. Static checking is always enabled. Dynamic checking is also supported. If dynamic checking is enabled, then new deftemplate facts have their values checked when created. This dynamic checking is disabled by default. This behavior can be changed using the **set‑dynamic‑constraint‑checking** function. If a violation occurs when dynamic checking is being performed, then execution will be halted.

Example

(deftemplate thing

(slot name

(type SYMBOL)

(default ?DERIVE))

(slot location

(type SYMBOL)

(default ?DERIVE))

(slot on-top-of

(type SYMBOL)

(default floor))

(slot weight

(allowed-values light heavy)

(default light))

(multislot contents

(type SYMBOL)

(default ?DERIVE)))

## 3.4 Implied Deftemplates

Asserting or referring to an ordered fact (such as in a LHS pattern) creates an "implied" deftemplate with a single implied multifield slot named *implied*. The implied multifield slot's name is not printed when the fact is printed. The implied deftemplate can be manipulated and examined identically to any user defined deftemplate.

Example

CLIPS\> (clear)

CLIPS\> (assert (groceries milk eggs cheese))

\<Fact-1\>

CLIPS\> (defrule study (homework math) =\>)

CLIPS\> (list-deftemplates)

groceries

homework

For a total of 2 deftemplates.

CLIPS\> (facts)

f-1 (groceries milk eggs cheese)

For a total of 1 fact.

CLIPS\>

#
