# Section 3: Deftemplate Construct

Ordered facts encode information positionally. To access that information, a user must know not only what data is stored in a fact, but also which field stores the data. Non-ordered (or deftemplate) facts allow the user to abstract the structure of a fact by assigning names to each field it contains. The **deftemplate** construct creates a template that allows access to the fields within non-ordered facts by name. The deftemplate construct is analogous to a record or structure definition in programming languages such as C.

Syntax

(deftemplate \<deftemplate-name\> \[\<comment\>\]

\[(is-a \<base-deftemplate-name\>)\]

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

\<constraint-attribute\> \|

\<pattern-match-attribute\>

\<default-attribute\>

::= (default ?DERIVE \| ?NONE \| \<expression\>\*) \|

(default-dynamic \<expression\>\*)

\<pattern-match-attribute\>

::= (pattern-match reactive \| non-reactive)

Redefining a deftemplate will result in the previous definition being discarded. A deftemplate cannot be redefined while it is being used (for example, by a fact or a pattern in a rule). A deftemplate can have any number of single-field or multifield slots. CLIPS always enforces the cardinality constraints of single-field and multifield slots. For example, it is an error to store (or match) multiple values in a single-field slot.

Example

(deftemplate thing

(slot name)

(slot location)

(slot on-top-of)

(slot weight)

(multislot contents))

## 3.1 Slot Default Values

The \<default‑attribute\> specifies the value to be used for unspecified slots of a template fact when an **assert** action is performed. One of two types of default selections can be chosen: default or dynamic‑default.

The **default** attribute specifies a static default value. The specified expressions are evaluated once when the deftemplate is defined, and the result is stored with the deftemplate. The result is assigned to the appropriate slot when a new template fact is asserted. If the keyword ?DERIVE is used for the default value, then a default value is derived from the constraints for the slot (see Section 11.5 for more details). By default, the default attribute for a slot is (default ?DERIVE). If the keyword ?NONE is used for the default value, then a value must explicitly be assigned for a slot when an assert is performed. It is an error to assert a template fact without specifying the values for the (default ?NONE) slots.

The **default‑dynamic** attribute is a dynamic default. The specified expressions are evaluated every time a template fact is asserted, and the result is assigned to the appropriate slot.

A single-field slot may only have a single value for its default. Any number of values may be specified as the default for a multifield slot (as long as the number of values satisfies the cardinality attribute for the slot).

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

## 3.2 Slot Default Constraints for Pattern Matching

Single‑field slots that are not specified in a pattern on the LHS of a rule are defaulted to single‑field wildcards (?) and multifield slots are defaulted to multifield wildcards (\$?).

## 3.3 Slot Value Constraint Attributes

The syntax and functionality of single-field and multifield constraint attributes are described in detail in Section 11. Static and dynamic constraint checking for deftemplate patterns, commands, and facts is supported. Static checking is performed when constructs or commands using deftemplate slots are parsed (and the specific deftemplate associated with the construct or command can be immediately determined). Template patterns used on the LHS of a rule are also checked to determine if constraint conflicts exist among variables used in more than one slot. Errors for inappropriate values are immediately signaled. References to fact‑indexes made in commands such as **modify**, **update**, and **duplicate** are considered ambiguous and are never checked using static checking. Static checking is always enabled. Dynamic checking is also supported. If dynamic checking is enabled, new deftemplate facts have their values checked when created. This dynamic checking is disabled by default, but this behavior can be changed using the **set‑dynamic‑constraint‑checking** function. If a violation occurs while dynamic checking is performed, execution will be halted.

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

Asserting or referring to an ordered fact (such as in a LHS pattern) creates an "implied" deftemplate with a single implied multifield slot named *implied*. The name of the implied multifield slot is not printed when the fact is displayed. The implied deftemplate can be manipulated and examined in the same way as any user-defined deftemplate.

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

## 3.5 Deftemplate Inheritance

If a deftemplate specifies a base deftemplate using the **is-a** keyword, the defined deftemplate will inherit slots and slot attributes from the base deftemplate. A deftemplate can redefine inherited slots, but generally, a redefined slot can only be made more specific than the corresponding slot in the base deftemplate.

Example

(deftemplate person

(slot name (default \"Kelly Doe\"))

(slot gender (allowed-values male female))

(slot age (type INTEGER) (range 0 ?VARIABLE)))

(deftemplate female

(is-a person)

(slot gender (allowed-values female)))

(deftemplate girl

(is-a female)

(slot name (default \"Janey Doe\"))

(slot age (range 0 17)))

(deftemplate woman

(is-a female)

(slot name (default \"Jane Doe\"))

(slot age (range 18 ?VARIABLE)))

## 3.6 Certainty Factors

CLIPS provides a mechanism for using MYCIN-style certainty factors with facts. MYCIN was an expert system developed in the 1970s to identify bacterial infections. It provided an ad hoc mechanism called certainty factors to indicate the degree of confidence in a particular piece of information. Certainty factors in MYCIN are numbers in the range of -1.0 to 1.0, where 1.0 indicates absolute certainty that the information is true, and -1.0 indicates absolute certainty that the information is false. In MYCIN, if the same information is derived from multiple sources, the certainty factors are combined to indicate a new degree of confidence in that information.

In CLIPS, certainty factors are represented using integers in the range from -100 to 100. To use certainty factors, a deftemplate must inherit from the Certainty Factor Deftemplate (CFD). This deftemplate is not explicitly defined, but for the purpose of inheritance, it behaves as though it were defined as follows:

(deftemplate CFD

(slot CF (type INTEGER) (range -100 100) (default 100)))

Deftemplates that inherit from the *CFD* deftemplate cannot redefine the *CF* slot.

Example

CLIPS\> (clear)

CLIPS\> (deftemplate symptom (is-a CFD) (slot name))

CLIPS\> (assert (symptom (name fever) (CF 60)))

\<Fact-1\>

CLIPS\> (assert (symptom (name rash) (CF 40)))

\<Fact-2\>

CLIPS\> (assert (symptom (name red-eyes) (CF -20)))

\<Fact-3\>

CLIPS\> (facts)

f-1 (symptom (CF 60) (name fever))

f-2 (symptom (CF 40) (name rash))

f-3 (symptom (CF -20) (name red-eyes))

For a total of 3 facts.

CLIPS\>

### 3.6.1 Combining Certainty Factors

By default, CLIPS does not allow duplicates of facts. When a *CFD* fact is asserted that duplicates an existing *CFD* fact (for all slots except the *CF* slot), the certainty factor of the existing *CFD* fact is combined with that of the duplicate fact using the following formula:

$${CF}_{Combine}\left( {CF}_{1},{CF}_{2} \right) = \ \left\{ \ \ \begin{matrix}
{CF}_{1} + {CF}_{2} - \frac{{CF}_{1}{CF}_{2}}{100} & if\ {CF}_{1},\ {CF}_{2} > 0 \\
{CF}_{1} + {CF}_{2} + \frac{{CF}_{1}{CF}_{2}}{100} & if\ {CF}_{1},\ {CF}_{2} > 0 \\
0 & if\ {CF}_{1}{+ \ CF}_{2} = 0 \\
\frac{{CF}_{1} + {CF}_{2}}{100 - min(\left| {CF}_{1} \right|,|{CF}_{2}|)} & otherwise
\end{matrix} \right.\ $$

The combined certainty factor is calculated using floating-point numbers, and the final value is rounded to an integer.

Example

CLIPS\> (assert (symptom (name fever) (CF -20)))

\<Fact-1\>

CLIPS\> (assert (symptom (name rash) (CF 40)))

\<Fact-2\>

CLIPS\> (facts)

f-1 (symptom (CF 50) (name fever))

f-2 (symptom (CF 64) (name rash))

f-3 (symptom (CF -20) (name red-eyes))

For a total of 3 facts.

CLIPS\>

### 3.6.2 Certainty Thresholds and Adjustments in Rules

Patterns in rules will not match facts with a certainty factor of less than 20. The fact will appear in the fact-list, but pattern matching will not be performed.

Example

CLIPS\> (deftemplate diagnosis (is-a CFD) (slot name))

CLIPS\>

(defrule measles

(declare (certainty 80))

(symptom (name fever))

(symptom (name rash))

(symptom (name red-eyes))

=\>

(assert (diagnosis (name measles))))

CLIPS\> (agenda)

CLIPS\> (matches measles)

Matches for Pattern 1

f-1

Matches for Pattern 2

f-2

Matches for Pattern 3

None

Partial matches for CEs 1 - 2

f-1,f-2

Partial matches for CEs 1 - 3

None

Activations

None

(2 1 0)

CLIPS\> (assert (symptom (name red-eyes) (CF 90)))

\<Fact-3\>

CLIPS\> (facts)

f-1 (symptom (CF 50) (name fever))

f-2 (symptom (CF 64) (name rash))

f-3 (symptom (CF 88) (name red-eyes))

For a total of 3 facts.

CLIPS\> (agenda)

0 measles: f-1,f-2,f-3

For a total of 1 activation.

CLIPS\>

The certainty factors of *CFD* facts asserted during the execution of a rule are adjusted using the tally of the conditions of the rule and the certainty factor specified for the rule in the rule's declare statement. The tally of the conditions is the minimum certainty value found in the facts from the rule activation. If there are no facts with certainty values in the conditions, the tally for the conditions will be 100. Similarly, if no certainty is specified in the rule's declare statement, the default of 100 will be used.

The adjusted certainty factor for a fact asserted by a rule is computed by dividing both the rule tally and the rule certainty by 100, multiplying them together, and then multiplying the result by the fact's certainty factor:

$${CF}_{Adjusted}\left( Tally,{CF}_{Rule},{CF}_{Fact} \right) = \ \frac{Tally}{100} \cdot \frac{{CF}_{Rule}}{100} \cdot {CF}_{Fact}$$

In the previous example, where the measles rule is activated and executed, f-1 has a certainty value of 50, f-2 has a certainty value of 64, and f-3 has a certainty value of 88. Consequently, the tally for the rule conditions is 50. This value is divided by 100 to yield 0.5. The rule certainty is specified as 80, which, when divided by 100, yields 0.8. When the measles diagnosis fact is asserted by the rule with the default certainty factor of 100, this value is multiplied by 0.5 and 0.8 to calculate an adjusted value of 40.

Example

CLIPS\> (run 1)

CLIPS\> (facts)

f-1 (symptom (CF 50) (name fever))

f-2 (symptom (CF 64) (name rash))

f-3 (symptom (CF 88) (name red-eyes))

f-4 (diagnosis (CF 40) (name measles))

For a total of 4 facts.

CLIPS\>

When the certainty factor for an existing fact changes as a result of being combined with a new assertion, but remains either above or below the certainty factor threshold of 20, the *CF* slot value is changed using an **update** command. This means that only rules containing patterns explicitly matching the *CF* slot will be reevaluated. When the certainty factor moves from below the threshold to above or from above the threshold to below, the *CF* slot value is changed using a **modify** command. This will trigger the reevaluation of all patterns that could match the fact.

## 3.7 Named Deftemplates

TBD Proofread Start

CLIPS provides a mechanism for assigning names which can be used for referring to that fact. All facts have an index and fact-address which can be used to refer to fact to provide linkages, but these can change (for example, if the facts are saved to a file and then reloaded, the fact-index and fact-address will change removing the linkage). Unlike instance-names, which their own type, fact-names are symbols. CLIPS treats any symbol being with the @ character as a fact-name. In situations where fact-names can utilized, CLIPS looks for the @ at the beginning of the fact-name.

To use fact-names, a deftemplate must inherit from the Named Deftemplate (ND). This deftemplate is not explicitly defined, but for the purpose of inheritance, it behaves as though it were defined as follows:

(deftemplate ND

(slot name (type SYMBOL)))

Deftemplates that inherit from the *ND* deftemplate cannot redefine the *name* slot.

A **fact-name** is a symbol that begins with the @ character and is used to identify a fact. Two facts are not permitted to have the same fact-name. When passed as an argument to a generic function, fact-names are converted to the fact-address of the corresponding fact.

A fact-name is a symbol beginning with the @ character, assigned to the **name** slot of facts inheriting from the **ND** deftemplate. The fact-name can be explicitly specified when the fact is asserted; otherwise, one will be automatically generated. The default value for the fact-name is generated by prepending the @ character to the fact identifier. For example, the fact-name for the fact with a fact-index of 1 would be \@f-1. If the default fact-name is already assigned to another fact, then an additional hyphen and an integer are appended to the fact-name to generate an unassigned fact-name.

Example

CLIPS\>

(deftemplate rectangle

(is-a ND)

(slot width)

(slot height))

CLIPS\>

(defmethod area ((?r rectangle))

(\* ?r:width ?r:height))

CLIPS\>

(assert (rectangle (width 2) (height 3)))

\@f-1

CLIPS\> (facts)

f-1 (rectangle (name \@f-1) (width 2) (height 3))

For a total of 1 fact.

CLIPS\> (area \@f-1)

6

CLIPS\> (modify \@f-1 (height 5))

\@f-1

CLIPS\> (area \@f-1)

10

CLIPS\>

TBD Proofread End
