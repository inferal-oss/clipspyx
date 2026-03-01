# Section 10: Defmodule Construct

CLIPS provides support for the modular development and execution of knowledge bases with the **defmodule** construct. CLIPS modules allow a set of constructs to be grouped together such that explicit control can be maintained over restricting the access of the constructs by other modules. This type of control is similar to global and local scoping used in languages such as C (note, however, that the global scoping used by CLIPS is strictly hierarchical and in one direction only---if module A can see constructs from module B, then it is not possible for module B to see any of module A's constructs). Modules are also used by rules to provide execution control. See Sections 13.12, 12.20, and 14.7 for additional information on functions and commands used with modules.

## 10.1 Defining Modules

Modules are defined using the defmodule construct.

Syntax

(defmodule \<module-name\> \[\<comment\>\]

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

A defmodule cannot be redefined or deleted once it is defined (with the exception of the MAIN module which can be redefined once). The only way to delete a module is with the **clear** command. Upon startup and after a **clear** command, CLIPS automatically constructs the following defmodule.

(defmodule MAIN)

All of the predefined system classes belong to the MAIN module. However, it is not necessary to import or export the system classes; they are always in scope. Otherwise, the predefined MAIN module does not import or export any constructs. However, unlike other modules, the MAIN module can be redefined once after startup or a **clear** command.

Example

(defmodule CONSTANTS (export defglobal max-users))

(defmodule DATA (export deftemplate ?ALL))

(defmodule UTILITIES (export ?ALL))

(defmodule PROCESS

(import CONSTANTS defglobal ?ALL)

(import UTILITIES ?ALL)

(import DATA deftemplate ?ALL)

(export ?ALL))

## 10.2 Specifying a Construct's Module

The module in which a construct is placed can be specified when the construct is defined. The deffacts, deftemplate, defrule, deffunction, defgeneric, defclass, and definstances constructs all specify the module for the construct by including it as part of the name. The module of a defglobal construct is indicated by specifying the module name after the defglobal keyword. The module of a defmessage‑handler is specified as part of the class specifier. The module of a defmethod is specified as part of the generic function specifier.

Example 1

(defmodule COMMON (export ?ALL))

(deftemplate COMMON::sensor\
(slot name)\
(slot value))

(deftemplate COMMON::fault

(slot name))

(defglobal COMMON ?\*sensor-count\* = 20)

(defclass COMMON::COMPONENT (is-a USER)

(slot flux)

(slot flow))

(defmessage-handler COMMON::COMPONENT get-charge ()\
(\* ?self:flux ?self:flow))

(defmethod COMMON::combine ((?x COMPONENT) (?y COMPONENT))\
(+ (send ?x get-charge) (send ?y get-charge)))

(defmodule DETECT (import COMMON ?ALL))

(defrule DETECT::Find-Fault\
(sensor (name ?name) (value bad))\
=\>\
(assert (fault (name ?name))))

Example 2

CLIPS\> (clear)

CLIPS\> (defmodule START)

CLIPS\> (defmodule END)

CLIPS\> (clear)

CLIPS\> (defmodule START)

CLIPS\> (defmodule FINISH)

CLIPS\> (defrule close =\>)

CLIPS\> (defrule START::open =\>)

CLIPS\> (list-defrules)

open

For a total of 1 defrule.

CLIPS\> (set-current-module FINISH)

START

CLIPS\> (list-defrules)

close

For a total of 1 defrule.

CLIPS\>

## 10.3 Specifying Modules

Commands such as **undefrule** and **ppdefrule** require the name of a construct on which to operate. With modules, however, it is possible to have a construct with the same name in two different modules. The modules associated with a name can be specified either explicitly or implicitly. To explicitly specify a name's module the module name (a symbol) is listed followed by two colons, ::, and then the name is listed. The module name followed by :: is referred to as a **module specifier**. For example, MAIN::find‑stuff, refers to the find‑stuff construct in the MAIN module. A module can also be implicitly specified since there is always a current module. The current module is changed whenever a defmodule construct is defined or the **set‑current‑module** function is used. The MAIN module is automatically defined by CLIPS and by default is the current module when CLIPS is started or after a **clear** command is issued. Thus the name find‑stuff would implicitly have the MAIN module as its module when CLIPS is first started.

CLIPS\> (clear)

CLIPS\> (defmodule MATH-CONSTANTS)

CLIPS\> (defglobal MATH-CONSTANTS ?\*chebyshev-constant\* = 0.590170299508048)

CLIPS\> (defmodule SYSTEM-CONSTANTS)

CLIPS\> (defglobal SYSTEM-CONSTANTS ?\*max-files\* = 100)

CLIPS\> (ppdefglobal max-files)

(defglobal SYSTEM-CONSTANTS ?\*max-files\* = 100)

CLIPS\> (ppdefglobal SYSTEM-CONSTANTS::max-files)

(defglobal SYSTEM-CONSTANTS ?\*max-files\* = 100)

CLIPS\> (ppdefglobal chebyshev-constant)

\[PRNTUTIL1\] Unable to find defglobal \'chebyshev-constant\'.

CLIPS\> (ppdefglobal MATH-CONSTANTS::chebyshev-constant)

(defglobal MATH-CONSTANTS ?\*chebyshev-constant\* = 0.590170299508048)

CLIPS\>

## 10.4 Importing and Exporting Constructs

Unless specifically **exported** and **imported**, the constructs of one module may not be used by another module. A construct is said to be visible or within scope of a module if that construct can be used by the module. For example, if module *SCHEDULE* wants to use the *person* deftemplate defined in module *COMMON*, then module *COMMON* must export the *person* deftemplate and module *SCHEDULE* must import the *person* deftemplate from module *COMMON*.

CLIPS\> (clear)

CLIPS\> (defmodule COMMON)

CLIPS\>

(deftemplate COMMON::person

(slot name)

(slot position)

(multislot available))

CLIPS\> (defmodule SCHEDULE)

CLIPS\>

(defrule SCHEDULE::unavailable

(person (name ?name) (availbale))

=\>

(println ?name \" is unavailable\" crlf))

\[PRNTUTIL2\] Syntax Error: Check appropriate syntax for defrule.

ERROR:

(defrule SCHEDULE::unavailable

(person (

CLIPS\> (clear)

CLIPS\> (defmodule COMMON (export deftemplate person))

CLIPS\>

(deftemplate COMMON::person

(slot name)

(slot position)

(multislot available))

CLIPS\> (defmodule SCHEDULE (import COMMON deftemplate person))

CLIPS\>

(defrule SCHEDULE::unavailable

(person (name ?name) (available))

=\>

(println ?name \" is unavailable\" crlf))

CLIPS\>

CLIPS will not allow a module or other construct to be defined that causes two constructs with the same name to be visible within the same module.

### 10.4.1 Exporting Constructs

The export specification in a defmodule definition is used to indicate which constructs will be accessible to other modules importing from the module being defined. Only deftemplates (including those created for ordered facts), defclasses, defglobals, deffunctions, and defgenerics may be exported. A module may export any valid constructs that are visible to it (not just constructs that it defines).

There are three different types of export specifications. First, a module may export all valid constructs that are visible to it. This accomplished by following the *export* keyword with the *?ALL* keyword. Second, a module may export all valid constructs of a particular type that are visible to it. This accomplished by following the *export* keyword with the name of the construct type followed by the *?ALL* keyword. Third, a module may export specific constructs of a particular type that are visible to it. This accomplished by following the *export* keyword with the name of the construct type followed by the name of one or more visible constructs of the specified type. In the following code, defmodule *COMMON* exports all of its constructs; defmodule *DATA* exports all of its deftemplates; and defmodule *CONSTANTS* exports the *Chebyshev*, MKB, and *Smarandache* defglobals.

(defmodule COMMON (export ?ALL))

(defmodule DATA (export deftemplate ?ALL))

(defmodule CONSTANTS (export defglobal Chebyshev MKB Smarandache))

The ?NONE keyword may be used in place of the ?ALL keyword to indicate either that no constructs are exported from a module or that no constructs of a particular type are exported from a module.

Defmethods and defmessage‑handlers cannot be explicitly exported. Exporting a defgeneric automatically exports all associated defmethods. Exporting a defclass automatically exports all associated defmessage‑handlers. Deffacts, definstances, and defrules are never exported regardless of the export settings for a module.

### 10.4.2 Importing Constructs

The import specification in a defmodule definition is used to indicate which constructs the module being defined will use from other modules. Only deftemplates, defclasses, defglobals, deffunctions, and defgenerics may be imported. Deffacts, definstances, and defrules are never imported regardless of the import settings for a module.

There are three different types of import specifications. First, a module may import all valid constructs that are visible to a specified module. This accomplished by following the *import* keyword with a module name followed by the *?ALL* keyword. Second, a module may import all valid constructs of a particular type that are visible to a specified module. This accomplished by following the *import* keyword with a module name followed by the name of the construct type followed by the *?ALL* keyword. Third, a module may import specific constructs of a particular type that are visible to it. This accomplished by following the *import* keyword with a module name followed by the name of the construct type followed by the name of one or more visible constructs of the specified type. In the following code, defmodule *START* imports all of module *COMMON*'s constructs; defmodule *UPDATE* imports all of module *DATA*'s deftemplates; and defmodule *COMPUTE* imports the *Chebyshev*, *MKB*, and *Smarandache* defglobals from module *CONSTANTS*.

(defmodule START (import COMMON ?ALL))

(defmodule UPDATE (import DATA deftemplate ?ALL))

(defmodule COMPUTE (import CONSTANTS defglobal Chebyshev MKB Smarandache))

The ?NONE keyword may be used in place of the ?ALL keyword to indicate either that no constructs are imported from a module or that no constructs of a particular type are imported from a module.

Defmethods and defmessage‑handlers cannot be explicitly imported. Importing a defgeneric automatically imports all associated defmethods. Importing a defclass automatically imports all associated defmessage‑handlers. Deffacts, definstances, and defrules cannot be imported.

A module must be defined before it is used in an import specification. In addition, if specific constructs are listed in the import specification, they must already be defined in the module exporting them. It is not necessary to import a construct from the module in which it is defined in order to use it. A construct can be indirectly imported from a module that directly imports and then exports the module to be used.

## 10.5 Importing and Exporting Facts and Instances

Facts and instances are "owned" by the module in which their corresponding deftemplate or defclass is defined, *not* by the module which creates them. Facts and instances are thus visible only to those modules that import the corresponding deftemplate or defclass. This allows a knowledge base to be partitioned such that rules and other constructs can only "see" those facts and instances that are of interest to them. Instance names, however, are global in scope, so it is still possible to send messages to an instance of a class that is not in scope.

Example

CLIPS\> (clear)

CLIPS\> (defmodule COMMON (export deftemplate player team))

CLIPS\>

(deftemplate COMMON::player

(slot name)

(slot age))

CLIPS\>

(deftemplate COMMON::team

(slot name)

(multislot players))

CLIPS\>

(deffacts COMMON::league

(player (name Fred) (age 15))

(player (name Jill) (age 13))

(player (name Sam) (age 14))

(team (name Tigers) (players Fred Jill Sam)))

CLIPS\> (defmodule ELIGIBLE (import COMMON deftemplate player))

CLIPS\> (reset)

CLIPS\> (facts COMMON)

f-1 (player (name Fred) (age 15))

f-2 (player (name Jill) (age 13))

f-3 (player (name Sam) (age 14))

f-4 (team (name Tigers) (players Fred Jill Sam))

For a total of 4 facts.

CLIPS\> (facts ELIGIBLE)

f-1 (player (name Fred) (age 15))

f-2 (player (name Jill) (age 13))

f-3 (player (name Sam) (age 14))

For a total of 3 facts.

CLIPS\>

### 10.5.1 Specifying Instance‑Names

Instance‑names are required to be unique regardless of the module that owns them. However, the syntax of instance‑names also allows module specifications (note that the left and right brackets in bold are to be typed and do not indicate an optional part of the syntax).

Syntax

\<instance-name\> ::= **\[**\<symbol\>**\]** \|

**\[**::\<symbol\>**\]** \|

**\[**\<module\>::symbol\>**\]**

Specifying just a symbol as the instance‑name, such as \[Rolls‑Royce\], will search for the instance in all modules. Specifying only the :: before the name, such as \[::Rolls‑Royce\], will search for the instance first in the current module and then recursively in the imported modules as defined in the module definition. Specifying both a symbol and a module name, such as \[CARS::Rolls‑Royce\], searches for the instance only in the specified module.

## 10.6 Modules and Rule Execution

Each module has its own pattern matching network for its rules and its own agenda. When a **run** command is given, the agenda of the module that is the current focus is executed (note that the **reset** and **clear** commands make the MAIN module the current focus). Rule execution continues until another module becomes the current focus, no rules are left on the agenda, or the **return** function is used from the RHS of a rule. Whenever the module with current focus has no remaining activations on its agenda, the current focus is removed from the focus stack, and the next module on the focus stack becomes the current focus. Before a rule executes, the current module is changed to the module in which the executing rule is defined (the current focus), but otherwise the current focus and the current module can be different. The current focus can be changed by using the **focus** command (see Section 14.7.3).

Example

CLIPS\> (clear)

CLIPS\> (defmodule MAIN (export deftemplate list))

CLIPS\> (deftemplate list (slot name) (multislot numbers))

CLIPS\>

(deffacts initial

(list (name A) (numbers 3 8 2 9 3 4 7))

(list (name B) (numbers 1 6 3 9 5 8 0)))

CLIPS\>

(defrule start

=\>

(focus SORT PRINT))

CLIPS\> (defmodule SORT (import MAIN deftemplate list))

CLIPS\>

(defrule sort

?f \<- (list (numbers \$?b ?x ?y&:(\> ?x ?y) \$?e))

=\>

(modify ?f (numbers ?b ?y ?x ?e)))

CLIPS\> (defmodule PRINT (import MAIN deftemplate list))

CLIPS\>

(defrule print

(list (name ?name) (numbers \$?numbers))

=\>

(println \"Sorted list \" ?name \" is \" (implode\$ ?numbers)))

CLIPS\> (reset)

CLIPS\> (run)

Sorted list A is 2 3 3 4 7 8 9

Sorted list B is 0 1 3 5 6 8 9

CLIPS\>
