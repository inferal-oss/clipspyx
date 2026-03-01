# Appendix B: Update Release Notes

The following changes were introduced in version 7.0 of CLIPS.

• **Deftemplate Inheritance** -- Deftemplates may inherit slots from other deftemplates using the **is-a** keyword. The **update** command is similar to the **modify** command but only effects rule patterns that match slots that have been changed.

• **Certainty Factors** -- Facts may now have MYCIN-style certainty factors associated with them. See Sections 3.6 and 5.4.12.3.

• **Named Facts** -- Facts may now

• **Data-Driven Backward Chaining** -- goal conditional element, explicit conditional element.

• **Deftable Construct** -- See section .

• **Generic Function Support for Deftemplates** -- Deftemplate names can be used as parameter type restrictions for defmethods. Within the body of a method, short hand slot references can be used for variables that have been bound to deftemplate types in the method parameters. See Section 8.6.

• **New Functions and Commands** ‑ Several new functions and commands have been added. They are:

• **iif** (see Section 13.6.12)

• **\$** (see Section 13.2.1)

• **TBD**

• **Command and Function Changes** ‑ The following commands and functions have been changed:

• **modify/duplicate/update** (see Section 13.9.3). These commands can dynamically specify slots.

• **save-instances** (see Section 14.14.3). The **save-instances** function now returns -1 if an error occurs.

• **system** (see Section 14.1.12). The **system** function now returns an integer completion status.

• **str-index** (see Section 13.3.4). The **str-index** function now returns 1 if the search string is the empty string \"\".

• **string-to-field** (see Section 13.3.12). The **string-to-field** function now returns symbols for tokens that are not primitive values.

• **watch** (see Section 14.2.3). The compilations watch flag now defaults to off.

• **+** (see Section 13.5.1). The **+** functions returns 0 if given no arguments, otherwise the sum of all arguments is returned.

• **−** (see Section 13.5.2). The **−** functions returns the negative of its first argument if passed just one argument.

• **\*** (see Section 13.5.3). The **\*** functions returns 1 if given no arguments, otherwise the product of all arguments is returned.

• **/** (see Section 13.5.4). The **/** functions returns the reciprocal of its argument if there is just one argument.

• **Incremental Reset** -- This behavior is now always enabled---newly defined rules are always updated based upon the current state of the fact‑list. The **get-incremental-reset** and **set-incremental-reset** functions are no longer supported.

• **Static Constraint Checking** -- This behavior is now always enabled---constraint violations are always checked when function calls and constructs are parsed. The **get-static-constraint-checking** and **set-static-constraint-checking** functions are no longer supported.

• **Auto Float Dividend** -- This behavior is now always enabled--- the dividend of the division function is always automatically converted to a floating point number. The **get-auto-float-dividend** and **set-auto-float-dividend** functions are no longer supported.

• **Legacy Functions** -- The **direct-mv-delete**, **direct-mv-insert**, **direct-mv-replace**, **length**, **member**, **mv-append**, **mv-delete**, **mv-replace**, **mv-slot-delete**, **mv-slot-insert**, **mv-slot-replace**, **mv-subseq**, **nth**, **sequencep**, **str-explode**, **str-implode**, **subset**, and **wordp** functions are no longer supported.

• **Instance Query Pruning** -- The instance set query functions (see Section 9.7) now prune all instance sets containing instances deleted by actions applied to prior instance sets.

• **Retracted Fact Errors** -- The following functions now generate errors when used with retracted facts: **dependencies**, **dependents**, **duplicate**, **fact-index**, **fact-relation**, **fact-slot-names**, **fact-slot-value**, **modify**, **ppfact**, and **timetag**.

• **Logical Names** -- The **wclips**, **wdialog**, **wdisplay**, and **wtrace** logical names are no longer supported. Output previously directed to these logical names is now sent to **stdout**.

• **Single Slot Keyword** -- The **single-slot** keyword in defclass definitions is no longer supported. The **slot** keyword should be used in its place.

The following changes were introduced in version 6.4.1 of CLIPS.

• **New Functions and Commands** ‑ Several new functions and commands have been added. They are:

• **union\$** (see Section 12.2.16)

• **intersection\$** (see Section 12.2.17)

• **difference\$** (see Section 12.2.18)
