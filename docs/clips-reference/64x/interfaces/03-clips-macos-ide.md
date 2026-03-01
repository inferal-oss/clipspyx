# Section 3: CLIPS macOS IDE

This section provides a brief summary of the CLIPS 6.4 macOS Integrated Development Environment (IDE). The IDE provides a dialog window that allows commands to be entered in a manner similar to the standard CLIPS command line interface. Any CLIPS I/O to standard input or standard output is directed to this dialog window. In addition, the IDE also provides browser windows for examining the current state of the CLIPS environment. When launched, the IDE displays a dialog window:

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image7.png){width="6.5in" height="4.734327427821523in"}

A status bar is displayed beneath the title bar. On the left side of the status bar is the current working directory. A **Pause** button is on the right side of the status bar. The CLIPS IDE is multi-threaded and uses a separate thread to execute commands entered in the dialog window. Pressing the **Pause** button while a command is executing will suspend execution of the command thread. This is useful if you need to examine the output of the executing program. Pressing the **Pause** button a second time will resume execution of the command thread.

Inline editing is supported in the dialog window. The left and right arrow keys can be used to move the caret backwards and forwards through the current command. Pressing the delete key will delete the character to the left of the caret. Insertion of other characters or pasted text occurs at the caret. The esc key moves the caret to the end of the current command. The caret must be at the end of the current command in order for pressing the return key to execute the command.

A command history is also supported for the dialog window. The up and down arrows allow you to cycle through the command history. The up arrow restores the previous command and the down arrow restores the next command. Holding the shift key down when the up or down arrow is pressed takes you respectively to the beginning or end of the command history.

From the CLIPS command prompt, the command **clear-window** (which takes no arguments) will also clear all of the text in the dialog window.

Holding down the **command** key while pressing the period key will halt rule execution. The RHS actions of the currently executing rule will be allowed to complete before rule execution is halted. Holding down the **shift** key, the **command** key, and the period key will halt rule execution after the current RHS action. Remaining RHS actions will not be executed. This key combination can also be used to halt the execution of commands and functions that loop. The **Halt Rules** menu item can also be selected from the Environment menu during execution. Selecting this menu item is equivalent to holding down the **command** key while pressing the period key. The **Halt Execution** menu item can also be selected from the Environment menu during execution. Selecting this menu item is equivalent to holding down the **shift** key and the **command** key while pressing the period key.

The interface also provides a text editor for writing CLIPS programs. Editing windows contain a control strip with a drop-down menu and a content area for text:

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image8.png){width="6.5in" height="4.33655293088364in"}

Newly created editing windows begin with the word Untitled in their title bar. If an editing window is associated with a file, then the title bar will contain the file name. Beneath the title bar is a control strip. The drop-down menu on the left side of the strip provides access to the same menu items that are in the **Text** menu. In the window shown previously, selecting the **Load Selection** menu item (either from the action menu or the **Text** menu) would load the selection in the editing window in the *Dialog* window.

## 3.1 The CLIPS IDE Menu

### 3.1.1 About CLIPS

This command displays version information about the CLIPS IDE application.

### 3.1.2 Preferences\... (⌘,)

This command displays a dialog box that allows the user to set the parameters for several options in the CLIPS MacOS IDE. With any tab selected, clicking the **Default** button restores the default settings for all tabs in the dialog.

#### 3.1.2.1 Dialog Tab

The Dialog tab allows text options for the dialog window to be set.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image9.png){width="6.5in" height="4.296953193350832in"}

The **Change...** button allows the font used in the editing windows to be changed. When you click this button, a Fonts dialog will appear. Select a font or font size from the Font dialog and the text in the Dialog tab will change to reflect the new font or font size.

The **Balance Parentheses** check box, if enabled, causes the matching left parenthesis to be momentarily highlighted whenever a right parenthesis is type or the cursor is moved immediately after a right parenthesis in the Dialog window.

#### 3.1.2.2 Editor Tab

The Editor tab allows text options for editing windows to be set.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image10.png){width="6.5in" height="4.296953193350832in"}

The **Change...** button allows the font used in the editing windows to be changed. When you click this button, a Fonts dialog will appear. Select a font or font size from the Font dialog and the text in the Editor tab will change to reflect the new font or font size.

The **Balance Parentheses** check box, if enabled, causes the matching left parenthesis to be momentarily highlighted whenever a right parenthesis is type or the cursor is moved immediately after a right parenthesis in an editing window.

### 3.1.3 Quit CLIPS IDE (⌘Q)

This command causes the CLIPS IDE to quit. The user will be prompted to save any files with unsaved changes.

## 3.2 The File Menu

### 3.2.1 New (⌘N)

This command opens a new buffer for editing with the window name Untitled.

### 3.2.2 Open\... (⌘O)

This command displays the standard file selection dialog sheet, allowing the user to select a text file to be opened in a window for editing. More than one file can be opened at the same time, however, the same file cannot be opened more than once. As files are opened, they are automatically stacked.

### 3.2.3 Open Recent

This command displays a list of recently opened files, allowing the user to select a text file to be opened as a buffer for editing.

### 3.2.4 Close (⌘W)

This command closes the active window if it has red close button in its upper left corner. If the active window is an editing window that has been modified since it was last saved, an alert sheet will confirm whether the changes should be saved or discarded or whether the close command should be canceled.

### 3.2.5 Save (⌘S)

This command saves the file in the active edit window. If the file is untitled, a save file dialog sheet will prompt for a file name under which to save the file.

### 3.2.6 Save As\... (⇧⌘S) 

This command allows the active edit window to be saved under a new name. A save file dialog sheet will appear to prompt for the new file name. The name of the editing window will be changed to the new file name.

### 3.2.7 Revert

This command restores the active edit window to the last-saved version of the file in the buffer. Any changes made since the file was last saved will be discarded.

### 3.2.8 Page Setup\... (⇧⌘P)

This command allows the user to specify information about the size of paper used by the printer.

### 3.2.9 Print\... (⌘P)

This command allows the user to print the active edit window.

## 3.3 The Edit Menu

### 3.3.1 Undo (⌘Z)

This command allows you to undo your last editing operation. Typing, cut, copy, paste, and delete operations can all be undone. The **Undo** menu item will change in the **Edit** menu to reflect the last operation performed. For example, if a **Paste** command was just performed, the **Undo** menu item will read **Undo Paste**.

### 3.3.2 Redo (⇧⌘Z)

This command allows you to redo your last editing operation. Typing, cut, copy, paste, and delete operations can all be redone. The **Redo** menu item will change in the **Edit** menu to reflect the last operation performed. For example, if a **Paste** command was just performed, the **Redo** menu item will read **Undo Paste**.

### 3.3.3 Cut (⌘X)

This command removes selected text in the active edit window or the dialog window and places it in the Clipboard. In the dialog window, only selected text from the current command being entered can be cut.

### 3.3.4 Copy (⌘C)

This command copies selected text in the active edit window or the dialog window and places it in the Clipboard.

### 3.3.5 Paste (⌘V)

This command copies the contents of the Clipboard to the selection point in the active edit window or the dialog window. If the selected text is in the active edit window, it is replaced by the contents of the Clipboard. In the dialog window, text can only be pasted/replaced in the current command being entered.

### 3.3.6 Delete

This command removes selected text in the active edit window or the display window. The selected text is not placed in the Clipboard.

### 3.3.7 Select All (⌘A)

This command selects all of the text in the active edit or display window.

### 3.3.8 Find Submenu

#### 3.3.8.1 Find\... (![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image11.png){width="0.1388888888888889in" height="0.125in"}F)

This command displays a dialog box which allows the user to set parameters for text search and replacement operations. The dialog box that appears allows a search and re­placement string to be specified.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image12.png){width="6.5in" height="2.8479385389326333in"}

Three other options can be set in the search dialog box. The **Ignore Case** option makes the string search operation case-insensitive for alphabetic characters; that is, the string "Upper" will match the string "uPPER". The **Wrap Around** option determines whether the search is restarted at the top of the document when the bottom of the document is reached. The drop-down menu allows the match criterion to be set. If it is set to **Contains**, then the search matches any text containing the search string. If it is set to **Starts with**, then only whole words beginning with the search string will be matched. If it is set to **Full word**, then only whole words will be matched.

Once search options have been set, one of five search dialog buttons can be pressed. The **Replace All** button replaces all occurrences of the **Find** string with the **Replace With** string. The **Replace** button replaces the current selection with the **Replace With** string. The **Replace & Find** button replaces the current selection with the **Replace With** string and finds and selects the next match for the **Find** string. The **Previous** button finds and selects the previous match for the **Find** string. The **Next** button finds and selects the next match for the **Find** string.

#### 3.3.8.2 Find Next (⌘G)

This command finds and selects the next match for the **Find** string.

#### 3.3.8.3 Find Previous (⇧⌘G)

This command finds and selects the previous match for the **Find** string.

#### 3.3.8.4 Use Selection for Find (⌘E)

This command sets the **Find** string to the current selection.

#### 3.3.8.5 Jump to Selection (⌘J)

This command brings the current selection into view.

## 3.4 The Text Menu

### 3.4.1 Load Selection (⌘K)

This command loads the constructs in the active edit window's current selection into CLIPS. Standard error detection and recovery routines used to load constructs from a file are also used when loading a selection (i.e., if a construct has an error in it, the rest of the construct will be skipped over until another construct to be loaded is found).

### 3.4.2 Batch Selection (⇧⌘K)

This command treats the active edit window's current selection as a batch file and executes it as a series of commands. Standard error detection and recovery routines used to load construct from a file are *not* used when batching a selection (i.e., if a construct has an error in it, a number of ancillary errors may be generated by subsequent parts of the same construct following the error).

### 3.4.3 Load Buffer

This command loads the constructs from the entire contents of active edit window into CLIPS. It is equivalent to selecting the entire buffer and executing a **Load Selection** command.

### 3.4.4 Balance (⌘B)

This command operates on the active edit window's current selection by expanding it until the selection begins and ends with parentheses and each parenthesis contained in the selection is properly nested (i.e. each left opening parenthesis has a properly nested right closing parenthesis and vice versa). Repeat­edly using this command will select larger and larger selections of text until a balanced se­lection cannot be found. The balance command is a purely textual operation and does not ignore parentheses contained within CLIPS string values.

### 3.4.5 Comment

This command operates on the current selection in the active edit window by adding a semicolon to the beginning of each line contained in the selection.

### 3.4.6 Uncomment

This command operates on the current selection in the active edit window by removing a semicolon (if one exists) from the beginning of each line contained in the selection.

## 3.5 The Environment Menu

### 3.5.1 Clear

This command is equivalent to the CLIPS command (clear). When this command is chosen, the CLIPS command (clear) will be echoed to the dialog window and exe­cuted. This command is not available when CLIPS is executing.

### 3.5.2 Load Constructs\... (⌘L)

This command displays the standard file selection dialog sheet, allowing the user to select a text file to be loaded into the knowledge base. This command is equivalent to the CLIPS command (load \<file-name\>). When this command is chosen and a file is se­lected, the appropriate CLIPS load command will be echoed to the environment window and executed.

### 3.5.3 Load Batch\... (⇧⌘L)

This command displays the standard file selection dialog sheet, allowing the user to select a text file to be executed as a batch file. This command is equivalent to the CLIPS command (batch \<file-name\>). When this command is chosen and a file is selected, the appropriate CLIPS batch command will be echoed to the environment window and executed.

### 3.5.4 Set Directory...

This command displays the standard folder selection dialog sheet, allowing the user to select the current directory associated with the environment. CLIPS file commands such as load, batch, and open use the current directory to determine the location where file operations should occur. The current directory for an environment window is displayed in the status pane below the window title.

### 3.5.5 Reset (⌘R)

This command is equivalent to the CLIPS command (reset). When this command is chosen, the CLIPS command (reset) will be echoed to the dialog window and exe­cuted.

### 3.5.6 Run (⇧⌘R)

This command is equivalent to the CLIPS command (run). When this command is cho­sen, the CLIPS command (run) will be echoed to the dialog window and executed.

### 3.5.7 Halt Rules (⌘.)

This command halts execution when the currently executing rule has finished executing all of its actions. This command has no effect if rules are not executing.

### 3.5.8 Halt Execution (⇧⌘.)

This command halts execution at the first available opportunity. If rules are executing, the currently executing rule may not complete all of its actions.

### 3.5.9 Clear Scrollback

This command clears all of the text in the dialog window. From the CLIPS command prompt, the command **clear-window** (which takes no arguments) will also clear all of the text in the environment window.

## 3.6 The Debug Menu

### 3.6.1 Watch Submenu

Watch items can be enabled or disabled by the appropriate menu item. Enabled watch items have a check to the left of the menu item. Disabled watch items have no check mark in their check box. Choosing the **All** menu item checks all of the watch items. Choosing the **None** menu item unchecks all of the watch items.

### 3.6.2 Agenda Browser

The **Agenda Browser** allows the activations on the agenda to be examined. The list on the left side of the window shows the modules currently on the focus stack. The list of the right side of the window shows the activations on the agenda of the selected module from the focus stack.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image13.png){width="6.5in" height="3.4349595363079617in"}

The **Reset** button sends a "(reset)" command to the dialog window. The **Run** button sends a "(run)" command to the dialog window. The **Step** button sends a "(run 1)" command to the dialog window. Pressing the **Halt Rules** button when rules are executing will halt execution when the currently executing rule has finished all of its actions.

### 3.6.3 Fact Browser

The **Fact Browser** allows the facts in the fact list to be examined. The list on the left side of the window shows the modules currently defined. The list in the middle of the window shows the facts that are visible to the selected module from the module list. The list on the right side of the window shows the slot values of the selected fact from the fact list.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image14.png){width="6.5in" height="3.5619192913385826in"}

The list of facts can be sorted based on either the fact index or the associated deftemplate name by clicking on either the **Index** or the **Template** column header. The list of slots can be sorted based on either the slot name or the slot value by clicking on either the **Slot** or the **Value** column header. If the **Display Defaulted Values** checkbox is enabled, then all of the slots of the selected fact will be displayed. If the checkbox is disabled, then only those slots that have a value different from their default slot value will be displayed.

The search text field can be used to filter the facts that are displayed in the fact list. When search text is entered and the return key is pressed each fact and its slots are examined to determine if the search text is found within one of the following templates:

f-\<index\>

\<deftemplate-name\> \<slot-name\> \<slot-value\>

For example, if the fact associated with the deftemplate thing had a fact index of 4 and slots name with value big-pillow, location with value t2-2, and on-top-of with value red-couch, then the fact would be displayed in the fact list only if the search text was found in one of the following strings:

f-4

thing name big-pillow

thing location t2-2

thing on-top-of red-couch

### 3.6.4 Instance Browser

The **Instance Browser** allows the instances in the instance list to be examined. The list on the left side of the window shows the modules currently defined. The list in the middle of the window shows the instances that are visible to the selected module from the module list. The list on the right side of the window shows the slot values of the selected instance from the instance list.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image15.png){width="6.5in" height="3.429589895013123in"}

The list of instances can be sorted based on either the instance name or the associated defclass name by clicking on either the **Name** or the **Class** column header. The list of slots can be sorted based on either the slot name or the slot value by clicking on either the **Slot** or the **Value** column header. If the **Display Defaulted Values** checkbox is enabled, then all of the slots of the selected instance will be displayed. If the checkbox is disabled, then only those slots that have a value different from their default slot value will be displayed.

The search text field can be used to filter the instances that are displayed in the instance list. When search text is entered and the return key is pressed each instance and its slots are examined to determine if the search text is found within one of the following templates:

\[\<name\>\]

\<defclass-name\> \<slot-name\> \<slot-value\>

For example, if the instance associated with the defclass THING had the instance name \[thing1\] and slots name with value big-pillow, location with value t2-2, and on-top-of with value red‑couch, then the instance would be displayed in the instance list only if the search text was found in one of the following strings:

\[thing1\]

THING name big-pillow

THING location t2-2

THING on-top-of red-couch

### 3.6.5 Construct Inspector

The **Construct Inspector** floats above the other CLIPS IDE windows and changes to show the text of the associated construct when one of the items from the browsers is selected.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image16.png){width="6.5in" height="1.812298775153106in"}

## 3.7 The Window Menu

The bottom portion of the Window menu (everything below the other window management menu items) is a list of all windows associated with the CLIPS IDE. A check mark is placed by the window name to indicate that it is the frontmost window. A filled circle appears next to an edit window title that has changes that need to be saved (unless it is the frontmost window).

## 3.8 The Help Menu

### 3.8.1 CLIPS Home Page

Opens the CLIPS Home web page on SourceForge.

### 3.8.2 Online Documentation

Opens a web page with links to CLIPS Documentation including the CLIPS User's Guide, CLIPS Reference Manuals, and other Documentation.

### 3.8.3 Online Examples

Opens a web page with links to example programs.

### 3.8.4 CLIPS Expert System Group

Opens the CLIPS Expert System Group web page on Google Groups.

### 3.8.5 SourceForge Forums

Opens the CLIPS Discussion Forums web page on SourceForge.

### 3.8.6 Stack Overflow Q&A

Opens the Stack Overflow web page for the CLIPS question tag.

## 3.9 Creating the macOS Executables

In order to create the macOSX executables, you must install the source code using the *clips_macos_project_642.dmg* disk image. This file can be downloaded from the SourceForge web site (see appendix A). Once downloaded, double click the file and then drag the *CLIPS Xcode Project* folder into the folder you'll be using for development. In addition to the source code specific to the macOS IDE, the core CLIPS source code is also included with the project, so there is no need to download this code separately.

### 3.9.1 Building the CLIPS IDE Using Xcode 16.2

Open the *CLIPS Xcode project* directory. Double click the *CLIPS.xcodeproj* file. After the file opens in the Xcode application, select the **Product** menu, then the **Scheme** submenu, and then select the **Edit Scheme...** menu item. On the **Info** tab, set the **Build Configuration** drop down menu to **Release** and the **Executable** drop down menu to **CLIPS IDE.app**. Select the **Build** menu item from the **Product** menu to create the CLIPS IDE executable. The generated executable can be found in the *:build:Release* folder.

#
