# Section 6: Creating Primitive Values

Section 4 demonstrated how to examine primitive values returned by CLIPS. This section documents the API for dynamically creating primitive values.

## 6.1 Primitive Creation Functions

CLIPS uses hash tables to store all integer, float, symbol, string;, and instance name primitives. These hash tables are used to prevent the duplication of primitive values referenced multiple times. Attempting to create one of these primitives values that already exists returns a pointer to the existing data structure for that primitive value.

### 6.1.1 Creating CLIPS Symbol, Strings, and Instance Names

CLIPSLexeme \*CreateSymbol(\
Environment \*env,\
const char \*str);

CLIPSLexeme \*CreateString(\
Environment \*env,\
const char \*str);

CLIPSLexeme \*CreateInstanceName(\
Environment \*env,\
const char \*str);

CLIPSLexeme \*CreateBoolean(\
Environment \*env,\
bool b);

CLIPSLexeme \*FalseSymbol(\
Environment \*env);

CLIPSLexeme \*TrueSymbol(\
Environment \*env);

The functions **CreateSymbol**, **CreateString**, and **CreateInstanceName** create primitive values with **type** field values of SYMBOL_TYPE, STRING_TYPE, and INSTANCE_NAME_TYPE respectively. Parameter **env** is a pointer to a previously created environment; and parameter **str** is a pointer to a character array containing the text that will be assigned to the **contents** field of the CLIPS symbol, string, or instance name being created. The return value of these functions is a pointer to a **CLIPSLexeme** type.

The function **CreateBoolean** creates a primitive value with **type** field value of SYMBOL_TYPE. Parameter **env** is a pointer to a previously created environment. If parameter **b** is true, a pointer to the **CLIPSLexeme** for the symbol TRUE is returned; otherwise a pointer to the **CLIPSLexeme** for the symbol FALSE is returned.

The function **FalseSymbol** returns a pointer to the **CLIPSLexeme** for the symbol FALSE. The function **TrueSymbol** returns a pointer to the **CLIPSLexeme** for the symbol TRUE.

### 6.1.2 Creating CLIPS Integers

CLIPSInteger \*CreateInteger(\
Environment \*env,\
long long ll);

The function **CreateInteger** creates a primitive value with a **type** field value of INTEGER_TYPE. Parameter **env** is a pointer to a previously created environment; and parameter **ll** is the C integer value that will be assigned to the **contents** field of the CLIPS integer being created. The return value of this function is a pointer to a **CLIPSInteger** type.

### 6.1.3 Creating CLIPS Floats

CLIPSFloat \*CreateFloat(\
Environment \*theEnv,\
double dbl);

The function **CreateFloat** creates a primitive value with a **type** field value of FLOAT_TYPE. Parameter **env** is a pointer to a previously created environment; and parameter **dbl** is the C double value that will be assigned to the **contents** field of the CLIPS float being created. The return value of this function is a pointer to a **CLIPSFloat** type.

### 6.1.4 Creating Multifields

Multifield \*EmptyMultifield(\
Environment \*env);

Multifield \*StringToMultifield(\
Environment \*env,\
const char \*str);

MultifieldBuilder \*CreateMultifieldBuilder(\
Environment \*env,\
size_t capacity);

Multifield \*MBCreate(\
MultifieldBuilder \*mb);

void MBReset(\
MultifieldBuilder \*mb);

void MBDispose(\
MultifieldBuilder \*mb);

void MBAppend(\
MultifieldBuilder \*mb,\
CLIPSValue \*value);

void MBAppendUDFValue(\
MultifieldBuilder \*mb,\
UDFValue \*);

void MBAppendInteger(\
MultifieldBuilder \*mb,\
long long value);

void MBAppendFloat(\
MultifieldBuilder \*mb,\
double value);

void MBAppendSymbol(\
MultifieldBuilder \*mb,\
const char \*value);

void MBAppendString(\
MultifieldBuilder \*mb,\
const char \*value);

void MBAppendInstanceName(\
MultifieldBuilder \*mb,\
const char \*value);

void MBAppendCLIPSInteger(\
MultifieldBuilder \*mb,\
CLIPSInteger \*value);

void MBAppendCLIPSFloat(\
MultifieldBuilder \*mb,\
CLIPSFloat \*value);

void MBAppendCLIPSLexeme(\
MultifieldBuilder \*mb,\
CLIPSLexeme \*value);

void MBAppendFact(\
MultifieldBuilder \*mb,\
Fact \*value);

void MBAppendInstance(\
MultifieldBuilder \*mb,\
Instance \*value);

void MBAppendMultifield(\
MultifieldBuilder \*mb,\
Multifield \*value);

void MBAppendCLIPSExternalAddress(\
MultifieldBuilder \*mb,\
CLIPSExternalAddress \*value);

The function **EmptyMultifield** returns a multifield primitive value of length 0.

The function **StringToMultifield** parses and creates a **Multifield** value from the values contained in the parameter **str**. For example, if the **str** parameter value is \"1 4.5 c\", a multifield with three values---the integer **1**, the float **4.5**, and the symbol **c**---will be created.

The function **CreateMultifieldBuilder** creates and initializes a value of type **MultifieldBuilder**. Parameter **env** is a pointer to a previously created environment; and parameter **capacity** is the initial size of the array used by the **MultifieldBuilder** for constructing multifields. The initial size does not limit the maximum size of the multifield that can be created. The capacity of the **MultifieldBuilder** will be increased if the multifield size becomes larger than the initial capacity. If successful, this function returns a pointer of type **MultifieldBuilder \*** to identify the target of other functions accepting a **MultifieldBuilder** parameter; if any error occurs, a null pointer is returned.

The function **MBCreate** creates and returns a **Multifield** based on values appended to the **MultifieldBuilder** specified by parameter **mb**. The length of the **MultifieldBuilder** is reset to 0 after this function is called.

The function **MBReset** resets the **MultifieldBuilder** specified by parameter **mb** to its initial capacity. Any values previously appended are removed and the **length** of the **MultifieldBuilder** is set to 0.

The function **MBDispose** deallocates all memory associated with previously allocated **MultifieldBuilder** specified by parameter **mb**.

The functions MBAppend, MBAppendUDFValue, MBAppendInteger, MBAppendFloat, MBAppendSymbol, MBAppendString, MBAppendInstanceName, MBAppendCLIPSInteger, MBAppendCLIPSFloat, MBAppendCLIPSLexeme, MBAppendFact, MBAppendInstance, MBAppendMultifield, and MBAppendCLIPSExternalAddress append the parameter value to the end of the multifield being created by the MultifieldBuilder specified by parameter mb. When appending a multifield value using MBAppend, MBAppendUDFValue, or MBAppendMultifield, each individual value within the multifield is appended to the multifield being created rather than the multifield being nested within the multifield being created.

### 6.1.5 The Void Value

CLIPSVoid \*VoidConstant(\
Environment \*env);

The function **VoidConstant** returns a pointer to the CLIPS void primitive value.

### 6.1.6 Creating External Addresses

CLIPSExternalAddress \*CreateCExternalAddress(\
Environment \*theEnv,\
void \*ea);

Creates a CLIPS external address value from a C void pointer. Note that it is up to the user to make sure that external addresses remain valid within CLIPS.

## 6.2 Examples

### 6.2.1 StringToMultifield

This example illustrates how to create a multifield primitive value from a string.

#include \"clips.h\"

int main()

{

Environment \*env;

Multifield \*mf;

env = CreateEnvironment();

mf = StringToMultifield(env,\"\\\"abc\\\" 3 4.5\");

Write(env,\"Created multifield is \");

WriteMultifield(env,STDOUT,mf);

Write(env,\"\\n\");

DestroyEnvironment(env);

}

The resulting output is:

Created multifield is (\"abc\" 3 4.5)

### 6.2.2 MultifieldBuilder

This example demonstrates how to create multifield primitive values using a **MultifieldBuilder**:

#include \"clips.h\"

int main()

{

Environment \*env;

MultifieldBuilder \*mb;

Multifield \*mf;

env = CreateEnvironment();

mb = CreateMultifieldBuilder(env,10);

MBAppendString(mb,\"abc\");

MBAppendInt(mb,3);

MBAppendFloat(mb,4.5);

mf = MBCreate(mb);

Write(env,\"Created multifield is \");

WriteMultifield(env,STDOUT,mf);

Write(env,\"\\n\");

MBAppendSymbol(mb,\"def\");

MBAppendInstanceName(mb,\"i1\");

mf = MBCreate(mb);

Write(env,\"Created multifield is \");

WriteMultifield(env,STDOUT,mf);

Write(env,\"\\n\");

MBDispose(mb);

DestroyEnvironment(env);

}

The resulting output is:

Created multifield is (\"abc\" 3 4.5)

Created multifield is (def \[i1\])

#
