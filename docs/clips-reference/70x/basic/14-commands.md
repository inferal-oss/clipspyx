# Section 14: Commands

This section describes commands primarily intended for use from the REPL. These commands may also be used from constructs and other places where functions can be used.

## 14.1 Environment Commands

The following commands control the CLIPS environment.

### 14.1.1 Loading Constructs From A File

The **load** command compiles the construct definitions stored in the file specified by the \<file‑name\> argument. If the **compilations** item is being watched as a result of the **watch** command, then an informational message (including the type and name of the construct) will be displayed for each construct loaded. If the **compilations** item is not being watched, then a character is printed for each construct loaded ("\*" for defrule, "\$" for deffacts, "%" for deftemplate, ":" for defglobal, "!" for deffunction, "\^" for defgeneric, "&" for defmethod, "#" for defclass, "\~" for defmessage‑handler, "@" for definstances, and "+" for defmodule). This command returns the symbol **TRUE** if the file was successfully loaded, otherwise FALSE is returned.

Syntax

(load \<file-name\>)

### 14.1.2 Loading Constructs From A File without Progress Information

The **load\*** command compiles the construct definitions stored in the file specified by the \<file‑name\> argument; however, unlike the **load** command, informational messsages are not printed to show the progress of compiling the file. Error messages are still printed if errors are encountered while loading the file. This command returns the symbol **TRUE** if the file was successfully loaded; otherwise, it returns the symbol **FALSE**.

Syntax

(load\* \<file-name\>)

### 14.1.3 Saving All Constructs To A File

The **save** command writes all construct definitions to the file specified by the \<file‑name\> argument, overwriting the file if it already exists. This command returns the symbol **TRUE** if the file was successfully saved; otherwise it returns the symbol **FALSE**. If the **conserve‑mem** command has been set to the symbol **on**, then the text representation of construct definitions is not saved when they are compiled and the **save** command will have no output.

Syntax

(save \<file-name\>)

### 14.1.4 Loading a Binary Image

The **bload** command loads the precompiled constructs stored in the binary file specified by the \<file‑name\> argument. The specified file must have been created by the **bsave** command. Loading a binary file is quicker than using the **load** command to load a UTF-8 text file. A **bload** clears all constructs (as well as all facts and instances). The only constructive/destructive operation that can occur after a **bload** is the **clear** command or the **bload** command (which clears the current binary image). This means that constructs cannot be loaded or deleted while a **bload** is in effect. In order to add constructs to a binary image, the original ASCII text file must be reloaded, the new constructs added, and then another **bsave** must be performed. This command returns the symbol **TRUE** if the file was successfully bloaded, otherwise FALSE is returned.

Binary images can be loaded into different compile‑time configurations of CLIPS, as long as the same version of CLIPS is used and all the functions and constructs needed by the binary image are supported. In addition, binary images should theoretically work across different hardware platforms if internal data representations are equivalent (e.g., same integer size, same byte order, same floating‑point format, etc), however, this is not recommended.

Syntax

(bload \<file-name\>)

### 14.1.5 Saving a Binary Image

The **bsave** command writes all of the construct definitions currently loaded to the file specified by the \<file‑name\> argument. The saved file is written using a binary format which results in faster load time. The text representation of construct definitions is not saved with a binary image (thus, commands like **ppdefrule** will show no output for any of the rules in the binary image). In addition, constraint information associated with constructs is not saved to the binary image unless dynamic constraint checking is enabled (using the **set‑dynamic‑constraint‑checking** command). This command returns the symbol **TRUE** if the file was successfully saved; otherwise, it returns the symbol **FALSE**.

Syntax

(bsave \<file-name\>)

### 14.1.6 Clearing CLIPS

The **clear** command removes all constructs and associated data (such as facts and instances). A clear may be performed safely at any time, however, certain constructs will not allow themselves to be deleted while they are in use. For example, while deffacts are being reset (by the **reset** command), it is not possible to remove them using the **clear** command. Note that the **clear** command does not effect many environment characteristics (such as the current conflict resolution strategy). This command has no return value.

Syntax

(clear)

### 14.1.7 Exiting CLIPS

The **exit** command terminates CLIPS execution. This command has no return value.

Syntax

(exit \[\<integer-expression\>\])

The optional \<integer-expression\> argument allows the exit status code to be specified and is passed to the C exit function.

### 14.1.8 Resetting CLIPS

The **reset** command removes all activations from the agenda, retracts all facts, deletes all instances, assigns global variables their initial values, asserts all facts from def­facts constructs, creates all instances from definstances constructs, and sets the current module and focus to the MAIN module. Note that the **reset** command does not effect many environment characteristics (such as the current conflict resolution strategy). This command has no return value.

Syntax

(reset)

### 14.1.9 Executing Commands From a File

The **batch** command allows automatic processing of CLIPS interactive com­mands by replacing standard input with the contents of a file. Any command or function can be used in a batch file, as well as construct definitions and re­sponses to functions that read input from standard input such as the **read** and **readline** functions. The **load** command should be used in batch files rather than defining constructs directly---the **load** command expects only constructs and provides better error recovery when parentheses are misplaced; the **batch** command, however, moves on until it finds the next construct *or* command (and in the case of a construct this is likely to generate more errors as the remaining commands and functions in the construct are parsed). This command returns the symbol **TRUE** if the batch file was successfully executed; otherwise, it returns the symbol **FALSE**.

Note that the **batch** command operates by replacing standard input rather than by immediately executing the commands found in the batch file. Thus, if you execute a batch command from the RHS of a rule, the commands in that batch file will not be processed until control is returned to the top‑level prompt.

Syntax

(batch \<file-name\>)

### 14.1.10 Executing Commands From a File Without Replacing Standard Input

The **batch\*** command evaluates the series of commands stored in the file specified by the \<file‑name\> argument. Unlike the **batch** command, the **batch\*** command evaluates all of the commands in the specified file before returning. The **batch\*** command does not replace standard input and thus a **batch\*** file cannot be used to provide input to functions such as **read** and **readline**. In addition, commands stored in the **batch\*** file and the return value of these commands are not echoed to standard output.

Syntax

(batch\* \<file-name\>)

### 14.1.11 Determining CLIPS Compilation Options

The **options** command prints the compiler flag settings (for enabling/disabling various features) used for creating the CLIPS executable.

Syntax

(options)

### 14.1.12 Calling the Operating System

The **system** command allows a call to the operating system. If no arguments are specified, the function returns 0 if a command processer is unavailable; otherwise, it returns a non-zero value. If one or more string/symbol arguments are specified, the arguments are concatenated into a single command string and this string is then passed to the command processor. In this case, the function returns an integer value indicating the completion status of the command (which can vary depending upon your operating system and compiler). If any invalid arguments are specified, this command returns the symbol **FALSE**.

Syntax

(system \<lexeme-expression\>\*)

Example

(defrule print-directory\
(print-directory ?directory)\
=\>\
(system \"dir \" ?directory))

Note that any spaces needed for a proper parsing of the **system** command must be added by the user in the call to the **system** command. Also note that the **system** command is not guaranteed to execute (e.g., the operating system may not have enough memory to spawn a new process).

 Portability Note

The **system** function uses the ANSI C function **system** as a base. The return value of this ANSI library function is implementation dependent and may change for different operating systems and compilers.

### 14.1.13 Setting the Dynamic Constraint Checking Behavior

The **set-dynamic-constraint-checking** function sets the dynamic constraint checking behavior. When this behavior is disabled (**FALSE** by default), newly created facts and instances do not have their slot values checked for constraint violations. When this behavior is enabled (**TRUE**), the slot values are checked for constraint violations. The return value for this command is the old value for the behavior. Constraint information is not saved when using the **bload** and **constructs‑to‑c** command if dynamic constraint checking is disabled.

Syntax

(set‑dynamic‑constraint‑checking \<boolean-expression\>)

### 14.1.14 Getting the Dynamic Constraint Checking Behavior

Thze **get-dynamic-constraint-checking** function returns the current value of the dynamic constraint checking behavior (the symbol **TRUE** or **FALSE**).

Syntax

(get‑dynamic‑constraint‑checking)

### 14.1.15 Finding Symbols

The **apropos** command displays all symbols currently defined in CLIPS which contain a specified substring. This command has no return value.

Syntax

(apropos \<lexeme\>)

Example

CLIPS\> (apropos pen)

dependencies

dependents

open

CLIPS\>

## 14.2 Debugging Commands

The following commands control the CLIPS debugging features.

### 14.2.1 Generating Trace Files

The **dribble-on** command sends all output normally sent to the logical names **stdout**, **werror**, and **wwarning** to the file specified by the \<file‑name\> argument as well as sending output to its normal destination. Additionally, all information received from logical name **stdin** is also sent to the file specified by the \<file‑name\> argument as well as being returned to the requesting function. This command returns the symbol **TRUE** if the dribble file was successfully opened; otherwise, it returns the symbol **FALSE**.

Syntax

(dribble‑on \<file-name\>)

### 14.2.2 Closing Trace Files

The **dribble-off** command stops sending output to the dribble file and closes it. This command returns the symbol **TRUE** if the dribble file was successfully closed; otherwise, it returns the symbol **FALSE**.

Syntax

(dribble‑off)

### 14.2.3 Enabling Watch Items

The **watch** command function enables debugging/informational output for various CLIPS operations.

Syntax

(watch \<watch-item\>)

\<watch-item\> ::= all \|

compilations \|

statistics \|

focus \|

messages \|

deffunctions \<deffunction-name\>\* \|

globals \<global-name\>\* \|

rules \<rule-name\>\* \|

activations \<rule-name\>\* \|

facts \<deftemplate-name\>\* \|

goals \<deftemplate-name\>\* \|

instances \<class-name\>\* \|

slots \<class-name\>\* \|

message-handlers \<handler-spec-1\>\*

\[\<handler-spec-2\>\]) \|

generic-functions \<generic-name\>\* \|

methods \<method-spec-1\>\* \[\<method-spec-2\>\]

\<handler-spec-1\> ::= \<class-name\>

\<handler-name\> \<handler-type\>

\<handler-spec-2\> ::= \<class-name\>

\[\<handler-name\> \[\<handler-type\>\]\]

\<method-spec-1\> ::= \<generic-name\> \<method-index\>

\<method-spec-2\> ::= \<generic-name\> \[\<method-index\>\]

If **compilations** are watched, the progress of construct definitions will be displayed.

If **facts** are watched, all fact assertions and retractions will be displayed. Optionally, facts associated with individual deftemplates can be watched by specifying one or more deftemplate names.

If **rules** are watched, all rule firings will be dis­played. If **activations** are watched, all rule activations and deactivations will be displayed. Optionally, rule firings and activations associated with individual defrules can be watched by specifying one or more defrule names. If **statistics** are watched, timing information along with other information (average number of facts, average number of activations, etc.) will be displayed after a run. Note that the number of rules fired and timing information is not printed unless this item is being watch. If **focus** is watched, then changes to the current focus will be displayed.

If **globals** are watched, variable assignments to globals variables will be displayed. Optionally, variable assignments associated with individual defglobals can be watched by specifying one or more defglobal names. If **deffunctions** are watched, the start and finish of deffunctions will be displayed. Optionally, the start and end display associated with individual deffunctions can be watched by specifying one or more deffunction names.

If **generic‑functions** are watched, the start and finish of generic functions will be displayed. Optionally, the start and end display associated with individual defgenerics can be watched by specifying one or more defgeneric names. If **methods** are watched, the start and finish of individual methods within a generic function will be displayed. Optionally, individual methods can be watched by specifying one or more methods using a defgeneric name and a method index. When the method index is not specified, then all methods of the specified defgeneric will be watched.

If **instances** are watched, creation and deletion of instances will be displayed. If **slots** are watched, changes to any instance slot values will be displayed. Optionally, instances and slots associated with individual concrete defclasses can be watched by specifying one or more concrete defclass names. If **message‑handlers** are watched, the start and finish of individual message‑handlers within a message will be displayed. Optionally, individual message‑handlers can be watched by specifying one or more message‑handlers using a defclass name, a message‑handler name, and a message‑handler type. When the message‑handler name and message‑handler type are not specified, then all message‑handlers for the specified class will be watched. When the message‑handler type is not specified, then all message‑handlers for the specified class with the specified message‑handler name will be watched. If **messages** are watched, the start and finish of messages will be displayed.

If **goals** are watched, the addition and removal of goals will be displayed. Optionally, goals associated with individual deftemplates can be watched by specifying one or more deftemplate names.

For the watch items that allow individual constructs to be watched, if no constructs are specified, then all constructs of that type will be watched. If all constructs associated with a watch item are being watched, then newly defined constructs of the same type will also be watched. A construct retains its old watch state if it is redefined. If **all** is watched, then all other watch items will be watched. By default, no items are watched. The **watch** command has no return value.

Example

CLIPS\> (watch rules)

CLIPS\>

### 14.2.4 Disabling Watch Items

The **unwatch** command disables the effect of the **watch** command for the specified watch item.

Syntax

(unwatch \<watch-item\>)

This command is identical to the **watch** command with the exception that it disables watch items rather than enabling them. This command has no return value.

Example

CLIPS\> (unwatch all)

CLIPS\>

### 14.2.5 Viewing the Current State of Watch Items

The **list-watch-items** command displays the current state of watch items.

Syntax

(list‑watch‑items \[\<watch-item\>\])

The **list-watch-items** command displays the current state of all watch items. If called without the \<watch‑item\> argument, the global watch state of all watch items is displayed. If called with the \<watch‑item\> argument, the global watch state for that item is displayed followed by the individual watch states for each item of the specified type which can be watched. This command has no return value.

Example

CLIPS\> (list-watch-items)

facts = off

instances = off

slots = off

rules = off

activations = off

messages = off

message-handlers = off

generic-functions = off

methods = off

deffunctions = off

compilations = off

statistics = off

globals = off

focus = off

CLIPS\> (list-watch-items facts)

facts = off

MAIN:

CLIPS\>

## 14.3 Deftemplate Commands

The following commands manipulate deftemplates.

### 14.3.1 Displaying the Text of a Deftemplate

The **ppdeftemplate** command sends the source text of a deftemplate to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdeftemplate \<deftemplate-name\> \[\<logical-name\>\])

### 14.3.2 Displaying the List of Deftemplates

The **list-deftemplates** command displays the names of all deftemplates. This command has no return value.

Syntax

(list‑deftemplates \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the names of all deftemplates in the current module are displayed. If the \<module‑name\> argument is specified, then the names of all deftemplates in the specified module are displayed. If the \<module‑name\> argument is the symbol **\***, then the names of all deftemplates in all modules are displayed.

### 14.3.3 Deleting a Deftemplate

The **undeftemplate** command deletes a previously defined deftemplate.

Syntax

(undeftemplate \<deftemplate-name\>)

If the deftemplate is in use (for example by a fact or a rule), then the deletion will fail. Otherwise, no further uses of the deleted deftemplate are permitted (unless redefined). If the symbol **\*** is used for the \<deftemplate‑name\> argument, then all deftemplates will be deleted (unless there is a deftemplate named **\***). This command has no return value.

## 14.4 Fact Commands

The following commands display information about facts.

### 14.4.1 Displaying the Fact-List

The **facts** command lists existing facts.

Syntax

(facts \[\<module-name\>\]

\[\<start-integer-expression\>

\[\<end-integer-expression\>

\[\<max-integer-expression\>\]\]\])

If the \<module‑name\> argument is not specified, then only facts visible to the current module will be displayed. If the \<module‑name\> argument is specified, then only facts visible to the specified module are displayed. If the symbol **\*** is used for the \<module‑name\> argument, then facts from any module may be displayed. If the start argument is speci­fied, only facts with fact‑indices greater than or equal to this argument are displayed. If the end argument is speci­fied, only facts with fact‑indices less than or equal to this argument are displayed. If the max argument is speci­fied, then no facts will be displayed beyond the specified maximum number of facts to be displayed. This command has no return value.

### 14.4.2 Displaying a Single Fact

The ppfact command displays a single fact, placing each slot and its value on a separate line. Optionally the logical name to which output is sent can be specified and slots containing their default values can be excluded from the output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the construct's text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

If the \<ignore-defaults-flag\> argument is the symbol **FALSE** or unspecified, then all of the fact's slots are displayed, otherwise slots with static defaults are only displayed if their current slot value differs from their initial default value.

Syntax

(ppfact \<fact-specifier\> \[\<logical-name\> \[\<ignore-defaults-flag\>\]\])

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(multislot name)

(slot age (default 0))

(slot net-worth (default 0.0)))

CLIPS\> (assert (person))

\<Fact-1\>

CLIPS\> (ppfact 1 t)

(person

(name)

(age 0)

(net-worth 0.0))

CLIPS\> (ppfact 1 t TRUE)

(person)

CLIPS\> (modify 1 (name John Smith) (age 23))

\<Fact-1\>

CLIPS\> (ppfact 1 t TRUE)

(person

(name John Smith)

(age 23))

CLIPS\> (ppfact 1 nil)

\"(person

(name John Smith)

(age 23)

(net-worth 0.0))\"

CLIPS\>

### 14.4.3 Saving Facts To A Text File

The **save-facts** command saves all of the facts in the current fact‑list into the file specified by the \<file‑name\> argument. External‑address and fact‑address fields are saved as strings. Instance‑address fields are converted to instance‑names. Optionally, the scope of facts to be saved can be specified. If the \<save‑scope\> argument is the symbol **visible**, then all facts visible to the current module are saved. If the \<save‑scope\> argument is the symbol **local**, then only those facts with deftemplates defined in the current module are saved. If the \<save‑scope\> argument is not specified, it defaults to **local**. If the \<save‑scope\> argument is specified, then one or more deftemplate names may also be specified. In this event, only those facts associated with a corresponding deftemplate in the specified list will be saved. This command returns the number of facts saved.

Syntax

(save‑facts \<file-name\> \[\<save-scope\> \<deftemplate-names\>\*\])

\<save-scope\> ::= visible \| local

### 14.4.4 Saving Facts to a Binary File

The **bsave‑facts** commands works exactly like **save‑facts** command except that the facts are saved in a binary format which can only be loaded with the **bload‑facts** command. The advantage to this format is that loading binary facts can be much faster than loading text facts for large numbers of facts. The disadvantage is that the file is not portable to other platforms.

Syntax

(bsave‑facts \<file-name\> \[\<save-scope\> \<deftemplate-names\>\*\])

### 14.4.5 Loading Facts From a Text File

The **load-facts** command will read facts in text format from the file specified by the \<file-name\> argument and assert them. It can read files created with the **save‑facts** command or any UTF-8 text file with facts in the correct format. Facts may span across lines and can be written in either ordered or deftemplate format. This command returns the number of facts loaded or ‑1 if it could not access the fact file.

Syntax

(load‑facts \<file-name\>)

Example

CLIPS\> (clear)

CLIPS\> (deftemplate person (slot name) (slot age))

CLIPS\> (open \"facts.fct\" facts \"w\")

TRUE

CLIPS\> (printout facts \"(person (name Jack) (age 23))\" crlf)

CLIPS\> (printout facts \"(person (name Jill) (age 34))\" crlf)

CLIPS\> (close facts)

TRUE

CLIPS\> (load-facts facts.fct)

2

CLIPS\> (facts)

f-1 (person (name Jack) (age 23))

f-2 (person (name Jill) (age 34))

For a total of 2 facts.

CLIPS\>

### 14.4.6 Loading Facts from a Binary File

The **bload-facts** command works exactly like **load‑facts** except that it can only work with files generated by **bsave‑facts**. This command returns the number of facts loaded or ‑1 if it could not access the fact file.

Syntax

(bload‑facts \<file-name\>)

### 14.4.7 Setting the Duplication Behavior of Facts

The **set-fact-duplication** command sets fact duplication behavior. When this behavior is disabled (**FALSE** by default), asserting a duplicate of a fact already in the fact‑list produces no effect. When enabled (**TRUE**), the duplicate fact is asserted with a new fact‑index. The return value for this command is the old value for the behavior.

Syntax

(set‑fact‑duplication \<boolean-expression\>)

Example

CLIPS\> (clear)

CLIPS\> (get-fact-duplication)

FALSE

CLIPS\> (watch facts)

CLIPS\> (assert (grocery-list milk eggs cheese))

==\> f-1 (grocery-list milk eggs cheese)

\<Fact-1\>

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (set-fact-duplication TRUE)

FALSE

CLIPS\> (assert (grocery-list milk eggs cheese))

==\> f-2 (grocery-list milk eggs cheese)

\<Fact-2\>

CLIPS\> (facts)

f-1 (grocery-list milk eggs cheese)

f-2 (grocery-list milk eggs cheese)

For a total of 2 facts.

CLIPS\> (unwatch facts)

CLIPS\> (set-fact-duplication FALSE)

TRUE

CLIPS\>

### 14.4.8 Getting the Duplication Behavior of Facts

The **get-fact-duplication** command returns the current value of the fact duplication behavior (the symbol **TRUE** or **FALSE**).

Syntax

(get‑fact‑duplication)

## 14.5 Deffacts Commands

The following commands manipulate deffacts.

### 14.5.1 Displaying the Text of a Deffacts

The **ppdeffacts** command sends the source text of a deffacts to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdeffacts \<deffacts-name\> \[\<logical-name\>\])

### 14.5.2 Displaying the List of Deffacts

The **list-deffacts** command displays the names of all defined deffacts.

Syntax

(list‑deffacts \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the names of all deffacts in the current module are displayed. If the \<module‑name\> argument is specified, then the names of all deffacts in the specified module are displayed. If the \<module‑name\> argument is the symbol **\***, then the names of all deffacts in all modules are displayed. This command has no return value.

### 14.5.3 Deleting a Deffacts

The **undeffacts** command deletes a previously defined deffacts.

Syntax

(undeffacts \<deffacts-name\>)

All facts listed in the deleted deffacts construct will no longer be asserted as part of a reset. If the symbol **\*** is used for the \<deffacts‑name\> argument, then all deffacts will be deleted (unless there exists a deffacts named **\***). This command has no return value.

## 14.6 Defrule Commands

The following commands manipulate defrules.

### 14.6.1 Displaying the Text of a Rule

The **ppdefrule** command sends the source text of a defrule to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdefrule \<rule-name\> \[\<logical-name\>\])

### 14.6.2 Displaying the List of Rules

The **list-defrules** command displays the names of all defined defrules.

Syntax

(list‑defrules \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the names of all defrules in the current module are displayed. If the \<module‑name\> argument is specified, then the names of all defrules in the specified module are displayed. If the \<module‑name\> argument is the symbol **\***, then the names of all defrules in all modules are displayed. This command has no return value.

### 14.6.3 Deleting a Defrule

The **undefrule** command deletes a previously defined defrule.

Syntax

(undefrule \<defrule-name\>)

If the symbol **\*** is used for the \<defrule‑name\> argument, then all defrules will be deleted (unless there is a defrule named **\***). This command has no return value.

### 14.6.4 Displaying Matches for a Rule

For the specified defrule, the **matches** command displays the list of the facts or instances which match each pattern in the rule's LHS, the partial matches for the rule, and the activations for the rule. When listed as a partial match, the *not*, *exists*, and *forall* CEs are shown as an asterisk. This command returns the symbol **FALSE** if the specified rule does not exist or the command is passed invalid arguments; otherwise, a multifield value is returned containing three values: the combined sum of the matches for each pattern, the combined sum of partial matches, and the number of activations.

Syntax

(matches \<rule-name\> \[\<verbosity\>\])

The \<verbosity\> argument is either the symbol **verbose**, **succinct**, or **terse**. If \<verbosity\> is not specified or \<verbosity\> is **verbose**, then output will include details for each match, partial match, and activation. If \<verbosity\> is **succinct**, then output will just include the total number of matches, partial matches, and activations. If \<verbosity\> is **terse**, no output will be displayed.

Example

In this example, the **example-1** rule has three patterns and none are added by CLIPS. Fact f-1 matches the first pattern, facts f-2 and f-3 match the the second pattern, and fact f-4 matches the third pattern. Issuing the **run** command removes all of the rule's activations from the agenda.

CLIPS\> (clear)

CLIPS\>

(defrule example-1

(a ?)

(b ?)

(c ?)

=\>)

CLIPS\> (assert (a 1) (b 1) (b 2) (c 1))

\<Fact-4\>

CLIPS\> (facts)

f-1 (a 1)

f-2 (b 1)

f-3 (b 2)

f-4 (c 1)

For a total of 4 facts.

CLIPS\> (agenda)

0 example-1: f-1,f-2,f-4

0 example-1: f-1,f-3,f-4

For a total of 2 activations.

CLIPS\> (run)

CLIPS\> (agenda)

CLIPS\>

The **example-2** rule has three patterns. There are no matches for the first pattern (since there are no *d* facts), facts f-2 and f-3 match the third pattern, and fact f-4 matches the forth pattern.

CLIPS\>\
(defrule example-2

(not (d ?))

(exists (b ?x)

(c ?x))

=\>)

CLIPS\> (agenda)

0 example-2: \*,\*

For a total of 1 activation.

CLIPS\>

Listing the matches for the **example-1** rule displays the matches for the patterns indicated previously. There are two partial matches which satisfy the first two patterns and two partial matches which satisfy all three patterns. Since all of the rule's activations were allowed to fire there are none listed.

CLIPS\> (matches example-1)

Matches for Pattern 1

f-1

Matches for Pattern 2

f-2

f-3

Matches for Pattern 3

f-4

Partial matches for CEs 1 - 2

f-1,f-3

f-1,f-2

Partial matches for CEs 1 - 3

f-1,f-2,f-4

f-1,f-3,f-4

Activations

None

(4 4 0)

CLIPS\>

Listing the matches for the **example-2** rule displays the matches for the patterns indicated previously. There is one partial match which satisfies the first two CEs (the **not** CE and the **exists** CE). The symbol **\*** indicates an existential match that is not associated with specific facts/instances (e.g., the **not** CE is satisfied because there are no **d** facts matching the pattern so \* is used to indicate a match as there's no specific fact matching that pattern). Since none of the rule's activations were allowed to fire they are listed. The list of activations will always be a subset of the partial matches for all of the rule's CEs.

CLIPS\> (matches example-2)

Matches for Pattern 1

None

Matches for Pattern 2

f-2

f-3

Matches for Pattern 3

f-4

Partial matches for CEs 1 - 2

\*,f-2

\*,f-3

Partial matches for CEs 1 - 3

\*,f-2,f-4

Partial matches for CEs 1 (P1) , 2 (P2 - P3)

\*,\*

Activations

\*,\*

(3 4 1)

CLIPS\>

To display a summary of the partial matches, specify the symbol **succinct** or **terse** as the second argument to the **matches** command.

CLIPS\> (matches example-2 succinct)

Pattern 1: 0

Pattern 2: 2

Pattern 3: 1

CEs 1 - 2: 2

CEs 1 - 3: 1

CEs 1 (P1) , 2 (P2 - P3): 1

Activations: 1

(3 4 1)

CLIPS\> (matches example-2 terse)

(3 4 1)

CLIPS\>

###  14.6.5 Setting a Breakpoint for a Rule

The **set-break** command sets a breakpoint for the specified defrule.

Syntax

(set‑break \<rule-name\>)

If a breakpoint is set for a rule, execution will halt prior to executing that rule. At least one rule must fire before a break­point will stop execution. This command has no return value.

### 14.6.6 Removing a Breakpoint for a Rule

The **remove-break** command removes a breakpoint for the specified defrule.

Syntax

(remove‑break \[\<defrule-name\>\])

If no argument is specified, then all breakpoints are removed. This command has no return value.

### 14.6.7 Displaying Rule Breakpoints

The **show-breaks** command displays all the rules which have breakpoints set. This command has no return value.

Syntax

(show‑breaks \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the names of all rules having breakpoints in the current module are displayed. If \<module‑name\> is specified, then the names of all rules having breakpoints in the specified module are displayed. If \<module‑name\> is the symbol **\***, then the names of all rules having breakpoints in all modules are displayed.

### 14.6.8 Refreshing a Rule

The **refresh** command places all current activations of the specified defrule on the agenda. This command has no return value.

Syntax

(refresh \<rule-name\>)

### 14.6.9 Determining the Logical Dependencies of a Pattern Entity

The **dependencies** command lists the partial matches from which a fact or instance receives logical support. This command has no return value.

Syntax

(dependencies \<fact-or-instance-specifier\>)

The \<fact‑or‑instance‑specifier\> term includes variables bound on the LHS to fact‑addresses or instance‑addresses, the fact‑index of the desired fact (e.g., 3 for the fact labeled f‑3), or the instance‑name (e.g., \[car-1\]).

### 14.6.10 Determining the Logical Dependents of a Pattern Entity

The **dependents** command lists all facts and instances which receive logical support from a fact or instance. This command has no return value.

Syntax

(dependents \<fact-or-instance-specifier\>)

The \<fact‑or‑instance‑specifier\> term includes variables bound on the LHS to fact‑addresses or instance‑addresses, the fact‑index of the desired fact (e.g., 3 for the fact labeled f‑3), or the instance‑name (e.g., \[car-1\]).

## 14.7 Agenda Commands

The following commands manipulate the agenda.

### 14.7.1 Displaying the Agenda

The **agenda** command displays all activations on the agenda. This command has no return value.

Syntax

(agenda \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then all activations in the current module (not the current focus) are displayed. If \<module‑name\> is specified, then all activations on the agenda of the specified module are displayed. If \<module‑name\> is the symbol **\***, then the activations on all agendas in all modules are displayed.

### 14.7.2 Running CLIPS

The **run** command starts execution of activated rules. If the optional first argument is a positive integer, execu­tion will cease after the specified number of rule firings or when the agenda con­tains no rule activations. If there are no arguments or the first argument is a negative integer, execution will cease when the agenda contains no rule activations. If the focus stack is empty, then the MAIN module automatically becomes the current focus. If the **rules** watch item is enabled using the **watch** command, then an informational message will be printed each time a rule is fired. This command has no return value.

Syntax

(run \[\<integer-expression\>\])

### 14.7.3 Focusing on a Group of Rules

The **focus** command pushes one or more modules onto the focus stack. The specified modules are pushed onto the focus stack in the reverse order they are listed. The current module is set to the last module pushed onto the focus stack. The current focus is the top module of the focus stack. Thus (focus COLLECT PROCESS UPDATE) pushes UPDATE, then PROCESS, then COLLECT unto the focus stack so that COLLECT is now the current focus. Note that the current focus is different from the current module. Focusing on a module remembers the current module so that it can be returned to later. Setting the current module with the **set‑current‑module** function changes it without remembering the old module. Before a rule executes, the current module is changed to the module in which the executing rule is defined (the current focus). This command returns the symbol **FALSE** if an error occurs; otherwise it returns the symbol **TRUE**.

Syntax

(focus \<module-name\>+)

### 14.7.4 Stopping Rule Execution

The **halt** command stops execution of activated rules. After **halt** is called, control is returned from the **run** command. The agenda is left intact, and execution may be continued with a **run** command. This command has no return value.

Syntax

(halt)

### 14.7.5 Setting The Current Conflict Resolution Strategy

This **set-strategy** command sets the current conflict resolution strategy. The default strategy is **depth**.

Syntax

(set‑strategy \<strategy\>)

The \<strategy\> argument must be one of the following symbols: **depth**, **breadth**, **simplicity**, **complexity**, **lex**, **mea**, or **random**. The agenda will be reordered to reflect the new conflict resolution strategy. The return value of this command is the prior conflict resolution strategy.

### 14.7.6 Getting The Current Conflict Resolution Strategy

The **get-strategy** command returns the current conflict resolution strategy (either the symbol **depth**, **breadth**, **simplicity**, **complexity**, **lex**, **mea**, or **random**).

Syntax

(get‑strategy)

### 14.7.7 Listing the Module Names on the Focus Stack

The **list‑focus‑stack** command lists all module names on the focus stack. The first name listed is the current focus.

Syntax

(list‑focus‑stack)

### 14.7.8 Removing all Module Names from the Focus Stack

The **clear‑focus‑stack** command removes all module names from the focus stack.

Syntax

(clear‑focus‑stack)

### 14.7.9 Setting the Salience Evaluation Behavior

The **set-salience-evaluation** command sets the salience evaluation behavior. By default, salience values are only evaluated when a rule is defined.

Syntax

(set‑salience‑evaluation \<evaluation\>)

The \<evaluation\> argument must be one of the symbols **when‑defined**, **when‑activated**, or **every‑cycle**. The **when‑defined** symbol forces salience evaluation at the time of rule definition. The **when‑activated** symbol forces salience evaluation at the time of rule definition and upon being activated. The **every‑cycle** symbol forces evaluation at the time of rule definition, upon being activated, and after every rule firing. The return value of this command is the prior value for salience evaluation.

### 14.7.10 Getting the Salience Evaluation Behavior

The **get-salience-evaluation** command returns the current salience evaluation behavior (either the symbol when‑defined, when‑activated, or every‑cycle).

Syntax

(get‑salience‑evaluation)

### 14.7.11 Refreshing the Salience Value of Rules on the Agenda

The **refresh-agenda** command reevaluates the saliences of all rules on the agenda regardless of the current salience evaluation setting. This command has no return value.

Syntax

(refresh‑agenda \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the agenda of the current module is refreshed. If \<module‑name\> is specified, then the agenda in the specified module is refreshed. If \<module‑name\> is the symbol **\***, then the agenda in every module is refreshed.

## 14.8 Defglobal Commands

The following commands manipulate defglobals.

### 14.8.1 Displaying the Text of a Defglobal

The **ppdefglobal** command sends the source text of a defglobal to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Unlike other constructs, defglobal definitions have no name associated with the entire construct. The variable name passed to ppdefglobal should not include the question mark or the asterisks (e.g., x is the variable name for the global variable ?\*x\*).

Syntax

(ppdefglobal \<global-variable-name\> \[\<logical-name\>\])

### 14.8.2 Displaying the List of Defglobals

The **list-defglobals** command displays the names of all defined defglobals. This command has no return value.

Syntax

(list‑defglobals \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the names of all defglobals in the current module are displayed. If \<module‑name\> is specified, then the names of all defglobals in the specified module are displayed. If \<module‑name\> is the symbol **\***, then the names of all defglobals in all modules are displayed.

### 14.8.3 Deleting a Defglobal

The **undefglobal** command deletes a previously defined defglobal.

Syntax

(undefglobal \<defglobal-name\>)

If the symbol **\*** is used for \<defglobal‑name\>, then all defglobals will be deleted (unless there is a defglobal named **\***). This command has no return value.

### 14.8.4 Displaying the Values of Global Variables

The **show-defglobals** command displays the name and current value of all defglobals. This command has no return value.

Syntax

(show‑defglobals \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the names and values of all defglobals in the current module are displayed. If \<module‑name\> is specified, then the names and values of all defglobals in the specified module are displayed. If \<module‑name\> is the symbol **\***, then the names and values of all defglobals in all modules are displayed.

### 14.8.5 Setting the Reset Behavior of Global Variables

The **set-reset-globals** command sets the values of the reset globals behavior. When this behavior is enabled (**TRUE** by default) global variables are reset to their original values when the **reset** command is performed. The return value for this command is the old value for the behavior.

Syntax

(set‑reset‑globals \<boolean-expression\>)

### 14.8.6 Getting the Reset Behavior of Global Variables

The **get-reset-globals** command returns the current value of the reset global variables behavior (either the symbol **TRUE** or **FALSE**).

Syntax

(get‑reset‑globals)

## 14.9 Deffunction Commands

The following commands manipulate deffunctions.

### 14.9.1 Displaying the Text of a Deffunction

The **ppdeffunction** command sends the source text of a deffunction to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdeffunction \<deffunction-name\> \[\<logical-name\>\])

### 14.9.2 Displaying the List of Deffunctions

The **list-deffunctions** command displays the names of all defined deffunctions. This command has no return value.

Syntax

(list‑deffunctions)

### 14.9.3 Deleting a Deffunction

The **undeffunction** command deletes a previously defined deffunction.

Syntax

(undeffunction \<deffunction-name\>)

If the symbol **\*** is used for the \<deffunction‑name\> argument, then all deffunctions will be deleted (unless there exists a deffunction named **\***). This command has no return value.

## 14.10 Generic Function Commands

The following commands manipulate generic functions.

### 14.10.1 Displaying the Text of a Generic Function Header

The **ppdefgeneric** command sends the source text of a defgeneric to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdefgeneric \<generic-function-name\> \[\<logical-name\>\])

### 14.10.2 Displaying the Text of a Generic Function Method

The **ppdefmethod** command sends the source text of a defmethod to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdefmethod \<generic-function-name\> \<index\> \[\<logical-name\>\])

The \<index\> term is the index of the method to be displayed. This command has no return value.

### 14.10.3 Displaying the List of Generic Functions

The **list-defgenerics** command displays the names of all defined generic functions.

Syntax

(list‑defgenerics \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the names of all defgenerics in the current module are displayed. If \<module‑name\> is specified, then the names of all defgenerics in the specified module are displayed. If \<module‑name\> is the symbol **\***, then the names of all defgenerics in all modules are displayed. This command has no return value.

### 14.10.4 Displaying the List of Methods for a Generic Function

The **list-defmethods** command displays the names, arguments, and indices of all defined defmethods. If no generic function name is specified, this command lists all defined generic function methods. If a name is specified, then only the methods for the named generic function are listed. The methods are listed in decreasing order of precedence for each generic function. This command has no return value.

Syntax

(list‑defmethods \[\<generic-function-name\>\])

### 14.10.5 Deleting a Generic Function

The **undefgeneric** command deletes a previously defined generic function.

Syntax

(undefgeneric \<generic-function-name\>)

If the symbol **\*** is used for the \<generic‑function‑name\> argument, then all generic functions will be deleted (unless there exists a generic function called **\***). This command removes the header and all methods for a generic function. This command has no return value.

### 14.10.6 Deleting a Generic Function Method

The **undefmethod** command deletes a previously defined generic function method.

Syntax

(undefmethod \<generic-function-name\> \<index\>)

The \<index\> argument is the index of the method to be deleted for the generic function. If the symbol **\*** is used for \<index\>, then all the methods for the generic function will be deleted. This is different from the undefgeneric command because the header is not removed. If **\*** is used for \<generic‑function‑name\>, then **\*** must also be specified for \<index\>, and all the methods for all generic functions will be removed. This command removes the specified method for a generic function, but even if the method removed is the last one, the generic function header is not removed. This command has no return value.

### 14.10.7 Previewing a Generic Function Call

The **preview-generic** command lists all applicable methods for a particular generic function call in order of decreasing precedence. The **list‑defmethods** command is different in that it lists all methods for a generic function.

Syntax

(preview‑generic \<generic-function-name\> \<expression\>\*)

This command does not actually execute any of the methods, but any side effects of evaluating the generic function arguments and any query parameter restrictions in methods do occur.

Example

CLIPS\> (clear)

CLIPS\> (defmethod + ((?a NUMBER) (?b INTEGER)))

CLIPS\> (defmethod + ((?a INTEGER) (?b INTEGER)))

CLIPS\> (defmethod + ((?a INTEGER) (?b NUMBER)))

CLIPS\>

(defmethod + ((?a NUMBER) (?b NUMBER)

(\$?rest PRIMITIVE)))

CLIPS\>

(defmethod + ((?a NUMBER)

(?b INTEGER (\> ?b 2))))

CLIPS\>

(defmethod + ((?a INTEGER (\> ?a 2))

(?b INTEGER (\> ?b 3))))

CLIPS\>

(defmethod + ((?a INTEGER (\> ?a 2))

(?b NUMBER)))

CLIPS\> (preview-generic + 4 5)

\+ #7 (INTEGER \<qry\>) (INTEGER \<qry\>)

\+ #8 (INTEGER \<qry\>) (NUMBER)

\+ #3 (INTEGER) (INTEGER)

\+ #4 (INTEGER) (NUMBER)

\+ #6 (NUMBER) (INTEGER \<qry\>)

\+ #2 (NUMBER) (INTEGER)

\+ #SYS1 (NUMBER) (NUMBER) (\$? NUMBER)

\+ #5 (NUMBER) (NUMBER) (\$? PRIMITIVE)

CLIPS\>

## 14.11 Defclass Commands

The following commands manipulate defclasses.

### 14.11.1 Displaying the Text of a Defclass

The **ppdefclass** command sends the source text of a defclass to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdefclass \<class-name\> \[\<logical-name\>\])

### 14.11.2 Displaying the List of Defclasses

The **list-defclasses** command displays the names of all defined defclasses. If the \<module‑name\> argument is unspecified, then the names of all defclasses in the current module are displayed. If \<module‑name\> is specified, then the names of all defclasses in the specified module are displayed. If \<module‑name\> is the symbol **\***, then the names of all defclasses in all modules are displayed. This command has no return value.

Syntax

(list‑defclasses \[\<module-name\>\])

### 14.11.3 Deleting a Defclass

The **undefclass** command deletes a previously defined defclass and all its subclasses.

Syntax

(undefclass \<class-name\>)

If the symbol **\*** is used for the \<class‑name\> argument, then all defclasses will be deleted (unless there exists a defclass called **\***). This command has no return value.

### 14.11.4 Examining a Class

The **describe-class** command provides a verbose description of a class including its role (whether direct instances can be created or not), direct superclasses and subclasses, class precedence list, slots with all their facets and sources, and all recognized message‑handlers. This command has no return value.

Syntax

(describe‑class \<class-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass CHILD (is-a USER)

(role abstract)

(multislot parents (cardinality 2 2))

(slot age (type INTEGER)

(range 0 18))

(slot sex (access read-only)

(type SYMBOL)

(allowed-symbols male female)

(storage shared)))

CLIPS\>

(defclass BOY (is-a CHILD)

(slot sex (source composite)

(default male)))

CLIPS\>

(defmessage-handler BOY play ()

(println \"The boy is now playing\...\"))

CLIPS\> (describe-class CHILD)

================================================================================

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

Abstract: direct instances of this class cannot be created.

Direct Superclasses: USER

Inheritance Precedence: CHILD USER OBJECT

Direct Subclasses: BOY

\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

SLOTS : FLD DEF PRP ACC STO MCH SRC VIS CRT OVRD-MSG SOURCE(S)

parents : MLT STC INH RW LCL RCT EXC PRV RW put-parents CHILD

age : SGL STC INH RW LCL RCT EXC PRV RW put-age CHILD

sex : SGL STC INH R SHR RCT EXC PRV R NIL CHILD

Constraint information for slots:

SLOTS : SYM STR INN INA EXA FTA INT FLT

parents : + + + + + + + + RNG:\[-oo..+oo\] CRD:\[2..2\]

age : + RNG:\[0..18\]

sex : \#

\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

Recognized message-handlers:

init primary in class USER

delete primary in class USER

create primary in class USER

print primary in class USER

direct-modify primary in class USER

message-modify primary in class USER

direct-duplicate primary in class USER

message-duplicate primary in class USER

get-parents primary in class CHILD

put-parents primary in class CHILD

get-age primary in class CHILD

put-age primary in class CHILD

get-sex primary in class CHILD

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

================================================================================

CLIPS\>

The following table explains the fields and their possible values in the slot descriptions.

+------------+--------------------+----------------------------------------------------------------------+
| **Field**  | **Values**         | **Explanation**                                                      |
+:==========:+:==================:+======================================================================+
| FLD        | > SGL/MLT          | > Field type (single-field or multifield)                            |
+------------+--------------------+----------------------------------------------------------------------+
| DEF        | > STC/DYN/NIL      | > Default value (static, dynamic, or none)                           |
+------------+--------------------+----------------------------------------------------------------------+
| PRP        | > INH/NIL          | > Propagation to subclasses (inheritable or not inheritable)         |
+------------+--------------------+----------------------------------------------------------------------+
| ACC        | > RW/R/INT         | > Access (read-write, read-only, or initialize-only)                 |
+------------+--------------------+----------------------------------------------------------------------+
| STO        | > LCL/SHR          | > Storage (local or shared)                                          |
+------------+--------------------+----------------------------------------------------------------------+
| MCH        | > RCT/NIL          | > Pattern-match (reactive or non-reactive)                           |
+------------+--------------------+----------------------------------------------------------------------+
| SRC        | > CMP/EXC          | > Source type (composite or exclusive)                               |
+------------+--------------------+----------------------------------------------------------------------+
| VIS        | > PUB/PRV          | > Visibility (public or private)                                     |
+------------+--------------------+----------------------------------------------------------------------+
| CRT        | > R/W/RW/NIL       | > Automatically created accessors (read, write, read-write, or none) |
+------------+--------------------+----------------------------------------------------------------------+
| OVRD-MSG   | > \<message-name\> | > Name of message sent for slot-overrides in make-instance, etc.     |
+------------+--------------------+----------------------------------------------------------------------+
| SOURCE(S)  | > \<class-name\>+  | > Source of slot (more than one class for composite)                 |
+------------+--------------------+----------------------------------------------------------------------+

In the constraint information summary for the slots, each of the columns shows one of the primitive data types. A *+* in the column means that any value of that type is allowed in the slot. A *\#* in the column means that some values of that type are allowed in the slot. Range and cardinality constraints are displayed to the far right of each slot's row. The following table explains the abbreviations used in the constraint information summary for the slots.

  -------------------------------------
   **Abbreviation**   **Explanation**
  ------------------ ------------------
         SYM               Symbol

         STR               String

         INN           Instance Name

         INA          Instance Address

         EXA          External Address

         FTA            Fact Address

         INT              Integer

         FLT               Float

         RNG               Range

         CRD            Cardinality
  -------------------------------------

### 14.11.5 Examining the Class Hierarchy

The **browse-classes** command provides a rudimentary display of the inheritance relationships between a class and all its subclasses. Indentation indicates a subclass. Because of multiple inheritance, some classes may appear more than once. Asterisks mark classes which are direct subclasses of more than one class. With no arguments, this command starts with the root class OBJECT. This command has no return value.

Syntax

(browse‑classes \[\<class-name\>\])

Example

CLIPS\> (clear)

CLIPS\> (defclass A (is-a USER))

CLIPS\> (defclass B (is-a USER))

CLIPS\> (defclass C (is-a A B))

CLIPS\> (defclass D (is-a USER))

CLIPS\> (defclass E (is-a C D))

CLIPS\> (defclass F (is-a E))

CLIPS\> (browse-classes)

OBJECT

PRIMITIVE

NUMBER

INTEGER

FLOAT

LEXEME

SYMBOL

STRING

MULTIFIELD

ADDRESS

EXTERNAL-ADDRESS

FACT-ADDRESS

INSTANCE-ADDRESS \*

INSTANCE

INSTANCE-ADDRESS \*

INSTANCE-NAME

USER

A

C \*

E \*

F

B

C \*

E \*

F

D

E \*

F

CLIPS\>

## 14.12 Message‑handler Commands

The following commands manipulate defmessage‑handlers.

### 14.12.1 Displaying the Text of a Defmessage‑handler

The **ppdefmessage-handler** command sends the source text of a defmessage-handler to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdefmessage‑handler \<class-name\> \<handler-name\>

\[\<handler-type\> \[\<logical-name\>\]\])

\<handler-type\> ::= around \| before \| primary \| after

If the \<handler-type\> argument is not specified, it defaults to **primary**.

### 14.12.2 Displaying the List of Defmessage‑handlers

The list-defmessage-handlers command displays the names of defined defmessage-handlers.

Syntax

(list‑defmessage‑handlers \[\<class-name\> \[inherit\]\])

If no arguments are specified, this command lists all defined message-handlers. If the optional \<class-name\> argument is specified, this command lists all message-handlers for that class. In addition, if the optional argument **inherit** is specified, inherited message‑handlers are also listed. This command has no return value.

### 14.12.3 Deleting a Defmessage‑handler

The **undefmessage-handler** command deletes a previously defined message‑handler.

Syntax

(undefmessage‑handler \<class-name\> \<handler-name\>

\[\<handler-type\>\])

\<handler-type\> ::= around \| before \| primary \| after

If the \<handler-type\> argument is not specified, it defaults to **primary**. The symbol **\*** can be used to specify a wildcard for any of the arguments (unless there is a class or message-handler named **\***). This command has no return value.

### 14.12.4 Previewing a Message

The **preview-send** command displays a list of all the applicable message‑handlers for a message sent to an instance of a particular class. The level of indentation indicates the number of times a handler is shadowed, and lines connect the beginning and ending portions of the execution of a handler if it encloses shadowed handlers. The right double‑angle brackets indicate the beginning of handler execution, and the left double‑angle brackets indicate the end of handler execution. Message arguments are not necessary for a preview since they do not dictate handler applicability.

Syntax

(preview‑send \<class-name\> \<message-name\>)

Example

For the example in Section 9.5.3, the output would be:

CLIPS\> (preview-send USER my-message)

\>\> my-message around in class USER

\| \>\> my-message around in class OBJECT

\| \| \>\> my-message before in class USER

\| \| \<\< my-message before in class USER

\| \| \>\> my-message before in class OBJECT

\| \| \<\< my-message before in class OBJECT

\| \| \>\> my-message primary in class USER

\| \| \| \>\> my-message primary in class OBJECT

\| \| \| \<\< my-message primary in class OBJECT

\| \| \<\< my-message primary in class USER

\| \| \>\> my-message after in class OBJECT

\| \| \<\< my-message after in class OBJECT

\| \| \>\> my-message after in class USER

\| \| \<\< my-message after in class USER

\| \<\< my-message around in class OBJECT

\<\< my-message around in class USER

CLIPS\>

## 14.13 Definstances Commands

The following commands manipulate definstances.

### 14.13.1 Displaying the Text of a Definstances

The **ppdefinstances** command sends the source text of a definstances to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdefinstances \<definstances-name\> \[\<logical-name\>\])

#### 14.13.2 Displaying the List of Definstances

The **list-definstances** command displays the names of all defined definstances.

Syntax

(list‑definstances \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the names of all definstances in the current module are displayed. If the \<module‑name\> argument is specified, then the names of all definstances in the specified module are displayed. If the \<module‑name\> argument is the symbol **\***, then the names of all definstances in all modules are displayed. This command has no return value.

### 14.13.3 Deleting a Definstances

The **undefinstances** command deletes a previously defined definstances.

Syntax

(undefinstances \<definstances-name\>)

If the symbol **\*** is used for \<definstances‑name\>, then all definstances will be deleted (unless there exists a definstances called **\***). This command has no return value.

## 14.14 Instances Commands

The following commands manipulate instances of user‑defined classes.

### 14.14.1 Listing the Instances

The **instances** command lists existing instances.

Syntax

(instances \[\<module-name\> \[\<class-name\> \[inherit\]\]\])

If no arguments are specified, all instances in scope of the current module are listed. If a module name is given, all instances within the scope of that module are given. If the symbol **\*** is specified (and there is no module named **\***), all instances in all modules are listed (only instances which actually belong to classes of a module are listed for each module to prevent duplicates). If a class name is specified, only the instances for the named class are listed. If a class is specified, then the optional keyword **inherit** causes this command to list instances of subclasses of the class as well. This command has no return value.

### 14.14.2 Printing an Instance's Slots from a Handler

The **ppinstance** command directly prints the slots of the active instance and is the one used to implement the print handler attached to class USER. This command operates implicitly on the active instance for a message, and thus can only be called from within the body of a message‑handler. This command has no return value.

Syntax

(ppinstance)

### 14.14.3 Saving Instances to a Text File

The **save-instances** command saves all instances to the specified file using the following format.

(\<instance-name\> of \<class-name\> \<slot-override\>\*)

\<slot-override\> ::= (\<slot-name\> \<single-field-value\>\*)

A slot‑override is generated for every slot of every instance, regardless of whether the slot currently holds a default value or not. External‑address and fact‑address slot values are saved as strings. Instance‑address slot values are saved as instance‑names. This command returns the number of instances saved or -1 if an error occurs.

Syntax

(save‑instances \<file-name\> \[local \| visible \[\[inherit\] \<class\>+\])

By default, **save‑instances** saves only the instances of all defclasses in the current module. Specifying **visible** saves instances for all classes within scope of the current module. Also, particular classes may be specified for saving, but they must be in scope according to the **local** or **visible** option. The **inherit** keyword can be used to force the saving of indirect instances of named classes as well (by default only direct instances are saved for named classes). Subclasses must still be in **local** or **visible** scope in order for their instances to be saved. Unless the **inherit** option is specified, only concrete classes can be specified. At least one class is required for the inherit option.

The file generated by this command can be loaded by either the **load‑instances** or **restore‑instances** command. The **save‑instances** command does not preserve module information, so the instance file should be loaded into the module which was current when it was saved.

### 14.14.4 Saving Instances to a Binary File

The **bsave‑instances** command works exactly like **save‑instances** command except that the instances are saved in a binary format which can only be loaded with the **bload‑instances** command. The advantage to this format is that loading binary instances can be much faster than loading text instances for large numbers of instances. The disadvantage is that the file is not portable to other platforms.

Syntax

(bsave‑instances \<file-name\> \[local \| visible \[\[inherit\] \<class\>+\])

### 14.14.5 Loading Instances from a Text File

The **load-instances** command loads instances in text format from a file and creates them. It can read files created with the save‑instances command or any UTF-8 text file. Each instance should be in the format described for the **save-instances** command (although the instance name can be left unspecified). Calling **load‑instances** is exactly equivalent to a series of make‑instance calls. This command returns the number of instances loaded or ‑1 if it could not access the instance file.

Syntax

(load‑instances \<file-name\>)

### 14.14.6 Loading Instances from a Text File without Message Passing

The **restore‑instances** command loads instances from a file into the CLIPS environment. It can read files created with save‑instances or any UTF-8 text file. Each instance should be in the format described for the **save-instances** command (although the instance name can be left unspecified). It is similar in operation to **load‑instances**, however, unlike **load‑instances**, **restore‑instances** does not use message‑passing for deletions, initialization, or slot‑overrides. Thus in order to preserve object encapsulation, it is recommended that **restore‑instances** only be used with files generated by **save‑instances**. This command returns the number of instances loaded or ‑1 if it could not access the instance file.

Syntax

(restore‑instances \<file-name\>)

### 14.14.7 Loading Instances from a Binary File

The **bload-instances** command is similar to **restore‑instances** except that it can only work with files generated by **bsave‑instances**. This command returns the number of instances loaded or ‑1 if it could not access the instance file.

Syntax

(bload‑instances \<file-name\>)

## 14.15 Defmodule Commands

The following commands manipulate defmodule constructs.

### 14.15.1 Displaying the Text of a Defmodule

The **ppdefmodule** command sends the source text of a defmodule to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdefmodule \<defmodule-name\> \[\<logical-name\>\])

### 14.15.2 Displaying the List of Defmodules

The **list-defmodules** command displays the names of all defined defmodule constructs. This command has no return value.

Syntax

(list‑defmodules)

## 14.16 Memory Management Commands

The following commands display CLIPS memory status information.

### 14.16.1 Determining the Amount of Memory Used by CLIPS

The **mem-used** command returns an integer representing the number of bytes CLIPS has currently in‑use or cached for later use. This number does not include operating system overhead for allocating memory.

Syntax

(mem‑used)

### 14.16.2 Determining the Number of Memory Requests Made by CLIPS

The **mem-requests** command returns an integer representing the number of outstanding memory requests CLIPS has made from the operating system. If the operating system overhead for allocating memory is known or guestimated, then the total memory used can be calculated with the following formula.

(+ (mem-used) (\* \<overhead-in-bytes\> (mem-requests)))

Syntax

(mem‑requests)

### 14.16.3 Releasing Memory Used by CLIPS

The **release-mem** command releases all free memory cached by CLIPS back to the operating system. CLIPS will automatically call this command if it is running low on memory to allow the operating system to coalesce smaller memory blocks into larger ones. This command returns an integer representing the amount of memory freed to the operating system.

Syntax

(release‑mem)

### 14.16.4 Conserving Memory

The **conserve-mem** command is used to enable or disable the storage of the text representation for constructs used by the **save** and **pp\<construct\>** commands. It should be called prior to loading any constructs. This command has no return value.

Syntax

(conserve‑mem \<value\>)

The \<value\> argument should be the symbol **on** or **off**.

## 14.17 External Text Manipulation

CLIPS provides a set of functions to build and access a hierarchical lookup system for multiple external files. Each file contains a set of text entries in a special format that CLIPS can later reference and display. The basic concept is that CLIPS retains a map of the text file in memory and can easily pull sections of text from the file without having to store the whole file in memory and without having to sequentially search the file for the appropriate text.

### 14.17.1 External Text File Format

Each external text file to be loaded into CLIPS must be described in a particular way. Each topic entry in each file must be in the format shown following.

Syntax

\<level-num\> \<entry-type\> BEGIN-ENTRY- \<topic-name\>

•

•

Topic information in form to be displayed when referenced.

•

•

END-ENTRY

The delimiter strings (lines with BEGIN_ENTRY or END_ENTRY info) must be the only text on their lines. Embedded white space between the fields of the delimiters is allowed.

The first parameter, \<level‑num\>, is the level of the hierarchical tree to which the entry belongs. The lower the number, the closer to the root level the topic is; i.e., the lowest level number indicates the root level. Subtopics are indicated by making the level number of the current topic larger than the previous entry (which is the parent). Thus, the tree must be entered in the file sequentially; i.e., a topic with all its subtopics must be described before going on to a topic at the same level. Entering a number less than that of the previous topic will cause the tree to be searched upwards until a level number is found which is less than the current one. The current topic then will be at­tached as a subtopic at that level. In this manner, multiple root trees may be created. Level number and order of entry in a file can indicate the order of precedence in which a list of subtopics that are all children of the same topic will be searched. Topics with the same level number will be searched in the order in which they appear in the file. Topics with lower‑level numbers will be searched first.

Example

0MBEGIN-ENTRY-ROOT\
\-- Text \--\
END-ENTRY\
2IBEGIN-ENTRY-SUBTOPIC1\
\-- Text \--\
END-ENTRY\
1IBEGIN-ENTRY-SUBTOPIC2\
\-- Text \--\
END-ENTRY

In the above example, SUBTOPIC1 and SUBTOPIC2 are children of ROOT. However, in searching the children of ROOT, SUBTOPIC2 would be found first.

The second parameter in the format defined above, the \<entry‑type\>, must be a single capital letter, either M (for MENU) or I (for INFORMATION). Only MENU entries may have subtopics.

The third parameter defined above, the \<topic‑name\>, can be any alphanumeric string of up to 80 characters. No white space can be embedded in the name.

Beginning a line with the delimiter "\$\$" forces the loader to treat the line as pure text, even if one of the key delimiters is in it. When the line is printed, the dollar signs are treated as blanks.

Example

0MBEGIN-ENTRY-ROOT1\
\-- Root1 Text \--\
END-ENTRY\
1MBEGIN-ENTRY-SUBTOPIC1\
\-- Subtopic1 Text \--\
END-ENTRY\
2IBEGIN-ENTRY-SUBTOPIC4\
\-- Subtopic4 Text \--\
END-ENTRY\
1IBEGIN-ENTRY-SUBTOPIC2\
\-- Subtopic2 Text \--\
END-ENTRY\
0IBEGIN-ENTRY-ROOT2\
\-- Root2 Text \--\
END-ENTRY\
-1MBEGIN-ENTRY-ROOT3\
\-- Root3 Text \--\
END-ENTRY\
0IBEGIN-ENTRY-SUBTOPIC3\
\-- Subtopic3 Text \--\
END-ENTRY

Tree Diagram of Above Example :

‑\> ROOT3 ‑‑‑‑‑‑‑‑‑\> ROOT1 ‑‑‑‑‑‑‑‑‑\> ROOT2\
\| / \\

\| / \\\
V V V

SUBTOPIC3 SUBTOPIC1 SUBTOPIC2\
\|\
\|\
V\
SUBTOPIC4

### 14.17.2 Loading External Text

The **fetch** command loads the named file into the internal lookup table.

Syntax

(fetch \<file-name\>)

This command returns the number of entries loaded if the fetch succeeded. If the file could not be loaded or was loaded already, this command returns the symbol **FALSE**.

### 14.17.3 Printing External Text

The **print‑region** command looks up a specified entry in a particular file which has been loaded previously into the lookup table and prints the contents of that entry to the specified output.

Syntax

(print‑region \<logical-name\> \<file-name\> \<topic-field\>\*)

The \<logical‑name\> argument is a name previously associated with an output destination. The symbol **t** may be used as a shortcut for **stdout**. The \<file‑name\> argument is the name of the previously loaded file in which the entry is to be found. The optional \<topic‑field\>\* arguments are the full path of the topic entry to be found.

Each element or field in the path is delimited by white space, and the command is not case sensitive. In addition, the entire name of a field does not need to be specified. Only enough characters to distinguish the field from other choices at the same level of the tree are necessary. If there is a conflict, the command will pick the first one in the list. A few special fields can be specified.

\^ Branch up one level.

? When specified at the end of a path, this forces a display of the current menu, even on branch‑ups.

\<nil\> Giving no topic field will branch up one level.

The level of the tree for a file remains constant between calls to **print‑region**. All levels count only from the menu entry. Information levels do not count for branching up or down. To access an entry at the root level after branching down several levels in a previous call or series of calls, an equal number of branches up must be executed.

Examples

The following command displays the entry for ROOT SUBTOPIC from the file info.lis to standard output.

(print-region t \"info.lis\" ROOT SUBTOPIC)

The following command will also produce the same output using fewer characters.

(print-region t \"info.lis\" roo sub)

Only one entry can be accessed per **print‑region** call. This command returns the symbol **TRUE** if the **print‑region** call succeeded; otherwise, it returns the symbol **FALSE**.

CLIPS\> (fetch \"info.lis\")

7

CLIPS\> (print-region t \"info.lis\" roo sub)

\-- Subtopic3 Text \--

TRUE

CLIPS\> (print-region t \"info.lis\" \"?\")

\-- Root3 Text \--

TRUE

CLIPS\> (print-region t \"info.lis\" \^ root1 sub)

\-- Subtopic1 Text \--

TRUE

CLIPS\> (print-region t \"info.lis\" sub)

\-- Subtopic4 Text \--

TRUE

CLIPS\> (print-region t \"info.lis\" \^ subtopic2)

\-- Subtopic2 Text \--

TRUE

CLIPS\> (print-region t \"info.lis\" \^ root2)

\-- Root2 Text \--

TRUE

CLIPS\> (toss \"info.lis\")

TRUE

CLIPS\>

### 14.17.4 Retrieving External Text

The **get‑region** command looks up a specified entry in a particular file which has been loaded previously into the lookup table and returns the contents of that entry as a string.

Syntax

(get‑region \<file-name\> \<topic-field\>\*)

The \<file‑name\> argument is the name of the previously loaded file in which the entry is to be found, and the optional \<topic‑field\>\* arguments are the full path of the topic entry to be found. The **get-region** the **print-region** commands share the same behavior for the special topic fields and maintaining the level of the tree for a file between command calls. If an error occurs, this command returns an empty string.

### 14.17.5 Unloading an External Text File

The **toss** command unloads the named file from the internal lookup table and releases the memory back to the system.

Syntax

(toss \<file-name\>)

This command returns the symbol **TRUE** if the toss succeeded; otherwise, it returns the symbol **FALSE**.

## 14.18 Profiling Commands

The following commands provide the ability to profile CLIPS programs for performance.

### 14.18.1 Setting the Profiling Report Threshold

The **set-profile-percent-threshold** command sets the minimum percentage of time that must be spent executing a construct or user function for it to be displayed by the **profile-info** command. By default, the percent threshold is zero, so all constructs or user-functions that were profiled and executed at least once will be displayed by the **profile-info** command. The return value of this command is the old percent threshold.

Syntax

(set-profile-percent-threshold \<number in the range 0 to 100\>)

### 14.18.2 Getting the Profiling Report Threshold

The **get-profile-percent-threshold** command returns the current value of the profile percent threshold.

Syntax

(get-profile-percent-threshold)

### 14.18.3 Resetting Profiling Information

The **profile-reset** command resets all profiling information currently collected for constructs and user functions.

Syntax

(profile-reset)

### 14.18.4 Displaying Profiling Information

The **profile-info** command displays profiling information currently collected for constructs or user functions. Profiling information is displayed in six columns. The first column contains the name of the construct or user function profiled. The second column indicates the number of times the construct or user function was executed. The third column is the amount of time spent executing the construct or user function. The fourth column is the percentage of time spent in the construct or user function with respect to the total amount of time profiling was enabled. The fifth column is the total amount of time spent in the first execution of the construct or user function and all subsequent calls to other constructs/user functions. The sixth column is the percentage of this time with respect to the total amount of time profiling was enabled.

Syntax

(profile-info)

### 14.18.5 Profiling Constructs and User Functions

The **profile** command is used to enable/disable profiling of constructs and user functions. If **constructs** are profiled, then the amount of time spent executing deffunctions, generic functions, message handlers, and the RHS of defrules is tracked. If **user-functions** are profiled, then the time spent executing system and user-defined functions is tracked. System defined functions include predefined functions such as the **\<** and **numberp** functions in addition to low level internal functions which can not be directly called (these will usually appear in **profile-info** output in all capital letters or surrounded by parentheses). It is not possible to profile constructs and user-functions at the same time; enabling one disables the other. The **off** keyword argument disables profiling. Profiling can be repeatedly enable and disabled as long as only one of **constructs** or **user-functions** is consistently enabled. The total amount of time spent with profiling enabled will be displayed by the **profile-info** command. If profiling is enabled from the command prompt, it is a good idea to place the calls enabling and disabling profiling within a single **progn** function call. This will prevent the elapsed profiling time from including the amount of time needed to type the commands being profiled.

Syntax

(profile constructs \| user-functions \| off)

Example

CLIPS\> (clear)

CLIPS\> (deffacts start (fact 1))

CLIPS\>

(deffunction function-1 (?x)

(bind ?y 1)

(loop-for-count (\* ?x 100)

(bind ?y (+ ?y ?x))))

CLIPS\>

(defrule rule-1

?f \<- (fact ?x&:(\< ?x 100))

=\>

(function-1 ?x)

(retract ?f)

(assert (fact (+ ?x 1))))

CLIPS\> (reset)

CLIPS\>

(progn (profile constructs)

(run)

(profile off))

CLIPS\> (profile-info)

Profile elapsed time = 15.9657 seconds

Construct Name Entries Time % Time+Kids %+Kids

\-\-\-\-\-\-\-\-\-\-\-\-\-- \-\-\-\-\-\-- \-\-\-\-\-- \-\-\-\-- \-\-\-\-\-\-\-\-- \-\-\-\-\--

\*\*\* Deffunctions \*\*\*

function-1 99 0.154689 0.97% 0.154689 0.97%

\*\*\* Defrules \*\*\*

rule-1 99 0.000212 0.00% 0.154902 0.97%

CLIPS\> (profile-reset)

CLIPS\> (reset)

CLIPS\>

(progn (profile user-functions)

(run)

(profile off))

CLIPS\> (profile-info)

Profile elapsed time = 0.401675 seconds

Function Name Entries Time % Time+Kids %+Kids

\-\-\-\-\-\-\-\-\-\-\-\-- \-\-\-\-\-\-- \-\-\-\-\-- \-\-\-\-- \-\-\-\-\-\-\-\-- \-\-\-\-\--

retract 99 0.007953 0.07% 0.010646 0.09%

retract 99 0.000111 0.03% 0.000129 0.03%

assert 99 0.000185 0.05% 0.000275 0.07%

run 1 0.000124 0.03% 0.401674 100.00%

profile 1 0.000001 0.00% 0.000001 0.00%

\* 99 0.000028 0.01% 0.000030 0.01%

\+ 495099 0.124870 31.09% 0.187941 46.79%

\< 99 0.000020 0.01% 0.000031 0.01%

progn 495198 0.059189 14.74% 0.401551 99.97%

loop-for-count 99 0.073839 18.38% 0.400954 99.82%

PCALL 99 0.000103 0.03% 0.401114 99.86%

FACT_PN_VAR3 99 0.000011 0.00% 0.000011 0.00%

FACT_JN_VAR1 99 0.000019 0.00% 0.000019 0.00%

FACT_JN_VAR3 198 0.000010 0.00% 0.000010 0.00%

FACT_STORE_MULTIFIELD 99 0.000031 0.01% 0.000059 0.01%

PROC_PARAM 495099 0.031070 7.74% 0.031070 7.74%

PROC_GET_BIND 495000 0.031995 7.97% 0.031995 7.97%

PROC_BIND 495099 0.080070 19.93% 0.267983 66.72%

CLIPS\> (set-profile-percent-threshold 1)

0.0

CLIPS\> (profile-info)

Profile elapsed time = 12.0454 seconds

Function Name Entries Time % Time+Kids %+Kids

\-\-\-\-\-\-\-\-\-\-\-\-- \-\-\-\-\-\-- \-\-\-\-\-- \-\-\-\-- \-\-\-\-\-\-\-\-- \-\-\-\-\--

\+ 49599 3.626217 30.10% 5.765490 47.86%

\+ 495099 0.124870 31.09% 0.187941 46.79%

progn 495198 0.059189 14.74% 0.401551 99.97%

loop-for-count 99 0.073839 18.38% 0.400954 99.82%

PROC_PARAM 495099 0.031070 7.74% 0.031070 7.74%

PROC_GET_BIND 495000 0.031995 7.97% 0.031995 7.97%

PROC_BIND 495099 0.080070 19.93% 0.267983 66.72%

CLIPS\> (profile-reset)

CLIPS\> (profile-info)

CLIPS\>

## 14.19 Goal Commands

The following commands display information about goals.

### 14.19.1 Displaying the Goal-List

The **goals** command lists existing goals.

Syntax

(goals \[\<module-name\>\]

\[\<start-integer-expression\>

\[\<end-integer-expression\>

\[\<max-integer-expression\>\]\]\])

If the \<module‑name\> argument is not specified, then only goals visible to the current module will be displayed. If the \<module‑name\> argument is specified, then only goals visible to the specified module are displayed. If the symbol **\*** is used for the \<module‑name\> argument, then goals from any module may be displayed. If the start argument is speci­fied, only goals with goal‑indices greater than or equal to this argument are displayed. If the end argument is speci­fied, only goal with goal‑indices less than or equal to this argument are displayed. If the max argument is speci­fied, then no goals will be displayed beyond the specified maximum number of goals to be displayed. This command has no return value.

### 14.19.2 Determining Why a Goal was Generated

The **why** command lists the rules that caused the generation of a goal.

Syntax

(why \<integer-expression\>)

If the \<module‑name\> argument is not specified, then only goals visible to the current module will be displayed. If the \<module‑name\> argument is specified, then only goals visible to the specified module are displayed. If the symbol **\*** is used for the \<module‑name\> argument, then goals from any module may be displayed. If the start argument is speci­fied, only goals with goal‑indices greater than or equal to this argument are displayed. If the end argument is speci­fied, only goal with goal‑indices less than or equal to this argument are displayed. If the max argument is speci­fied, then no goals will be displayed beyond the specified maximum number of goals to be displayed. This command has no return value.

## 14.20 Deftable Commands

The following commands manipulate deftables.

### 14.20.1 Displaying the Text of a Deftable

The **ppdeftable** command sends the source text of a deftable to a logical name as output. If the \<logical-name\> argument is **t** or unspecified, then output is sent to the logical name **stdout**, otherwise it is sent to the specified logical name. If the logical name **nil** is used, then the text is used as the return value of this command rather than being sent to an output destination; otherwise this command has no return value.

Syntax

(ppdeftable \<deftable-name\> \[\<logical-name\>\])

### 14.20.2 Displaying the List of Deftables

The **list-deftables** command displays the names of all defined deftables.

Syntax

(list‑deftables \[\<module-name\>\])

If the \<module‑name\> argument is unspecified, then the names of all deftables in the current module are displayed. If the \<module‑name\> argument is specified, then the names of all deftables in the specified module are displayed. If the \<module‑name\> argument is the symbol **\***, then the names of all deftables in all modules are displayed. This command has no return value.

### 14.20.3 Deleting a Deftable

The **undeftable** command deletes a previously defined deftable.

Syntax

(undeftable \<deftable-name\>)

If the symbol **\*** is used for the \<deftable‑name\> argument, then all deftables will be deleted (unless there exists a deftable named **\***). This command has no return value.
