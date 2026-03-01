# Section 4: Deffacts Construct

With the **deffacts** construct, a list of facts can be defined which are automatically asserted whenever the **reset** command is performed. Facts as­serted through deffacts may be retracted or pattern‑matched like any other fact. The initial fact‑list, including any defined deffacts, is always reconstructed after a **reset** command.

Syntax

(deffacts \<deffacts-name\> \[\<comment\>\]\
\<RHS-pattern\>\*)

Redefining a currently existing deffacts causes the previous deffacts with the same name to be removed even if the new definition has errors in it. There may be multiple deffacts constructs and any number of facts (either ordered or deftemplate) may be asserted into the initial fact‑list by each deffacts construct.

Dynamic expressions may be included in a fact by embedding the expression directly within the fact. All such expressions are evaluated when CLIPS is reset.

Example

CLIPS\> (clear)

CLIPS\>

(deftemplate oav

(slot object)

(slot attribute)

(slot value))

CLIPS\>

(deffacts startup \"Refrigerator Status\"

(oav (object refrigerator)

(attribute light)

(value on))

(oav (object refrigerator)

(attribute door)

(value open))

(oav (object refrigerator)

(attribute temp)

(value 40)))

CLIPS\> (facts)

CLIPS\> (reset)

CLIPS\> (facts)

f-1 (oav (object refrigerator) (attribute light) (value on))

f-2 (oav (object refrigerator) (attribute door) (value open))

f-3 (oav (object refrigerator) (attribute temp) (value 40))

For a total of 3 facts.

CLIPS\>

#
