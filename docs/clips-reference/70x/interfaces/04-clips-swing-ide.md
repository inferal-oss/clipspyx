# Section 4: CLIPS Swing IDE

This section provides a brief summary of the CLIPS 6.4 Swing Integrated Development Environment (IDE). The IDE provides a dialog window that allows commands to be entered in a manner similar to the standard CLIPS command line interface. Any CLIPS I/O to standard input or standard output is directed to this dialog window. In addition, the IDE also provides browser windows for examining the current state of the CLIPS environment.

On Windows and macOS, enter the following command from the CLIPSJNI directory (see section 7.1) to launch the Swing IDE:

java -jar CLIPSIDE.jar

On Linux, you must first create the CLIPSJNI native library (see section 7.6.3). Once created, enter the following command from the CLIPSJNI directory:

java -Djava.library.path=. --jar CLIPSIDE.jar

When launched, the IDE displays a dialog window:

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/70x/media/media/image17.png){width="4.130328083989501in" height="3.443687664041995in"}

A status bar is displayed beneath the title bar. On the left side of the status bar is the current working directory. A **Pause** button is on the right side of the status bar. The CLIPS IDE is multi-threaded and uses a separate thread to execute commands. Pressing the **Pause** button while a command is executing will suspend execution of the command thread. This is useful if you need to examine the output of the executing program. Pressing the **Pause** button a second time will resume execution of the command thread.

Inline editing is supported in the dialog window. The left and right arrow keys can be used to move the caret backwards and forwards through the current command. Pressing the delete key will delete the character to the left of the caret. Insertion of other characters or pasted text occurs at the caret. The esc key moves the caret to the end of the current command. The caret must be at the end of the current command in order for pressing the return key to execute the command.

A command history is also supported for the dialog window. The up and down arrows allow you to cycle through the command history. The up arrow restores the previous command and the down arrow restores the next command. Holding the shift key down when the up or down arrow is pressed takes you respectively to the beginning or end of the command history.

From the CLIPS command prompt, the command **clear-window** (which takes no arguments) will also clear all of the text in the dialog window.

Holding down the **control** key while pressing the period key will halt rule execution. The RHS actions of the currently executing rule will be allowed to complete before rule execution is halted. Holding down the **shift** key, the **control** key, and the period key will halt execution at the first possible opportunity. If rules are executing, this will typically occur after the current RHS action. Remaining RHS actions will not be executed. This key combination can also be used to halt the execution of commands and functions that loop.

## 4.2 The File Menu

### 4.2.1 New (\^-N)

This command opens a new buffer for editing with the window name Untitled.

### 4.2.2 Open\... (\^-O)

This command displays the standard file selection dialog sheet, allowing the user to select a text file to be opened as a buffer for editing. More than one file can be opened at the same time, however, the same file cannot be opened more than once. As files are opened, they are automatically stacked.

### 4.2.3 Save (\^-S)

This command saves the file in the active edit window. If the file is untitled, a save file dialog sheet will prompt for a file name under which to save the file.

### 4.2.4 Save As\... (\^+⇧-S) 

This command allows the active edit window to be saved under a new name. A save file dialog sheet will appear to prompt for the new file name. The name of the editing window will be changed to the new file name.

### 4.2.5 Page Setup\...

This command allows the user to specify information about the size of paper used by the printer.

### 4.2.6 Print\...

This command allows the user to print the active edit window.

### 4.2.7 Quit CLIPS IDE (\^-Q)

This command causes the CLIPS IDE to quit. The user will be prompted to save any files with unsaved changes.

## 4.3 The Edit Menu

### 4.3.1 Undo (\^-Z)

This command allows you to undo your last editing operation. Typing, cut, copy, and paste operations can all be undone.

### 4.3.2 Redo (\^+⇧-Z)

This command allows you to redo your last editing operation. Typing, cut, copy, and paste operations can all be redone.

### 4.3.3 Cut (\^-X)

This command removes selected text in the active edit window or the dialog window and places it in the Clipboard. In the dialog window, only selected text from the current command being entered can be cut.

### 4.3.4 Copy (\^-C)

This command copies selected text in the active edit window or the dialog window and places it in the Clipboard.

### 4.3.5 Paste (\^-V)

This command copies the contents of the Clipboard to the selection point in the active edit window or the dialog window. If the selected text is in the active edit window, it is replaced by the contents of the Clipboard. In the dialog window, text can only be pasted/replaced in the current command being entered.

### 4.3.6 Set Font\... 

This command displays a dialog allowing the fonts to be changed for the dialog, browser, and editor windows.

## 4.4 The Text Menu

### 4.4.1 Load Selection (\^-K)

This command loads the constructs in the active edit window's current selection into CLIPS. Standard error detection and recovery routines used to load constructs from a file are also used when loading a selection (i.e., if a construct has an error in it, the rest of the construct will be skipped over until another construct to be loaded is found).

### 4.4.2 Batch Selection (\^+⇧-K)

This command treats the active edit window's current selection as a batch file and executes it as a series of commands. Standard error detection and recovery routines used to load construct from a file are *not* used when batching a selection (i.e., if a construct has an error in it, a number of ancillary errors may be generated by subsequent parts of the same construct following the error).

### 4.4.3 Load Buffer

This command loads the constructs from the entire contents of active edit window into CLIPS. It is equivalent to selecting the entire buffer and executing a **Load Selection** command.

### 4.4.4 Balance (\^-B)

This command operates on the active edit window's current selection by expanding it until the selection begins and ends with parentheses and each parenthesis contained in the selection is properly nested (i.e. each left opening parenthesis has a properly nested right closing parenthesis and vice versa). Repeat­edly using this command will select larger and larger selections of text until a balanced se­lection cannot be found. The balance command is a purely textual operation and does not ignore parentheses contained within CLIPS string values.

### 4.4.5 Comment

This command operates on the current selection in the active edit window by adding a semicolon to the beginning of each line contained in the selection.

### 4.4.6 Uncomment

This command operates on the current selection in the active edit window by removing a semicolon (if one exists) from the beginning of each line contained in the selection.

## 4.5 The Environment Menu

### 4.5.1 Clear

This command is equivalent to the CLIPS command (clear). When this command is chosen, the CLIPS command (clear) will be echoed to the dialog window and exe­cuted. This command is not available when CLIPS is executing.

### 4.5.2 Load Constructs\... (\^-L)

This command displays a file selection dialog, allowing the user to select a text file containing constructs to be loaded into CLIPS. This command is equivalent to the CLIPS command (load \<file-name\>). When this command is chosen and a file is se­lected, the appropriate CLIPS load command will be echoed to the dialog window and executed.

### 4.5.3 Load Batch\... (\^+⇧-L)

This command displays a file selection dialog, allowing the user to select a text file to be executed as a batch file. This command is equivalent to the CLIPS command (batch \<file-name\>). When this command is chosen and a file is selected, the appropriate CLIPS batch command will be echoed to the dialog window and executed.

### 4.5.4 Set Directory...

This command displays a folder selection dialog, allowing the user to select the current directory associated with the CLIPS environment. File commands such as load, batch, and open use the current directory to determine the location where file operations should occur. The current directory for the dialog window is displayed in the status pane below the window title.

### 4.5.5 Reset (\^-R)

This command is equivalent to the CLIPS command (reset). When this command is chosen, the CLIPS command (reset) will be echoed to the dialog window and exe­cuted.

### 4.5.6 Run (\^+⇧-R)

This command is equivalent to the CLIPS command (run). When this command is cho­sen, the CLIPS command (run) will be echoed to the dialog window and executed.

### 4.5.7 Halt Rules (\^-.)

This command halts execution when the currently executing rule has finished executing all of its actions. This command has no effect if rules are not executing.

### 4.5.8 Halt Execution (\^+⇧-.)

This command halts execution at the first available opportunity. If rules are executing, the currently executing rule may not complete all of its actions.

### 4.5.9 Clear Scrollback

This command clears all of the text in the dialog window. From the CLIPS command prompt, the command **clear-window** (which takes no arguments) will also clear all of the text in the dialog window.

## 4.6 The Debug Menu

### 4.6.1 Watch Submenu

Watch items can be enabled or disabled by the appropriate menu item. Enabled watch items have a check to the left of the menu item. Disabled watch items have no check mark in their check box. Choosing the **All** menu item checks all of the watch items. Choosing the **None** menu item unchecks all of the watch items.

### 4.6.2 Agenda Browser

The **Agenda Browser** allows the activations on the agenda to be examined. The list on the left side of the window shows the modules currently on the focus stack. The list of the right side of the window shows the activations on the agenda of the selected module from the focus stack.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/70x/media/media/image18.png){width="6.5in" height="2.47213145231846in"}

The **Reset** button sends a "(reset)" command to the dialog window. The **Run** button sends a "(run)" command to the dialog window. The **Step** button sends a "(run 1)" command to the dialog window. Pressing the **Halt Rules** button when rules are executing will halt execution when the currently executing rule has finished all of its actions.

### 4.6.3 Fact Browser

The **Fact Browser** allows the facts in the fact list to be examined. The list on the left side of the window shows the modules currently defined. The list in the middle of the window shows the facts that are visible to the selected module from the module list. The list on the right side of the window shows the slot values of the selected fact from the fact list.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/70x/media/media/image19.png){width="6.5in" height="3.0205194663167103in"}

The list of facts can be sorted based on either the fact index or the associated deftemplate name by clicking on either the **Index** or the **Template** column header. The list of slots can be sorted based on either the slot name or the slot value by clicking on either the **Slot** or the **Value** column header. If the **Display Defaulted Values** checkbox is enabled, then all of the slots of the selected fact will be displayed. If the checkbox is disabled, then only those slots that have a value different from their default slot value will be displayed.

The search text field can be used to filter the facts that are displayed in the fact list. When search text is entered and the return key is pressed each fact and its slots are examined to determine if the search text is found within one of the following templates:

f-\<index\>

\<deftemplate-name\> \<slot-name\> \<slot-value\>

For example, if the fact associated with the deftemplate thing had a fact index of 4 and slots name with value big-pillow, location with value t2-2, and on-top-of with value red-couch, then the fact would be displayed in the fact list only if the search text was found in one of the following strings:

f-4

thing name big-pillow

thing location t2-2

thing on-top-of red-couch

### 4.6.4 Instance Browser

The **Instance Browser** allows the instances in the instance list to be examined. The list on the left side of the window shows the modules currently defined. The list in the middle of the window shows the instances that are visible to the selected module from the module list. The list on the right side of the window shows the slot values of the selected instance from the instance list.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/70x/media/media/image20.png){width="6.5in" height="3.126768372703412in"}

The list of instances can be sorted based on either the instance name or the associated defclass name by clicking on either the **Name** or the **Class** column header. The list of slots can be sorted based on either the slot name or the slot value by clicking on either the **Slot** or the **Value** column header. If the **Display Defaulted Values** checkbox is enabled, then all of the slots of the selected instance will be displayed. If the checkbox is disabled, then only those slots that have a value different from their default slot value will be displayed.

The search text field can be used to filter the instances that are displayed in the instance list. When search text is entered and the return key is pressed each instance and its slots are examined to determine if the search text is found within one of the following templates:

\[\<name\>\]

\<defclass-name\> \<slot-name\> \<slot-value\>

For example, if the instance associated with the defclass THING had the instance name \[thing1\] and slots name with value big-pillow, location with value t2-2, and on-top-of with value red‑couch, then the instance would be displayed in the instance list only if the search text was found in one of the following strings:

\[thing1\]

THING name big-pillow

THING location t2-2

THING on-top-of red-couch

### 4.6.5 Construct Inspector

The **Construct Inspector** floats above the other CLIPS IDE windows and changes to show the text of the associated construct when one of the items from the browsers is selected.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/70x/media/media/image21.png){width="6.5in" height="1.6376148293963255in"}

## 4.7 The Window Menu

The Window menu is a list of all windows associated with the CLIPS IDE. A check mark is placed by the window name to indicate that it is the frontmost window.

## 4.8 The Help Menu

### 4.8.1 CLIPS Home Page

Opens the CLIPS Home web page.

### 4.8.2 Online Documentation

Opens a web page with links to CLIPS Documentation including the CLIPS User's Guide, CLIPS Reference Manuals, and other Documentation.

### 4.8.3 Online Examples

Opens a web page with links to example programs.

### 4.8.4 CLIPS Expert System Group

Opens the CLIPS Expert System Group web page on Google Groups.

### 4.8.5 SourceForge Forums

Opens the CLIPS Discussion Forums web page on SourceForge.

### 4.8.6 Stack Overflow Q&A

Opens the Stack Overflow web page for the CLIPS question tag.

### 4.8.7 About CLIPS IDE

This command displays version information about the CLIPS IDE application.

## 4.9 Creating the Swing IDE Executable

See section 7 for details on creating the Swing IDE executable.
