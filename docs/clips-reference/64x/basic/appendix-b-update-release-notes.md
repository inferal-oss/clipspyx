# Appendix B: Update Release Notes

The following changes were introduced in version 6.4 of CLIPS.

• **Initial Fact** -- The initial-fact deftemplate and deffacts are no longer supported.

• **Initial Object** -- The INITIAL-OBJECT defclass and initial-object definstances are no longer supported.

• **Object Pattern Performance Improvements** -- Rule performance has been improved for object patterns particularly in situations with a large number of class slots.

• **New Functions and Commands** ‑ Several new functions and commands have been added. They are:

• **str-replace** (see section 12.3.13)

• **print** (see section 12.4.3)

• **println** (see section 12.4.3)

• **unget-char** (see section 12.4.10)

• **flush** (see section 12.4.13)

• **rewind** (see section 12.4.14)

• **tell** (see section 12.4.15)

• **seek** (see section 12.4.16)

• **chdir** (see section 12.4.17)

• **atan2** (see section 12.5.11.1)

• **local-time** (see section 12.7.12)

• **gm-time** (see section 12.7.13)

• **get-error** (see section 12.7.14)

• **clear-error** (see section 12.7.15)

• **set-error** (see section 12.7.16)

• **void** (see section 12.7.17)

• **bsave-facts** (see section 13.4.4)

• **bload-facts** (see section 13.4.6)

• **Command and Function Changes** ‑ The following commands and functions have been changed:

• **assert** (see section 12.9.1). When a duplicate fact is asserted, the return value of the **assert** command is the originally asserted fact. The symbol **false** is only returned by the **assert** command if an error occurs.

• **bsave-instances** (see section 13.14.3). The **bsave-instances** function now returns -1 if an error occurs.

• **duplicate** (see section 12.9.4). The return value of a function call can be used to specify the fact being duplicated. Specifying the fact using a fact-index is no longer limited to top-level commands.

• **eval** (see section 12.3.5). When executed from the command prompt, the eval function can access previously bound local variables. The **eval** function is now available in binary-load only and run-time CLIPS configurations.

• **explode\$** (see section 12.2.6). The **explode\$** function now returns symbols for tokens that are not primitive values.

• **funcall** (see section 12.7.9). A module specifier can be used as part of the function name when referencing a deffunction or defgeneric that is exported by a module.

• **open** (see section 12.4.1). The r+, w+, and a+ modes and their binary counterparts are now supported.

• **length\$** (see section 12.2.13). The length\$ function no longer accepts strings or symbols as arguments.

• **load** (see section 13.1.1). The file name and line number are now printed for each error/warning message generated during execution of this command.

• **load-facts** (see section 13.4.5). The **load-facts** command now returns the number of facts loaded.

• **modify** (see section 12.9.3). The **modify** command now preserves the fact-index and fact-address of the fact being modified. Modifying a fact without changing any slots no longer retracts and reasserts the original fact. If facts are being watched, only changed slots are displayed when a fact is being modified. The return value of a function call can be used to specify the fact being modified. Specifying the fact using a fact-index is no longer limited to top-level commands. If all slot changes specified in the modify command match the current values of the fact to be modified, no action is taken.

• **pointerp**. The **pointerp** function is deprecated. The **external-addressp** function (see section 12.1.10) should be used instead.

• **Pretty Print Commands** -- The **ppdefclass**, **ppdeffacts**, **ppdeffunction**, **ppdefgeneric**, **ppdefglobal**, **ppdefinstances**, **ppdefmessage-handler**, **ppdefmethod**, **ppdefmodule**, **ppdefrule**, and **ppdeftemplate** commands now accept an optional logical name argument. The logical name **nil** can be used to return the source text as the command return value rather than sending it to an output destination. The **ppfact** command now returns the source text of a fact when the logical name **nil** is specified.

• **read** (see section 12.4.4). The **read** function now returns symbols for tokens that are not primitive values. For example, the token ?var is returned as the symbol ?var and not the string \"?var\". If an error occurs, the **read** function now returns the symbol FALSE and the **get-error** function can be used to determine the error that occurred.

• **readline** (see section 12.4.5). If an error occurs, the **readline** function now returns the symbol **FALSE**.

• **read-number** (see section 12.4.11). If an error occurs, the **read-number** function now returns the symbol **FALSE**.

• **round** (see section 12.5.22). If the argument to the **round** function is exactly between two integers, it is now rounded away from zero.

• **save-facts** (see section 13.4.3). The **save-facts** command now returns the number of facts saved.

• **save-instances** (see section 13.14.3). The **save-instances** function now returns -1 if an error occurs.

• **system** (see section 13.1.12). The **system** function now returns an integer completion status.

• **str-index** (see section 12.3.4). The **str-index** function now returns 1 if the search string is the empty string \"\".

• **string-to-field** (see section 12.3.12). The **string-to-field** function now returns symbols for tokens that are not primitive values.

• **watch** (see section 13.2.3). The compilations watch flag now defaults to off.

• **Incremental Reset** -- This behavior is now always enabled---newly defined rules are always updated based upon the current state of the fact‑list. The **get-incremental-reset** and **set-incremental-reset** functions are no longer supported.

• **Static Constraint Checking** -- This behavior is now always enabled---constraint violations are always checked when function calls and constructs are parsed. The **get-static-constraint-checking** and **set-static-constraint-checking** functions are no longer supported.

• **Auto Float Dividend** -- This behavior is now always enabled--- the dividend of the division function is always automatically converted to a floating point number. The **get-auto-float-dividend** and **set-auto-float-dividend** functions are no longer supported.

• **Legacy Functions** -- The **direct-mv-delete**, **direct-mv-insert**, **direct-mv-replace**, **length**, **member**, **mv-append**, **mv-delete**, **mv-replace**, **mv-slot-delete**, **mv-slot-insert**, **mv-slot-replace**, **mv-subseq**, **nth**, **sequencep**, **str-explode**, **str-implode**, **subset**, and **wordp** functions are no longer supported.

• **Fact Query Pruning** -- The fact set query functions (see section 12.9.12) now prune all fact sets containing facts retracted by actions applied to prior fact sets.

• **Instance Query Pruning** -- The instance set query functions (see sections 9.7) now prune all instance sets containing instances deleted by actions applied to prior instance sets.

• **Retracted Fact Errors** -- The following functions now generate errors when used with retracted facts: **dependencies**, **dependents**, **duplicate**, **fact-index**, **fact-relation**, **fact-slot-names**, **fact-slot-value**, **modify**, **ppfact**, and **timetag**.

• **Logical Names** -- The **wclips**, **wdialog**, **wdisplay**, and **wtrace** logical names are no longer supported. Output previously directed to these logical names is now sent to **stdout**.

• **Single Slot Keyword** -- The **single-slot** keyword in defclass definitions is no longer supported. The **slot** keyword should be used in its place.

The following changes were introduced in version 6.4.1 of CLIPS.

• **New Functions and Commands** ‑ Several new functions and commands have been added. They are:

• **union\$** (see section 12.2.16)

• **intersection\$** (see section 12.2.17)

• **difference\$** (see section 12.2.18)

The following changes were introduced in version 6.4.2 of CLIPS.

• **New Functions and Commands** ‑ Several new functions and commands have been added. They are:

• **str-byte-length** (see section 12.3.14)

• **with-open-file** (see section 12.4.18)

• **try** (see section 12.6.11)

• **fact-index-to-fact** (see section 12.9.13)

• **Command and Function Changes** ‑ The following commands and functions have been changed:

• **printout**, **print**, and **println** (see section 12.4.3). The symbols **cr** and **lf** and be used to print carriage returns and line feeds.

• **format** (see section 12.4.6). Updated to appropriately handle width and precison for UTF-8 multibyte characters.

• **External Text Manipulation** -- Removed the restriction on the maximum length for file and topic names. See section 13.17.
