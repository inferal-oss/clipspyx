# Section 8: User Defined Functions

CLIPS provides a collection of system defined functions and commands for a variety of purposes. In addition, the deffunction construct can be used to create new functions and commands within a CLIPS program. In some cases, however, it is necessary to integrate functions written in C with the CLIPS C source code. This may be for performance reasons; to integrate existing code written in C; or to integrate a C library.

Functions written in C that are integrated with CLIPS using the protocols described in this section are referred to as User Defined Functions (UDFs) and can be used in the same manner as system defined functions and commands. In fact, the system defined functions and commands provided by CLIPS are integrated using the protocols described in this section. Note that while the word 'command' is typically used throughout this documentation to refer to a function that has no return value, the protocols used to implement functions and commands are the same.

This section describes the protocols for registering UDFs, passing arguments to them, and returning values from them. Prototypes for the functions listed in this section can be included by using the **clips.h** header file.

## 8.1 User Defined Function Types

The interface between a function reference in CLIPS code and the C code which implements the function is handled by creating a function of type **UserDefinedFunction**:

typedef void UserDefinedFunction(\
Environment \*env,\
UDFContext \*udfc,\
UDFValue \*out);

typedef struct udfContext\
{\
void \*context;\
} UDFContext;

typedef struct udfValue\
{\
union\
{\
void \*value;\
TypeHeader \*header;\
CLIPSLexeme \*lexemeValue;\
CLIPSFloat \*floatValue;\
CLIPSInteger \*integerValue;\
CLIPSVoid \*voidValue;\
Multifield \*multifieldValue;\
Fact \*factValue;\
Instance \*instanceValue;\
CLIPSExternalAddress \*externalAddressValue;\
};\
size_t begin;\
size_t range;\
} UDFValue;

A **UserDefinedFunction** is passed three parameters: **env** is a pointer to the **Environment** in which the UDF is executed; **udfc** is a pointer to a **UDFContext**; and **out** is a pointer to a **UDFValue**.

The **UDFContext** type contains the public field **context**, a pointer to user data supplied when the UDF is registered, as well as several private fields used to track UDF argument requests (through the **udfc** parameter value).

The **UDFValue** type is used both for returning a value from a UDF (through the **out** parameter value) as well as requesting argument values passed to the UDF. The **UDFValue** type is similar to the **CLIPSValue** type, but also includes **begin** and **range** fields. These fields allow you to manipulate multifield values within a UDF without creating a new multifield. The **begin** field represents the starting position and the **range** field represents the number of values within a multifield. For example, if a UDFValue contained the multifield (a b c d), setting the **begin** field to 1 and the **range** field to 2 would change the UDFValue to the multifield (b c).

## 8.2 Registering User Defined Functions

AddUDFError AddUDF(\
Environment \*env,\
const char \*clipsName,\
const char \*returnTypes,\
unsigned short minArgs,\
unsigned short maxArgs,\
const char \*argTypes,\
UserDefinedFunction \*cfp,\
const char \*cName,\
void \*context);

typedef enum\
{\
AUE_NO_ERROR,\
AUE_MIN_EXCEEDS_MAX_ERROR,\
AUE_FUNCTION_NAME_IN_USE_ERROR,\
AUE_INVALID_ARGUMENT_TYPE_ERROR,\
AUE_INVALID_RETURN_TYPE_ERROR\
} AddUDFError;

UDFs must be registered with CLIPS using the function **AddUDF** before they can be referenced from CLIPS code. Calls to **AddUDF** can be made in the function **UserFunctions**[]{.indexref entry="UserFunctions"} contained in the CLIPS **userfunctions.c** file. Within **UserFunctions**, a call should be made for every function which is to be integrated with CLIPS. The user's source code then can be compiled and linked with CLIPS. Alternately, the user can call **AddUDF** from their own initialization code---the only restrictions is that it must be called after CLIPS has been initialized and before the UDF is referenced.

Parameter **env** is a pointer to a previously defined environment; parameter **clipsName** is the name associated with the UDF when it is called from within CLIPS; parameter **returnsTypes** is a string containing character codes indicating the CLIPS types returned by the UDF; parameter **minArgs** is the minimum number of arguments that must be passed to the UDF; parameter **maxArgs** is the maximum number of arguments that may be passed to the UDF; parameter **argTypes** is a string containing one or more groups of character codes specifying the allowed types for arguments; parameter **cfp** is a pointer to a function of type **UserDefinedFunction** to be invoked by CLIPS; parameter **cName** is the name of the UDF as specified in the C source code; and parameter **context** is a user supplied pointer to data that is passed to the UDF when it is invoked through the **UDFContext** paramter. The error codes for this function are:

  --------------------------------------- ----------------------------------------------------------------------------------
  **Error Code**                          **Meaning**

  AUE_NO_ERROR                            No error occurred.

  AUE_MIN_EXCEEDS_MAX_ERROR               The minimum number of arguments is greater than the maximum number of arguments.

  AUE_FUNCTION_NAME_IN_USE_ERROR          The function name is already in use.

  AUE_INVALID_ARGUMENT_TYPE_ERROR         An invalid argument type was specified.

  AUE_INVALID_RETURN_TYPE_ERROR           An invalid return type was specified.
  --------------------------------------- ----------------------------------------------------------------------------------

If the **returnTypes** parameter value is a null pointer, then CLIPS assumes that the UDF can return any valid type. Specifying one or more type character codes, however, allows CLIPS to detect errors when the return value of a UDF is used as a parameter value to a function that specifies the types allowed for that parameter. The following codes are supported for return values and argument types:

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

One or more characters can be specified. For example, \"l\" indicates the UDF returns an integer; \"ld\" indicates the UDF returns an integer or float; and \"syn\" indicates the UDF returns a symbol, string, or instance name.

The **minArgs** and **maxArgs** parameter values can be specified as the constant **UNBOUNDED** to indicate that there is no restriction on the minimum or maximum number of arguments.

If the **argTypes** parameter value is a null pointer, then there are no argument type restrictions. One or more character argument types can also be specified, separated by semicolons. The first type specified is the default type (used when no other type is specified for an argument), followed by types for specific arguments. For example, \"ld\" indicates that the default argument type is an integer or float; \"ld;s\" indicates that the default argument type is an integer or float, and the first argument must be a string; \"\*;;m\" indicates that the default argument type is any type, and the second argument must be a multifield; \";sy;ld\" indicates that the default argument type is any type, the first argument must be a string or symbol; and the second argument type must be an integer or float.

User‑defined functions can't using the same name as an existing system functions. The error code **AUE_FUNCTION_NAME_IN_USE_ERROR** will be returned by **AddUDF** in this case. The **RemoveUDF** function can be used to remove an existing function in order to redefine it:

bool RemoveUDF(\
Environment \*env,\
const char \*clipsName);

## 8.3 Passing Arguments from CLIPS to User Defined Func­tions

Unlike a C function call, CLIPS does immediately evaluate all of the arguments in a function call and directly pass the resulting values to the C function implementating the UDF. Instead arguments are evaluated and supplied when requested through argument access functions.

CLIPS will generate an error and terminate the invocation of a UDF before it is called if the incorrect number of arguments is supplied (either there are fewer arguments than the minimum specified or more arguments than the maximum specified).

Several access functions are provided to retrieve arguments:

unsigned UDFArgumentCount(\
UDFContext \*udfc);

bool UDFFirstArgument(\
UDFContext \*udfc,\
unsigned expectedType,\
UDFValue \*out);

bool UDFNextArgument(\
UDFContext \*udfc,\
unsigned expectedType,\
UDFValue \*out);

bool UDFNthArgument(\
UDFContext \*udfc,\
unsigned n,\
unsigned expectedType,\
UDFValue \*out);

bool UDFHasNextArgument(\
UDFContext \*udfc);

void UDFThrowError (\
UDFContext \*udfc);

void SetErrorValue (\
Environment \*theEnv,\
TypeHeader \*theValue);

The function **UDFArgumentCount** returns the number of arguments passed to the UDF. At the point the UDF is invoked, the argument count has been verified to fall within the range specified by the minimum and maximum number of arguments specified in the call to **AddUDF**. Thus a UDF should only need to check the argument count if the minimum and maximum number of arguments are not the same.

The function **UDFFirstArgument** retrieves the first argument passed to the UDF. Parameter **udfc** is a pointer to the UDFContext; parameter **expectedType** is a bit field containing the expcted types for the argument; and parameter **out** is a pointer to a UDFValue in which the retrieved argument value is stored. This function returns true if the argument was successfully retrieved and is the expected type; otherwise, it returns false.

The function **UDFNextArgument** retrieves the argument following the previously retrieved argument (either from **UDFFirstArgument**, **UDFNextArgument**, or **UDFNthArgument**). It retrieves the first argument if no arguments have been previously retrieved. Parameter **udfc** is a pointer to the UDFContext; parameter **expectedType** is a bit field containing the expcted types for the argument; and parameter **out** is a pointer to a UDFValue in which the retrieved argument value is stored. This function returns true if the argument was successfully retrieved and is the expected type; otherwise, it returns false.

The function **UDFNthArgument** retrieves a specific argument passed to the UDF. Parameter **udfc** is a pointer to the UDFContext; parameter **n** is the index of the argument to be retrieved (with indices starting at 1); parameter **expectedType** is a bit field containing the expcted types for the argument; and parameter **out** is a pointer to a UDFValue in which the retrieved argument value is stored. This function returns true if the argument was successfully retrieved and is the expected type; otherwise, it returns false.

The function **UDFHasNextArgument** returns true if there is an argument is available to be retrieved; otherwise, it returns false. The "next" argument is considered to be the first argument if no previous call to **UDFFirstArgument**, **UDFNextArgument**, or **UDFNthArgument** has been made; otherwise it is the next argument following the most recent call to one of those functions.

The function **UDFThrowError** can be used by a **UDF** to indicate that an error has occurred and execution should terminate.

The **SetErrorValue** function can be used to assign an error value which can be retrieved using the **get-error** and **set-error** CLIPS functions. This function can be used for situations where a function\'s return value can not be used to indicate an error and execution should not be terminated.

The functions **UDFFirstArgument**, **UDFNextArgument**, and **UDFNthArgument** use bit fields rather than character codes to indicate the types allowed for the **expectedType** parameter value. The following constants are defined for specifying bit codes:

  ------------------------------- --------------------------------------------------
         **Type Bit Code**        **Type**

             FLOAT_BIT            Float

            INTEGER_BIT           Integer

            SYMBOL_BIT            Symbol

            STRING_BIT            String

          MULTIFIELD_BIT          Multifield

       EXTERNAL_ADDRESS_BIT       External Address

         FACT_ADDRESS_BIT         Fact Address

       INSTANCE_ADDRESS_BIT       Instance Address

         INSTANCE_NAME_BIT        Instance Name

             VOID_BIT             Void

            BOOLEAN_BIT           Boolean

            NUMBER_BITS           Float, Integer

            LEXEME_BITS           Symbol, String

           ADDRESS_BITS           External Address, Fact Address, Instance Address

           INSTANCE_BITS          Instance Address, Instance Name

         SINGLEFIELD_BITS         Number, Lexeme, Address, Instance Name

           ANY_TYPE_BITS          Void, Singlefield, Multifield
  ------------------------------- --------------------------------------------------

These bit codes can be combined using the C \| operator. For example, the following code indicates that an argument should either be an integer or symbol:

INTEGER_BIT \| SYMBOL_BIT

## 8.4 Examples

### 8.4.1 Euler's Number

This example demonstrates returning a mathematical constant, Euler's number, from a user defined function.

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **e**; the return value type is a float; the UDF does not expect any arguments; and the C implementation of the UDF is the function **EulersNumber**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"e\",\"d\",0,0,NULL,EulersNumber,\"EulersNumber\",NULL);

}

The implementation of the CLIPS function **e** in the C function **EulersNumber** uses the function **CreateFloat** to create the return value. The C library function **exp** is used to calculate the value for Euler's number.

#include \<math.h\>

void EulersNumber(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

out-\>floatValue = CreateFloat(env,exp(1.0));

}

After creating a new executable including the UDF code, the function **e** can be invoked within CLIPS.

CLIPS\> **(e)**

2.71828182845905

CLIPS\>

### 8.4.2 Week Days Multifield Constant

This example demonstrates returning a multifield constant, the weekdays, from a user defined function.

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **weekdays**; the return value type is a multifield value; the UDF does not expect any arguments; and the C implementation of the UDF is the function **Weekdays**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"weekdays\",\"m\",0,0,NULL,Weekdays,\"Weekdays\",NULL);

}

The implementation of the CLIPS function **weekdays** in the C function **Weekdays** uses the function **StringToMultifield** to create the return value.

void Weekdays(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

out-\>multifieldValue =

StringToMultifield(env,\"Monday Tuesday Wednesday Thursday Friday\");

}

After creating a new executable including the UDF code, the function **week-days** can be invoked within CLIPS.

CLIPS\> **(weekdays)**

(Monday Tuesday Wednesday Thursday Friday)

CLIPS\>

### 8.4.3 Cubing a Number

This example demonstrates a user defined function that cubes a numeric argument value and returns either an integer or float depending upon the type of the argument value.

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **cube**; the return value type is an integer or float value; the UDF expects one argument that must be an integer or a float; and the C implementation of the UDF is the function **Cube**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"cube\",\"ld\",1,1,\"ld\",Cube,\"Cube\",NULL);

}

The implementation of the CLIPS function **cube** in the C function **Cube** uses the function **UDFFirstArgument** to retrieve the numeric argument passed to the function. If the argument value is an integer, the function **CreateInteger** is used to create the return value. If the argument value is a float, the function **CreateFloat** is used to create the return value.

void Cube(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

UDFValue theArg;

// Retrieve the first argument.

if (! UDFFirstArgument(udfc,NUMBER_BITS,&theArg))

{ return; }

// Cube the argument.

if (theArg.header-\>type == INTEGER_TYPE)

{

long long integerValue = theArg.integerValue-\>contents;

integerValue = integerValue \* integerValue \* integerValue;

out-\>integerValue = CreateInteger(env,integerValue);

}

else /\* the type must be FLOAT \*/

{

double floatValue = theArg.floatValue-\>contents;

floatValue = floatValue \* floatValue \* floatValue;

out-\>floatValue = CreateFloat(env,floatValue);

}

}

After creating a new executable including the UDF code, the function **cube** can be invoked within CLIPS.

CLIPS\> **(cube 3)**

27

CLIPS\> **(cube 3.5)**

42.875

CLIPS\>

### 8.4.4 Positive Number Predicate

This example demonstrates a user defined function that returns a boolean value indicating whether a numeric argument value is positive.

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **positivep**; the return value type is a boolean value (either the symbol TRUE or FALSE); the UDF expects one argument that must be an integer or a float; and the C implementation of the UDF is the function **Positivep**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"positivep\",\"b\",1,1,\"ld\",Positivep,\"Positivep\",NULL);

}

The implementation of the CLIPS function **positivep** in the C function **Positivep** uses the function **UDFFirstArgument** to retrieve the numeric argument passed to the function. The function **CreateBoolean** is used to create the return value.

void Positivep(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

UDFValue theArg;

bool b;

// Retrieve the first argument.

if (! UDFFirstArgument(udfc,NUMBER_BITS,&theArg))

{ return; }

// Determine if the value is positive.

if (theArg.header-\>type == INTEGER_TYPE)

{ b = (theArg.integerValue-\>contents \> 0); }

else /\* the type must be FLOAT \*/

{ b = (theArg.floatValue-\>contents \> 0.0); }

out-\>lexemeValue = CreateBoolean(env,b);

}

After creating a new executable including the UDF code, the function **positivep** can be invoked within CLIPS.

CLIPS\> **(positivep -3)**

FALSE

CLIPS\> **(positivep 4.5)**

TRUE

CLIPS\>

### 8.4.5 Exclusive Or

This example demonstrates a user defined function that returns a boolean value indicating whether an odd number of its arguments values are true (exclusive or).

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **xor**; the return value type is a boolean value (either the symbol TRUE or FALSE); the UDF expects at least two arguments; and the C implementation of the UDF is the function **Xor**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"xor\",\"b\",2,UNBOUNDED,NULL,Xor,\"Xor\",NULL);

}

The implementation of the CLIPS function **xor** in the C function **Xor** uses the functions **UDFHasNextArgument** and **UDFNextArgument** to retrieve the variable number of arguments passed to the function. Any value other than the symbol FALSE is considered to be "TRUE" by CLIPS, so when counting the number of argument values to be true, each argument is compared for inequality to the return value of the **FalseSymbol** function. Finally, the function **CreateBoolean** is used to create the return value.

void Xor(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

UDFValue theArg;

int trueCount = 0;

while (UDFHasNextArgument(udfc))

{

UDFNextArgument(udfc,ANY_TYPE_BITS,&theArg);

if (theArg.value != FalseSymbol(env))

{ trueCount++; }

}

out-\>lexemeValue = CreateBoolean(env,trueCount % 2);

}

After creating a new executable including the UDF code, the function **xor** can be invoked within CLIPS.

CLIPS\> **(xor TRUE FALSE)**

TRUE

CLIPS\> **(xor FALSE FALSE)**

FALSE

CLIPS\> **(xor TRUE FALSE TRUE FALSE TRUE)**

TRUE

CLIPS\>

### 8.4.6 String Reversal

This example demonstrates a user defined function that reverses the characters in a CLIPS symbol, string, or instance name.

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **reverse**; the return value type is a string, symbol, or instance name; the UDF expects one argument that must be a string, symbol, or instance name; and the C implementation of the UDF is the function **Reverse**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"reverse\",\"syn\",1,1,\"syn\",Reverse,\"Reverse\",NULL);

}

The implementation of the CLIPS function **reverse** in the C function **Reverse** uses the function **UDFFirstArgument** to retrieve the lexeme argument (string, symbol, or instance name) passed to the function. The function **genalloc** is used to allocate temporary memory for reversing the order of characters in the string. Depending upon the argument value type, the function **CreateString**, **CreateSymbol**, or **CreateInstanceName** is used to create the return value. Finally, the function **genfree** is used to deallocate the temporary memory.

void Reverse(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

UDFValue theArg;

const char \*theString;

char \*tempString;

size_t length, i;

// Retrieve the first argument.

if (! UDFFirstArgument(udfc,LEXEME_BITS \| INSTANCE_NAME_BIT,&theArg))

{ return; }

theString = theArg.lexemeValue-\>contents;

// Allocate temporary space to store the reversed string.

length = strlen(theString);

tempString = (char \*) genalloc(env,length + 1);

// Reverse the string.

for (i = 0; i \< length; i++)

{ tempString\[length - (i + 1)\] = theString\[i\]; }

tempString\[length\] = \'\\0\';

// Set the return value before deallocating

// the temporary reversed string.

switch (theArg.header-\>type)

{

case STRING_TYPE:

out-\>lexemeValue = CreateString(env,tempString);

break;

case SYMBOL_TYPE:

out-\>lexemeValue = CreateSymbol(env,tempString);

break;

case INSTANCE_NAME_TYPE:

out-\>lexemeValue = CreateInstanceName(env,tempString);

break;

}

// Deallocate temporary space

genfree(env,tempString,length+1);

}

After creating a new executable including the UDF code, the function **reverse** can be invoked within CLIPS.

CLIPS\> **(reverse abcd)\**
dcba**\**
CLIPS\> **(reverse \"xyz\")\**
\"zyx\"**\**
CLIPS\> **(reverse \[ijk\])\**
\[kji\]**\**
CLIPS\>

### 8.4.7 Reversing the Values in a Multifield Value

This example demonstrates a user defined function that creates a multifield value comprised from its arguments values, but in reverse order.

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **reverse\$**; the return value type is a multifield value; the UDF expects any number of arguments; and the C implementation of the UDF is the function **ReverseMF**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"reverse\$\",\"m\",0,UNBOUNDED,NULL,ReverseMF,\"ReverseMF\",NULL);

}

The implementation of the CLIPS function **reverse\$** in the C function **ReverseMF** uses the functions **UDFArgumentCount** and **UDFNthArgument** to retrieve the function arguments in reverse order. A multifield builder is created using the function **CreateMultifieldBuilder**. Each function argument is appended to the multifield builder using the function **MBAppendUDFValue**. The return value is created using **MBCreate**. Finally, the multifield builder is deallocated using the function **MBDispose**.

void ReverseMF(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

UDFValue theArg;

MultifieldBuilder \*mb;

unsigned argCount;

// Create the multifield builder.

mb = CreateMultifieldBuilder(env,20);

// Iterate over the argument

// values in reverse order.

argCount = UDFArgumentCount(udfc);

for (unsigned i = argCount; i != 0; i\--)

{

// Append the Nth argument

// to the multifield builder

UDFNthArgument(udfc,i,ANY_TYPE_BITS,&theArg);

MBAppendUDFValue(mb,&theArg);

}

// Create the return value.

out-\>multifieldValue = MBCreate(mb);

// Dispose of the multifield value.

MBDispose(mb);

}

After creating a new executable including the UDF code, the function **reverse\$** can be invoked within CLIPS.

CLIPS\> **(reverse\$ 1 2 3)**

(3 2 1)

CLIPS\> (reverse\$ a 6 (create\$ 6.3 5.4) \"s\")

(\"s\" 6.3 5.4 6 a)\
CLIPS\>

### 8.4.8 Trimming a Multifield

This example demonstrates a user defined function that trims values from the beginning and end of a multifield value.

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **trim\$**; the return value type is a multifield value; the UDF expects three arguments (the default type is an integer and the first argument must be a multiefield value); and the C implementation of the UDF is the function **Trim**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"trim\$\",\"m\",3,3,\"l;m\",Trim,\"Trim\",NULL);

}

The implementation of the CLIPS function **trim\$** in the C function **Trim** uses the functions **UDFFirstArgument** and **UDFNextArgument** to retrieve arguments passed to the function. The first argument is a multifield value; and the second and third arguments are integers (the number of values to trim from the beginning and end of the multifield value). If the trim values are negative or exceed the number of values contained in the multifield, then the functions **PrintString** and **UDFThrowError** are used to indicate an error; otherwise the **begin** and **range** fields of the argument value stored in the return value parameter **out** are modified to trim the appropriate number of values from the beginning and end of the multifield.

void Trim(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

long long front, back;

UDFValue arg;

// Retrieve the arguments.

UDFFirstArgument(udfc,MULTIFIELD_BIT,out);

UDFNextArgument(udfc,INTEGER_BIT,&arg);

front = arg.integerValue-\>contents;

UDFNextArgument(udfc,INTEGER_BIT,&arg);

back = arg.integerValue-\>contents;

// Detect errors.

if ((front \< 0) \|\| (back \< 0))

{

Writeln(env,\"Trim\$ indices cannot be negative.\");

UDFThrowError(udfc);

return;

}

if ((front + back) \> (long long) out-\>multifieldValue-\>length)

{

Writeln(env,\"Trim\$ exceeds length of multifield.\");

UDFThrowError(udfc);

return;

};

// Adjust the begin and range.

out-\>begin += (size_t) front;

out-\>range -= (size_t) (front + back);

}

After creating a new executable including the UDF code, the function **trim\$** can be invoked within CLIPS.

CLIPS\> **(trim\$ (create\$ a b c d e f g) 1 2)**

(b c d e)

CLIPS\> **(trim\$ (create\$ a b c) -1 2)**

Trim\$ indices cannot be negative.

(a b c)

CLIPS\>

### 8.4.9 Removing Duplicates from a Multifield

This example demonstrates a user defined function that removes duplicate values from a multifield value.

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **compact\$**; the return value type is a multifield value; the UDF expects one argument that must be a multifield value; and the C implementation of the UDF is the function **Compact**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"compact\$\",\"m\",1,1,\"m\",Compact,\"Compact\",NULL);

}

The implementation of the CLIPS function **compact\$** in the C function **Compact** uses the function **UDFFirstArgument** to retrieve the multifield argument value passed to the function. A multifield builder is created using the function **CreateMultifieldBuilder**. The **begin** and **range** fields are used to iterate over the values of the multifield argument value. If the value is not contained within the multifield builder, then it is added using the **MBAppend** function. The return value of the function is created using the **MBCreate** function. Finally, the multifield builder is deallocated using the function **MBDispose**.

void Compact(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

UDFValue arg;

MultifieldBuilder \*mb;

size_t i, j;

// Retrieve the argument.

UDFFirstArgument(udfc,MULTIFIELD_BIT,&arg);

// Create the multifield builder.

mb = CreateMultifieldBuilder(env,20);

// Iterate over each value in the multifield

// and add it to the compacted multifield if

// it is not already present.

for (i = arg.begin; i \< (arg.begin + arg.range); i++)

{

// Look for the value in the multifield builder.

for (j = 0; j \< mb-\>length; j++)

{

if (arg.multifieldValue-\>contents\[i\].value == mb-\>contents\[j\].value)

{ break; }

}

// If the value wasn\'t found, add it.

if (j == mb-\>length)

{ MBAppend(mb,&arg.multifieldValue-\>contents\[i\]); }

}

// Create the return value.

out-\>multifieldValue = MBCreate(mb);

// Dispose of the multifield builder.

MBDispose(mb);

}

After creating a new executable including the UDF code, the function **compact\$** can be invoked within CLIPS.

CLIPS\> **(compact\$ (create\$ a b c))**

(a b c)

CLIPS\> **(compact\$ (create\$ a a b c b c d))**

(a b c d)

CLIPS\>

### 8.4.10 Prime Factors

This example demonstrates a user defined function that determines the prime factors of an integer.

The **AddUDF** function call required in **UserFunctions** specifies that the CLIPS function name is **prime-factors**; the return value type is an integer; the UDF expects one argument that must be an integer; and the C implementation of the UDF is the function **PrimeFactors**.

void UserFunctions(

Environment \*env)

{

AddUDF(env,\"prime-factors\",\"m\",1,1,\"l\",PrimeFactors,\"PrimeFactors\",NULL);

}

The implementation of the CLIPS function **prime-factors** in the C function **PrimeFactor** uses the function **UDFFirstArgument** to retrieve the integer argument value passed to the function. If the integer is less than 2, the return value is created using the function **EmptyMultifield** to indicate that there are no prime factors. Otherwise, a multifield builder is created using the function **CreateMultifieldBuilder**. A trial division algorithm is then used to determine the prime factors and, as each is found, it is added to the multifield builder using the **MBAppendInteger** function. The return value of the function is created using the **MBCreate** function. Finally, the multifield builder is deallocated using the function **MBDispose**.

#include \<math.h\>

void PrimeFactors(

Environment \*env,

UDFContext \*udfc,

UDFValue \*out)

{

UDFValue value;

long long num, p, upper;

MultifieldBuilder \*mb;

// Retrieve the integer argument.

UDFFirstArgument(udfc,INTEGER_BIT,&value);

num = value.integerValue-\>contents;

// Integers less than 2 don\'t have

// a prime factorization.

if (num \< 2)

{

out-\>multifieldValue = EmptyMultifield(env);

return;

}

// Create the multifield builder.

mb = CreateMultifieldBuilder(env,10);

// Determine the prime factors.

upper = (long long) sqrt(num);

for (p = 2; p \<= upper; p++)

{

if ((p \* p) \> num) break;

while ((num % p) == 0)

{

MBAppendInteger(mb,p);

num /= p;

}

}

if (num \> 1)

{ MBAppendInteger(mb,num); }

// Set the return value.

out-\>multifieldValue = MBCreate(mb);

// Dispose of the multifield builder.

MBDispose(mb);

}

After creating a new executable including the UDF code, the function **prime-factor** can be invoked within CLIPS.

CLIPS\> **(prime-factors 1)**

()

CLIPS\> **(prime-factors 3)**

\(3\)

CLIPS\> **(prime-factors 128)**

(2 2 2 2 2 2 2)

CLIPS\> **(prime-factors 5040)**

(2 2 2 2 3 3 5 7)

CLIPS\> **(prime-factors 1257383)**

(373 3371)

CLIPS\> **(prime-factors 6469693230)**

(2 3 5 7 11 13 17 19 23 29)

CLIPS\>
