# Appendix C: Glossary

This section defines some of the terminology used throughout this manual.

+:--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **abstraction**           | The definition of new classes to describe the common properties and behavior of a group of objects.                                                                                                                                                                                                                                                |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **action**                | A function executed by a construct (such as the RHS of a rule) which typically has no return value, but performs some useful action.                                                                                                                                                                                                               |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **activation**            | A rule is activated if all of its conditional elements are satisfied and it has not yet fired based on a specific set of matching facts and/or instances that caused it to be activated. Note that a rule can be activated by more than one set of facts and/or instances. An activated rule that is placed on the agenda is called an activation. |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **active instance**       | The object responding to a message which can be referred to by ?self in the message's handlers.                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **agenda**                | A list of all rules that are presently ready to fire. It is sorted by salience values and the current conflict resolution strategy. The rule at the top of the agenda is the next rule that will fire.                                                                                                                                             |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **antecedent**            | The LHS of a rule.                                                                                                                                                                                                                                                                                                                                 |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **bind**                  | The action of storing a value in a variable.                                                                                                                                                                                                                                                                                                       |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **class**                 | Template for describing the common properties (slots) and behavior (message‑handlers) of a group of objects called instances of the class.                                                                                                                                                                                                         |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **class precedence list** | A linear ordering of classes which describes the path of inheritance for a class.                                                                                                                                                                                                                                                                  |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **command**               | A function executed at the REPL (such as the reset command) typically having no return value.                                                                                                                                                                                                                                                      |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **command prompt**        | In the interactive interface, the "CLIPS\>" prompt which indicates that CLIPS is ready for a command to be entered.                                                                                                                                                                                                                                |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **condition**             | A conditional element.                                                                                                                                                                                                                                                                                                                             |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                           |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **conditional**           | A restriction on the LHS of a rule which must be satisfied in order for the rule to be applicable (also referred to as a CE).                                                                                                                                                                                                                      |
|                           |                                                                                                                                                                                                                                                                                                                                                    |
| **element**               |                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **conflict resolution** | A method for determining the order in which rules should fire among rules with the same salience. There are seven different conflict resolution strategies: depth, breadth, simplicity, complexity, lex, mea, and random. |
|                         |                                                                                                                                                                                                                           |
| **strategy**            |                                                                                                                                                                                                                           |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  ---------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **consequent**                           The RHS of a rule.

                                           

  **constant**                             A non‑varying single-field value directly expressed as a series of characters.

                                           

  **constraint**                           In patterns, a constraint is a requirement that is placed on the value of a field from a fact or instance that must be satisified in order for the pattern to be satisfied. For example, the \~red constraint is satisfied if the field to which the constraint is applied is not the symbol *red*. The term constraint is also used to refer to the legal values allowed in the slots of facts and instances.

                                           

  **construct**                            A high level CLIPS abstraction used to add components to the knowledge base.

                                           

  **current focus**                        The module from which activations are selected to be fired.

                                           

  **current module**                       The module to which newly defined constructs that do not have a module specifier are added. It is also the default module for certain commands which accept as an optional argument a module name (such as list-defrules).

                                           

  **daemon**                               A message‑handler which executes implicitly whenever some action is taken upon an object, such as initialization, deletion, or slot access.

                                           

  **deffunction**                          A non‑overloaded function written directly in CLIPS.

                                           

  **deftemplate fact**                     A deftemplate name followed by a list of named fields (slots) and specific values used to represent a deftemplate object. Note that a deftemplate fact has no inheritance. Also called a non‑ordered fact.

                                           

  **deftemplate pattern**                  A list of named constraints (constrained slots). A deftemplate pattern describes the attributes and associated values of a deftemplate object. Also called a non‑ordered pattern.

                                           

  **delimiter**                            A character which indicates the end of a symbol. The following characters act as delimiters: any non‑printable ASCII character (including spaces, tabs, carriage returns, and line feeds), a double quote, opening and closing parenthesis "(" and ")", an ampersand "&", a vertical bar "\|", a less than "\<", a semicolon ";", and a tilde "\~".

                                           

  **dynamic binding**                      The deferral of which message‑handlers will be called for a message until run‑time.

                                           

  **encapsulation**                        The requirement that all manipulation of instances of user‑defined classes be done with messages.

                                           

  **expression**                           A function call with arguments specified.

                                           

  **external‑address**                     The address of an external data structure returned by a function (written in a language such as C) that has been integrated with CLIPS.

                                           

  **external function**                    A function written in an external language (such as C) defined by the user or provided by CLIPS and called from within CLIPS rules.

                                           

  **facet**                                A component of a slot specification for a class, e.g., default value and cardinality.

                                           

  **fact**                                 An ordered or deftemplate (non‑ordered) fact. Facts are the data about which rules rea­son and represent the current state of the program.

                                           

  **fact‑address**                         A pointer to a fact obtained by binding a variable to the fact which matches a pattern on the LHS of a rule.

                                           

  **fact‑identifier**                      A shorthand notation for referring to a fact. It consists of the character "f", followed by a dash, followed by the fact‑index of the fact.

                                           

  **fact‑index**                           A unique integer index used to identify a particular fact.

                                           

  **fact‑list**                            The list of current facts.

                                           

  **field**                                A placeholder (named or unnamed) that has a value.

                                           

  **fire**                                 A rule is said to have fired if all of its conditions are satisfied and the actions then are executed.

                                           

  **float**                                A number that begins with an optional sign followed optionally in order by zero or more digits, a decimal point, zero or more digits, and an exponent (consisting of an e or E followed by an integer). A floating point number must have at least one digit in it (not including the exponent) and must either contain a decimal point or an exponent.

                                           

  **focus**                                As a verb, refers to changing the current focus. As a noun, refers to the current focus.

                                           

  **focus stack**                          The list of modules that have been focused upon. The module at the top of the focus stack is the current focus. When all the activations from the current focus have been fired, the current focus is removed from the focus stack and the next module on the stack becomes the current focus.

                                           

  **function**                             A piece of executable code identified by a specific name which returns a useful value or performs a useful side effect. Typically only used to refer to functions which do return a value (whereas commands and actions are used to refer to functions which do not return a value).

                                           

  **generic dispatch**                     The process whereby applicable methods are selected and executed for a particular generic function call.

                                           

  **generic function**                     A function written in CLIPS which can do different things depending on what the number and types of its arguments.

                                           

  **inference engine**                     The mechanism that automatically matches patterns against the current state of the fact‑list and list of instances and determines which rules are applicable.

                                           

  **inheritance**                          The process whereby one class can be defined in terms of other class(es).

                                           

  **instance**                             An object is an instance of a class. Throughout the documentation, the term instance usually refers to objects which are instances of user‑defined classes.

                                           

  **instance (of a user‑defined class)**   An object which can only be manipulated via messages, i.e all objects except symbols, strings, integers, floats, multifields and external‑addresses.

                                           

  **instance‑address**                     The address of an instance of a user‑defined class.

                                           

  **instance‑name**                        A symbol enclosed within left and right brackets. An instance‑name refers to an object of the specified name which is an instance of a user‑defined class.

                                           

  **instance‑set**                         An ordered collection of instances of user‑defined classes. Each member of an instance‑set is an instance of a set of classes, where the set can be different for each member.

                                           

  **instance‑set distributed action**      A user‑defined expression which is evaluated for every instance‑set which satisfies an instance‑set query.

                                           

  **instance‑set query**                   A user‑defined boolean expression applied to an instance‑set to see if it satisfies further user‑defined criteria.

                                           

  **integer**                              A number that begins with an optional sign followed by one or more digits.

                                           

  **LHS**                                  Left‑Hand Side. The set of conditional elements that must be satisfied for the ac­tions of the RHS of a rule to be performed.

                                           

  **list**                                 A group of items with no implied order.

                                           

  **logical name**                         A symbolic name that is associated with an I/O source or destination.

                                           

  **message**                              The mechanism used to manipulate an object.

                                           

  **message dispatch**                     The process whereby applicable message‑handlers are selected and executed for a particular message.

                                           

  **message‑handler**                      An implementation of a message for a particular class of objects.

                                           

  **message‑handler precedence**           The property used by the message dispatch to select between handlers when more than one is applicable to a particular message.

                                           

  **method**                               An implementation of a generic function for a particular set of argument restrictions.

                                           

  **method index**                         A shorthand notation for referring to a method with a particular set of parameter restrictions.

                                           

  **method precedence**                    The property used by the generic dispatch to select a method when more than one is applicable to a particular generic function call.

                                           

  **module**                               A container where a set of constructs can be grouped together such that explicit control can be maintained over restricting the access of the constructs by other modules. Also used to control the flow of execution of rules through the use of the focus command.

                                           

  **module specifier**                     A notation for specifying a module. It consists of a module name followed by two colons. When placed before a construct name, it's used to specify which module a newly defined construct is to be added to or to specify which construct a command will affect if that construct is not in the current module.

                                           

  **multifield**                           A sequence of unnamed placeholders each having a value.

                                           

  **multifield value**                     A sequence of zero or more single‑field values.

                                           

  **non‑ordered fact**                     A deftemplate fact.

                                           

  **number**                               An integer or float.

                                           

  **object**                               A symbol, a string, a floating‑point or integer number, a multifield value, an external address, or an instance of a user‑defined class.

                                           

  **order**                                Position is significant.

                                           

  **ordered fact**                         A sequence of unnamed fields.

                                           

  **ordered pattern**                      A sequence of constraints.

                                           

  **overload**                             The process whereby a generic function can do different things depending on the types and number of its arguments, i.e., the generic function has multiple methods.

                                           

  **pattern**                              A conditional element on the LHS of a rule which is used to match facts in the fact‑list.

                                           

  **pattern entity**                       An item that is capable of matching a pattern on the LHS of a rule. Facts and instances are the only types of pattern entities available.

                                           

  **pattern matching**                     The process of matching facts or instances to patterns on the LHS of rules.

                                           

  **polymorphism**                         The ability of different objects to respond to the same message in a specialized manner.

                                           

  **primitive type object**                A symbol, string, integer, float, multifield, fact address, instance name, instance address, or external‑address.

                                           

  **Relation**                             The first field in a fact or fact pattern. Synonomous with the associated deftemplate name.

                                           

  **REPL**                                 Read-Eval-Print Loop. The primary method for issuing commands to CLIPS interactively.

                                           

  **RHS**                                  Right‑Hand Side. The actions to be performed when the LHS of a rule is satisfied.

                                           

  **rule**                                 A collection of conditions and actions. When all patterns are satisfied, the actions will be taken.

                                           

  **salience**                             A priority number given to a rule. When multiple rules are ready for firing, they are fired in order of priority. The default salience is zero (0). Rules with the same salience are fired according to the current conflict resolution strategy.

                                           

  **sequence**                             An ordered list.

                                           

  **shadowed message‑handler**             A message‑handler that must be explicitly called by another message‑handler in order to execute.

                                           

  **shadowed method**                      A method that must be explicitly called by another method in order to execute.

                                           

  **single‑field value**                   One of the primitive data types: float, integer, symbol, string, external‑address, instance‑name, or instance‑address.

                                           

  **slot**                                 Named single field or multifield. To write a slot give the field name (attribute) followed by the field value. A single‑field slot has one value, while a multifield slot has zero or more values. Note that a multifield slot with one value is strictly not the same as a single-field slot. However, the value of a single‑field slot (or variable) may match a multifield slot (or multifield variable) that has one field.

                                           

  **slot‑accessor**                        Implicit message‑handlers which provide read and write access to slots of an object.

                                           

  **specificity (class)**                  A class that precedes another class in a class precedence list is said to be more specific. A class is more specific than any of its superclasses.

                                           

  **specificity (rule)**                   A measure of how "specific" the LHS of a rule is in the pattern matching process. The specificity is determined by the number of constants, variables, and function calls used within LHS conditional elements.

                                           

  **string**                               A set of characters that starts with double quotes (\") and is followed by zero or more printable characters and ends with double quotes.

                                           

  **subclass**                             If a class inherits from a second class, the first class is a subclass of the second class.

                                           

  **superclass**                           If a class inherits from a second class, the second class is a superclass of the first class.

                                           

  **symbol**                               Any sequence of characters that starts with any printable ASCII character and is followed by zero or more characters.

                                           

  **top-level**                            In the interactive interface, the "CLIPS\>" prompt which indicates that CLIPS is ready for a command to be entered.

                                           

  **value**                                A single or multifield value.

                                           

  **variable**                             An symbolic location which can store a value.
  ---------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
