# Section 12: Deftable Construct

A common use case involves referencing immutable data within a rule using a value bound to a variable from a previous pattern. For example, in the following rule, the first pattern binds a variable to the name of an attribute whose value needs to be determined, while the second pattern uses that name to retrieve the corresponding question text for the attribute. This is similar to the use of a foreign key in a database.

(defrule determine-attribute

(goal (av (attribute ?attribute)))

(question (attribute ?attribute) (text ?text))

=\>

(print ?text \" \")

(assert (av (attribute ?attribute) (value (read)))))

Storing questions as facts or instances avoids hardcoding text directly in rules, simplifying internationalization and rule generalization. However, mixing mutable and immutable data among facts and instances can obscure changing data, making programs more difficult to debug.

CLIPS allows immutable data to be represented using a construct visually resembling a table. Table definitions include an optional declaration, followed by a row containing the column names used by the table. Each column name must be a symbol, and at least one column must be specified. The subsequent rows store data, with each row containing values corresponding to the column names in the first row. Table values can be either single or multifield values.

The first value in each row serves as a unique identifier, known as the key. No two rows can share the same key. The key can be a single-field value, such as a symbolic ID associated with an attribute, or a multifield value, such as the make and model of a car.

The following two-column table stores the text of a couple of questions. The first column, *ID*, acts as the unique key for each row, while the second column, *text*, contains the corresponding question associated with each ID.

(deftable questions

(ID text )

(donor-group \"What is the donor\'s blood group?\" )

(recipient-group \"What is the recipient\'s blood group?\" ))

The prior rule can now be written as:

> (defrule determine-attribute\
> (goal (av (attribute ?attribute)))\
> =\>
>
> (print (lookup questions ?attribute text) \" \")
>
> (assert (av (attribute ?attribute) (value (read)))))

## 12.1 Defining Tables

Tables are defined using the deftable construct.

Syntax

(deftable \<deftable-name\> \[\<comment\>\]

\[\<table-declaration\>\]\
\<column-specification\>

\<row-specification\>\*)

\<table-declaration\> ::= (declare \<table-property\>+)

\<table-property\> ::= (auto-keys \<boolean-symbol\>)

\<boolean-symbol\> ::= TRUE \| FALSE

\<column-specification\> ::= (\<column-name\>\*)

\<column-name\> ::= \<symbol\> \|

\<global-variable\> \|

=\<function-call\>

\<row-specification\> ::= (\<row-column-value\>\*)

\<row-column-value\> ::= \<table-constant\> \|\
(\<table-constant\>\*) \|

\<global-variable\> \|\
=\<function-call\>

\<table-constant\> ::= \<symbol\> \| \<string\> \| \<instance-name\> \| \<integer\> \| \<float\>

If the auto-keys property is declared as TRUE, the first column name in the column specification is automatically defined as the symbol **key**. Additionally, a *key* column value is automatically assigned to each row specification, starting at 1 and incrementing by 1 for each subsequent row.

A table must have at least one column, either by declaring the auto-keys property as TRUE or by explicitly specifying a column in the column specification. Additionally, each row must contain a number of values that matches the number of columns in the column specification.

Example 1

In this example, the blood groups, their types, and Rh compatibility are represented using tables:

CLIPS\>

(deftable blood-groups

( group type rh )

;\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

( A+ A + )

( A- A - )

( B+ B + )

( B- B - )

( AB+ AB + )

( AB- AB - )

( O+ O + )

( O- O - ))

CLIPS\>

(deftable type-compatibility

(donor recipient )

;\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

(O (O A B AB) )

(A (A AB) )

(B (B AB) )

(AB (AB) ))

CLIPS\>

(deftable rh-compatibility

(donor recipient )

;\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

(+ (+) )

(- (- +) ))

CLIPS\>

The **lookup** function is used to retrieve values from table rows:

CLIPS\> (lookup blood-groups A+ type)

A

CLIPS\> (lookup blood-groups A+ rh)

\+

CLIPS\> (lookup type-compatibility O recipient)

(O A B AB)

CLIPS\>

Retrieval of values from the tables can be wrapped within deffunctions to determine blood compatibility:

CLIPS\>

(deffunction blood-type (?group)

(lookup blood-groups ?group type))

CLIPS\>

(deffunction type-compatible (?dt ?rt)

(member\$ ?rt (lookup type-compatibility ?dt recipient)))

CLIPS\>

(deffunction blood-rh (?group)

(lookup blood-groups ?group rh))

CLIPS\>

(deffunction rh-compatible (?dr ?rr)

(member\$ ?rr (lookup rh-compatibility ?dr recipient)))

CLIPS\>

(deffunction compatible (?d ?r)

(and (type-compatible (blood-type ?d) (blood-type ?r))

(rh-compatible (blood-rh ?d) (blood-rh ?r))))

CLIPS\> (compatible O- A+)

TRUE

CLIPS\> (compatible AB+ B-)

FALSE

CLIPS\>

The questions and conclusions for identifying blood compatibility can be stored in tables:

CLIPS\>

(deftable questions

(key text )

;\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

(donor-group \"What is the donor\'s blood group?\" )

(recipient-group \"What is the recipient\'s blood group?\" ))

CLIPS\>

(deftable conclusions

(key text )

;\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

(TRUE \"Donation is compatible.\" )

(FALSE \"Donation is not compatible.\" ))

CLIPS\>

Finally, rules can be added to determine the donor and recipient blood groups and identify compatibility:

CLIPS\>

(deftemplate av

(slot attribute)

(slot value))

CLIPS\>

(defrule compatible

(av (attribute donor-group) (value ?d))

(av (attribute recipient-group) (value ?r))

=\>

(println (lookup conclusions (compatible ?d ?r) text)))

CLIPS\>

(defrule determine-attribute

(goal (av (attribute ?attribute)))

=\>

(print (lookup questions ?attribute text) \" \")

(assert (av (attribute ?attribute) (value (read)))))

CLIPS\>

The example is now ready for execution:

CLIPS\> (reset)

CLIPS\> (run)

What is the donor\'s blood group? O-

What is the recipient\'s blood group? A+

Donation is compatible.

CLIPS\> (reset)

CLIPS\> (run)

What is the donor\'s blood group? AB+

What is the recipient\'s blood group? B-

Donation is not compatible.

CLIPS\>

Example 2

This example demonstrates the use of the **do-for-row** table query function:

CLIPS\>

(deftable grade-table

( grade lower upper )

;\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

( A+ 97 100 )

( A 93 96 )

( A- 90 92 )

( B+ 87 89 )

( B 83 86 )

( B- 80 82 )

( C+ 77 79 )

( C 73 76 )

( C- 70 72 )

( D+ 67 69 )

( D 63 66 )

( D- 60 62 )

( F 0 60 ))

CLIPS\>

(deffunction to-grade (?num)

(do-for-row (?r grade-table)

(and (\>= ?num ?r:lower) (\<= ?num ?r:upper))

?r:grade))

CLIPS\> (to-grade 92)

A-

CLIPS\> (to-grade 55)

F

CLIPS\>

Example 3

This example demonstrates the use of the **auto-keys** property:

CLIPS\>

(deftable math-classes

(declare (auto-keys TRUE))

( teacher class start end )

;\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

( Winsor Algebra 9:00 10:00 )

( Winsor Geometry 11:00 12:00 )

( Dyke Algebra 9:00 10:00 )

( Dyke Trigonometry 1:00 2:00 )

( Hicks Geometry 12:00 1:00 )

( Hicks Trigonometry 3:00 4:00 )

( Ferguson Calculus 10:00 11:00 )

( Ferguson Calculus 2:00 3:00 ))

CLIPS\>

(deffunction available (?table ?teacher ?class)

(do-for-all-rows (?t ?table)

(and (or (eq ?t:teacher ?teacher) (eq ?teacher any))

(or (eq ?t:class ?class) (eq ?class any)))

(println ?t:teacher \" \" ?t:class \" \" ?t:start \" \" ?t:end)))

CLIPS\> (available math-classes Ferguson any)

Ferguson Calculus 10:00 11:00

Ferguson Calculus 2:00 3:00

CLIPS\> (available math-classes any Trigonometry)

Dyke Trigonometry 1:00 2:00

Hicks Trigonometry 3:00 4:00

CLIPS\> (available math-classes Hicks Geometry)

Hicks Geometry 12:00 1:00

CLIPS\>
