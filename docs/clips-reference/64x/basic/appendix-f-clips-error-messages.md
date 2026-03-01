# Appendix F: CLIPS Error Messages

CLIPS typically will display two kinds of error messages: those associated with executing constructs and those associated with loading constructs. This appendix describes some of the more common error messages and what they mean. Each message begins with a unique identifier enclosed in brackets; the messages are listed here in alphabetic order according to the identifier.

\[ANALYSIS1\] Duplicate pattern‑address \<variable name\> found in CE \<CE number\>.

This message occurs when two facts or instances are bound to the same pattern‑address variable.

Example:

CLIPS\> (defrule error ?f \<- (a) ?f \<- (b) =\>)

\[ANALYSIS2\] Pattern‑address \<variable name\> used in CE #2 was previously bound within a pattern CE.

A variable first bound within a pattern cannot be later bound to a fact‑address.

Example:

CLIPS\> (defrule error (a ?f) ?f \<- (b) =\>)

\[ANALYSIS3\] Variable \<variable name\> is used as both a single and multifield variable in the LHS.

Variables on the LHS of a rule cannot be bound to both single and multifield variables.

Example:

CLIPS\> (defrule error (a ?x \$?x) =\>)

\[ANALYSIS4\] Variable \<variable name\> \[found in the expression \<expression\>\]

was referenced in CE \<CE number\> \<field or slot identifier\> before being defined

A variable cannot be referenced before it is defined and, thus, results in this error message.

Example:

CLIPS\> (defrule error (a \~?x) =\>)

\[ARGACCES1\] Function \<name\> expected exactly \<number\> argument(s).

This error occurs when a function that expects a precise number of argument(s) re­ceives an incorrect number of arguments.

\[ARGACCES1\] Function \<name\> expected at least \<number\> argument(s).

This error occurs when a function does not receive the minimum number of argu­ment(s) that it expected.

\[ARGACCES1\] Function \<name\> expected no more than \<number\> argument(s).

This error occurs when a function receives more than the maximum number of argu­ment(s) expected.

\[ARGACCES2\] Function \<name\> expected argument #\<number\> to be of type \<data‑type\>.

This error occurs when a function is passed the wrong type of argument.

\[ARGACCES3\] Function \<function‑name\> was unable to open file \<file‑name\>.

This error occurs when the specified function cannot open a file.

\[BLOAD1\] Cannot load \<construct type\> construct with binary load in effect.

If the bload command was used to load in a binary image, then the named construct cannot be entered until a clear command has been performed to remove the binary image.

\[BLOAD2\] File \<file‑name\> is not a binary construct file.

This error occurs when the bload command is used to load a file that was not cre­ated with the bsave command.

\[BLOAD3\] File \<file‑name\> is an incompatible binary construct file.

This error occurs when the bload command is used to load a file that was cre­ated with the bsave command using a different version of CLIPS.

\[BLOAD4\] The CLIPS environment could not be cleared.\
Binary load cannot continue.

A binary load cannot be performed unless the current CLIPS environment can be cleared.

\[BLOAD5\] Some constructs are still in use by the current binary image:\
\<construct‑name 1\>\
\<construct‑name 2\>\
\...\
\<construct‑name N\>

Binary \<operation\> cannot continue.

This error occurs when the current binary image cannot be cleared because some constructs are still being used. The \<operation\> in progress may either be a binary load or a binary clear.

\[BLOAD6\] The following undefined functions are referenced by this binary image:\
\<function‑name 1\>\
\<function‑name 2\>\
\...\
\<function‑name N\>

This error occurs when a binary image is loaded that calls functions which were available in the CLIPS executable that originally created the binary image, but which are not available in the CLIPS executable that is loading the binary image.

\[BSAVE1\] Cannot perform a binary save while a binary load is in effect.

The bsave command does not work when a binary image is loaded.

\[CLASSEXM1\] Inherited slot \<slot‑name\> from class \<class‑name\> is not valid for function \<name\>.

This error message occurs when functions expecting a slot name defined for a class is given an inherited slot.

Example:

CLIPS\>

(defclass ORDER (is-a USER)

(slot id (visibility private)))

CLIPS\> (defclass SPECIAL-ORDER (is-a ORDER))

CLIPS\> (slot-publicp SPECIAL-ORDER id)

\[CLASSFUN1\] Unable to find class \<class name\> in function \<function name\>.

This error message occurs when a function is given a non‑existent class name.

Example:

CLIPS\> (class-slots MACHINE)

\[CLASSFUN2\] Maximum number of simultaneous class hierarchy traversals exceeded \<number\>.

This error is usually caused by too many simultaneously active instance‑set queries, e.g., **do‑for‑all‑instances**. The direct or indirect nesting of instance‑set query functions is limited in the following way:

Ci is the number of members in an instance‑set for the ith nested instance‑set query function.

N is the number of nested instance‑set query functions.

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------
  ![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image9.emf){width="0.3888888888888889in" height="0.4722222222222222in"}   \<= 256 (the default upper limit)

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------

Example:

CLIPS\>

(deffunction my-func ()

(do-for-instance ((?a USER) (?b USER) (?c USER)) TRUE

(println ?a \" \" ?b \" \" ?c)))

; The sum here is C1 = 3 which is OK.

CLIPS\>

(do-for-all-instances ((?a OBJECT) (?b OBJECT)) TRUE

(my-func))

; The sum here is C1 + C2 = 2 + 3 = 5 which is OK.

The default upper limit of 256 should be sufficient for most if not all applications. However, the limit may be increased by editing the header file object.h and recompiling CLIPS.

\[CLASSPSR1\] An abstract class cannot be reactive.

Only concrete classes can be reactive.

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(role abstract)

(pattern-match reactive))

\[CLASSPSR2\] Cannot redefine a predefined system class.

Predefined system classes cannot be modified by the user.

Example:

CLIPS\> (defclass STRING (is-a NUMBER))

\[CLASSPSR3\] Class \<name\> cannot be redefined while outstanding references to it still exist.

This error occurs when an attempt to redefine a class is made under one or both of the following two circumstances:

1\) The class (or any of its subclasses) has instances.

2\) The class (or any of its subclasses) appear in the parameter restrictions of any generic function method.

Before the class can be redefined, all such instances and methods must be deleted.

Example:

CLIPS\> (defclass A (is-a USER))

CLIPS\> (defmethod AM ((?a A LEXEME)))

CLIPS\> (defclass A (is-a OBJECT)))

\[CLASSPSR4\] The \<attribute\> class attribute is already declared.

Only one specification of a class attribute is allowed.

Example:

CLIPS\>

(defclass A (is-a USER)

(role abstract)

(role concrete))

\[CLSLTPSR1\] The \<slot-name\> slot for class \<class-name\> is already specified.

Slots in a defclass must be unique.

Example:

CLIPS\>

(defclass ORDER (is-a USER)

(slot id)

(slot id))

\[CLSLTPSR2\] The \<name\> facet for slot \<slot-name\> is already specified.

Only one occurrence of a facet per slot is allowed.

Example:

CLIPS\>

(defclass ORDER (is-a USER)

(slot id (access read-only)

(access read-write)))

\[CLSLTPSR3\] The \'cardinality\' facet can only be used with multifield slots.

Single‑field slots by definition have a cardinality of one.

Example:

CLIPS\>

(defclass PERSON (is-a USER)

(slot favorites (cardinality 0 5)))

\[CLSLTPSR4\] Slots with an \'access\' facet value of \'read‑only\' must have a default value.

Since slots cannot be unbound and **read‑only** slots cannot be set after initial creation of the instance, **read‑only** slots must have a default value.

Example:

CLIPS\>

(defclass PERSON (is-a USER)

(slot age (access read-only)

(default ?NONE)))

\[CLSLTPSR5\] Slots with an \'access\' facet value of \'read‑only\' cannot have a write accessor.

Since **read‑only** slots cannot be changed after initializationof the instance, a **write** accessor (**put‑** message‑handler) is not allowed.

Example:

CLIPS\>

(defclass PERSON (is-a USER)

(slot age (access read-only)

(create-accessor write)))

\[CLSLTPSR6\] Slots with a \'propagation\' value of \'no‑inherit\' cannot have a \'visibility\' facet value of \'public\'.

**no‑inherit** slots are by definition not accessible to subclasses and thus only visible to the parent class.

Example:

CLIPS\>

(defclass PERSON (is-a USER)

(slot age (propagation no-inherit)

(visibility public)))

\[COMMLINE1\] Expected a \'(\', constant, or global variable.

This message occurs when a top‑level command does not begin with a \'(\', constant, or global variable.

Example:

CLIPS\> )

\[COMMLINE2\] Expected a command.

This message occurs when a top‑level command is not a symbol.

Example:

CLIPS\> (\"facts\")

\[CONSCOMP1\] Invalid file name \<fileName\> contains \'.\'

A \'.\' cannot be used in the file name prefix that is passed to the constructs‑to‑c command since this prefix is used to generate file names and some operating systems do not allow more than one \'.\' to appear in a file name.

\[CONSCOMP2\] Aborting because the base file name may cause the fopen maximum of \<integer\> to be violated when file names are generated.

The constructs‑to‑c command generates file names using the file name prefix supplied as an argument. If this base file name is longer than the maximum supported by the operating system, then the possibility exists that files may be overwritten.

\[CONSTRCT1\] Some constructs are still in use. Clear cannot continue.

This error occurs when the clear command is issued when a construct is in use (such as a rule that is firing).

\[CSTRCPSR1\] Expected the beginning of a construct.

This error occurs when the load command expects a left parenthesis followed a construct type and these token types are not found.

\[CSTRCPSR2\] Missing name for \<construct‑type\> construct.

This error occurs when the name is missing for a construct that requires a name.

Example:

CLIPS\> (defgeneric ())

\[CSTRCPSR3\] Cannot define \<construct‑type\> \<construct‑name\> because of an import/export conflict.

or

\[CSTRCPSR3\] Cannot define defmodule \<defmodule‑name\> because of an import/export conflict cause by the \<construct‑type\> \<construct‑name\>.

A construct cannot be defined if defining the construct would allow two different definitions of the same construct type and name to both be visible to any module.

Example:

CLIPS\> (defmodule MAIN (export ?ALL))

CLIPS\> (deftemplate MAIN::start)

CLIPS\> (defmodule DATA (import MAIN ?ALL))

CLIPS\> (deftemplate DATA::start (slot file-name))

\[CSTRCPSR4\] Cannot redefine \<construct‑type\> \<construct‑name\> while it is in use.

A construct cannot be redefined while it is being used by another construct or other data structure (such as a fact or instance).

Example:

CLIPS\> (deftemplate person)

CLIPS\> (assert (person))

\<Fact-1\>

CLIPS\> (deftemplate person (slot age))

\[CSTRNCHK1\] *Message Varies*

This error ID covers a range of messages indicating a type, value, range, or cardinality violation.

Example:

CLIPS\> (deftemplate person (slot age (type INTEGER)))

CLIPS\> (assert (person (age thirteen)))

\[CSTRNPSR1\] The \<first attribute name\> attribute conflicts with the \<second attribute name\> attribute.

This error message occurs when two slot attributes conflict.

Example:

CLIPS\> (deftemplate person (slot age (type SYMBOL) (range 0 120)))

\[CSTRNPSR2\] Minimum \<attribute\> value must be less than or equal to the maximum \<attribute\> value.

The minimum attribute value for the range and cardinality attributes must be less than or equal to the maximum attribute value for the attribute.

Example:

CLIPS\> (deftemplate person (slot age (range 120 0)))

\[CSTRNPSR3\] The \<first attribute name\> attribute cannot be used in conjunction with the \<second attribute name\> attribute.

The use of some slot attributes excludes the use of other slot attributes.

Example:

CLIPS\>

(deftemplate person

(slot gender (allowed-values male)

(allowed-symbols female)))

\[CSTRNPSR4\] Value does not match the expected type for the \<attribute name\> attribute.

The arguments to an attribute must match the type expected for that attribute (e.g. integers must be used for the allowed‑integers attribute).

Example:

CLIPS\>

(deftemplate person

(slot gender (allowed-strings male female)))

\[CSTRNPSR5\] The \'cardinality\' attribute can only be used with multifield slots.

The cardinality attribute can only be used for slots defined with the multislot keyword.

Example:

CLIPS\> (deftemplate person (slot age (cardinality 1 1)))

\[CSTRNPSR6\] Minimum \'cardinality\' value must be greater than or equal to zero.

A multislot with no value has a cardinality of 0. It is not possible to have a lower cardinality.

Example:

CLIPS\> (deftemplate person (multislot hobbies (cardinality -1 5)))

\[DEFAULT1\] The default value for a single field slot must be a single field value.

This error occurs when the default or default‑dynamic attribute for a single‑field slot does not contain a single value or an expression returning a single value.

Example:

CLIPS\> (deftemplate person (slot age (default)))

\[DFFNXPSR1\] Deffunctions are not allowed to replace constructs.

A deffunction cannot have the same name as any construct.

Example:

CLIPS\> (deffunction defgeneric ())

\[DFFNXPSR2\] Deffunctions are not allowed to replace external functions.

A deffunction cannot have the same name as any system or user‑defined external function.

Example:

CLIPS\> (deffunction + ())

\[DFFNXPSR3\] Deffunctions are not allowed to replace generic functions.

A deffunction cannot have the same name as any generic function.

Example:

CLIPS\> (defgeneric start)

CLIPS\> (deffunction start ())

\[DFFNXPSR4\] Deffunction \<name\> may not be redefined while it is executing.

A deffunction can be loaded at any time except when a deffunction of the same name is already executing.

Example:

CLIPS\>

(deffunction create ()

(build \"(deffunction create ())\"))

CLIPS\> (create)

**\[DFFNXPSR5\] Defgeneric \<name\> imported from module \<module name\> conflicts with this deffunction.**

A deffunction cannot have the same name as any generic function imported from another module.

Example:

CLIPS\> (defmodule MAIN (export ?ALL))

CLIPS\> (defmethod start ())

CLIPS\> (defmodule DATA (import MAIN ?ALL))

CLIPS\> (deffunction start)

\[DRIVE1\] This error occurred in the join network.

Problem resides in associated join

Of pattern #\<pattern-number\> in rule \<rule-name\>

This error pinpoints other evaluation errors associated with evaluating an expression within the join network. The specific pattern of the problem rules is identified.

\[EMATHFUN1\] Domain error for \<function‑name\> function.

This error occurs when an argument passed to a math function is not in the domain of values for which a return value exists.

\[EMATHFUN2\] Argument overflow for \<function‑name\> function.

This error occurs when an argument to an extended math function would cause a numeric overflow.

\[EMATHFUN3\] Singularity at asymptote in \<function‑name\> function.

This error occurs when an argument to a trigonometric math function would cause a singularity.

\[EVALUATN1\] Variable \<name\> is unbound

This error occurs when a local variable not set by a previous call to **bind** is accessed at the top-level.

Example:

CLIPS\> (progn ?error)

\[EXPRNPSR1\] A function name must be a symbol.

In the following example, \'**\~**\' is recognized by CLIPS as an operator, not a function:

Example:

CLIPS\> (+ (\~ 3 4) 4)

\[EXPRNPSR2\] Expected a constant, variable, or expression.

In the following example, \'**\~**\' is an operator and is illegal as an argument to a function call:

Example:

CLIPS\> (\<= \~ 4)

\[EXPRNPSR3\] Missing function declaration for \<name\>.

CLIPS does not recognize \<name\> as a declared function and gives this error message.

Example:

CLIPS\> (undefined)

\[EXPRNPSR4\] \$ Sequence operator not a valid argument for \<name\>.

The sequence expansion operator cannot be used with certain functions.

Example:

CLIPS\> (set-sequence-operator-recognition TRUE)

FALSE

CLIPS\> (defrule error (list \$?v) =\> (assert (copy-list \$?v)))

\[FACTMCH1\] This error occurred in the fact pattern network

Currently active fact: \<newly assert fact\>

Problem resides in slot \<slot name\>

Of pattern #\<pattern‑number\> in rule \<rule name\>

This error pinpoints other evaluation errors associated with evaluating an expression within the pattern network. The specific pattern and field of the problem rules are identified.

\[FACTMNGR1\] Facts may not be retracted during pattern‑matching

or

\[FACTMNGR2\] Facts may not be asserted during pattern‑matching

Functions used on the LHS of a rule should not have side effects (such as the creation of a new instance or fact).

Example:

CLIPS\> (defrule error (start) (test (assert (end))) =\>)

CLIPS\> (assert (start))

\[FACTRHS1\] Implied deftemplate \<name\> cannot be created with binary load in effect.

This error occurs when an assert is attempted for a deftemplate which does not exist in a runtime or active **bload** image. In other situations, CLIPS will create an implied deftemplate if one does not already exist.

Example:

CLIPS\> (clear)

CLIPS\> (bsave error.bin)

TRUE

CLIPS\> (bload error.bin)

TRUE

CLIPS\> (assert (error))

\[GENRCCOM1\] No such generic function \<name\> in function undefmethod.

This error occurs when the generic function name passed to the undefmethod function does not exist.

Example:

CLIPS\> (undefmethod process 3)

\[GENRCCOM2\] Expected a valid method index in function undefmethod.

This error occurs when an invalid method index is passed to undefmethod (e.g. a negative integer or a symbol other than \*).

Example:

CLIPS\> (defmethod process ())

CLIPS\> (undefmethod process a)

\[GENRCCOM3\] Incomplete method specification for deletion.

It is illegal to specify a non‑wildcard method index when a wildcard is given for the generic function in the **undefmethod** command.

Example:

CLIPS\> (undefmethod \* 1)

\[GENRCCOM4\] Cannot remove implicit system function method for generic function \<name\>.

A method corresponding to a system defined function cannot be deleted.

Example:

CLIPS\> (defmethod integer ((?x SYMBOL)) 0)

CLIPS\> (list-defmethods integer)

integer #SYS1 (NUMBER)

integer #2 (SYMBOL)

For a total of 2 methods.

CLIPS\> (undefmethod integer 1)

\[GENRCEXE1\] No applicable methods for \<name\>.

The generic function call arguments do not satisfy any method's parameter restrictions.

Example:

CLIPS\> (defmethod process ())

CLIPS\> (process 1 2)

\[GENRCEXE2\] Shadowed methods not applicable in current context.

No shadowed method is available when the **call‑next‑method** function is called.

Example:

CLIPS\> (call-next-method)

\[GENRCEXE3\] Unable to determine class of \<value\> in generic function \<name\>.

The class or type of a generic function argument could not be determined for comparison to a method type restriction.

Example:

CLIPS\> (defmethod process ((?a INTEGER)))

CLIPS\> (process \[invalid\])

\[GENRCEXE4\] Generic function \<name\> method #\<index\> is not applicable to the given arguments.

This error occurs when **call‑specific‑method** is called with an inappropriate set of arguments for the specified method.

Example:

CLIPS\> (defmethod process ())

CLIPS\> (call-specific-method process 1 a)

\[GENRCFUN1\] Defgeneric \<name\> cannot be modified while one of its methods is executing.

Defgenerics can't be redefined while one of their methods is currently executing.

Example:

CLIPS\> (defgeneric process)

CLIPS\> (defmethod process () (build \"(defgeneric process)\"))

CLIPS\> (process)

\[GENRCFUN2\] Unable to find method \<name\> #\<index\> in function \<name\>.

No generic function method of the specified index could be found by the named function.

Example:

CLIPS\> (defmethod process 1 ())

CLIPS\> (ppdefmethod process 2)

\[GENRCFUN3\] Unable to find generic function \<name\> in function \<name\>.

No generic function method of the specified index could be found by the named function.

Example:

CLIPS\> (preview-generic error)

\[GENRCPSR1\] Expected \')\' to complete defgeneric.

A right parenthesis completes the definition of a generic function header.

Example:

CLIPS\> (defgeneric process ())

\[GENRCPSR2\] New method #\<index1\> would be indistinguishable from method #\<index2\>.

An explicit index has been specified for a new method that does not match that of an older method which has identical parameter restrictions.

Example:

CLIPS\> (defmethod process 1 ((?a INTEGER)))

CLIPS\> (defmethod process 2 ((?a INTEGER)))

\[GENRCPSR3\] Defgenerics are not allowed to replace constructs.

A generic function cannot have the same name as any construct.

**\[GENRCPSR4\] Deffunction \<name\> imported from module \<module name\> conflicts with this defgeneric.**

A deffunction cannot have the same name as any generic function imported from another module.

Example:

CLIPS\> (defmodule MAIN (export ?ALL))

CLIPS\> (deffunction process ())

CLIPS\> (defmodule DATA (import MAIN ?ALL))

CLIPS\> (defmethod process)

\[GENRCPSR5\] Defgenerics are not allowed to replace deffunctions.

A generic function cannot have the same name as any deffunction.

\[GENRCPSR6\] Method index out of range.

A method index cannot be greater than the maximum value of an integer or less than 1.

Example:

CLIPS\> (defmethod process 0)

\[GENRCPSR7\] Expected a \'(\' to begin method parameter restrictions.

A left parenthesis must begin a parameter restriction list for a method.

Example:

CLIPS\> (defmethod process)

\[GENRCPSR8\] Expected a variable for parameter specification.

A method parameter with restrictions must be a variable.

Example:

CLIPS\> (defmethod process ((value)))

\[GENRCPSR9\] Expected a variable or \'(\' for parameter specification.

A method parameter must be a variable with or without restrictions.

Example:

CLIPS\> (defmethod process (value))

\[GENRCPSR10\] Query must be last in parameter restriction.

A query parameter restriction must follow a type parameter restriction (if any).

Example:

CLIPS\> (defmethod process ((?a (\< ?a 1) INTEGER)))

\[GENRCPSR11\] Duplicate classes/types not allowed in parameter restriction.

A method type parameter restriction may have only a single occurrence of a particular class.

Example:

CLIPS\> (defmethod process ((?a INTEGER INTEGER)))

\[GENRCPSR12\] Binds are not allowed in query expressions.

Binding new variables in a method query parameter restriction is illegal.

Example:

CLIPS\> (defmethod process ((?a (bind ?b 1))))

\[GENRCPSR13\] Expected a valid class/type name or query.

Method parameter restrictions consist of zero or more class names and an optional query expression.

Example:

CLIPS\> (defmethod process ((?a 34)))

\[GENRCPSR14\] Unknown class/type in method.

Classes in method type parameter restrictions must already be defined.

Example:

CLIPS\> (defmethod process ((?a UNKNOWN-CLASS)))

\[GENRCPSR15\] Class \<name\> is redundant.

All classes in a method type parameter restriction should be unrelated.

Example:

CLIPS\> (defmethod process ((?a INTEGER NUMBER)))

\[GENRCPSR16\] The system function \<name\> cannot be overloaded.

Some system functions canot be overloaded.

Example:

CLIPS\> (defmethod if ())

\[GENRCPSR17\] Cannot replace the implicit system method #\<integer\>.

A system function can not be overloaded with a method that has the exact number and types of arguments.

Example:

CLIPS\> (defmethod integer ((?x NUMBER)) (\* 2 ?x))

\[GLOBLDEF1\] Global variable \<variable name\> is unbound.

A global variable must be defined before it can be accessed at the command prompt or elsewhere.

Example:

CLIPS\> (clear)

CLIPS\> ?\*x\*

\[GLOBLPSR1\] Global variable \<variable name\> was referenced, but is not defined.

A global variable must be defined before it can be accessed at the command prompt or elsewhere.

Example:

CLIPS\> (clear)

CLIPS\> (bind ?\*x\* 1)

\[INHERPSR1\] A class may not have itself as a superclass.

A class may not inherit from itself.

Example:

CLIPS\> (defclass MACHINE (is-a MACHINE))

\[INHERPSR2\] A class may inherit from a superclass only once.

All direct superclasses of a class must be unique.

Example:

CLIPS\> (defclass MACHINE (is-a USER USER))

\[INHERPSR3\] A class must be defined after all its superclasses.

Subclasses must be defined last.

Example:

CLIPS\> (defclass MACHINE (is-a DEVICE))

\[INHERPSR4\] A class must have at least one superclass.

All user‑defined classes must have at least one direct superclass.

Example:

CLIPS\> (defclass MACHINE (is-a))

\[INHERPSR5\] Partial precedence list formed: \<classa\> \<classb\> ... \<classc\>

Precedence loop in superclasses: \<class1\> \<class2\> ... \<classn\> \<class1\>

No class precedence list satisfies the rules specified in section 9.3.1.1 for the given direct superclass list. The message shows a conflict for \<class1\> because the precedence implies that \<class1\> must both precede and succeed \<class2\> through \<classn\>. The full loop can be used to help identify which particular classes are causing the problem. This loop is not necessarily the only loop in the precedence list; it is the first one detected. The part of the precedence list which was successfully formed is also listed.

Example:

CLIPS\> (defclass A (is-a MULTIFIELD FLOAT SYMBOL))

CLIPS\> (defclass B (is-a SYMBOL FLOAT))

CLIPS\> (defclass C (is-a A B))

\[INHERPSR6\] A user‑defined class cannot be a subclass of \<name\>.

The INSTANCE, INSTANCE‑NAME, and INSTANCE‑ADDRESS classes cannot have any subclasses.

Example:

CLIPS\> (defclass MACHINE (is-a INSTANCE))

\[INSCOM1\] Undefined type in function \<name\>.

The evaluation of an expression yielded something other than a recognized class or primitive type.

\[INSFILE1\] Function \<function‑name\> could not completely process file \<name\>.

This error occurs when an instance definition is improperly formed in the input file for the **load‑instances**, **restore‑instances**, or **bload‑instances** command.

Example:

CLIPS\> (load-instances bogus.txt)

\[INSFILE2\] File \<file‑name\> is not a binary instances file.

or

\[INSFILE3\] File \<file‑name\> is not a compatible binary instances file.

This error occurs when bload‑instances attempts to load a file that was not created with bsave‑instances or when the file being loaded was created by a different version of CLIPS.

Example:

CLIPS\> (reset)

CLIPS\> (save-instances data.ins)

1

CLIPS\> (bload-instances data.ins)

\[INSFILE4\] Function \'bload‑instances\' is unable to load instance \<instance‑name\>.

This error occurs when an instance specification in the input file for the **bload‑instances** command could not be created.

Example:

CLIPS\> (defclass A (is-a USER))

CLIPS\> (make-instance of A)

\[gen1\]

CLIPS\> (bsave-instances data.bin)

1

CLIPS\> (clear)

CLIPS\> (defclass A (is-a USER) (role abstract))

CLIPS\> (bload-instances data.bin)

\[INSFUN1\] Expected a valid instance in function \<name\>.

The named function expected an instance‑name or address as an argument.

Example:

CLIPS\> (initialize-instance 34)

\[INSFUN2\] No such instance \<name\> in function \<name\>.

This error occurs when the named function cannot find the specified instance.

Example:

CLIPS\> (instance-address \[invalid-instance\])

\[INSFUN3\] No such slot \<name\> in function \<name\>.

This error occurs when the named function cannot find the specified slot in an instance or class.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (slot-writablep MACHINE id)

\[INSFUN4\] Invalid instance‑address in function \<name\>, argument #\<integer\>.

This error occurs when an attempt is made to use the address of a deleted instance.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (defglobal ?\*selected-machine\* = (instance-address \[m\]))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (class ?\*selected-machine\*)

\[INSFUN5\] Cannot modify reactive instance slots while pattern‑matching is in process.

CLIPS does not allow reactive instance slots to be changed while pattern‑matching is taking place. Functions used on the LHS of a rule should not have side effects (such as the changing slot values).

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(slot id))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\>

(defrule error

(start)

(test (send \[m\] put-id 34))

=\>)

CLIPS\> (assert (start))

\[INSFUN6\] Unable to pattern‑match on shared slot \<name\> in class \<name\>.

This error occurs when the number of simultaneous class hierarchy traversals is exceeded while pattern‑matching on a shared slot. See the related error message \[CLASSFUN2\] for more details.

\[INSFUN7\] The value\<multifield‑value\> is illegal for single‑field slot \<name\> of instance \<name\> found in \<function‑call or message‑handler\>.

Single‑field slots in an instance can hold only one atomic value.

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(slot id))

CLIPS\>

(deffunction assign-id (?ins ?id)

(send ?ins put-id ?id))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (assign-id \[m\] (create\$ 1 2 3 4))

\[INSFUN8\] Void function illegal value for slot \<name\> of instance \<name\> found in \<function‑call or message‑handler\>.

Only functions which have a return value can be used to generate values for an instance slot.

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(slot id))

CLIPS\>

(defmessage-handler MACHINE error ()

(bind ?self:id (agenda)))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (send \[m\] error)

\[INSMNGR1\] Expected a valid name for new instance.

**make‑instance** expects a symbol or an instance‑name for the name of a new instance.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance 34 of MACHINE)

\[INSMNGR2\] Expected a valid class name for new instance.

**make‑instance** expects a symbol for the class of a new instance.

Example:

CLIPS\> (make-instance m of 34)

\[INSMNGR3\] Cannot create instances of abstract class \<name\>.

Direct instances of abstract classes, such as the predefined system classes, are illegal.

Example:

CLIPS\> (make-instance \[m\] of USER)

\[INSMGNR4\] The instance \<name\> has a slot‑value which depends on the instance definition.

The initialization of an instance is recursive in that a slot‑override or default‑value tries to create or reinitialize the same instance.

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(slot id))

CLIPS\> (make-instance m of MACHINE (id (make-instance m of MACHINE)))

\[INSMNGR5\] Unable to delete old instance \<name\>.

**make‑instance** will attempt to delete an old instance of the same name if it exists. This error occurs if that deletion fails.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\>

(defmessage-handler MACHINE delete around ()

(if (neq (instance-name ?self) \[m\]) then

(call-next-handler)))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (make-instance m of MACHINE)

\[INSMNGR6\] Cannot delete instance \<name\> during initialization.

The evaluation of a slot‑override in **make‑instance** or **initialize‑instance** attempted to delete the instance.

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(slot id))

CLIPS\>

(defmessage-handler MACHINE put-id after (\$?any)

(delete-instance))

CLIPS\> (make-instance m of MACHINE (id 3))

\[INSMNGR7\] Instance \<name\> is already being initialized.

An instance cannot be reinitialized during initialization.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\>

(defmessage-handler MACHINE init after ()

(initialize-instance ?self))

CLIPS\> (initialize-instance m)

\[INSMNGR8\] An error occurred during the initialization of instance \<name\>.

This message is displayed when an evaluation error occurs while the **init** message is executing for an instance.

\[INSMNGR9\] Expected a valid slot name for slot‑override.

**make‑instance** and **initialize‑instance** expect symbols for slot names.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance m of MACHINE (34 3))

\[INSMNGR10\] Cannot create instances of reactive classes while pattern‑matching is in process.

CLIPS does not allow instances of reactive classes to be created while pattern‑matching is taking place. Functions used on the LHS of a rule should not have side effects (such as the creation of a new instance or fact).

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\>

(defrule error

(start)

(test (make-instance of MACHINE))

=\>)

CLIPS\> (assert (start))

\[INSMNGR11\] Invalid module specifier in new instance name.

This error occurs when the module specifier in the instance‑name is illegal (such as an undefined module name).

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance INVALID::m of MACHINE)

\[INSMNGR12\] Cannot delete instances of reactive classes while pattern‑matching is in process.

CLIPS does not allow instances of reactive classes to be deleted while pattern‑matching is taking place. Functions used on the LHS of a rule should not have side effects (such as the deletion of a new instance or the retraction of a fact).

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\>

(defrule error

(start)

(test (send \[m\] delete))

=\>)

CLIPS\> (assert (start))

\[INSMNGR13\] Slot \<slot‑name\> does not exist in instance \<instance‑name\>.

This error occurs when the slot name of a slot override does not correspond to any of the valid slot names for an instance.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance of MACHINE (id 33))

\[INSMNGR14\] Override required for slot \<slot‑name\> in instance \<instance‑name\>.

If the ?NONE keyword was specified with the default attribute for a slot, then a slot override must be provided when an instance containing that slot is created.

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(slot id (default ?NONE)))

CLIPS\> (make-instance of MACHINE)

\[INSMNGR15\] init‑slots not valid in this context.

The special function **init‑slots** (for initializing slots of an instance to the class default values) can only be called during the dispatch of an **init** message for an instance, i.e., in an **init** message‑handler.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\>

(defmessage-handler MACHINE error ()

(init-slots))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (send \[m\] error)

\[INSMNGR16\] The instance name \<instance-name\> is in use by an instance of class \<class-name\>.

An instance of one class cannot be created using an instance name belonging to a different class.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (defclass PRODUCT (is-a USER))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (make-instance m of PRODUCT)

\[INSMODDP1\] Direct/message‑modify message valid only in modify‑instance.

The **direct‑modify** and **message‑modify** message‑handlers attached to the class **USER** can only be called as a result of the appropriate message being sent.by the **modify‑instance** or **message‑modify‑instance** functions. Additional handlers may be defined, but the message can only be sent in this context.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (send \[m\] direct-modify 0)

\[INSMODDP2\] Direct/message‑duplicate message valid only in duplicate‑instance.

The **direct‑duplicate** and **message‑duplicate** message‑handlers attached to the class **USER** can only be called as a result of the appropriate message being sent.by the **duplicate‑instance** or **message‑duplicate‑instance** functions. Additional handlers may be defined, but the message can only be sent in this context.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (send \[m\] direct-duplicate 0 0)

\[INSMODDP3\] Instance copy must have a different name in duplicate‑instance.

If an instance‑name is specified for the new instance in the call to **duplicate‑instance**, it must be different from the source instance's name.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (duplicate-instance m to m)

\[INSMULT1\] Function \<name\> cannot be used on single‑field slot \<name\> in instance \<name\>.

Some functions, such as **slot‑insert\$**, can only operate on multifield slots.

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(slot id))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (slot-insert\$ m id 273 383 377)

\[INSQYPSR1\] Duplicate instance‑set member variable name in function \<name\>.

Instance‑set member variables in an instance‑set query function must be unique.

Example:

CLIPS\> (any-instancep ((?a OBJECT) (?a OBJECT)) TRUE)

\[INSQYPSR2\] Binds are not allowed in instance‑set query in function \<name\>.

An instance‑set query cannot bind variables.

Example:

CLIPS\>

(any-instancep ((?a OBJECT) (?b OBJECT))

(bind ?c 1))

\[INSQYPSR3\] Cannot rebind instance‑set member variable \<name\> in function \<name\>.

Instance‑set member variables cannot be changed within the actions of an instance‑set query function.

Example:

CLIPS\>

(do-for-all-instances ((?a USER))

(if (slot-existp ?a age) then

(\> ?a:age 30))

(bind ?a (send ?a get-brother)))

\[IOFUN1\] Illegal logical name used for \<function name\> function.

A logical name must be either a symbol, string, instance‑name, float, or integer.

Example:

(printout invalid \"Hello World!\" crlf)

\[IOFUN2\] Logical name \<logical name\> already in use.

A logical name cannot be associated with two different files.

Example:

CLIPS\> (open \"out.txt\" output \"w\")

TRUE

CLIPS\> (open \"out2.txt\" output \"w\")

\[MEMORY1\] Out of memory

This error indicates insufficient memory exists to expand internal struc­tures enough to allow continued operation (causing an exit to the operating system).

\[MISCFUN1\] The function \'expand\$\' must be used in the argument list of a function call.

or

\[MISCFUN1\] Sequence expansion must be used in the argument list of a function call.

Sequence expansion and the expand\$ function may not be used unless it is within the argument list of another function.

Example:

CLIPS\> (expand\$ (create\$ red green blue))

\[MODULDEF1\] Illegal use of the module specifier.

The module specifier can only be used as part of a defined construct's name or as an argument to a function.

Example:

CLIPS\> (deftemplate person (slot name) (slot age))

CLIPS\> (defrule match (MAIN::person) =\>)

\[MODULPSR1\] Module \<module name\> does not export any constructs.

or

\[MODULPSR1\] Module \<module name\> does not export any \<construct type\> constructs.

or

\[MODULPSR1\] Module \<module name\> does not export the \<construct type\> \<construct name\>.

A construct cannot be imported from a module unless the defmodule exports that construct.

Example:

CLIPS\> (clear)

CLIPS\> (defmodule START)

CLIPS\> (deftemplate START::data)

CLIPS\> (defmodule FINISH (import START deftemplate data))

\[MSGCOM1\] Incomplete message‑handler specification for deletion.

It is illegal to specify a non‑wildcard handler index when a wildcard is given for the class in the external C function **UndefmessageHandler()**. This error can only be generated when a user‑defined external function linked with CLIPS calls this command incorrectly.

\[MSGCOM2\] Unable to find message‑handler \<name\> \<type\> for class \<name\> in function \<name\>.

This error occurs when the named function cannot find the specified message‑handler.

Example:

CLIPS\> (ppdefmessage-handler USER print around)

\[MSGCOM3\] Unable to delete message‑handlers.

This error occurs when a message‑handler can't be deleted (such as when a binary image is loaded).

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (defmessage-handler MACHINE start ())

CLIPS\> (bsave \"program.bin\")

TRUE

CLIPS\> (bload \"program.bin\")

TRUE

CLIPS\> (undefmessage-handler MACHINE start)

\[MSGFUN1\] No applicable primary message‑handlers found for \<message\>.

No primary message‑handler attached to the object's classes matched the name of the message.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (send \[m\] invalid-message)

\[MSGFUN2\] Message‑handler \<name\> \<type\> in class \<name\> expected exactly/at least \<number\> argument(s).

The number of message arguments was inappropriate for one of the applicable message‑handlers.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (defmessage-handler MACHINE start (?start ?duration))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (send \[m\] start)

\[MSGFUN3\] Write access denied for slot \<name\> in instance \<name\>.

This error occurs when an attempt is made to change the value of a read‑only slot.

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(slot id (access initialize-only)))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (send \[m\] put-id)

\[MSGFUN4\] The function \<function\> may only be called from within message‑handlers.

The named function operates on the active instance of a message and thus can only be called by message‑handlers.

Example:

CLIPS\> (ppinstance)

\[MSGFUN5\] The function \<function\> operates only on instances.

The named function operates on the active instance of a message and can only handle instances of user‑defined classes (not primitive type objects).

Example:

CLIPS\>

(defmessage-handler INTEGER print ()

(ppinstance))

CLIPS\> (send 34 print)

\[MSGFUN6\] Private slot \<slot‑name\> of class \<class‑name\> cannot be accessed directly by handlers attached to class \<class‑name\>

A subclass which inherits private slots from a superclass may not access those slots using the ?self variable. This error can also occur when a superclass tries to access via **dynamic‑put** or **dynamic‑get** a private slot in a subclass.

Example:

CLIPS\> (defclass DEVICE (is-a USER) (slot id))

CLIPS\> (defclass MACHINE (is-a DEVICE))

CLIPS\> (defmessage-handler MACHINE mid () ?self:id)

\[MSGFUN7\] Unrecognized message‑handler type in defmessage‑handler in function \<function\>.

Allowed message‑handler types include primary, before, after, and around.

Example:

CLIPS\> (defmessage-handler USER print behind ())

\[MSGFUN8\] Unable to delete message‑handler(s) from class \<name\>.

This error occurs when an attempt is made to delete a message‑handler attached to a class for which any of the message‑handlers are executing.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\>

(defmessage-handler MACHINE error ()

(undefmessage-handler MACHINE error primary))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (send \[m\] error)

\[MSGPASS1\] Shadowed message‑handlers not applicable in current context.

No shadowed message‑handler is available when the function **call‑next‑handler** or **override‑next‑handler** is called.

Example:

CLIPS\> (call-next-handler)

\[MSGPASS2\] No such instance \<name\> in function \<name\>.

This error occurs when the named function cannot find the specified instance.

Example:

CLIPS\> (instance-address \[invalid-instance\])

\[MSGPASS3\] Static reference to slot \<name\> of class \<name\> does not apply to \<instance‑name\> of \<class‑name\>.

This error occurs when a static reference to a slot in a superclass by a message‑handler attached to that superclass is incorrectly applied to an instance of a subclass which redefines that slot. Static slot references always refer to the slot defined in the class to which the message‑handler is attached.

Example:

CLIPS\>

(defclass DEVICE (is-a USER)

(slot id))

CLIPS\>

(defclass MACHINE (is-a DEVICE)

(slot id))

CLIPS\>

(defmessage-handler DEVICE access-id ()

?self:id)

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\> (send \[m\] access-id)

\[MSGPSR1\] A class must be defined before its message‑handlers.

A message‑handler can only be attached to an existing class.

Example:

CLIPS\> (defmessage-handler UNDEFINED-CLASS process ())

\[MSGPSR2\] Cannot (re)define message‑handlers during execution of other message‑handlers for the same class.

No message‑handlers for a class can be loaded while any current message‑handlers attached to the class are executing.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (make-instance m of MACHINE)

\[m\]

CLIPS\>

(defmessage-handler MACHINE build-new ()

(build \"(defmessage-handler MACHINE new ())\"))

CLIPS\> (send \[m\] build-new)

\[MSGPSR3\] System message‑handlers may not be modified.

There are four primary message‑handlers attached to the class USER which cannot be modified: init, delete, create and print.

Example:

CLIPS\> (defmessage-handler USER init ())

\[MSGPSR4\] Illegal slot reference in parameter list.

Direct slot references are allowed only within message‑handler bodies.

Example:

CLIPS\> (defmessage-handler USER process (?self:id))

\[MSGPSR5\] Active instance parameter cannot be changed.

?self is a reserved parameter for the active instance.

Example:

CLIPS\>

(defmessage-handler USER process ()

(bind ?self 1))

\[MSGPSR6\] No such slot \<name\> in class \<name\> for ?self reference.

The symbol following the ?self: reference must be a valid slot for the class.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (defmessage-handler MACHINE id () ?self:id)

\[MSGPSR7\] Illegal value for ?self reference.

The symbol following the ?self: reference must be a symbol.

Example:

CLIPS\> (defclass MACHINE (is-a USER))

CLIPS\> (defmessage-handler MACHINE id () ?self:7)

\[MSGPSR8\] Message‑handlers cannot be attached to the class \<name\>.

Message‑handlers cannot be attached to the INSTANCE, INSTANCE‑ADDRESS, or INSTANCE‑NAME classes.

Example:

CLIPS\> (defmessage-handler INSTANCE process ())

\[MULTIFUN1\] Multifield index \<index\> out of range 1..\<end range\> in function \<name\>

or

\[MULTIFUN1\] Multifield index range \<start\>\...\<end\> out of range 1..\<end range\> in function \<name\>

This error occurs when a multifield manipulation function is passed a single index or range of indices that does not fall within the specified range of allowed indices.

Example:

CLIPS\> (delete\$ (create\$ red green blue) 4 4)

\[MULTIFUN2\] Cannot rebind field variable in function \<function\>.

The field variable (if specified) cannot be rebound within the body of the progn\$ or foreach function.

Example:

CLIPS\> (progn\$ (?field (create\$ a)) (bind ?field 3))

\[OBJRTBLD1\] No objects of existing classes can satisfy pattern.

No objects of existing classes could possibly satisfy the pattern. This error usually occurs when a restriction placed on the is‑a attribute is incompatible with slot restrictions before it in the pattern.

Example:

CLIPS\> (defclass MACHINE (is-a USER) (slot id))

CLIPS\> (defrule error (object (id ?) (is-a \~MACHINE)) =\>)

\[OBJRTBLD2\] No objects of existing classes can satisfy \<attribute‑name\> restriction in object pattern.

The restrictions on \<attribute\> are such that no objects of existing classes (which also satisfy preceding restrictions) could possibly satisfy the pattern.

Example:

CLIPS\> (defrule error (object (invalid-slot ?)) =\>)

\[OBJRTBLD3\] No objects of existing classes can satisfy pattern #\<pattern‑num\>.

No objects of existing classes could possibly satisfy the pattern. This error occurs when the constraints for a slot as given in the defclass(es) are incompatible with the constraints imposed by the pattern.

Example:

CLIPS\>

(defclass MACHINE (is-a USER)

(slot id (type INTEGER)))

CLIPS\>

(defclass PRODUCT (is-a USER)

(slot id (type STRING))

(slot manufacturer))

CLIPS\>

(defrule error

(object (id 100) (manufacturer ?))

=\>)

\[OBJRTBLD4\] Multiple restrictions on attribute \<attribute‑name\> not allowed.

Only one restriction per attribute is allowed per object pattern.

Example:

CLIPS\> (defrule error (object (is-a ?) (is-a ?)) =\>)

\[OBJRTBLD5\] Undefined class \<class-name\> in object pattern.

Object patterns are applicable only to classes of objects which are already defined.

Example:

CLIPS\> (defrule error (object (is-a UNDEFINED-CLASS)) =\>)

\[OBJRTMCH1\] This error occurred in the object pattern network

Currently active instance: \<instance‑name\>

Problem resides in slot \<slot name\> field #\<field‑index\>

Of pattern #\<pattern‑number\> in rule(s):

\<problem‑rules\>+

This error pinpoints other evaluation errors associated with evaluating an expression within the object pattern network. The specific pattern and field of the problem rules are identified.

\[PATTERN1\] The symbol \<symbol name\> has special meaning and may not be used as a \<use name\>.

Certain keywords have special meaning to CLIPS and may not be used in situations that would cause an ambiguity.

Example:

CLIPS\> (deftemplate exists (slot id))

\[PATTERN2\] Single and multifield constraints cannot be mixed in a field constraint

Single and multifield variable constraints cannot be mixed in a field constraint (this restriction does not include variables passed to functions with the predicate or return value constraints).

Example:

CLIPS\> (defrule error (pattern ?x \$?y ?x&\~\$?y) =\>)

\[PRCCODE1\] Attempted to call a \<construct\> which does not exist.

In a CLIPS configuration without deffunctions and/or generic functions, an attempt was made to call a deffunction or generic function from a binary image generated by the **bsave** command.

\[PRCCODE2\] Functions without a return value are illegal as \<construct\> arguments.

An evaluation error occurred while examining the arguments for a deffunction, generic function or message.

Example:

CLIPS\> (defmethod process (?a))

CLIPS\> (process (instances))

\[PRCCODE3\] Undefined variable \<name\> referenced in \<where\>.

Local variables in the actions of a deffunction, method, message‑handler, or defrule must reference parameters, variables bound within the actions with the **bind** function, or variables bound on the LHS of a rule.

Example:

CLIPS\> (defrule error =\> (+ ?a 3))

\[PRCCODE4\] Execution halted during the actions of \<construct\> \<name\>.

This error occurs when the actions of a rule, deffunction, generic function method or message‑handler are prematurely aborted due to an error.

\[PRCCODE5\] Variable \<name\> unbound \[in \<construct\> \<name\>\].

This error occurs when local variables in the actions of a deffunction, method, message‑handler, or defrule becomes unbound during execution as a result of calling the **bind** function with no arguments.

Example:

CLIPS\> (deffunction process () (bind ?a) ?a)

CLIPS\> (process)

\[PRCCODE6\] This error occurred while evaluating arguments for the \<construct\> \<name\>.

An evaluation error occurred while examining the arguments for a deffunction, generic function method or message‑handler.

Example:

CLIPS\> (deffunction process (?a))

CLIPS\> (process (+ (eval \"(gensym)\") 2))

\[PRCCODE7\] Duplicate parameter names not allowed.

Deffunction, method or message‑handler parameter names must be unique.

Example:

CLIPS\> (defmethod process ((?x INTEGER) (?x FLOAT)))

\[PRCCODE8\] No parameters allowed after wildcard parameter.

A wildcard parameter for a deffunction, method or message‑handler must be the last parameter.

Example:

CLIPS\> (defmethod process ((\$?x INTEGER) (?y SYMBOL)))

\[PRCDRPSR1\] Cannot rebind count variable in function loop‑for‑count.

The special variable ?count cannot be rebound within the body of the loop‑for‑count function.

Example:

CLIPS\> (loop-for-count (?count 10) (bind ?count 3))

\[PRCDRPSR2\] The return function is not valid in this context.

or

\[PRCDRPSR2\] The break function is not valid in this context.

The return and break functions can only be used within certain contexts (e.g. the break function can only be used within a while loop and certain instance set query functions).

Example:

CLIPS\> (return 3)

\[PRCDRPSR3\] Duplicate case found in switch function.

A case may be specified only once in a switch statement.

Example:

CLIPS\> (switch a (case a then 8) (case a then 9))

\[PRNTUTIL1\] Unable to find \<item\> \<item‑name\>

This error occurs when CLIPS cannot find the named item (check for typos).

\[PRNTUTIL2\] Syntax Error: Check appropriate syntax for \<item\>

This error occurs when the appropriate syntax is not used.

Example:

CLIPS\> (if (\> 3 4))

\[PRNTUTIL3\]

\*\*\* CLIPS SYSTEM ERROR \*\*\*

ID = \<error‑id\>

CLIPS data structures are in an inconsistent or corrupted state.

This error may have occurred from errors in user defined code.

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

This error indicates an internal problem within CLIPS (which may have been caused by user defined functions or other user code). If the problem cannot be located within user defined code, then the \<error‑id\> should be reported.

\[PRNTUTIL4\] Unable to delete \<item\> \<item‑name\>

This error occurs when CLIPS cannot delete the named item (e.g. a construct might be in use). One example which will cause this error is an attempt to delete a deffunction or generic function which is used in another construct (such as the RHS of a defrule or a default‑dynamic facet of a defclass slot).

\[PRNTUTIL5\] The \<item\> has already been parsed.

This error occurs when CLIPS has already parsed an attribute or declaration.

\[PRNTUTIL6\] Local variables cannot be accessed by \<function or construct\>.

This error occurs when a local variable is used by a function or construct that cannot use global variables.

Example:

CLIPS\> (deffacts info (id ?x))

\[PRNTUTIL7\] Attempt to divide by zero in \<function‑name\> function.

This error occurs when a function attempts to divide by zero.

Example:

CLIPS\> (/ 3 0)

\[PRNTUTIL8\] This error occurred while evaluating the salience \[for rule \<name\>\]

When an error results from evaluating a salience value for a rule, this error message is given.

\[PRNTUTIL9\] Salience value out of range \<min\> to \<max\>

The range of allowed salience has an explicit limit; this error message will result if the value is out of that range.

Example:

CLIPS\> (defrule error (declare (salience 20000)) =\>)

\[PRNUTIL10\] Salience value must be an integer value.

Salience requires a integer argument and will otherwise result in this error message.

Example:

CLIPS\> (defrule error (declare (salience a)) =\>)

\[PRNUTIL11\] The fact \<fact-id\> has been retracted.

This error occurs when a function expecting a fact address argument is provided a retracted fact.

Example:

CLIPS\> (bind ?f (assert (a b c)))

\<Fact-1\>

CLIPS\> (retract ?f)

CLIPS\> (fact-index ?f)

\[PRNUTIL12\] The variable/slot reference ?\<variable\>:\<slot\> cannot be resolved because the referenced fact \<fact-id\> has been retracted.

This error occurs when using shorthand slot notation with a retracted fact.

Example:

CLIPS\> (deftemplate point (slot x) (slot y))

CLIPS\> (assert (point (x 1) (y 2)))

\<Fact-1\>

CLIPS\> (do-for-fact ((?p point)) TRUE (retract ?p) (+ ?p:x ?p:y))

\[PRNUTIL13\] The variable/slot reference ?\<variable\>:\<slot\> is invalid because the referenced fact \<fact-id\> does not contain the specified slot.

This error occurs when using shorthand slot notation for a fact that does not contain the specified slot.

Example:

CLIPS\> (deftemplate point (slot x) (slot y))

CLIPS\> (assert (point (x 1) (y 2)))

\<Fact-1\>

CLIPS\> (do-for-fact ((?p point)) TRUE (+ ?p:x ?p:z))

\[PRNUTIL14\] The variable/slot reference ?\<variable\>:\<slot\> is invalid because slot names must be symbols.

This error occurs when using shorthand slot notation with a non-symbolic slot name.

Example:

CLIPS\> (deftemplate point (slot x) (slot y))

CLIPS\> (do-for-fact ((?p point)) TRUE (+ ?p:x ?p:37))

\[PRNUTIL15\] The variable/slot reference ?\<variable\>:\<slot\> cannot be resolved because the referenced instance \<instance-name\> has been deleted.

This error occurs when using shorthand slot notation with a deleted instance.

Example:

CLIPS\> (defclass POINT (is-a USER) (slot x) (slot y))

CLIPS\> (make-instance p1 of POINT (x 1) (y 2))

\[p1\]

CLIPS\> (do-for-all-instances ((?p POINT)) TRUE (send ?p delete) (+ ?p:x ?p:y))

\[PRNUTIL16\] The variable/slot reference ?\<variable\>:\<slot\> is invalid because the referenced instance \<instance-name\> does not contain the specified slot.

This error occurs when using shorthand slot notation for an instance that does not contain the specified slot.

Example:

CLIPS\> (defclass POINT (is-a USER) (slot x) (slot y))

CLIPS\> (make-instance p1 of POINT (x 1) (y 2))

\[p1\]

CLIPS\> (do-for-all-instances ((?p POINT)) TRUE (+ ?p:x ?p:z))

\[ROUTER1\] Logical name \<logical_name\> was not recognized by any routers

This error results because \"Hello\" is not recognized as a valid router name.

Example:

CLIPS\> (printout \"Hello\" crlf)

\[RULECSTR1\] Variable \<variable name\> in CE #\<integer\> slot \<slot name\> has constraint conflicts which make the pattern unmatchable.

or

\[RULECSTR1\] Variable \<variable name\> in CE #\<integer\> field #\<integer\> has constraint conflicts which make the pattern unmatchable.

or

\[RULECSTR1\] CE #\<integer\> slot \<slot name\> has constraint conflicts which make the pattern unmatchable.

or

\[RULECSTR1\] CE #\<integer\> field #\<integer\> has constraint conflicts which make the pattern unmatchable.

This error occurs when slot value constraints (such as allowed types) prevents any value from matching the slot constraint for a pattern.

Example:

CLIPS\> (deftemplate machine (slot id (type SYMBOL)))

CLIPS\> (deftemplate product (slot id (type INTEGER)))

CLIPS\>

(defrule error

(machine (id ?id))

(product (id ?id))

=\>)

\[RULECSTR2\] Previous variable bindings of \<variable name\> caused the type restrictions

for argument #\<integer\> of the expression \<expression\>

found in CE#\<integer\> slot \<slot name\> to be violated.

This error occurs when previous variable bindings and constraints prevent a variable from containing a value which satisfies the type constraints for one of a function's parameters.

Example:

CLIPS\> (deftemplate machine (slot id (type SYMBOL)))

CLIPS\>

(defrule error

(machine (id ?id&:(\> ?id 3)))

=\>)

\[RULECSTR3\] Previous variable bindings of \<variable name\> caused the type restrictions

for argument #\<integer\> of the expression \<expression\>

found in the rule\'s RHS to be violated.

This error occurs when previous variable bindings and constraints prevent a variable from containing a value which satisfies the type constraints for one of a function's parameters.

Example:

CLIPS\> (deftemplate machine (slot id (type SYMBOL)))

CLIPS\>

(defrule error

(machine (id ?id))

=\>

(println (+ ?id 1)))

\[RULELHS1\] The logical CE cannot be used with a not/exists/forall CE.

Logical CEs can be placed outside, but not inside, a not/exists/forall CE.

Example:

CLIPS\> (defrule error (not (logical (machine))) =\>)

\[RULELHS2\] A pattern CE cannot be bound to a pattern‑address within a not CE

This is an illegal operation and results in an error message.

Example:

CLIPS\> (defrule error (not ?m \<- (machine)) =\>)

\[RULEPSR1\] Logical CEs must be placed first in a rule

If logical CEs are used, then the first CE must be a logical CE.

Example:

CLIPS\> (defrule error (machine) (logical (product)) =\>)

\[RULEPSR2\] Gaps may not exist between logical CEs

Logical CEs found within a rule must be contiguous.

Example:

CLIPS\> (defrule error (logical (machine)) (product) (logical (order)) =\>)

\[STRNGFUN1\] Function build does not work in run time modules.

The build function does not work in run time modules because the code required for parsing is not available.

\[STRNGFUN2\] Function \'\<function\>\' encountered extraneous input.

The \'eval\' and \'build\' cannot contain additional input after the first command or construct that is parsed.

Example:

CLIPS\> (eval \"(+ 2 3) (\* 4 5)\")

\[SYSDEP1\] No file found for \<option\> option.

This message occurs if the --f, -f2, or -l option is used when executing CLIPS, but no arguments are provided.

Example:

clips --f

\[SYSDEP2\] Invalid option \<option\>.

This message occurs if an invalid option is used.

Example:

clips --f3

\[TEXTPRO1\] Could not open file \<file-name\>.

This error occurs when the external text‑processing system command **fetch** encounters an error when loading a file.

Example:

CLIPS\> (fetch \"invalid.txt\")

\[TEXTPRO2\] File \<file-name\> already loaded.

This error occurs when the external text‑processing system command **fetch** encounters an error when loading a file.

Example:

CLIPS\> (fetch \"file.txt\")

CLIPS\> (fetch \"file.txt\")

\[TEXTPRO3\] No entries found.

or

\[TEXTPRO4\] Line \<number\> : Previous entry not closed.

or

\[TEXTPRO5\] Line \<number\> : Invalid delimeter string.

or

\[TEXTPRO6\] Line \<number\> : Invalid entry type.

or

\[TEXTPRO7\] Line \<number\> : Non-menu entries cannot have subtopics.

or

\[TEXTPRO8\] Line \<number\> : Unmatched end marker.

These errors occurs when a file is fetched with invalid entries.

\[TMPLTDEF1\] Invalid slot \<slot name\> not defined in corresponding deftemplate \<deftemplate name\>

The slot name supplied does not correspond to a slot name defined in the corre­sponding deftemplate

Example:

CLIPS\> (deftemplate machine (slot id))

CLIPS\> (defrule error (machine (manufacturer Acme)) =\>)

\[TMPLTDEF2\] The single field slot \<slot name\> can only contain a single field value.

If a slot definition is specified in a template pattern or fact, the contents of the slot must be capable of matching against or evaluating to a single value.

Example:

CLIPS\> (deftemplate machine (slot id))

CLIPS\> (assert (machine (id)))

\[TMPLTFUN1\] Attempted to assert a multifield value into the single field slot \<slot name\> of deftemplate \<deftemplate name\>.

A multifield value cannot be stored in a single field slot.

Example:

CLIPS\> (deftemplate machine (slot id))

CLIPS\>

(defrule error

=\>

(bind ?id (create\$ 34 890))

(assert (machine (id ?id))))

CLIPS\> (run)

\[TMPLTRHS1\] Slot \<slot name\> requires a value because of its (default ?NONE) attribute.

The (default ?NONE) attribute requires that a slot value be supplied whenever a new fact is created.

Example:

CLIPS\> (deftemplate machine (slot id (default ?NONE)))

CLIPS\> (assert (machine))
