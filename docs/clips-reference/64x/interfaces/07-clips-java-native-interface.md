# Section 7: CLIPS Java Native Interface

This section describes the CLIPS Java Native Interface (CLIPSJNI) and the examples demonstrating the integration of CLIPS with a Swing interface. The examples have been tested with the following software environments:

• Windows 11 with JDK 11.0.17 and Visual Studio Community 2022

• MacOS 15.2 with JDK 18.0.1.1 and Xcode 16.2

• Linux: Ubuntu 22.04 LTS with OpenJDK 17.0.13, Debian 11.3 with OpenJDK 17.0.13, Fedora 36 with OpenJDK 17.0.7, CentOS 9 with OpenJDK 17.0.13, and Mint 20.3 with OpenJDK 17.0.13.

## 7.1 CLIPSJNI Directory Structure

In order to use CLIPSJNI, you must obtain the source code by downloading either the *clips_jni_642.zip* or *clips_jni_642.tar.gz* file from the Files page on the CLIPS SourceForge web page (see appendix A for the SourceForge URL). When uncompressed the *CLIPSJNI* directory contains the following structure:

CLIPSJNI

bin

animal

auto

clipsjni

ide

router

sudoku

wine

java-src

net

sf

clipsrules

jni

examples

animal

resources

auto

resources

ide

resources

router

resources

sudoku

resources

wine

resources

library-src

If you are using the CLIPSJNI on Windows or macOS, then the native CLIPS library is already contained in the top-level *CLIPSJNI* directory.

On other systems or 32-bit systems, you must create a native library using the source files contained in the *library-src* directory before you can utilize the CLIPSJNI.

The *CLIPSJNI.jar* file is also contained in the top-level *CLIPSJNI* directory. The source files used to create the jar file are contained in the *java-src* directory.

## 7.2 Issuing Commands from the Terminal

As packaged, invoking and compiling various CLIPSJNI components requires that you enter commands from a terminal application.

On Windows 11, to run the precompiled Java applications, launch the Command Prompt application (enter 'Command Prompt' in the search field of the taskbar and then click on the Command Prompt app). To recompile the native library or use the provided makefiles to rebuild the Java source code, you must have Visual Studio installed. In this case, launch the Command Prompt application by selecting Start \> All apps \> Visual Studio 2022 \> Developer Command Prompt for VS 2022. Using the *Developer Command Prompt for VS 2022* application sets the appropriate paths to use the Visual Studio compiler and make tools. Alternately *x86 Native Tools Command Prompt for VS 2022* or *x64 Native Tools Command Prompt for VS 2022* can be used to compile for a specific processor architecture.

On macOS, click the Spotlight icon in the menu bar, enter 'Terminal' in the search field, and then double click on Terminal.app in the search results to launch the application.

On Ubuntu, click on the "Search your computer" icon, enter 'Terminal' in the search field, and then click on Terminal in the search results to launch the application.

On Fedora and Debian, click on Activities in the menu bar, click the Show Applications icon, enter 'Terminal' in the search field, and then click on Terminal in the search results to launch the application.

On CentOS, click on Applications in the menu bar, click on Activities Overview, click the Show Applications icon, enter 'Terminal' in the search field, and then click on Terminal in the search results to launch the application.

On Mint, click on Menu in the lower toolbar, enter 'Terminal' in the search field, and then click Terminal in the search results to launch the application.

Once the terminal has been launched, set the directory to the CLIPSJNI top-level directory (using the cd command). Unless otherwise noted, all commands should be entered while in the CLIPSJNI directory.

## 7.3 Running CLIPSJNI in Command Line Mode

You can invoke the command line mode of CLIPS through CLIPSJNI to interactively enter commands while running within a Java environment.

On Windows and macOS, enter the following command from the CLIPSJNI directory:

java -jar CLIPSJNI.jar

On Linux, you must first create the CLIPSJNI native library (see section 7.6.3). Once created, enter the following command from the CLIPSJNI directory:

java -Djava.library.path=. -jar CLIPSJNI.jar

The CLIPS banner and command prompt should appear:

CLIPS (6.4.2 1/14/25)

CLIPS\>

## 7.4 Running the Swing Demo Programs

The Swing CLIPSJNI demonstration programs can be run on Windows 11 or macOS using the precompiled native libraries in the CLIPSJNI top-level directory. On Linux and other systems, a CLIPSJNI native library must first be created before the programs can be run.

### 7.4.1 Sudoku Demo

To run the Sudoku demo on Windows 11 or macOS, enter the following command:

java -jar SudokuDemo.jar

To run the Sudoku demo on Linux, enter the following command:

java -Djava.library.path=. -jar SudokuDemo.jar

The Sudoku Demo window should appear (Windows 11 pictured):

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image26.png){width="3.2083333333333335in" height="2.85in"}

### 7.4.2 Wine Demo

To run the Wine demo on Windows 11 or macOS, enter the following command:

java -jar WineDemo.jar

To run the Wine demo on Linux, enter the following command:

java -Djava.library.path=. -jar WineDemo.jar

The Wine Demo window should appear (macOS pictured):

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image27.png){width="5.291666666666667in" height="3.8916666666666666in"}

### 7.4.3 Auto Demo

To run the Auto demo on Windows 11 or macOS, enter the following command:

java -jar AutoDemo.jar

To run the Auto demo on Linux, enter the following command:

java -Djava.library.path=. -jar AutoDemo.jar

The Auto Demo window should appear (Ubuntu pictured):

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image28.png){width="3.925in" height="2.7083333333333335in"}

### 7.4.4 Animal Demo

To run the Animal demo on Windows 11 or macOS, enter the following command:

java -jar AnimalDemo.jar

To run the Animal demo on Linux, enter the following command:

java -Djava.library.path=. -jar AnimalDemo.jar

The Animal Demo window should appear (Windows 11 pictured):

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image29.png){width="3.175in" height="1.925in"}

### 7.4.5 Router Demo

To run the Router demo on Windows 11 or macOS, enter the following command:

java -jar RouterDemo.jar

To run the Router demo on Linux, enter the following command:

java -Djava.library.path=. -jar RouterDemo.jar

The Router Demo window should appear (macOS pictured):

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image30.png){width="6.5in" height="4.813953412073491in"}

## 7.5 Creating the CLIPSJNI JAR File

If you wish to add new functionality to the CLIPSJNI package, it is necessary to recreate the CLIPSJNI jar file. The CLIPSJNI distribution already contains the precompiled CLIPSJNI jar file in the top-level CLIPSJNI directory, so if you are not adding new functionality to the CLIPSJNI package, you do not need to recreate the jar file (unless you want to create a jar file using a different version of Java).

If you are adding new native functions to the CLIPSJNI package, it is also necessary to create the JNI header file that is used to compile the native library. While you are in the CLIPSJNI directory, enter the following command:

javah -d library-src -classpath java-src -jni net.sf.clipsrules.jni.Environment

This command creates a file named net_sf_clipsrules_jni_Environment.h and places it in the CLIPSJNI/library-src directory.

On macOS, enter the following command to compile the CLIPSJNI java source and generate the JAR file:

make -f makefile.mac clipsjni

On Windows 11, enter the following command to compile the CLIPSJNI java source and generate the JAR file:

nmake -f makefile.win clipsjni

On Ubuntu, enter the following command to compile the CLIPSJNI java source and generate the JAR file:

make -f makefile.ubu clipsjni

## 7.6 Creating the CLIPSJNI Native Library

The CLIPSJNI distribution already contains a precompiled universal library for macOS, libCLIPSJNI.jnilib, and for Windows, CLIPSJNI.dll, in the top-level CLIPSJNI directory. It is necessary to create a native library only if you are using the CLIPSJNI with an operating system other than macOS or Windows. You must also create the native library if you want to add new functionality to the CLIPSJNI package by adding additional native functions. The steps for creating a native library varies between operating systems, so some research may be necessary to determine how to create one for your operating system.

### 7.6.1 Creating the Native Library on macOS

Launch the Terminal application (as described in section 7.2). Set the directory to the CLIPSJNI/library-src directory (using the cd command).

To create a universal native library that can run on both Intel and ARM 64 bit architectures, enter the following command:

make -f makefile.mac

Once you have create the native library, copy the libCLIPSJNI.jnilib file from the CLIPSJNI/library-src to the top-level CLIPSJNI directory.

### 7.6.2 Creating the Native Library on Windows 11

Launch the Terminal application (as described in section 7.2). Set the directory to the CLIPSJNI/library-src directory (using the cd command).

To create the native library DLL, enter the following command:

nmake -f makefile.win

Once you have create the native library, copy the CLIPSJNI.dll file from the CLIPSJNI/library-src to the top-level CLIPSJNI directory.

### 7.6.3 Creating the Native Library On Linux

Launch the Terminal application (as described in section 7.2). Set the directory to the CLIPSJNI/library-src directory (using the cd command).

To create a native library, enter the following command (where \<distribution\> is either ubuntu, fedora, debian, mint, or centos):

make -f makefile.lnx \<distribution\>

Once you have create the shared library, copy the libCLIPSJNI.so file from the CLIPSJNI/library-src to the top-level CLIPSJNI directory.

## 7.7 Recompiling the Swing Demo Programs

If you want to make modification to the Swing Demo programs, you can recompile them using the makefiles in the CLIPSJNI directory.

### 7.7.1 Recompiling the Swing Demo Programs on macOS

Use these commands to recompile the examples:

make --f makefile.mac sudoku

make --f makefile.mac wine

make --f makefile.mac auto

make --f makefile.mac animal

make --f makefile.mac router

make --f makefile.mac ide

### 7.7.2 Recompiling the Swing Demo Programs on Windows

Use these commands to recompile the examples:

nmake --f makefile.win sudoku

nmake --f makefile.win wine

nmake --f makefile.win auto

nmake --f makefile.win animal

nmake --f makefile.win router

nmake --f makefile.win ide

### 7.7.3 Recompiling the Swing Demo Programs on Linux

Use these commands to recompile the examples:

make --f makefile.lnx sudoku

make --f makefile.lnx wine

make --f makefile.lnx auto

make --f makefile.lnx animal

make --f makefile.lnx router

make --f makefile.lnx ide

## 7.8 Internationalizing the Swing Demo Programs

The Swing Demo Programs have been designed for internationalization. Several software generated example translations have been provided including Japanese (language code ja), Russian (language code ru), Spanish (language code es), and Arabic (language code ar). The Sudoku and Wine demos make use of translations just for the Swing Interface. The Auto and Animal demos also demonstrate the use of translation text from within CLIPS. To make use of one of the translations, specify the language code when starting the demonstration program. For example, to run the Animal Demo in Japanese on Mac OS X, use the following command:

java -Duser.language=ja -jar AnimalDemo.jar

The welcome screen for the program should appear in Japanese rather than English:

![](/Users/yrashk/Projects/inferaldata/inferal-workspace/repos/clipspyx/main/docs/clips-reference/64x/media/media/image31.png){width="3.716666666666667in" height="2.4833333333333334in"}

It may be necessary to install additional fonts to view some languages. On macOS, you can see which languages are supported by launching 'System Preferences' and clicking the 'Language & Region' icon. On Windows 10, you can see which languages are supported by launching Settings, selecting 'Time and language,' and then selecting 'Region and language.'

To create translations for other languages, first determine the two-character language code for the target language. Make a copy in the resources directory of the ASCII English properties file for the demo program and save it as a UTF-8 encoded file including the language code in the name and using the .source extension. A list of language code is available at http://www.mathguide.de/info/tools/languagecode.html. For example, to create a Greek translation file for the Wine Demo, create the UTF-8 encoded WineResources_el.source file from the ASCII WineResources.properties file. Note that this step requires that you to do more than just duplicate the property file and rename it. You need to use a text editor that allows you to change the encoding from ASCII to UTF-8.

Once you've created the translation source file, edit the values for the properties keys and replaced the English text following each = symbol with the appropriate translation. When you have completed the translation, use the Java native2ascii utility to create an ASCII text file from the source file. For example, to create a Greek translation for the Wine Demo program, you'd use the following command:

native2ascii --encoding UTF-8 WineResources_el.source WineResources_el.properties

Note that the properties file for languages containing non-ASCII characters will contain Unicode escape sequences and is therefore more difficult to read (assuming of course that you can read the language in the original source file). This is the reason that two files are used for creating the translation. The UTF-8 source file is encoded so that you can read and edit the translation and the ASCII properties file is encoded in the format expected for use with Java internationalization features.

The CLIPS translation files stored in the resource directory (such as animal_es.clp) can be duplicated and edited to support new languages. The base name of each new file should end with the appropriate two-letter language code. There is no need to convert these UTF-8 files to another format as CLIPS can read these directly.

## 7.9 CLIPSJNI Classes

This section describes the classes and methods available in the CLIPSJNI.jar file for developing CLIPS applications in Java.

### 7.9.1 The Environment Class

public class Environment

Java programs interacting with CLIPS must create at least one instance of the **Environment** class.

#### 7.9.1.1 Constructors

public Environment()

#### 7.9.1.2 Clearing, Loading, and Creating Constructs

public void clear() throws CLIPSException

public void load(String fileName) throws CLIPSLoadException

public void loadFromString(String loadString) throws CLIPSLoadException

public void loadFromResource(String resourceFile) throws CLIPSLoadException

public void build(String buildString) throws CLIPSException

The **clear** method removes all constructs from an **Environment** instance. The **load**, **loadFromString**, and **loadFromResource** methods load constructs into an **Environment** instance. The **fileName** parameter of the **load** method specifies a file path to a text file containing constructs. The **loadString** parameter of the **loadFromString** method is a string containing constructs. The **resourceFile** parameter of the **loadFromResource** string specifies the resource path to a text file containing constructs. The **build** method loads a single construct into an **Environment** instance.

#### 7.9.1.3 Executing Rules

public void reset() throws CLIPSException

public long run(long runLimit) throws CLIPSException

public long run() throws CLIPSException

The **reset** method removes all fact and instances from an **Environment** instance and creates the facts and instances specified in deffacts and definstances constructs. The **run** method executes the number of rules specified by the **runLimit** parameter or all rules if the **runLimit** parameter is unspecified. The **run** method returns the number of rules executed (which may be less than the **runLimit** parameter value).

#### 7.9.1.4 Creating Facts and Instances

public FactAddressValue assertString(String factStr) throws CLIPSException

public InstanceAddressValue makeInstance(String instanceStr) throws CLIPSException

The **assertString** method asserts a fact using the deftemplate and slot values specified by the **factStr** parameter. The **makeInstance** method creates an instance using the instance name, defclass, and slot values specified by the **instanceStr** parameter.

#### 7.9.1.5 Searching for Facts and Instances

public FactAddressValue findFact(\
String deftemplate) throws CLIPSException

public FactAddressValue findFact(\
String variable,\
String deftemplateName,\
String condition) throws CLIPSException

public List\<FactAddressValue\> findAllFacts(\
String deftemplateName) throws CLIPSException

public List\<FactAddressValue\> findAllFacts(\
String variable,\
String deftemplateName,\
String condition) throws CLIPSException

public InstanceAddressValue findInstance(\
String defclassName) throws CLIPSException

public InstanceAddressValue findInstance(\
String variable,\
String defclassName,\
String condition) throws CLIPSException

public List\<InstanceAddressValue\> findAllInstances(\
String defclassName) throws CLIPSException

public List\<InstanceAddressValue\> findAllInstances(\
String variable,\
String defclassName,\
String condition) throws CLIPSException

The **findFact** methods return the first fact associated with the deftemplate construct specified by the **deftemplateName** parameter. The optional **variable** and **condition** parameters can be jointly specified to restrict the fact returned by specifying a CLIPS expression that must evaluate to a value other FALSE in order for the fact to be returned. Each fact of the specified deftemplate will be tested until a fact satisfying the condition is found. The fact being tested is assigned to the CLIPS variable specified by the **variable** parameter and may be referenced in the **condition** parameter. If no facts of the specified deftemplate exist, or no facts satisfy the condition, the value null is returned.

The **findAllFacts** methods returns the list of facts associated with the deftemplate construct specified by the **deftemplateName** parameter. The optional **variable** and **condition** parameters can be jointly specified to restrict the facts returned by specifying a CLIPS expression that must evaluate to a value other FALSE in order for a fact to be returned. Each fact of the specified deftemplate will be tested to determine whether it will be added to the list. The fact being tested is assigned to the CLIPS variable specified by the **variable** parameter and may be referenced in the **condition** parameter. If no facts of the specified deftemplate exist, or no facts satisfy the condition, a list with no members is returned.

The **findInstance** methods return the first instance associated with the defclass construct specified by the **defclassName** parameter. The optional **variable** and **condition** parameters can be jointly specified to restrict the instance returned by specifying a CLIPS expression that must evaluate to a value other FALSE in order for the instance to be returned. Each instance of the specified defclass will be tested until an instance satisfying the condition is found. The instance being tested is assigned to the CLIPS variable specified by the **variable** parameter and may be referenced in the **condition** parameter. If no instances of the specified defclass exist, or no instances satisfy the condition, the value null is returned.

The **findAllInstances** methods returns the list of instances associated with the defclass construct specified by the **defclassName** parameter. The optional **variable** and **condition** parameters can be jointly specified to restrict the instances returned by specifying a CLIPS expression that must evaluate to a value other FALSE in order for an instance to be returned. Each instance of the specified defclass will be tested to determine whether it will be added to the list. The instance being tested is assigned to the CLIPS variable specified by the **variable** parameter and may be referenced in the **condition** parameter. If no instances of the specified defclass exist, or no instances satisfy the condition, a list with no members is returned.

#### 7.9.1.5 Executing Functions and Commands

public PrimitiveValue eval(String evalStr) throws CLIPSException

The **eval** method evaluates the command or function call specified by the **evalStr** parameter and returns the result of the evaluation.

#### 7.9.1.6 Debugging

public void watch(String watchItem)

public void unwatch(String watchItem)

public boolean getWatchItem(String watchItem)

public void setWatchItem(String watchItem,boolean newValue)

The **watchItem** parameter should be one of the following static String values defined in the Environment class: FACTS, RULES, DEFFUNCTIONS, COMPILATIONS, INSTANCES, SLOTS, ACTIVATIONS, STATISTICS, FOCUS, GENERIC_FUNCTIONS, METHODS, GLOBALS, MESSAGES, MESSAGE_HANDLERS, NONE, or ALL.

The **watch** method enables the specified watch item and the **unwatch** method disables the specified watch item. The **getWatchItem** method returns the current state of the specified watch item. The **setWatchItem** method enables the specified watch item if the **newValue** parameter is true and disables it if the **newValue** parameter is false.

#### 7.9.1.7 Adding and Removing User Functions

public void addUserFunction(\
String functionName,\
UserFunction callback)

public void addUserFunction(\
String functionName,\
String returnTypes,\
int minArgs,\
int maxArgs,\
String argTypes,\
UserFunction callback)

public void removeUserFunction(\
String functionName)

The **addUserFunction** method associates a CLIPS function name (specified by the **functionName** parameter) with an instance of a Java class implementing the **UserFunction** interface (specified by the **callback** parameter). This allows you to call Java code from within CLIPS code. The optional parameters **returnTypes**, **minArg**, **maxArgs**, and **argTypes** can be used to specify the CLIPS primitive types returned by the function, the minimum and maximum number of arguments the function is expecting, and the primitive types allowed for each argument. The UNBOUNDED constant from the **UserFunction** interface can be used for the **maxArgs** parameter to indicate that there is no upper limit on the number of arguments.

If the **returnTypes** parameter value is null, then CLIPS assumes that the UDF can return any valid type. Specifying one or more type character codes, however, allows CLIPS to detect errors when the return value of a UDF is used as a parameter value to a function that specifies the types allowed for that parameter. The following codes are supported for return values and argument types:

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

The **addUserFunction** method throws an **IllegalArgumentException** if the association fails because one already exists for the **functionName** parameter.

The **removeUserFunction** method removes the association between a CLIPS function name and the user function code associated the function name. You can use this to remove a previously created associated (either to remove it altogether or to replace the old associated with a new one). The **removeUserFunction** method throws an **IllegalArgumentException** if no association currently exists for the **functionName** parameter.

#### 7.9.1.8 Managing Routers

public void addRouter(\
Router theRouter)

public void deleteRouter(\
Router theRouter)

public void activateRouter(\
Router theRouter)

public void deactivateRouter(\
Router theRouter)

public void print (\
String logicalName,\
String printString)

public void print(\
String printString)

public void println (\
String logicalName,\
String printString)

public void println(\
String printString)

The **addRouter** method adds an instance of a Java class implementing the **Router** interface to the list of routers checked by CLIPS for processing I/O requests. The **deleteRouter** method removes a Router instance from the list of CLIPS routers. The methods **deactivateRouter** and **activateRouter** allow a router to be disabled/enabled without removing it from the list of routers.

The **print** and **println** methods output the string specified by the printString parameter through the router system. These methods direct the output to the logical name specified by the **logicalName** parameter. If the **logicalName** parameter is unspecified, output is directed to standard output. In addition, the **println** method appends a carriage return to the output.

#### 7.9.1.9 Command Loop

public void commandLoop()

The **commandLoop** method starts the CLIPS Read-Eval-Print Loop (REPL) using the Java standard input and output streams.

### 7.9.2 The PrimitiveValue Class and Subclasses

public abstract class PrimitiveValue

public class VoidValue extends PrimitiveValue

public abstract class NumberValue extends PrimitiveValue

public class FloatValue extends NumberValue

public class IntegerValue extends NumberValue

public abstract class LexemeValue extends PrimitiveValue

public class SymbolValue extends LexemeValue

public class StringValue extends LexemeValue

public class InstanceNameValue extends LexemeValue

public class MultifieldValue extends PrimitiveValue\
implements Iterable\<PrimitiveValue\>

public class FactAddressValue extends PrimitiveValue

public class InstanceAddressValue extends PrimitiveValue

The **PrimitiveValue** class and its subclasses constitute the Java representation of the CLIPS primitive data types. Several methods (such as **eval** and **getSlotValue**) return objects belonging to concrete subclasses of the **PrimitiveValue** class.

Several methods are provided for determining the type of a PrimitiveValue object:

public CLIPSType getCLIPSType()

public boolean isVoid()

public boolean isLexeme()

public boolean isSymbol()

public boolean isString()

public boolean isInstanceName()

public boolean isNumber()

public boolean isFloat()

public boolean isInteger()

public boolean isFactAddress()

public boolean isInstance()

public boolean isInstanceAddress()

public boolean isMultifield()

public boolean isExternalAddress()

The **getCLIPSType** method returns one of the following **CLIPSType** enumerations: FLOAT, INTEGER, SYMBOL, STRING, MULTIFIELD, EXTERNAL_ADDRESS, FACT_ADDRESS, INSTANCE_ADDRESS, INSTANCE_NAME, or VOID.

Several methods are provided for creating objects belonging to the **FloatValue**, **IntegerValue**, **SymbolValue**, **StringValue**, **InstanceNameValue**, **MultifieldValue**, and **VoidValue** classes:

public FloatValue()

public FloatValue(double value)

public FloatValue(Double value)

public IntegerValue()

public IntegerValue(long value)

public IntegerValue(Long value)

public SymbolValue()

public SymbolValue(String value)

public StringValue()

public StringValue(String value)

public InstanceNameValue()

public InstanceNameValue(String value)

public MultifieldValue()

public MultifieldValue(List\<PrimitiveValue\> value)

public VoidValue()

The **assertString** and **makeInstance** methods of the **Environment** class can be used to create objects of the **FactAddressValue** and **InstanceAddressValue** classes respectively.

The following **NumberValue** methods are available for retrieving the underlying Java value from **IntegerValue** and **FloatValue** objects:

public Number numberValue()

public int intValue()

public long longValue()

public float floatValue()

public double doubleValue()

The following **LexemeValue** method is provided to retrieve the underlying Java value from **SymbolValue**, **StringValue**, and **InstanceNameValue** objects:

public String lexemeValue()

The **InstanceNameValue** class also provides a method for converting an instance name to the corresponding instance address in a specified environment:

public InstanceAddressValue getInstance(Environment theEnv)

The following **MultifieldValue** methods provide access to the list of **PrimitiveValue** objects contained in a **MultifieldValue** method:

public List\<PrimitiveValue\> multifieldValue()

public int size()

public PrimitiveValue get(int index)

The following **FactAddressValue** methods provide access to the slot values and fact index of the associated CLIPS fact:

public PrimitiveValue getSlotValue(String slotName)

public long getFactIndex ()

The following **InstanceAddressValue** methods provide access to the slot values and instance name of the associated CLIPS instance:

public PrimitiveValue getSlotValue(String slotName)

public String getInstanceName()

The following **ExternalAddressValue** method provides access to the value of the associated CLIPS external address (a C pointer converted to a Java long integer):

public long getExternalAddress()

The **FactAddressValue**, **InstanceAddressValue**, and **ExternalAddressValue** classes provide the following reference count methods:

public void retain()

public void release()

Since objects of these classes retain pointers to C data structures, retaining the object prevents the C code from releasing these data structures while there are still outstanding references to them. Each call to the **retain** method increments the number of reference counts to the object and each call to the **release** method decrements the number of reference counts to the object.

### 7.9.3 The CLIPSException and CLIPSLoadException Classes

public class CLIPSException extends Exception

public class CLIPSLoadException extends CLIPSException

CLIPSJNI provides two subclasses of the **Exception** class for methods generating errors: CLIPS **Exception** and **CLIPSLoadException**.

#### 7.9.3.1 CLIPSLoadException Methods

public List\<CLIPSLineError\> getErrorList()

public class CLIPSLineError

Loading constructs can generate multiple errors, so the **getErrorList** method of the **CLIPSLoadException** class returns the list of **CLIPSLineError** objects detailing each error.

##### 7.9.3.1.1 CLIPSLineError Methods

public String getFileName()

public long getLineNumber()

public String getMessage()

The **getFileName,** **getLineNumber**, and **getMessage** respectively return the file name, line number, and error message associated with a **CLIPSLineError** object.

### 7.9.4 The Router Interface

public interface Router

The **Router** interface allows Java objects implementing the interface to interact with the CLIPS I/O router system.

#### 7.9.4.1 Required Methods

public int getPriority()

public String getName()

public boolean query(String logicalName)

public void write(String logicalName,String writeString)

public int read(String logicalName)

public int unread(String logicalName,int theChar)

public void exit(boolean failure)

The **getPriority** method returns the integer priority of the router. Routers with higher priorities are queried before routers of lower priority to determine if they can process an I/O request. The **getName** method returns the identifier associated with the router. The **query** method is called to determine if the router handles I/O requests for the **logicalName** parameter. It should return true if the router can process the request, otherwise it should return false. The **write** method is called to output the value specified by the **writeString** parameter to the **logicalName** parameter. The **read** method returns an input character for the **logicalName** parameter. It should return -1 if no characters are available in the input queue. The **unread** method places the character specified by parameter **theChar** back on the input queue so that it is available for the next **read** request. It returns the value of parameter **theChar** if successful, otherwise it returns -1. The **exit** method is invoked when the CLIPS **exit** command is issued or an unrecoverable error occurs. The **failure** parameter will either be false for an exit command or true for an unrecoverable error.

#### 7.9.4.2 Predefined Router Names

public static final String STDIN

public static final String STDOUT

public static final String STDWRN

public static final String STDERR

The String constants STDIN, STDOUT, STDWRN, and STDERR are the standard predefined logical names used by CLIPS.

#### 7.9.4.3 The BaseRouter Class

public class BaseRouter implements Router

The **BaseRouter** class is an implementation of the **Router** interface. Its **write**, **read**, **unread**, and **exit** methods are minimal implementations; the **write** and **exit** methods execute no statements and the **read** and **unread** methods always return -1. Subclasses can override these methods as needed to create functional routers.

##### 7.9.4.3.1 Constructors

public BaseRouter (\
Environment env,\
String \[\] queryNames)

public BaseRouter(\
Environment env,\
String \[\] queryNames,\
int priority)

public BaseRouter(\
Environment env,\
String \[\] queryNames,\
int priority,\
String routerName)

The **BaseRouter** constructor requires the **env** and **queryName** parameters. Optionally, the **priority** parameter or the **priority** and **routerName** parameters can be supplied. The **env** parameter is the **Environment** object associated with the **Router** object. The **queryNames** parameter is an Array of strings used by the **query** method of the **BaseRouter** object to determine whether the router handles I/O for a specific logical name. The **priority** parameter is the priority of the router; if it is unspecified, it defaults to 0. The **routerName** parameter is the name that serves as an identifier for the **BaseRouter** object; if it is unspecified an identifier will be generated for the router.

### 7.9.5 The UserFunction Interface

public interface UserFunction

The **UserFunction** interface provides a method for invoking a Java method from CLIPS code.

#### 7.9.5.1 Required Methods

public PrimitiveValue evaluate (List\<PrimitiveValue\> arguments)

Once a linkage has been made between a CLIPS function name and an object implementing the **UserFunction** interface, the **evaluate** method is invoked when the linked CLIPS function call is executed. The **function** arguments are evaluated and passed to the evaluate method via the **arguments** parameter.

#### 7.9.5.2 Constants

public static final int UNBOUNDED

The UNBOUNDED constant can be used for the **maxArgs** parameter of the **AddUserFunction** method of the **Environment** class to indicate that there is no upper limit on the number of arguments.

### 7.9.6 Examples

The following examples assume the example code is placed in the top-level CLIPSJNI directory. Additionally the native libraries must be built and present in the directory (either libCLIPSJNI.jnilib for macOS, CLPSJNI.dll for Windows, or libCLIPSJNI.so for Linux). The CLIPSJNI Java source files should also be compiled using the appropriate command for Windows, macOS, or Linux:

make -f makefile.win clipsjni

make -f makefile.mac clipsjni

make -f makefile.lnx clipsjni

#### 7.9.6.1 Loading Constructs from a JAR file

This example demonstrates how to load a CLIPS source file that has been stored inside a JAR file.

First, create the source file hello.clp within the CLIPSJNI directory with the following content:

(defrule hello

=\>

(println \"Hello World\"))

Next create the Java source file Example.java with the following content:

import net.sf.clipsrules.jni.\*;

public class Example

{

public static void main(String args\[\])

{

Environment clips;

clips = new Environment();

try

{

clips.loadFromResource(\"/hello.clp\");

clips.reset();

clips.run();

}

catch (Exception e)

{ e.printStackTrace(); }

}

}

Next, compile the Java source and create a jar file to contain the Example class, the CLIPSJNI classes, and the CLIPS construct file:

\$ javac -cp CLIPSJNI.jar Example.java

\$ jar -cfe Example.jar Example Example.class

\$ jar -uf Example.jar -C bin/clipsjni net

\$ jar -uf Example.jar hello.clp

\$

Finally, run the program:

\$ java -jar Example.jar

Hello World

\$

#### 7.9.6.2 Fact Query

This example demonstrates how to query CLIPS to retrieve facts.

First create the Java source file Example.java with the following content:

import net.sf.clipsrules.jni.\*;

import java.util.List;

public class Example

{

public static void main(String args\[\])

{

Environment clips;

clips = new Environment();

try

{

clips.build(\"(deftemplate person (slot name) (slot age))\");

clips.assertString(\"(person (name \\\"Fred Jones\\\") (age 17))\");

clips.assertString(\"(person (name \\\"Sally Smith\\\") (age 23))\");

clips.assertString(\"(person (name \\\"Wally North\\\") (age 35))\");

clips.assertString(\"(person (name \\\"Jenny Wallis\\\") (age 11))\");

System.out.println(\"All people:\");

List\<FactAddressValue\> people = clips.findAllFacts(\"person\");

for (FactAddressValue p : people)

{ System.out.println(\" \" + p.getSlotValue(\"name\")); }

System.out.println(\"Adults:\");

people = clips.findAllFacts(\"?f\",\"person\",\"(\>= ?f:age 18)\");

for (FactAddressValue p : people)

{ System.out.println(\" \" + p.getSlotValue(\"name\")); }

}

catch (Exception e)

{ e.printStackTrace(); }

}

}

Next, compile the Java source and create a jar file to contain the Example and CLIPSJNI classes:

\$ javac -cp CLIPSJNI.jar Example.java

\$ jar -cfe Example.jar Example Example.class

\$ jar -uf Example.jar -C bin/clipsjni net

\$

Finally, run the program:

\$ java -jar Example.jar

All people:

\"Fred Jones\"

\"Sally Smith\"

\"Wally North\"

\"Jenny Wallis\"

Adults:

\"Sally Smith\"

\"Wally North\"

\$

#### 7.9.6.3 Big Integer Multiplication User Function

This example demonstrates how to add a user function to multiply two numbers together using big integer math. It also demonstrates using the eval method to evaluate a CLIPS function call.

First create the Java source file Example.java with the following content:

import net.sf.clipsrules.jni.\*;

import java.util.List;

import java.math.BigInteger;

public class Example

{

public static void main(String args\[\])

{

Environment clips;

clips = new Environment();

clips.addUserFunction(\"bi\*\",\"s\",2,Router.UNBOUNDED,\"s\",

new UserFunction()

{

public PrimitiveValue evaluate(List\<PrimitiveValue\> arguments)

{

LexemeValue lv = (LexemeValue) arguments.get(0);

BigInteger rv = new BigInteger(lv.lexemeValue());

for (int i = 1; i \< arguments.size(); i++)

{

lv = (LexemeValue) arguments.get(i);

rv = rv.multiply(new BigInteger(lv.lexemeValue()));

}

return new StringValue(rv.toString());

}

});

try

{

System.out.println(\"(\* 9 8) = \" +

clips.eval(\"(\* 9 8)\"));

System.out.println(\"(bi\* \\\"9\\\" \\\"8\\\") = \" +

clips.eval(\"(bi\* \\\"9\\\" \\\"8\\\")\"));

System.out.println(\"(\* 4294967296 4294967296) = \" +

clips.eval(\"(\* 4294967296 4294967296)\"));

System.out.println(\"(bi\* \\\"4294967296\\\" \\\"4294967296\\\") = \" +

clips.eval(\"(bi\* \\\"4294967296\\\" \\\"4294967296\\\")\"));

}

catch (Exception e)

{ e.printStackTrace(); }

}

}

Next, compile the Java source and create a jar file to contain the Example and CLIPSJNI classes:

\$ javac -cp CLIPSJNI.jar Example.java

\$ jar -cfe Example.jar Example Example\*.class

\$ jar -uf Example.jar -C bin/clipsjni net

\$

Finally, run the program:

\$ java -jar Example.jar

(\* 9 8) = 72

(bi\* \"9\" \"8\") = \"72\"

(\* 4294967296 4294967296) = 0

(bi\* \"4294967296\" \"4294967296\") = \"18446744073709551616\"

\$

#### 7.9.6.4 Get Properties User Function

This example demonstrates how to add a user function that returns a multifield value containing the list of system properties.

First create the Java source file Example.java with the following content:

import net.sf.clipsrules.jni.\*;

import java.util.ArrayList;

import java.util.List;

import java.util.Properties;

public class Example

{

public static void main(String args\[\])

{

Environment clips;

clips = new Environment();

clips.addUserFunction(\"get-properties\",\"m\",0,0,null,

new UserFunction()

{

public PrimitiveValue evaluate(List\<PrimitiveValue\> arguments)

{

List\<PrimitiveValue\> values = new ArrayList\<PrimitiveValue\>();

Properties props = System.getProperties();

for (String key : props.stringPropertyNames())

{ values.add(new SymbolValue(key)); }

return new MultifieldValue(values);

}

});

clips.commandLoop();

}

}

Next, compile the Java source and create a jar file to contain the Example and CLIPSJNI classes:

\$ javac -cp CLIPSJNI.jar Example.java

\$ jar -cfe Example.jar Example Example\*.class

\$ jar -uf Example.jar -C bin/clipsjni net

\$

Finally, run the program:

\$ java -jar Example.jar

CLIPS (6.4.2 1/14/25)

CLIPS\> (get-properties)

(java.runtime.name sun.boot.library.path java.vm.version gopherProxySet java.vm.vendor java.vendor.url path.separator java.vm.name file.encoding.pkg user.country sun.java.launcher sun.os.patch.level java.vm.specification.name user.dir java.runtime.version java.awt.graphicsenv java.endorsed.dirs os.arch java.io.tmpdir line.separator java.vm.specification.vendor os.name sun.jnu.encoding java.library.path java.specification.name java.class.version sun.management.compiler os.version http.nonProxyHosts user.home user.timezone java.awt.printerjob file.encoding java.specification.version user.name java.class.path java.vm.specification.version sun.arch.data.model java.home sun.java.command java.specification.vendor user.language awt.toolkit java.vm.info java.version java.ext.dirs sun.boot.class.path java.vendor file.separator java.vendor.url.bug sun.cpu.endian sun.io.unicode.encoding socksNonProxyHosts ftp.nonProxyHosts sun.cpu.isalist)

CLIPS\> (exit)

\$
