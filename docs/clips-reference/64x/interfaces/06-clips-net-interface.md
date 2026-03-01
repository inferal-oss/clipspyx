# Section 6: CLIPS .NET Interface

This section describes various techniques for integrating CLIPS and creating executables when using Microsoft .NET. The examples in this section have been tested running on Windows 11 with Visual Studio Community 2022.

## 6.1 Installing the Source Code

In order to create the Windows .NET DLL and executables, you must install the source code by downloading the *clips_windows_projects_642.zip* file (see appendix A for information on obtaining CLIPS). Once downloaded, you must then extract the contents of the file by right clicking on it and selecting the **Extract All...** menu item. Drag the *clips_windows_projects_642* directory into the directory you'll be using for development. In addition to the source code specific to the Windows projects, the core CLIPS source code is also included, so there is no need to download this code separately.

## 6.2 Building the .NET Library and Example Executables

The Visual Studio CLIPS solution file includes nine .NET projects:

- AnimalFormsExample

- AnimalWPFExample

- AutoFormsExample

- AutoWPFExample

- CLIPSCLRWrapper

- RouterFormsExample

- RouterWPFExample

- WineFormsExample

- WineWPFExample

The CLIPSCLRWrapper project creates a .NET DLL using a Common Language Runtime wrapper around the native CLIPS code. There are four examples utilizing the DLL with each example implemented using a Windows Forms project and a Windows Presentation Foundation project (for a total of eight projects).

### 6.2.1 Building the Projects Using Microsoft Visual Studio Community 2022

Navigate to the *MVS_2022* directory and open the file CLIPS.sln by double clicking on it (or right click on it and select the **Open** menu item). After the file opens in Visual Studio, select **Configuration Manager...** from the **Build** menu. Select the Configuration (**Debug** or **Release**) and the Platform (**x86** or **x64**) for each project and then click the **Close** button. To compile projects individually, right click on the project name in the Solution Explorer pane and select the **Build** menu item. When compilation is complete, each example application will be in the *\<Platform\>\\\<Configuration\>* subdirectory of the corresponding project *bin* directory and the .NET DLL files will be in the similar subdirectory of the *Libraries* directory of the *CLIPSCLRWrapper* project.

## 6.3 Running the .NET Demo Programs

The CLIPS .NET demonstration programs can be run on Windows by double clicking their executable. The CLIPSCLRWrapper.dll file must be in the same directory as the executable.

### 6.3.1 Wine Demo

When launched, the Wine Demo window should appear (WPF version pictured):

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image22.png){width="4.66in" height="4.3in"}

### 6.3.2 Auto Demo

When launched, the Auto Demo window should appear (Forms version pictured):

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image23.png){width="3.58in" height="2.21in"}

### 6.3.3 Animal Demo

When launched, the Animal Demo window should appear (WPF version pictured):

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image24.png){width="3.58in" height="2.21in"}

### 6.3.4 Router Demo

When launched, the Router Demo window should appear (Forms version pictured):

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image25.png){width="5.99in" height="3.05in"}

## 6.4 CLIPS .NET Classes

This section describes the classes and methods available in the CLIPSCLRWrapper.dll file for developing CLIPS .NET applications. These classes and methods reside in the CLIPSNET namespace.

### 6.4.1 The Environment Class

public class Environment

.NET programs interacting with CLIPS must create at least one instance of the **Environment** class.

#### 6.4.1.1 Constructors

public Environment();

#### 6.4.1.2 Clearing, Loading, and Creating Constructs

public void Clear();

public void Load(String fileName);

public void LoadFromString(String loadString);

public void LoadFromResource(String assemblyName, String resourceFile);

public void Build(String buildString);

The **Clear** method removes all constructs from an **Environment** instance. The **Load**, **LoadFromString**, and **LoadFromResource** methods load constructs into an **Environment** instance. The **fileName** parameter of the **Load** method specifies a file path to a text file containing constructs. The **loadString** parameter of the **LoadFromString** method is a string containing constructs. The **resourceFile** parameter of the **LoadFromResource** string specifies the resource path to a text file containing constructs and the **assemblyName** parameter specifies the assembly in which it's contained. The **Build** method loads a single construct into an **Environment** instance; it returns true if the construct was successfully loaded, otherwise it returns false.

A **CLIPSException** is thrown by the **Clear** and **Build** methods if an error occurs. A **CLIPSLoadException** is thrown by the **Load**, **LoadFromString**, and **LoadFromResource** methods if an error occurs.

#### 6.4.1.3 Executing Rules

public void Reset();

public long long Run(long long runLimit);

public long long Run();

The **Reset** method removes all fact and instances from an **Environment** instance and creates the facts and instances specified in deffacts and definstances constructs. The **Run** method executes the number of rules specified by the **runLimit** parameter or all rules if the **runLimit** parameter is unspecified. The **Run** method returns the number of rules executed (which may be less than the **runLimit** parameter value). A **CLIPSException** is thrown by the **Reset** and **Run** methods if an error occurs.

#### 6.4.1.4 Creating Facts and Instances

public FactAddressValue AssertString(String factString);

public InstanceAddressValue MakeInstance(String instanceString);

The **AssertString** method asserts a fact using the deftemplate and slot values specified by the **factString** parameter. The **MakeInstance** method creates an instance using the instance name, defclass, and slot values specified by the **instanceString** parameter. A **CLIPSException** is thrown by the **AssertString** and **MakeInstance** methods if an error occurs.

#### 6.5.1.5 Searching for Facts and Instances

public FactAddressValue FindFact(\
String deftemplate);

public FactAddressValue FindFact(\
String variable,\
String deftemplateName,\
String condition);

public List\<FactAddressValue\> FindAllFacts(\
String deftemplateName);

public List\<FactAddressValue\> FindAllFacts(\
String variable,\
String deftemplateName,\
String condition);

public InstanceAddressValue FindInstance(\
String defclassName);

public InstanceAddressValue FindInstance(\
String variable,\
String defclassName,\
String condition);

public List\<InstanceAddressValue\> FindAllInstances(\
String defclassName);

public List\<InstanceAddressValue\> FindAllInstances(\
String variable,\
String defclassName,\
String condition);

The **FindFact** methods return the first fact associated with the deftemplate construct specified by the **deftemplateName** parameter. The optional **variable** and **condition** parameters can be jointly specified to restrict the fact returned by specifying a CLIPS expression that must evaluate to a value other FALSE in order for the fact to be returned. Each fact of the specified deftemplate will be tested until a fact satisfying the condition is found. The fact being tested is assigned to the CLIPS variable specified by the **variable** parameter and may be referenced in the **condition** parameter. If no facts of the specified deftemplate exist, or no facts satisfy the condition, the value nullptr is returned. A **CLIPSException** is thrown if an error occurs.

The **FindAllFacts** methods returns the list of facts associated with the deftemplate construct specified by the **deftemplateName** parameter. The optional **variable** and **condition** parameters can be jointly specified to restrict the facts returned by specifying a CLIPS expression that must evaluate to a value other FALSE in order for a fact to be returned. Each fact of the specified deftemplate will be tested to determine whether it will be added to the list. The fact being tested is assigned to the CLIPS variable specified by the **variable** parameter and may be referenced in the **condition** parameter. If no facts of the specified deftemplate exist, or no facts satisfy the condition, a list with no members is returned. A **CLIPSException** is thrown if an error occurs.

The **FindInstance** methods return the first instance associated with the defclass construct specified by the **defclassName** parameter. The optional **variable** and **condition** parameters can be jointly specified to restrict the instance returned by specifying a CLIPS expression that must evaluate to a value other FALSE in order for the instance to be returned. Each instance of the specified defclass will be tested until an instance satisfying the condition is found. The instance being tested is assigned to the CLIPS variable specified by the **variable** parameter and may be referenced in the **condition** parameter. If no instances of the specified defclass exist, or no instances satisfy the condition, the value nullptr is returned. A **CLIPSException** is thrown if an error occurs.

The **FindAllInstances** methods returns the list of instances associated with the defclass construct specified by the **defclassName** parameter. The optional **variable** and **condition** parameters can be jointly specified to restrict the instances returned by specifying a CLIPS expression that must evaluate to a value other FALSE in order for an instance to be returned. Each instance of the specified defclass will be tested to determine whether it will be added to the list. The instance being tested is assigned to the CLIPS variable specified by the **variable** parameter and may be referenced in the **condition** parameter. If no instances of the specified defclass exist, or no instances satisfy the condition, a list with no members is returned. A **CLIPSException** is thrown if an error occurs.

#### 6.5.1.5 Executing Functions and Commands

public PrimitiveValue Eval(String evalString);

The **Eval** method evaluates the command or function call specified by the **evalString** parameter and returns the result of the evaluation. A **CLIPSException** is thrown if an error occurs.

#### 6.5.1.6 Debugging

public void Watch(String watchItem);

public void Unwatch(String watchItem);

public bool GetWatchItem(String watchItem);

public void SetWatchItem(String watchItem,bool newValue);

The **watchItem** parameter should be one of the following static String values defined in the Environment class: FACTS, RULES, DEFFUNCTIONS, COMPILATIONS, INSTANCES, SLOTS, ACTIVATIONS, STATISTICS, FOCUS, GENERIC_FUNCTIONS, METHODS, GLOBALS, MESSAGES, MESSAGE_HANDLERS, NONE, or ALL.

The **Watch** method enables the specified watch item and the **Unwatch** method disables the specified watch item. The **GetWatchItem** method returns the current state of the specified watch item. The **SetWatchItem** method enables the specified watch item if the **newValue** parameter is true and disables it if the **newValue** parameter is false.

#### 6.5.1.7 Adding and Removing User Functions

public void AddUserFunction(\
String functionName,\
UserFunction callback);

public void AddUserFunction(\
String functionName,\
String returnTypes,\
unsigned short minArgs,\
unsigned short maxArgs,\
String argTypes,\
UserFunction callback);

public void RemoveUserFunction(\
String functionName);

The **AddUserFunction** method associates a CLIPS function name (specified by the **functionName** parameter) with an instance of a .NET class inheriting from the **UserFunction** class (specified by the **callback** parameter). This allows you to call .NET code from within CLIPS code. The optional parameters **returnTypes**, **minArg**, **maxArgs**, and **argTypes** can be used to specify the CLIPS primitive types returned by the function, the minimum and maximum number of arguments the function is expecting, and the primitive types allowed for each argument. The UNBOUNDED constant from the **UserFunction** class can be used for the **maxArgs** parameter to indicate that there is no upper limit on the number of arguments.

If the **returnTypes** parameter value is nullptr, then CLIPS assumes that the UDF can return any valid type. Specifying one or more type character codes, however, allows CLIPS to detect errors when the return value of a UDF is used as a parameter value to a function that specifies the types allowed for that parameter. The following codes are supported for return values and argument types:

  --------------- --------------------------------------------------------
   **Type Code**  **Type**

         b        Boolean

         d        Double Precision Float

         e        External Address

         f        Fact Address

         i        Instance Address

         l        Long Long Integer

         m        Multifield

         n        Instance Name

         s        String

         y        Symbol

         v        Void---No Return Value

        \*        Any Type
  --------------- --------------------------------------------------------

If the **argTypes** parameter value is null, then there are no argument type restrictions. One or more character argument types can also be specified, separated by semicolons. The first type specified is the default type (used when no other type is specified for an argument), followed by types for specific arguments. For example, \"ld\" indicates that the default argument type is an integer or float; \"ld;s\" indicates that the default argument type is an integer or float, and the first argument must be a string; \"\*;;m\" indicates that the default argument type is any type, and the second argument must be a multifield; \";sy;ld\" indicates that the default argument type is any type, the first argument must be a string or symbol; and the second argument type must be an integer or float.

The **AddUserFunction** method throws an **ArgumentException** if the association fails because one already exists for the **functionName** parameter.

The **RemoveUserFunction** method removes the association between a CLIPS function name and the user function code associated the function name. You can use this to remove a previously created associated (either to remove it altogether or to replace the old associated with a new one). The **RemoveUserFunction** method throws an **ArgumentException** if no association currently exists for the **functionName** parameter.

#### 6.5.1.8 Managing Routers

public void AddRouter(\
Router theRouter);

public void DeleteRouter(\
Router theRouter);

public void ActivateRouter(\
Router theRouter);

public void DeactivateRouter(\
Router theRouter);

public void Write(\
String logicalName,\
String printString);

public void Write(\
String printString);

public void WriteLine(\
String logicalName,\
String printString);

public void WriteLine(\
String printString);

The **AddRouter** method adds an instance of a .NET class inheriting from the **Router** class to the list of routers checked by CLIPS for processing I/O requests. The **DeleteRouter** method removes a Router instance from the list of CLIPS routers. The methods **DeactivateRouter** and **ActivateRouter** allow a router to be disabled/enabled without removing it from the list of routers.

The **Write** and **WriteLine** methods output the string specified by the **printString** parameter through the router system. These methods direct the output to the logical name specified by the **logicalName** parameter. If the **logicalName** parameter is unspecified, output is directed to standard output. In addition, the **WriteLine** method appends a carriage return to the output.

#### 6.5.1.9 Command Loop

public void CommandLoop();

The **CommandLoop** method starts the CLIPS Read-Eval-Print Loop (REPL) using the .NET standard input and output streams.

### 6.5.2 The PrimitiveValue Class and Subclasses

public class PrimitiveValue abstract

public class VoidValue : PrimitiveValue

public class NumberValue abstract : PrimitiveValue

public class FloatValue : NumberValue

public class IntegerValue : NumberValue

public class LexemeValue abstract : PrimitiveValue

public class SymbolValue : LexemeValue

public class StringValue : LexemeValue

public class InstanceNameValue : LexemeValue

public class MultifieldValue : PrimitiveValue , IEnumerable

public class FactAddressValue : PrimitiveValue

public class InstanceAddressValue : PrimitiveValue

public class ExternalAddressValue : PrimitiveValue

The **PrimitiveValue** class and its subclasses constitute the .NET representation of the CLIPS primitive data types. Several methods (such as **Eval** and **GetSlotValue**) return objects belonging to concrete subclasses of the **PrimitiveValue** class.

Several methods are provided for determining the type of a PrimitiveValue object:

public CLIPSNetType CLIPSType();

public bool IsVoid();

public bool IsLexeme();

public bool IsSymbol();

public bool IsString();

public bool IsInstanceName();

public bool IsNumber();

public bool IsFloat();

public bool IsInteger();

public bool IsFactAddress();

public bool IsInstance();

public bool IsInstanceAddress();

public bool IsMultifield();

public bool IsExternalAddress();

The **CLIPSType** method returns one of the following **CLIPSNETType** enumerations: FLOAT, INTEGER, SYMBOL, STRING, MULTIFIELD, EXTERNAL_ADDRESS, FACT_ADDRESS, INSTANCE_ADDRESS, INSTANCE_NAME, or VOID.

Several methods are provided for creating objects belonging to the **FloatValue**, **IntegerValue**, **SymbolValue**, **StringValue**, **InstanceNameValue**, **MultifieldValue**, and **VoidValue** classes:

public FloatValue();

public FloatValue(long long value);

public FloatValue(double value);

public IntegerValue();

public IntegerValue(long long value);

public IntegerValue(double value);

public SymbolValue()

public SymbolValue(String value);

public StringValue();

public StringValue(String value);

public InstanceNameValue();

public InstanceNameValue(String value);

public MultifieldValue();

public MultifieldValue(List\<PrimitiveValue\> value);

public VoidValue();

The **AssertString** and **MakeInstance** methods of the **Environment** class can be used to create objects of the **FactAddressValue** and **InstanceAddressValue** classes respectively.

The following **NumberValue** operators are available for retrieving the underlying .NET value from **NumberValue** objects:

public static operator long long (NumberValue \^ val);

public static operator double (NumberValue \^ val);

The **Value** property is available for retrieving the underlying .NET value from **IntegerValue** objects:

property long long Value { get; }

The **Value** property is available for retrieving the underlying .NET value from **FloatValue** objects:

property double Value { get; }

The **Value** property is provided to retrieve the underlying Java value from **SymbolValue**, **StringValue**, and **InstanceNameValue** objects:

public property String \^ Value { get; }

The **InstanceNameValue** class also provides a method for converting an instance name to the corresponding instance address in a specified environment:

public InstanceAddressValue GetInstance (Environment theEnv);

The following **MultifieldValue** properties provide access to the list of **PrimitiveValue** objects contained in a **MultifieldValue** method:

property PrimitiveValue \^ default\[int\] { get; }

property List\<PrimitiveValue \^\> \^ Value { get; }

public property int Count { get; }

The following **FactAddressValue** methods and properties provide access to the slot values and fact index of the associated CLIPS fact:

public property PrimitiveValue default\[String\] { get; }

public PrimitiveValue GetSlotValue(String slotName) { get; }

public property long long FactIndex { get; }

The following **InstanceAddressValue** methods and properties provide access to the slot values and instance name of the associated CLIPS instance:

public property PrimitiveValue default\[String\] { get; }

public PrimitiveValue GetSlotValue(String slotName);

public property String InstanceName { get; }

Access to the underlying values of **ExternalAddressValue** objects is not currently supported.

### 6.5.3 The CLIPSException and CLIPSLoadException Classes

public class CLIPSException : Exception

public class CLIPSLoadException : CLIPSException

CLIPS.NET provides two subclasses of the **Exception** class for methods generating errors: CLIPS **Exception** and **CLIPSLoadException**.

#### 6.5.3.1 CLIPSLoadException Properties

public property CLIPSLineError \^ default\[int\] { get; }

public property List\<CLIPSLineError\> LineErrors { get; }

public property int Count { get; }

public class CLIPSLineError;

Loading constructs can generate multiple errors, so the **LineErrors** property of the **CLIPSLoadException** class returns the list of **CLIPSLineError** objects detailing each error.

##### 6.5.3.1.1 CLIPSLineError Properties

public property String FileName { get; }

public property long LineNumber { get; }

public property String Message { get; }

The **FileName,** **LineNumber**, and **Message** properties respectively return the file name, line number, and error message associated with a **CLIPSLineError** object.

### 6.5.4 The Router Class

public class Router

The **Router** class allows .NET objects to interact with the CLIPS I/O router system.

#### 6.5.4.1 Required Properties and Methods

public property int Priority { get; set; }

public property String Name;

public virtual bool Query(String logicalName);

public virtual void Write(String logicalName,String writeString);

public virtual int Read(String logicalName);

public virtual int Unread(String logicalName,int theChar);

public void Exit(bool failure);

The **Priority** property is the integer priority of the router. Routers with higher priorities are queried before routers of lower priority to determine if they can process an I/O request. The **Name** property is the identifier associated with the router. The **Query** method is called to determine if the router handles I/O requests for the **logicalName** parameter. It should return true if the router can process the request, otherwise it should return false. The **Write** method is called to output the value specified by the **writeString** parameter to the **logicalName** parameter. The **Read** method returns an input character for the **logicalName** parameter. It should return -1 if no characters are available in the input queue. The **Read** method places the character specified by parameter **theChar** back on the input queue so that it is available for the next **Read** request. It returns the value of parameter **theChar** if successful, otherwise it returns -1. The **Exit** method is invoked when the CLIPS **exit** command is issued or an unrecoverable error occurs. The **failure** parameter will either be false for an exit command or true for an unrecoverable error.

#### 6.5.4.2 Predefined Router Names

public static String STDIN;

public static String STDOUT;

public static String STDWRN;

public static String STDERR;

The String constants STDIN, STDOUT, STDWRN, and STDERR are the standard predefined logical names used by CLIPS.

#### 6.5.4.3 The BaseRouter Class

public class BaseRouter : Router

The **BaseRouter** class is an implementation of the **Router** interface. Its **Write**, **Read**, **Unread**, and **Exit** methods are minimal implementations; the **Write** and **Exit** methods execute no statements and the **Read** and **Unread** methods always return -1. Subclasses can override these methods as needed to create functional routers.

##### 6.5.4.3.1 Constructors

public BaseRouter(\
Environment env,\
String \[\] queryNames);

public BaseRouter(\
Environment env,\
String \[\] queryNames,\
int priority);

public BaseRouter(\
Environment env,\
String \[\] queryNames,\
int priority,\
String routerName);

The **BaseRouter** constructor requires the **env** and **queryName** parameters. Optionally, the **priority** parameter or the **priority** and **routerName** parameters can be supplied. The **env** parameter is the **Environment** object associated with the **Router** object. The **queryNames** parameter is an array of strings used by the **Query** method of the **BaseRouter** object to determine whether the router handles I/O for a specific logical name. The **priority** parameter is the priority of the router; if it is unspecified, it defaults to 0. The **routerName** parameter is the name that serves as an identifier for the **BaseRouter** object; if it is unspecified an identifier will be generated for the router.

### 6.5.5 The UserFunction Class

public class UserFunction

The **UserFunction** class provides a method for invoking a .NET method from CLIPS code.

#### 6.5.5.1 Required Methods

public PrimitiveValue Evaluate(List\<PrimitiveValue\> arguments);

Once a linkage has been made between a CLIPS function name and an object implementing the **UserFunction** interface, the **Evaluate** method is invoked when the linked CLIPS function call is executed. The **function** arguments are evaluated and passed to the evaluate method via the **arguments** parameter.

#### 6.5.5.2 Constants

public static unsigned short UNBOUNDED;

The UNBOUNDED constant can be used for the **maxArgs** parameter of the **AddUserFunction** method of the **Environment** class to indicate that there is no upper limit on the number of arguments.

### 6.5.6 Examples

The following examples require a new **Console Application** project to be created in a solution containing the **CLIPSCLRWrapper** project.

To create a new project, right click on the solution in the **Solution Explorer** and select the **Add -\> New Project...** menu item. In the **language** dropdown menu, select **C#**. In the **platform** dropdown menu, select **Windows**. In the **project types** dropdown, select **Console**. In the list of available projects, select **Console Application**. Click the **Next** button.

Enter Example as the content of the **Project name** text box and then click the **Next** button.

Select the appropriate Target Framework (or use the default framework) and then click the **Create** button to add the new project to the solution.

The new project must reference the **CLIPSCLRWrapper** project. To add a reference, right click on **Dependencies** in the **Example** project in the **Solution Explorer** and then select the **Add Project Reference...** menu item. In the left pane of the dialog that appears, select **Solution** under **Projects**. In the middle pane, check the box for the **CLIPSCLRWrapper** project. Finally, click the **OK** button.

#### 6.5.6.1 Loading Constructs from an Embedded Resource file

This example demonstrates how to load a CLIPS source file that has been embedded in the application.

First, right click on the Example project, select **Add -\> New Item...** menu item. Under **Visual C# Items -\> General**, select **Text File**, change the name to hello.clp, and then click the **Add** button. Select the hello.clp file in the Solution Explorer and then change the **Build Action** in the Properties window to **Embedded Resource**.

Add the following content:

(defrule hello

=\>

(println \"Hello World\"))

Next replace the contents of the Program.cs file with the following code:

using CLIPSNET;

namespace Example

{

class Program

{

static void Main(string\[\] args)

{

CLIPSNET.Environment clips = new CLIPSNET.Environment();

clips.LoadFromResource(\"Example\",\"Example.hello.clp\");

clips.Watch(CLIPSNET.Environment.RULES);

clips.Reset();

clips.Run();

}

}

}

Finally, build and run the program:

FIRE 1 hello: \*

Hello World

#### 6.5.6.2 Fact Query

This example demonstrates how to query CLIPS to retrieve facts.

First, replace the contents of the Program.cs file with the following code:

using System;

using System.Collections.Generic;

using CLIPSNET;

namespace Example

{

class Program

{

static void Main(string\[\] args)

{

CLIPSNET.Environment clips = new CLIPSNET.Environment();

clips.Build(\"(deftemplate person (slot name) (slot age))\");

clips.AssertString(\"(person (name \\\"Fred Jones\\\") (age 17))\");

clips.AssertString(\"(person (name \\\"Sally Smith\\\") (age 23))\");

clips.AssertString(\"(person (name \\\"Wally North\\\") (age 35))\");

clips.AssertString(\"(person (name \\\"Jenny Wallis\\\") (age 11))\");

Console.WriteLine(\"All people:\");

List\<FactAddressValue\> people = clips.FindAllFacts(\"person\");

foreach (FactAddressValue p in people)

{ Console.WriteLine(\" \" + p\[\"name\"\]); }

Console.WriteLine(\"All adults:\");

people = clips.FindAllFacts(\"?f\",\"person\",\"(\>= ?f:age 18)\");

foreach (FactAddressValue p in people)

{ Console.WriteLine(\" \" + p\[\"name\"\]); }

}

}

}

Next, build and run the program:

All people:

\"Fred Jones\"

\"Sally Smith\"

\"Wally North\"

\"Jenny Wallis\"

Adults:

\"Sally Smith\"

\"Wally North\"

#### 6.5.6.3 Big Integer Multiplication User Function

This example demonstrates how to add a user function to multiply two numbers together using big integer math. It also demonstrates using the **Eval** method to evaluate a CLIPS function call.

Replace the contents of the Program.cs file with the following code:

using System;

using System.Collections.Generic;

using System.Numerics;

using CLIPSNET;

namespace Example

{

public class BIM_UDF : UserFunction

{

public BIM_UDF()

{

}

public override PrimitiveValue Evaluate(List\<PrimitiveValue\> arguments)

{

LexemeValue lv = (LexemeValue) arguments\[0\];

BigInteger rv = BigInteger.Parse(lv.Value);

for (int i = 1; i \< arguments.Count; i++)

{

lv = (LexemeValue) arguments\[i\];

rv = BigInteger.Multiply(rv,BigInteger.Parse(lv.Value));

}

return new StringValue(rv.ToString());

}

}

class Program

{

static void Main(string\[\] args)

{

CLIPSNET.Environment clips = new CLIPSNET.Environment();

clips.AddUserFunction(\"bi\*\",\"s\",2,UserFunction.UNBOUNDED,\"s\",

new BIM_UDF());

Console.WriteLine(\"(\* 9 8) = \" +

clips.Eval(\"(\* 9 8)\"));

Console.WriteLine(\"(bi\* \\\"9\\\" \\\"8\\\") = \" +

clips.Eval(\"(bi\* \\\"9\\\" \\\"8\\\")\"));

Console.WriteLine(\"(\* 4294967296 4294967296) = \" +

clips.Eval(\"(\* 4294967296 4294967296)\"));

Console.WriteLine(\"(bi\* \\\"4294967296\\\" \\\"4294967296\\\") = \" +

clips.Eval(\"(bi\* \\\"4294967296\\\" \\\"4294967296\\\")\"));

}

}

}

Finally, build and run the program:

(\* 9 8) = 72

(bi\* \"9\" \"8\") = \"72\"

(\* 4294967296 4294967296) = 0

(bi\* \"4294967296\" \"4294967296\") = \"18446744073709551616\"

\$

#### 6.5.6.4 Get Properties User Function

This example demonstrates how to add a user function that returns a multifield value containing the list of environment variables.

First, replace the contents of the Program.cs file with the following code:

using System.Collections;

using System.Collections.Generic;

using CLIPSNET;

namespace Example

{

public class GV_UDF : UserFunction

{

public GV_UDF()

{

}

public override PrimitiveValue Evaluate(List\<PrimitiveValue\> arguments)

{

List\<PrimitiveValue\> values = new List\<PrimitiveValue\>();

foreach (DictionaryEntry de in

System.Environment.GetEnvironmentVariables())

{ values.Add(new SymbolValue(de.Key.ToString())); }

return new MultifieldValue(values);

}

}

class Program

{

static void Main(string\[\] args)

{

CLIPSNET.Environment clips = new CLIPSNET.Environment();

clips.AddUserFunction(\"get-variables\",\"m\",0,0,null,new GV_UDF());

clips.CommandLoop();

}

}

}

Next, build and run the program:

CLIPS (6.4.2 1/14/25)

CLIPS\> (get-variables)

(HOMEPATH COMPUTERNAME OneDrive VisualStudioEdition PROCESSOR_REVISION VS100COMNTOOLS DNX_HOME PkgDefApplicationConfigFile PATHEXT SystemDrive TMP TEMP LOCALAPPDATA PUBLIC USERDOMAIN Path PROCESSOR_LEVEL PROCESSOR_IDENTIFIER PROMPT PSModulePath NUMBER_OF_PROCESSORS FPS_BROWSER_USER_PROFILE_STRING CommonProgramFiles ProgramData ProgramFiles FP_NO_HOST_CHECK SystemRoot SESSIONNAME VisualStudioVersion LOGONSERVER USERPROFILE MSBuildLoadMicrosoftTargetsReadOnly VS140COMNTOOLS VSLANG USERDOMAIN_ROAMINGPROFILE APPDATA HOMEDRIVE USERNAME FPS_BROWSER_APP_PROFILE_STRING PROCESSOR_ARCHITECTURE OS ComSpec VisualStudioDir windir ALLUSERSPROFILE)

CLIPS\> (exit)
