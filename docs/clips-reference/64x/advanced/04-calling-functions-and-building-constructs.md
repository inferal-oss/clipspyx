# Section 4: Calling Functions and Building Constructs

The **Eval** function provides a mechanism for executing functions and commands in CLIPS and returning a value from CLIPS back to C. This is useful for executing commands from C in a similar manner to using the CLIPS command prompt. In conjunction with the fact and instance query functions, it is also a useful mechanism for retrieving the results of a CLIPS program.

The **Build** function provides a mechanism for defining individual constructs in a similar manner to using the CLIPS command prompt. Much like entering constructs at the command prompt, this functionality is primarily useful in examples and tutorials.

Since many CLIPS functions (including **Eval** and **Build**) take string arguments that may need to be created dynamically, CLIPS provides **StringBuilder** functions that automate the allocation, construction, and resizing of strings as character data is appended.

## 4.1 CLIPS Primitive Values

CLIPS wraps the underlying C representation of its primitive data types within C structure types that share a common **header** field containing type information. This allows CLIPS primitive values to be passed as a single pointer that can be examined for type to determine the C primitive type stored in the structure.

There are nine C types for used to represent CLIPS primitive values: **TypeHeader** for any CLIPS primitive value; **CLIPSLexeme** for symbols, strings, and instance names, **CLIPSFloat** for floats; **CLIPSInteger** for integers; **CLIPSVoid** for void; **Fact** for facts; **Instance** for instances; **CLIPSExternalAddress** for external addresses; and **Multifield** for multifields.

### 4.1.1 TypeHeader

The C **TypeHeader** type is used to store the CLIPS primitive value type.

typedef struct typeHeader

{

unsigned short type;

} TypeHeader;

The integer stored in the **type** field is one of the following predefined constants:

> EXTERNAL_ADDRESS_TYPE
>
> FACT_ADDRESS_TYPE
>
> FLOAT_TYPE
>
> INSTANCE_ADDRESS_TYPE
>
> INSTANCE_NAME_TYPE
>
> INTEGER_TYPE
>
> MULTIFIELD_TYPE
>
> STRING_TYPE
>
> SYMBOL_TYPE
>
> VOID_TYPE

### 4.1.2 CLIPSValue

The C **CLIPSValue** type encapsulates all of the CLIPS primitive types. Functions returning primitive values from CLIPS to C have parameters of type **CLIPSValue \***. The return value of the function is stored in the **CLIPSValue** structure allocated by caller. The **header** field of the **CLIPSValue** union can be examined to determine the CLIPS primitive value type and then the appropriate field from the **CLIPSValue** union can be examined to retrieve the C representation of the type.

typedef struct clipsValue

{

union

{

void \*value;

TypeHeader \*header;

CLIPSLexeme \*lexemeValue;

CLIPSFloat \*floatValue;

CLIPSInteger \*integerValue;

CLIPSVoid \*voidValue;

Fact \*factValue;

Instance \*instanceValue;

Multifield \*multifieldValue;

CLIPSExternalAddress \*externalAddressValue;

};

} CLIPSValue;

### 4.1.3 Symbol, Strings, and Instance Names

The C **CLIPSLexeme** type is used to represent CLIPS symbol, string, and instance name primitive types.

typedef struct clipsLexeme

{

TypeHeader header;

const char \*contents;

} CLIPSLexeme;

The **contents** field of the **CLIPSLexeme** contains the C string associated with the CLIPS primitive value. This value should not be changed by user code.

### 4.1.4 Integers

The C **CLIPSInteger** type is used to represent CLIPS integers.

typedef struct clipsInteger

{

TypeHeader header;

long long contents;

} CLIPSInteger;

The **contents** field of the **CLIPSInteger** contains the C long long associated with the CLIPS primitive value. This value should not be changed by user code.

### 4.1.5 Floats

The C **CLIPSFloat** type is used to represent CLIPS floats.

typedef struct clipsFloat

{

TypeHeader header;

double contents;

} CLIPSFloat;

The **contents** field of the **CLIPSFloat** contains the C double associated with the CLIPS primitive value. This value should not be changed by user code.

### 4.1.6 Multifields

The C **Multifield** type is used to represent CLIPS multifields.

typedef struct multifield

{

TypeHeader header;

size_t length;

CLIPSValue \*contents;

} Multifield;

The **length** field contains the number of CLIPS primitive values contained in the **Multifield** type. The **contents** field is a pointer to an array containing a number of CLIPValue structs that is specified by the length field.

### 4.1.7 Void

The **CLIPSVoid** type is used to represent the CLIPS void value.

typedef struct clipsVoid

{

TypeHeader header;

} CLIPSVoid;

### 4.1.8 External Address

The **CLIPSExternalAddress** struct is used to represent CLIPS external addresses.

typedef struct clipsExternalAddress

{

TypeHeader header;

void \*contents;

} CLIPSExternalAddress;

The **contents** field of the **CLIPSExternalAddress** contains the external address associated with the CLIPS primitive value. This value should not be changed by user code.

## 4.2 Eval and Build

EvalError Eval(\
Environment \*env,\
const char \*str,\
CLIPSValue \*cv);

BuildError Build(\
Environment \*env,\
const char \*str);

typedef enum\
{\
EE_NO_ERROR,\
EE_PARSING_ERROR,\
EE_PROCESSING_ERROR\
} EvalError;

typedef enum\
{\
BE_NO_ERROR,\
BE_COULD_NOT_BUILD_ERROR,\
BE_CONSTRUCT_NOT_FOUND_ERROR,\
BE_PARSING_ERROR,\
} BuildError;

The function **Eval** is the C equivalent of the CLIPS **eval** command. The function **Build** is the C equivalent of the CLIPS **build** command. For both functions, the **env** parameter is a pointer to a previously created environment. The **str** parameter for the **Eval** function is a string containing a CLIPS command or function call; and for the **Build** function is a string containing a construct definition. If the **cv** parameter value for the **Eval** function is not a null pointer, then the return value of the CLIPS command or function call is stored in the **CLIPSValue** structure allocated by the caller and referenced by the pointer.

The error codes for the **Eval** function are:

  -------------------------------- ----------------------------------------------------------
  **Error Code**                   **Meaning**

  EE_NO_ERROR                      No error occurred.

  EE_PARSING_ERROR                 A syntax error was encountered while parsing.

  EE_PROCESSING_ERROR              An error occurred while executing the parsed expression.
  -------------------------------- ----------------------------------------------------------

The error codes for the **Build** function are:

  ----------------------------------- -------------------------------------------------------------------------------
  **Error Code**                      **Meaning**

  BE_NO_ERROR                         No error occurred.

  BE_PARSING_ERROR                    A syntax error was encountered while parsing.

  BE_CONSTRUCT_NOT_FOUND_ERROR        The construct name following the opening left parenthesis was not recognized.

  BE_COULD_NOT_BUILD_ERROR            The construct could not be added (such as when pattern matching is active).
  ----------------------------------- -------------------------------------------------------------------------------

## 4.3 FunctionCallBuilder Functions

The CLIPS **FunctionCallBuilder** functions provide a mechanism for dynamically calling CLIPS functions. It can be used in place of the simpler **Eval** function when arguments that cannot be represented as strings (such as fact and instance pointers) must be passed to a function. A **FunctionCallBuilder** is created using the **CreateFunctionCallBuilder** function. Arguments can be appended to the **FunctionCallBuilder** using the **FCBAppend...** functions. A function can then be evaluated with the assigned arguments by calling the **FCBCall** function. To call a function with different parameters, the **FCBReset** function can be called to reset the **FunctionCallBuilder** to its initial state. Once it is no longer needed, the **FunctionCallBuilder** can be deallocated using the **FCBDispose** function.

FunctionCallBuilder \*CreateFunctionCallBuilder(\
Environment \*env,\
size_t capacity);

FunctionCallBuilderError FCBCall(\
FunctionCallBuilder \*fcb,\
const char \*functionName,\
CLIPSValue \*cv);

void FCBReset(\
FunctionCallBuilder \*fcb);

void FCBDispose(\
FunctionCallBuilder \*fcb);

void FCBAppend(\
FunctionCallBuilder \*mb,\
CLIPSValue \*value);

void FCBAppendUDFValue(\
FunctionCallBuilder \*fcb,\
UDFValue \*);

void FCBAppendInteger(\
FunctionCallBuilder \*fcb,\
long long value);

void FCBAppendFloat(\
FunctionCallBuilder \*fcb,\
double value);

void FCBAppendSymbol(\
FunctionCallBuilder \*fcb,\
const char \*value);

void FCBAppendString(\
FunctionCallBuilder \*fcb,\
const char \*value);

void FCBAppendInstanceName(\
FunctionCallBuilder \*fcb,\
const char \*value);

void FCBAppendCLIPSInteger(\
FunctionCallBuilder \*fcb,\
CLIPSInteger \*value);

void FCBAppendCLIPSFloat(\
FunctionCallBuilder \*fcb,\
CLIPSFloat \*value);

void FCBAppendCLIPSLexeme(\
FunctionCallBuilder \*fcb,\
CLIPSLexeme \*value);

void FCBAppendFact(\
FunctionCallBuilder \*fcb,\
Fact \*value);

void FCBAppendInstance(\
FunctionCallBuilder \*fcb,\
CLIPSValue \*value);

void FCBAppendMultifield(\
FunctionCallBuilder \*fcb,\
Multifield \*value);

void FCBAppendCLIPSExternalAddress(\
FunctionCallBuilder \*fcb,\
CLIPSExternalAddress \*value);

void FCBPopArgument(\
FunctionCallBuilder \*fcb);

typedef enum\
{\
FCBE_NO_ERROR,\
FCBE_NULL_POINTER_ERROR,\
FCBE_FUNCTION_NOT_FOUND_ERROR,\
FCBE_INVALID_FUNCTION_ERROR,\
FCBE_ARGUMENT_COUNT_ERROR,\
FCBE_ARGUMENT_TYPE_ERROR,\
FCBE_PROCESSING_ERROR\
} FunctionCallBuilderError;

The function **CreateFunctionCallBuilder** creates and initializes a value of type **FunctionCallBuilder**. Parameter **env** is a pointer to a previously created environment; and parameter **capacity** is the initial size of the array used by the **FunctionCallBuilder** for storing the function call arguments. The initial size does not limit the maximum number arguments that can be passed to a function. The capacity of the **FunctionCallBuilder** will be increased if the number of arguments becomes larger than the initial capacity. If successful, this function returns a pointer of type **FunctionCallBuilder \*** to identify the target of other functions accepting a **FunctionCallBuilder** parameter; if any error occurs, a null pointer is returned.

The function **FCBCall** executes the function specified by the **functionName** parameter with the arguments that were previously appended to the **FunctionCallBuilder** specified by parameter **fcb**. If the parameter **cv** is not a NULL pointer, the return value of the executed function will be stored in the specified **CLIPSValue** structure.

The error codes for the **FCBCall** function are:

  ------------------------------------ ----------------------------------------------------------------------------------------------------------------------------
  **Error Code**                       **Meaning**

  FCBE_NO_ERROR                        No error occurred.

  FCBE_NULL_POINTER_ERROR              The **fcb** or **functionName** parameter was NULL.

  FCBE_FUNCTION_NOT_FOUND_ERROR        A function, deffunction, or generic function could not be found with the name specified by the **functionName** parameter.

  FCBE_INVALID_FUNCTION_ERROR          The function or command has a specialized parser (such as the **assert** command) and cannot be invoked.

  FCBE_ARGUMENT_COUNT_ERROR            The function was passed the incorrect number of arguments.

  FCBE_ARGUMENT_TYPE_ERROR             The function was passed an argument with an invalid type.

  FCBE_PROCESSING_ERROR                An error occurred while the function was being evaluated.
  ------------------------------------ ----------------------------------------------------------------------------------------------------------------------------

The function **FCBReset** resets the **FunctionCallBuilder** specified by parameter **fcb** to its initial capacity. Any arguments previously appended are removed.

The function **FCBDispose** deallocates all memory associated with previously allocated **FunctionCallBuilder** specified by parameter **fcb**.

The functions **FCBAppend**, **FCBAppendUDFValue**, **FCBAppendInteger**, **FCBAppendFloat**, **FCBAppendSymbol**, **FCBAppendString**, **FCBAppendInstanceName**, **FCBAppendCLIPSInteger**, **FCBAppendCLIPSFloat**, **FCBAppendCLIPSLexeme**, **FCBAppendFact**, **FCBAppendInstance**, **FCBAppendMultifield**, and **FCBAppendCLIPSExternalAddress** append the parameter value to the end of the arguments being created by the **FunctionCallBuilder** specified by parameter **fcb**.

The function **FCBPopArgument** removes the last argument of the **FunctionCallBuilder** specified by parameter **fcb**.

## 4.4 StringBuilder Functions

The CLIPS **StringBuilder** functions provide a mechanism for dynamically creating strings of varying length, automatically resizing the **content** output string as character data is added. A StringBuilder is created using the **CreateStringBuilder** function. Character data can then be append to the StringBuilder using the **SBAddChar** and **SBAppend** functions. To build additional strings, the **SBReset** function can be called to reset the **StringBuilder** to its initial state. Once it is no longer needed, the StringBuilder can be deallocated using the **SBDispose** function.

The **StringBuilder** type definition with public fields is:

typedef struct stringBuilder

{

char \*contents;

size_t length;

} StringBuilder;

The **contents** field of the **StringBuilder** type is a pointer to a character array containing all of the characters that have been appended by calls to the **SBAddChar** and **SBAppend** functions. The value of the **contents** field can change if appending to the **StringBuilder** exceeds the current capacity, so it is recommended to always directly retrieve the **contents** field from the **StringBuilder** pointer. Use the **SBCopy** function to create a copy of the **contents** field if desired; otherwise, the **contents** field should never be directly modified.

The **length** field of the **StringBuilder** type contains the number of characters in the **contents** field not including the null character at the end of the string.

### 4.4.1 CreateStringBuilder

StringBuilder \*CreateStringBuilder(\
Environment \*env,\
size_t capacity);

The function **CreateStringBuilder** creates and initializes a value of type **StringBuilder**. Parameter **env** is a pointer to a previously created environment; and parameter **capacity** is the initial size of the character array used by the **StringBuilder** for constructing strings. The initial size does not limit the maximum size of the **contents** string. The capacity of the StringBuilder will be increased if the string size becomes larger than the initial capacity. If successful, this function returns a pointer of type **StringBuilder \*** to identify the target of other functions accepting a **StringBuilder** parameter; if any error occurs, a null pointer is returned.

### 4.4.2 SBAddChar

void SBAddChar(\
StringBuilder \*sb,\
int c);

The function **SBAddChar** appends the single character specified by parameter **c** to the **contents** string of the previously allocated **StringBuilder** specified by parameter **sb**. If the **c** parameter value is a backspace, then the last character of the **contents** string is removed.

### 4.4.3 SBAppend Functions

void SBAppend(\
StringBuilder \*sb,\
const char \*value);

void SBAppendInteger(\
StringBuilder \*sb,\
long long value);

void SBAppendFloat(\
StringBuilder \*sb,\
double value);

The **SBAppend** functions append the parameter **value** to the **contents** string of the previously allocated **StringBuilder** specified by parameter **sb**.

### 4.4.4 SBCopy

char \*SBCopy(\
StringBuilder \*sb);

The function **SBCopy** returns a copy of **contents** string of the previously allocated **StringBuffer** specified by parameter **sb**. The memory allocated for this string will not be freed by CLIPS, so it is necessary for the user's code to call the **free** C library function to deallocate the memory once it is no longer needed.

### 4.4.5 SBDispose

void SBDispose(\
StringBuilder \*sb);

The function **SBDispose** deallocates all memory associated with previously allocated **StringBuilder** specified by parameter **sb**.

### 4.4.6 SBReset

void SBReset(\
StringBuilder \*sb);

The function **SBReset** resets the **StringBuilder** specified by parameter **sb** to its initial capacity. The **contents** string is set to an empty string and the **length** of the **StringBuilder** is set to 0.

## 4.5 Examples

### 4.5.1 Debugging Revisited

This example reimplements the debugging example from section 3.6.2 but uses the **Build** function for adding constructs and the **Eval** function for issuing commands.

#include \"clips.h\"

int main()

{

Environment \*env;

env = CreateEnvironment();

Build(env,\"(deftemplate list\"

\" (multislot numbers))\");

Build(env,\"(defrule sort\"

\" ?f \<- (list (numbers \$?b ?x ?y&:(\> ?x ?y) \$?e))\"

\" =\>\"

\" (modify ?f (numbers ?b ?y ?x ?e)))\");

Eval(env,\"(watch facts)\",NULL);

Eval(env,\"(watch rules)\",NULL);

Eval(env,\"(watch activations)\",NULL);

Eval(env,\"(dribble-on sort.dbg)\",NULL);

Eval(env,\"(reset)\",NULL);

Eval(env,\"(assert (list (numbers 61 31 27 48)))\",NULL);

Eval(env,\"(run)\",NULL);

Eval(env,\"(dribble-off)\",NULL);

DestroyEnvironment(env);

}

### 4.5.2 String Builder Function Call

This example illustrates using the **StringBuilder** and **Eval** functions to construct and evaluate a function call. The **PrintString** and **PrintCLIPSValue** **Router** functions (described in Section 9) are used to print the value and type of each field in the multifield return value.

#include \"clips.h\"

int main()

{

Environment \*env;

StringBuilder \*sb;

CLIPSValue cv;

char \*fullName;

// Create an Environment

// and StringBuilder.

env = CreateEnvironment();

sb = CreateStringBuilder(env,512);

// Get the first name.

Write(env,\"First Name: \");

Eval(env,\"(read)\",&cv);

if (cv.header-\>type == SYMBOL_TYPE)

{ SBAppend(sb,cv.lexemeValue-\>contents); }

else

{ SBAppend(sb,\"John\"); }

SBAppend(sb,\" \");

// Get the last name.

Write(env,\"Last Name: \");

Eval(env,\"(read)\",&cv);

if (cv.header-\>type == SYMBOL_TYPE)

{ SBAppend(sb,cv.lexemeValue-\>contents); }

else

{ SBAppend(sb,\"Doe\"); }

// Get a copy of the full name

// constructed by the StringBuilder.

fullName = SBCopy(sb);

// Create a function call to convert

// the full name to upper case.

SBReset(sb);

SBAppend(sb,\"(upcase \\\"\");

SBAppend(sb,fullName);

SBAppend(sb,\"\\\")\");

// Evaluate the function call

// and print the results.

Eval(env,sb-\>contents,&cv);

Write(env,\"Result is \");

Writeln(env,cv.lexemeValue-\>contents);

// Free the fullName

free(fullName);

// Dispose of the StringBuilder

// and the Environment.

SBDispose(sb);

DestroyEnvironment(env);

}

The resulting output (with input in bold) is:

First Name: **Sally**

Last Name: **Jones**

Result is SALLY JONES

### 4.5.3 Multifield Iteration

This example illustrates iteration over the values contained in a **Multifield**.

#include \"clips.h\"

int main()

{

Environment \*env;

StringBuilder \*sb;

CLIPSValue cv;

// Create an Environment

// and StringBuilder.

env = CreateEnvironment();

sb = CreateStringBuilder(env,512);

// Call the CLIPS readline function to

// capture a list of values in a string.

Write(env,\"Enter a list of values: \");

Eval(env,\"(readline)\",&cv);

// Call the CLIPS create\$ function to generate

// a multifield value from the string.

SBAppend(sb,\"(create\$ \");

SBAppend(sb,cv.lexemeValue-\>contents);

SBAppend(sb,\")\");

Eval(env,sb-\>contents,&cv);

// Iterate over each value in the

// multifield and print its type.

for (size_t i = 0; i \< cv.multifieldValue-\>length; i++)

{

WriteCLIPSValue(env,STDOUT,&cv.multifieldValue-\>contents\[i\]);

switch(cv.multifieldValue-\>contents\[i\].header-\>type)

{

case INTEGER_TYPE:

Write(env,\" is an integer\\n\");

break;

case FLOAT_TYPE:

Write(env,\" is a float\\n\");

break;

case STRING_TYPE:

Write(env,\" is a string\\n\");

break;

case SYMBOL_TYPE:

Write(env,\" is a symbol\\n\");

break;

case INSTANCE_NAME_TYPE:

Write(env,\" is an instance name\\n\");

break;

}

}

// Dispose of the StringBuilder

// and the Environment.

SBDispose(sb);

DestroyEnvironment(env);

}

The resulting output (with input in bold) is:

Enter a list of values: **a \"b\" \[c\] 1.2 3**

a is a symbol

\"b\" is a string

\[c\] is an instance name

1.2 is a float

3 is an integer

### 4.5.4 Fact Query

This example illustrates how to use the **StringBuilder** and **Eval** functions to dynamically construct and assert a fact, retrieve values from CLIPS function calls, and use a fact query to retrieve a slot value from a fact after rules have executed.

The first section of code for this example (that includes the function **CreateNumbers**) demonstrates the construction of a **list** fact with a **numbers** slot containing zero or more integers. The number of integers to be created is specified by the **howMany** parameter.

#include \"clips.h\"

void CreateNumbers(Environment \*,StringBuilder \*,int);

void PrintNumbers(Environment \*);

void CreateNumbers(

Environment \*env,

StringBuilder \*sb,

int howMany)

{

CLIPSValue cv;

// Append the opening parentheses

// for the fact and the slot.

SBAppend(sb,\"(list (numbers\");

// Loop adding the specified

// number of random integers

for (int i = 0; i \< howMany; i++)

{

// Generate a random number in the

// range 0 - 99. Convert the integer

// on the CLIPS side to a symbol.

Eval(env,\"(sym-cat (random 0 99))\",&cv);

// Add the string value of the

// integer to the slot.

SBAppend(sb,\" \");

SBAppend(sb,cv.lexemeValue-\>contents);

}

// Append the closing parentheses

// for the slot and the fact.

SBAppend(sb,\"))\");

// Assert the fact.

Watch(env,FACTS);

AssertString(env,sb-\>contents);

Unwatch(env,FACTS);

// Clear the StringBuilder.

SBReset(sb);

}

The next section of code (that includes the **PrintNumbers** function) demonstrates how to use a query function to retrieve a slot value from a fact; and how to iterate through the contents of a multifield value. The **Write** and **WriteCLIPSValue** **Router** functions (described in Section 9) are used to print the slot value.

void PrintNumbers(

Environment \*env)

{

CLIPSValue cv;

// This do-for-fact query call will find the first list

// fact \-- there should just be one \-- and return the

// value of the numbers slot in the variable cv.

Eval(env,\"(do-for-fact ((?f list)) TRUE ?f:numbers)\",&cv);

// The numbers slot should be a multifield value.

if (cv.header-\>type == MULTIFIELD_TYPE)

{

Write(env,\"Sorted list is (\");

// Iterate over each value in the

// multifield and print it.

for (size_t i = 0; i \< cv.multifieldValue-\>length; i++)

{

if (i != 0) Write(env,\" \");

WriteCLIPSValue(env,STDOUT,&cv.multifieldValue-\>contents\[i\]);

}

Write(env,\")\\n\");

}

}

The final section of code (that includes the **main** function) generates a list of random numbers (using the **CreateNumbers** function), sorts them (using the **sort** rule), prints the sorted numbers (using the **PrintNumbers** function), and then repeats the process a second time.

int main()

{

Environment \*env;

StringBuilder \*sb;

// Create an Environment

// and StringBuilder.

env = CreateEnvironment();

sb = CreateStringBuilder(env,512);

// Seed the random number generator so that

// different numeric values are generated

// each time the program is run.

Eval(env,\"(seed (integer (time)))\",NULL);

// Create the sorting constructs

Build(env,\"(deftemplate list\"

\" (multislot numbers))\");

Build(env,\"(defrule sort\"

\" ?f \<- (list (numbers \$?b ?x ?y&:(\> ?x ?y) \$?e))\"

\" =\>\"

\" (modify ?f (numbers ?b ?y ?x ?e)))\");

// Create a list, sort it,

// and print the results.

Reset(env);

CreateNumbers(env,sb,5);

Run(env,-1);

PrintNumbers(env);

// Create another list, sort

// it, and print the results.

Reset(env);

CreateNumbers(env,sb,7);

Run(env,-1);

PrintNumbers(env);

// Dispose of the StringBuilder

// and the Environment.

SBDispose(sb);

DestroyEnvironment(env);

}

The resulting output is:

==\> f-1 (list (numbers 43 76 3 55 87))

Sorted list is (3 43 55 76 87)

==\> f-1 (list (numbers 73 17 7 84 68 54 67))

Sorted list is (7 17 54 67 68 73 84)

Note that the sorted integers displayed will vary since the generated random integers are dependent on the implementation of the C **rand** library function as well as the seeding of the random number generator using the current time.

### 4.5.5 Function Call Builder

This example illustrates using the **FunctionCallBuilder** functions to send an instance a print message.

#include \"clips.h\"

int main()

{

Environment \*env;

FunctionCallBuilder \*fcb;

Instance \*ins;

env = CreateEnvironment();

Build(env,\"(defclass POINT (is-a USER) (slot x) (slot y))\");

ins = MakeInstance(env,\"(\[p1\] of POINT (x 3) (y 4))\");

fcb = CreateFunctionCallBuilder(env,2);

FCBAppendInstance(fcb,ins);

FCBAppendSymbol(fcb,\"print\");

FCBCall(fcb,\"send\",NULL);

FCBDispose(fcb);

DestroyEnvironment(env);

}

The resulting output is:

\[p1\] of POINT

(x 3)

(y 4)
