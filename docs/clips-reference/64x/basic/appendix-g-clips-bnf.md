# Appendix G: CLIPS BNF

Data Types

\<symbol\> ::= **A valid symbol as specified**

**in section 2.3.1**

\<string\> ::= **A valid string as specified**

**in section 2.3.1**

\<float\> ::= **A valid float as specified**

**in section 2.3.1**

\<integer\> ::= **A valid integer as specified**

**in section 2.3.1**

\<instance-name\> ::= **A valid instance‑name as specified**

**in section 2.3.1**

\<number\> ::= \<float\> \| \<integer\>

\<lexeme\> ::= \<symbol\> \| \<string\>

\<constant\> ::= \<symbol\> \| \<string\> \| \<integer\> \|

\<float\> \| \<instance‑name\>

\<comment\> ::= \<string\>

\<variable-symbol\> ::= **A symbol beginning with an**

**alphabetic character**

\<function-name\> ::= **Any symbol which corresponds to a**

**system or user defined function, a**

**deffunction name, or a defgeneric**

**name**

\<file-name\> ::= **A symbol or string which is a valid**

**file name (including path**

**information) for the operating**

**system under which CLIPS is running**

\<slot-name\> ::= **A valid deftemplate slot name**

\<\...-name\> ::= **A \<symbol\> where the ellipsis**

**indicate what the symbol represents.**

**For example, \<rule-name\> is a symbol**

**which represents the name of a rule.**

Variables and Expressions

\<single-field-variable\> ::= ?\<variable-symbol\>

\<multifield-variable\> ::= \$?\<variable-symbol\>

\<global-variable\> ::= ?\*\<symbol\>\*

\<variable\> ::= \<single-field-variable\> \|

\<multifield-variable\> \|

\<global-variable\>

\<function-call\> ::= (\<function-name\> \<expression\>\*)

\<expression\> ::= \<constant\> \| \<variable\> \|

\<function-call\>

\<action\> ::= \<expression\>

\<\...-expression\> ::= **An \<expression\> which returns**

**the type indicated by the**

**ellipsis. For example,**

**\<integer-expression\> should**

**return an integer.**

Constructs

\<CLIPS-program\> ::= \<construct\>\*

\<construct\> ::= \<deffacts-construct\> \|

\<deftemplate-construct\> \|

\<defglobal-construct\> \|

\<defrule-construct\> \|

\<deffunction-construct\> \|

\<defgeneric-construct\> \|

\<defmethod-construct\> \|

\<defclass-construct\> \|

\<definstance-construct\> \|

\<defmessage-handler-construct\> \|

\<defmodule-construct\>

Deffacts Construct

\<deffacts-construct\> ::= (deffacts \<deffacts-name\> \[\<comment\>\]\
\<RHS-pattern\>\*)

Deftemplate Construct

\<deftemplate-construct\>

::= (deftemplate \<deftemplate-name\>

\[\<comment\>\]

\<slot-definition\>\*)

\<slot-definition\> ::= \<single-slot-definition\> \|

\<multislot-definition\>

\<single-slot-definition\>

::= (slot \<slot-name\> \<template-attribute\>\*)

\<multislot-definition\>

::= (multislot \<slot-name\>

\<template-attribute\>\*)

\<template-attribute\>

::= \<default-attribute\> \|

\<constraint-attribute\>

\<default-attribute\>

::= (default ?DERIVE \| ?NONE \| \<expression\>\*) \|

(default-dynamic \<expression\>\*)

Fact Specification

\<RHS-pattern\> ::= \<ordered-RHS-pattern\> \|

\<template-RHS-pattern\>

\<ordered-RHS-pattern\> ::= (\<symbol\> \<RHS-field\>+)

\<template-RHS-pattern\> ::= (\<deftemplate-name\> \<RHS-slot\>\*)

\<RHS-slot\> ::= \<single-field-RHS-slot\> \|

\<multifield-RHS-slot\>

\<single-field-RHS-slot\> ::= (\<slot-name\> \<RHS-field\>)

\<multifield-RHS-slot\> ::= (\<slot-name\> \<RHS-field\>\*)

\<RHS-field\> ::= \<variable\> \|

\<constant\> \|

\<function-call\>

Defrule Construct

\<defrule-construct\> ::= (defrule \<rule-name\> \[\<comment\>\]

\[\<declaration\>\]

\<conditional-element\>\*\
=\>\
\<action\>\*)

\<declaration\> ::= (declare \<rule-property\>+)

\<rule-property\> ::= (salience \<integer-expression\>) \|

(auto-focus \<boolean-symbol\>)

\<boolean-symbol\> ::= TRUE \| FALSE

\<conditional-element\> ::= \<pattern-CE\> \|

\<assigned-pattern-CE\> \|

\<not-CE\> \| \<and-CE\> \| \<or-CE\> \|

\<logical-CE\> \| \<test-CE\> \|

\<exists-CE\> \| \<forall-CE\>

\<pattern-CE\> ::= \<ordered-pattern-CE\> \|

\<template-pattern-CE\> \|

\<object-pattern-CE\>

\<assigned-pattern-CE\> ::= \<single-field-variable\> \<- \<pattern-CE\>

\<not-CE\> ::= (not \<conditional-element\>)

\<and-CE\> ::= (and \<conditional-element\>+)

\<or-CE\> ::= (or \<conditional-element\>+)

\<logical-CE\> ::= (logical \<conditional-element\>+)

\<test-CE\> ::= (test \<function-call\>)

\<exists-CE\> ::= (exists \<conditional-element\>+)

\<forall-CE\> ::= (forall \<conditional-element\>

\<conditional-element\>+)

\<ordered-pattern-CE\> ::= (\<symbol\> \<constraint\>\*)

\<template-pattern-CE\> ::= (\<deftemplate-name\> \<LHS-slot\>\*)

\<object-pattern-CE\> ::= (object \<attribute-constraint\>\*)

\<attribute-constraint\> ::= (is-a \<constraint\>) \|

(name \<constraint\>) \|

(\<slot-name\> \<constraint\>\*)

\<LHS-slot\> ::= \<single-field-LHS-slot\> \|

\<multifield-LHS-slot\>

\<single-field-LHS-slot\> ::= (\<slot-name\> \<constraint\>)

\<multifield-LHS-slot\> ::= (\<slot-name\> \<constraint\>\*)

\<constraint\> ::= ? \| \$? \| \<connected-constraint\>

\<connected-constraint\>

::= \<single-constraint\> \|

\<single-constraint\> **&** \<connected-constraint\> \|

\<single-constraint\> **\|** \<connected-constraint\>

\<single-constraint\> ::= \<term\> \| \~\<term\>

\<term\> ::= \<constant\> \|

\<single-field-variable\> \|

\<multifield-variable\> \|

:\<function-call\> \|

=\<function-call\>

Defglobal Construct

\<defglobal-construct\> ::= (defglobal \[\<defmodule-name\>\]

\<global-assignment\>\*)

\<global-assignment\> ::= \<global-variable\> = \<expression\>

\<global-variable\> ::= ?\*\<symbol\>\*

Deffunction Construct

\<deffunction-construct\>

::= (deffunction \<name\> \[\<comment\>\]

(\<regular-parameter\>\* \[\<wildcard-parameter\>\])

\<action\>\*)

\<regular-parameter\> ::= \<single-field-variable\>

\<wildcard-parameter\> ::= \<multifield-variable\>

Defgeneric Construct

\<defgeneric-construct\> ::= (defgeneric \<name\> \[\<comment\>\])

Defmethod Construct

\<defmethod-construct\>

::= (defmethod \<name\> \[\<index\>\] \[\<comment\>\]

(\<parameter-restriction\>\*

\[\<wildcard-parameter-restriction\>\])

\<action\>\*)

\<parameter-restriction\>

::= \<single-field-variable\> \|

(\<single-field-variable\> \<type\>\* \[\<query\>\])

\<wildcard-parameter-restriction\>

::= \<multifield-variable\> \|

(\<multifield-variable\> \<type\>\* \[\<query\>\])

\<type\> ::= \<class-name\>

\<query\> ::= \<global-variable\> \| \<function-call\>

Defclass Construct

\<defclass-construct\> ::= (defclass \<name\> \[\<comment\>\]

(is-a \<superclass-name\>+)

\[\<role\>\]

\[\<pattern-match-role\>\]

\<slot\>\*

\<handler-documentation\>\*)

\<role\> ::= (role concrete \| abstract)

\<pattern-match-role\>

::= (pattern-match reactive \| non-reactive)

\<slot\> ::= (slot \<name\> \<facet\>\*) \|

(single-slot \<name\> \<facet\>\*) \|

(multislot \<name\> \<facet\>\*)

\<facet\> ::= \<default-facet\> \| \<storage-facet\> \|

\<access-facet\> \| \<propagation-facet\> \|

\<source-facet\> \| \<pattern-match-facet\> \|

\<visibility-facet\> \| \<create-accessor-facet\>

\<override-message-facet\> \| \<constraint-attribute\>

\<default-facet\> ::=

(default ?DERIVE \| ?NONE \| \<expression\>\*) \|

(default-dynamic \<expression\>\*)

\<storage-facet\> ::= (storage local \| shared)

\<access-facet\>

::= (access read-write \| read-only \| initialize-only)

\<propagation-facet\> ::= (propagation inherit \| no-inherit)

\<source-facet\> ::= (source exclusive \| composite)

\<pattern-match-facet\>

::= (pattern-match reactive \| non-reactive)

\<visibility-facet\> ::= (visibility private \| public)

\<create-accessor-facet\>

::= (create-accessor ?NONE \| read \| write \| read-write)

\<override-message-facet\>

::= (override-message ?DEFAULT \| \<message-name\>)

\<handler-documentation\>

::= (message-handler \<name\> \[\<handler-type\>\])

\<handler-type\> ::= primary \| around \| before \| after

Defmessage-handler Construct

\<defmessage-handler-construct\>

::= (defmessage-handler \<class-name\>

\<message-name\> \[\<handler‑type\>\] \[\<comment\>\]

(\<parameter\>\* \[\<wildcard-parameter\>\])

\<action\>\*)

\<handler-type\> ::= around \| before \| primary \| after

\<parameter\> ::= \<single-field-variable\>

\<wildcard-parameter\> ::= \<multifield-variable\>

Definstances Construct

\<definstances-construct\>

::= (definstances \<definstances-name\>

\[active\] \[\<comment\>\]

\<instance-template\>\*)

\<instance-template\> ::= (\<instance-definition\>)

\<instance-definition\> ::= \[\<instance-name-expression\>\] of\
\<class-name-expression\>\
\<slot-override\>\*

\<slot-override\> ::= (\<slot-name-expression\> \<expression\>\*)

Defmodule Construct

\<defmodule-construct\> ::= (defmodule \<module-name\> \[\<comment\>\]

\<port-specification\>\*)

\<port-specification\> ::= (export \<port-item\>) \|

(import \<module-name\> \<port-item\>)

\<port-item\> ::= ?ALL \|

?NONE \|

\<port-construct\> ?ALL \|

\<port-construct\> ?NONE \|

\<port-construct\> \<construct-name\>+

\<port-construct\> ::= deftemplate \| defclass \|

defglobal \| deffunction \|

defgeneric

Constraint Attributes

\<constraint-attribute\>

::= \<type-attribute\> \|

\<allowed-constant-attribute\> \|

\<range-attribute\> \|

\<cardinality-attribute\>

\<type-attribute\> ::= (type \<type-specification\>)

\<type-specification\> ::= \<allowed-type\>+ \| ?VARIABLE

\<allowed-type\> ::= SYMBOL \| STRING \| LEXEME \|

INTEGER \| FLOAT \| NUMBER \|

INSTANCE-NAME \| INSTANCE-ADDRESS \|

INSTANCE \| EXTERNAL-ADDRESS \|

FACT-ADDRESS

\<allowed-constant-attribute\>

::= (allowed-symbols \<symbol-list\>) \|

(allowed-strings \<string-list\>) \|

(allowed-lexemes \<lexeme-list\> \|

(allowed-integers \<integer-list\>) \|

(allowed-floats \<float-list\>) \|

(allowed-numbers \<number-list\>) \|

(allowed-instance-names \<instance-list\>) \|

(allowed-classes \<class-name-list\>) \|

(allowed-values \<value-list\>)

\<symbol-list\> ::= \<symbol\>+ \| ?VARIABLE

\<string-list\> ::= \<string\>+ \| ?VARIABLE

\<lexeme-list\> ::= \<lexeme\>+ \| ?VARIABLE

\<integer-list\> ::= \<integer\>+ \| ?VARIABLE

\<float-list\> ::= \<float\>+ \| ?VARIABLE

\<number-list\> ::= \<number\>+ \| ?VARIABLE

\<instance-name-list\> ::= \<instance-name\>+ \| ?VARIABLE

\<class-name-list\> ::= \<class-name\>+ \| ?VARIABLE

\<value-list\> ::= \<constant\>+ \| ?VARIABLE

\<range-attribute\> ::= (range \<range-specification\>

\<range-specification\>)

\<range-specification\> ::= \<number\> \| ?VARIABLE

\<cardinality-attribute\>

::= (cardinality \<cardinality-specification\>

\<cardinality-specification\>)

\<cardinality-specification\>

::= \<integer\> \| ?VARIABLE
