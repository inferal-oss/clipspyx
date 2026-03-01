# Section 2: CLIPS Overview

This section gives a general overview of CLIPS and of the basic concepts used through­out this manual.

## 2.1 Interacting with CLIPS

CLIPS programs may be executed in three ways: interactively using a simple Read-Eval-Print Loop (REPL) interface; interactively using an Integrated Development Environment (IDE) interface; or as embedded application in which the user provides a main pro­gram and controls execution of the expert system through the CLIPS Application Programming Interface (API).

The CLIPS REPL interface is similar to a LISP or Python REPL and is portable to all environments. Stan­dard usage for the REPL is to create or edit a knowledge base using any standard text editor; save the knowledge base as one or more text files; then load, debug, and run the knowledge base using the CLIPS REPL.

Integrated Development Environments are also available for macOS, Windows, and Java. The IDEs provide an enhanced REPL that supports inline editing and a command history; dialog boxes for specifying files and directories; and debugging windows for displaying the current state of a CLIPS program. The IDEs are described in more detail in the *Interfaces Guide*.

Embedded applications are dis­cussed in the *Advanced Programming Guide*.

### 2.1.1 Read-Eval-Print Loop

The primary method for interacting with CLIPS in a non‑embedded environment is through the CLIPS Read-Eval-Print Loop (REPL). When the "CLIPS\>" prompt is displayed, CLIPS waits for input to evaluate. Once valid input is provided and followed by pressing the return key, the input is evaluated and the result (if any) is printed. Any extraneous input following the valid input is discarded.

Valid input includes function calls, constructs, local or global variables, and constants. Function calls in CLIPS use prefix notation---operands to a function always appear after the function name. Entering a construct definition at the CLIPS prompt creates a new construct of the appropriate type. Both function calls and constructs use parentheses as delimiters, and these must be properly balanced; otherwise, the input will not be evaluated, or an error will occur.

Entering a global variable causes its value to be printed. Local variables can be set at the command prompt using the bind function and retain their value until a reset or clear command is issued. Entering a local variable causes its value to be printed. Entering a constant causes the constant to be printed (which is not very useful).

An example interaction with the REPL is shown following.

CLIPS (7.0.0 12/9/24)

CLIPS\> (+ 3 4)

7

CLIPS\> (defglobal ?\*x\* = 3)

CLIPS\> ?\*x\*

3

CLIPS\> red

red

CLIPS\> (bind ?a 5)

5

CLIPS\> (+ ?a 3)

8

CLIPS\> (reset)

CLIPS\> ?a

\[EVALUATN1\] Variable a is unbound

FALSE

CLIPS\>

The interactions and their results are:

• The addition function is called, adding the numbers 3 and 4 to yield the result 7.

• A global variable ?\*x\* is defined and given the value 3.

• The variable ?\*x\* is entered at the prompt, and its value is returned.

• The constant symbol *red* is entered and returned (since a constant evaluates to itself).

• The local variable ?a is assigned the value 5 using the bind function.

• The addition function is called again to add the variable ?a to the integer 3, yielding 8.

• The reset command is called to reset the CLIPS environment (which, among other effects, removes the assignment of local variables).

• The variable ?a is entered at the prompt, which causes an error because the variable is no longer bound.

### 2.1.2 Automated Command Entry and Loading

Some operating systems allow additional arguments to be specified for a program when it begins execution. When the CLIPS executable is started under such an operating system, CLIPS can automatically execute a series of commands read directly from a file or load constructs from a file. The command‑line syntax for starting CLIPS and automatically reading commands or loading constructs from a file is shown following.

Syntax

clips \<option\>\*

\<option\> ::= -f \<filename\> \|

-f2 \<filename\> \|

-l \<filename\>

For the **‑f** option, \<filename\> is a file that contains CLIPS commands. If an **exit** command is included in the file, CLIPS will halt, and the user will be returned to the operat­ing system after executing the commands in the file. If an **exit** command is not included, CLIPS will enter its interactive state after executing the commands. Commands in the file should be entered exactly as they would be interactively (i.e., opening and closing parentheses must be included, and a carriage return must appear at the end of each command). The **‑f** command‑line option is equivalent to interactively entering a **batch** command as the first command at the CLIPS prompt.

The **-f2** option is similar to the **-f** option, but is equivalent to interactively entering a **batch\*** command. The commands stored in \<filename\> are immediately executed, but the commands and their return values are not displayed as they would be for a **batch** command.

For the **-l** option, \<filename\> should be a file containing CLIPS constructs. This file will be loaded into the environment. The **‑l** command‑line option is equivalent to interactively entering a **load** command.

Files specified using the **--f** option are not processed until the CLIPS prompt appears, so these files will always be processed after files specified using the **--f2** and **--l** options.

## 2.2 Reference Manual Syntax

Terminology is used throughout this manual to describe the syntax of CLIPS constructs and functions. Plain words or characters (including parentheses) are to be typed exactly as they appear. Sequences of words enclosed in single‑angle brackets (called terms or non-terminal symbols), such as \<string\>, represent a single entity of the named class of items to be supplied by the user. A non-terminal symbol followed by an \* represents zero or more entities of the named class of items. A non-terminal symbol followed by a + represents one or more entities of the named class of items. An \* or + by itself is to be typed as it appears. Vertical and horizontal ellipses (three dots arranged vertically and horizontally, respectively) are also used between non-terminal symbols to indicate the occurrence of one or more entities. A term enclosed within square brackets, such as \[\<comment\>\], is optional (i.e., it may or may not be included). Vertical bars indicate a choice between multiple terms. White spaces (tabs, spaces, carriage returns) are used by CLIPS only as delimiters between terms and are ignored otherwise (unless inside double quotes). The ::= symbol is used to indicate how a non-terminal symbol can be replaced. For example, the following syntax description indicates that a \<lexeme\> can be replaced with either a \<symbol\> or a \<string\>.

\<lexeme\> ::= \<symbol\> \| \<string\>

A complete BNF listing for CLIPS constructs along with some commonly used replacements for non-terminal symbols is listed in Appendix G.

## 2.3 Basic Programming Elements

CLIPS provides three basic elements for writing programs: primitive data types, functions for manipulating data, and constructs for adding to a knowledge base.

### 2.3.1 Data Types

CLIPS provides eight primitive data types for representing information. These types are **float**, **integer**, **symbol**, **string**, **external‑address**, **fact‑address**, **instance‑name,** and **instance‑address**. Numeric information can be represented using floats and integers. Symbolic information can be represented using symbols and strings.

A .ib;**number**; consists *only* of digits (0--9), a decimal point (.), a sign (+ or -), and, optionally, an (e) for exponential notation with its corresponding sign. A number is either stored as a float; or an integer. Any number consisting of an optional sign followed by only digits is stored as an **integer** (represented internally by CLIPS as a C long long integer). All other numbers are stored as **floats** (represented internally by CLIPS as a C double‑precision float). The number of significant digits will depend on the machine implementation. Roundoff errors may also occur, again depend­ing on the machine implementation. As with any computer language, care should be taken when comparing floating‑point values to each other or comparing integers to floating-point values. Some examples of integers are:

237 15 +12 -32

Some examples of floats are:

237e3 15.09 +12.0 -32.3e-7

Specifically, integers use the following format:

\<integer\> ::= \[+ \| -\] \<digit\>+

\<digit\> ::= 0 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9

Floating point numbers use the following format:

\<float\> ::= \<integer\> \<exponent\> \|

\<integer\> . \[\<exponent\>\] \|

. \<unsigned integer\> \[\<exponent\>\] \|

\<integer\> . \<unsigned integer\> \[\<exponent\>\]

\<unsigned-integer\> ::= \<digit\>+

\<exponent\> ::= e \| E \<integer\>

A sequence of characters that does not exactly follow the format of a number is treated as a symbol.

A **symbol** in CLIPS is any sequence of characters that starts with a printable ASCII character and is followed by zero or more printable ASCII characters. The symbol ends when a delimiter is encountered. The following characters act as **delimiters**: any non-printable ASCII character (including spaces, tabs, carriage returns, and line feeds), a double quote, opening and closing parentheses "(" and ")", an ampersand "&", a vertical bar "\|", a less-than sign "\<", and a tilde "\~". A semicolon ";" starts a CLIPS comment and also acts as a delimiter. Delimiters may not be included in symbols, with the exception of the "\<" character, which may be the first character in a symbol. Additionally, a symbol may not begin with either the "?" character or the "\$?" sequence of characters (though these characters may appear elsewhere in a symbol), as these are reserved for variables. CLIPS is case-sensitive (i.e., uppercase letters will match only uppercase letters). Note that numbers are a special case of symbols (i.e., they satisfy the definition of a symbol, but they are treated as a different data type). Some simple examples of symbols are:

red Hello B76-HI bad_value

127A 456-93-039 @+=-% 2each

A **string** is a set of characters that starts with a double quote (\") and is followed by zero or more printable characters. A string ends with a double quote. Double quotes may be embedded within a string by placing a backslash (\\) in front of the character. A backslash may be embedded by placing two consecutive backslash characters in the string. Some examples are:

\"red\" \"a and b\" \"1 number\" \"a\\\"quote\"

Note that the string "abcd\" is not the same as the symbol *abcd*. They both contain the same characters, but are of different types. The same holds true for the instance name \[abcd\].

An **external‑address** is the address of an external data structure returned by a function (written in a language such as C or Java) that has been integrated with CLIPS. This data type can only be created by calling a function (i.e., it is not possible to specify an external‑address using text). In the basic version of CLIPS (which has no user-defined external functions), it is not possible to create this data type. External‑addresses are discussed in further detail in the *Advanced Programming Guide*;. Within CLIPS, the printed representation of an external‑address is:

\<Pointer-C-XXXXXX\>

where XXXXXX is the external‑address.

A **fact** is a list of primitive values that are either referenced positionally (ordered facts) or by name (non‑ordered or template facts). Facts are referred to by index, fact-name, or fact-address. The printed format of a **fact‑address** is:

\<Fact-XXX\>

where XXX is the fact‑index.

A **fact-name** is a symbol that begins with the @ character and is used to identify a fact. Two facts are not permitted to have the same fact-name. When passed as an argument to a generic function, fact-names are converted to the fact-address of the corresponding fact.

An **instance** is an **object** that is an instantiation or specific example of a **class**. Objects in CLIPS are defined as floats, integers, symbols, strings, multifield values, external‑addresses, fact‑addresses, and instances of a user‑defined class. A user‑defined class is created using the **defclass** construct. An instance of a user‑defined class is created with the **make‑instance** function, and such an instance can be referred to uniquely by address. An **instance‑name** is formed by enclosing a symbol within left and right brackets. Thus, pure symbols may not be surrounded by brackets. If the CLIPS Object-Oriented Language (COOL) is not included in a particular CLIPS configuration, then brackets may be wrapped around symbols. Some examples of instance‑names are:

\[pump-1\] \[red\] \[+++\] \[123-890\]

Note that the brackets are not part of the name of the instance; they merely indicate that the enclosed symbol is an instance‑name. An **instance‑address** can only be obtained by binding the return value of a function called **instance‑address** or by binding a variable to an instance that matches an object pattern on the LHS of a rule (i.e., it is not possible to specify an instance‑address by typing the value). A reference to an instance of a user‑defined class can be by either name or address. Within CLIPS, the printed representation of an instance‑address is

\<Instance-XXX\>

where XXX is the name of the instance.

In CLIPS, a placeholder that has a value (one of the primitive data types) is referred to as a **field**. The primitive data types are referred to as **single‑field values**. A **constant** is a non‑varying single-field value directly expressed as a series of characters (which means that external‑addresses, fact‑addresses, and instance‑addresses cannot be expressed as constants because they can only be obtained through function calls and variable bindings). A **multifield value** is a sequence of zero or more single-field values. When displayed by CLIPS, multifield values are enclosed in parentheses. Collectively, single-field and multifield values are referred to as **values**. Some examples of multifield values are:

\(a\) (1 blue red) () (x 3.0 \"red\" 567)

Note that the multifield value (a) is not the same as the single-field value *a*. Multifield values are created either by calling functions that return multifield values, by using wildcard arguments in a deffunction, object message‑handler, or method, or by binding variables during the pattern matching process for rules. In CLIPS, a **variable** is a symbolic location that is used to store values. Variables are used by many of the CLIPS constructs (such as defrule, deffunction, defmethod, and defmessage‑handler) and their usage is explained in the sections describing each of these constructs.

### 2.3.2 Functions

A **function** in CLIPS is a piece of executable code identified by a specific name that returns a useful value or performs a useful side effect (such as displaying information). Throughout the CLIPS documentation, the word function is generally used to refer only to functions that return a value (whereas commands and actions are used to refer to functions that have a side effect but generally do not return a value).

There are several types of functions. **User-defined functions** and **system-defined functions** are pieces of code that have been written in an external language (such as C, Java, or C#) and linked with the CLIPS environment. System defined functions are those functions that have been defined internally by the CLIPS environment. User-defined functions are functions that have been defined externally to the CLIPS environment. A complete list of system defined functions can be found in Appendix H.

The **deffunction** construct allows users to define new functions directly in the CLIPS environment using CLIPS syntax. Functions defined in this manner appear and act like other functions; however, instead of being directly executed (as code written in an external language would be), they are interpreted by the CLIPS environment.

Generic functions can be defined using the **defgeneric** and **defmethod** constructs. Generic functions allow different pieces of code to be executed depending upon the arguments passed to the generic function. Thus, a single function name can be **overloaded** with more than one piece of code.

Function calls in CLIPS use a prefix notation --- the arguments to a function always appear after the function name. Function calls begin with a left parenthesis, followed by the name of the function, and then the arguments to the function (each argument separated by one or more spaces). Arguments to a function can be primitive data types, variables, or another function call. The function call is closed with a right parenthesis.

Example

CLIPS\> (+ 3 4 5)

12

CLIPS\> (\* 5 6.0 2)

60.0

CLIPS\> (+ 3 (\* 8 9) 4)

79

CLIPS\> (\* 8 (+ 3 (\* 2 3 4) 9) (\* 3 4))

3456

CLIPS\>

While a function refers to a piece of executable code identified by a specific name, an **expression** refers to a function with specified arguments (which may or may not include function calls). Thus, the previous example contains expressions that make calls to the \* and + functions.

### 2.3.3 Constructs

Several defining **constructs** appear in CLIPS: **defmodule**, **defrule**, **deffacts**, **deftemplate**, **defglobal**, **deffunction**, **defclass**, **definstances**, **defmessage‑handler**, **defgeneric**, **defmethod**, and **deftable**. All constructs in CLIPS are surrounded by parentheses. The construct opens with a left parenthe­sis and closes with a right parenthesis. Defining a construct differs from calling a function primarily in its effect. Typically a function call leaves the CLIPS environment unchanged (with some notable exceptions, such as resetting or clearing the environment or opening a file). Defining a construct, however, is explicitly intended to alter the CLIPS environment by adding to the CLIPS knowledge base. Unlike function calls, constructs never have a return value.

As with any programming language, it is highly beneficial to comment CLIPS code. All constructs (with the exception of defglobal) allow a comment directly following the construct name. Comments also can be placed within CLIPS code by using a semicolon (;). Everything from the semicolon until the next newline character will be ignored by CLIPS. If the semicolon is the first character in the line, the entire line will be treated as a comment. Semicolon-commented text is not saved by CLIPS when loading constructs (however, the optional comment string within a construct is saved).

## 2.4 Data Abstraction

There are four primary formats for representing information in CLIPS: facts, objects, global variables, and goals.

### 2.4.1 Facts

Facts are one of the basic high‑level forms for representing information in a CLIPS system. Each **fact** represents a piece of information that has been placed in the current list of facts, called the **fact‑list**. Facts are the fundamental units of data used by rules.

Facts may be added to the fact‑list (using the **assert** command), removed from the fact‑list (using the **retract** command), modified (using the **modify** or **update** command), or duplicated (using the **duplicate** command) through explicit user interaction or as a CLIPS program executes;.

If a fact is asserted into the fact‑list that exactly matches an already existing fact, the new assertion will be ignored (however, this behavior can be changed using the **set-fact-duplication** function). Duplicates of facts using certainty factors are allowed (where the check for duplication does not include the **CF** slot), but a new fact is not asserted; instead, the certainty factor of the existing fact is updated by combining it with the certainty factor of the new fact. Two named facts cannot use the same fact-name in their **name** slot; attempting to assert a named fact using the fact-name of an existing named fact will generate an error.

Some commands, such as the **retract**, **modify**, **update**, and **duplicate** commands, require a fact to be specified. A fact can be specified by its **fact‑index**, **fact‑name**, or **fact‑address**.

The fact-index of a fact is an integer assigned to the fact when it is asserted. Fact‑indices start at one and are incremented by one for each new fact. When a fact is modified, its fact-index remains unchanged. Whenever a **reset** or **clear** command is given, the fact‑indices restart at one.

A **fact identifier** is a shorthand notation for displaying a fact using its fact-index. It consists of the character "f", followed by a dash, and then the fact‑index of the fact. For example, f‑10 refers to the fact with fact‑index 10.

A fact-name is a symbol beginning with the @ character, assigned to the **name** slot of facts inheriting from the **ND** deftemplate. The fact-name can be explicitly specified when the fact is asserted; otherwise, one will be automatically generated. The default value for the fact-name is generated by prepending the @ character to the fact identifier. For example, the fact-name for the fact with a fact-index of 1 would be \@f-1. If the default fact-name is already assigned to another fact, then an additional hyphen and an integer are appended to the fact-name to generate an unassigned fact-name.

The fact‑address of a fact can be obtained by capturing the return value of commands that return fact addresses (such as **assert**, **modify**, **update**, and **duplicate**), or by binding a variable to the fact address of a fact which matches a pattern on the LHS of a rule.

A fact is stored in one of two formats: ordered or non‑ordered.

#### 2.4.1.1 Ordered Facts

**Ordered facts** consist of a symbol followed by a sequence of zero or more fields, separated by spaces and delimited by an opening parenthesis on the left and a closing parenthesis on the right. The first field of an ordered fact specifies a "relation" that applies to the remaining fields in the ordered fact. For example, (father‑of Jack Bill) states that Bill is the father of Jack.

Some examples of ordered facts are shown following:

(the pump is on)

(altitude is 10000 feet)

(grocery-list bread milk eggs)

Fields in a non‑ordered fact may be of any of the primitive data types (with the exception of the first field, which must be a symbol), and no restriction is placed on the ordering of fields. The following symbols are reserved and should not be used as the *first* field in any fact (ordered or non‑ordered): *test*, *and*, *or*, *not*, *declare*, *logical*, *object*, *exists*, *forall*, *goal*, and *explicit*. These words are reserved only when used as a deftemplate name (whether explicitly defined or implied). These symbols may be used as slot names; however, this is not recommended.

#### 2.4.1.2 Non‑ordered Facts

Ordered facts encode information positionally. To access that information, a user must know not only what data is stored in a fact but also which position contains the data. **Non‑ordered (or deftemplate) facts** provide the user with the ability to abstract the structure of a fact by assign­ing names to each field in the fact. The **deftemplate** construct is used to create a template that can then be used to access fields by name. The deftemplate construct is analogous to a structure definition in C.

The deftemplate construct allows the name of a template to be defined, along with zero or more **slot** definitions. Unlike ordered facts, the slots of a deftemplate fact may be constrained by type, value, and numeric range. In addition, default values can be specified for a slot. A slot consists of an opening parenthesis, followed by the name of the slot, zero or more fields, and a closing parenthesis. Note that slots cannot be used in an ordered fact and information in a deftemplate fact cannot be referenced positionally.

Deftemplate facts are distinguished from ordered facts by the first field within the fact. The first field of all facts must be a symbol; however, if that symbol corresponds to the name of a deftemplate, then the fact is a deftemplate fact. The first field of a deftemplate fact is followed by a list of zero or more slots. As with ordered facts, deftemplate facts are enclosed by an opening parenthesis on the left and a closing parenthesis on the right.

Some examples of deftemplate facts are shown following.

(client (name \"Joe Brown\") (id X9345A))

(point-mass (x-velocity 100) (y-velocity -200))

(class (teacher \"Martha Jones\") (#-students 30) (Room \"37A\"))

(grocery-list (#-of-items 3) (items bread milk eggs))

Note that the order of slots in a deftemplate fact is not important. For example, the following facts are all identical:

(class (teacher \"Martha Jones\") (#-students 30) (Room \"37A\"))

(class (#-students 30) (teacher \"Martha Jones\") (Room \"37A\"))

(class (Room \"37A\") (#-students 30) (teacher \"Martha Jones\"))

In contrast, note that the following ordered facts *are not* identical:

(class \"Martha Jones\" 30 \"37A\")\
(class 30 \"Martha Jones\" \"37A\")\
(class \"37A\" 30 \"Martha Jones\")

In addition to being asserted and retracted, deftemplate facts can also be modified, updated, and duplicated (using the **modify**, **update**, and **duplicate** commands). Modifying or updating a fact changes a set of specified slots within that fact. When a fact is updated, pattern matching is limited to associated patterns that contain one of the changed slots. When a fact is modified, pattern matching is performed for all associated patterns. Duplicating a fact creates a new fact identical to the original, and then changes a set of specified slots within the new fact. The benefit of using the modify, update, and duplicate commands is that slots that don't change do not need to be specified.

Deftemplates support inheritance. A deftemplate can be defined using another deftemplate as a base, inheriting all slots and associated attributes of the base deftemplate while allowing for the addition of new slots or the refinement of inherited ones. Two predefined deftemplates feature managed slots: the **ND** (named) deftemplate and the **CFD** (certainty factor) deftemplate. The **ND** deftemplate defines a **name** slot for storing a fact's fact-name, while the **CFD** deftemplate defines a **CF** slot for storing a fact's certainty factor. These slots function similarly to other slots; however, special logic ensures that their values are maintained correctly. The **name** slot must contain a unique fact-name that is not shared by any other fact, and the **CF** slot's value is automatically recomputed when an identical fact is asserted.

#### 2.4.1.3 Initial Facts

The **deffacts** construct allows a set of *a priori* or initial knowledge to be specified as a collection of facts. When the CLIPS environment is reset (using the **reset** command), every fact specified within a deffacts construct in the CLIPS knowledge base is added to the fact‑list.

### 2.4.2 Objects

An **object** in CLIPS is a symbol, a string, a floating-point or integer number, a multifield value, an external-address, or an instance of a user-defined class. Objects are described in two fundamental parts: properties and behavior. A **class** serves as a template for the common properties and behaviors of objects that are **instances** of that class. Examples of objects and their corresponding classes include:

  ------------------------------------------------------------------
   **Object (Printed Representation)**           **Class**
  ------------------------------------- ----------------------------
               Rolls-Royce                         SYMBOL

             \"Rolls-Royce\"                       STRING

                   8.0                             FLOAT

                    8                             INTEGER

   (8.0 Rolls-Royce 8 \[Rolls-Royce\])           MULTIFIELD

          \<Pointer-00CF61AB\>                EXTERNAL-ADDRESS

             \[Rolls-Royce\]             CAR (a user-defined class)
  ------------------------------------------------------------------

Objects in CLIPS are divided into two categories: primitive types and instances of *user‑defined* classes. These two types of objects differ in how they are referenced, created, and deleted, as well as in how their properties are specified.

Primitive-type objects are referenced simply by their value and are created and deleted implicitly by CLIPS as they are needed. These objects have no names or slots, and their classes are predefined by CLIPS. Although primitive-type objects behave similarly to instances of user-defined classes---allowing you to define message‑handlers and attach them to the primitive-type classes---their use in an object-oriented programming (OOP) context is expected to be minimal. The primary reason classes are provided for primitive types is to support generic functions, which use the classes of their arguments to determine which methods to execute.

An instance of a user-defined class is referenced by name or address and is created and deleted explicitly via messages and special functions. The properties of an instance of a *user‑defined* class are expressed through a set of slots, which the object inherits from its class. As previously defined, slots are named single-field or multifield values. For example, the object Rolls‑Royce is an instance of the class CAR. One of the slots in the class CAR might be "price", and the Rolls‑Royce object's value for this slot could be \$75,000.00. The behavior of an object is specified using procedural code called message‑handlers, which are attached to the object's class. All instances of a user-defined class share the same set of slots, but each instance may have different values for those slots. However, two instances with identical sets of slots do not necessarily belong to the same class, as two different classes can have identical sets of slots.

Inheritance allows the properties and behavior of a class to be described in terms of other classes. COOL supports multiple inheritance: a class may directly inherit slots and message‑handlers from more than one class. In contrast, deftemplates support single inheritance. Since inheritance is only useful for slots and message‑handlers, it is often not meaningful to inherit from one of the primitive type classes, such as MULTIFIELD or NUMBER. This is because these classes cannot have slots and typically do not have message‑handlers.

#### 2.4.2.1 Initial Objects

The **definstances** construct allows a set of *a priori* or initial knowledge to be specified as a collection of instances of user-defined classes. When the CLIPS environment is reset (using the **reset** command), every instance specified within a definstances construct in the CLIPS knowledge base is added to the instance-list.

### 2.4.3 Global Variables

The **defglobal** construct allows variables to be defined as global in scope throughout the CLIPS environment. That is, a global variable can be accessed anywhere within the CLIPS environment and retains its value independently of other constructs. In contrast, some constructs (such as defrule and deffunction) allow local variables to be defined within the construct's definition. These local variables can be referenced within the construct but cannot be referenced outside of it. A CLIPS global variable is similar to global variables found in procedural programming languages such as C and Java.

### 2.4.4 Goals

CLIPS supports data-driven backward chaining. When a deftemplate pattern in a rule has no matches, and another rule contains a **goal** conditional element for that deftemplate, a goal is automatically generated. For example:

(defrule welcome-user\
(av (attribute user) (value ?user))\
=\>\
(println \"Welcome \" ?user))

(defrule get-value\
(goal (av (attribute ?attribute)))\
=\>\
(print \"What is the value of \" ?attribute \"? \")\
(assert (av (attribute ?attribute) (value (readline)))))

Because the *get-value* rule has a **goal** conditional element for the *av* deftemplate, rules with an unmatched pattern for the *av* deftemplate can generate goals. If the *av* pattern in the *welcome-user* rule is unmatched, a goal is generated for it:

g-1 (av (attribute user) (value ??))

Goals appear similar to facts, but instead of a fact identifier, there is a goal identifier (in this case, g-1). The value ?? in the goal represents a universally quantified value, indicating that the value was not specified when the goal was generated. When pattern matching, a universally quantified value matches any literal value constraint.

Once the goal is generated, the *get-value* rule is activated. If allowed to execute, it will assert an *av* fact with the *attribute* slot set to *user* and the *value* slot set to the user's response. Once this fact is asserted, the pattern in the *welcome-user* rule is matched, and the goal is automatically removed.

## 2.5 Knowledge Representation

CLIPS provides heuristic and procedural paradigms for representing knowledge, which are discussed in this section. Object‑oriented programming (which combines aspects of both data abstraction and procedural knowledge) is covered in Section 2.6.

### 2.5.1 Heuristic Knowledge -- Rules

The primary method of representing heuristic knowledge in CLIPS is through rules, which specify a set of actions to be performed for a given situation. The developer of an expert system defines a set of rules that collectively work together to solve a problem. A **rule** is composed of an **antecedent** and a **consequent**. The antecedent of a rule is also referred to as the **if portion** or the **left-hand side** (LHS) of the rule. The consequent of a rule is also referred to as the **then portion** or the **right-hand side** (RHS) of the rule.

The antecedent of a rule is a set of **conditions** (or **conditional elements**) that must be satisfied for the rule to be applicable. In CLIPS, the conditions of a rule are satisfied based on the existence or non-existence of specified facts in the fact‑list or specified instances of user‑defined classes in the instance‑list. One type of condition that can be specified is a **pattern**. Patterns consist of a set of restrictions used to determine which facts or objects satisfy the condition specified by the pattern. The process of matching facts and objects to patterns is called **pattern matching**. CLIPS provides a mechanism, called the **inference engine**, which automatically matches patterns against the current state of the fact‑list and instance‑list and determines which rules are applicable.

The consequent of a rule is the set of actions to be executed when the rule is applicable. The actions of applicable rules are executed when the CLIPS inference engine is instructed to begin execution. If more than one rule is applicable, the inference engine uses a **conflict resolution strategy** to select which rule should have its actions executed. The actions of the selected rule are executed (which may affect the list of applicable rules), and then the inference engine selects another rule and executes its actions. This process continues until no applicable rules remain.

In some ways, rules can be thought of as IF-THEN statements found in procedural programming languages like C and Java. However, the conditions of an IF-THEN statement in a procedural language are only evaluated when the program flow of control reaches the IF‑THEN statement. In contrast, rules function like WHEN-THEN statements. The inference engine continuously tracks rules whose conditions are satisfied, enabling them to be executed immediately when applicable.

### 2.5.2 Procedural Knowledge

CLIPS also supports a procedural paradigm for representing knowledge. Deffunctions and generic functions allow the user to define new executable elements in CLIPS that perform a useful side effect or return a useful value. These new functions can be called just like the built‑in functions of CLIPS. Message‑handlers allow the user to define the behavior of objects by specifying their response to messages. Deffunctions, generic functions, and message‑handlers are all procedural pieces of code specified by the user that CLIPS executes interpretively at the appropriate times. Defmodules allow a knowledge base to be partitioned.

#### 2.5.2.1 Deffunctions

Deffunctions allow you to define new functions in CLIPS directly (as opposed to user‑defined functions, which are written in an external language such as C or Java). The body of a deffunction is a series of expressions similar to the RHS of a rule that are executed in order by CLIPS when the deffunction is called. The return value of a deffunction is the value of the last expression evaluated within the deffunction. Calling a deffunction is identical to calling any other function in CLIPS.

#### 2.5.2.2 Generic Functions

Generic functions are similar to deffunctions in that they can be used to define new procedural code directly in CLIPS, and they can be called like any other function. However, generic functions are much more powerful because they can be **overloaded**. A generic function will do different things depending on the types (or classes and deftemplates) and number of its arguments. Generic functions are composed of multiple components called methods, where each method handles different cases of arguments for the generic function. For example, you might overload the "+" operator to do string concatenation when it is passed strings as arguments. However, the "+" operator will still perform arithmetic addition when passed numbers. There are two methods in this example: an explicit one for strings defined by the user and an implicit one, which is the standard CLIPS arithmetic addition operator. The return value of a generic function is the evaluation of the last expression in the method executed.

#### 2.5.2.3 Object Message‑Passing

Objects are described in two basic parts: properties and behavior. Object properties are specified in terms of slots obtained from the object's class. Object behavior is specified in terms of procedural code called message‑handlers, which are attached to the object's class. Objects are manipulated via message‑passing. For example, to cause the Rolls-Royce object, which is an instance of the class CAR, to start its engine, the user must call the **send** function to send the message "start‑engine" to the Rolls-Royce. How the Rolls-Royce responds to this message will be dictated by the execution of the message‑handlers for "start‑engine" attached to the CAR class and any of its superclasses. The result of a message is similar to a function call in CLIPS: a useful return value or side effect.

#### 2.5.2.4 Defmodules

Defmodules allow a knowledge base to be partitioned. Every construct that is defined must be placed in a module. The programmer can explicitly control which constructs in a module are visible to other modules and which constructs from other modules are visible to a module. The visibility of facts and instances between modules can be controlled in a similar manner. Modules can also be used to control the flow of execution of rules.

## 2.6 CLIPS Object‑Oriented Language

This section provides a brief overview of the programming elements of the CLIPS Object‑Oriented Language (COOL). COOL includes elements of data abstraction and knowledge representation. This section offers an overview of COOL as a whole, incorporating the elements of both concepts.

### 2.6.1 COOL Deviations from a Pure OOP Paradigm

In a pure OOP language, *all* programming elements are objects that can only be manipulated via messages. In CLIPS, the definition of an object is much more constrained: floating-point and integer numbers, symbols, strings, multifield values, external‑addresses, fact‑addresses, and instances of user-defined classes. All objects *may* be manipulated with messages, except instances of user-defined classes, which *must* be manipulated via messages. For example, in a pure OOP system, to add two numbers together, you would send the message "add" to the first number object with the second number object as an argument. In CLIPS, you may simply call the "+" function with the two numbers as arguments, or you can define message‑handlers for the NUMBER class that allow you to do it in a purely OOP fashion.

All programming elements that are not objects must be manipulated in a non‑OOP utilizing function tailored for those programming elements. For example, to print a rule, you call the **ppdefrule** command; you do not send a message "print" to a rule, since it is not an object.

### 2.6.2 Primary OOP Features

OOP systems have five primary characteristics: **abstraction**, **encapsulation**, **inheritance**, **polymorphism**, and **dynamic binding**. An abstraction is a higher level, more intuitive representation of a complex concept. Encapsulation is the process whereby the implementation details of an object are masked by a well-defined external interface. Classes may be described in terms of other classes through inheritance. Polymorphism is the ability of different objects to respond to the same message in a specialized manner. Dynamic binding is the ability to defer the selection of which specific message‑handlers will be called for a message until runtime.

The definition of new classes allows the abstraction of new data types in COOL. The slots and message‑handlers of these classes describe the properties and behavior of a new set of objects.

COOL supports encapsulation by requiring message‑passing for the manipulation of instances of user‑defined classes. An instance cannot respond to a message for which it does not have a defined message‑handler.

COOL allows the user to specify some or all of the properties and behavior of a class in terms of one or more unrelated superclasses. This process is called **multiple inheritance**. COOL uses the existing hierarchy of classes to establish a linear ordering called the **class precedence list** for a new class. Objects that are instances of this new class can inherit properties (slots) and behavior (message‑handlers) from each of the classes in the class precedence list. The word "precedence" implies that properties and behavior of a class that first appear in the list override conflicting definitions of a class that appear later in the list.

One COOL object can respond to a message in a completely different way than another object; this is polymorphism. This is accomplished by attaching message‑handlers with differing actions, which have the same name, to the classes of these two objects, respectively.

Dynamic binding is supported in that an object reference in a **send** function call is not bound until runtime. For example, an instance‑name or variable might refer to one object at the time a message is sent and another at a later time.

### 2.6.3 Instance‑set Queries and Distributed Actions

In addition to the ability of rules to directly pattern‑match on objects, COOL provides a useful query system for determining, grouping, and performing actions on sets of instances of user-defined classes that meet user-defined criteria. The query system allows you to associate instances that are either related or not. You can simply use the query system to determine if a particular association set exists, save the set for future reference, or iterate an action over the set. An example of the use of the query system might be to find the set of all pairs of boys and girls that have the same age.

#
