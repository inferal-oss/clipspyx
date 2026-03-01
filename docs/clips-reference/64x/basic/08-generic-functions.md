# Section 8: Generic Functions

With the **defgeneric** and **defmethod** constructs, new generic functions may be written directly in CLIPS. Generic functions are similar to deffunctions because they can be used to define new procedural code directly in CLIPS, and they can be called like any other function. However, generic functions are much more powerful because they can do different things depending on the types (or classes) and number of their arguments. For example, a "+" operator could be defined which performs concatenation for strings but still performs arithmetic addition for numbers. Generic functions are comprised of multiple components called **methods**, where each method handles different cases of arguments for the generic function. A generic function which has more than one method is said to be **overloaded**.

Generic functions can have system functions and user‑defined external functions as *implicit* methods. For example, an overloading of the "+" operator to handle strings consists of two methods: 1) an implicit one which is the system function handling numerical addition, and 2) an explicit (user‑defined) one handling string concatenation. Deffunctions, however, may not be methods of generic functions because they are subsumed by generic functions anyway. Deffunctions are only provided so that basic new functions can be added directly in CLIPS without the concerns of overloading. For example, a generic function that has only one method that restricts only the number of arguments is equivalent to a deffunction.

In most cases, generic function methods are not called directly (the **call‑specific‑method** function can be used to do so, however). CLIPS recognizes that a function call is generic and uses the generic function's arguments to find and execute the appropriate method. This process is termed the **generic dispatch**.

## 8.1 Note on the Use of the Term *Method*

Most OOP systems support procedural behavior of objects either through message‑passing (e.g. Smalltalk) or by generic functions (e.g. CLOS). CLIPS supports both of these mechanisms, although generic functions are not strictly part of COOL. A generic function may examine the classes of its arguments but must still use messages within the bodies of its methods to manipulate any arguments that are instances of user‑defined classes. The fact that CLIPS supports both mechanisms leads to confusion in terminology. In OOP systems that support message‑passing only, the term **method** is used to denote the different implementations of a **message** for different classes. In systems that support generic functions only, however, the term **method** is used to denote the different implementations of a generic function for different sets of argument restrictions. To avoid this confusion, the term **message‑handler** is used to take the place of **method** in the context of messages. Thus in CLIPS, **message‑handlers** denote the different implementations of a **message** for different classes, and **methods** denote the different implementations of a **generic function** for different sets of argument restrictions.

## 8.2 Performance Penalty of Generic Functions

A call to a generic function is computationally more expensive than a call to a system function, user‑defined external function, or deffunction. This is because CLIPS must first examine the function arguments to determine which method is applicable. A performance penalty of 15%‑20% is not unexpected. In practice, generic functions should always have at least two methods. Deffunctions or user‑defined external functions should be used when overloading is not required. A system or user‑defined external function that is not overloaded will, of course, execute as quickly as ever, since the generic dispatch is unnecessary.

## 8.3 Order Dependence of Generic Function Definitions

If a construct which uses a system or user‑defined external function is loaded before a generic function that uses that function as an implicit method, all calls to that function from that construct will bypass the generic dispatch. For example, if a generic function which overloads the "+" operator is defined after a rule which uses the "+" operator, that rule will always call the "+" system function directly. However, similar rules defined after the generic function will use the generic dispatch.

## 8.4 Defining a New Generic Function

A generic function is comprised of a header (similar to a forward declaration) and zero or more methods. A generic function header can either be explicitly declared by the user or implicitly declared by the definition of at least one method. A method is comprised of six elements: 1) a name (which identifies to which generic function the method belongs), 2) an optional index, 3) an optional comment, 4) a set of parameter **restrictions**, 5) an optional wildcard parameter restriction to handle a variable number of arguments and 6) a sequence of actions, or expressions, which will be executed in order when the method is called. The parameter restrictions are used by the generic dispatch to determine a method's applicability to a set of arguments when the generic function is actually called. The **defgeneric** construct is used to specify the generic function header, and the **defmethod** construct is used for each of the generic function's methods.

Syntax

(defgeneric \<name\> \[\<comment\>\])

(defmethod \<name\> \[\<index\>\] \[\<comment\>\]

(\<parameter-restriction\>\* \[\<wildcard-parameter-restriction\>\])

\<action\>\*)

\<parameter-restriction\> ::=

\<single-field-variable\> \|

(\<single-field-variable\> \<type\>\* \[\<query\>\])

\<wildcard-parameter-restriction\> ::=

\<multifield-variable\> \|

(\<multifield-variable\> \<type\>\* \[\<query\>\])

\<type\> ::= \<class-name\>

\<query\> ::= \<global-variable\> \|

\<function-call\>

A generic function must be declared, either by a header or a method, prior to being called from another generic function method, deffunction, object message‑handler, rule, or the REPL. The only exception is a self recursive generic function.

### 8.4.1 Generic Function Headers

A generic function is uniquely identified by name. In order to reference a generic function in other constructs before any of its methods are declared, an explicit header is necessary. Otherwise, the declaration of the first method implicitly creates a header. For example, two generic functions whose methods mutually call the other generic function (mutually recursive generic functions) would require explicit headers.

### 8.4.2 Method Indices

A method is uniquely identified by name and index, or by name and parameter restrictions. Each method for a generic function is assigned a unique integer index within the group of all methods for that generic function. Thus, if a new method is defined which has exactly the same name and parameter restrictions as another method, CLIPS will automatically replace the older method. However, any difference in parameter restrictions will cause the new method to be defined *in addition to* the older method. To replace an old method with one that has different parameter restrictions, the index of the old method can be explicitly specified in the new method definition. However, the parameter restrictions of the new method must not match that of another method with a different index. If an index is not specified, CLIPS assigns an index that has never been used by any method (past or current) of this generic function. The index assigned by CLIPS can be determined with the **list‑defmethods** command.

### 8.4.3 Method Parameter Restrictions

Each parameter for a method can be defined to have arbitrarily complex restrictions or none at all. A parameter restriction is applied to a generic function argument at run‑time to determine if a particular method will accept the argument. A parameter can have two types of restrictions: type and query. A type restriction constrains the classes of arguments that will be accepted for a parameter. A query restriction is a user‑defined boolean test which must be satisfied for an argument to be acceptable. The complexity of parameter restrictions directly affects the speed of the generic dispatch.

A parameter that has no restrictions means that the method will accept any argument in that position. However, each method of a generic function must have parameter restrictions that make it distinguishable from all of the other methods so that the generic dispatch can tell which one to call at run‑time. If there are no applicable methods for a particular generic function call, CLIPS will generate an error.

A type restriction allows the user to specify a list of types (or classes), one of which must match (or be a superclass of) the class of the generic function argument. If COOL is not installed in the current CLIPS configuration, the only types (or classes) available are: OBJECT, PRIMITIVE, LEXEME, SYMBOL, STRING, NUMBER, INTEGER, FLOAT, MULTIFIELD, FACT‑ADDRESS and EXTERNAL‑ADDRESS. With COOL, INSTANCE, INSTANCE‑ADDRESS, INSTANCE‑NAME, USER, and any user‑defined classes are also available. Generic functions that use only the first group of types in their methods will work the same whether COOL is installed or not. The classes in a type restriction must be defined already, since they are used to predetermine the precedence between a generic function's methods. Redundant classes are not allowed in restriction class lists. For example, the following method parameter's type restriction is redundant since INTEGER is a subclass of NUMBER.

Example

(defmethod process ((?a INTEGER NUMBER)))

If the type restriction (if any) is satisfied for an argument, then a query restriction (if any) will be applied. The query restriction must either be a global variable or a function call. CLIPS evaluates this expression, and if it evaluates to anything but the symbol FALSE, the restriction is considered satisfied. Since a query restriction is not always satisfied, queries should *not* have any side‑effects, for they will be evaluated for a method that may not end up being applicable to the generic function call. Since parameter restrictions are examined from left to right, queries that involve multiple parameters should be included with the rightmost parameter. This insures that all parameter type restrictions have already been satisfied. For example, the following method delays evaluation of the query restriction until the classes of both arguments have been verified.

Example

(defmethod process ((?a INTEGER) (?b INTEGER (\> ?a ?b))))

If the argument passes all these tests, it is deemed acceptable to a method. If *all* generic function arguments are accepted by a method's restrictions, the method itself is deemed **applicable** to the set of arguments. When more than one method is applicable to a set of arguments, the generic dispatch must determine an ordering among them and execute the first one in that ordering. Method precedence is used for this purpose.

Example

In the following example, the first call to the generic function "+" executes the system operator "+", an implicit method for numerical addition. The second call executes the explicit method for string concatenation, since there are two arguments and they are both strings. The third call generates an error because the explicit method for string concatenation only accepts two arguments and the implicit method for numerical addition does not accept strings at all.

CLIPS\> (clear)

CLIPS\>

(defmethod + ((?a STRING) (?b STRING))

(str-cat ?a ?b))

CLIPS\> (+ 1 2)

3

CLIPS\> (+ \"1\" \"2\")

\"12\"

CLIPS\> (+ \"1\" \"2\" \"3\")

\[GENRCEXE1\] No applicable methods for \'+\'.

FALSE

CLIPS\>

### 8.4.4 Method Wildcard Parameter

A method may accept *exactly* or *at least* a specified number of arguments, depending on whether a wildcard parameter is used or not. The regular parameters specify the minimum number of arguments that must be passed to the method. Each of these parameters may be referenced like a normal single‑field variable within the actions of the method. If a wildcard parameter is present, the method may be passed any number of arguments greater than or equal to the minimum. If no wildcard parameter is present, then the method must be passed exactly the number of arguments specified by the regular parameters. Method arguments that do not correspond to a regular parameter can be grouped into a multifield value that can be referenced by the wildcard parameter within the body of the method. The standard CLIPS multifield functions, such as length\$ and expand\$, can be applied to the wildcard parameter.

If multifield values are passed as extra arguments, they will all be merged into one multifield value referenced by the wildcard parameter. This is because CLIPS does not support nested multifield values.

Type and query restrictions can be applied to arguments grouped in the wildcard parameter similarly to regular parameters. Such restrictions apply to each individual field of the resulting multifield value (not the entire multifield). However, expressions involving the wildcard parameter variable may be used in the query. In addition, a special variable may be used in query restrictions on the wildcard parameter to refer to the individual arguments grouped into the wildcard: **?current‑argument**. This variable is only in scope within the query and has no meaning in the body of the method. For example, to create a version of the '+' operator which acts differently for sums of all even integers:

Example

CLIPS\>

(defmethod +

((\$?any INTEGER (evenp ?current-argument)))

(div (call-next-method) 2))

CLIPS\> (+ 1 2)

3

CLIPS\> (+ 4 6 4)

7

CLIPS\>

It is important to emphasize that query and type restrictions on the wildcard parameter are applied to every argument grouped in the wildcard. Thus in the following example, the **\>** and **length\$** functions are actually called three times, since there are three arguments:

Example

CLIPS\> (defmethod many ((\$?args (\> (length\$ ?args) 2))) yes)

CLIPS\> (many apple pear lemon)

yes

CLIPS\>

In addition, a query restriction will never be examined if there are no arguments in the wildcard parameter range. For example, the previous method *would* be applicable to a call to the generic function with no arguments because the query restriction is never evaluated:

Example

CLIPS\> (many)

yes

CLIPS\>

Typically query restrictions applied to the entire wildcard parameter are testing the cardinality (the number of arguments passed to the method). In cases like this where the type is irrelevant to the test, the query restriction can be attached to a regular parameter instead to improve performance. Thus the previous method could be improved as follows:

Example

CLIPS\> (clear)

CLIPS\> (defmethod many ((?arg (\> (length\$ ?args) 1)) \$?args) yes)

CLIPS\> (many apple pear lemon)

yes

CLIPS\> (many)

\[GENRCEXE1\] No applicable methods for \'many\'.

FALSE

CLIPS\>

This approach should not be used if the types of the arguments grouped by the wildcard must be verified prior to safely evaluating the query restriction.

## 8.5 Generic Dispatch

When a generic function is called, CLIPS selects the method for that generic function with highest precedence for which parameter restrictions are satisfied by the arguments. This method is executed, and its value is returned as the value of the generic function. This entire process is referred to as the **generic dispatch**. Shown following is a flow diagram summary:

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image3.emf){width="5.319444444444445in" height="5.541666666666667in"}

The solid arrows indicate automatic control transfer by the generic dispatch. The dashed arrows indicate control transfer that can only be accomplished by the use or lack of the use of call-next-method or override-next-method.

### 8.5.1 Applicability of Methods Summary

An explicit (user‑defined) method is applicable to a generic function call if the following three conditions are met: 1) its name matches that of the generic function, 2) it accepts at least as many arguments as were passed to the generic function, and 3) every argument of the generic function satisfies the corresponding parameter restriction (if any) of the method.

Method restrictions are examined from left to right. As soon as one restriction is not satisfied, the method is abandoned, and the rest of the restrictions (if any) are not examined.

When a standard CLIPS system function is overloaded, CLIPS forms an implicit method definition corresponding to that system function. This implicit method is derived from the argument restriction parameters for the **AddUDF** call defining that function to CLIPS (see the *Advanced Programming Guide*). This string can be accessed with the function **get‑function‑restrictions** function. The specification of this implicit method can be examined with the **list‑defmethods** or **get‑method‑restrictions** functions. The method that CLIPS will form for a system function can be derived by the user from the BNF given in this document. For example,

(+ \<number\> \<number\>+)

would yield the following method for the '+' function:

(defmethod + ((?first NUMBER) (?second NUMBER) (\$?rest NUMBER))

\...)

The method definition is used to determine the applicability and precedence of the system function to the generic function call.

The following system functions cannot be overloaded, and CLIPS will generate an error if an attempt is made to do so.

  --------------------------------------- --------------------------------
  **active‑duplicate‑instance**           **find‑all‑instances**

  **active‑initialize‑instance**          **find‑fact**‑

  **active‑make‑instance**                **find‑instance**

  **active‑message‑duplicate‑instance**   **foreach**

  **active‑message‑modify‑instance**      **if**

  **active‑modify‑instance**              **make‑instance**

  **any‑instancep**                       **initialize‑instance**

  **assert**                              **loop‑for‑count**

  **bind**                                **message‑duplicate‑instance**

  **break**                               **message‑modify‑instance**

  **call‑next‑handler**                   **modify**

  **call‑next‑method**                    **modify‑instance**

  **call‑specific‑method**                **next‑handlerp**

  **delayed‑do‑for‑all‑facts**            **next‑methodp**

  **delayed‑do‑for‑all‑instances**        **object‑pattern‑match‑delay**

  **do‑for‑all‑facts**‑                   **override‑next‑handler**

  **do‑for‑all‑instances**                **override‑next‑method**

  **do‑for‑fact**‑                        **progn**

  **do‑for‑instance**                     **progn\$**

  **duplicate**                           **return**

  **duplicate‑instance**                  **switch**

  **expand\$**                            **while**

  **find‑all‑facts**‑                     
  --------------------------------------- --------------------------------

### 8.5.2 Method Precedence

When two or more methods are applicable to a particular generic function call, CLIPS must pick the one with highest **precedence** for execution. Method precedence is determined when a method is defined; the **list‑defmethods** function can be used to examine the precedence of methods for a generic function.

The precedence between two methods is determined by comparing their parameter restrictions. In general, the method with the most specific parameter restrictions has the highest precedence. For example, a method that demands an integer for a particular argument will have higher precedence than a method which only demands a number. The exact rules of precedence between two methods are given in order below; the result of the first rule that establishes precedence is taken.

1\) The parameter restrictions of both methods are positionally compared from left to right. In other words, the first parameter restriction in the first method is matched against the first parameter restriction in the second method, and so on. The comparisons between these pairs of parameter restrictions from the two methods determine the overall precedence between the two methods. The result of the first pair of parameter restrictions that specifies precedence is taken. The following rules are applied in order to a parameter pair; the result of the first rule that establishes precedence is taken.

a)  A regular parameter has precedence over a wildcard parameter.

b)  The most specific type restriction on a particular parameter has priority. A class is more specific than any of its superclasses.

c\) A parameter with a query restriction has priority over one that does not.

2\) The method with the greater number of regular parameters has precedence.

3\) A method without a wildcard parameter has precedence over one that does

4\) A method defined before another one has priority.

If there are multiple classes on a single restriction, determining specificity is slightly more complicated. Since all precedence determination is done when the new method is defined, and the actual class of the generic function argument will not be known until run‑time, arbitrary (but deterministic) rules are needed for determining the precedence between two class lists. The two class lists are examined by pairs from left to right, e.g. the pair of first classes from both lists, the pair of second classes from both lists and so on. The first pair containing a class and its superclass specify precedence. The class list containing the subclass has priority. If no class pairs specify precedence, then the shorter class list has priority. Otherwise, the class lists do not specify precedence between the parameter restrictions.

Example 1

; The system operator \'+\' is an implicit method ; #1

; Its definition provided by the system is:

; (defmethod + ((?a NUMBER) (?b NUMBER) (\$?rest NUMBER)))

(defmethod + ((?a NUMBER) (?b INTEGER))) ; #2

(defmethod + ((?a INTEGER) (?b INTEGER))) ; #3

(defmethod + ((?a INTEGER) (?b NUMBER))) ; #4

(defmethod + ((?a NUMBER) (?b NUMBER) ; #5

(\$?rest PRIMITIVE)))

(defmethod + ((?a NUMBER) ; #6

(?b INTEGER (\> ?b 2))))

(defmethod + ((?a INTEGER (\> ?a 2)) ; #7

(?b INTEGER (\> ?b 3))))

(defmethod + ((?a INTEGER (\> ?a 2)) ; #8

(?b NUMBER)))

The precedence would be: #7, #8, #3, #4, #6, #2, #1, #5. The methods can be immediately partitioned into three groups of decreasing precedence according to their restrictions on the first parameter: A) methods which have a query restriction and a type restriction of INTEGER (#7, #8), B) methods which have a type restriction of INTEGER (#3, #4), and C) methods which have a type restriction of NUMBER (#1, #2, #5, #6). Group A has precedence over group B because parameters with query restrictions have priority over those that do not. Group B has precedence over group C because INTEGER is a subclass of NUMBER. Thus, the ordering so far is: (#7, #8), (#3, #4), (#1, #2, #5, #6). Ordering between the methods in a particular set of parentheses is not yet established.

The next step in determining precedence between these methods considers their restrictions on the second parameter. #7 has priority over #8 because INTEGER is a subclass of NUMBER. #3 has priority over #4 because INTEGER is a subclass of NUMBER. #6 and #2 have priority over #1 and #5 because INTEGER is a subclass of NUMBER. #6 has priority over #2 because it has a query restriction and #2 does not. Thus the ordering is now: #7, #8, #3, #4, #6, #2, (#1, #5).

The restriction on the wildcard argument yields that #1 (the system function implicit method) has priority over #5 since NUMBER is a subclass of PRIMITIVE. This gives the final ordering: #7, #8, #3, #4, #6, #2, #1, #5.

Example 2

(defmethod combine ((?a NUMBER STRING))) ; #1

(defmethod combine ((?a INTEGER LEXEME))) ; #2

The precedence would be #2, #1. Although STRING is a subclass of LEXEME, the ordering is still #2, #1 because INTEGER is a subclass of NUMBER, and NUMBER/INTEGER is the leftmost pair in the class lists.

Example 3

(defmethod combine ((?a MULTIFIELD STRING))) ; #1

(defmethod combine ((?a LEXEME))) ; #2

The precedence would be #2, #1 because the classes of the first pair in the type restriction (MULTIFIELD/LEXEME) are unrelated and #2 has fewer classes in its class list.

Example 4

(defmethod combine ((?a INTEGER LEXEME))) ; #1

(defmethod combine ((?a STRING NUMBER))) ; #2

Both pairs of classes (INTEGER/STRING and LEXEME/NUMBER) are unrelated, and the class lists are of equal length. Thus, the precedence is taken from the order of definition: #1, #2.

### 8.5.3 Shadowed Methods

If one method must be called by another method in order to be executed, the first function or method is said to be **shadowed** by the second method. Normally, only one method or system function will be applicable to a particular generic function call. If there is more than one applicable method, the generic dispatch will only execute the one with highest precedence. Letting the generic dispatch automatically handle the methods in this manner is called the **declarative** technique, for the declarations of the method restrictions dictate which method gets executed in specific circumstances. However, the **call‑next‑method** and **override‑next‑method** functions may also be used which allow a method to execute the method that it is shadowing. This is called the **imperative** technique, since the method execution itself plays a role in the generic dispatch. This is *not* recommended unless it is absolutely necessary. In most circumstances, only one piece of code should need to be executed for a particular set of arguments. Another imperative technique is to use the **call‑specific‑method** function to override method precedence.

### 8.5.4 Method Execution Errors

If an error occurs while any method for a generic function call is executing, any actions in the current method not yet executed will be aborted, any methods not yet called will be aborted, and the generic function will return the symbol FALSE. The lack of any applicable methods for a set of generic function arguments is considered a method execution error.

### 8.5.5 Generic Function Return Value

The return value of a generic function is the return value of the applicable method with the highest precedence. Each applicable method that is executed can choose to ignore or capture the return value of any method that it is shadowing.

The return value of a particular method is the last action evaluated by that method.

#
