# Appendix E: CLIPS Warning Messages

CLIPS typically will display two kinds of warning messages: those associated with executing constructs and those associated with loading constructs. This appendix describes some of the more common warning messages and what they mean. Each message begins with a unique identifier enclosed in brackets followed by the keyword **WARNING**; the messages are listed here in alphabetic order according to the identifier.

\[CSTRCPSR1\] WARNING: Redefining \<constructType\>: \<constructName\>

or

\[CSTRCPSR1\] WARNING: Method \# \<method index\> redefined.

This indicates that a previously defined construct of the specified type has been redefined.

\[CSTRNBIN1\] WARNING: Constraints are not saved with a binary image when dynamic constraint checking is disabled

or

\[CSTRNCMP1\] WARNING: Constraints are not saved with a constructs‑to‑c image when dynamic constraint checking is disabled

These warnings occur when dynamic constraint checking is disabled and the **constructs‑to‑c** or **bsave** commands are executed. Constraints attached to deftemplate and defclass slots will not be saved with the runtime or binary image in these cases since it is assumed that dynamic constraint checking is not required. Enable dynamic constraint checking with the **set‑dynamic‑constraint‑checking** function before calling **constructs‑to‑c** or **bsave** in order to include constraints in the runtime or binary image.

\[DFFNXFUN1\] WARNING: Deffunction \<name\> only partially deleted due to usage by other constructs.

During a clear or deletion of all deffunctions, only the actions of a deffunction were deleted because another construct which also could not be deleted referenced the deffunction.

Example:

CLIPS\>

(deffunction hello ()

(println \"Hi there!\"))

CLIPS\>

(deffunction delete ()

(hello)

(undeffunction \*))

CLIPS\> (delete)7yuo

\[GENRCBIN1\] WARNING: COOL not installed! User‑defined class in method restriction substituted with OBJECT.

This warning occurs when a generic function method restricted by defclasses is loaded using the **bload** command into a CLIPS configuration where the object language is not enabled. The restriction containing the defclass will match any of the primitive types.

\[PRCCODE4\] WARNING: Execution halted during the actions of defrule \<name\>.

This warning occurs when the rules are being watch and rule execution is halted.

Example:

CLIPS\> (defrule halt =\> (halt))

CLIPS\> (watch rules)

CLIPS\> (run)

\[SCANNER1\] WARNING: Over or underflow of long long integer.

This warning occurs when an integer is outside of the range of values that can be represented in the C long long integer type.

Example:

CLIPS\> 12345678901234567890
