# Section 12: Actions And Functions

This section describes various actions and functions which may be used on the LHS and RHS of rules, from the REPL, and from other constructs such as deffunctions, defmessage‑handlers, and defmethods. The terms functions, actions, and commands should be thought of interchangeably. However, when the term **function** is used it generally refers to a function that returns a value. The term **action** refers to a function having no return value but performing some basic operation as a side effect (such as printout). The term **command** refers to functions normally entered at the top‑level command prompt (such as the **reset** command, which does not return a value, and the **set‑strategy** command, which does return a value).

## 12.1 Predicate Functions

The following functions perform predicate tests.

### 12.1.1 Testing For Numbers

The **numberp** function returns the symbol **TRUE** if its argument is a float or integer; otherwise, it returns the symbol **FALSE**.

Syntax

(numberp \<expression\>)

Example

CLIPS\> (clear)

CLIPS\>

(defrule invalid-response

(response ?v)

(test (not (numberp ?v)))

=\>

(println \"Response \" ?v \" is not a number\"))

CLIPS\> (assert (response 3))

\<Fact-1\>

CLIPS\> (assert (response 7.5))

\<Fact-2\>

CLIPS\> (assert (response abc))

\<Fact-3\>

CLIPS\> (run)

Response abc is not a number

CLIPS\>

### 12.1.2 Testing For Floats

The **floatp** function returns the symbol **TRUE** if its argument is a float; otherwise, it returns the symbol **FALSE**.

Syntax

(floatp \<expression\>)

### 12.1.3 Testing For Integers

The **integerp** function returns the symbol **TRUE** if its argument is an integer; otherwise, it returns the symbol **FALSE**.

Syntax

(integerp \<expression\>)

### 12.1.4 Testing For Strings Or Symbols

The **lexemep** function returns the symbol **TRUE** if its argument is a string or symbol; otherwise. it returns the symbol **FALSE**.

Syntax

(lexemep \<expression\>)

### 12.1.5 Testing For Strings

The **stringp** function returns the **symbol** TRUE if its argument is a string; otherwise, it returns the symbol **FALSE**.

Syntax

(stringp \<expression\>)

### 12.1.6 Testing For Symbols

The **symbolp** function returns the symbol **TRUE** if its argument is a symbol; otherwise, it returns the symbol **FALSE**.

Syntax

(symbolp \<expression\>)

### 12.1.7 Testing For Even Numbers

The **evenp** function returns the symbol **TRUE** if its argument is an even number; otherwise, it returns the symbol **FALSE**.

Syntax

(evenp \<integer-expression\>)

### 12.1.8 Testing For Odd Numbers

The **oddp** function returns the symbol **TRUE** if its argument is an odd number; otherwise, it returns the symbol **FALSE**.

Syntax

(oddp \<integer-expression\>)

### 12.1.9 Testing For Multifield Values

The **multifieldp** function returns the symbol **TRUE** if its argument is a multifield value; otherwise, it returns the symbol **FALSE**.

Syntax

(multifieldp \<expression\>)

Example

CLIPS\> (multifieldp (create\$ red green blue))

TRUE

CLIPS\> (multifieldp 3)

FALSE

CLIPS\>

### 12.1.10 Testing For External‑Addresses

The **external-addressp** function returns the symbol **TRUE** if its argument is an external‑address; otherwise, it returns the symbol **FALSE**.

Syntax

(pointerp \<expression\>)

### 12.1.11 Comparing for Equality

The **eq** function returns the symbol **TRUE** if its first argument is equal in value to all its subsequent arguments; otherwise, it returns the symbol **FALSE**. Note that **eq** compares types as well as values. Thus, (eq 3 3.0) returns the symbol **FALSE** since 3 is an integer and 3.0 is a float.

Syntax

(eq \<expression\> \<expression\>+)

Example

CLIPS\> (eq red green blue red)

FALSE

CLIPS\> (eq red red red red)

TRUE

CLIPS\> (eq 3 4)

FALSE

CLIPS\>

### 12.1.12 Comparing for Inequality

The **neq** function returns the symbol **TRUE** if its first argument is not equal in value to all its subsequent arguments; otherwise, it returns the symbol **FALSE**. Note that **neq** compares types as well as values. Thus, (neq 3 3.0) return the symbol **TRUE** since 3 is an integer and 3.0 is a float.

Syntax

(neq \<expression\> \<expression\>+)

Example

CLIPS\> (neq red green blue green)

TRUE

CLIPS\> (neq red red green blue)

FALSE

CLIPS\> (neq 3 red)

TRUE

CLIPS\>

 Usage Note

When comparing more than two arguments, a **neq** function call is not equivalent to an **eq** function call within a **not** function call:

CLIPS\> (neq a a b)

FALSE

CLIPS\> (not (eq a a b))

TRUE

CLIPS\>

### 12.1.13 Comparing Numbers for Equality

The **=** function returns the symbol **TRUE** if its first argument is equal in value to all its subsequent arguments; otherwise it returns the symbol **FALSE**. Note that **=** compares only numeric values and will convert integers to floats when necessary for comparison.

Syntax

(= \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (= 3 3.0)

TRUE

CLIPS\> (= 4 4.1)

FALSE

CLIPS\>

 Portability Note

Because the precision of floating point numbers varies from one computer to another, it is possible for the numeric comparison functions to work correctly on one computer and incorrectly on another. In fact, you should be aware, even if code is not being ported, that roundoff error can cause erroneous results. For example, the following expression erroneously returns the symbol TRUE because both numbers are rounded up to 0.6666666666666666667.

CLIPS\> (= 0.66666666666666666666 0.66666666666666666667)

TRUE

CLIPS\>

### 12.1.14 Comparing Numbers for Inequality

The **\<\>** function returns the symbol **TRUE** if its first argument is not equal in value to all its subsequent arguments; otherwise, it returns the symbol **FALSE**. Note that **\<\>** compares only numeric values and will convert integers to floats when necessary for comparison.

Syntax

(\<\> \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (\<\> 3 3.0)

FALSE

CLIPS\> (\<\> 4 4.1)

TRUE

CLIPS\>

 Portability Note

See portability note in section 12.1.13.

 Usage Note

When comparing more than two arguments, a **\<\>** function call is not equivalent to an **=** function call within a **not** function call:

CLIPS\> (\<\> 3 3 4)

FALSE

CLIPS\> (not (= 3 3 4))

TRUE

CLIPS\>

### 12.1.15 Greater Than Comparison

The **\>** function returns the symbol **TRUE** if for all its arguments, argument n‑1 is greater than argument n; otherwise, it returns the symbol **FALSE**. Note that **\>** compares only numeric values and will convert integers to floats when necessary for comparison.

Syntax

(\> \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (\> 5 4 3)

TRUE

CLIPS\> (\> 5 3 4)

FALSE

CLIPS\>

 Portability Note

See portability note in section 12.1.13.

### 12.1.16 Greater Than or Equal Comparison

The **\>=** function returns the symbol **TRUE** if for all its arguments, argument n‑1 is greater than or equal to argument n; otherwise, it returns the symbol **FALSE**. Note that **\>=** compares only numeric values and will convert integers to floats when necessary for comparison.

Syntax

(\>= \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (\>= 5 5 3)

TRUE

CLIPS\> (\>= 5 3 5)

FALSE

CLIPS\>

 Portability Note

See portability note in section 12.1.13.

### 12.1.17 Less Than Comparison

The **\<** function returns the symbol **TRUE** if for all its arguments, argument n‑1 is less than argument n; otherwise it returns the symbol **FALSE**. Note that **\<** compares only numeric values and will convert integers to floats when necessary for comparison.

Syntax

(\< \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (\< 3 4 5)

TRUE

CLIPS\> (\< 3 5 4)

FALSE

CLIPS\>

 Portability Note

See portability note in section 12.1.13.

### 12.1.18 Less Than or Equal Comparison

The **\<=** function returns the symbol **TRUE** if for all its arguments, argument n‑1 is less than or equal to argument n; otherwise, it returns the symbol **FALSE**. Note that **\<=** compares only numeric values and will convert integers to floats when necessary for comparison.

Syntax

(\<= \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (\<= 3 5 5)

TRUE

CLIPS\> (\<= 5 3 5)

FALSE

CLIPS\>

 Portability Note

See portability note in section 12.1.13.

### 12.1.19 Boolean And

The **and** function returns the symbol **TRUE** if each of its arguments evaluates to the symbol **TRUE**; otherwise, it returns the symbol **FALSE**. Each argument of the function is evaluated from left to right. If any argument evaluates to the symbol **FALSE**, then the symbol **FALSE** is immediately returned by the function.

Syntax

(and \<expression\>+)

### 12.1.20 Boolean Or

The **or** function returns the symbol **TRUE** if any of its arguments evaluates to the symbol **TRUE**; otherwise, it returns the symbol **FALSE**. Each argument of the function is evaluated from left to right. If any argument evaluates to the symbol **TRUE**, then the symbol **TRUE** is immediately returned by the function.

Syntax

(or \<expression\>+)

### 12.1.21 Boolean Not

The **not** function returns the symbol **TRUE** if its argument evaluates to the symbol **FALSE**; otherwise it returns the symbol **FALSE**.

Syntax

(not \<expression\>)

## 12.2 Multifield Functions

The following functions operate on multifield values.

### 12.2.1 Creating Multifield Values

The **create\$** function appends any number of fields together to create a multifield value.

Syntax

(create\$ \<expression\>\*)

The return value of **create\$** is a multifield value regardless of the number or types of arguments (single‑field or multifield). Calling **create\$** with no arguments creates a multifield value of length zero.

Example

CLIPS (create\$ hammer drill saw screw pliers wrench)

(hammer drill saw screw pliers wrench)

CLIPS\> (create\$ (+ 3 4) (\* 2 3) (/ 8 4))

(7 6 2.0)

CLIPS\> (create\$)

()

CLIPS\>

### 12.2.2 Specifying an Element

The **nth\$** function will return a specified field from a multifield value.

Syntax

(nth\$ \<integer-expression\> \<multifield-expression\>)

The first argument should be an integer from 1 to the number of elements within the second argument. The symbol **nil** will be returned if the first argument is greater than the number of fields in the second argument.

Example

CLIPS\> (nth\$ 3 (create\$ a b c d e f g))

c

CLIPS\> (nth\$ 12 (create\$ a b c d e f g))

nil

CLIPS\>

### 12.2.3 Finding an Element

The **member\$** function determines whether a primitive value is contained in a multifield value.

Syntax

(member\$ \<expression\> \<multifield-expression\>)

If the first argument is a single field value and is one of the fields within the second argument, **member\$** will return the integer position of the field (from 1 to the length of the second argument). If the first argument is a multifield value and this value is embedded in the second argument, then the return value is a two field multifield value consisting of the starting and ending integer indices of the first argument within the second argument. If neither of these situations is satisfied, then the symbol **FALSE** is returned.

Example

CLIPS\> (member\$ blue (create\$ red 3 \"text\" 8.7 blue))

5

CLIPS\> (member\$ 4 (create\$ red 3 \"text\" 8.7 blue))

FALSE

CLIPS\> (member\$ (create\$ b c) (create\$ a b c d))

(2 3)

CLIPS\>

### 12.2.4 Comparing Multifield Values

The **subsetp** function checks if one multifield value is a subset of another (i.e., if all the fields in the first multifield value are also in the second multifield value).

Syntax

(subsetp \<multifield-expression\> \<multifield-expression\>)

If the first argument is a subset of the second argument, this function returns the symbol **TRUE**; otherwise, it returns the symbol **FALSE**. The order of the fields is not consi­dered. If the first argument is bound to a multifield of length zero, **subsetp** always returns the symbol **TRUE**.

Example

CLIPS\> (subsetp (create\$ hammer saw drill)

(create\$ hammer drill wrench pliers saw))

TRUE

CLIPS\> (subsetp (create\$ wrench crowbar)

(create\$ hammer drill wrench pliers saw))

FALSE

CLIPS\> (subsetp (create\$)

(create\$ hammer drill wrench pliers saw))

TRUE

CLIPS\> (subsetp (create\$ wrench crowbar)

(create\$))

FALSE

CLIPS\>

### 12.2.5 Deletion of Fields in Multifield Values

The **delete\$** function deletes the specified range from a multifield value.

Syntax

(delete\$ \<multifield-expression\>

\<begin-integer-expression\>

\<end-integer-expression\>)

The modified multifield value is returned, which is the same as \<multifield‑expression\> with the fields ranging from \<begin‑integer‑expression\> to \<end‑integer‑expression\> removed. To delete a single field, the begin range field should equal the end range field.

Example

CLIPS\> (delete\$ (create\$ hammer drill saw pliers wrench) 3 4)

(hammer drill wrench)

CLIPS\> (delete\$ (create\$ computer printer hard-disk) 1 1)

(printer hard-disk)

CLIPS\>

### 12.2.6 Creating Multifield Values from Strings.

The **explode\$** function constructs a multifield value from a string by using each field in a string as a field in a new multifield value.

Syntax

(explode\$ \<string-expression\>)

A new multifield value is created in which each delimited field in order in \<string‑expression\> is taken to be a field in the new multifield value that is returned. A string with no fields creates a multifield value of length zero. Fields other than symbols, strings, integer, floats, or instances names (such as parentheses or variables) are converted to symbols.

Example

CLIPS\> (explode\$ \"hammer drill saw screw\")

(hammer drill saw screw)

CLIPS\> (explode\$ \"1 2 abc 3 4 \\\"abc\\\" \\\"def\\\"\")

(1 2 abc 3 4 \"abc\" \"def\")

CLIPS\> (explode\$ \"?x \~ )\")

(?x \~ ))

CLIPS\>

### 12.2.7 Creating Strings from Multifield Values

The **implode\$** function creates a single string from a multifield value.

Syntax

(implode\$ \<multifield-expression\>)

Each field in \<multifield‑expression\> in order is concatenated into a string value with a single blank sepa­rating fields. The new string is returned.

Example

CLIPS\> (implode\$ (create\$ hammer drill screwdriver))

\"hammer drill screwdriver\"

CLIPS\> (implode\$ (create\$ 1 \"abc\" def \"ghi\" 2))

\"1 \"abc\" def \"ghi\" 2\"

CLIPS\> (implode\$ (create\$ \"abc def ghi\"))

\"\"abc def ghi\"\"

CLIPS\>

### 12.2.8 Extracting a Sub‑sequence from a Multifield Value

The **subseq\$** function extracts a specified range from a multifield value and returns a new mul­tifield value containing just the sub‑sequence.

Syntax

(subseq\$ \<multifield-value\>

\<begin-integer-expression\>

\<end-integer-expression\>)

The second and third arguments to the function are integers specifying the begin and end fields of the desired sub‑sequence in \<multifield‑expression\>.

Example

CLIPS\> (subseq\$ (create\$ hammer drill wrench pliers) 3 4)

(wrench pliers)

CLIPS\> (subseq\$ (create\$ 1 \"abc\" def \"ghi\" 2) 1 1)

\(1\)

CLIPS\>

### 12.2.9 Replacing Fields within a Multifield Value

The **replace\$** function replaces a range of field in a multifield value with a series of single‑field and/or multifield values and returns a new mul­tifield value containing the replacement values within the original multifield value.

Syntax

(replace\$ \<multifield-expression\>

\<begin-integer-expression\>

\<end-integer-expression\>

\<single-or-multi-field-expression\>+)

The \<begin‑integer‑expression\> to \<end‑integer‑expression\> argurments is the range of values to be replaced.

Example

CLIPS\> (replace\$ (create\$ drill wrench pliers) 3 3 machete)

(drill wrench machete)

CLIPS\> (replace\$ (create\$ a b c d) 2 3 x y (create\$ q r s))

(a x y q r s d)

CLIPS\>

### 12.2.10 Inserting Fields within a Multifield Value

The **insert\$** function inserts a series of single‑field and/or multifield values at a specified location in a multifield value with and returns a new mul­tifield value containing the inserted values within the original multifield value.

Syntax

(insert\$ \<multifield-expression\>

\<integer-expression\>

\<single-or-multi-field-expression\>+)

The \<integer‑expression\> argument is the location where the values are to be inserted. This value must be greater than or equal to 1. A value of 1 inserts the new value(s) at the beginning of the \<multifield‑expression\>. Any value greater than the length of the \<multifield‑expression\> appends the new values to the end of the \<multifield‑expression\>.

Example

CLIPS\> (insert\$ (create\$ a b c d) 1 x)

(x a b c d)

CLIPS\> (insert\$ (create\$ a b c d) 4 y z)

(a b c y z d)

CLIPS\> (insert\$ (create\$ a b c d) 5 (create\$ q r))

(a b c d q r)

CLIPS\>

### 12.2.11 Getting the First Field from a Multifield Value

The **first\$** function returns the first field of a multifield value as a multifield value

Syntax

(first\$ \<multifield-expression\>)

Example

CLIPS\> (first\$ (create\$ a b c))

\(a\)

CLIPS\> (first\$ (create\$))

()

CLIPS\>

### 12.2.12 Getting All but the First Field from a Multifield Value

The **rest\$** function returns all but the first field of a multifield value as a multifield value.

Syntax

(rest\$ \<multifield-expression\>)

Example

CLIPS\> (rest\$ (create\$ a b c))

(b c)

CLIPS\> (rest\$ (create\$))

()

CLIPS\>

### 12.2.13 Determining the Number of Fields in a Multifield Value

The **length\$** function returns an integer indicating the number of fields contained in a multifield value.

Syntax

(length\$ \<multifield-expression\>)

Example

CLIPS\> (length\$ (create\$ a b c d e f g))

7

CLIPS\>

### 12.2.14 Deleting Specific Values within a Multifield Value

The **delete-member\$** function deletes specific values contained within a multifield value and returns the modified multifield value.

Syntax

(delete-member\$ \<multifield-expression\> \<expression\>+)

The \<expression\>+ term is one or more values to be deleted from \<multifield-expression\>. If \<expression\> is a multifield value, the entire sequence must be contained within the first argument in the correct order.

Example

CLIPS\> (delete-member\$ (create\$ a b a c) b a)

\(c\)

CLIPS\> (delete-member\$ (create\$ a b c c b a) (create\$ b a))

(a b c c)

CLIPS\>

### 12.2.15 Replacing Specific Values within a Multifield Value

The **replace-member\$** function replaces specific values contained within a multifield value and returns the modified multifield value.

Syntax

(replace-member\$ \<multifield-expression\> \<substitute-expression\>

\<search-expression\>+)

Any \<search-expression\> value that is contained within \<multifield-expression\> is replaced by \<substitute-expression\>.

Example

CLIPS\> (replace-member\$ (create\$ a b a b) (create\$ a b a) a b)

(a b a a b a a b a a b a)

CLIPS\> (replace-member\$ (create\$ a b a b) (create\$ a b a) (create\$ a b))

(a b a a b a)

CLIPS\>

### 12.2.16 Creating the Union of Multifield Values

The **union\$** function creates a multifield value containing a single occurrence of each value contained within each of its multifield arguments.

Syntax

(union\$ \<multifield-expression\>\*)

Example

CLIPS\> (union\$ (create\$ a b b c) (create\$ d e e f))

(a b c d e f)

CLIPS\> (union\$)

()

CLIPS\>

### 12.2.17 Creating the Intersection of Multifield Values

The **intersection\$** function creates a multifield value containing a single occurrence of each value that is contained within all of its multifield arguments.

Syntax

(intersection\$ \<multifield-expression\>\*)

Example

CLIPS\> (intersection\$ (create\$ a b b c) (create\$ b c c e))

(b c)

CLIPS\> (intersection\$ (create\$ a b c) (create\$ d e f))

()

CLIPS\>

### 12.2.18 Creating the Difference of Multifield Values

The **difference\$** function creates a multifield value containing a single occurrence of each value that is contained within its first argument, but none of its subsequent multifield arguments.

Syntax

(difference\$ \<multifield-expression\>+)

Example

CLIPS\> (difference\$ (create\$ a b b c d) (create\$ a c))

(b d)

CLIPS\> (difference\$ (create\$ a b b c))

(a b c)

CLIPS\>

## 12.3 String Functions

The following functions perform operations that are related to strings.

### 12.3.1 String Concatenation

The **str‑cat** function will concatenates its arguments into a single string.

Syntax

(str-cat \<expression\>\*)

Each \<expression\> should be one of the following types: symbol, string, float, integer, or instance‑name.

Example

CLIPS\> (str-cat 2018 \"-\" 5 \"-\" 29)

\"2018-5-29\"

CLIPS\>

### 12.3.2 Symbol Concatenation

The **sym‑cat** function will concatenate its arguments into a single symbol. It is functionally identical to the str‑cat function with the exception that the returned value is a symbol and not a string.

Syntax

(sym-cat \<expression\>\*)

Each \<expression\> should be one of the following types: symbol, string, float, integer, or instance‑name.

### 12.3.3 Taking a String Apart

The **sub‑string** function will retrieve a portion of a string from another string.

Syntax

(sub-string \<integer-expression\> \<integer-expression\>

\<string-expression\>)

The first argument, counting from one, must be a number marking the begin­ning position in the string and the second argument must be a number marking the ending position in the string. If the first argument is greater than the second argument, the string **\"\"** is returned.

Example

CLIPS\> (sub-string 3 8 \"abcdefghijkl\")

\"cdefgh\"

CLIPS\>

### 12.3.4 Searching a String

The **str‑index** function will return the position of a string inside another string.

Syntax

(str-index \<lexeme-expression\> \<lexeme-expression\>)

The second argument is searched for the first occurrence of the first argument. The **str‑index** function re­turns the integer starting position, counting from one, of the first argument in the second argument; otherwise if the first argument is not contained in the second argument, the symbol **FALSE** is returned.

Example

CLIPS\> (str-index \"def\" \"abcdefghi\")

4

CLIPS\> (str-index \"qwerty\" \"qwertypoiuyt\")

1

CLIPS\> (str-index \"qwerty\" \"poiuytqwer\")

FALSE

CLIPS\>

### 12.3.5 Evaluating a Function within a String

The **eval** function evaluates the string as though it were entered at the Read-Eval-Print Loop (REPL).

Syntax

(eval \<string-or-symbol-expression\>)

The only argument is a string containing the command, constant, or local/global variable to be evaluated. NOTE: **eval** will not evaluate any of the construct definition forms (i.e., **defrule**, **deffacts**, etc.;). The return value is the result of the evaluation of the string if no errors occur; otherwise, the symbol **FALSE** is returned.

Example

CLIPS\> (bind ?y 3)

3

CLIPS\> (defglobal ?\*x\* = 4)

CLIPS\> (eval \"(+ 3 4)\")

7

CLIPS\> (eval \"(+ ?\*x\* ?y)\")

7

CLIPS\> (eval \"?\*x\*\")

4

CLIPS\> (eval \"?y\")

3

CLIPS\> (eval \"3\")

3

CLIPS\>

### 12.3.6 Evaluating a Construct within a String

The **build** function evaluates the string as though it were entered at the REPL.

Syntax

(build \<string-or-symbol-expression\>)

The only argument is the construct to be added. The return value is the symbol **TRUE** if the construct was successfully added; otherwise the symbol **FALSE** is returned.

The **build** function is not available for binary-load only or run‑time CLIPS configurations (see the *Advanced Programming Guide*).

Example

CLIPS\> (clear)

CLIPS\> (build \"(defrule hello =\> (println \\\"Hello\\\"))\")

TRUE

CLIPS\> (rules)

hello

For a total of 1 defrule.

CLIPS\> (run)

Hello

CLIPS\>

### 12.3.7 Converting a String to Uppercase

The **upcase** function will return a string or symbol with uppercase alphabetic characters.

Syntax

(upcase \<string-or-symbol-expression\>)

Example

CLIPS\> (upcase \"This is a test of upcase\")

\"THIS IS A TEST OF UPCASE\"

CLIPS\> (upcase A_Word_Test_for_Upcase)

A_WORD_TEST_FOR_UPCASE

CLIPS\>

### 12.3.8 Converting a String to Lowercase

The **lowcase** function will return a string or symbol with lowercase alphabetic characters.

Syntax

(lowcase \<string-or-symbol-expression\>)

Example

CLIPS\> (lowcase \"This is a test of lowcase\")

\"this is a test of lowcase\"

CLIPS\> (lowcase A_Word_Test_for_Lowcase)

a_word_test_for_lowcase

CLIPS\>

### 12.3.9 Comparing Two Strings

The **str‑compare** function will compare two strings lexicographically to determine their logical relationship (i.e., equal to, less than, greater than). The comparison is performed character‑by‑character until the strings are exhausted (implying equal strings) or un­equal characters are found. The positions of the unequal characters within the ASCII character set are used to determine the logical relationship of unequal strings.

Syntax

(str-compare \<string-or-symbol-expression\>

\<string-or-symbol-expression\>)

This function returns an integer representing the result of the comparison (0 if the strings are equal, -1 if the first argument is less than the second argument, and 1 if the first argument is greater than the second argument).

Example

CLIPS\> (str-compare \"string\" \"string\")

0

CLIPS\> (str-compare \"string1\" \"string2\")

-1

CLIPS\> (str-compare \"string2\" \"string1\")

1

CLIPS\>

### 12.3.10 Determining the Length of a String

The **str‑length** function returns the integer length of a string.

Syntax

(str-length \<string-or-symbol-expression\>)

Example

CLIPS\> (str-length \"abcd\")

4

CLIPS\> (str-length xyz)

3

CLIPS\>

### 12.3.11 Checking the Syntax of a Construct or Function Call within a String

The **check-syntax** function allows the text representation of a construct or function call to be checked for syntax and semantic errors.

Syntax

(check-syntax \<construct-or-function-string\>)

This function returns the symbol **FALSE** if there are no errors or warnings encountered parsing the construct or function call. The symbol **MISSING-LEFT-PARENTHESIS** is returned if the first token is not a left parenthesis. The symbol **EXTRANEOUS-INPUT-AFTER-LAST-PARENTHESIS** is returned if there are additional tokens after the closing right parenthesis of the construct or function call. If errors or warnings are encounted parsing, the a multifield of length two is returned. The first field of the multifield is a string containing the text of the error message (or the symbol **FALSE** if no errors were encountered). The second field of the multifield is a string containing the text of the warning message (or the symbol **FALSE** if no warnings were encountered).

Example

CLIPS\> (check-syntax \"(defrule good =\>)\")

FALSE

CLIPS\> (check-syntax \"(defrule bad (number 40000000000000000000) =\>)\")

(FALSE \"\[SCANNER1\] WARNING: Over or underflow of long long integer.

\")

CLIPS\> (check-syntax \"(defrule bad (3) =\>)\")

(\"

\[PRNTUTIL2\] Syntax Error: Check appropriate syntax for the first field of a pattern.

ERROR:

(defrule MAIN::bad

(3

\" FALSE)

CLIPS\>

### 12.3.12 Converting a String to a Field

The **string-to-field** function parses a string and converts its contents to a primitive data type.

Syntax

(string-to-field \<string-or-symbol-expression\>)

The only argument is the string to be parsed. Essentially calling **string-to-field** with its string argument is equivalent to calling the **read** function and manually typing the contents of the string argument or reading it from a file.

Example

CLIPS\> (string-to-field \"3.4\")

3.4

CLIPS\> (string-to-field \"a b\")

a

CLIPS\>

### 12.3.13 Replacing Portions of a String

The **str‑replace** function will replace all occurrences of a sequence of characters in a string with another sequence of characters.

Syntax

(str-replace \<lexeme-expression\> \<search-expression\> \<replace-expression\>)

All three arguments to this function are lexemes. Occurrences of the \<search-expression\> argument in the \<lexeme-expression\> argument are replaced with the \<replace-expression\> argument and the new string with replaced sequences is returned.

Example

CLIPS\> (str-replace \"abcdeabcde\" \"bcd\" \"xyz\")

\"axyzeaxyze\"

CLIPS\>

### 12.3.14 Determining the Byte Length of a String

The **str‑byte-length**‑ function returns an integer indicating the number of bytes used to represent a string. For strings containing only ASCII characters, the return value of the **str**‑**byte-length** function will be the same as that returned by the **str-length** function. Non-ASCII UTF-8 characters require 2 to 4 bytes to represent.

Syntax

(str-byte-length \<string-or-symbol-expression\>)

Example

CLIPS\> (str-length \"é\")

1

CLIPS\> (str-byte-length \"é\")

2

CLIPS\>

## 12.4 I/O Functions

CLIPS uses a system called I/O routers which provide a layered mechanism for handling I/O requests. The router system allows multiple sources to intercept and/or handle a single I/O request. For example, the **batch** command redirects input requests from the REPL to a router which reads input from a file; the **dribble-on** command intercepts output to the REPL and directs it to a router which writes output to a file; and the CLIPS Integrated Development Environments for macOS, Windows, and Java use routers to intercept all console I/O for the REPL and redirect it to the REPL window for the IDE. CLIPS programs do not directly create routers. Instead routers are indirectly created by calling system or user defined functions, or by other application code in which CLIPS has been embedded (such as an IDE). The C API for creating routers is described in the *Advanced Programming Guide*.

Logical names play a crucial role in I/O routers, providing a way to reference I/O devices without needing to understand their implementation details. In CLIPS, many functions accept logical names as arguments. These names can be symbols, numbers, or strings and have a global scope. This means that a logical name used to open a file in one rule can also be used by another rule to read from or close the same file.

Several logical names are predefined by CLIPS, as shown in the following table.

+----------+-----------------------------------------------------------------------------------------------------------------------------+
| **Name** | **Description**                                                                                                             |
+:========:+=============================================================================================================================+
| stdin    | > The default for all user input. The read and readline functions read from stdin if t is specified as the logical name.    |
+----------+-----------------------------------------------------------------------------------------------------------------------------+
| stdout   | > The default for all user output. The printout and format functions write to stdout if t is specified as the logical name. |
+----------+-----------------------------------------------------------------------------------------------------------------------------+
| werror   | > All error messages are sent to this logical name.                                                                         |
+----------+-----------------------------------------------------------------------------------------------------------------------------+
| wwarning | > All warning messages are sent to this logical name.                                                                       |
+----------+-----------------------------------------------------------------------------------------------------------------------------+

### 12.4.1 Opening a File

The **open** function allows a user to open a file and associate a logical name with it. This function takes three arguments: (1) the name of the file to be opened; (2) the logical name which will be used by other CLIPS I/O functions to ac­cess the file; and (3) an optional mode specifier. The mode specifier must be one of the strings from the following table.

+----------+---------------------------------------------------------+
| **Mode** | > **Means**                                             |
+:========:+=========================================================+
| r        | > Character read access. Specified file must exist.     |
+----------+---------------------------------------------------------+
| w        | > Character write access. Existing content overwritten. |
+----------+---------------------------------------------------------+
| a        | > Character write access. Writes append to end of file. |
+----------+---------------------------------------------------------+
| r+       | > Read and write access. Specified file must exist.     |
+----------+---------------------------------------------------------+
| w+       | > Read and write access. Existing content overwritten.  |
+----------+---------------------------------------------------------+
| a+       | > Read and write access. Writes append to end of file.  |
+----------+---------------------------------------------------------+

Binary character mode can also be specified by appending a 'b' at the end of the mode or immediately preceding the '+' character (e.g. rb, rb+, or r+b). If the mode is not specified, it defaults to character read access.

Syntax

(open \<file-name\> \<logical-name\> \[\<mode\>\])

The \<file‑name\> must either be a string or symbol and may include directory speci­fiers. If a string is used, the backslash (\\) and any other special characters that are part of \<file‑name\> must be escaped with a backslash. Since logical names are global in scope, the \<logical-name\> specified cannot already be associated with another open file. The **open** function returns the symbol **TRUE** if it was successful; otherwise, the symbol **FALSE** is returned.

Example

CLIPS\> (open \"data.txt\" data \"w\")

TRUE

CLIPS\> (close)

TRUE

CLIPS\> (open \"data.txt\" data)

TRUE

CLIPS\> (close)

TRUE

CLIPS\>

### 12.4.2 Closing a File

The **close** function closes a file stream previously opened with the **open** com­mand. The file is specified by a logical name previously attached to the desired stream.

Syntax

(close \[\<logical-name\>\])

If **close** is called without arguments, all open files will be closed. CLIPS will attempt to close all open files when the **exit** command is executed, however, programs should explicitly close files before exiting to ensure that output is saved. The **close** function returns the symbol **TRUE** if any files were successfully closed; otherwise the symbol **FALSE** is returned.

Example

CLIPS\> (open \"data.txt\" data \"w\")

TRUE

CLIPS\> (close data)

TRUE

CLIPS\> (close data)

FALSE

CLIPS\> (open \"data.txt\" data)

TRUE

CLIPS\> (close)

TRUE

CLIPS\> (close)

FALSE

CLIPS\>

### 12.4.3 Printing

The **printout** function allows output to a destination associated with a logical name. The logical name *must* be specified and the destination must have been prepared previously for output (e.g., a file must be opened first). The logical name **t** may be used instead of **stdout** to send output to standard output (the REPL). If the logical name **nil** is used, the **printout** function does nothing; if the logical name is variable rather than a constant, this allows you to easily disable output by assigning the value **nil** to the variable.

The **print** and **println** functions are variants of the **printout** function. Both function always direct output to **stdout** and the **println** function appends a carriage return/line feed after printing all of its arguments.

Syntax

(printout \<logical-name\> \<expression\>\*)

(print \<expression\>\*)

(println \<expression\>\*)

Any number of expressions may be placed in a **printout** call. Each expression is evaluated and printed (with no spaces added between each printed expression). The symbol **crlf** used as an \<expression\> will force a carriage return/newline and may be placed anywhere in the list of expressions to be printed. Similarly, the symbols **tab**, **vtab**, **ff**, **cr**, and **lf** will print respectively a tab, a vertical tab, a form feed, a carriage return, and a line feed. The appearance of these special symbols may vary from one operating system to another. The printout function strips quotation marks from around strings when it prints them. This function has no return value.

Example

CLIPS\> (printout t \"Hello World!\" crlf)

Hello World!

CLIPS\> (println \"Hello World!\")

Hello World!

CLIPS\> (print \"Hello World!\" crlf)

Hello World!

CLIPS\> (open \"data.txt\" data \"w\")

TRUE

CLIPS\> (printout data \"red green\")

CLIPS\> (close)

TRUE

CLIPS\>

### 12.4.4 Reading a Single Field

The **read** function allows the input of a single field from a source associated with a logical name. All of the stan­dard restrictions for a field (e.g., multiple symbols must be embedded within quotes) apply.

Syntax

(read \[\<logical-name\>\])

The \<logical‑name\> term is an optional parameter. If specified, **read** requests input from the source associated with the logical name. If the \<logical‑name\> parameter is **t** or unspeci­fied, the function will request input from **stdin**. All the delimiters defined in section 2.3.1 can be used as delimiters. The **read** function always returns a primitive data type. Spaces, carriage returns, and tabs only act as delimiters and are not contained within the return value (unless these characters are included within double quotes as part of a string). If the end of file is encountered while reading, **read** will return the symbol **EOF** and the **get-error** function (if called) will return the symbol **EOF**. If errors are encountered while reading, the symbol **FALSE** will be returned and the **get-error** function (if called) will return an error code (other than the symbol **FALSE**).

Example 1

CLIPS\> (open \"data.txt\" data \"w\")

TRUE

CLIPS\> (printout data \"red green\")

CLIPS\> (close)

TRUE

CLIPS\> (open \"data.txt\" data)

TRUE

CLIPS\> (read data)

red

CLIPS\> (get-error)

FALSE

CLIPS\> (read data)

green

CLIPS\> (read data)

EOF

CLIPS\> (get-error)

EOF

CLIPS\> (close)

TRUE

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(defrule get-name

=\>

(print \"What is your first name? \")

(bind ?first (read))

(print \"What is your last name? \")

(bind ?last (read))

(assert (name ?first ?last)))

CLIPS\>

(defrule print-name

(name ?first ?last)

=\>

(println \"Hello \" ?first \" \" ?last \".\"))

CLIPS\> (run)

What is your first name? Jack

What is your last name? Smith

Hello Jack Smith.

CLIPS\>

### 12.4.5 Reading an Entire Line

The **readline** function is similar to the **read** function, but it reads an entire line of input instead of a single field. Normally, **read** will stop when it encounters a delimiter. The **readline** function only stops when it encounters a carriage return, a semicolon, or the end of file. Any tabs or spaces in the input are returned by **readline** as a part of the string. The **readline** function returns a string.

Syntax

(readline \[\<logical-name\>\])

The \<logical‑name\> term is an optional parameter. If specified, **readline** requests input from the source associated with the logical name. If the \<logical‑name\> parameter is **t** or unspeci­fied, the function will request input from **stdin**. If an end of file (EOF) is encountered while reading, **readline** will return the symbol **EOF**. If errors are encountered while reading, the symbol **FALSE** will be returned.

Example 1

CLIPS\> (open \"data.txt\" data \"w\")

TRUE

CLIPS\> (printout data \"red green\")

CLIPS\> (close)

TRUE

CLIPS\> (open \"data.txt\" data)

TRUE

CLIPS\> (readline data)

\"red green\"

CLIPS\> (readline data)

EOF

CLIPS\> (close)

TRUE

CLIPS\>

Example 2

CLIPS\> (clear)

CLIPS\>

(defrule get-name

=\>

(print \"What is your name? \")

(bind ?name (readline))

(assert (name ?name)))

CLIPS\>

(defrule print-name

(name ?name)

=\>

(println \"Hello \" ?name \".\"))

CLIPS\> (run)

What is your name? Jack Smith

Hello Jack Smith.

CLIPS\>

### 12.4.6 Formatted Printing

The **format** function allows formatted output to be sent to a destination associated with a logical name. It can be used in place of **printout** when special formatting of out­put information is desired. The **format** function is simi­lar to the **printf** function in C. The **format** function always returns a string containing the formatted output. A logical name of **nil** may be used when the formatted return string is desired without sending output to a destination.

Syntax

(format \<logical-name\> \<string-expression\> \<expression\>\*)

If the symbol **t** is specified as the \<logical-name\> parameter, output is sent to **stdout**. The second argument to format, called the control string, specifies how the output should be formatted. Subsequent arguments to format (the parameter list for the control string) are the expressions which are to be out­put as indicated by the control string. The **format** function does not allow expressions returning multifield values to be included in the parameter list.

The control string consists of text and format flags. Text is output exactly as speci­fied, and format flags describe how each parameter in the parameter list is to be for­matted. The first format flag corresponds to the first value in the parameter list, the second flag corresponds to the second value, etc. The format flags must be preceded by a percent sign (%) and use the general format shown following.

%‑M.Nx

The x placeholder is one of the flags listed in the following table, the minus sign is an optional justification flag, and M and N are optional parameters which specify the field width and the precision argument (which varies in meaning based on the format flag). If M is used, at least M characters will be output. If more than M characters are required to display the value, **format** expands the field as needed. If M starts with a 0 (e.g., %07d), a zero is used as the pad character; oth­er­wise, spaces are used. If N is not specified, it defaults to six digits for floating‑point numbers. If a minus sign is included before the M, the value will be left justified; oth­erwise the value is right justified.

+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Format Flag** | > **Meaning**                                                                                                                                                                                                       |
+:===============:+=====================================================================================================================================================================================================================+
| c               | > Display parameter as a single character.                                                                                                                                                                          |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| d               | > Display parameter as a long long integer. (The N specifier is the minimum number of digits to be printed.)                                                                                                        |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| f               | > Display parameter as a floating‑point number (The N specifier is the number of digits following the decimal point).                                                                                               |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| e               | > Display parameter as a floating‑point using power of 10 notation (The N specifier is the number of digits following the decimal point).                                                                           |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| g               | > Display parameter in the most general format, whichever is shorter (the N specifier is the number of significant digits to be printed).                                                                           |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| o               | > Display parameter as an unsigned octal number. (The N specifier is the minimum number of digits to be printed.)                                                                                                   |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| x               | > Display parameter as an unsigned hexadecimal number. (The N specifier is the minimum number of digits to be printed.)                                                                                             |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| s               | > Display parameter as a string. Strings will have the leading and trailing quotes stripped. (The N specifier indicates the maximum number of characters to be printed. Zero cannot be used for the pad character.) |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| n               | > Put a new line in the output.                                                                                                                                                                                     |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| r               | > Put a carriage return in the output.                                                                                                                                                                              |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| \%              | > Put the percent character in the output.                                                                                                                                                                          |
+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Example

CLIPS\> (format t \"Hello World!%n\")

Hello World!

\"Hello World!

\"

CLIPS\> (format nil \"Integer: \|%d\|\" 12)

\"Integer: \|12\|\"

CLIPS\> (format nil \"Integer: \|%4d\|\" 12)

\"Integer: \| 12\|\"

CLIPS\> (format nil \"Integer: \|%-04d\|\" 12)

\"Integer: \|12 \|\"

CLIPS\> (format nil \"Integer: \|%6.4d\|\" 12)

\"Integer: \| 0012\|\"

CLIPS\> (format nil \"Float: \|%f\|\" 12.01)

\"Float: \|12.010000\|\"

CLIPS\> (format nil \"Float: \|%7.2f\| \"12.01)

\"Float: \| 12.01\| \"

CLIPS\> (format nil \"Test: \|%e\|\" 12.01)

\"Test: \|1.201000e+01\|\"

CLIPS\> (format nil \"Test: \|%7.2e\|\" 12.01)

\"Test: \|1.20e+01\|\"

CLIPS\> (format nil \"General: \|%g\|\" 1234567890)

\"General: \|1.23457e+09\|\"

CLIPS\> (format nil \"General: \|%6.3g\|\" 1234567890)

\"General: \|1.23e+09\|\"

CLIPS\> (format nil \"Hexadecimal: \|%x\|\" 12)

\"Hexadecimal: \|c\|\"

CLIPS\> (format nil \"Octal: \|%o\|\" 12)

\"Octal: \|14\|\"

CLIPS\> (format nil \"Symbols: \|%s\| \|%s\|\" value-a1 capacity)

\"Symbols: \|value-a1\| \|capacity\|\"

CLIPS\>

 Portability Note

The **format** function is implemented using the ANSI C function **sprintf**.

### 12.4.7 Renaming a File

The **rename** function is used to change the name of a file.

Syntax

(rename \<old-file-name\> \<new-file-name\>)

Both \<old‑file‑name\> and \<new‑file‑name\> must either be a string or symbol and may include directory speci­fiers. If a string is used, the backslash (\\) and any other special characters that are part of either \<old‑file‑name\> or \<new‑file‑name\> must be escaped with a backslash. The **rename** function returns the symbol **TRUE** if it was successful; otherwise, the symbol **FALSE** is returned.

 Portability Note

The **rename** function is implemented using the ANSI C function **rename**.

### 12.4.8 Removing a File

The **remove** function is used to delete a file.

Syntax

(remove \<file-name\>)

The \<file‑name\> must either be a string or symbol and may include directory speci­fiers. If a string is used, the backslash (\\) and any other special characters that are part of \<file‑name\> must be escaped with a backslash. The **remove** function returns the symbol **TRUE** if it was successful; otherwise, the symbol **FALSE** is returned.

 Portability Note

The **remove** function is implemented using the ANSI C function **remove**.

### 12.4.9 Reading a Character

The **get-char** function allows a single character to be retrieved from an input source.

Syntax

(get-char \[\<logical-name\>\])

The \<logical‑name\> term is an optional parameter. If specified, **get-char** tries to retrieve a character from the specified logical file name. If \<logical‑name\> is the symbol **t** or is not speci­fied, the function will read from **stdin**. The return value is the integer ASCII value of the character retrieved. The integer **-1** is returned if the end of file is encountered while retrieving a character.

Example

CLIPS\> (open data.txt data \"w\")

TRUE

CLIPS\> (printout data \"ABC\" crlf)

CLIPS\> (close data)

TRUE

CLIPS\> (open data.txt data)

TRUE

CLIPS\> (get-char data)

65

CLIPS\> (format nil \"%c\" (get-char data))

\"B\"

CLIPS\> (get-char data)

67

CLIPS\> (get-char data)

10

CLIPS\> (get-char data)

-1

CLIPS\>

(progn (print \"Press any character to continue\...\")

(get-char t))

Press any character to continue\...

13

CLIPS\> (close)

TRUE

CLIPS\>

### 12.4.10 Unreading a Character

The **unget-char** function allows a single character to be returned to an input source.

Syntax

(unget-char \[\<logical-name\>\] \<character\>)

The \<logical‑name\> term is an optional parameter and \<character\> is an integer ASCII value of a character. If \<logical-name\> is specified, **unget-char** tries to return \<character\> to the input source associated with the logical name. If \<logical‑name\> is the symbol **t** or is not speci­fied, the function will return the character to **stdin**. If successful, the return value is the integer ASCII value of the character returned; otherwise, the integer **-1** is returnd.

Example

CLIPS\> (open data.txt data \"w\")

TRUE

CLIPS\> (printout data \"ABC\" crlf)

CLIPS\> (close data)

TRUE

CLIPS\> (open data.txt data)

TRUE

CLIPS\> (get-char data)

65

CLIPS\> (unget-char data 65)

65

CLIPS\> (get-char data)

65

CLIPS\> (get-char data)

66

CLIPS\> (unget-char data 68)

68

CLIPS\> (get-char data)

68

CLIPS\> (get-char data)

67

CLIPS\> (close)

TRUE

CLIPS\>

### 12.4.11 Reading a Number

The **read-number** function allows input of a single number using the localized format (if one has been specified using the **set-locale**[]{.indexref entry="set-locale"} function). If a localized format has not been specified, then the C format for a number is used.

Syntax

(read-number \[\<logical-name\>\])

The \<logical‑name\> term is an optional parameter. If specified, **read-number** attempts to read from the source associated with the logical file name. If \<logical‑name\> is the symbol **t** or is not speci­fied, the function will read from **stdin**. If a number is successfully parsed, the **read-number** function will return either an integer (if the number contained just a sign and digits) or a float (if the number contained the localized decimal point character or an exponent). If an end of file is encountered while reading, **read-number** will return the symbol **EOF**. If errors are encountered while reading, the symbol **FALSE** is returned.

Example

CLIPS\> (read-number)

34

34

CLIPS\> (read-number)

34.0

34.0

CLIPS\> (read-number)

8x8

FALSE

CLIPS\>

### 12.4.12 Setting the Locale

The **set-locale** function allows the locale to be specified which affects the numeric format behavior of the **format**[]{.indexref entry="format"} and **read-number**[]{.indexref entry="read-number"} functions. Before a number is printed by the **format** function or is parsed by the **read-number** function, the locale is temporarily changed to the last value specified to the **set-locale** function (or the default C locale if no value was previously specified).

Syntax

(set-locale \[\<locale-string\>\])

The optional parameter \<locale-string\> is a string containing the new locale to be used by the **format** and **read‑number** functions. If \<local-string\> is specified, then the value of the previous locale is returned. If \<locale-string\> is not specified, then the value of the current locale is returned. A \<locale-string\> value of **\"\"** uses the native locale (and the specification of this locale is dependent on the environment in which CLIPS is run). A \<locale-string\> of **\"C\"** specifies the standard C locale (which is the default).

Example

CLIPS\> (set-locale)

C

CLIPS\> (read-number)

12.1

12.1

CLIPS\> (read-number)

12,1

FALSE

CLIPS\> (format nil \"%f\" 12.1)

\"12.100000\"

CLIPS\> (set-locale \"de_DE\") ; macOS

C

CLIPS\> (read-number)

12.1

FALSE

CLIPS\> (read-number)

12,1

12.1

CLIPS\> (format nil \"%f\" 12.1)

\"12,100000\"

CLIPS\> (set-locale)

\"de_DE\"

CLIPS\> (set-locale \"C\")

\"de_DE\"

CLIPS\>

 Portability Note

The CLIPS **set-locale** function uses the ANSI C function **setlocale** to temporarily change the locale. The value used to set a specific local can vary. For example, in Windows the \<local-string\> for Germany is "DE" and in macOS, the \<locale-string\> for Germany is "de_DE".

### 12.4.13 Flushing Output

The **flush** function writes pending output to a file stream previously opened with the **open** com­mand. The file is specified by a logical name previously associated with the file stream. Flushed files remain open. Typically output does not need to be flushed since closing the file with the **close** com­mand will flush pending output.

Syntax

(flush \[\<logical-name\>\])

If **flush** is called without arguments, all open files will be flushed. The **flush** function returns the symbol **TRUE** if any files were successfully flushed; otherwise, the symbol **FALSE** is returned.

 Portability Note

The **flush** function uses the ANSI C function **fflush** as a base.

### 12.4.14 Rewinding the File Position

The **rewind** function sets the position in a file stream previously opened with the **open** com­mand to the beginning of the file. The file is specified by a logical name previously associated with the file stream.

Syntax

(rewind \<logical-name\>)

The **rewind** function returns the symbol **TRUE** if successful; otherwise, the symbol **FALSE** is returned.

 Portability Note

The **rewind** function uses the ANSI C function **rewind** as a base.

### 12.4.15 Retrieving the File Position

The **tell** function returns the current position in a file stream previously opened with the **open** command. The file is specified by a logical name previously associated with the file stream.

Syntax

(tell \<logical-name\>)

The **tell** function returns the integer file position if successful; otherwise, the symbol **FALSE** is returned.

 Portability Note

The **tell** function uses the ANSI C function **ftell** as a base.

### 12.4.16 Setting the File Position

The **seek** function sets the current position in a file stream previously opened with the **open** command. The file is specified by a logical name previously associated with the file stream.

Syntax

(seek \<logical-name\> \<offset\> \<relative-position)

The \<offset\> argument is an integer value and the \<relative-position\> argument is one of the symbols **seek-set**, **seek-cur**, or **seek-end**. If **seek-set** is specified, the file position is set based on the offset relative to the beginning of the file. If **seek-cur** is specified, the file position is set based on the offset relative to the current positiion in the file. If **seek-end** is specified, the file position is set based on the offset relative to the end of the file. The **seek** function returns the symbol **TRUE** if the file position was successfully set; otherwise the symbol **FALSE** is returned.

 Portability Note

The **seek** function uses the ANSI C function **fseek** as a base.

### 12.4.17 Changing the Current Directory

The **chdir** function changes the current directory.

Syntax

(chdir \[\<path\>\])

The optional \<path\> argument is a string or symbol value containing the path to the new directory (either absolute or relative). If the \<path\> argument is unspecified, then the function returns the symbol **TRUE** if the system supports the **chdir** function; otherwise, the symbol **FALSE** is returned. If the \<path\> argument is specified, then the function returns the symbol **TRUE** if the directory was successfully changed; otherwise, the symbol **FALSE** is returned.

 Portability Note

The **chdir** function uses the C function **chdir** as a base on macOS and Linux and the C function **\_wchdir** as a base on Windows. This function is not supported on other platforms.

### 12.4.18 Opening a File Temporarily to Perform Actions

The **with-open-file** function allows users to temporarily open a file, perform actions, and automatically close it once those actions are completed. The arguments for opening the file are the same as those used with the **open** function.

Syntax

(with-open-file (\<file-name\> \<logical-name\> \[\<mode\>\]) \<expression\>\*)

The \<file‑name\> must be either a string or a symbol and may include directory speci­fiers. If a string is used, the backslash (\\) and any other special characters within \<file‑name\> must be escaped with a backslash. The logical name should not be associated with another open file. The allowed values for \<mode\> are the same as those for the **open** function: r, w, a, r+, w+, a+, rb, wb, ab, wb+, ab+, w+b, and a+b. The **with-open-file** function returns the symbol **TRUE** if the file was opened successfully, the actions were performed without error, and the file was successfully closed. Otherwise, the symbol **FALSE** is returned.

Example

CLIPS\> (clear)

CLIPS\>

(with-open-file (data.txt data \"w\")

(printout data \"Hello World\"))

TRUE

CLIPS\>

(with-open-file (data.txt data)

(println (readline data)))

Hello World

TRUE

CLIPS\>

## 12.5 Math Functions

CLIPS provides numerous functions for mathematical computa­tions. They are split into two sets: a set of standard math functions and a set of extended math functions.

The standard math functions are listed below. These func­tions should be used only on numeric arguments. An error message will be printed if a string argument is passed to a math function.

### 12.5.1 Addition

The **+** function returns the sum of its arguments. Each of its arguments should be a numeric expression. Addition is performed using the type of the arguments provided unless mixed mode arguments (integer and float) are used. In this case, the function return value and integer arguments are converted to floats after the first float argument has been encountered. This function returns a float if any of its arguments is a float; otherwise, it returns an integer.

Syntax

(+ \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (+ 2 3 4)

9

CLIPS\> (+ 2 3.0 5)

10.0

CLIPS\> (+ 3.1 4.7)

7.8

CLIPS\>

### 12.5.2 Subtraction

The **‑**‑ function returns the value of the first argument minus the sum of all subsequent arguments. Each of its arguments should be a numeric expression. Subtraction is performed using the type of the arguments provided unless mixed mode arguments (integer and float) are used. In this case, the function return value and integer arguments are converted to floats after the first float argument has been encountered. This function returns a float if any of its arguments is a float; otherwise, it returns an integer.

Syntax

(- \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (- 12 3 4)

5

CLIPS\> (- 12 3.0 5)

4.0

CLIPS\> (- 4.7 3.1)

1.6

CLIPS\>

### 12.5.3 Multiplication

The **\*** function returns the product of its arguments. Each of its arguments should be a numeric expression. Multiplication is performed using the type of the arguments provided unless mixed mode arguments (integer and float) are used. In this case, the function return value and integer arguments are converted to floats after the first float argument has been encountered. This function returns a float if any of its arguments is a float; otherwise, it returns an integer.

Syntax

(\* \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (\* 2 3 4)

24

CLIPS\> (\* 2 3.0 5)

30.0

CLIPS\> (\* 3.1 4.7)

14.57

CLIPS\>

### 12.5.4 Division

The **/** function returns the value of the first argument divided by each of the subsequent arguments. Each of its arguments should be a numeric expression. Each argument is *automatically converted* to a float and floating point division is performed. This function returns a float.

Syntax

(/ \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (/ 4 2)

2.0

CLIPS\> (/ 4.0 2.0)

2.0

CLIPS\> (/ 24 3 4)

2.0

CLIPS\>

### 12.5.5 Integer Division

The **div** function returns the value of the first argument divided by each of the subsequent arguments. Each of its arguments should be a numeric expression. Each argument is *automatically converted* to an integer and integer division is performed. This function returns an integer.

Syntax

(div \<numeric-expression\> \<numeric-expression\>+)

Example

CLIPS\> (div 4 2)

2

CLIPS\> (div 5 2)

2

CLIPS\> (div 33 2 3 5)

1

CLIPS\>

### 12.5.6 Maximum Numeric Value

The **max** function returns the value of its largest numeric argument. Each of its arguments should be a numeric expression. When necessary, integers are temporarily converted to floats for comparison. The return value will either be integer or float (depending upon the type of the largest argument).

Syntax

(max \<numeric-expression\>+)

Example

CLIPS\> (max 3.0 4 2.0)

4

CLIPS\>

### 12.5.7 Minimum Numeric Value

The **min** function returns the value of its smallest numeric argument. Each of its arguments should be a numeric expression. When necessary, integers are temporarily converted to floats for comparison. The return value will either be integer or float (depending upon the type of the smallest argument).

Syntax

(min \<numeric-expression\>+)

Example

CLIPS\> (min 4 0.1 -2.3)

-2.3

CLIPS\>

### 12.5.8 Absolute Value

The **abs** function returns the absolute value of its only argument (which should be a numeric expression). The return value will either be integer or float (depending upon the type the argument).

Syntax

(abs \<numeric-expression\>)

Example

CLIPS\> (abs 4.0)

4.0

CLIPS\> (abs -2)

2

CLIPS\>

### 12.5.9 Convert To Float

The **float** function converts its only argument (which should be a numeric expression) to type float and returns this value.

Syntax

(float \<numeric-expression\>)

Example

CLIPS\> (float 4.0)

4.0

CLIPS\> (float -2)

-2.0

CLIPS\>

### 12.5.10 Convert To Integer

The **integer** function converts its only argument (which should be a numeric expression) to type integer and returns this value.

Syntax

(integer \<numeric-expression\>)

Example

CLIPS\> (integer 4.0)

4

CLIPS\> (integer -2)

-2

CLIPS\>

### 12.5.11 Trigonometric Functions

The following trigonometric functions take one numeric argument and return a floating‑point number. The argument is expected to be in radians.

+-----------------------------------+--------------------------------------------+
|   -----------------------------   |   ---------------------------------------- |
|    **Function**   **Returns**     |    **Function**         **Returns**        |
|   -------------- --------------   |   -------------- ------------------------- |
|        acos        arccosine      |       acosh        hyperbolic arccosine    |
|                                   |                                            |
|        acot       arccotangent    |       acoth       hyperbolic arccotangent  |
|                                   |                                            |
|        acsc       arccosecant     |       acsch       hyperbolic arccosecant   |
|                                   |                                            |
|        asec        arcsecant      |       asech        hyperbolic arcsecant    |
|                                   |                                            |
|        asin         arcsine       |       asinh         hyperbolic arcsine     |
|                                   |                                            |
|        atan        arctangent     |       atanh        hyperbolic arctangent   |
|                                   |                                            |
|        cos           cosine       |        cosh          hyperbolic cosine     |
|                                   |                                            |
|        cot         cotangent      |        coth        hyperbolic cotangent    |
|                                   |                                            |
|        csc          cosecant      |        csch         hyperbolic cosecant    |
|                                   |                                            |
|        sec           secant       |        sech          hyperbolic secant     |
|                                   |                                            |
|        sin            sine        |        sinh           hyperbolic sine      |
|                                   |                                            |
|        tan          tangent       |        tanh         hyperbolic tangent     |
|   -----------------------------   |   ---------------------------------------- |
+===================================+============================================+

Example

CLIPS\> (cos 0)

1.0

CLIPS\> (acos 1.0)

0.0

CLIPS\>

#### 12.5.11.1 Two Argument Arctangent

The **atan2** function returns the arctangent of the value y/x where the arguments represent the point (x,y) in a Cartesian coordinate system.

Syntax

(atan2 \<y-numeric-expression\> \<x-numeric-expression\>)

Example

CLIPS\> (atan -1)

-0.785398163397448

CLIPS\> (atan2 1 -1)

2.35619449019234

CLIPS\> (atan2 -1 1)

-0.785398163397448

CLIPS\>

### 12.5.12 Convert From Degrees to Grads

The **deg‑grad** function converts its only argument (which should be a numeric expression) from units of degrees to units of grads (360 degrees = 400 grads). The return value of this function is a float.

Syntax

(deg-grad \<numeric-expression\>)

Example

CLIPS\> (deg-grad 90)

100.0

CLIPS\>

### 12.5.13 Convert From Degrees to Radians

The **deg‑rad** function converts its only argument (which should be a numeric expression) from units of degrees to units of radians (360 degrees = 2π radians). The return value of this function is a float.

Syntax

(deg-rad \<numeric-expression\>)

Example

CLIPS\> (deg-rad 180)

3.141592653589793

CLIPS\>

### 12.5.14 Convert From Grads to Degrees

The **grad‑deg** function converts its only argument (which should be a numeric expression) from units of grads to units of degrees (360 degrees = 400 grads). The return value of this function is a float.

Syntax

(grad-deg \<numeric-expression\>)

Example

CLIPS\> (grad-deg 100)

90.0

CLIPS\>

### 12.5.15 Convert From Radians to Degrees 

The **rad‑deg** function converts its only argument (which should be a numeric expression) from units of radians to units of degrees (360 degrees = 2π radians). The return value of this function is a float.

Syntax

(rad-deg \<numeric-expression\>)

Example

CLIPS\> (rad-deg 3.141592653589793)

180.0

CLIPS\>

### 12.5.16 Return the Value of π

The **pi** function returns the value of π (3.141592653589793\...) as a float.

Syntax

(pi)

Example

CLIPS\> (pi)

3.141592653589793

CLIPS\>

### 12.5.17 Square Root

The **sqrt** function returns the square root of its only argument (which should be a numeric expression) as a float.

Syntax

(sqrt \<numeric-expression\>)

Example

CLIPS\> (sqrt 9)

3.0

CLIPS\>

### 12.5.18 Power

The **\*\*** function raises its first argument to the power of its second argument and returns this value as a float.

Syntax

(\*\* \<numeric-expression\> \<numeric-expression\>)

Example

CLIPS\> (\*\* 3 2)

9.0

CLIPS\>

### 12.5.19 Exponential

The **exp** function raises the value e (the base of the natural system of logarithms, having a value of approximately 2.718\...) to the power specified by its only argument and returns this value as a float.

Syntax

(exp \<numeric-expression\>)

Example

CLIPS\> (exp 1)

2.718281828459045

CLIPS\>

### 12.5.20 Logarithm

Given n (the only argument) and the value e is the base of the natural system of logarithms, the **log** function returns the float value x such that the following equation is satisfied:

n = ex

Syntax

(log \<numeric-expression\>)

Example

CLIPS\> (log 2.718281828459045)

1.0

CLIPS\>

### 12.5.21 Logarithm Base 10

Given n (the only argument), the **log10** function returns the float value x such that the following equation is satisfied:

n = 10x

Syntax

(log10 \<numeric-expression\>)

Example

CLIPS\> (log10 100)

2.0

CLIPS\>

### 12.5.22 Round

The **round** function rounds its only argument (which should be a numeric expression) toward the closest integer. If the argument is exactly between two integers, it is rounded away from zero). The return value of this function is an integer.

Syntax

(round \<numeric-expression\>)

Example

CLIPS\> (round 3.6)

4

CLIPS\>

### 12.5.23 Modulus

The **mod** function returns the remainder of the result of dividing its first argument by its second argument (assuming that the result of division must be an integer). It returns an integer if both arguments are integers, otherwise it returns a float.

Syntax

(mod \<numeric-expression\> \<numeric-expression\>)

Example

CLIPS\> (mod 5 2)

1

CLIPS\> (mod 3.7 1.2)

0.1

CLIPS\>

## 12.6 Procedural Functions

The following are functions which provide procedural programming capabilities similar to languages such as C and Java.

### 12.6.1 Binding Variables

The **bind** function allows values to be assigned to variables.

Syntax

(bind \<variable\> \<expression\>\*)

The \<variable\> term is the local or global variable to be bound (which may have been bound previously). The bind function may also be used within a message‑handler's body to set a slot's value.

If no \<expression\> is specified, then local variables are unbound and global variables are reset to their original value. If one \<expression\> is specified, then the value of \<variable\> is set to the return value from evaluating \<expression\>. If more than one \<expression\> is specified, then all of the \<expressions\> are evaluated and grouped together as a multifield value and the resulting value is stored in \<variable\>.

The bind function returns the symbol **FALSE** when a local variable is unbound, otherwise, the return value is the value to which \<variable\> is set.

Example 1

CLIPS\> (defglobal ?\*x\* = 3.4)

CLIPS\> ?\*x\*

3.4

CLIPS\> (bind ?\*x\* (+ 8 9))

17

CLIPS\> ?\*x\*

17

CLIPS\> (bind ?\*x\* (create\$ a b c d))

(a b c d)

CLIPS\> ?\*x\*

(a b c d)

CLIPS\> (bind ?\*x\* d e f)

(d e f)

CLIPS\> ?\*x\*

(d e f)

CLIPS\> (bind ?\*x\*)

3.4

CLIPS\> ?\*x\*

3.4

CLIPS\> (bind ?x 32)

32

CLIPS\> ?x

32

CLIPS\> (reset)

CLIPS\> ?x

\[EVALUATN1\] Variable x is unbound

FALSE

CLIPS\>

Example 2

CLIPS\>

(defclass A (is-a USER)

(slot x)

(slot y))

CLIPS\>

(defmessage-handler A init after ()

(bind ?self:x 3)

(bind ?self:y 4))

CLIPS\> (make-instance a of A)

\[a\]

CLIPS\> (send \[a\] print)

\[a\] of A

(x 3)

(y 4)

CLIPS\>

### 12.6.2 If\...then\...else Function

The **if** function allows conditional execution of a set of actions.

Syntax

(if \<expression\>\
then\
\<action\>\*\
\[else\
\<action\>\*\])

Any number of allowable actions may be used inside of the **then** or **else** portion, including another **if\...then\...else** structure. The **else** portion is optional. If \<expression\> evaluates to anything other than the symbol **FALSE**, then the actions associated with the **then** portion are executed. Otherwise, the actions associated with the **else** portion are executed. The return value of the **if** function is the value of the last \<expression\> or \<action\> evaluated.

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age))

CLIPS\>

(defrule print-age

(person (name ?name) (age ?age))

=\>

(if (= ?age 1)

then

(println ?name \" is 1 year old\")

else

(println ?name \" is \" ?age \" years old\")))

CLIPS\> (assert (person (name \"Sam Jones\") (age 1)))

\<Fact-1\>

CLIPS\> (assert (person (name \"Jill Smith\") (age 13)))

\<Fact-2\>

CLIPS\> (run)

Jill Smith is 13 years old

Sam Jones is 1 year old

CLIPS\>

When using the **if** function in the actions of a rule, one should consider whether shifting the conditions to separate rules is preferable. For example, the **print-age** rule in the prior example could be rewritten as the following two rules.

> (defrule print-age-1\
> (person (name ?name) (age 1))\
> =\>\
> (println ?name \" is 1 year old\"))

(defrule print-age-not-1

(person (name ?name) (age ?age&\~1))

=\>

(println ?name \" is \" ?age \" years old\"))

### 12.6.3 While

The **while** function allows simple looping based on a condition.

Syntax

(while[]{.indexref entry="while" bold=""} \<expression\> \[do\]\
\<action\>\*)

Any number of allowable actions may be placed inside the **while** block. The \<expression\> term is performed prior to the first execution of the loop. The actions within the **while** loop are executed until \<expression\> evaluates to the symbol **FALSE**. The **while** may optionally include the symbol **do** after the condition and before the first action. The **break** and **return** functions can be used to terminate the loop prematurely. The return value of this function is the symbol **FALSE** unless the **return** function is used to terminate the loop.

Example

CLIPS\>

(deffunction countdown (?count)

(while (\> ?count 0)

(println ?count)

(bind ?count (- ?count 1)))

(return (void)))

CLIPS\> (countdown 3)

3

2

1

CLIPS\>

### 12.6.4 Loop-for-count

The **loop‑for‑count** function allows iterative looping.

Syntax

(loop-for-count \<range-spec\> \[do\] \<action\>\*)

\<range-spec\> ::= \<end-index\> \|

(\<loop-variable\> \<start-index\> \<end-index\>) \|

(\<loop-variable\> \<end-index\>)

\<start-index\> ::= \<integer-expression\>

\<end-index\> ::= \<integer-expression\>

The \<action\> term is performed the number of times specified by \<range‑spec\>. If \<start‑index\> is not given, it is assumed to be one. If \<start‑index\> is greater than \<end‑index\>, then the body of the loop is never executed. The integer value of the current iteration can be examined with the loop variable, if specified. The **break** and **return** functions can be used to terminate the loop prematurely. The return value of this function is the symbol **FALSE** unless the **return** function is used to terminate the loop. Variables from an outer scope may be used within the loop, but the loop variable (if specified) masks any outer variables of the same name. Loops can be nested.

Example

CLIPS\> (loop-for-count 2 (println \"Hello World!\"))

Hello World!

Hello World!

FALSE

CLIPS\>

(loop-for-count (?cnt1 2 4) do

(loop-for-count (?cnt2 1 3) do

(println ?cnt1 \" \" ?cnt2)))

2 1

2 2

2 3

3 1

3 2

3 3

4 1

4 2

4 3

FALSE

CLIPS\>

### 12.6.5 Progn

The **progn** function evaluates all of its arguments and returns the value of the last argument;.

Syntax

(progn[]{.indexref entry="progn" bold=""} \<expression\>\*)

Example

CLIPS\> (progn (setgen 5) (gensym))

gen5

CLIPS\>

### 12.6.6 Progn\$

The **progn\$** function performs a set of actions for each field of a multifield value.

Syntax

(progn\$[]{.indexref entry="progn$" bold=""} \<multifield-spec\> \<expression\>\*)

\<multifield-spec\> ::= \<multifield-expression\> \|

(\<field-variable\> \<multifield-expression\>)

The field of the current iteration can be examined with the \<field‑variable\> term, if specified. The index of the current iteration can be examined with \<field‑variable\>**‑index**. The **progn\$** function can use variables from outer scopes, and the **return** and **break** functions can also be used within a **progn\$** as long as they are valid in the outer scope. The return value of this function is the return value of the last action performed for the last field in the multifield value.

Example

CLIPS\>

(progn\$ (?item (create\$ milk eggs cheese))

(println ?item-index \". \" ?item))

1\. milk

2\. eggs

3\. cheese

CLIPS\>

### 12.6.7 Return

The **return** function immediately terminates the currently executing deffunction, generic function method, message‑handler, defrule, or fact/instance set query function. Without any arguments, there is no return value. However, if an argument is included, its value is the return value of the deffunction, method, or message‑handler in which it is contained. If used in the RHS of a rule, the current focus is removed from the focus stack.

Syntax

(return \[\<expression\>\])

Example

CLIPS\>

(deffunction sign (?num)

(if (\> ?num 0) then

(return 1))

(if (\< ?num 0) then

(return -1))

0\)

CLIPS\> (sign 5)

1

CLIPS\> (sign -10)

-1

CLIPS\> (sign 0)

0

CLIPS\>

### 12.6.8 Break

The **break** function immediately terminates the currently iterating **while** loop, **loop-for-count** execution, **progn** execution, **progn\$** execution, **foreach** execution, or fact/instance set query function.

Syntax

(break)

Example

CLIPS\>

(deffunction iterate (?num)

(bind ?i 0)

(while TRUE do

(if (\>= ?i ?num) then

(break))

(print ?i \" \")

(bind ?i (+ ?i 1)))

(println))

CLIPS\> (iterate 1)

0

CLIPS\> (iterate 10)

0 1 2 3 4 5 6 7 8 9

CLIPS\>

### 12.6.9 Switch

The **switch** function selects a particular group of actions (among several groups of actions) to perform based on a specified value.

Syntax

(switch[]{.indexref entry="switch" bold=""} \<test-expression\>

\<case-statement\>\*

\[\<default-statement\>\])

\<case-statement\> ::=

(case \<comparison-expression\> then \<action\>\*)

\<default-statement\> ::= (default \<action\>\*)

As indicated by the BNF, the optional default statement must succeed all case statements. None of the case comparison expressions should be the same.

The **switch** function evaluates the \<test‑expression\> term first and then evaluates each \<comparison‑expression\> term in order of definition. Once the evaluation of the \<comparison‑expression\> is equivalent to the evaluation of the \<test‑expression\>, the actions of that case are evaluated (in order) and the switch function is terminated. If no cases are satisfied, the default actions (if any) are evaluated (in order).

The return value of the **switch** function is the last action evaluated in the **switch** function. If no actions are evaluated, the return value is the symbol **FALSE**.

Example

CLIPS\>

(deffunction complement (?color)

(switch ?color

(case red then cyan)

(case cyan then red)

(case green then magenta)

(case magenta then green)

(case blue then yellow)

(case yellow then blue)

(default FALSE)))

CLIPS\> (complement green)

magenta

CLIPS\> (complement black)

FALSE

CLIPS\>

### 12.6.10 Foreach

The **foreach** function performs a set of actions for each field of a multifield value.

Syntax

(foreach[]{.indexref entry="foreach" bold=""} \<field-variable\> \<multifield-expression\> \<expression\>\*)

The field of the current iteration can be examined with the \<field‑variable\> term if specified. The index of the current iteration can be examined with \<field‑variable\>**‑index**. The **foreach** function can use variables from outer scopes, and the **return** and **break** functions can also be used within a **foreach** as long as they are valid in the outer scope. The return value of this function is the return value of the last action performed for the last field in the multifield value.

Example

CLIPS\>

(foreach ?item (create\$ milk eggs cheese)

(println ?item-index \". \" ?item))

1\. milk

2\. eggs

3\. cheese

CLIPS\>

 Portability Note

The **foreach** function provides the same functionality as the **progn\$**[]{.indexref entry="progn$"} function, but uses different syntax with a more meaningful function name.

### 12.6.11 Try

The **try** function performs a set of actions, and if an error occurs, allows another set of actions to be performed.

Syntax

(try[]{.indexref entry="try" bold=""} \<try-action\>\* \[catch \<catch-action\>\*\])

Each \<try-action\> following the **try** keyword is performed. If an error occurs, execution of the try actions is terminated and each \<catch-action\> following the **catch** keyword is executed. The return value of this function is the symbol TRUE if an error occurred; otherwise, it is the symbol FALSE.

Example

CLIPS\>

(loop-for-count (?i 3)

(try

(println \"Before \" ?i)

(println (/ 4 (- ?i 2)))

(println \"After \" ?i)

catch

(print \"Continue? \")

(if (neq (read) yes) then (break))))

Before 1

-4.0

After 1

Before 2

\[PRNTUTIL7\] Attempt to divide by zero in \'/\' function.

Continue? yes

Before 3

4.0

After 3

FALSE

CLIPS\>

## 12.7 Miscellaneous Functions

The following are additional functions for use within CLIPS.

### 12.7.1 Gensym

The **gensym** function returns a sequenced generated symbol that can be stored as a sin­gle field. This is useful for slot values that need a simple identifier. Multiple calls to **gensym** return different identifiers of the form genX where X is a positive integer. The first call to **gensym** returns **gen1**; all subsequent calls increment the number. Note that **gensym** is *not* reset after a call to **clear**. If users plan to use the gensym feature, they should avoid creating facts which include a user‑defined field of this form.

Example

CLIPS\>

(deftemplate order

(slot id (default-dynamic (gensym)))

(slot item)

(slot quantity))

CLIPS\> (assert (order (item C3) (quantity 3)))

\<Fact-1\>

CLIPS\> (assert (order (item B1) (quantity 1)))

\<Fact-2\>

CLIPS\> (assert (order (item C3) (quantity 3)))

\<Fact-3\>

CLIPS\> (facts)

f-1 (order (id gen1) (item C3) (quantity 3))

f-2 (order (id gen2) (item B1) (quantity 1))

f-3 (order (id gen3) (item C3) (quantity 3))

For a total of 3 facts.

CLIPS\>

### 12.7.2 Gensym\*

The **gensym\*** function is similar to the **gensym** function, however, it will produce a unique symbol that does not currently exist within the CLIPS environment.

Example

CLIPS\> (setgen 1)

1

CLIPS\> (assert (gen1 gen2 gen3))

\<Fact-1\>

CLIPS\> (gensym)

gen1

CLIPS\> (gensym\*)

gen4

CLIPS\>

### 12.7.3 Setgen

The **setgen** function assigns the starting integer used by the **gensym** and **gensym\*** functions.

Syntax

(setgen \<integer-expression\>)

The \<intger-expression\> term must be a positive integer value and is the value returned by this function. All subsequent calls to **gensym** will return a sequenced symbol with the numeric portion of the symbol starting at \<integer-expression\>.

Example

CLIPS\> (setgen 32)

32

CLIPS\> (gensym)

gen32

CLIPS\>

### 12.7.4 Random

The **random** function returns a random integer value.

Syntax

(random \[\<start-integer-expression\> \<end-integer-expression\>\])

The \<start-integer-expression\> and \<end-integer-expression\> terms, if specified, indicate the range of values to which the randomly generated integer is limited.

Example

CLIPS\> (clear)

CLIPS\>

(defrule roll-the-dice

?f \<- (roll-the-dice)

=\>

(retract ?f)

(bind ?roll1 (random 1 6))

(bind ?roll2 (random 1 6))

(println \"Your roll is: \" ?roll1 \" \" ?roll2))

CLIPS\> (assert (roll-the-dice))

\<Fact-1\>

CLIPS\> (run)

Your roll is: 5 6

CLIPS\>

 Portability Note

The **rand** function is implemented using the ANSI C function **rand**.

### 12.7.5 Seed

The **seed** function seeds the random number generator.

Syntax

(seed \<integer-expression\>)

The \<integer-expression\> term is the integer seed value. This function has no return value.

Example

CLIPS\> (seed 2357)

CLIPS\> (random 1 10)

10

CLIPS\> (random 1 10)

4

CLIPS\> (random 1 10)

2

CLIPS\> (seed 2357)

CLIPS\> (random 1 10)

10

CLIPS\> (random 1 10)

4

CLIPS\> (random 1 10)

2

CLIPS\>

 Portability Note

The **seed** function is implemented using the ANSI C function **srand**. The CLIPS Integrated Development Environments for Windows, macOS, and Java use a multi-threaded implementation; the user interface runs on the main thread and each command entered at the Read-Eval-Print Loop is executed using a separate newly created thread. In this situation, the **seed** function (via **srand**) is not guaranteed to properly seed the random number generator for newly created threads (i.e. subsequent commands entered at the REPL).

### 12.7.6 Time

The **time** function returns a floating‑point value representing the elapsed seconds since the system refer­ence time.

Syntax

(time)

### 12.7.7 Determining the Restrictions for a Function

The **get‑function‑restrictions** function can be used to gain access to the restriction string associated with a system or user defined function created using the **AddUDF** API. The restriction string contains information on the number and types of arguments that a function expects. The restriction string contains the minimum number of arguments, maximum number of arguments, default argument type, and specific argument types. Each entry in the restriction string is delimited by a semicolon. See section 8 of the Advanced Programming Guide for the meaning of the characters which compose the restriction string.

Syntax

(get-function-restrictions \<function-name\>)

Example

CLIPS\> (get-function-restrictions +)

\"2;\*;ld\"

CLIPS\>

### 12.7.8 Sorting a List of Values

The **sort** function allows a list of values to be sorted.

Syntax

(sort \<comparison-function-name\> \<expression\>\*)

The **sort** function returns a multifield value containing the sorted values specified as arguments. The comparison function used for sorting should accept exactly two arguments and can be a user-defined function, a generic function, or a deffunction. Given two adjacent arguments from the list to be sorted, the comparison function should return the symbol **TRUE** if its first argument should come after its second argument in the sorted list; otherwise, the symbol **FALSE** should be returned.

Example

CLIPS\> (sort \> 4 3 5 7 2 7)

(2 3 4 5 7 7)

CLIPS\>

(deffunction string\> (?a ?b)

(\> (str-compare ?a ?b) 0))

CLIPS\> (sort string\> ax aa bk mn ft m)

(aa ax bk ft m mn)

CLIPS\>

### 12.7.9 Calling a Function

The **funcall** function constructs a function call from its arguments and then evaluates the function call. The first argument should be the name of a user-defined function, deffunction, or generic function. The remaining arguments are evaluated and then passed to the specified function when it is evaluated. Functions that are invoked using specialized syntax, such as the **assert**[]{.indexref entry="assert"} command (which uses parentheses to delimit both slot and function names), may not be called using funcall.

Syntax

(funcall \<function-name\> \<expression\>\*)

Example

CLIPS\> (funcall delete\$ (create\$ a b c) 2 2)

(a c)

CLIPS\> (funcall + 1 2 (expand\$ (create\$ 3 4)))

10

CLIPS\>

### 12.7.10 Timing Functions and Commands

The **timer** function returns the number of seconds elapsed evaluating a series of expressions.

Syntax

(timer \<expression\>\*)

Example

CLIPS\> (timer (loop-for-count 10000 (+ 3 4)))

0.0416709999999512

CLIPS\>

### 12.7.11 Determining the Operating System

The **operating-system** function returns a symbol indicating the opertating system on which CLIPS is running. Possible return values are the symbols **UNIX-V**, **UNIX‑7**, **LINUX**, **DARWIN**, **MAC‑OS**, **DOS**, **WINDOWS**, and **UNKNOWN**.

Syntax

(operating-system)

### 12.7.12 Local Time

The **local-time** function returns a multifield value containing fields indicating the local time. In order, the returned fields are year, month, day, hours, seconds, day of week, days since the beginning of the year, and a boolean flag indicating whether daylight savings time is in effect.

Syntax

(local-time)

Example

CLIPS\> (local-time)

(2018 6 6 15 1 9 Wednesday 156 TRUE)

CLIPS\>

### 12.7.13 Greenwich Mean Time

The **gm-time** function returns returns a multifield value containing fields indicating Greenwich mean time. In order, the returned fields are year, month, day, hours, seconds, day of week, days since the beginning of the year, and a boolean flag indicating whether daylight savings time is in effect.

Syntax

(gm-time)

Example

CLIPS\> (gm-time)

(2018 6 6 20 1 44 Wednesday 156 FALSE)

CLIPS\>

### 12.7.14 Getting the Error State

The **get-error** function returns the current value of the error state (or status value). The error state can be set by system and user defined functions as well as using the **set-error** function.

Syntax

(get-error)

### 12.7.15 Clearing the Error State

The **clear-error** function resets the error state (or status value) to the the symbol **FALSE** and returns the prior value of the error state.

Syntax

(clear-error)

### 12.7.16 Setting the Error State

The **set-error** function sets the error state (or status value).

Syntax

(set-error \<expression\>)

Example

CLIPS\> (set-error 10)**\**
CLIPS\> (get-error)**\**
10**\**
CLIPS\> (get-error)**\**
10**\**
CLIPS\> (clear-error)**\**
10**\**
CLIPS\> (get-error)**\**
FALSE**\**
CLIPS\>

### 12.7.17 Void Value

The **void** function returns the void value.

Syntax

(void)

Example

CLIPS\>

(deffunction countdown (?c)

(loop-for-count (?i 0 ?c) (println (- ?c ?i))))

CLIPS\> (countdown 3)

3

2

1

0

FALSE

CLIPS\>

(deffunction countdown (?c)

(loop-for-count (?i 0 ?c) (println (- ?c ?i)))

(void))

CLIPS\> (countdown 3)

3

2

1

0

CLIPS\>

## 12.8 Deftemplate Functions

The following functions provide ancillary capabilities for the deftemplate construct.

### 12.8.1 Determining the Module in which a Deftemplate is Defined

The **deftemplate-module** function returns the module in which the specified deftemplate name is defined.

Syntax

(deftemplate‑module \<deftemplate-name\>)

### 12.8.2 Getting the Allowed Values for a Deftemplate Slot

The **deftemplate-slot-allowed-values** function groups the allowed values for a slot (specified in any of allowed‑... attributes for the slots) into a multifield variable. If no allowed‑... attributes were specified for the slot, then the symbol **FALSE** is returned. A multifield of length zero is returned if an error occurs.

Syntax

(deftemplate-slot‑allowed‑values \<deftemplate-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot gender (allowed-symbols male female)))

CLIPS\> (deftemplate-slot-allowed-values person gender)

(male female)

CLIPS\>

### 12.8.3 Getting the Cardinality for a Deftemplate Slot

The **deftemplate-slot-cardinality** function groups the minimum and maximum cardinality allowed for a multifield slot into a multifield variable. A maximum cardinality of infinity is indicated by the symbol **+oo** (the plus character followed by two lowercase o's---not zeroes). A multifield of length zero is returned for single field slots or if an error occurs.

Syntax

(deftemplate-slot‑cardinality \<deftemplate-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate polygon

(multislot coordinates

(type INTEGER)

(cardinality 6 ?VARIABLE)))

CLIPS\> (deftemplate-slot-cardinality polygon coordinates)

(6 +oo)

CLIPS\>

### 12.8.4 Testing whether a Deftemplate Slot has a Default

The **deftemplate-slot-defaultp** function returns the symbol static if the specified slot in the specified deftemplate has a static default (whether explicitly or implicitly defined), the symbol dynamic if the slot has a dynamic default, or the symbol **FALSE** if the slot does not have a default. An error is generated if the specified deftemplate or slot does not exist.

Syntax

(deftemplate-slot-defaultp \<deftemplate-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate order

(slot id (default-dynamic (gensym)))

(slot item (type STRING) (default ?NONE))

(slot quantity (type INTEGER) (default 1))

(slot details (type STRING)))

CLIPS\> (deftemplate-slot-defaultp order id)

dynamic

CLIPS\> (deftemplate-slot-defaultp order item)

FALSE

CLIPS\> (deftemplate-slot-defaultp order quantity)

static

CLIPS\> (deftemplate-slot-defaultp order details)

static

CLIPS\>

### 12.8.5 Getting the Default Value for a Deftemplate Slot

The **deftemplate-slot-default-value** function returns the default value associated with a deftemplate slot. If a slot has a dynamic default, the expression will be evaluated when this function is called. The symbol **FALSE** is returned if an error occurs.

Syntax

(deftemplate-slot‑default-value \<deftemplate-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate order

(slot id (default-dynamic (gensym)))

(slot item (type STRING) (default ?NONE))

(slot quantity (type INTEGER) (default 1))

(slot details (type STRING)))

CLIPS\> (deftemplate-slot-default-value order id)

gen1

CLIPS\> (deftemplate-slot-default-value order item)

?NONE

CLIPS\> (deftemplate-slot-default-value order quantity)

1

CLIPS\> (deftemplate-slot-default-value order details)

\"\"

CLIPS\>

### 12.8.6 Deftemplate Slot Existence

The **deftemplate-slot-existp** function returns the symbol **TRUE** if the specified slot is present in the specified deftemplate; otherwise, it returns the symbol **FALSE**.

Syntax

(deftemplate-slot-existp \<deftemplate-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age))

CLIPS\> (deftemplate-slot-existp person name)

TRUE

CLIPS\> (deftemplate-slot-existp person gender)

FALSE

CLIPS\>

### 12.8.7 Testing whether a Deftemplate Slot is a Multifield Slot 

The **deftemplate-slot-multip** function returns the symbol **TRUE** if the specified slot in the specified deftemplate is a multifield slot; otherwise, it returns the symbol **FALSE**. An error is generated if the specified deftemplate or slot does not exist.

Syntax

(deftemplate-slot‑multip \<deftemplate-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age)

(multislot hobbies))

CLIPS\> (deftemplate-slot-multip person name)

FALSE

CLIPS\> (deftemplate-slot-multip person hobbies)

TRUE

CLIPS\>

### 12.8.8 Determining the Slot Names Associated with a Deftemplate

The **deftemplate‑slot-names** function returns the slot names associated with the deftemplate in a multifield value. The symbol **implied** is returned for an implied deftemplate (which has a single implied multifield slot). The symbol **FALSE** is returned if the specified deftemplate does not exist.

Syntax

(deftemplate-slot-names \<deftemplate-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age)

(multislot hobbies))

CLIPS\> (deftemplate-slot-names person)

(name age hobbies)

CLIPS\>

### 12.8.9 Getting the Numeric Range for a Deftemplate Slot

The **deftemplate-slot-range** function groups the minimum and maximum numeric ranges allowed for a slot into a multifield variable. A minimum value of infinity is indicated by the symbol **‑oo** (the minus character followed by two lowercase 'o' characters---not zeroes). A maximum value of infinity is indicated by the symbol **+oo** (the plus character followed by two lowercase 'o' characters). The symbol **FALSE** is returned for slots in which numeric values are not allowed. A multifield of length zero is returned if an error occurs.

Syntax

(deftemplate-slot‑range \<deftemplate-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name (type STRING))

(slot age (type INTEGER) (range 0 120))

(slot net-worth (type FLOAT)))

CLIPS\> (deftemplate-slot-range person name)

FALSE

CLIPS\> (deftemplate-slot-range person age)

(0 120)

CLIPS\> (deftemplate-slot-range person net-worth)

(-oo +oo)

CLIPS\>

### 12.8.10 Testing whether a Deftemplate Slot is a Single-Field Slot 

The **deftemplate-slot-singlep** function returns the symbol **TRUE** if the specified slot in the specified deftemplate is a single-field slot; otherwise, it returns the symbol **FALSE**. An error is generated if the specified deftemplate or slot does not exist.

Syntax

(deftemplate-slot‑singlep \<deftemplate-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age)

(multislot hobbies))

CLIPS\> (deftemplate-slot-singlep person name)

TRUE

CLIPS\> (deftemplate-slot-singlep person hobbies)

FALSE

CLIPS\>

### 12.8.11 Getting the Primitive Types for a Deftemplate Slot

The **deftemplate-slot-types** function groups the names of the primitive types allowed for a deftemplate slot into a multifield variable. A multifield of length zero is returned if an error occurs.

Syntax

(deftemplate-slot‑types \<deftemplate-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name (type STRING))

(slot age (type INTEGER) (range 0 120))

(slot net-worth (type FLOAT))

(multislot tags (type LEXEME NUMBER)))

CLIPS\> (deftemplate-slot-types person age)

(INTEGER)

CLIPS\> (deftemplate-slot-types person tags)

(FLOAT INTEGER SYMBOL STRING)

CLIPS\>

### 12.8.12 Getting the List of Deftemplates

The **get‑deftemplate‑list** function returns a multifield value containing the names of all deftemplate constructs facts visible to the module specified by \<module-name\> or to the current module if none is specified. If the symbol **\*** is specified as the module name, then all deftemplates are returned.

Syntax

(get‑deftemplate‑list \[\<module-name\>\])

Example

CLIPS\> (clear)

CLIPS\> (deftemplate person)

CLIPS\> (deftemplate order)

CLIPS\> (get-deftemplate-list)

(person order)

CLIPS\>

## 12.9 Fact Functions

The following actions are used for assert, retracting, and modifying facts.

### 12.9.1 Creating New Facts

The **assert** function creates new facts and adds them to the fact‑list. Multiple facts may be asserted with each call. If the **facts** item is being watched as a result of the **watch** command, then an informational message will be printed each time a fact is asserted.

Syntax

(assert \<RHS-pattern\>+)

Missing slots in a tem­plate fact being asserted are assigned their default value. If an identical copy of the fact already exists in the fact‑list, the fact will not be added (however, this behavior can be changed using the **set-fact-duplication** command). Note that in addition to constants, expressions can be placed within a fact to be asserted. The first field of a fact must be a symbol. The value returned of the assert function is the fact‑address of the last fact asserted. If an identical copy of the last fact already exists in the fact‑list, then the fact-address of the existing fact is returned. If the assertion of the last fact causes an error, then the symbol **FALSE** is returned.

Example

CLIPS\> (clear)

CLIPS\> (assert (color red))

\<Fact-1\>

CLIPS\> (assert (color blue) (value (+ 3 4)))

\<Fact-3\>

CLIPS\> (assert (color red))

FALSE

CLIPS\> (deftemplate status (slot temp) (slot pressure))

CLIPS\> (assert (status (temp high)

(pressure low)))

\<Fact-4\>

CLIPS\> (facts)

f-1 (color red)

f-2 (color blue)

f-3 (value 7)

f-4 (status (temp high) (pressure low))

For a total of 4 facts.

CLIPS\>

### 12.9.2 Removing Facts from the Fact‑list

The **retract** function removes facts from the fact‑list. Multiple facts may be retracted with a single retract call. The retraction of a fact also removes all rules that depended upon that fact for activation from the agenda. Retraction of a fact may also cause the retraction of other facts which receive logical support from the retracted fact. If the facts item is being watched as a result of the **watch** command, then an informational message will be printed each time a fact is retracted.

Syntax

(retract \<retract-specifier\>+ \| \*)

\<retract-specifier\> ::= \<fact-specifier\> \| \<integer-expression\>

The \<retract‑specifier\> term includes variables bound on the LHS to fact‑addresses, the **fact‑index** of the desired fact (e.g. 3 for the fact labeled f‑3), or an expression which evaluates to a retract‑specifier. If the symbol **\*** is used as an argument, all facts will be retracted. This function has no return value.

Example

CLIPS\> (clear)

CLIPS\>

(defrule purchased

?gl \<- (grocery-list \$?b ?item \$?e)

?p \<- (purchased ?item)

=\>

(retract ?gl ?p)

(assert (grocery-list ?b ?e)))

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (assert (purchased milk) (purchased cheese))

\<Fact-3\>

CLIPS\> (watch rules)

CLIPS\> (watch facts)

CLIPS\> (run)

FIRE 1 purchased: f-1,f-3

\<== f-1 (grocery-list milk eggs cheese)

\<== f-3 (purchased cheese)

==\> f-4 (grocery-list milk eggs)

FIRE 2 purchased: f-4,f-2

\<== f-4 (grocery-list milk eggs)

\<== f-2 (purchased milk)

==\> f-5 (grocery-list eggs)

CLIPS\> (facts)

f-5 (grocery-list eggs)

For a total of 1 fact.

CLIPS\> (unwatch all)

CLIPS\>

### 12.9.3 Modifying Template Facts

The **modify** function modifies the slot values of an existing template fact. Only one fact may be modified with a single modify call. The modification of a fact is equivalent to retracting the present fact and asserting the modified fact. Therefore, any facts receiving logical support from a template fact are retracted (assuming no other support) when the template fact is modified and the new template fact loses any logical support that it previously had.

Syntax

(modify \<fact-specifier\> \<RHS-slot\>\*)

The \<fact‑specifier\> term includes variables bound on the LHS to fact‑addresses, the **fact‑index** of the desired fact (e.g. 3 for the fact labeled f‑3), or an expression which evaluates to a fact‑specifier. Static deftemplate checking is not performed when a fact‑index is used as the \<fact‑specifier\> since the deftemplate being referenced is unknown until the action is executed. The value returned by this function is the fact‑address of the newly modified fact. If an identical copy of the newly modified fact already exists in the fact‑list, the fact-address of the existing copy is returned; otherwise the fact-address and fact-index of a modified fact is preserved. If the assertion of the newly modified fact causes an error, the symbol **FALSE** is returned. If all slot changes specified in the modify command match the current values of the fact to be modified, no action is taken.

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate valve

(slot id)

(slot state))

CLIPS\>

(deftemplate set

(slot id)

(slot state))

CLIPS\>

(defrule change-valve-status

?f1 \<- (valve (id ?v) (state ?state))

?f2 \<- (set (id ?v) (state ?new-state))

=\>

(retract ?f2)

(modify ?f1 (state ?new-state)))

CLIPS\> (assert (valve (id 1) (state open)))

\<Fact-1\>

CLIPS\> (assert (set (id 1) (state closed)))

\<Fact-2\>

CLIPS\> (watch facts)

CLIPS\> (run)

\<== f-2 (set (id 1) (state closed))

\<== f-1 (valve \... (state open))

==\> f-1 (valve \... (state closed))

CLIPS\> (unwatch facts)

CLIPS\>

### 12.9.4 Duplicating Template Facts

The **duplicate** function creates a new template fact from the slot values of an existing template fact. The new fact is created by assigning the slot values specified in the **duplicate** call and then copying the remaining slot values from the existing fact. Only one fact may be duplicated with a single duplicate statement. The duplicate function is similar to the **modify** function except the fact being duplicated is not retracted.

Syntax

(duplicate \<fact-specifier\> \<RHS-slot\>\*)

The \<fact‑specifier\> term includes variables bound on the LHS to fact‑addresses, the **fact‑index** of the desired fact (e.g. 3 for the fact labeled f‑3), or an expression which evaluates to a fact‑specifier. Static deftemplate checking is not performed when a fact‑index is used as the \<fact‑specifier\> since the deftemplate being referenced is usually ambiguous. The value returned by this function is the fact‑address of the newly duplicated fact. If an identical copy of the newly duplicated fact already exists in the fact‑list, the fact-address of the existing copy is returned. If the assertion of the newly duplicated fact causes an error, then the symbol **FALSE** is returned.

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate order

(slot id)

(slot item)

(slot quantity))

CLIPS\>

(defrule clone-order

?c \<- (clone ?id ?new-id)

?o \<- (order (id ?id))

=\>

(retract ?c)

(duplicate ?o (id ?new-id)))

CLIPS\> (assert (order (id o1) (item #6732938) (quantity 2)))

\<Fact-1\>

CLIPS\> (assert (clone o1 o2))

\<Fact-2\>

CLIPS\> (watch facts)

CLIPS\> (run)

\<== f-2 (clone o1 o2)

==\> f-3 (order (id o2) (item #6732938) (quantity 2))

CLIPS\> (unwatch facts)

CLIPS\>

### 12.9.5 Asserting a String

The **assert‑string** function is similar to the **assert** function in that it creates a new fact and adds it to the fact‑list. How­ever, **assert‑string** takes a single string representing a fact (expressed in either ordered or deftemplate format) and asserts it. Only one fact may be asserted with each **assert‑string** statement.

Syntax

(assert-string \<string-expression\>)

If an identical copy of the fact already exists in the fact‑list, the fact will not be added (however, this behavior can be changed using the **set-fact-duplication** command). Fields within the fact may contain a string by escaping the quote character with a backslash. Note that this function takes a string and turns it into fields. If the fields within that string are going to contain special characters (such as a backslash), they need to be escaped twice (because you are literally embedding a string within a string and the backslash mechanism ends up being applied twice). Global variables and expressions can be contained within the string. The value returned by this function is the fact‑address of the newly created fact. If an identical copy of the newly created fact already exists in the fact‑list, the fact-address of the existing copy is returned. If the assertion of the newly created fact causes an error, then the symbol **FALSE** is returned.

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age))

CLIPS\> (assert-string \"(grocery-list milk eggs cheese)\")

\<Fact-1\>

CLIPS\> (assert-string \"(fees-paid \\\"N\\\\\\\\A\\\")\")

\<Fact-2\>

CLIPS\> (assert-string \"(person (name \\\"Jack Farmer\\\") (age 23))\")

\<Fact-3\>

CLIPS\> (facts)

f-1 (grocery-list milk eggs cheese)

f-2 (fees-paid \"N\\A\")

f-3 (person (name \"Jack Farmer\") (age 23))

For a total of 3 facts.

CLIPS\>

### 12.9.6 Getting the Fact‑Index of a Fact‑address

The **fact‑index** function returns the fact‑index (an integer) of a fact‑address.

Syntax

(fact-index \<fact-address\>)

Example

CLIPS\> (clear)

CLIPS\> (bind ?f (assert (grocery-list milk eggs cheese)))

\<Fact-1\>

CLIPS\> (fact-index ?f)

1

CLIPS\>

### 12.9.7 Determining If a Fact Exists

The **fact‑existp** function returns the symbol **TRUE** if the fact specified by its fact-index or fact-address argument exists; otherwise, the symbol **FALSE** is returned.

Syntax

(fact-existp \<fact-address-or-index\>)

Example

CLIPS\> (clear)

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (fact-existp 1)

TRUE

CLIPS\> (retract 1)

CLIPS\> (fact-existp 1)

FALSE

CLIPS\>

### 12.9.8 Determining the Deftemplate (Relation) Name Associated with a Fact

The **fact‑relation** function returns the deftemplate (relation) name associated with the fact. The symbol **FALSE** is returned if the specified fact does not exist.

Syntax

(fact-relation \<fact-address-or-index\>)

Example

CLIPS\> (clear)

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (fact-relation 1)

grocery-list

CLIPS\>

### 12.9.9 Determining the Slot Names Associated with a Fact

The **fact‑slot-names** function returns a multifield value containing the slot names associated with a fact. The symbol **implied** is returned for an ordered fact (which has a single implied multifield slot). The symbol **FALSE** is returned if the specified fact does not exist.

Syntax

(fact-slot-names \<fact-address-or-index\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age)

(multislot hobbies))

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (assert (person (name \"Jack Smith\") (age 23) (hobbies movies golf)))

\<Fact-2\>

CLIPS\> (fact-slot-names 1)

(implied)

CLIPS\> (fact-slot-names 2)

(name age hobbies)

CLIPS\>

### 12.9.10 Retrieving the Slot Value of a Fact

The **fact‑slot-value** function returns the value of the specified slot from the specified fact. The symbol **implied** should be used as the slot name for the implied multifield slot of an ordered fact. The symbol **FALSE** is returned if the slot name argument is invalid or the specified fact does not exist.

Syntax

(fact-slot-value \<fact-address-or-index\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate person

(slot name)

(slot age)

(multislot hobbies))

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (assert (person (name \"Jack Smith\") (age 23) (hobbies movies golf)))

\<Fact-2\>

CLIPS\> (fact-slot-value 1 implied)

(milk eggs cheese)

CLIPS\> (fact-slot-value 2 name)

\"Jack Smith\"

CLIPS\> (fact-slot-value 2 hobbies)

(movies golf)

CLIPS\>

### 12.9.11 Retrieving the Fact-List

The **get-fact-list** function returns a multifield containing the list of facts visible to the module specified by \<module-name\> or to the current module if none is specified. If the symbol **\*** is specified as the module name, then all facts are returned.

Syntax

(get-fact-list \[\<module-name\>\])

Example

CLIPS\> (clear)

CLIPS\> (defmodule PEOPLE)

CLIPS\>

(deftemplate person

(slot name)

(slot credit))

CLIPS\> (assert (person (name \"Jack Smith\") (credit 100.0)))

\<Fact-1\>

CLIPS\> (defmodule ORDERS)

CLIPS\>

(deftemplate order

(slot item)

(slot quantity)

(slot customer))

CLIPS\> (assert (order (item #7362383) (quantity 2) (customer \"Jack Smith\")))

\<Fact-2\>

CLIPS\> (get-fact-list)

(\<Fact-2\>)

CLIPS\> (get-fact-list PEOPLE)

(\<Fact-1\>)

CLIPS\> (get-fact-list \*)

(\<Fact-1\> \<Fact-2\>)

CLIPS\>

### 12.9.12 Fact‑set Queries and Distributed Actions

CLIPS provides a query system for finding and performing actions on sets of facts that satisfy queries. The fact query system provides the six functions shown in the following table.

+--------------------------+------------------------------------------------------------------------------------------+
| **Function**             | **Purpose**                                                                              |
+==========================+==========================================================================================+
| any-factp                | > Determines if one or more fact‑sets satisfy a query                                    |
+--------------------------+------------------------------------------------------------------------------------------+
| find-fact                | > Returns the first fact‑set that satisfies a query                                      |
+--------------------------+------------------------------------------------------------------------------------------+
| find-all-facts           | > Groups and returns all fact‑sets which satisfy a query                                 |
+--------------------------+------------------------------------------------------------------------------------------+
| do-for-fact              | > Performs an action for the first fact‑set which satisfies a query                      |
+--------------------------+------------------------------------------------------------------------------------------+
| do-for-all-facts         | > Performs an action for every fact‑set which satisfies a query as they are found        |
+--------------------------+------------------------------------------------------------------------------------------+
| delayed-do-for-all-facts | > Groups all fact‑sets which satisfy a query and then iterates an action over this group |
+--------------------------+------------------------------------------------------------------------------------------+

The following diagram shows a fact‑set query function call with key components labeled. The various components will be discussed later in this section.

![FST](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image8.jpeg){width="5.819444444444445in" height="1.8611111111111112in"}

The examples in this section assume that the following commands have already been entered.

CLIPS\> (clear)

CLIPS\>

(deftemplate girl

(slot name)

(slot sex (default female))

(slot age (default 4)))

CLIPS\>

(deftemplate woman

(slot name)

(slot sex (default female))

(slot age (default 25)))

CLIPS\>

(deftemplate boy

(slot name)

(slot sex (default male))

(slot age (default 4)))

CLIPS\>

(deftemplate man

(slot name)

(slot sex (default male))

(slot age (default 25)))

CLIPS\>

(deffacts PEOPLE

(man (name Man-1) (age 18))

(man (name Man-2) (age 60))

(woman (name Woman-1) (age 18))

(woman (name Woman-2) (age 60))

(woman (name Woman-3))

(boy (name Boy-1) (age 8))

(boy (name Boy-2))

(boy (name Boy-3))

(boy (name Boy-4))

(girl (name Girl-1) (age 8))

(girl (name Girl-2)))

CLIPS\> (reset)

CLIPS\> (facts)

f-1 (man (name Man-1) (sex male) (age 18))

f-2 (man (name Man-2) (sex male) (age 60))

f-3 (woman (name Woman-1) (sex female) (age 18))

f-4 (woman (name Woman-2) (sex female) (age 60))

f-5 (woman (name Woman-3) (sex female) (age 25))

f-6 (boy (name Boy-1) (sex male) (age 8))

f-7 (boy (name Boy-2) (sex male) (age 4))

f-8 (boy (name Boy-3) (sex male) (age 4))

f-9 (boy (name Boy-4) (sex male) (age 4))

f-10 (girl (name Girl-1) (sex female) (age 8))

f-11 (girl (name Girl-2) (sex female) (age 4))

For a total of 11 facts.

CLIPS\>

#### 12.9.12.1 Fact‑set Definition

A **fact‑set** is an ordered collection of facts. Each **fact‑set member** is a member of a set of deftemplates, called **template restrictions**, specified in the function call. The template restrictions can be different for each fact‑set member. The query functions use **fact‑set templates** to generate fact‑sets. A fact‑set template is a set of **fact‑set member variables** and their associated template restrictions. Fact‑set member variables reference the corresponding members in each fact‑set which matches a template. Variables may be used to specify the deftemplates for the fact‑set template, but if the constant names of the deftemplates are specified, the deftemplates must already be defined. Module specifiers may be included with the deftemplate names; the deftemplates need not be in scope of the current module.

Syntax

\<fact-set-template\>

::= (\<fact-set-member-template\>+)

\<fact-set-member-template\>

::= (\<fact-set-member-variable\> \<deftemplate-restrictions\>)

\<fact-set-member-variable\> ::= \<single-field-variable\>

\<deftemplate-restrictions\> ::= \<deftemplate-name-expression\>+

Example

One fact‑set template might be the ordered pairs of boys or men and girls or women.

((?man-or-boy boy man) (?woman-or-girl girl woman))

Fact‑set member variables (e.g. ?man‑or‑boy) are bound to fact-addresses.

#### 12.9.12.2 Fact‑set Determination

CLIPS uses straightforward permutations to generate fact‑sets that match a fact‑set template from the actual facts in the system. The rules are as follows:

1\) When there is more than one member in a fact‑set template, vary the rightmost members first.

2\) When there is more than one deftemplate that a fact‑set member can be, iterate through the deftemplates from left to right.

3\) Examine facts of a deftemplate in the order that they were defined.

Example

For the fact‑set template given in section 12.9.12.1, thirty fact‑sets would be generated in the following order:

+--------------------------------+--------------------------------+
| 1\. \<Fact-6\> \<Fact-10\>     | 16\. \<Fact-9\> \<Fact-10\>    |
|                                |                                |
| 2\. \<Fact-6\> \<Fact-11\>     | 17\. \<Fact-9\> \<Fact-11\>    |
|                                |                                |
| 3\. \<Fact-6\> \<Fact-3\>      | 18\. \<Fact-9\> \<Fact-3\>     |
|                                |                                |
| 4\. \<Fact-6\> \<Fact-4\>      | 19\. \<Fact-9\> \<Fact-4\>     |
|                                |                                |
| 5\. \<Fact-6\> \<Fact-5\>      | 20\. \<Fact-9\> \<Fact-5\>     |
|                                |                                |
| 6\. \<Fact-7\> \<Fact-10\>     | 21\. \<Fact-1\> \<Fact-10\>    |
|                                |                                |
| 7\. \<Fact-7\> \<Fact-11\>     | 22\. \<Fact-1\> \<Fact-11\>    |
|                                |                                |
| 8\. \<Fact-7\> \<Fact-3\>      | 23\. \<Fact-1\> \<Fact-3\>     |
|                                |                                |
| 9\. \<Fact-7\> \<Fact-4\>      | 24\. \<Fact-1\> \<Fact-4\>     |
|                                |                                |
| 10\. \<Fact-7\> \<Fact-5\>     | 25\. \<Fact-1\> \<Fact-5\>     |
|                                |                                |
| 11\. \<Fact-8\> \<Fact-10\>    | 26\. \<Fact-2\> \<Fact-10\>    |
|                                |                                |
| 12\. \<Fact-8\> \<Fact-11\>    | 27\. \<Fact-2\> \<Fact-11\>    |
|                                |                                |
| 13 \<Fact-8\> \<Fact-3\>       | 28\. \<Fact-2\> \<Fact-3\>     |
|                                |                                |
| 14\. \<Fact-8\> \<Fact-4\>     | 29\. \<Fact-2\> \<Fact-4\>     |
|                                |                                |
| 15\. \<Fact-8\> \<Fact-5\>     | 30\. \<Fact-2\> \<Fact-5\>     |
+--------------------------------+--------------------------------+

#### 12.9.12.3 Query Definition

A **query** is a boolean expression applied to a fact‑set to determine if the fact‑set meets further restrictions. If the return value of this expression for an fact‑set is not the symbol **FALSE**, the fact‑set is said to satisfy the query.

Syntax

\<query\> ::= \<boolean-expression\>

Example

Continuing the previous example, one query might be that the two facts in an ordered pair have the same age.

(= (fact-slot-value ?man-or-boy age) (fact-slot-value ?woman-or-girl age))

Within a query, slots of fact‑set members can be directly read with a shorthand notation similar to that used by instances in message‑handlers.

Syntax

\<fact-set-member-variable\>:\<slot-name\>

Example

The previous example could be rewritten as:

(= ?man-or-boy:age ?woman-or-girl:age)

Since only fact‑sets which satisfy a query are of interest, and the query is evaluated for all possible fact‑sets, the query should not have any side‑effects.

#### 12.9.12.4 Distributed Action Definition

A **distributed action** is a user‑defined expression evaluated for each fact‑set which satisfies a query.

Action Syntax

\<action\> ::= \<expression\>

Example

Continuing the previous example, one distributed action might be to simply print out the ordered pair to the screen.

(println \"(\" ?man-or-boy:name \",\" ?woman-or-girl:name \")\")

#### 12.9.12.5 Scope in Fact‑set Query Functions

Fact‑set member variables are only in scope within the fact‑set query function. Attempting to use fact‑set member variables in an outer scope will generate an error. If a variable from an outer scope is not masked by a fact‑set member variable, then that variable may be referenced within the query and action. In addition, rebinding variables within a fact‑set function action is allowed. However, attempts to rebind fact‑set member variables will generate errors. Binding variables is not allowed within a query. Fact‑set query functions can be nested.

Example 1

CLIPS\>

(deffunction count-facts (?template)

(bind ?count 0)

(do-for-all-facts ((?fct ?template)) TRUE

(bind ?count (+ ?count 1)))

?count)

CLIPS\>

(deffunction count-facts-2 (?template)

(length (find-all-facts ((?fct ?template)) TRUE)))

CLIPS\> (count-facts woman)

3

CLIPS\> (count-facts-2 boy)

4

CLIPS\>

Example 2

(deffunction last-fact (?template)

(any-factp ((?fct ?template)) TRUE)

?fct)

\[PRCCODE3\] Undefined variable ?fct referenced in deffunction.

ERROR:

(deffunction ORDERS::last-fact

(?template)

(any-factp ((?fct ?template))

TRUE)

?fct

)

CLIPS\>

#### 12.9.12.6 Errors during Fact‑set Query Functions

If an error occurs during an fact‑set query function, the function will be immediately terminated and the return value will be the symbol **FALSE**.

#### 12.9.12.7 Halting and Returning Values from Query Functions

The **break** and **return** functions are valid inside the action of the fact‑set query functions **do‑for‑fact**, **do‑for‑all‑facts**, and **delayed‑do‑for‑all‑facts**. The **return** function is only valid if it is applicable in the outer scope, whereas the **break** function halts the query.

#### 12.9.12.8 Fact‑set Query Functions

The fact query system in CLIPS provides six functions. For a given set of facts, all six query functions will iterate over these facts in the same order. However, if a particular fact is retracted and reasserted, the iteration order will change.

##### 12.9.12.8.1 Testing if Any Fact‑set Satisfies a Query

The **any-factp** function applies a query to each fact‑set which matches the template. If a fact‑set satisfies the query, then the function is immediately terminated, and the return value is the symbol **TRUE**; otherwise, the symbol **FALSE** is returned.

Syntax

(any‑factp \<fact-set-template\> \<query\>)

Example

Are there any men over age 30?

CLIPS\> (any-factp ((?man man)) (\> ?man:age 30))

TRUE

CLIPS\>

##### 12.9.12.8.2 Determining the First Fact‑set Satisfying a Query

The **find-fact** function applies a query to each fact‑set which matches the template. If a fact‑set satisfies the query, then the function is immediately terminated, and a multifield value containing the fact‑set is returned. Otherwise, the return value is a zero‑length multifield value. Each field of the multifield value is a fact‑address representing a fact‑set member.

Syntax

(find‑fact \<fact-set-template\> \<query\>)

Example

Find the first pair of a man and a woman who have the same age.

CLIPS\>

(find-fact((?m man) (?w woman)) (= ?m:age ?w:age))

(\<Fact-1\> \<Fact-3\>)

CLIPS\>

##### 12.9.12.8.3 Determining All Fact‑sets Satisfying a Query

The **find-all-facts** function applies a query to each fact‑set which matches the template. Each fact‑set which satisfies the query is stored in a multifield value. This multifield value is returned when the query has been applied to all possible fact‑sets. If there are n facts in each fact‑set, and m fact‑sets satisfied the query, then the length of the returned multifield value will be n \* m. The first n fields correspond to the first fact‑set, and so on. Each field of the multifield value is an fact‑address representing a fact‑set member.

Syntax

(find‑all‑facts \<fact-set-template\> \<query\>)

Example

Find all pairs of a man and a woman who have the same age.

CLIPS\>

(find-all-facts ((?m man) (?w woman)) (= ?m:age ?w:age))

(\<Fact-1\> \<Fact-3\> \<Fact-2\> \<Fact-4\>)

CLIPS\>

##### 12.9.12.8.4 Executing an Action for the First Fact‑set Satisfying a Query

The **do-for-fact** function applies a query to each fact‑set which matches the template. If a fact‑set satisfies the query, the specified action is executed, and the function is immediately terminated. The return value is the evaluation of the action. If no fact‑set satisfied the query, then the return value is the symbol **FALSE**.

Syntax

(do‑for‑fact \<fact-set-template\> \<query\> \<action\>\*)

Example

Print out the first triplet of different people that have the same age. The calls to **neq** in the query eliminate the permutations where two or more members of the instance‑set are identical.

CLIPS\>

(do-for-fact ((?p1 girl boy woman man)

(?p2 girl boy woman man)

(?p3 girl boy woman man))

(and (= ?p1:age ?p2:age ?p3:age)

(neq ?p1 ?p2)

(neq ?p1 ?p3)

(neq ?p2 ?p3))

(println ?p1:name \" \" ?p2:name \" \" ?p3:name))

Girl-2 Boy-2 Boy-3

CLIPS\>

##### 12.9.12.8.5 Executing an Action for All Fact‑sets Satisfying a Query

The **do-for-all-facts** function applies a query to each fact‑set which matches the template. If a fact‑set satisfies the query, the specified action is executed. The return value is the evaluation of the action for the last fact‑set which satisfied the query. If no fact‑set satisfied the query, then the return value is the symbol **FALSE**.

Syntax

(do‑for‑all‑facts \<fact-set-template\> \<query\> \<action\>\*)

Example

Print out all triplets of different people that have the same age. The calls to **str‑compare** limit the fact‑sets which satisfy the query to combinations instead of permutations. Without these restrictions, two fact‑sets which differed only in the order of their members would both satisfy the query.

CLIPS\>\
(do-for-all-facts ((?p1 girl boy woman man)\
(?p2 girl boy woman man)\
(?p3 girl boy woman man))

(and (= ?p1:age ?p2:age ?p3:age)

(\> (str-compare ?p1:name ?p2:name) 0)

(\> (str-compare ?p2:name ?p3:name) 0))

(println ?p1:name \" \" ?p2:name \" \" ?p3:name))

Girl-2 Boy-3 Boy-2

Girl-2 Boy-4 Boy-2

Girl-2 Boy-4 Boy-3

Boy-4 Boy-3 Boy-2

CLIPS\>

##### 12.9.12.8.6 Executing a Delayed Action for All Fact‑sets Satisfying a Query

The **delayed-do-for-all-facts** function is similar to the **do‑for‑all‑facts** function except that it groups all fact‑sets which satisfy the query into an intermediary multifield value. If there are no fact‑sets which satisfy the query, then the function returns the symbol **FALSE**. Otherwise, the specified action is executed for each fact‑set in the multifield value, and the return value is the evaluation of the action for the last fact‑set to satisfy the query. The intermediary multifield value is discarded. This function should be used in lieu of **do‑for‑all‑facts** when the action applied to one fact‑set would change the result of the query for another fact‑set (unless that is the desired effect). Even though execution of the action is delayed until all fact-sets are computed, retracting a fact in the actions for one fact-set will exclude execution of the action for subsequent fact-sets containing that fact.

Syntax

(delayed‑do‑for‑all‑facts \<fact-set-template\>

\<query\> \<action\>\*)

Example

Delete all boys with the greatest age. The test in this case is another query function which determines if there are any older boys than the one currently being examined. The action needs to be delayed until all boys have been processed, or the greatest age will decrease as the older boys are deleted.

CLIPS\> (watch facts)

CLIPS\>

(delayed-do-for-all-facts ((?b1 boy))

(not (any-factp ((?b2 boy)) (\> ?b2:age ?b1:age)))

(retract ?b1))

\<== f-6 (boy (name Boy-1) (sex male) (age 8))

CLIPS\> (unwatch facts)

CLIPS\> (reset)

CLIPS\> (watch facts)

CLIPS\>

(do-for-all-facts ((?b1 boy))

(not (any-factp ((?b2 boy)) (\> ?b2:age ?b1:age)))

(retract ?b1))

\<== f-6 (boy (name Boy-1) (sex male) (age 8))

\<== f-7 (boy (name Boy-2) (sex male) (age 4))

\<== f-8 (boy (name Boy-3) (sex male) (age 4))

\<== f-9 (boy (name Boy-4) (sex male) (age 4))

CLIPS\> (unwatch facts)

CLIPS\>

### 12.9.13 Getting the Fact-address Associated with a Fact‑Index

The **fact‑index-to-fact** function returns the fact-address associated with a fact‑index (an integer). If there is no fact-address associated with the fact-index, the symbol **FALSE** is returned.

Syntax

(fact-index-to-fact \<fact-index\>)

Example

CLIPS\> (fact-index-to-fact 1)

FALSE

CLIPS\> (assert (numbers 1 2 3))

\<Fact-1\>

CLIPS\> (fact-index-to-fact 1)

\<Fact-1\>

CLIPS\>

## 12.10 Deffacts Functions

The following functions provide ancillary capabilities for the deffacts construct.

### 12.10.1 Getting the List of Deffacts

The **get‑deffacts‑list** function returns a multifield value containing the names of all deffacts constructs visible to the module specified by \<module-name\> or to the current module if none is specified. If the symbol **\*** is specified as the module name, then all deffacts are returned.

Syntax

(get‑deffacts‑list \[\<module-name\>\])

Example

CLIPS\> (clear)

CLIPS\> (get-deffacts-list)

()

CLIPS\>

(deffacts initial

(grocery-list milk eggs cheese)

(item milk)

(item eggs)

(item cheese))

CLIPS\> (get-deffacts-list)

(initial)

CLIPS\>

### 12.10.2 Determining the Module in which a Deffacts is Defined

The **deffacts-module** function returns the module in which the specified deffacts name is defined.

Syntax

(deffacts‑module \<deffacts-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(deffacts initial

(grocery-list milk eggs cheese)

(item milk)

(item eggs)

(item cheese))

CLIPS\> (deffacts-module initial)

MAIN

CLIPS\>

## 12.11 Defrule Functions

The following functions provide ancillary capabilities for the defrule construct.

### 12.11.1 Getting the List of Defrules

The **get‑defrule‑list** function returns a multifield value containing the names of all defrule constructs visible to the module specified by \<module-name\> or to the current module if none is specified. If the symbol **\*** is specified as the module name, then all defrules are returned.

Syntax

(get‑defrule‑list)

### 12.11.2 Determining the Module in which a Defrule is Defined

The **defrule-module** function returns the module in which the specified defrule name is defined.

Syntax

(defrule‑module \<defrule-name\>)

## 12.12 Agenda Functions

The following functions provide ancillary capabilities for manipulating the agenda.

### 12.12.1 Getting the Current Focus

The **get‑focus** function returns the module name of the current focus. If the focus stack is empty, then the symbol **FALSE** is returned.

Syntax

(get‑focus)

Example

CLIPS\> (clear)

CLIPS\> (get-focus)

MAIN

CLIPS\> (defmodule COLLECT)

CLIPS\> (defmodule PROCESS)

CLIPS\> (focus COLLECT PROCESS)

TRUE

CLIPS\> (get-focus)

COLLECT

CLIPS\>

### 12.12.2 Getting the Focus Stack

The **get‑focus‑stack** function returns a multifield value containing all of the module names in the focus stack. A multifield value of length zero is returned if the focus stack is empty.

Syntax

(get‑focus‑stack)

Example

CLIPS\> (clear)

CLIPS\> (get-focus-stack)

(MAIN)

CLIPS\> (run)

CLIPS\> (get-focus-stack)

()

CLIPS\> (defmodule COLLECT)

CLIPS\> (defmodule PROCESS)

CLIPS\> (focus COLLECT PROCESS)

TRUE

CLIPS\> (get-focus-stack)

(COLLECT PROCESS)

CLIPS\>

### 12.12.3 Removing the Current Focus from the Focus Stack

The **pop‑focus** function removes the current focus from the focus stack and returns the module name of the current focus. If the focus stack is empty, then the symbol **FALSE** is returned.

Syntax

(pop‑focus)

Example

CLIPS\> (clear)

CLIPS\> (list-focus-stack)

MAIN

CLIPS\> (pop-focus)

MAIN

CLIPS\> (list-focus-stack)

CLIPS\> (defmodule COLLECT)

CLIPS\> (defmodule PROCESS)

CLIPS\> (focus COLLECT PROCESS)

TRUE

CLIPS\> (list-focus-stack)

COLLECT

PROCESS

CLIPS\> (pop-focus)

COLLECT

CLIPS\> (list-focus-stack)

PROCESS

CLIPS\>

## 12.13 Defglobal Functions

The following functions provide ancillary capabilities for the defglobal construct.

### 12.13.1 Getting the List of Defglobals

The **get‑defglobal‑list** function returns a multifield value containing the names of all global variables visible to the module specified by \<module-name\> or to the current module if none is specified. If the symbol **\*** is specified as the module name, then all globals are returned.

Syntax

(get‑defglobal‑list \[\<module-name\>\])

### 12.13.2 Determining the Module in which a Defglobal is Defined

The **defglobal-module** function returns the module in which the specified defglobal name is defined.

Syntax

(defglobal‑module \<defglobal-name\>)

## 12.14 Deffunction Functions

The following functions provide ancillary capabilities for the deffunction construct.

### 12.14.1 Getting the List of Deffunctions

The **get‑deffunction‑list** function returns a multifield value containing the names of all deffunction constructs visible to the module specified by \<module-name\> or to the current module if none is specified. If the symbol **\*** is specified as the module name, then all deffunctions are returned.

Syntax

(get‑deffunction‑list \[\<module-name\>\])

### 12.14.2 Determining the Module in which a Deffunction is Defined

The **deffunction-module** function returns the module in which the specified deffunction name is defined.

Syntax

(deffunction‑module \<deffunction-name\>)

## 12.15 Generic Function Functions

The following functions provide ancillary capabilities for generic function methods.

### 12.15.1 Getting the List of Defgenerics

The **get‑defgeneric‑list** function returns a multifield value containing the names of all defgeneric constructs that are currently defined.

Syntax

(get‑defgeneric‑list)

### 12.15.2 Determining the Module in which a Generic Function is Defined

The **defgeneric-module** function returns the module in which the specified defgeneric name is defined.

Syntax

(defgeneric‑module \<defgeneric-name\>)

### 12.15.3 Getting the List of Defmethods

The **get‑defmethod‑list** function returns a multifield value containing method name/indices pairs for all defmethod constructs that are currently defined. The optional \<generic‑function-name\> parameter restricts the methods return value to only those of the specified generic function.

Syntax

(get‑defmethod‑list \[\<generic-function-name\>\])

Example

CLIPS\> (clear)

CLIPS\> (get-defmethod-list)

()

CLIPS\> (defmethod add ((?x MULTIFIELD) (?y MULTIFIELD)) (create\$ ?x ?y))

CLIPS\> (defmethod add ((?x STRING) (?y STRING)) (str-cat ?x ?y))

CLIPS\>

(defmethod subtract ((?x MULTIFIELD) (?y MULTIFIELD)) (delete-member\$ ?x ?y))

CLIPS\> (get-defmethod-list)

(add 1 add 2 subtract 1)

CLIPS\> (get-defmethod-list add)

(add 1 add 2)

CLIPS\>

### 12.15.4 Type Determination

The **type** function returns a symbol which is the name of the type (or class) of its argument. This function is equivalent to the **class** function, but, unlike the **class** function, it is available even when COOL is not installed.

Syntax

(type \<expression\>)

Example

CLIPS\> (clear)

CLIPS\> (type (+ 2 2))

INTEGER

CLIPS\> (defclass CAR (is-a USER))

CLIPS\> (make-instance Rolls-Royce of CAR)

\[Rolls-Royce\]

CLIPS\> (type Rolls-Royce)

SYMBOL

CLIPS\> (type \[Rolls-Royce\])

CAR

CLIPS\>

### 12.15.5 Existence of Shadowed Methods

If called from a method for a generic function, the **next‑methodp** function will return the symbol **TRUE** if there is another method shadowed by the current one; otherwise, the function will return the symbol **FALSE**.

Syntax

(next‑methodp)

### 12.15.6 Calling Shadowed Methods

If the conditions are such that the **next‑methodp** function would return the symbol **TRUE**, then calling the **call‑next‑method** function will execute the shadowed method; otherwise, a method execution error will occur. In the event of an error, the return value of this function is the symbol **FALSE**, otherwise it is the return value of the shadowed method. The shadowed method is passed the same arguments as the calling method.

A method may continue execution after calling **call‑next‑method**. In addition, a method may make multiple calls to **call‑next‑method**, and the same shadowed method will be executed each time.

Syntax

(call‑next‑method)

Example

CLIPS\> (clear)

CLIPS\>

(defmethod describe ((?a INTEGER))

(if (next-methodp) then

(bind ?extension (str-cat \" \" (call-next-method)))

else

(bind ?extension \"\"))

(str-cat \"INTEGER\" ?extension))

CLIPS\> (describe 3)

\"INTEGER\"

CLIPS\>

(defmethod describe ((?a NUMBER))

\"NUMBER\")

CLIPS\> (describe 3)

\"INTEGER NUMBER\"

CLIPS\> (describe 3.0)

\"NUMBER\"

CLIPS\>

### 12.15.7 Calling Shadowed Methods with Overrides

The **override‑next‑method** function is similar to **call‑next‑method**, except that new arguments can be provided. This allows one method to act as a wrapper for another and set up a special environment for the shadowed method. From the set of methods which are more general than the currently executing one, the most specific method which is applicable to the new arguments is executed. (In contrast, **call‑next‑method** calls the next most specific method which is applicable to the same arguments as the currently executing one received.) A recursive call to the generic function itself should be used in lieu of **override‑next‑method** if the most specific of all methods for the generic function which is applicable to the new arguments should be executed.

Syntax

(override‑next‑method \<expression\>\*)

Example

CLIPS\> (clear)

CLIPS\>

(defmethod + ((?a INTEGER) (?b INTEGER))

(override-next-method (\* ?a 2) (\* ?b 3)))

CLIPS\> (list-defmethods +)

\+ #2 (INTEGER) (INTEGER)

\+ #SYS1 (NUMBER) (NUMBER) (\$? NUMBER)

For a total of 2 methods.

CLIPS\> (preview-generic + 1 2)

\+ #2 (INTEGER) (INTEGER)

\+ #SYS1 (NUMBER) (NUMBER) (\$? NUMBER)

CLIPS\> (watch methods)

CLIPS\> (+ 1 2)

MTH \>\> +:#2 ED:1 (1 2)

MTH \>\> +:#SYS1 ED:2 (2 6)

MTH \<\< +:#SYS1 ED:2 (2 6)

MTH \<\< +:#2 ED:1 (1 2)

8

CLIPS\> (unwatch methods)

CLIPS\>

### 12.15.8 Calling a Specific Method

The **call‑specific‑method** function allows a particular method of a generic function to be called without regards to method precedence. This allows method precedence to be bypassed when absolutely necessary. The method must be applicable to the arguments passed. Shadowed methods can still be called via **call‑next‑method** and **override‑next‑method**.

Syntax

(call‑specific‑method \<generic-function\> \<method-index\>

\<expression\>\*)

Example

CLIPS\> (clear)

CLIPS\>

(defmethod + ((?a INTEGER) (?b INTEGER))

(\* (- ?a ?b) (- ?b ?a)))

CLIPS\> (list-defmethods +)

\+ #2 (INTEGER) (INTEGER)

\+ #SYS1 (NUMBER) (NUMBER) (\$? NUMBER)

For a total of 2 methods.

CLIPS\> (preview-generic + 1 2)

\+ #2 (INTEGER) (INTEGER)

\+ #SYS1 (NUMBER) (NUMBER) (\$? NUMBER)

CLIPS\> (watch methods)

CLIPS\> (+ 1 2)

MTH \>\> +:#2 ED:1 (1 2)

MTH \<\< +:#2 ED:1 (1 2)

-1

CLIPS\> (call-specific-method + 1 1 2)

MTH \>\> +:#SYS1 ED:1 (1 2)

MTH \<\< +:#SYS1 ED:1 (1 2)

3

CLIPS\> (unwatch methods)

CLIPS\>

### 12.15.9 Getting the Restrictions of Defmethods

The **get‑method‑restrictions** function returns a multifield value containing information about the restrictions for the specified method using the following format:

\<minimum-number-of-arguments\>

\<maximum-number-of-arguments\> (can be -1 for wildcards)

\<number-of-restrictions\>

\<multifield-index-of-first-restriction-info\>

.

.

.

\<multifield-index-of-nth-restriction-info\>

\<first-restriction-query\> (TRUE or FALSE)

\<first-restriction-class-count\>

\<first-restriction-first-class\>

.

.

.

\<first-restriction-nth-class\>

.

.

.

\<mth-restriction-class-count\>

\<mth-restriction-first-class\>

.

.

.

\<mth-restriction-nth-class\>

Syntax

(get‑method‑restrictions \<generic-function-name\>

\<method-index\>)

Example

CLIPS\> (clear)

CLIPS\> (defmethod example 50 ((?a INTEGER SYMBOL) (?b (= 1 1)) \$?c))

CLIPS\> (get-method-restrictions example 50)

(2 -1 3 7 11 13 FALSE 2 INTEGER SYMBOL TRUE 0 FALSE 0)

CLIPS\>

## 12.16 Defclass Functions

### 12.16.1 Getting the List of Defclasses

The **get‑defclass‑list** function returns a multifield value containing the names of all defclass constructs visible to the module specified by \<module-name\> or to the current module if none is specified. If the symbol **\*** is specified as the module name, then all defclasses are returned.

Syntax

(get‑defclass‑list \[\<module-name\>\])

Example

CLIPS\> (clear)

CLIPS\> (get-defclass-list)

(FLOAT INTEGER SYMBOL STRING MULTIFIELD EXTERNAL-ADDRESS FACT-ADDRESS INSTANCE-ADDRESS INSTANCE-NAME OBJECT PRIMITIVE NUMBER LEXEME ADDRESS INSTANCE USER)

CLIPS\> (defclass ORDER (is-a USER))

CLIPS\> (defclass CUSTOMER (is-a USER))

CLIPS\> (get-defclass-list)

(FLOAT INTEGER SYMBOL STRING MULTIFIELD EXTERNAL-ADDRESS FACT-ADDRESS INSTANCE-ADDRESS INSTANCE-NAME OBJECT PRIMITIVE NUMBER LEXEME ADDRESS INSTANCE USER ORDER CUSTOMER)

CLIPS\>

### 12.16.2 Determining the Module in which a Defclass is Defined

The **defclass-module** function returns the module in which the specified defclass name is defined.

Syntax

(defclass‑module \<defclass-name\>)

### 12.16.3 Determining if a Class Exists

The **class-existp** function returns the symbol **TRUE** if the specified class is defined; otherwise, it returns the symbol **FALSE**.

Syntax

(class‑existp \<class-name\>)

### 12.16.4 Superclass Determination

The **superclassp** function returns the symbol **TRUE** if the first class is a superclass of the second class; otherwise, it returns the symbol **FALSE**.

Syntax

(superclassp \<class1-name\> \<class2-name\>)

### 12.16.5 Subclass Determination

The **subclassp** function returns the symbol **TRUE** if the first class is a subclass of the second class; otherwise, it returns the symbol **FALSE**.

Syntax

(subclassp \<class1-name\> \<class2-name\>)

### 12.16.6 Slot Existence

The **slot-existp** function returns the symbol **TRUE** if the specified slot is present in the specified class; otherwise, it returns the symbol **FALSE**. If the **inherit** keyword is specified, then the slot may be inherited; otherwise it must be directly defined in the specified class.

Syntax

(slot-existp \<class\> \<slot\> \[inherit\])

### 12.16.7 Testing whether a Slot is Writable 

The **slot-writablep** function returns the symbol **TRUE** if the specified slot in the specified class is writable; otherwise, it returns the symbol **FALSE**. An error is generated if the specified class or slot does not exist.

Syntax

(slot‑writablep \<class-expression\> \<slot-name-expression\>)

### 12.16.8 Testing whether a Slot is Initializable

The **slot-initablep** function returns the symbol **TRUE** if the specified slot in the specified class is initializable; otherwise, it returns the symbol **FALSE**. An error is generated if the specified class or slot does not exist.

Syntax

(slot‑initablep \<class-expression\> \<slot-name-expression\>)

### 12.16.9 Testing whether a Slot is Public

The **slot-publicp** function returns the symbol **TRUE** if the specified slot in the specified class is public; otherwise, it returns the symbol **FALSE**. An error is generated if the specified class or slot does not exist.

Syntax

(slot‑publicp \<class-expression\> \<slot-name-expression\>)

### 12.16.10 Testing whether a Slot can be Accessed Directly

The **slot-direct-accessp** function returns the symbol **TRUE** if the specified slot in the specified class can be accessed directly; otherwise, it returns the symbol **FALSE**. An error is generated if the specified class or slot does not exist.

Syntax

(slot‑direct‑accessp \<class-expression\> \<slot-name-expression\>)

### 12.16.11 Message‑handler Existence

The **message-handler-existp** function returns the symbol **TRUE** if the specified message‑handler is defined (directly only, not by inheritance) for the class; otherwise, it returns the symbol **FALSE**.

Syntax

(message‑handler‑existp \<class-name\> \<handler-name\> \[\<handler-type\>\])

\<handler-type\> ::= around \| before \| primary \| after

If unspecified, the \<handler-type\> term defaults to the symbol **primary**.

### 12.16.12 Determining if a Class can have Direct Instances

The **class-abstractp** function returns the symbol **TRUE** if the specified class is abstract (i.e. the class cannot have direct instances); otherwise, it returns the symbol **FALSE**.

Syntax

(class‑abstractp \<class-name\>)

### 12.16.13 Determining if a Class can Satisfy Object Patterns

The **class-reactivep** function returns the symbol **TRUE** if the specified class is reactive (i.e. objects of the class can match object patterns); otherwise it returns the symbol **FALSE**.

Syntax

(class‑reactivep \<class-name\>)

### 12.16.14 Getting the List of Superclasses for a Class

The **class-superclasses** function returns a multifield value containing the names of the direct superclasses of the specified class. If the optional argument **inherit** is specified, indirect superclasses are also included. A multifield value of length zero is returned if an error occurs.

Syntax

(class‑superclasses \<class-name\> \[inherit\])

Example

CLIPS\> (class-superclasses INTEGER)

(NUMBER)

CLIPS\> (class-superclasses INTEGER inherit)

(NUMBER PRIMITIVE OBJECT)

CLIPS\>

### 12.16.15 Getting the List of Subclasses for a Class

The **class-subclasses** function returns a multifield value containing the names of the direct subclasses of the specified class. If the optional argument **inherit** is specified, indirect subclasses are also included. A multifield value of length zero is returned if an error occurs.

Syntax

(class‑subclasses \<class-name\> \[inherit\])

Example

CLIPS\> (class-subclasses PRIMITIVE)

(NUMBER LEXEME MULTIFIELD ADDRESS INSTANCE)

CLIPS\> (class-subclasses PRIMITIVE inherit)

(NUMBER INTEGER FLOAT LEXEME SYMBOL STRING MULTIFIELD ADDRESS EXTERNAL-ADDRESS FACT-ADDRESS INSTANCE-ADDRESS INSTANCE INSTANCE-NAME)

CLIPS\>

### 12.16.16 Getting the List of Slots for a Class

The **class-slots** function returns a multifield value containing the names of the explicitly defined slots of the specified class. If the optional argument **inherit** is given, inherited slots are also included. A multifield value of length zero is returned if an error occurs.

Syntax

(class‑slots \<class-name\> \[inherit\])

Example

CLIPS\> (clear)

CLIPS\>

(defclass VEHICLE (is-a USER)

(slot wheels)

(slot engine))

CLIPS\>

(defclass CAR (is-a VEHICLE)

(slot make)

(slot model))

CLIPS\> (class-slots CAR)

(make model)

CLIPS\> (class-slots CAR inherit)

(wheels engine make model)

CLIPS\>

### 12.16.17 Getting the List of Message‑Handlers for a Class

The **get-defmessage-handler-list** function returns a multifield value containing the class names, message names, and message types of the message‑handlers attached directly to the specified class (implicit slot‑accessors are not included). If the optional argument **inherit** is specified, inherited message‑handlers are also included. A multifield value of length zero is returned if an error occurs.

Syntax

(get‑defmessage‑handler‑list \<class-name\> \[inherit\])

Example

CLIPS\> (clear)

CLIPS\>

(defclass PERSON

(is-a USER)

(slot first-name (create-accessor ?NONE))

(slot middle-name (create-accessor ?NONE))

(slot last-name (create-accessor ?NONE)))

CLIPS\>

(defmessage-handler PERSON full-name ()

(str-cat ?self:first-name \" \" ?self:middle-name \" \" ?self:last-name))

CLIPS\> (get-defmessage-handler-list PERSON)

(PERSON full-name primary)

CLIPS\> (get-defmessage-handler-list PERSON inherit)

(USER init primary USER delete primary USER create primary USER print primary USER direct-modify primary USER message-modify primary USER direct-duplicate primary USER message-duplicate primary PERSON full-name primary)

CLIPS\>

### 12.16.18 Getting the List of Facets for a Slot

The **slot-facets** function returns a multifield value containing the facet values for the specified slot (the slot can be inherited or explicitly defined for the class). A multifield value of length zero is returned if an error occurs. The following table lists the meaning of each field position and its possible values.

+-------------+-----------------------+--------------------+---------------------------------------------+
| > **Field** | > **Meaning**         | **Values**         | **Explanation**                             |
+=============+=======================+====================+=============================================+
| > 1         | > Field Type          | > SGL/MLT          | > Single-field or multifield                |
+-------------+-----------------------+--------------------+---------------------------------------------+
| > 2         | > Default Value       | > STC/DYN/NIL      | > Static, dynamic, or none                  |
+-------------+-----------------------+--------------------+---------------------------------------------+
| > 3         | > Inheritance         | > INH/NIL          | > Inheritable by other classes or not       |
+-------------+-----------------------+--------------------+---------------------------------------------+
| > 4         | > Access              | > RW/R/INT         | > Read-write, read-only, or initialize-only |
+-------------+-----------------------+--------------------+---------------------------------------------+
| > 5         | > Storage             | > LCL/SHR          | > Local or shared                           |
+-------------+-----------------------+--------------------+---------------------------------------------+
| > 6         | > Pattern-Match       | > RCT/NIL          | > Reactive or non-reactive                  |
+-------------+-----------------------+--------------------+---------------------------------------------+
| > 7         | > Source              | > EXC/CMP          | > Exclusive or composite                    |
+-------------+-----------------------+--------------------+---------------------------------------------+
| > 8         | > Visibility          | > PUB/PRV          | > Public or private                         |
+-------------+-----------------------+--------------------+---------------------------------------------+
| > 9         | > Automatic Accessors | > R/W/RW/NIL       | > Read, write, read-write, or none          |
+-------------+-----------------------+--------------------+---------------------------------------------+
| > 10        | > Override-Message    | > \<message-name\> | > Name of message sent for slot-overrides   |
+-------------+-----------------------+--------------------+---------------------------------------------+

Syntax

(slot‑facets \<class-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass PERSON

(is-a USER)

(multislot full-name))

CLIPS\> (slot-facets PERSON full-name)

(MLT STC INH RW LCL RCT EXC PRV RW put-full-name)

CLIPS\>

### 12.16.19 Getting the List of Source Classes for a Slot

The **slot-sources** function returns a multifield value containing the names of the classes which provide facets for a slot of the specified class. In the case of an exclusive slot, this multifield will be of length one and contain the name of the contributing class. However, composite slots may have facets from many different classes. A multifield of length zero is returned if an error occurs.

Syntax

(slot‑sources \<class-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass PERSON (is-a USER)

(slot full-name (default \"\"))

(slot age (default 0)))

CLIPS\>

(defclass LOCKED-PERSON (is-a PERSON)

(slot full-name

(source composite)

(access initialize-only)))

CLIPS\> (slot-sources PERSON full-name)

(PERSON)

CLIPS\> (slot-sources LOCKED-PERSON full-name)

(PERSON LOCKED-PERSON)

CLIPS\> (slot-sources LOCKED-PERSON age)

(PERSON)

CLIPS\>

### 12.16.20 Getting the Primitive Types for a Slot

The **slot-types** function returns a multifield value containing the names of the primitive types allowed for a slot. A multifield of length zero is returned if an error occurs.

Syntax

(slot‑types \<class-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass PERSON

(is-a USER)

(slot full-name (type STRING))

(slot age (type INTEGER)))

CLIPS\> (slot-types PERSON full-name)

(STRING)

CLIPS\> (slot-types PERSON age)

(INTEGER)

CLIPS\>

### 12.16.21 Getting the Cardinality for a Slot

The **slot-cardinality** function returns a multifield value containing the minimum and maximum cardinality allowed for a multifield slot of the specified class. A maximum cardinality of infinity is indicated by the symbol **+oo** (the plus character followed by two lowercase 'o' characters---not zeroes). A multifield of length zero is returned for single field slots or if an error occurs.

Syntax

(slot‑cardinality \<class-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass POLYGON (is-a USER)

(slot sides)

(multislot coordinates

(type INTEGER)

(cardinality 6 ?VARIABLE)))

CLIPS\> (slot-cardinality POLYGON sides)

()

CLIPS\> (slot-cardinality POLYGON coordinates)

(6 +oo)

CLIPS\>

### 12.16.22 Getting the Allowed Values for a Slot

The **slot-allowed-values** function returns a multifield value containing the allowed values for a slot (specified in any of allowed‑... facets for the slots). If no allowed‑... facets were specified for the slot, then the symbol **FALSE** is returned. A multifield of length zero is returned if an error occurs.

Syntax

(slot‑allowed‑values \<class-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass PERSON (is-a USER)

(slot full-name)

(slot gender (allowed-values male female)))

CLIPS\> (slot-allowed-values PERSON full-name)

FALSE

CLIPS\> (slot-allowed-values PERSON gender)

(male female)

CLIPS\>

### 12.16.23 Getting the Numeric Range for a Slot

The **slot-range** function returns a multifield value containing the minimum and maximum numeric ranges allowed a slot. A minimum value of infinity is indicated by the symbol **‑oo** (the minus character followed by two lowercase 'o' characters---not zeroes). A maximum value of infinity is indicated by the symbol **+oo** (the plus character followed by two lowercase 'o' characters). The symbol **FALSE** is returned for slots in which numeric values are not allowed. A multifield of length zero is returned if an error occurs.

Syntax

(slot‑range \<class-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass PERSON (is-a USER)

(slot full-name (type STRING))

(slot age (type INTEGER) (range 0 120))

(slot net-worth (type FLOAT)))

CLIPS\> (slot-range PERSON full-name)

FALSE

CLIPS\> (slot-range PERSON age)

(0 120)

CLIPS\> (slot-range PERSON net-worth)

(-oo +oo)

CLIPS\>

### 12.16.24 Getting the Default Value for a Slot

The **slot-default-value** function returns the default value associated with a slot. If a slot has a dynamic default, the expression will be evaluated when this function is called. The symbol **FALSE** is returned if an error occurs.

Syntax

(slot‑default-value \<class-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass ORDER (is-a USER)

(slot id (default-dynamic (gensym)))

(slot item (type STRING) (default ?NONE))

(slot quantity (type INTEGER) (default 1))

(slot details (type STRING)))

CLIPS\> (slot-default-value ORDER id)

gen1

CLIPS\> (slot-default-value ORDER item)

?NONE

CLIPS\> (slot-default-value ORDER quantity)

1

CLIPS\> (slot-default-value ORDER details)

\"\"

CLIPS\>

### 12.16.25 Setting the Defaults Mode for Classes

The **set-class-defaults-mode** function sets the defaults mode used when classes are defined. The old mode is the return value of this function.

Syntax

(set‑class-defaults-mode \<mode\>)

The \<mode\> term is either the symbol **convenience** or **conservation**. By default, the class defaults mode is **convenience**. If the mode is **convenience**, then for the purposes of role inheritance, system defined class behave as concrete classes; for the purpose of pattern-match inheritance, system defined classes behave as reactive classes unless the inheriting class is abstract; and the default setting for the create-accessor facet of the class' slots is **read‑write**. If the class defaults mode is **conservation**, then the role and reactivity of system-defined classes is unchanged for the purposes of role and pattern-match inheritance and the default setting for the create-accessor facet of the class' slots is **?NONE**.

### 12.16.26 Getting the Defaults Mode for Classes

The **get-class-defaults-mode** function returns the current defaults mode used when classes are defined (**convenience** or **conservation**).

Syntax

(get‑class-defaults-mode)

### 12.16.27 Getting the Allowed Classes for a Slot

The **slot-allowed-classes** function returns a multifield value containing the allowed classes for a slot (specified by the **allowed‑classes** facet for the slot). If the **allowed‑classes** facet was not specified for the slot, then the symbol **FALSE** is returned. A multifield of length zero is returned if an error occurs.

Syntax

(slot‑allowed‑classes \<class-name\> \<slot-name\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass ORDER (is-a USER)

(slot item)

(slot quantity))

CLIPS\>

(defclass CUSTOMER (is-a USER)

(slot id)

(multislot orders (allowed-classes ORDER)))

CLIPS\> (slot-allowed-classes CUSTOMER id)

FALSE

CLIPS\> (slot-allowed-classes CUSTOMER orders)

(ORDER)

CLIPS\>

## 12.17 Message‑handler Functions

### 12.17.1 Existence of Shadowed Handlers

The **next-handlerp** function returns the symbol **TRUE** if there is another message‑handler available for execution; otherwise, it returns the symbol **FALSE**. If this function is called from an around handler and there are any shadowed handlers, the return value is the symbol **TRUE**. If this function is called from a primary handler and there are any shadowed primary handlers, the return value is the symbol **TRUE**. In any other circumstance, the return value is the symbol **FALSE**.

Syntax

(next‑handlerp)

### 12.17.2 Calling Shadowed Handlers

If the conditions are such that the **next‑handlerp** function would return the symbol **TRUE**, then calling the **call-next-handler** function will execute the shadowed method; otherwise, a message execution error will occur. In the event of an error, the return value of this function is the symbol **FALSE**; otherwise, it is the return value of the shadowed handler. The shadowed handler is passed the same arguments as the calling handler.

A handler may continue execution after calling **call‑next‑handler**. In addition, a handler may make multiple calls to **call‑next‑handler**, and the same shadowed handler will be executed each time.

Syntax

(call‑next‑handler)

Example

CLIPS\> (clear)

CLIPS\> (defclass PROCESS (is-a USER))

CLIPS\>

(defmessage-handler PROCESS print-args (\$?any)

(println \"PROCESS: \" ?any)

(if (next-handlerp) then

(call-next-handler)))

CLIPS\>

(defmessage-handler USER print-args (\$?any)

(println \"USER: \" ?any))

CLIPS\> (make-instance p of PROCESS)

\[p\]

CLIPS\> (send \[p\] print-args 1 2 3 4)

PROCESS: (1 2 3 4)

USER: (1 2 3 4)

CLIPS\>

### 12.17.3 Calling Shadowed Handlers with Different Arguments

The **override-next-handler** function is identical to **call‑next‑handler** except that it can change the arguments passed to the shadowed handler.

Syntax

(override‑next‑handler \<expression\>\*)

Example

CLIPS\> (clear)

CLIPS\> (defclass PROCESS (is-a USER))

CLIPS\>

(defmessage-handler PROCESS print-args (\$?any)

(println \"PROCESS: \" ?any)

(if (next-handlerp) then

(override-next-handler (rest\$ ?any))))

CLIPS\>

(defmessage-handler USER print-args (\$?any)

(println \"USER: \" ?any))

CLIPS\> (make-instance p of PROCESS)

\[p\]

CLIPS\> (send \[p\] print-args 1 2 3 4)

PROCESS: (1 2 3 4)

USER: (2 3 4)

CLIPS\>

## 12.18 Definstances Functions

### 12.18.1 Getting the List of Definstances

The **get‑definstances‑list** function returns a multifield value containing the names of all definstances constructs visible to the module specified by \<module-name\> or to the current module if none is specified. If the symbol **\*** is specified as the module name, then all definstances are returned.

Syntax

(get‑definstances‑list \[\<module-name\>\])

### 12.18.2 Determining the Module in which a Definstances is Defined

The **definstances-module** function returns the module in which the specified definstances name is defined.

Syntax

(definstances‑module \<definstances-name\>)

## 12.19 Instance Functions

### 12.19.1 Initializing an Instance

The **init-slots** function implements the init message‑handler attached to the class USER. This function evaluates and places slot expressions given by the class definition that were not specified by slot‑overrides in the call to **make‑instance** or **initialize‑instance**. This function should never be called directly unless an init message‑handler is being defined such that the one attached to USER will never be called. A user‑defined class which does not inherit indirectly or directly from the class USER will require an init message‑handler which calls this function in order for instances of the class to be created. If this function is called from an init message within the context of a **make‑instance** or **initialize‑instance** call and there are no errors in evaluating the class defaults, this function will return the address of the instance it is initializing. Otherwise, this function will return the symbol **FALSE**.

Syntax

(init‑slots)

### 12.19.2 Deleting an Instance

The **unmake-instance** function deletes the specified instances by sending them a **delete** message. The argument can be one or more instance‑names, instance‑addresses, or symbols (an instance‑name without enclosing brackets). The instance specified by the arguments must exist (except in the case of the symbol **\***). If the symbol **\*** is specified for the instance, all instances will be sent the **delete** message (unless there is an instance named **\***). This function returns the symbol **TRUE** if all instances were successfully deleted, otherwise it returns the symbol **FALSE**. Note, this function is exactly equivalent to sending the instance(s) the **delete** message directly and is provided only as an intuitive counterpart to the **retract** function for facts.

Syntax

(unmake‑instance \<instance-expression\>+)

### 12.19.3 Deleting the Active Instance from a Handler

The **delete-instance** function operates implicitly on the active instance for a message, and thus can only be called from within the body of a message‑handler. This function directly deletes the active instance and is the one used to implement the delete handler attached to class USER. This function returns the symbol **TRUE** if the instance was successfully deleted; otherwise, it returns the symbol **FALSE**.

Syntax

(delete‑instance)

### 12.19.4 Determining the Class of an Object

The **class** function returns a symbol which is the name of the class of its argument. It returns the symbol **FALSE** on errors. This function is equivalent to the **type** function.

Syntax

(class \<object-expression\>)

Example

CLIPS\> (class 34)

INTEGER

CLIPS\>

### 12.19.5 Determining the Name of an Instance

The **instance-name** function returns a symbol which is the name of its instance argument. It returns the symbol **FALSE** on errors. The evaluation of the argument must be an instance‑name or instance‑address of an existing instance.

Syntax

(instance‑name \<instance-expression\>)

### 12.19.6 Determining the Address of an Instance

The **instance-address** function returns the address of its instance argument. It returns the symbol **FALSE** on errors. The evaluation of \<instance expression\> must be an instance‑name or instance‑address of an existing instance. If \<module\> or the symbol **\*** is not specified, the function searches only in the current module. If the symbol **\*** is specified, the current module and imported modules are recursively searched. If \<module\> is specified, only that module is searched. The :: syntax cannot be used with the instance‑name if \<module\> or \* is specified.

Syntax

(instance‑address \[\<module\> \| \*\] \<instance-expression\>)

### 12.19.7 Converting a Symbol to an Instance‑Name

The **symbol-to-instance-name** function returns an instance‑name which is equivalent to its symbol argument. It returns the symbol **FALSE** on errors.

Syntax

(symbol‑to‑instance‑name \<symbol-expression\>)

Example

CLIPS\> (symbol-to-instance-name (sym-cat abc def))

\[abcdef\]

CLIPS\>

### 12.19.8 Converting an Instance‑Name to a Symbol

The **instance-name-to-symbol** function returns a symbol which is equivalent to its instance‑name argument. It returns the symbol **FALSE** on errors.

Syntax

(instance‑name‑to‑symbol \<instance-name-expression\>)

Example

CLIPS\> (instance-name-to-symbol \[a\])

a

CLIPS\>

### 12.19.9 Testing for an Instance

The **instancep** function returns the symbol **TRUE** if the evaluation of its argument is an instance‑address or an instance‑name; otherwise, it returns the symbol **FALSE**.

Syntax

(instancep \<expression\>)

### 12.19.10 Testing for an Instance‑Address

The **instance-addressp** function returns the symbol **TRUE** if the evaluation of its argument is an instance‑address; otherwise, it returns the symbol **FALSE**.

Syntax

(instance‑addressp \<expression\>)

### 12.19.11 Testing for an Instance‑Name

The **instance-namep** function returns the symbol **TRUE** if the evaluation of its argument is an instance‑name; otherwise, it returns the symbol **FALSE**.

Syntax

(instance‑namep \<expression\>)

### 12.19.12 Testing for the Existence an Instance

The **instance-existp** function returns the symbol **TRUE** if the specified instance exists; otherwise, it returns the symbol **FALSE**. If the argument is an instance‑name, the function determines if an instance of the specified name exists. If the argument is an instance‑address, the function determines if the specified address is still valid.

Syntax

(instance‑existp \<instance-expression\>)

### 12.19.13 Reading a Slot Value

The **dynamic-get** function returns the value of the specified slot of the active instance. If the slot does not exist, the slot does not have a value, or this function is called from outside a message‑handler, this function will return the symbol **FALSE** and an error will be generated. This function differs from the ?self:\<slot‑name\> syntax in that the slot is not looked up until the function is actually called. Thus it is possible to access different slots every time the function is executed. This function bypasses message‑passing.

Syntax

(dynamic‑get \<slot-name-expression\>)

### 12.19.14 Setting a Slot Value

The **dynamic-put** function sets the value of the specified slot of the active instance. If the slot does not exist, there is an error in evaluating the arguments to be placed, or this function is called from outside a message‑handler, this function will return the symbol **FALSE** and an error will be generated. Otherwise, the new slot value is returned. This function differs from the (bind ?self:\<slot‑name\> \<value\>\*) syntax in that the slot is not looked up until the function is actually called. Thus it is possible to access different slots every time the function is executed. This function bypasses message‑passing.

Syntax

(dynamic‑put \<slot-name-expression\> \<expression\>\*)

### 12.19.15 Replacing Fields in a Slot

The **slot-replace\$** and **slot-direct-replace\$** functions allow the replacement of a range of fields in a multifield slot value with one or more new values. The range indices must be from 1 to n, where n is the number of fields in the multifield slot's original value and n \> 0.

The **slot-replace\$** function sets the new slot value with a **put-** message. The **slot-direct-replace\$** function can only be called from message-handlers and sets the new slot value for the active instance directly. Both functions read the original value of the slot directly without the use of a **get-** message and return the new slot value on success and the symbol **FALSE** on errors.

Syntax

(slot‑replace\$ \<instance-expression\> \<mv-slot-name\>

\<range-begin\> \<range-end\> \<expression\>+)

(slot-direct‑replace\$ \<mv-slot-name\>

\<range-begin\> \<range-end\> \<expression\>+)

Example

CLIPS\> (clear)

CLIPS\>

(defclass LIST (is-a USER)

(multislot items))

CLIPS\> (make-instance gl of LIST (items milk eggs cheese))

\[gl\]

CLIPS\> (slot-replace\$ gl items 2 2 beer pretzels)

(milk beer pretzels cheese)

CLIPS\>

### 12.19.16 Inserting Fields in a Slot

The **slot-insert\$** and **slot-direct-insert\$** functions allow the insertion of one or more new values in a multifield slot value before a specified field index. The index must greater than or equal to 1. A value of 1 inserts the new value(s) at the beginning of the slot's value. Any value greater than the length of the slot's value appends the new values to the end of the slot's value.

The **slot-insert\$** function sets the new slot value with a **put-** message. The **slot-direct-insert\$** function can only be called from message-handlers and sets the new slot value for the active instance directly. Both functions read the original value of the slot directly without the use of a **get-** message and return the new slot value on success and the symbol **FALSE** on errors.

Syntax

(slot‑insert\$ \<instance-expression\> \<mv-slot-name\>

\<index\> \<expression\>+)

(slot-direct‑insert\$ \<mv-slot-name\> \<index\> \<expression\>+)

Example

CLIPS\> (clear)

CLIPS\>

(defclass LIST (is-a USER)

(multislot items))

CLIPS\> (make-instance gl of LIST (items milk eggs cheese))

\[gl\]

CLIPS\> (slot-insert\$ \[gl\] items 2 beer pretzels)

(milk beer pretzels eggs cheese)

CLIPS\>

### 12.19.17 Deleting Fields in a Slot

The **slot-delete\$** and **slot-direct-delete\$** functions allow the deletion of a range of fields in a multifield slot value. The range indices must be from 1..n, where n is the number of fields in the multifield slot's original value and n \> 0.

The **slot-delete\$** function sets the new slot value with a **put-** message. The **slot-direct-delete\$** function can only be called from message-handlers and sets the new slot value for the active instance directly. Both functions read the original value of the slot directly without the use of a **get-** message and return the new slot value on success and the symbol **FALSE** on errors.

Syntax

(slot‑delete\$ \<instance-expression\> \<mv-slot-name\>

\<range-begin\> \<range-end\>)

(slot-direct‑delete\$ \<mv-slot-name\> \<range-begin\> \<range-end\>)

Example

CLIPS\> (clear)

CLIPS\>

(defclass LIST (is-a USER)

(multislot items))

CLIPS\> (make-instance gl of LIST (items milk eggs cheese))

\[gl\]

CLIPS\> (slot-delete\$ \[gl\] items 2 3)

(milk)

CLIPS\>

## 12.20 Defmodule Functions

The following functions provide ancillary capabilities for the defmodule construct.

### 12.20.1 Getting the List of Defmodules

The **get‑defmodule‑list** function returns a multifield value containing the names of all defmodules that are currently defined.

Syntax

(get‑defmodule‑list)

Example

CLIPS\> (clear)

CLIPS\> (get-defmodule-list)

(MAIN)

CLIPS\> (defmodule COLLECT)

CLIPS\> (defmodule PROCESS)

CLIPS\> (get-defmodule-list)

(MAIN COLLECT PROCESS)

CLIPS\>

### 12.20.2 Setting the Current Module

The **set-current-module** function sets the current module. It returns the name of the previous current module. If an invalid module name is given, then the current module is not changed and the name of the current module is returned.

Syntax

(set‑current‑module \<defmodule-name\>)

### 12.20.3 Getting the Current Module

The **get-current-module** function returns the name of the current module.

Syntax

(get‑current‑module)

## 12.21 Sequence Expansion

By default, there is no distinction between single‑field and multifield variable references within function calls (as opposed to declaring variables for function parameters or variables used for pattern‑matching). For example:

CLIPS\> (clear)

CLIPS\>

(defrule print-list

(grocery-list \$?groceries)

=\>

(println ?groceries)

(println \$?groceries))

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (run)

(milk eggs cheese)

(milk eggs cheese)

CLIPS\>

Note that both printout statements in the rule produce identical output when the rule executes. The use of ?groceries and \$?groceries within the function call behave identically.

Multifield variable references within function calls, however, can optionally be expanded into multiple single field arguments. The \$ acts as a "sequence expansion" operator and has special meaning when applied to a global or local variable reference within the argument list of a function call. The \$ means to take the fields of the multifield value referenced by the variable and treat them as separate arguments to the function as opposed to passing a single multifield value argument.

For example, using sequence expansion with the *print-list* rule would give the following output:

CLIPS\> (clear)

CLIPS\> (set-sequence-operator-recognition TRUE)

FALSE

CLIPS\>

(defrule print-list

(grocery-list \$?groceries)

=\>

(println ?groceries)

(println \$?groceries))

CLIPS\> (assert (grocery-list milk eggs cheese))

\<Fact-1\>

CLIPS\> (run)

(milk eggs cheese)

milkeggscheese

CLIPS\> (set-sequence-operator-recognition FALSE)

TRUE

CLIPS\>

Using sequence expansion, the two printout statements on the RHS of the expansion rule are equivalent to:

(println (create\$ milk eggs cheese))

(println milk eggs cheese)

The \$ operator also works with global variables. For example:

CLIPS\> (clear)

CLIPS\> (set-sequence-operator-recognition TRUE)

FALSE

CLIPS\> (defglobal ?\*sides\* = (create\$ 3 4 5))

CLIPS\> (+ ?\*sides\*)

\[ARGACCES1\] Function \'+\' expected at least 2 arguments.

CLIPS\> (+ \$?\*sides\*)

12

CLIPS\> (set-sequence-operator-recognition FALSE)

TRUE

CLIPS\>

The sequence expansion operator is particularly useful for generic function methods. Consider the ease now of defining a general addition function for strings.

CLIPS\> (clear)

CLIPS\> (set-sequence-operator-recognition TRUE)

TRUE

CLIPS\>

(defmethod + ((\$?any STRING))

(str-cat \$?any))

CLIPS\> (+ \"red\" \"white\" \"blue\")

\"redwhiteblue\"

CLIPS\> (set-sequence-operator-recognition FALSE)

TRUE

CLIPS\>

By default, sequence expansion is disabled. The behavior can be enabled using the **set‑sequence‑operator‑recognition** function.

### 12.21.1 Sequence Expansion and Rules

Sequence expansion is allowed on the LHS of rules, but only within function calls. If a variable is specified in a pattern as a single or multifield variable, then all other references to that variable that are not within function calls must also be the same. For example, the following rule is not allowed

(defrule bad-rule

(pattern \$?x ?x \$?x)

=\>)

The following rule illustrates appropriate use of sequence expansion on the LHS of rules.

(defrule good-rule-1

(pattern \$?x&:(\> (length\$ ?x) 1))

(another-pattern \$?y&:(\> (length\$ ?y) 1))

(test (\> (+ \$?x) (+ \$?y)))

=\>)

The first and second patterns use the length\$ function to determine that the multifields bound to ?x and ?y are greater than 1. Sequence expansion is not used to pass ?x and ?y to the length\$ function since the length\$ function expects a single argument of type multifield. The test CE calls the + function to determine the sum of the values bound to ?x and ?y. Sequence expansion is used for these function calls since the + function expects two or more arguments with numeric data values.

Sequence expansion has no affect within an **assert**, **modify**, or **duplicate**; however, it can be used with other functions on the RHS of a rule.

### 12.21.2 Multifield Expansion Function

The \$ operator is merely a shorthand notation for the **expand\$** function call. For example, the function calls

(println \$?b)

and

(println (expand\$ ?b))

are identical.

Syntax

(expand\$ \<multifield-expression\>)

The **expand\$** function is valid only within the argument list of a function call. The **expand\$** function (and hence sequence expansion) cannot be used as an argument to the following functions: **expand\$**, **return**, **progn**, **while**, **if**, **progn\$**, **foreach**, **switch**, **loop‑for‑count**, **assert**, **modify**, **duplicate** and **object‑pattern‑match‑delay**.

### 12.21.3 Setting The Sequence Operator Recognition Behavior

The **set-sequence-operator-recognition** function sets the sequence operator recognition behavior. When this behavior is disabled (FALSE by default), multifield variables found in function calls are treated as a single argument. When this behaviour is enabled, multifield variables are expanded and passed as separate arguments in the function call. This behavior should be set *before* an expression references a multifield variable is encountered (i.e. changing the behavior does not retroactively change the behavior for previously encountered expressions). The return value for this function is the old value for the behavior.

Syntax

(set‑sequence‑operator‑recognition \<boolean-expression\>)

### 12.21.4 Getting The Sequence Operator Recognition Behavior

The **get-sequence-operator-recognition** function returns the current value of the sequence operator recognition behavior (either the symbol **TRUE** or **FALSE**).

Syntax

(get‑sequence‑operator‑recognition)

### 12.21.5 Sequence Operator Caveat

CLIPS normally tries to detect as many constraint errors as possible for a function call at parse time, such as the wrong number of arguments or argument types. However, if the sequence expansion operator is used in the function call, all such checking is delayed until run‑time (because the number and types of arguments can change for each execution of the call.) For example:

CLIPS\> (clear)

CLIPS\> (set-sequence-operator-recognition TRUE)

FALSE

CLIPS\> (deffunction f1 (?a ?b))

CLIPS\> (deffunction f2 (\$?a) (f1 ?a))

\[ARGACCES1\] Function \'f1\' expected exactly 2 arguments.

ERROR:

(deffunction MAIN::f2

(\$?a)

(f1 ?a)

CLIPS\> (deffunction f2 (\$?a) (f1 \$?a))

CLIPS\> (f2 1)

\[ARGACCES1\] Function \'f1\' expected exactly 2 arguments.

\[PRCCODE4\] Execution halted during the actions of deffunction \'f2\'.

FALSE

CLIPS\> (f2 1 2)

FALSE

CLIPS\> (set-sequence-operator-recognition FALSE)

TRUE

CLIPS\>
