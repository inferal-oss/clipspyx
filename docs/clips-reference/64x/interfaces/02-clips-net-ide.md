# Section 2: CLIPS .NET IDE

This section provides a brief summary of the CLIPS 6.4 .NET Integrated Development Environment (IDE). The IDE provides a dialog pane that allows commands to be entered in a manner similar to the standard CLIPS command line interface. Any CLIPS I/O to standard input or standard output is directed to this dialog pane. In addition, the IDE also provides a browser pane for examining the current state of the CLIPS environment. When launched, the IDE displays a window containing a menu bar, a status bar, and a dialog pane:

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image3.png){width="6.105860673665791in" height="4.22in"}

The status bar is displayed beneath the menu bar. On the left side of the status bar is the current working directory. The splitter along the bottom edge of the dialog pane can be dragged to reveal or hide any browser tabs that are open in the browser pane.

Inline editing is supported in the dialog pane. The left and right arrow keys can be used to move the caret backwards and forwards through the current command. Pressing the delete key will delete the character to the left of the caret. Insertion of other characters or pasted text occurs at the caret. The esc key moves the caret to the end of the current command. The caret must be at the end of the current command in order for pressing the return key to execute the command.

A command history is also supported for the dialog pane. The up and down arrows allow you to cycle through the command history. The up arrow restores the previous command and the down arrow restores the next command. Holding the shift key down when the up or down arrow is pressed takes you respectively to the beginning or end of the command history.

From the CLIPS command prompt, the command **clear-window** (which takes no arguments) will also clear all of the text in the dialog pane.

Holding down the **control** key while pressing the period key will halt rule execution. The RHS actions of the currently executing rule will be allowed to complete before rule execution is halted. Holding down the **shift** key, the **control** key, and the H key will halt rule execution after the current RHS action. Remaining RHS actions will not be executed. This key combination can also be used to halt the execution of commands and functions that loop. The **Halt Rules** menu item can also be selected from the Environment menu during execution. Selecting this menu item is equivalent to holding down the **control** key while pressing the H key. The **Halt Execution** menu item can also be selected from the Environment menu during execution. Selecting this menu item is equivalent to holding down the **shift** key and the **control** key while pressing the H key.

## 2.1 The File Menu

### 2.1.1 Quit

This command exits CLIPS.

## 2.2 The Edit Menu

### 2.2.1 Cut (Ctrl+X)

This command removes selected text in the dialog pane and places it in the Clipboard. Only selected text from the current command being entered can be cut.

### 2.2.2 Copy (Ctrl+C)

This command copies selected text in the dialog pane and places it in the Clipboard.

### 2.2.3 Paste (Ctrl+V)

This command copies the contents of the Clipboard to the selection point or selected text in the dialog pane. Text can only be pasted into the current command being entered.

### 2.2.4 Set Dialog Font\... (Ctrl+V)

This command allows the font used in the main dialog window to be changed.

### 2.2.5 Set Browser Font\... (Ctrl+V)

This command allows the font used for displaying data in the browser tabs to be changed.

## 2.3 The Environment Menu

### 2.3.1 Clear

This command is equivalent to the CLIPS command (clear). When this command is chosen, the CLIPS command (clear) will be echoed to the dialog pane and exe­cuted. This command is not available when CLIPS is executing.

### 2.3.2 Load Constructs\... (Ctrl+L)

This command displays a file selection dialog, allowing the user to select a text file containing constructs to be loaded into CLIPS. This command is equivalent to the CLIPS command (load \<file-name\>). When this command is chosen and a file is se­lected, the appropriate CLIPS load command will be echoed to the dialog pane and executed.

### 2.3.3 Load Batch\... (Ctrl+Shift+L)

This command displays a file selection dialog, allowing the user to select a text file to be executed as a batch file. This command is equivalent to the CLIPS command (batch \<file-name\>). When this command is chosen and a file is selected, the appropriate CLIPS batch command will be echoed to the dialog pane and executed.

### 2.3.4 Set Directory...

This command displays a folder selection dialog, allowing the user to select the current directory associated with the CLIPS environment. File commands such as load, batch, and open use the current directory to determine the location where file operations should occur. The current directory for the dialog pane is displayed in the status bar.

### 2.3.5 Reset (Ctrl+R)

This command is equivalent to the CLIPS command (reset). When this command is chosen, the CLIPS command (reset) will be echoed to the dialog pane and exe­cuted.

### 2.3.6 Run (Ctrl+Shift+R)

This command is equivalent to the CLIPS command (run). When this command is cho­sen, the CLIPS command (run) will be echoed to the dialog pane and executed.

### 2.3.7 Halt Rules (Ctrl+H)

This command halts execution when the currently executing rule has finished executing all of its actions. This command has no effect if rules are not executing.

### 2.3.8 Halt Execution (Ctrl+Shift+H)

This command halts execution at the first available opportunity. If rules are executing, the currently executing rule may not complete all of its actions.

### 2.3.9 Clear Scrollback

This command clears all of the text in the dialog pane. From the CLIPS command prompt, the command **clear-window** (which takes no arguments) will also clear all of the text in the dialog pane.

## 2.5 The Debug Menu

### 2.5.1 Watch Submenu

Watch items can be enabled or disabled by the appropriate menu item. Enabled watch items have a check to the left of the menu item. Disabled watch items have no check mark in their check box. Choosing the **All** menu item checks all of the watch items. Choosing the **None** menu item unchecks all of the watch items.

### 2.5.2 Agenda Browser

The **Agenda Browser** allows the activations on the agenda to be examined. The list on the left side of the browser shows the modules currently on the focus stack. The list of the right side of the browser shows the activations on the agenda of the selected module from the focus stack.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image4.png){width="6.1906944444444445in" height="2.576388888888889in"}

The **Reset** button sends a "(reset)" command to the dialog pane. The **Run** button sends a "(run)" command to the dialog pane. The **Step** button sends a "(run 1)" command to the dialog pane. Pressing the **Halt Rules** button when rules are executing will halt execution when the currently executing rule has finished all of its actions.

### 2.5.3 Fact Browser

The **Fact Browser** allows the facts in the fact list to be examined. The list on the left side of the browser shows the modules currently defined. The list in the middle of the browser shows the facts that are visible to the selected module from the module list. The list on the right side of the browser shows the slot values of the selected fact from the fact list.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image5.png){width="6.24in" height="2.758888888888889in"}

The list of facts can be sorted based on either the fact index or the associated deftemplate name by clicking on either the **Index** or the **Template** column header. The list of slots can be sorted based on either the slot name or the slot value by clicking on either the **Slot** or the **Value** column header. If the **Display Defaulted Values** checkbox is enabled, then all of the slots of the selected fact will be displayed. If the checkbox is disabled, then only those slots that have a value different from their default slot value will be displayed.

The search text field can be used to filter the facts that are displayed in the fact list. When search text is entered and the return key is pressed each fact and its slots are examined to determine if the search text is found within one of the following templates:

f-\<index\>

\<deftemplate-name\> \<slot-name\> \<slot-value\>

For example, if the fact associated with the deftemplate thing had a fact index of 4 and slots name with value big-pillow, location with value t2-2, and on-top-of with value red-couch, then the fact would be displayed in the fact list only if the search text was found in one of the following strings:

f-4

thing name big-pillow

thing location t2-2

thing on-top-of red-couch

### 2.5.4 Instance Browser

The **Instance Browser** allows the instances in the instance list to be examined. The list on the left side of the browser shows the modules currently defined. The list in the middle of the browser shows the instances that are visible to the selected module from the module list. The list on the right side of the browser shows the slot values of the selected instance from the instance list.

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image6.png){width="6.5in" height="2.7102274715660544in"}

The list of instances can be sorted based on either the instance name or the associated defclass name by clicking on either the **Name** or the **Class** column header. The list of slots can be sorted based on either the slot name or the slot value by clicking on either the **Slot** or the **Value** column header. If the **Display Defaulted Values** checkbox is enabled, then all of the slots of the selected instance will be displayed. If the checkbox is disabled, then only those slots that have a value different from their default slot value will be displayed.

The search text field can be used to filter the instances that are displayed in the instance list. When search text is entered and the return key is pressed each instance and its slots are examined to determine if the search text is found within one of the following templates:

\[\<name\>\]

\<defclass-name\> \<slot-name\> \<slot-value\>

For example, if the instance associated with the defclass THING had the instance name \[thing1\] and slots name with value big-pillow, location with value t2-2, and on-top-of with value red‑couch, then the instance would be displayed in the instance list only if the search text was found in one of the following strings:

\[thing1\]

THING name big-pillow

THING location t2-2

THING on-top-of red-couch

## 2.6 The Help Menu

### 2.6.1 CLIPS Home Page

Opens the CLIPS Home web page on SourceForge.

### 2.6.2 Online Documentation

Opens a web page with links to CLIPS Documentation including the CLIPS User's Guide, CLIPS Reference Manuals, and other Documentation.

### 2.6.3 Online Examples

Opens a web page with links to example programs.

### 2.6.4 CLIPS Expert System Group

Opens the CLIPS Expert System Group web page on Google Groups.

### 2.6.5 SourceForge Forums

Opens the CLIPS Discussion Forums web page on SourceForge.

### 2.6.6 Stack Overflow Q&A

Opens the Stack Overflow web page for the CLIPS question tag.

### 2.6.7 About CLIPS IDE

This command displays version information about the CLIPS IDE application.

## 2.8 Building the Windows Executables

In order to create the Windows executables, you must install the source code by downloading the *clips_windows_projects_642.zip file* (see appendix A for information on obtaining CLIPS). Once downloaded, you must then extract the contents of the file by right clicking on it and selecting the **Extract All...** menu item. Drag the *clips_windows_projects_642* directory into the directory you'll be using for development. In addition to the source code specific to the Windows projects, the core CLIPS source code is also included, so there is no need to download this code separately.

### 2.8.1 Building CLIPSIDE Using Microsoft Visual Studio Community 2022

Navigate to the *MVS_2022* directory. Open the file *CLIPS.sln* by double clicking on it or right click on it and select the **Open** menu item. After the file opens in Visual Studio, select **Configuration Manager...** from the **Build** menu. Select the **Release** configuration for CLIPSIDE, the appropriate platform (either **x64** for a 64-bit system or **x86** for a 32-bit system), and then click the **Close** button. Right click on the CLIPSIDE project name in the Solution Explorer and select the **Build** menu item. When compilation is complete, the CLIPSIDE executable will be in the corresponding \<Platform\>\\\<Configuration\> directory of *MVS_2022\\CLIPSIDE\\bin*.

### 2.8.2 Building CLIPSDOS Using Microsoft Visual Studio Community 2022

Navigate to the *MVS_2022* directory. Open the file *CLIPS.sln* by double clicking on it or right click on it and select the **Open** menu item. After the file opens in Visual Studio, select **Configuration Manager...** from the **Build** menu. Select the **Release** configuration for CLIPSDOS, the appropriate platform (either **x64** for a 64-bit system or **Win32** for a 32-bit system), and then click the **Close** button. Right click on the CLIPSDOS project name in the Solution Explorer and select the **Build** menu item. When compilation is complete, the CLIPSDOS executable will be in the corresponding \<Platform\>\\\<Configuration\> directory of the *MVS_2022\\CLIPSDOS\\Executables*.
