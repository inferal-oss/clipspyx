# Section 9: I/O Routers

The **I/O router** system provided in CLIPS is quite flexible and will allow a wide va­riety of interfaces to be developed and easily attached to CLIPS. The system is rela­tively easy to use and is explained fully in sections 9.1 through 9.4. The CLIPS I/O functions for using the router system are described in sections 9.5 and 9.6, and finally, in section 9.7, some examples are included which show how I/O routing could be used for simple interfaces.

## 9.1 Introduction

The problem that originally inspired the idea of I/O routing will be considered as an introduction to I/O routing. Because CLIPS was designed with portability as a major goal, it was not possible to build a sophisticated user interface that would support many of the features found in the interfaces of commercial expert system building tools. A prototype was built of a semi‑portable interface for CLIPS using the CURSES screen manage­ment package. Many problems were encountered during this effort in­volving both portability concerns and CLIPS internal features. For example, every statement in the source code which used the C print function, **printf**, for printing to the terminal had to be replaced by the CURSES function, **wprintw**, which would print to a window on the terminal. In addition to changing function call names, different types of I/O had to be di­rected to different windows. The tracing information was to be sent to one window, the command prompt was to appear in another window, and output from printout statements was to be sent to yet another window.

This prototype effort pointed out two major needs: First, the need for generic I/O func­tions that would remain the same regardless of whether I/O was directed to a standard terminal interface or to a more complex interface (such as windows); and second, the need to be able to specify different sources and destinations for I/O. I/O routing was designed in CLIPS to handle these needs. The concept of I/O routing will be further explained in the following sections.

## 9.2 Logical Names

One of the key concepts of I/O routing is the use of **logical names**. An analogy will be useful in explaining this concept. Consider the Acme company which has two com­puters: computers X and Y. The Acme company stores three data sets on these two computers: a personnel data set, an accounting data set, and a documenta­tion data set. One of the employees, Joe, wishes to update the payroll in­formation in the accounting data set. If the payroll information was located in directory A on computer Y, Joe\'s command would be

update Y:\[A\]payroll

If the data were moved to directory B on computer X, Joe's command would have to be changed to

update X:\[B\]payroll

To update the payroll file, Joe must know its location. If the file is moved, Joe must be informed of its new location to be able to update it. From Joe's point of view, he does not care where the file is located physically. He simply wants to be able to specify that he wants the information from the accounting data set. He would rather use a com­mand like

update accounting:payroll

By using logical names, the information about where the ac­counting files are located physically can be hidden from Joe while still allowing him to access them. The loca­tions of the files are equated with logical names as shown here.

accounting = X:\[A\]

documentation = X:\[C\]

personnel = Y:\[B\]

Now, if the files are moved, Joe does not have to be informed of their relocation so long as the logical names are updated. This is the power of using logical names. Joe does not have to be aware of the physical location of the files to access them; he only needs to be aware that accounting is the logical name for the location of the account­ing data files. Logical names allow reference to an object without having to un­derstand the details of the implementation of the reference.

In CLIPS, logical names are used to send I/O requests without having to know which device and/or function is handling the request. Consider the message that is printed in CLIPS when rule tracing is turned on and a rule has just fired. A typical message would be

FIRE 1 example‑rule: f‑1

The routine that requests this message be printed should not have to know where the message is being sent. Different routines are required to print this message to a stan­dard terminal, a window interface, or a printer. The tracing routine should be able to send this message to a logical name (for example, **trace-out**) and should not have to know if the device to which the message is being sent is a terminal or a printer. The logical name **trace-out** allows tracing information to be sent simply to "the place where tracing information is displayed." In short, logical names allow I/O requests to be sent to specific locations without having to specify the details of how the I/O request is to be handled.

Many functions in CLIPS make use of logical names. Both the **printout** and **format** functions require a logical name as their first argument. The **read** func­tion can take a logical name as an optional argument. The **open** function causes the association of a logical name with a file, and the **close** function removes this as­sociation.

Several logical names are predefined by CLIPS and are used extensively throughout the system code. These are

**Name Description**

**stdin** The default for all user inputs. The **read** and **readline** functions read from **stdin** if **t** is specified as the logical name.

**stdout** The default for all user outputs. The **format** and **printout** functions send output to **stdout** if **t** is specified as the logical name.

**stderr** All error messages are sent to this logical name.

**stdwrn** All warning messages are sent to this logical name.

Within CLIPS code, these predefined logical names should be specified in lower case (and typically the only one you'll use is **t** and depending upon which function you're using this will be mapped to either **stdin** or **stdout**). Within C code, these logical names can be specified using constants that have been defined in upper case: STDIN, STDOUT, STDERR, and STDWRN.

## 9.3 Routers

The use of logical names solves two problems. Logical names make it easy to create generic I/O functions, and they allow the specification of different sources and destinations for I/O. The use of logical names allows CLIPS to ignore the specifics of an I/O request. However, such requests must still be specified at some level. I/O routers are provided to handle the specific details of a request.

A router consists of three components. The first component is a function which can determine whether the router can handle an I/O request for a given logical name. The router which recognizes I/O requests that are to be sent to the serial port may not recognize the same logical names as that which recognizes I/O re­quests that are to be sent to the terminal. On the other hand, two routers may recog­nize the same logical names. A router that keeps a log of a CLIPS session (a drib­ble file) may recog­nize the same logical names as that which handles I/O re­quests for the terminal.

The second component of a router is its priority. When CLIPS receives an I/O request, it begins to query each router to discover whether it can handle an I/O re­quest. Routers with high priorities are queried before routers with low priorities. Priorities are very important when dealing with one or more routers that can each process the same I/O request. This is particularly true when a router is going to redefine the stan­dard user interface. The router associated with the standard interface will handle the same I/O requests as the new router; but, if the new router is given a higher priority, the standard router will never receive any I/O requests. The new router will "intercept" all of the I/O requests. Priorities will be discussed in more detail in the next section.

The third component of a router consists of the functions which actually handle an I/O request. These include functions for printing strings, getting a character from an input buffer, returning a character to an input buffer, and a function to clean up (e.g., close files, remove windows) when CLIPS is exited.

## 9.4 Router Priorities

Each I/O router has a priority. Priority determines which routers are queried first when determining the router that will handle an I/O request. Routers with high priorities are queried before routers with low priorities. Priorities are assigned as integer values (the higher the integer, the higher the priority). Priorities are important because more than one router can handle an I/O request for a single logical name, and they enable the user to define a custom interface for CLIPS. For example, the user could build a custom router which han­dles all logical names normally handled by the default router associated with the standard interface. The user adds the custom router with a priority higher than the priority of the router for the standard interface. The custom router will then intercept all I/O requests intended for the standard interface and spe­cially process those re­quests to the custom interface.

Once the router system sends an I/O request out to a router, it considers the request satisfied. If a router is going to share an I/O request (i.e., process it) then allow other routers to process the request also, that router must deactivate itself and call **WriteString** again. These types of routers should use a priority of either 30 or 40. An example is given in appendix 9.7.2.

**Priority Router Description**

50 Any router that uses "unique" logical names and does not want to share I/O with catch-all routers.

40 Any router that wants to grab standard I/O and is willing to share it with other routers. A dribble file is a good example of this type of router. The dribble file router needs to grab all output that normally would go to the terminal so it can be placed in the dribble file, but this same output also needs to be sent to the router which displays output on the terminal.

30 Any router that uses "unique" logical names and is willing to share I/O with catch‑all routers.

20 Any router that wants to grab standard logical names and is not willing to share them with other routers.

10 This priority is used by a router which redefines the default user inter­face I/O router. Only one router should use this priority.

0 This priority is used by the default router for handling stan­dard and file logical names. Other routers should not use this priority.

## 9.5 Internal I/O Functions

The following functions are called internally by CLIPS. These functions search the list of active routers and determine which router should handle an I/O request. Some routers may wish to deactivate themselves and call one of these functions to allow the next router to process an I/O request. Prototypes for these functions can be included by using the **clips.h** header file or the **router.h** header file.

### 9.5.1 ExitRouter

void ExitRouter(\
Environment \*env,\
int code);

The function **ExitRouter** calls the exit function callback associated with each active router before exiting CLIPS. Parameter **env** is a pointer to a previously created environment; and parameter **code** is an integer passed to the callback as well as the system **exit** function once all callbacks have been executed. User code that detects an unrecoverable error should call this function rather than calling the system **exit** function so that routers have the opportunity to execute cleanup code.

### 9.5.2 Input

int ReadRouter(\
Environment \*env,\
const char \*logicalName);

int UnreadRouter(\
Environment \*env,\
const char \*logicalName,\
int ch);

The function **ReadRouter** queries all active routers to retrieve character input. This function should be used in place of **getc** to ensure that character input from the function can be received from a custom interface. Parameter **env** is a pointer to a previously created environment; and parameter **logicalName** is the query string that must be recognized by the router to be invoked to handle the I/O request. The get character function callback for that router is invoked and the return value of that callback is returned by this function.

The function **UnreadRouter** queries all active routers to push character input back into an input source. This function should be used in place of **ungetc** to ensure that character input works properly using a custom interface. Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the query string that must be recognized by the router to be invoked to handle the I/O request; and parameter **ch** is the character to be pushed back to the input source. The unget character function callback for that router is invoked. The return value for this function is the parameter value **ch** if the character is successfully pushed back to the input source; otherwise, -1 is returned.

### 9.5.3 Output

void Write(\
Environment \*env,\
const char \*str);

void WriteCLIPSValue(\
Environment \*env,\
const char \*logicalName,\
CLIPSValue \*cv);

void WriteFloat(\
Environment \*env,\
const char \*logicalName,\
double d);

void WriteInteger(\
Environment \*env,\
const char \*logicalName,\
long long l);

void Writeln(\
Environment \*env,\
const char \*str);

void WriteString(\
Environment \*env,\
const char \*logicalName,\
const char \*str);

void WriteMultifield(\
Environment \*env,\
const char \*logicalName,\
Multifield \*mf);

void WriteUDFValue(\
Environment \*env,\
const char \*logicalName,\
UDFValue \*udfv);

The functions **Write**, **WriteCLIPSValue**, **WriteFloat**, **WriteInteger**, **Writeln**, **WriteString**, **WriteMultifield**, and **WriteUDFValue** direct output to a router for display. Using these functions in place of **printf** ensures that output will be displayed appropriately whether CLIPS is run as part of a console application, integrated development environment, or custom interface. By default, output from these functions will use **printf** for display if no other routers are detected to handle the output request.

For all of these functions, parameter **env** is a pointer to a previously created environment. For all function except **Write** and **Writeln**, the parameter **logicalName** is the query string that must be recognized by a router to indicate it can handle the output request. All active routers are queried in order of their priority until the query function callback for a router returns true to indicate if handles the specified logical name. The **Write** and **Writeln** functions automatically sent output to the STDOUT logical name.

The remaining parameter for all of these functions is the value to be printed. The parameters **d**, **l**, and **str** are the C types double, long long, and a char pointer to a null-terminated string. Parameter **mf** is a pointer to a **Multifield**. Parameters **cv** and **udfv** are pointers to **CLIPSValue** and **UDFValue** types that have been allocated and populated with data by the caller. The **Writeln** function additionally prints a carriage return after printing the **str** parameter.

## 9.6 Router Handling Functions

The following functions are used for creating, deleting, and handling I/O routers. They are intended for use within user‑defined functions. Prototypes for these functions can be included by using the **clips.h** header file or the **router.h** header file.

### 9.6.1 Creating Routers

bool AddRouter(\
Environment \*env,\
const char \*name,\
int priority,\
RouterQueryFunction \*queryCallback,\
RouterWriteFunction \*writeCallback,\
RouterReadFunction \*readCallback,\
RouterUnreadFunction \*unreadCallback,\
RouterExitFunction \*exitCallback,\
void \*context);

typedef bool RouterQueryFunction(\
Environment \*env,\
const char \*logicalName,\
void \*context);

typedef void RouterWriteFunction(\
Environment \*env,\
const char \*logicalName,\
const char \*str,\
void \*context);

typedef void RouterExitFunction(\
Environment \*environment,\
int code,\
void \*context);

typedef int RouterReadFunction(\
Environment \*env,\
const char \*logicalName,\
void \*context);

typedef int RouterUnreadFunction(\
Environment \*env,\
const char \*logicalName,\
int ch,\
void \*context);

The function **AddRouter** creates and activates a new router. Parameter **env** is a pointer to a previously created environment; parameter **name** is a string that uniquely identifies the router for removal using **DeleteRouter**; parameters **queryCallback**, **writeCallback**, **readCallback**, **unreadCallback**, and **exitCallback** are pointers to callback functions; parameter **priority** is the priority of the router used to determine the order in which routers are queried (higher priority routers are queried first); and parameter **context** is a user supplied pointer to data that is passed to the router callback functions when they are invoked (a null pointer should be used if there is no data that needs to be passed to the router callback functions). The **queryCallback** parameter value must be a non-null function pointer, otherwise the other router callback functions will never be invoked. If the router does not handle output requests, the **writeCallback** parameter value should be a null pointer. If the router does not handle input requests, the **readCallback** and **unreadCallback** parameter values should be null pointers. This function returns true if the router was successfully added; otherwise, it returns false.

The **RouterQueryFunction** type has three parameters: **env** is a pointer to a previously created environment; **logicalName** is the logical name associated with the I/O request; and **context** is the user supplied data pointer provided when the router was created. This function should return true if the **logicalName** parameter value is recognized by this router; otherwise, it should return false.

The **RouterWriteFunction** type has four parameters: **env** is a pointer to a previously created environment; **logicalName** is the logical name associated with the I/O request; **str** is the null character terminated string to be printed; and **context** is the user supplied data pointer provided when the router was created.

The **RouterExitFunction** type has three parameters: **env** is a pointer to a previously created environment; **code** is the exit code value (either the value passed to the CLIPS **exit** command or the C **ExitRouter** function); and **context** is the user supplied data pointer provided when the router was created.

The **RouterReadFunction** type has three parameters: **env** is a pointer to a previously created environment; **logicalName** is the logical name associated with the I/O request; and **context** is the user supplied data pointer provided when the router was created. The return value of this function is an integer character code or -1 to indicate EOF (end of file).

The **RouterUnreadFunction** type has four parameters: **env** is a pointer to a previously created environment; **logicalName** is the logical name associated with the I/O request; **ch** is the character code to be pushed back into the router input source; and **context** is the user supplied data pointer provided when the router was created. The return value of this function should be the **ch** parameter value if the function successfully pushes the character code; otherwise, it should return -1 (EOF).

### 9.6.2 Deleting Routers

bool DeleteRouter(\
Environment \*env,\
const char \*name);

The function **DeleteRouter** removes previously created router. Parameter **env** is a pointer to a previously created environment; and parameter **name** is the string used to identify the router when it was added using **AddRouter**. The function returns true if the router was successfully deleted; otherwise, it returns false.

### 9.6.3 Activating and Deactivating Routers

bool ActivateRouter(\
Environment \*env,\
const char \*name);

bool DeactivateRouter(\
Environment \*env,\
const char \*name);

The function **ActivateRouter** activates the I/O router specified by parameter **name** (the string used to identify the router when it was created using **AddRouter**). The activated router will be queried to see if it can handle an I/O re­quest. Newly created routers do not have to be activated. This function returns true if the router exists and was successfully activated; otherwise, false is returned.

The function **DeactivateRouter** deactivates the I/O router specified by parameter **name** (the string used to identify the router when it was created using **AddRouter**). The deactivated router will not be queried to see if it can handle an I/O re­quest. This function returns true if the router exists and was successfully deactivated; otherwise, false is returned.

## 9.7 Examples

The following examples demonstrate the use of the I/O router system. These exam­ples show the necessary C code for implementing the basic capabilities described.

### 9.7.1 Dribble System

Write the necessary functions that will divert all error information to the file named \"error.txt\".

/\*

First of all, we need to create an environment data structure for storing a file pointer to the dribble file which will contain the error information. The data position is offset to prevent conflict with other examples in this document. We also need to declare prototypes for the functions used in this example.

\*/

#include \<stdio.h\>

#include \<stdlib.h\>

#include \"clips.h\"

#define DRIBBLE_DATA USER_ENVIRONMENT_DATA + 1

struct dribbleData

{

FILE \*traceFP;

};

#define DribbleData(theEnv) \\

((struct dribbleData \*) GetEnvironmentData(theEnv,DRIBBLE_DATA))

bool QueryTraceCallback(Environment \*,const char \*,void \*);

void WriteTraceCallback(Environment \*,const char \*,const char \*,void \*);

void ExitTraceCallback(Environment \*environment,int,void \*);

void TraceOn(Environment \*,UDFContext \*,UDFValue \*);

void TraceOff(Environment \*,UDFContext \*,UDFValue \*);

/\*

We want to recognize any output that is sent to the logical name STDERR because all tracing information is sent to this logical name. The query function for our router is defined below.

\*/

bool QueryTraceCallback(

Environment \*environment,

const char \*logicalName,

void \*context)

{

if (strcmp(logicalName,STDERR) == 0) return(true);

return(false);

}

/\*

We now need to define a function which will print the tracing in¬formation to our trace file. The print function for our router is defined below. The context argument is used to retrieve the FILE pointer that will be supplied when AddRouter is called.

\*/

void WriteTraceCallback(

Environment \*environment,

const char \*logicalName,

const char \*str,

void \*context)

{

FILE \*theFile = (FILE \*) context;

fprintf(theFile,\"%s\",str);

}

/\*

When we exit CLIPS the trace file needs to be closed. The exit function for our router is defined below. The context argument is used to retrieve the FILE pointer that will be supplied when AddRouter is called.

\*/

void ExitTraceCallback(

Environment \*environment,

int exitCode,

void \*context)

{

FILE \*theFile = (FILE \*) context;

fclose(theFile);

}

/\*

There is no need to define a get character or ungetc character function since this router does not handle input.

A function to turn the trace mode on needs to be defined. This function will check if the trace file has already been opened. If the file is already open, then nothing will happen. Otherwise, the trace file will be opened and the trace router will be creat¬ed. This new router will intercept tracing information intended for the user interface and send it to the trace file. The trace on function is defined below.

\*/

void TraceOn(

Environment \*environment,

UDFContext \*context,

UDFValue \*returnValue)

{

if (DribbleData(environment)-\>traceFP == NULL)

{

DribbleData(environment)-\>traceFP = fopen(\"error.txt\",\"w\");

if (DribbleData(environment)-\>traceFP == NULL)

{

returnValue-\>lexemeValue = environment-\>FalseSymbol;

return;

}

}

else

{

returnValue-\>lexemeValue = environment-\>FalseSymbol;

return;

}

AddRouter(environment,

\"trace\", /\* Router name \*/

20, /\* Priority \*/

QueryTraceCallback, /\* Query function \*/

WriteTraceCallback, /\* Write function \*/

NULL, /\* Read function \*/

NULL, /\* Unread function \*/

ExitTraceCallback, /\* Exit function \*/

DribbleData(environment)-\>traceFP); /\* Context \*/

returnValue-\>lexemeValue = environment-\>TrueSymbol;

}

/\*

A function to turn the trace mode off needs to be defined. This function will check if the trace file is already closed. If the file is already closed, then nothing will happen. Otherwise, the trace router will be deleted and the trace file will be closed. The trace off function is defined below.

\*/

void TraceOff(

Environment \*environment,

UDFContext \*context,

UDFValue \*returnValue)

{

if (DribbleData(environment)-\>traceFP != NULL)

{

DeleteRouter(environment,\"trace\");

if (fclose(DribbleData(environment)-\>traceFP) == 0)

{

DribbleData(environment)-\>traceFP = NULL;

returnValue-\>lexemeValue = environment-\>TrueSymbol;

return;

}

}

DribbleData(environment)-\>traceFP = NULL;

returnValue-\>lexemeValue = environment-\>FalseSymbol;

}

/\*

Now add the definitions for these functions to the UserFunctions func­tion in file \"userfunctions.c\".

\*/

void UserFunctions(

Environment \*env)

{

if (! AllocateEnvironmentData(env,DRIBBLE_DATA,

sizeof(struct dribbleData),NULL))

{

printf(\"Error allocating environment data for DRIBBLE_DATA\\n\");

exit(EXIT_FAILURE);

}

AddUDF(env,\"tron\",\"b\",0,0,NULL,TraceOn,\"tron\",NULL);

AddUDF(env,\"troff\",\"b\",0,0,NULL,TraceOff,\"troff\",NULL);

}

/\*

Compile and link the appropriate files. The trace functions should now be accessible within CLIPS as external functions. For Example:

CLIPS\> (tron)

TRUE

CLIPS\> (+ 2 3)

5

CLIPS\> (\* 3 a)

CLIPS\> (troff)

TRUE

CLIPS\> (exit)

The file error.txt will now contain the following text:

\[ARGACCES5\] Function \* expected argument #2 to be of type integer or float

\*/

### 9.7.2 Better Dribble System

Modify example 1 so the error information is sent to the terminal as well as to the dribble file.

/\*

This example requires a modification of the WriteTraceCallback function. After the error string is printed to the file, the trace router must be deactivated. The error string can then be sent through the WriteString function so that the next router in line can handle the output. After this is done, then the trace router can be reactivated.

\*/

void WriteTraceCallback(

Environment \*environment,

const char \*logicalName,

const char \*str,

void \*context)

{

FILE \*theFile = (FILE \*) context;

fprintf(theFile,\"%s\",str);

DeactivateRouter(environment,\"trace\");

WriteString(environment,logicalName,str);

ActivateRouter(environment,\"trace\");

}

/\*

The TraceOn function must also be modified. The priority of the router should be 40 instead of 20 since the router passes the output along to other routers.

\*/

void TraceOn(

Environment \*environment,

UDFContext \*context,

UDFValue \*returnValue)

{

if (DribbleData(environment)-\>traceFP == NULL)

{

DribbleData(environment)-\>traceFP = fopen(\"error.txt\",\"w\");

if (DribbleData(environment)-\>traceFP == NULL)

{

returnValue-\>lexemeValue = environment-\>FalseSymbol;

return;

}

}

else

{

returnValue-\>lexemeValue = environment-\>FalseSymbol;

return;

}

AddRouter(environment,

\"trace\", /\* Router name \*/

40, /\* Priority \*/

QueryTraceCallback, /\* Query function \*/

WriteTraceCallback, /\* Write function \*/

NULL, /\* Read function \*/

NULL, /\* Unread function \*/

ExitTraceCallback, /\* Exit function \*/

DribbleData(environment)-\>traceFP); /\* Context \*/

returnValue-\>lexemeValue = environment-\>TrueSymbol;

}

### 9.7.3 Batch System

Write the necessary functions that will allow batch input from the file \"batch.txt\" to the CLIPS top‑level interface. ***Note that this example only works in the console version of CLIPS***.

/\*

First of all, we need a file pointer to the batch file which will contain the batch command information.

\*/

#include \<stdio.h\>

#include \<stdlib.h\>

#include \"clips.h\"

#define BATCH_DATA USER_ENVIRONMENT_DATA + 2

struct batchData

{

FILE \*batchFP;

StringBuilder \*batchBuffer;

};

#define BatchData(theEnv) \\

((struct batchData \*) GetEnvironmentData(theEnv,BATCH_DATA))

bool QueryMybatchCallback(Environment \*,const char \*,void \*);

int ReadMybatchCallback(Environment \*,const char \*,void \*);

int UnreadMybatchCallback(Environment \*,const char \*,int,void \*);

void ExitMybatchCallback(Environment \*environment,int,void \*);

void MybatchOn(Environment \*,UDFContext \*,UDFValue \*);

/\*

We want to recognize any input requested from the logical name \"stdin\" because all user input is received from this logical name. The recognizer function for our router is defined below.

\*/

bool QueryMybatchCallback(

Environment \*environment,

const char \*logicalName,

void \*context)

{

if (strcmp(logicalName,STDIN) == 0) return true;

return false;

}

/\*

We now need to define a function which will get and unget charac­ters from our batch file. The get and ungetc character functions for our router are defined below.

\*/

int ReadMybatchCallback(

Environment \*environment,

const char \*logicalName,

void \*context)

{

int rv;

rv = getc(BatchData(environment)-\>batchFP);

if (rv == EOF)

{

Write(environment,BatchData(environment)-\>batchBuffer-\>contents);

SBDispose(BatchData(environment)-\>batchBuffer);

BatchData(environment)-\>batchBuffer = NULL;

DeleteRouter(environment,\"mybatch\");

fclose(BatchData(environment)-\>batchFP);

return ReadRouter(environment,logicalName);

}

SBAddChar(BatchData(environment)-\>batchBuffer,rv);

if ((rv == \'\\n\') \|\| (rv == \'\\r\'))

{

Write(environment,BatchData(environment)-\>batchBuffer-\>contents);

SBReset(BatchData(environment)-\>batchBuffer);

}

return rv;

}

int UnreadMybatchCallback(

Environment \*environment,

const char \*logicalName,

int ch,

void \*context)

{

SBAddChar(BatchData(environment)-\>batchBuffer,\'\\b\');

return ungetc(ch,BatchData(environment)-\>batchFP);

}

/\*

When we exit CLIPS the batch file needs to be closed. The exit function for our router is defined below.

\*/

void ExitMybatchCallback(

Environment \*environment,

int exitCode,

void \*context)

{

FILE \*theFile = (FILE \*) context;

if (BatchData(environment)-\>batchBuffer != NULL)

{

SBDispose(BatchData(environment)-\>batchBuffer);

BatchData(environment)-\>batchBuffer = NULL;

}

fclose(theFile);

}

/\*

There is no need to define a print function since this router does not handle output except for echoing the command line.

Now we define a function that turns the batch mode on.

\*/

void MybatchOn(

Environment \*environment,

UDFContext \*context,

UDFValue \*returnValue)

{

BatchData(environment)-\>batchFP = fopen(\"batch.txt\",\"r\");

if (BatchData(environment)-\>batchFP == NULL)

{

returnValue-\>lexemeValue = environment-\>FalseSymbol;

return;

}

if (BatchData(environment)-\>batchBuffer == NULL)

{ BatchData(environment)-\>batchBuffer = CreateStringBuilder(environment,80); }

AddRouter(environment,

\"mybatch\", /\* Router name \*/

20, /\* Priority \*/

QueryMybatchCallback, /\* Query function \*/

NULL, /\* Write function \*/

ReadMybatchCallback, /\* Read function \*/

UnreadMybatchCallback, /\* Unread function \*/

ExitMybatchCallback, /\* Exit function \*/

BatchData(environment)-\>batchFP); /\* context \*/

returnValue-\>lexemeValue = environment-\>TrueSymbol;

}

/\*

Now add the definition for this function to the UserFunctions function in file \"userfunctions.c\".

\*/

void UserFunctions(

Environment \*env)

{

if (! AllocateEnvironmentData(env,BATCH_DATA,

sizeof(struct batchData),NULL))

{

printf(\"Error allocating environment data for BATCH_DATA\\n\");

exit(EXIT_FAILURE);

}

AddUDF(env,\"mybatch\",\"b\",0,0,NULL,MybatchOn,\"MybatchOn\",NULL);

}

/\*

Compile and link the appropriate files. The batch function should now be accessible within CLIPS as external function. For Example, create the file batch.txt with the

following content:

(+ 2 3)

(\* 4 5)

Launch CLIPS and enter a (mybatch) command:

CLIPS\> (mybatch)

TRUE

CLIPS\> (+ 2 3)

5

CLIPS\> (\* 4 5)

20

CLIPS\>

\*/

### 9.7.4 Simple Window System

Write the necessary functions using CURSES (a screen management function available in UNIX) that will allow a top/bottom split screen interface. Output sent to the logical name **top** will be printed in the upper win­dow. All other screen I/O should go to the lower window. (NOTE: Use of CURSES may require linking with special libraries. On UNIX systems try using --lcurses when linking.)

/\*

First of all, we need some pointers to the windows and a flag to indicate that the windows have been initialized.

\*/

#include \<stdio.h\>

#include \<stdlib.h\>

#include \<curses.h\>

#include \"clips.h\"

#define CURSES_DATA USER_ENVIRONMENT_DATA + 3

struct cursesData

{

WINDOW \*lowerWindow, \*upperWindow;

bool windowsInitialized;

bool useSave;

int saveChar;

bool sendReturn;

char buffer\[512\];

int charLocation;

};

#define CursesData(theEnv) \\

((struct cursesData \*) GetEnvironmentData(theEnv,CURSES_DATA))

bool QueryScreenCallback(Environment \*,const char \*,void \*);

void WriteScreenCallback(Environment \*,const char \*,const char \*,void \*);

int ReadScreenCallback(Environment \*,const char \*,void \*);

int UnreadScreenCallback(Environment \*,const char \*,int,void \*);

void ExitScreenCallback(Environment \*environment,int,void \*);

void ScreenOn(Environment \*,UDFContext \*,UDFValue \*);

void ScreenOff(Environment \*,UDFContext \*,UDFValue \*);

/\*

We want to intercept any I/O requests that the standard interface would handle. In addition, we also need to handle requests for the logical name top. The recognizer function for our router is defined below.

\*/

bool QueryScreenCallback(

Environment \*environment,

const char \*logicalName,

void \*context)

{

if ((strcmp(logicalName,STDOUT) == 0) \|\|

(strcmp(logicalName,STDIN) == 0) \|\|

(strcmp(logicalName,STDERR) == 0) \|\|

(strcmp(logicalName,STDWRN) == 0) \|\|

(strcmp(logicalName,\"top\") == 0) )

{ return true; }

return false;

}

/\*

We now need to define a function which will print strings to the two windows. The print function for our router is defined below.

\*/

void WriteScreenCallback(

Environment \*environment,

const char \*logicalName,

const char \*str,

void \*context)

{

struct cursesData \*theData = (struct cursesData \*) context;

if (strcmp(logicalName,\"top\") == 0)

{

wprintw(theData-\>upperWindow,\"%s\",str);

wrefresh(theData-\>upperWindow);

}

else

{

wprintw(theData-\>lowerWindow,\"%s\",str);

wrefresh(theData-\>lowerWindow);

}

}

/\*

We now need to define a function which will get and unget characters from the lower window. CURSES uses unbuffered input so we will simulate buffered input for CLIPS. The get and ungetc char­acter functions for our router are defined below.

\*/

int ReadScreenCallback(

Environment \*environment,

const char \*logicalName,

void \*context)

{

struct cursesData \*theData = (struct cursesData \*) context;

int rv;

if (theData-\>useSave)

{

theData-\>useSave = false;

return theData-\>saveChar;

}

if (theData-\>buffer\[theData-\>charLocation\] == \'\\0\')

{

if (theData-\>sendReturn == false)

{

theData-\>sendReturn = true;

return \'\\n\';

}

wgetnstr(theData-\>lowerWindow,&theData-\>buffer\[0\],511);

theData-\>charLocation = 0;

}

rv = theData-\>buffer\[theData-\>charLocation\];

if (rv == \'\\0\') return \'\\n\';

theData-\>charLocation++;

theData-\>sendReturn = false;

return rv;

}

int UnreadScreenCallback(

Environment \*environment,

const char \*logicalName,

int ch,

void \*context)

{

struct cursesData \*theData = (struct cursesData \*) context;

theData-\>useSave = true;

theData-\>saveChar = ch;

return ch;

}

/\*

When we exit CLIPS CURSES needs to be deactivated. The exit function for our router is defined below.

\*/

void ExitScreenCallback(

Environment \*environment,

int exitCode,

void \*context)

{

endwin();

}

/\*

Now define a function that turns the screen mode on.

\*/

void ScreenOn(

Environment \*environment,

UDFContext \*context,

UDFValue \*returnValue)

{

int halfLines, i;

/\* Has initialization already occurred? \*/

if (CursesData(environment)-\>windowsInitialized)

{

returnValue-\>lexemeValue = environment-\>FalseSymbol;

return;

}

/\* Reroute I/O and initialize CURSES. \*/

initscr();

echo();

CursesData(environment)-\>windowsInitialized = true;

CursesData(environment)-\>useSave = false;

CursesData(environment)-\>sendReturn = true;

CursesData(environment)-\>buffer\[0\] = \'\\0\';

CursesData(environment)-\>charLocation = 0;

AddRouter(environment,

\"screen\", /\* Router name \*/

10, /\* Priority \*/

QueryScreenCallback, /\* Query function \*/

WriteScreenCallback, /\* Write function \*/

ReadScreenCallback, /\* Read function \*/

UnreadScreenCallback, /\* Unread function \*/

ExitScreenCallback, /\* Exit function \*/

CursesData(environment)); /\* Context \*/

/\* Create the two windows. \*/

halfLines = LINES / 2;

CursesData(environment)-\>upperWindow = newwin(halfLines,COLS,0,0);

CursesData(environment)-\>lowerWindow = newwin(halfLines - 1,COLS,halfLines + 1,0);

/\* Both windows should be scrollable. \*/

scrollok(CursesData(environment)-\>upperWindow,TRUE);

scrollok(CursesData(environment)-\>lowerWindow,TRUE);

/\* Separate the two windows with a line. \*/

for (i = 0 ; i \< COLS ; i++)

{ mvaddch(halfLines,i,\'-\'); }

refresh();

wclear(CursesData(environment)-\>upperWindow);

wclear(CursesData(environment)-\>lowerWindow);

wmove(CursesData(environment)-\>lowerWindow,0,0);

returnValue-\>lexemeValue = environment-\>TrueSymbol;

}

/\*

Now define a function that turns the screen mode off.

\*/

void ScreenOff(

Environment \*environment,

UDFContext \*context,

UDFValue \*returnValue)

{

/\* Is CURSES already deactivated? \*/

if (CursesData(environment)-\>windowsInitialized == false)

{

returnValue-\>lexemeValue = environment-\>FalseSymbol;

return;

}

CursesData(environment)-\>windowsInitialized = false;

/\* Remove I/O rerouting and deactivate CURSES. \*/

DeleteRouter(environment,\"screen\");

endwin();

returnValue-\>lexemeValue = environment-\>TrueSymbol;

}

/\*

Now add the definitions for these functions to the UserFunctions func­tion in file \"userfunctions.c\".

\*/

void UserFunctions(

Environment \*env)

{

if (! AllocateEnvironmentData(env,CURSES_DATA,

sizeof(struct cursesData),NULL))

{

printf(\"Error allocating environment data for CURSES_DATA\\n\");

exit(EXIT_FAILURE);

}

AddUDF(env,\"screen-on\",\"b\",0,0,NULL,ScreenOn,\"ScreenOn\",NULL);

AddUDF(env,\"screen-off\",\"b\",0,0,NULL,ScreenOff,\"ScreenOff\",NULL);

}

/\*

Compile and link the appropriate files. The screen functions should now be accessible within CLIPS as external functions. For Example

CLIPS\> (screen-on)

CLIPS\> (printout top \"Hello World\" crlf)

•

•

•

CLIPS\> (screen-off)

\*/
