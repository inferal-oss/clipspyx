# Section 6: Defglobal Construct

With the **defglobal** construct, global variables can be defined, set, and accessed within the CLIPS environment. Global variables can be accessed as part of the pattern matching process, but changing them does not invoke the pattern matching process. The **bind** function is used to set the value of global variables. Global variables are reset to their original value when the **reset** command is performed or when **bind** is called for the global with no values. This behavior can be changed using the **set‑reset‑globals** function. Global variables can be removed by using the **clear** command or the **undefglobal** command. If the globals item is being watched as a result of the **watch** command, then an informational message will be displayed each time the value of a global variable is changed.

Syntax

(defglobal \[\<defmodule-name\>\] \<global-assignment\>\*)

\<global-assignment\> ::= \<global-variable\> = \<expression\>

\<global-variable\> ::= ?\*\<symbol\>\*

There may be multiple defglobal constructs and any number of global variables may be defined in each defglobal statement. The optional \<defmodule‑name\> indicates the module in which the defglobals will be defined. If none is specified, the globals will be placed in the current module. If a variable was defined in a previous defglobal construct, its value will be replaced by the value found in the new defglobal construct. If an error is encountered when defining a defglobal construct, any global variable definitions that occurred before the error was encountered will still remain in effect.

Commands that operate on defglobals such as ppdefglobal and undefglobal expect the symbolic name of the global without the astericks (e.g., use the symbol *max* when you want to refer to the global variable ?\*max\*).

Global variables may be used anyplace that a local variable could be used (with two exceptions). Global variables may not be used as a parameter variable for a deffunction, defmethod, or message-handler. Global variables may not be used in the same way that a local variable is used on the LHS of a rule to bind a value. Therefore, the following rule is illegal

(defrule example

(number ?\*x\*)

=\>)

The following rule, however, is legal.

(defrule example

(number ?y&:(\> ?y ?\*x\*))

=\>)

Note that this rule will not necessarily be updated when the value of ?\*x\* is changed. For example, if ?\*x\* is 4 and the fact (number 3) is added, then the rule is not satisfied. If the value of ?\*x\* is now changed to 2, the rule will not be activated.

Example

(defglobal

?\*x\* = 3

?\*y\* = ?\*x\*

?\*z\* = (+ ?\*x\* ?\*y\*)

?\*q\* = (create\$ a b c))

 Usage Note

The inappropriate use of globals within rules is quite often the first resort of beginning programmers who have reached an impasse in developing a program because they do not fully understand how rules and pattern matching work. As it relates to this issue, the following sentence from the beginning of this section is important enough to repeat:

*Global variables can be accessed as part of the pattern matching process, but changing them does not invoke the pattern matching process.*

Facts and instances are the primary mechanism that should be used to pass information from one rule to another specifically because they *do* invoke pattern matching. A change to a slot value of a fact or instance will trigger pattern matching ensuring that a rule is aware of the current state of that fact or instance. Since a change to a global variable does not trigger pattern matching, it is possible for a rule to remain activated based on a past value of a global variable and that is undesirable in most situations.

It's worth pointing out that facts and instances are no less 'global' in nature than global variables. Just as a rule can access any global variable that's visible (i.e., it hasn't been hidden through the use of modules), so too can it access any fact or instance belonging to a deftemplate or defclass that's visible. In the case of a fact, one can either pattern-match for the fact on the LHS of a rule or use the fact-set query functions from the RHS of a rule. In the case of an instance, pattern matching and instance-set query functions can also be used, and in addition an instance can be directly referenced by name just as a global variable can.

Common Problem

One of the more common situations in which it is tempting to use global variables is collecting a group of slot values from a fact. First attempts at rules to accomplish this task often loop endlessly because of rules inadvertently retriggered by changes. For example, the following rule will loop endlessly because the new *collection* fact asserted will create an activation with the same *data* fact that was just added to the *collection* fact:

> (defrule add-data
>
> (data ?data)
>
> ?c \<- (collection \$?collection)
>
> =\>
>
> (retract ?c)
>
> (assert (collection ?collection ?data)))

This problem can be corrected by removing the *data* fact just added to the *collection* fact:

(defrule add-data

?f \<- (data ?data)

?c \<- (collection \$?collection)

=\>

(retract ?f ?c)

(assert (collection ?collection ?data)))

Retracting the *data* facts, however, isn't a viable solution if these facts are needed by other rules. A non-destructive approach makes use of temporary facts created by a helper rule:

(defrule add-data-helper

(data ?data)

=\>

(assert (temp-data ?data)))

(defrule add-data

?f \<- (temp-data ?data)

?c \<- (collection \$?collection)

=\>

(retract ?f ?c)

(assert (collection ?collection ?data)))

It certainly looks simpler, however, to use a global variable to collect the slot values:

(defglobal ?\*collection\* = (create\$))

(defrule add-data

(data ?data)

=\>

(bind ?\*collection\* (create\$ ?\*collection\* ?data)))

Again, the drawback to this approach is that changes to a global variable do not trigger pattern matching, so in spite of its greater complexity the fact-based approach is still preferable.

Although it's important to understand how each of the previous approaches work, they're not practical solutions. If there are 1000 *data* facts, the add-data/add-add-helper rules will each fire 1000 times generating and retracting 2000 facts. The best solution is to use the fact-set query functions to iterate over all of the *data* facts and generate the *collection* fact as the result of a single rule firing:

> (defrule collect-data
>
> (collect-data)
>
> =\>
>
> (bind ?data (create\$))
>
> (do-for-all-facts ((?f data)) TRUE
>
> (bind ?data (create\$ ?data ?f:implied)))
>
> (assert (collection ?data)))

With this approach, the *collection* fact is available for pattern matching with the added benefit that there are no intermediate results generated in creating the fact. Typically if other rules are waiting for the finished result of the collection, they would need to have lower salience so that they aren't fired for the intermediate results:

(defrule print-data

(declare (salience -10))

(collection \$?data)

=\>

(println \"The collected data is \" ?data))

If the *data* facts are collected by a single rule firing, then the salience declaration is unnecessary.

Appropriate Uses

The primary use of global variables (in conjunction with rules) is in making a program easier to maintain. It is a rare situation where a global variable is required in order to solve a problem. One appropriate use of global variables is defining salience values shared among multiple rules:

(defglobal ?\*high-priority\* = 100)

(defrule rule-1

(declare (salience ?\*high-priority\*))

=\>)

(defrule rule-2

(declare (salience ?\*high-priority\*))

=\>)

Another use is defining constants used on the LHS or RHS of a rule:

(defglobal ?\*week-days\* =

(create\$ monday tuesday wednesday thursday friday saturday sunday))

(defrule invalid-day

(day ?day&:(not (member\$ ?day ?\*week-days\*)))

=\>

(println ?day \" is invalid\"))

(defrule valid-day

(day ?day&:(member\$ ?day ?\*week-days\*))

=\>

(println t ?day \" is valid\"))

A third use is passing information to a rule when it is desirable *not* to trigger pattern matching. In the following rule, a global variable is used to determine whether additional debugging information is printed:

(defglobal ?\*debug-print\* = nil)

(defrule rule-debug

?f \<- (info ?info)

=\>

(retract ?f)

(printout ?\*debug-print\* \"Retracting info \" ?info crlf))

If ?\*debug-print\* is set to nil, then the printout statement will not display any information. If the ?\*debug-print\* is set to t, then debugging information will be sent to the screen. Because ?\*debug-print\* is a global, it can be changed interactively without causing rules to be reactivated. This is useful when stepping through a program because it allows the level of information displayed to be changed without effecting the normal flow of the program.

It's possible, but a little more verbose, to achieve this same functionality using instances rather than global variables:

(defclass DEBUG-INFO

(is-a USER)

(slot debug-print))

(definstances debug

(\[debug-info\] of DEBUG-INFO (debug-print nil)))

(defrule rule-debug

?f \<- (info ?info)

=\>

(retract ?f)

(printout (send \[debug-info\] get-debug-print) \"Retracting info \" ?info crlf))

Changes to a slot of an instance won't trigger pattern matching in a rule unless the slot is specified on the LHS of that rule, thus you have explicit control over whether an instance slot triggers pattern matching. The following rule won't be retriggered if a change is made to the *debug-print* slot:

(defrule rule-debug

?f \<- (info ?info)

(object (is-a DEBUG-INFO) (name ?name))

=\>

(retract ?f)

(printout (send ?name get-debug-print) \"Retracting info \" ?info crlf))

This is a generally applicable technique and can be used in many situations to prevent rules from inadvertently looping when slot values are changed.

#
