# Section 12: Embedding CLIPS

CLIPS was designed to be embedded within other programs. When CLIPS is used as an em­bedded application, the user must provide a main program. Calls to CLIPS are made like any other subroutine. To embed CLIPS, add the following include state­ments to the user's main program file:

#include \"clips.h\"

Most of the embedded API function calls require an environment pointer argument. Each environment represents a single instance of the CLIPS engine which can load and run a program. A program must create at least one environment in order to make embedded API calls. In many cases, the program's main function will create a single environment to be used as the argument for all embedded API calls. In other cases, such as creating shared libraries or DLLs, new instances of environments will be created as they are needed. New environments can be created by calling the function **CreateEnvironment** (see section 9).

To create an embedded program, compile and link all of the user's code with all CLIPS files *except* **main.c**. If a library is being created, it may be necessary to use different link options or compile and link "wrapper" source code with the CLIPS source files. Otherwise, the embedded program must provide a replacement main function for the one normally provided by CLIPS.

When running CLIPS as an embedded pro­gram, many of the capabilities available in the interactive interface (in addition to others) are available through function calls. The functions are documented in the following sec­tions. Prototypes for these functions can be included by using the **clips.h** header file.

## 12.1 Environment Functions

The following function calls control the CLIPS environment:

### 12.1.1 LoadFromString

bool LoadFromString(\
Environment \*env,\
const char \*str,\
size_t length);

The function **LoadFromString** loads a set of constructs from a string input source (much like the **Load** function only using a string for input rather than a file). Parameter **env** is a pointer to a previously created environment; parameter **str** is a string containing constructs; and parameter **length** is the maximum number of characters to be read from the input string. If the **length** parameter value is SIZE_MAX, then the **str** parameter value must be terminated by a null character; otherwise, the **length** parameter value indicates the maximum number characters that will be read from the **str** parameter value. This function returns true if no error occurred while loading constructs; otherwise, it returns false.

### 12.1.2 Clear Callback Functions

bool AddClearFunction(\
Environment \*env,\
const char \*name,\
VoidCallFunction \*f,\
int p,\
void \*context);

bool RemoveClearFunction(\
Environment \*env,\
const char \*name);

typedef void VoidCallFunction(\
Environment \*env,\
void \*context);

The function **AddClearFunction** adds a callback function to the list of functions invoked when the CLIPS **clear** command is executed. Parameter **env** is a pointer to a previously created environment; parameter **name** is a string that uniquely identifies the callback for removal using **RemoveClearFunction**; parameter **f** is a pointer to the callback function of type **VoidCallFunction**; parameter **p** is the priority of the callback function; and parameter **context** is a user supplied pointer to data that is passed to the callback function when it is invoked (a null pointer should be used if there is no data that needs to be passed to the callback function). The **priority** parameter determines the order in which the callback functions are invoked (higher priority items are called first); the values -2000 to 2000 are reserved for internal use by CLIPS. This function returns true if the callback function was successfully added; otherwise, it returns false.

The function **RemoveClearFunction** removes a callback function from the list of functions invoked when the CLIPS **clear** command is executed. Parameter **env** is a pointer to a previously created environment; and parameter **name** is the string used to identify the callback when it was added using **AddClearFunction**. The function returns true if the callback was successfully removed; otherwise, it returns false.

### 12.1.3 Periodic Callback Functions

bool AddPeriodicFunction(\
Environment \*env,\
const char \*name\
VoidCallFunction \*f,\
int p,\
void \*context);

bool RemovePeriodicFunction(\
Environment \*env,\
const char \*name);

typedef void VoidCallFunction(\
Environment \*env,\
void \*context);

The function **AddPeriodicFunction** adds a callback function to the list of functions invoked periodically when CLIPS is executing. Among other possible uses, this functionality allows event processing during execution when CLIPS is embedded within an application that must periodically perform tasks. Care should be taken not to use any operations in a periodic function which would affect CLIPS data structures constructively or destructively, i.e. CLIPS internals may be examined but not modified during a periodic callback.

Parameter **env** is a pointer to a previously created environment; parameter **name** is a string that uniquely identifies the callback for removal using **RemovePeriodicFunction**; parameter **f** is a pointer to the callback function of type **VoidCallFunction**; parameter **p** is the priority of the callback function; and parameter **context** is a user supplied pointer to data that is passed to the callback function when it is invoked (a null pointer should be used if there is no data that needs to be passed to the callback function). The **priority** parameter determines the order in which the callback functions are invoked (higher priority items are called first); the values -2000 to 2000 are reserved for internal use by CLIPS. This function returns true if the callback function was successfully added; otherwise, it returns false.

The function **RemovePeriodicFunction** removes a callback function from the list of functions invoked periodically when CLIPS is executing. Parameter **env** is a pointer to a previously created environment; and parameter **name** is the string used to identify the callback when it was added using **AddPeriodicFunction**. The function returns true if the callback was successfully removed; otherwise, it returns false.

### 12.1.4 Reset Callback Functions

bool AddResetFunction(\
Environment \*env,\
const char \*name,\
VoidCallFunction \*f,\
int p,\
void \*context);

bool RemoveResetFunction(\
Environment \*env,\
const char \*name);

typedef void VoidCallFunction(\
Environment \*env,\
void \*context);

The function **AddResetFunction** adds a callback function to the list of functions invoked when the CLIPS **reset** command is executed. Parameter **env** is a pointer to a previously created environment; parameter **name** is a string that uniquely identifies the callback for removal using **RemoveResetFunction**; parameter **f** is a pointer to the callback function of type **VoidCallFunction**; parameter **p** is the priority of the callback function; and parameter **context** is a user supplied pointer to data that is passed to the callback function when it is invoked (a null pointer should be used if there is no data that needs to be passed to the callback function). The **priority** parameter determines the order in which the callback functions are invoked (higher priority items are called first); the values -2000 to 2000 are reserved for internal use by CLIPS. This function returns true if the callback function was successfully added; otherwise, it returns false.

The function **RemoveResetFunction** removes a callback function from the list of functions invoked when the CLIPS **reset** command is executed. Parameter **env** is a pointer to a previously created environment; and parameter **name** is the string used to identify the callback when it was added using **AddResetFunction**. The function returns true if the callback was successfully removed; otherwise, it returns false.

### 12.1.5 File Operations

bool BatchStar(\
Environment \*env\
const char \*fileName);

bool Bsave(\
Environment \*env,\
const char \*fileName);

bool Save(\
Environment \*env,\
const char \*fileName);

The function **BatchStar** is the C equivalent of the CLIPS **batch\*** command. The **env** parameter is a pointer to a previously created environment; the **filename** parameter is a full or partial path string to an ASCII or UTF-8 file containing CLIPS functions, commands, and constructs. This function returns true if the file was successfully opened; otherwise, it returns false.

The function **Bsave** is the C equivalent of the CLIPS **bsave** command. The **env** parameter is a pointer to a previously created environment; the **filename** parameter is a full or partial path string for the binary save file to be created. This function returns true if the file was successfully created; otherwise, it returns false.

The function **Save** is the C equivalent of the CLIPS **save** command. The **env** parameter is a pointer to a previously created environment; the **fileName** parameter is a full or partial path string for the text save file to be created. This function returns true if the file was successfully created; otherwise, it returns false.

### 12.1.6 Settings

bool GetDynamicConstraintChecking(\
Environment \*env);

bool GetSequenceOperatorRecognition(\
Environment \*env);

bool SetDynamicConstraintChecking(\
Environment \*env,\
bool b);

bool SetSequenceOperatorRecognition(\
Environment \*env,\
bool b);

The function **GetDynamicConstraintChecking** is the C equivalent of the CLIPS **get‑dynamic‑constraint‑checking** command. The **env** parameter is a pointer to a previously created environment. This function returns true if the dynamic constraint checking behavior is enabled; otherwise, it returns false.

The function **GetSequenceOperatorRecognition** is the C equivalent of the CLIPS **get-sequence-operator-recognition** command. Parameter **env** is a pointer to a previously created environment. This function returns true if the sequence operator recognition behavior is enabled; otherwise, it returns false.

The function **SetDynamicConstraintChecking** is the C equivalent of the CLIPS command **set‑dynamic‑constraint-checking**. The **env** parameter is a pointer to a previously created environment; the **b** parameter is the new setting for the behavior (either true to enable it or false to disable it). This function returns the old setting for the behavior.

The function **SetSequenceOperatorRecognition** is the C equivalent of the CLIPS **set-sequence-operator-recognition** command. Parameter **env** is a pointer to a previously created environment; and parameter **b** is the new setting for the behavior (either true to enable it or false to disable it). This function returns the old setting for the behavior.

## 12.2 Debugging Functions

The following function call controls the CLIPS debugging aids:

### 12.2.1 DribbleActive

bool DribbleActive(\
Environment \*env);

The function **DribbleActive** returns true if the environment specified by parameter **env** has an active dribble file for capturing output; otherwise, it returns false.

### 12.2.2 GetWatchState and SetWatchState

bool GetWatchState(\
Environment \*env,\
WatchItem item);

void SetWatchState(\
Environment \*env,\
WatchItem item,\
bool b);

typedef enum\
{\
ALL,\
FACTS,\
INSTANCES,\
SLOTS,\
RULES,\
ACTIVATIONS,\
MESSAGES,\
MESSAGE_HANDLERS,\
GENERIC_FUNCTIONS,\
METHODS,\
DEFFUNCTIONS,\
COMPILATIONS,\
STATISTICS,\
GLOBALS,\
FOCUS\
} WatchItem;

The function **GetWatchState** returns the current state of the watch item specified by the parameter **item** in the environment specified by the parameter **env**: true if the watch item is enabled; otherwise, false. If ALL is specified for the parameter **item**, the return value of this function is undefined.

The function **SetWatchState** sets the state of the watch item specified by the parameter **item** in the environment specified by the parameter **env**. If parameter **b** is true, the watch item is enabled; otherwise, it is disabled. If ALL is specified for the parameter **item**, then all watch items are set to the state specified by parameter **b**.

## 12.3 Deftemplate Functions

The following function calls are used for manipulating deftemplates.

### 12.3.1 Search, Iteration, and Listing

Deftemplate \*FindDeftemplate(\
Environment \*env,\
const char \*name);

Deftemplate \*GetNextDeftemplate(\
Environment \*env,\
Deftemplate \*d);

void GetDeftemplateList(\
Environment \*env,\
CLIPSValue \*out,\
Defmodule \*d);

void ListDeftemplates(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

The function **FindDeftemplate** searches for the deftemplate specified by parameter **name** in the environment specified by parameter **env**. This function returns a pointer to the named deftemplate if it exists; otherwise, it returns a null pointer.

The function **GetNextDeftemplate** provides iteration support for the list of deftemplates in the current module. If parameter **d** is a null pointer, then a pointer to the first **Deftemplate** in the current module is returned by this function; otherwise, a pointer to the next **Deftemplate** following the **Deftemplate** specified by parameter **d** is returned. If parameter **d** is the last **Deftemplate** in the current module, a null pointer is returned.

The function **GetDeftemplateList** is the C equivalent of the CLIPS **get-deftemplate-list** function. Parameter **env** is a pointer to a previously created environment; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **d** is a pointer to a **Defmodule**. The output of the function call---a multifield containing a list of deftemplate names---is stored in the **out** parameter value. If parameter **d** is a null pointer, then deftemplates in all modules will be included in parameter **out**; otherwise, only deftemplates in the specified module will be included.

The function **ListDeftemplates** is the C equivalent of the CLIPS **list‑deftemplates** command). Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the router output destination; and parameter **d** is a pointer to a defmodule. If parameter **d** is a null pointer, then deftemplates in all modules will be listed; otherwise, only deftemplates in the specified module will be listed.

### 12.3.2 Attributes

const char \*DeftemplateModule(\
Deftemplate \*d);

const char \*DeftemplateName(\
Deftemplate \*d);

const char \*DeftemplatePPForm(\
Deftemplate \*d);

void DeftemplateSlotNames(\
Deftemplate \*d,\
CLIPSValue \*out);

The function **DeftemplateModule** is the C equivalent of the CLIPS **deftemplate-module** command. The return value of this function is the name of the module in which the deftemplate specified by parameter **d** is defined.

The function **DeftemplateName** returns the name of the deftemplate specified by the **d** parameter.

The function **DeftemplatePPForm** returns the text representation of the **Deftemplate** specified by the **d** parameter. The null pointer is returned if the text representation is not available.

The function **DeftemplateSlotNames** is the C equivalent of the CLIPS **deftemplate-slot-names** function. Parameter **d** is a pointer to a **Deftemplate**; and parameter **out** is a pointer to a **CLIPSValue** allocated by the caller. The output of the function call---a multifield containing the deftemplate's slot names---is stored in the **out** parameter value. For implied deftemplates, a multifield value containing the single symbol *implied* is returned.

### 12.3.3 Deletion

bool DeftemplateIsDeletable(\
Deftemplate \*d);

bool Undeftemplate(\
Deftemplate \*d,\
Environment \*env);

The function **DeftemplateIsDeletable** returns true if the deftemplate specified by parameter **d** can be deleted; otherwise it returns false.

The **Undeftemplate** function is the C equivalent of the CLIPS **undeftemplate** command. It deletes the deftemplate specified by parameter **d**; or if parameter **d** is a null pointer, it deletes all deftemplates in the environment specified by parameter **env**. This function returns true if the deletion is successful; otherwise, it returns false.

### 12.3.4 Watching Deftemplate Facts

bool DeftemplateGetWatch(\
Deftemplate \*d);

void DeftemplateSetWatch(\
Deftemplate \*d,\
bool b);

The function **DeftemplateGetWatch** returns true if facts are being watched for the deftemplate specified by the **d** parameter value; otherwise, it returns false.

The function **DeftemplateSetWatch** sets the fact watch state for the deftemplate specified by the **d** parameter value to the value specified by the parameter **b**.

### 12.3.5 Slot Attributes

bool DeftemplateSlotAllowedValues(\
Deftemplate \*d,\
const char \*name,\
CLIPSValue \*out);

bool DeftemplateSlotCardinality(\
Deftemplate \*d,\
const char \*name,\
CLIPSValue \*out);

bool DeftemplateSlotRange(\
Deftemplate \*d,\
const char \*name,\
CLIPSValue \*out);

bool DeftemplateSlotDefaultValue(\
Deftemplate \*d,\
const char \*name,\
CLIPSValue \*out);

bool DeftemplateSlotTypes(\
Deftemplate \*d,\
const char \*name,\
CLIPSValue \*out);

The function **DeftemplateSlotAllowedValues** is the C equivalent of the CLIPS **deftemplate-slot‑allowed-values** function.

The function **DeftemplateSlotCardinality** is the C equivalent of the CLIPS **deftemplate-slot-cardinality** function.

The function **DeftemplateSlotRange** is the C equivalent of the CLIPS **deftemplate-slot‑range** function.

The function **DeftemplateSlotDefaultValue** is the C equivalent of the CLIPS **deftemplate-slot-default-value** function.

The function **DeftemplateSlotTypes** is the C equivalent of the CLIPS **deftemplate-slot-types** function.

Parameter **d** is a pointer to a **Deftemplate**; parameter **name** specifies a valid slot name for the specified deftemplate; and parameter **out** is a pointer to a **CLIPSValue** allocated by the caller. The output of the function call---a multifield containing the attribute values---is stored in the **out** parameter value. These function return true if a valid slot name was specified and the output value is successfully set; otherwise, false is returned.

### 12.3.6 Slot Predicates

bool DeftemplateSlotExistP(\
Deftemplate \*d,\
const char \*name);

bool DeftemplateSlotMultiP(\
Deftemplate \*d,\
const char \*name);

bool DeftemplateSlotSingleP(\
Deftemplate \*d,\
const char \*name);

DefaultType DeftemplateSlotDefaultP(\
Deftemplate \*deftemplatePtr,\
const char \*slotName);

typedef enum\
{\
NO_DEFAULT,\
STATIC_DEFAULT,\
DYNAMIC_DEFAULT\
} DefaultType;

The function **DeftemplateSlotExistp** is the C equivalent of the CLIPS **deftemplate-slot-existp** function. Parameter **d** is a pointer to a **Deftemplate**; and parameter **name** specifies a slot name. This function returns true if specified slot exists; otherwise it returns false.

The function **DeftemplateSlotMultiP** is the C equivalent of the CLIPS **deftemplate-slot-multip** function. Parameter **d** is a pointer to a **Deftemplate**; and parameter **name** specifies a valid slot name. This function returns true if the specified slot is a multifield slot; otherwise it returns false.

The function **DeftemplateSlotSingleP** is the C equivalent of the CLIPS **deftemplate-slot-singlep** function. Parameter **d** is a pointer to a **Deftemplate**; and parameter **name** specifies a valid slot name. This function returns true if the specified slot is a single-field slot; otherwise it returns false.

The function **DeftemplateSlotDefaultP** is the C equivalent of the CLIPS **deftemplate-slot-defaultp** function. Parameter **d** is a pointer to a **Deftemplate**; and parameter **name** specifies a valid slot name. This function returns the **DefaultType** enumeration for the specified slot.

## 12.4 Fact Functions

The following function calls manipulate and display information about facts.

### 12.4.1 Iteration and Listing

Fact \*GetNextFact(\
Environment \*env,\
Fact \*f);

Fact \*GetNextFactInTemplate(\
Deftemplate \*d,\
Fact \*f);

void GetFactList(\
Environment \*env,\
CLIPSValue \*out,\
Defmodule \*d);

void Facts(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d,\
long long start,\
long long end,\
long long max);

void PPFact(\
Fact \*f,\
const char \*logicalName,\
bool ignoreDefaults);

The function **GetNextFact** provides iteration support for the list of facts in an environment. If parameter **f** is a null pointer, then a pointer to the first **Fact** in the environment specified by parameter **env** is returned by this function; otherwise, a pointer to the next **Fact** following the **Fact** specified by parameter **f** is returned. If parameter **f** is the last **Fact** in the specified environment, a null pointer is returned.

The function **GetNextFactInTemplate** provides iteration support for the list of facts belonging to a deftemplate. If parameter **f** is a null pointer, then a pointer to the first **Fact** for the deftemplate specified by parameter **d** is returned by this function; otherwise, a pointer to the next **Fact** of the specified deftemplate following the **Fact** specified by parameter **f** is returned. If parameter **f** is the last **Fact** for the specified deftemplate, a null pointer is returned.

Do not call **GetNextFact** or **GetNextFactInTemplate** with a pointer to a fact that has been retracted. If the return value of these functions is stored as part of a persistent data structure or in a static data area, then the function **RetainFact** should be called to insure that the fact cannot be disposed while external references to the fact still exist.

The function **GetFactList** is the C equivalent of the CLIPS **get-fact-list** function. Parameter **env** is a pointer to a previously created environment; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **d** is a pointer to a **Defmodule**. The output of the function call---a multifield containing a list of fact addresses---is stored in the **out** parameter value. If parameter **d** is a null pointer, then all facts in all modules will be included in parameter **out**; otherwise, only facts associated with deftemplates in the specified module will be included.

The function **Facts** is the C equivalent of the CLIPS **facts** command. Parameter env is a pointer to a previously created environment; parameter **logicalName** is the router output destination; parameter **d** is a pointer to a **Defmodule**; parameter **start** is the lower fact index range of facts to be listed; parameter **end** is the upper fact index range of facts to be listed; and parameter **max** is the maximum number of facts to be listed. If parameter **d** is a non-null pointer, then only facts visible to the specified module are printed; otherwise, all facts will be printed. A value of -1 for the **start**, **end**, or **max** parameter indicates the parameter is unspecified and should not restrict the facts that are listed.

The function **PPFact** is the C equivalent of the CLIPS **ppfact** command. Parameter **f** is a pointer to the **Fact** to be displayed; parameter **logicalName** is the router output destination; and parameter **ignoreDefaults** is a boolean flag indicating whether slots should be excluded from display if their current value is the same as their static default value.

### 12.4.2 Attributes

Deftemplate \*FactDeftemplate(\
Fact \*f);

long long FactIndex(\
Fact \*f);

void FactPPForm(\
Fact \*f,\
StringBuilder \*sb,\
bool ignoreDefaults);

void FactSlotNames(\
Fact \*f,\
CLIPSValue \*out);

GetSlotError GetFactSlot(\
Fact \*f,\
const char \*name,\
CLIPSValue \*out);

typedef enum\
{\
GSE_NO_ERROR,\
GSE_NULL_POINTER_ERROR,\
GSE_INVALID_TARGET_ERROR,\
GSE_SLOT_NOT_FOUND_ERROR,\
} GetSlotError;

The function **FactDeftemplateModule** returns a pointer to the **Deftemplate** associated with the **Fact** specified by parameter **f**.

The function **FactIndex** is the C equivalent of the CLIPS **fact-index** command. It returns the fact-index of the fact specified by parameter **f**.

The function **FactPPForm** stores the text representation of the **Fact** specified by the **f** parameter in the **StringBuilder** specified by parameter **sb**. The parameter **ignoreDefaults** is a boolean flag indicating whether slots should be excluded from display if their current value is the same as their static default value

The function **FactSlotNames** is the C equivalent of the CLIPS **fact-slot-names** function. Parameter **f** is a pointer to a **Fact**; and parameter **out** is a pointer to a **CLIPSValue** allocated by the caller. The output of the function call---a multifield containing the facts's slot names---is stored in the **out** parameter value. For ordered facts, a multifield value containing the single symbol *implied* is returned.

The function **GetFactSlot** retrieves the slot value specified by parameter **name** from the fact specified by parameter **f** and stores it in parameter **out**, a **CLIPSValue** allocated by the caller. For ordered facts---which have an implied multifield slot---a null pointer or the string \"implied\" should be used for the **name** parameter value. The error codes for this function are:

  --------------------------------- ------------------------------------------------------------------------------------------------------------------------------
  **Error Code**                    **Meaning**

  GSE_NO_ERROR                      No error occurred.

  GSE_NULL_POINTER_ERROR            One of the function arguments was a NULL pointers (except for the **name** parameter which may be NULL for an ordered fact).

  GSE_INVALID_TARGET_ERROR          The fact specified by parameter **f** has been retracted.

  GSE_SLOT_NOT_FOUND_ERROR          The fact does not have the specified slot.
  --------------------------------- ------------------------------------------------------------------------------------------------------------------------------

### 12.4.3 Deletion

RetractError RetractAllFacts(\
Environment \*env);

bool FactExistp(\
Fact \*f);

The function **RetractAllFacts** retracts all of the facts in the environment specified by parameter **env**. It returns RE_NO_ERROR if all facts were successfully retracted. See the **Retract** command in section 3.3.3 for the list of error codes in the **RetractError** enumeration.

The function **FactExistp** is the C equivalent of the CLIPS **fact-existp** function. It returns true if the fact has not been retracted. The parameter **f** must be a **Fact** that has either not been retracted or has been retained (see section 5.2).

### 12.4.4 Settings

bool GetFactDuplication(\
Environment \*env);

bool SetFactDuplication(\
Environment \*env,\
bool b);

The function **GetFactDuplication** is the C equivalent of the CLIPS **get-fact-duplication** command. The **env** parameter is a pointer to a previously created environment. This function returns the boolean value corresponding to the current setting.

The function **SetFactDuplication** is the C equivalent of the CLIPS **set‑fact‑duplication** command. The **env** parameter is a pointer to a previously created environment; the parameter **b** is the new setting for the behavior. This function returns the old setting for the behavior.

### 12.4.5 Detecting Changes to Facts

bool GetFactListChanged(\
Environment \*env);

void SetFactListChanged(\
Environment \*env,\
bool b);

The function **GetFactsChanged** returns true if changes to facts for the environment specified by parameter **env** have occurred (either assertions, retractions, or modifications); otherwise, it returns false. To track future changes, **SetFactsChanged** should reset the change tracking value to false.

The function **SetFactsChanged** sets the facts change tracking value for the environment specified by the parameter **env** to the value specified by the parameter **b**.

## 12.5 Deffacts Functions

The following function calls are used for manipulating deffacts.

### 12.5.1 Search, Iteration, and Listing

Deffacts \*FindDeffacts(\
Environment \*env,\
const char \*name);

Deffacts \*GetNextDeffacts(\
Environment \*env,\
Deffacts \*d);

void GetDeffactsList(\
Environment \*env,\
CLIPSValue \*out,\
Defmodule \*d);

void ListDeffacts(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

The function **FindDeffacts** searches for the deffacts specified by parameter **name** in the environment specified by parameter **env**. This function returns a pointer to the named deffacts if it exists; otherwise, it returns a null pointer.

The function **GetNextDeffacts** provides iteration support for the list of deffacts in the current module. If parameter **d** is a null pointer, then a pointer to the first **Deffacts** in the current module is returned by this function; otherwise, a pointer to the next **Deffacts** following the **Deffacts** specified by parameter **d** is returned. If parameter **d** is the last **Deffacts** in the current module, a null pointer is returned.

The function **GetDeffactsList** is the C equivalent of the CLIPS **get-deffacts-list** function. Parameter **env** is a pointer to a previously created environment; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **d** is a pointer to a **Defmodule**. The output of the function call---a multifield containing a list of deffacts names---is stored in the **out** parameter value. If parameter **d** is a null pointer, then deffacts in all modules will be included in parameter **out**; otherwise, only deffacts in the specified module will be included.

The function **ListDeffacts** is the C equivalent of the CLIPS **list‑deffacts** command. Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the router output destination; and parameter **d** is a pointer to a defmodule. If parameter **d** is a null pointer, then deffacts in all modules will be listed; otherwise, only deffacts in the specified module will be listed.

### 12.5.2 Attributes

const char \*DeffactsModule(\
Deffacts \*d);

const char \*DeffactsName(\
Deffacts \*d);

const char \*DeffactsPPForm(\
Deffacts \*d);

The function **DeffactsModule** is the C equivalent of the CLIPS **deffacts-module** function. The return value of this function is the name of the module in which the deffacts specified by parameter **d** is defined.

The function **DeffactsName** returns the name of the deffacts specified by the **d** parameter.

The function **DeffactsPPForm** returns the text representation of the **Deffacts** specified by the **d** parameter. The null pointer is returned if the text representation is not available.

### 12.5.3 Deletion

bool DeffactsIsDeletable(\
Deffacts \*d);

bool Undeffacts(\
Deffacts \*d,\
Environment \*env);

The function **DeffactsIsDeletable** returns true if the deffacts specified by parameter **d** can be deleted; otherwise it returns false.

The **Undeffacts** function is the C equivalent of the CLIPS **undeffacts** command. It deletes the deffacts specified by parameter **d**; or if parameter **d** is a null pointer, it deletes all deffacts in the environment specified by parameter **env**. This function returns true if the deletion is successful; otherwise, it returns false.

## 12.6 Defrule Functions

The following function calls are used for manipulating defrules.

### 12.6.1 Search, Iteration, and Listing

Defrule \*FindDefrule(\
Environment \*env,\
const char \*name);

Defrule \*GetNextDefrule(\
Environment \*env,\
Defrule \*d);

void GetDefruleList(\
Environment \*env,\
CLIPSValue \*out,\
Defmodule \*d);

void ListDefrules(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

The function **FindDefrule** searches for the defrule specified by the **name** parameter in the environment specified by the **env** parameter. This function returns a pointer to the named defrule if it exists; otherwise, it returns a null pointer.

The function **GetNextDefrule** provides iteration support for the list of defrules in the current module. If the **d** parameter value is a null pointer, then a pointer to the first **Defrule** in the current module is returned by this function; otherwise, the next **Defrule** following the **d** parameter value is returned. If the **d** parameter is the last **Defrule** in the current module, a null pointer is returned.

The function **GetDefruleList** is the C equivalent of the CLIPS **get-defrule-list** function. The **env** parameter is a pointer to a previously created environment; the **out** parameter is a pointer to a **CLIPSValue** allocated by the caller; and the **d** parameter is a pointer to a **Defmodule**. The output of the function call---a multifield containing a list of defrule names---is stored in the **out** parameter value. If the parameter **d** is a null pointer, then defrules in all modules will be included in the out parameter value; otherwise, only defrules in the specified module will be included.

The function **ListDefrules** is the C equivalent of the CLIPS **list‑defrules** command. The **env** parameter is a pointer to a previously created environment; the **logicalName** parameter is the router output destination; and the **d** parameter is a pointer to a defmodule. If the parameter **d** is a null pointer, then defrules in all modules will be listed; otherwise, only defrules in the specified module will be listed.

### 12.6.2 Attributes

const char \*DefruleModule(\
Defrule \*d);

const char \*DefruleName(\
Defrule \*d);

const char \*DefrulePPForm(\
Defrule \*d);

The function **DefruleModule** is the C equivalent of the CLIPS **defrule-module** command). The return value of this function is the name of the module in which the **Defrule** specified by the **d** parameter is defined.

The function **DefruleName** returns the name of the **Defrule** specified by the **d** parameter.

The function **DefrulePPForm** returns the text representation of the **Defrule** specified by the **d** parameter. The null pointer is returned if the text representation is not available.

### 12.6.3 Deletion

bool DefruleIsDeletable(\
Defrule \*d);

bool Undefrule(\
Defrule \*d,\
Environment \*env);

The function **DefruleIsDeletable** returns true if the **Defrule** specified by the **d** parameter value can be deleted; otherwise it returns false.

The function **Undefrule** is the C equivalent of the CLIPS **undefrule** command. It deletes the defrule specified by the **d** parameter; or if the **d** parameter is a null pointer, it deletes all defrules in the environment specified by the **env** parameter. The function returns true if the deletion was successful; otherwise, it returns false.

### 12.6.4 Watch Activations and Firings

bool DefruleGetWatchActivations(\
Defrule \*d);

bool DefruleGetWatchFirings(\
Defrule \*d);

void DefruleSetWatchActivations(\
Defrule \*d,\
bool b);

void DefruleSetWatchFirings(\
Defrule \*d,\
bool b);

The function **DefruleGetWatchActivations** returns true if rule activations are being watched for the defrule specified by the **d** parameter value; otherwise, it returns false.

The function **DefruleGetWatchFirings** returns true if rule firings are being watched for the **Defrule** specified by the **d** parameter; otherwise, it returns false.

The function **DefruleSetWatchActivations** sets the rule activations watch state for the defrule specified by the **d** parameter value to the value specified by the parameter **b**.

The function **DefruleSetWatchFirings** sets the rule firings watch state for the defrule specified by the **d** parameter value to the value specified by the parameter **b**.

### 12.6.5 Breakpoints

bool DefruleHasBreakpoint(\
Defrule \*d);

bool RemoveBreak(\
Defrule \*d);

void SetBreak(\
Defrule \*d);

void ShowBreaks(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

The function **DefruleHasBreakpoint** returns true if the defrule specified by the **d** parameter value has a breakpoint set; otherwise it returns false.

The function **RemoveBreak** is the C equivalent of the CLIPS **remove-break** command. It returns false if a breakpoint does not exist for the defrule specified by the **d** parameter value; otherwise, it removes the breakpoint and returns true;

The function **SetBreak** is the C equivalent of the CLIPS **set-break** command. It sets a breakpoint for the defrule specified by the **d** parameter value.

The function **ShowBreaks** is the C equivalent of the CLIPS **show-breaks** command. The **env** parameter is a pointer to a previously created environment; the **logicalName** parameter is the router output destination; and the **d** parameter is a pointer to a defmodule. If the parameter **d** is a null pointer, then breakpoints for defrules in all modules will be listed; otherwise, only breakpoints for defrules in the specified module will be listed.

### 12.6.6 Matches

void Matches(\
Defrule \*d,\
Verbosity v,\
CLIPSValue \*out);

typedef enum\
{\
VERBOSE,\
SUCCINCT,\
TERSE\
} Verbosity;

The function **Matches** is the C equivalent of the CLIPS **matches** command. The **d** parameter is a pointer to a **Defrule**; the **v** parameter specifies the level of information displayed in the printed output; and the **out** parameter is a pointer to a CLIPSValue allocated by the caller. The output of the function call---a multifield containing three integer fields indicating the number of pattern matches, partial matches, and activations---is stored in the **out** parameter value.

### 12.6.7 Refresh

void Refresh(\
Defrule \*d);

The function **Refresh** is the C equivalent of the CLIPS **refresh** command.

## 12.7 Agenda Functions

The following function calls are used for manipulating the agenda.

### 12.7.1 Iteration and Listing

Activation \*GetNextActivation(\
Environment \*env,\
Activation \*a);

FocalModule \*GetNextFocus(\
Environment \*env,\
FocalModule \*fm);

void GetFocusStack(\
Environment \*env,\
CLIPSValue \*out);

void Agenda(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

void ListFocusStack(\
Environment \*env,\
const char \*logicalName);

The function **GetNextActivation** provides iteration support for the list of activations on the agenda of the current module in an environment. If parameter **a** is a null pointer, then a pointer to the first **Activation** on the agenda of the current module in the environment specified by parameter **env** is returned by this function; otherwise, a pointer to the next **Activation** following the **Activation** specified by parameter **a** is returned. If parameter **a** is the last **Activation** on the agenda of the current module in the specified environment, a null pointer is returned.

The function **GetNextFocus** provides iteration support for the list of modules on the focus stack of an environment. If parameter **fm** is a null pointer, then a pointer to the first **FocusModule** on the focus stack in the environment specified by parameter **env** is returned by this function; otherwise, a pointer to the next **FocusModule** following the **FocusModule** specified by parameter **fm** is returned. If parameter **fm** is the last **FocusModule** on the agenda of the current module in the specified environment, a null pointer is returned.

The function **GetFocusStack** is the C equivalent of the CLIPS **get-focus-stack** function. Parameter **env** is a pointer to a previously created environment; and parameter **out** is a pointer to a **CLIPSValue** allocated by the caller. The output of the function call---a multifield containing a list of defmodule names---is stored in the **out** parameter value.

The function **Agenda** is the C equivalent of the CLIPS **agenda** command. Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the router output destination; and parameter **d** is a pointer to a **Defmodule**. If parameter **d** is a null pointer, then the agenda of every module is listed; otherwise, only the agenda of the specified module is listed.

The function **ListFocusStack** is the C equivalent of the CLIPS **list-focus-stack** command. Parameter **env** is a pointer to a previously created environment; and parameter **logicalName** is the router output destination.

### 12.7.2 Activation Attributes

const char \*ActivationRuleName(\
Activation \*a);

void ActivationPPForm(\
Activation \*a,\
StringBuilder \*sb);

int ActivationGetSalience(\
Activation \*a);

int ActivationSetSalience(\
Activation \*a,\
int s);

The function **ActivationRuleName** returns the name of the defrule that generated the activation specified by parameter **a**.

The function **ActivationPPForm** stores the text representation of the **Activation** specified by parameter **a** in the **StringBuilder** specified by parameter **sb**.

The function **ActivationGetSalience** returns the salience of the activation specified by parameter **a**. This salience value may be different from the the salience value of the defrule which generated the activation (due to dynamic salience).

The function **ActivationSetSalience** sets the salience of the activation specified by parameter **a** to the integer specified by parameter **s**. Salience values greater than 10,000 will assign the value 10,000 instead and salience values less than -10,000 will assign the value -10 instead. The function **ReorderAgenda** should be called after salience values have been changed to update the agenda.

### 12.7.3 FocalModule Attributes

const char \*FocalModuleName(\
FocalModule \*fm);

Defmodule \*FocalModuleModule(\
FocalModule \*fm);

The function **FocalModuleName** returns the name of the defmodule associated with the **FocalModule** specified by parameter **fm**.

The function **FocalModuleModule** returns a pointer to the **Defmodule** associated with the **FocalModule** specified by parameter **fm**.

### 12.7.4 Rule Fired Callback Functions

bool AddBeforeRuleFiresFunction(\
Environment \*env,\
const char \*name,\
RuleFiredFunction \*f,\
int p,\
void \*context);

bool AddAfterRuleFiresFunction(\
Environment \*env,\
const char \*name,\
RuleFiredFunction \*f,\
int p,\
void \*context);

bool RemoveBeforeRuleFiresFunction(\
Environment \*env,\
const char \*name);

bool RemoveAfterRuleFiresFunction(\
Environment \*env,\
const char \*name);

typedef void RuleFiredFunction(\
Environment \*env,\
Activation \*a,\
void \*context);

The function **AddBeforeRuleFiresFunction** adds a callback function to the list of functions invoked after a rule executes. Parameter **env** is a pointer to a previously created environment; parameter **name** is a string that uniquely identifies the callback for removal using **RemoveBeforeRuleFiresFunction**; parameter **f** is a pointer to the callback function of type **RuleFiredFunction**; parameter **p** is the priority of the callback function; and parameter **context** is a user supplied pointer to data that is passed to the callback function when it is invoked (a null pointer should be used if there is no data that needs to be passed to the callback function). The **priority** parameter determines the order in which the callback functions are invoked (higher priority items are called first); the values -2000 to 2000 are reserved for internal use by CLIPS. This function returns true if the callback function was successfully added; otherwise, it returns false.

The function **AddAfterRuleFiresFunction** adds a callback function to the list of functions invoked after a rule executes. Parameter **env** is a pointer to a previously created environment; parameter **name** is a string that uniquely identifies the callback for removal using **RemoveAfterRuleFiresFunction**; parameter **f** is a pointer to the callback function of type **RuleFiredFunction**; parameter **p** is the priority of the callback function; and parameter **context** is a user supplied pointer to data that is passed to the callback function when it is invoked (a null pointer should be used if there is no data that needs to be passed to the callback function). The **priority** parameter determines the order in which the callback functions are invoked (higher priority items are called first); the values -2000 to 2000 are reserved for internal use by CLIPS. This function returns true if the callback function was successfully added; otherwise, it returns false.

When invoked, the **RuleFiredFunction** is passed parameter **a** that is a pointer to the **Activation** being executed. In the event that no rules are executed, the callbacks added by **AddAfterRuleFiresFunction** are invoked once with the parameter value **a** set to a null pointer.

The function **RemoveBeforeRuleFiresFunction** removes a callback function from the list of functions invoked before a rule executes. Parameter **env** is a pointer to a previously created environment; and parameter **name** is the string used to identify the callback when it was added using **AddBeforeRuleFiresFunction**. The function returns true if the callback was successfully removed; otherwise, it returns false.

The function **RemoveAfterRuleFiresFunction** removes a callback function from the list of functions invoked after a rule executes. Parameter **env** is a pointer to a previously created environment; and parameter **name** is the string used to identify the callback when it was added using **AddAfterRuleFiresFunction**. The function returns true if the callback was successfully removed; otherwise, it returns false.

### 12.7.6 Manipulating the Focus Stack

void ClearFocusStack(\
Environment \*env);

void Focus(\
Defmodule \*d);

Defmodule \*PopFocus(\
Environment \*env);

Defmodule \*GetFocus(\
Environment \*env);

The function **ClearFocusStack** is the C equivalent of the CLIPS **clear-focus-stack** command.

The function **Focus** is the C equivalent of the CLIPS **focus** command.

The function **PopFocus** is the C equivalent of the CLIPS **pop-focus** function. It removes the current focus from the focus stack and returns the **Defmodule** associated with that focus.

The function **GetFocus** is the C equivalent of the CLIPS **get-focus** function. It returns a pointer to the **Defmodule** that is the current focus on the focus stack. A null pointer is returned if the focus stack is empty.

### 12.7.7 Manipulating the Agenda

void RefreshAgenda(\
Defmodule \*d);

void RefreshAllAgendas(\
Environment \*env);

void ReorderAgenda(\
Defmodule \*d);

void ReorderAllAgendas(\
Environment \*env);

void DeleteActivation(\
Activation \*a);

void DeleteAllActivations(\
Defmodule \*d);

The function **RefreshAgenda** is the C equivalent of the CLIPS **refresh-agenda** command. For the agenda of the module specified by parameter **d**, it recomputes the salience values for all activations and then reorders the agenda.

The function **RefreshAllAgendas** invokes the **RefreshAgenda** function for every module in the evironment specified by parameter **env**.

The function **ReorderAgenda** reorders the agenda of the module specified by parameter **d** using the current conflict resolution strategy and current activation saliences.

The function **ReorderAllAgendas** invokes the **ReorderAgenda** function for every module in the evironment specified by parameter **env**.

The function **DeleteActivation** removes an activation from its agenda.

The function **DeleteAllActivations** removes all activations from the agenda of the module specified by parameter **d**;

### 12.7.8 Detecting Changes to the Agenda

bool GetAgendaChanged(\
Environment \*env);

void SetAgendaChanged(\
Environment \*env,\
bool b);

The function **GetAgendaChanged** returns true if changes to the agenda for the environment specified by parameter **env** have occurred (either activations, firings, or deactivations); otherwise, it returns false. To track future changes, **SetAgendaChanged** should reset the change tracking value to false.

The function **SetAgendaChanged** sets the agenda change tracking value for the environment specified by the parameter **env** to the value specified by the parameter **b**.

### 12.7.9 Settings

SalienceEvaluationType GetSalienceEvaluation(\
Environment \*env);

SalienceEvaluationType SetSalienceEvaluation(\
Environment \*env,\
SalienceEvaluationType set);

StrategyType GetStrategy(\
Environment \*env);

StrategyType SetStrategy(\
Environment \*env,\
StrategyType st);

typedef enum\
{\
WHEN_DEFINED,\
WHEN_ACTIVATED,\
EVERY_CYCLE\
} SalienceEvaluationType;

typedef enum\
{\
DEPTH_STRATEGY,\
BREADTH_STRATEGY,\
LEX_STRATEGY,\
MEA_STRATEGY,\
COMPLEXITY_STRATEGY,\
SIMPLICITY_STRATEGY,\
RANDOM_STRATEGY\
} StrategyType;

The function **GetSalienceEvaluation** is the C equivalent of the CLIPS **get-salience-evaluation** command. The **env** parameter is a pointer to a previously created environment. This function returns the enumeration value corresponding to the current setting.

The function **SetSalienceEvaluation** is the C equivalent of the CLIPS **set-salience-evaluation** command). The **env** parameter is a pointer to a previously created environment; and the parameter **set** is the new setting for the behavior. This function returns the old setting for the behavior.

The function **GetStrategy** is the C equivalent of the CLIPS **get-strategy** command. The **env** parameter is a pointer to a previously created environment. This function returns the enumeration value corresponding to the current setting.

The function **SetStrategy** is the C equivalent of the CLIPS **set-strategy** command. The **env** parameter is a pointer to a previously created environment; and the parameter **st** is the new setting for the behavior. This function returns the old setting for the behavior.

### 12.7.10 Examples

#### 12.7.10.1 Calling a Function After Each Rule Firing

The following code is a simple example that prints a period after each rule firing:

#include \"clips.h\"

void PrintPeriod(Environment \*,Activation \*,void \*);

int main()

{

Environment \*env;

env = CreateEnvironment();

Build(env,\"(defrule loop\"

\" ?f \<- (loop)\"

\" =\>\"

\" (retract ?f)\"

\" (assert (loop)))\");

AssertString(env,\"(loop)\");

AddAfterRuleFiresFunction(env,\"print-dot\",PrintPeriod,0,NULL);

Run(env,20);

Write(env,\"\\n\");

}

void PrintPeriod(

Environment \*env,

Activation \*a,

void \*context)

{

Write(env,\".\");

}

When run, the program produces the following output:

\...\...\...\...\...\.....

## 12.8 Defglobal Functions

The following function calls are used for manipulating defglobals.

### 12.8.1 Search, Iteration, and Listing

Defglobal \*FindDefglobal(\
Environment \*env,\
const char \*name);

Defglobal \*GetNextDefglobal(\
Environment \*env,\
Defglobal \*d);

void GetDefglobalList(\
Environment \*env,\
CLIPSValue \*out,\
Defmodule \*d);

void ListDefglobals(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

void ShowDefglobals(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

The function **FindDefglobal** searches for the defrule specified by the **name** parameter in the environment specified by the **env** parameter. For example, to retrieve the value of the global variable ?\*x\*, use the value \"x\" for the **name** parameter. This function returns a pointer to the named defglobal if it exists; otherwise, it returns a null pointer.

The function **GetNextDefglobal** provides iteration support for the list of defglobals in the current module. If parameter **d** is a null pointer, then a pointer to the first **Defglobal** in the current module is returned by this function; otherwise, a pointer to the next **Defglobal** following the **Defglobal** specified by parameter **d** is returned. If parameter **d** is the last **Defglobal** in the current module, a null pointer is returned.

The function **GetDefglobalList** is the C equivalent of the CLIPS **get-defglobal-list** function). The **env** parameter is a pointer to a previously created environment; the **out** parameter is a pointer to a **CLIPSValue** allocated by the caller; and the **d** parameter is a pointer to a **Defmodule**. The output of the function call---a multifield containing a list of defglobal names---is stored in the **out** parameter value. If the parameter **d** is a null pointer, then defglobals in all modules will be included in the out parameter value; otherwise, only defglobals in the specified module will be included.

The function **ListDefglobals** is the C equivalent of the CLIPS **list‑defglobals** command. The parameter **env** is a pointer to a previously created environment; the parameter **logicalName** is the router output destination; and the parameter **d** is a pointer to a defmodule. If the parameter **d** is a null pointer, then defglobals in all modules will be listed; otherwise, only defglobals in the specified module will be listed.

The function **ShowDefglobals** is the C equivalent of the CLIPS **show‑defglobals** command. The parameter **env** is a pointer to a previously created environment; the parameter **logicalName** is the router output destination; and the parameter **d** is a pointer to a defmodule. If the parameter **d** is a null pointer, then defglobals in all modules will be listed with their current value; otherwise, only defglobals in the specified module will be listed with their current value.

### 12.8.2 Attributes

const char \*DefglobalModule(\
Defglobal \*d);

const char \*DefglobalName(\
Defglobal \*d);

const char \*DefglobalPPForm(\
Defglobal \*d);

void DefglobalValueForm(\
Defglobal \*d,\
StringBuilder \*sb);

void DefglobalGetValue(\
Defglobal \*d,\
CLIPSValue \*out);

void DefglobalSetValue(\
Defglobal \*d,\
CLIPSValue \*value);

void DefglobalSetInteger (\
Defglobal \*d,\
long long value);

void DefglobalSetFloat (\
Defglobal \*d,\
double value);

void DefglobalSetSymbol (\
Defglobal \*d,\
const char \*value);

void DefglobalSetString (\
Defglobal \*d,\
const char \*value);

void DefglobalSetInstanceName (\
Defglobal \*d,\
const char \*value);

void DefglobalSetCLIPSInteger (\
Defglobal \*d,\
CLIPSInteger \*value);

void DefglobalSetCLIPSFloat (\
Defglobal \*d,\
CLIPSFloat \*value);

void DefglobalSetCLIPSLexeme (\
Defglobal \*d,\
CLIPSLexeme \*value);

void DefglobalSetFact (\
Defglobal \*d,\
Fact \*value);

void DefglobalSetInstance (\
Defglobal \*d,\
Instance \*value);

void DefglobalSetMultifield (\
Defglobal \*d,\
Multifield \*value);

void DefglobalSetCLIPSExternalAddress (\
Defglobal \*d,\
CLIPSExternalAddress \*value);

The function **DefglobalModule** is the C equivalent of the CLIPS **defglobal-module** command. The return value of this function is the name of the module in which the **Defglobal** specified by the **d** parameter is defined.

The function **DefglobalName** returns the name of the defglobal specified by parameter **d**.

The function **DefglobalPPForm** returns the text representation of the defglobal specified by parameter **d**. The null pointer is returned if the text representation is not available.

The function **DefglobalValueForm** returns a string representation of a defglobal and its current value. Parameter **d** is a pointer to a **Defglobal**; and parameter **sb** is a pointer to a **StringBuilder** allocated by the caller in which the representation is stored.

The function **DefglobalGetValue** returns the value of the defglobal specified by parameter **d** in parameter **out**, a **CLIPSValue** allocated by the caller.

The function **DefglobalSet...** functions set the value of the defglobal specified by parameter **d** to the value specified by parameter **value**, a **CLIPSValue** allocated by the caller. This function can trigger garbage collection.

### 12.8.3 Deletion

bool DefglobalIsDeletable(\
Defglobal \*d);

bool Undefglobal(\
Defglobal \*d,\
Environment \*env);

The function **DefglobalIsDeletable** returns true if the defglobal specified by parameter **d** can be deleted; otherwise it returns false.

The function **Undefglobal** is the C equivalent of the CLIPS **undefglobal** command. It deletes the defglobal specified by parameter **d**; or if parameter **d** is a null pointer, it deletes all defglobals in the environment specified by parameter **env**. The function returns true if the deletion was successful; otherwise, it returns false.

### 12.8.4 Watching and Detecting Changes to Defglobals

bool DefglobalGetWatch(\
Defglobal \*d);

void DefglobalSetWatch(\
Defglobal \*d,\
bool b);

bool GetGlobalsChanged(\
Environment \*env);

void SetGlobalsChanged(\
Environment \*env,\
bool b);

The function **DefglobalGetWatch** returns true if the defglobal specified by parameter **d** is being watched; otherwise, it returns false.

The function **DefglobalSetWatch** sets the watch state for the defglobal specified by parameter **d**. If parameter **b** is true, the watch state is enabled; otherwise, it is disabled.

The function **GetGlobalsChanged** returns true if changes to global variables for the environment specified by parameter **env** have occurred (either additions, deletions, or value modifications); otherwise, it returns false. To track future changes, **SetGlobalsChanged** should reset the change tracking value to false.

The function **SetGlobalsChanged** sets the global change tracking value for the environment specified by the parameter **env** to the value specified by the parameter **b**.

### 12.8.5 Reset Globals Behavior

bool GetResetGlobals(\
Environment \*env);

bool SetResetGlobals(\
Environment \*env,\
bool b);

The function **GetResetGlobals** is the C equivalent of the CLIPS **get‑reset‑globals** command. Parameter **env** is a pointer to a previously created environment. This function returns true if the behavior is enabled; otherwise, it returns false.

The function **SetResetGlobals** is the C equivalent of the CLIPS **set‑reset‑globals** command). Parameter **env** is a pointer to a previously created environment; and parameter **b** is the new setting for the behavior (either true to enable it or false to disable it). This function returns the old setting for the behavior.

### 12.8.6 Examples

#### 12.8.6.1 Listing, Watching, and Setting the Value of Defglobals

int main()

{

Environment \*env;

CLIPSValue value;

env = CreateEnvironment();

Build(env,\"(defglobal ?\*x\* = 3)\");

Build(env,\"(defglobal ?\*y\* = (create\$ a b c))\");

Write(env,\"Listing Globals:\\n\\n\");

ListDefglobals(env,STDOUT,NULL);

Write(env,\"\\nShowing Values:\\n\\n\");

ShowDefglobals(env,STDOUT,NULL);

Write(env,\"\\nSetting Values:\\n\\n\");

Watch(env,GLOBALS);

Eval(env,\"(\* 3 4)\",&value);

DefglobalSetValue(FindDefglobal(env,\"x\"),&value);

value.lexemeValue = CreateString(env,\"123 Main St.\");

DefglobalSetValue(FindDefglobal(env,\"y\"),&value);

DestroyEnvironment(env);

}

When run, the program produces the following output:

Listing Globals:

MAIN:

x

y

For a total of 2 defglobals.

Showing Values:

MAIN:

?\*x\* = 3

?\*y\* = (a b c)

Setting Values:

:== ?\*x\* ==\> 12 \<== 3

:== ?\*y\* ==\> \"123 Main St.\" \<== (a b c)

## 12.9 Deffunction Functions

The following function calls are used for manipulating deffunctions.

### 12.9.1 Search, Iteration, and Listing

Deffunction \*FindDeffunction(\
Environment \*env,\
const char \*name);

Deffunction \*GetNextDeffunction(\
Environment \*env,\
Deffunction \*d);

void GetDeffunctionList(\
Environment \*env,\
CLIPSValue \*out,\
Defmodule \*d);

void ListDeffunctions(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

The function **FindDeffunction** searches for the deffunction specified by parameter **name** in the environment specified by parameter **env**. This function returns a pointer to the named deffunction if it exists; otherwise, it returns a null pointer.

The function **GetNextDeffunction** provides iteration support for the list of deffunctions in the current module. If parameter **d** is a null pointer, then a pointer to the first **Deffunction** in the current module is returned by this function; otherwise, a pointer to the next **Deffunction** following the **Deffunction** specified by parameter **d** is returned. If parameter **d** is the last **Deffunction** in the current module, a null pointer is returned.

The function **GetDeffunctionList** is the C equivalent of the CLIPS **get-deffunction-list** function. Parameter **env** is a pointer to a previously created environment; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **d** is a pointer to a **Defmodule**. The output of the function call---a multifield containing a list of deffunction names---is stored in the **out** parameter value. If parameter **d** is a null pointer, then deffunctions in all modules will be included in parameter **out**; otherwise, only deffunctions in the specified module will be included.

The function **ListDeffunctions** is the C equivalent of the CLIPS **list‑deffunctions** command. Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the router output destination; and parameter **d** is a pointer to a defmodule. If parameter **d** is a null pointer, then deffunctions in all modules will be listed; otherwise, only deffunctions in the specified module will be listed.

### 12.9.2 Attributes

const char \*DeffunctionModule(\
Deffunction \*d);

const char \*DeffunctionName(\
Deffunction \*d);

const char \*DeffunctionPPForm(\
Deffunction \*d);

The function **DeffunctionModule** is the C equivalent of the CLIPS **deffunction-module** command. The return value of this function is the name of the module in which the deffunction specified by parameter **d** is defined.

The function **DeffunctionName** returns the name of the deffunction specified by the **d** parameter.

The function **DeffunctionPPForm** returns the text representation of the **Deffunction** specified by the **d** parameter. The null pointer is returned if the text representation is not available.

### 12.9.3 Deletion

bool DeffunctionIsDeletable(\
Deffunction \*d);

bool Undeffunction(\
Deffunction \*d,\
Environment \*env);

The function **DeffactsIsDeletable** returns true if the deffacts specified by parameter **d** can be deleted; otherwise it returns false.

The function **Undeffunction** is the C equivalent of the CLIPS **undeffunction** command). It deletes the deffacts specified by parameter **d**; or if parameter **d** is a null pointer, it deletes all deffacts in the environment specified by parameter **env**. This function returns true if the deletion is successful; otherwise, it returns false.

### 12.9.4 Watching Deffunctions

bool DeffunctionGetWatch(\
Deffunction \*d);

void DeffunctionSetWatch(\
Deffunction \*d,\
bool b);

The function **DeffunctionGetWatch** returns true if the watch state is enabled for the deffunction specified by the **d** parameter value; otherwise, it returns false.

The function **DeffunctionSetWatch** sets the watch state for the deffunction specified by the **d** parameter value to the value specified by the parameter **b**.

## 12.10 Defgeneric Functions

The following function calls are used for manipulating generic functions.

### 12.10.1 Search, Iteration, and Listing

Defgeneric \*FindDefgeneric(\
Environment \*env,\
const char \*name);

Defgeneric \*GetNextDefgeneric(\
Environment \*env,\
Defgeneric \*d);

void GetDefgenericList(\
Environment \*env,\
CLIPSValue \*out,\
Defmodule \*d);

void ListDefgenerics(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

The function **FindDefgeneric** searches for the defgeneric specified by parameter **name** in the environment specified by parameter **env**. This function returns a pointer to the named defgeneric if it exists; otherwise, it returns a null pointer.

The function **GetNextDefgeneric** provides iteration support for the list of defgenerics in the current module. If parameter **d** is a null pointer, then a pointer to the first **Defgeneric** in the current module is returned by this function; otherwise, a pointer to the next **Defgeneric** following the **Defgeneric** specified by parameter **d** is returned. If parameter **d** is the last **Defgeneric** in the current module, a null pointer is returned.

The function **GetDefgenericList** is the C equivalent of the CLIPS **get-defgeneric-list** function. Parameter **env** is a pointer to a previously created environment; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **d** is a pointer to a **Defmodule**. The output of the function call---a multifield containing a list of defgeneric names---is stored in the **out** parameter value. If parameter **d** is a null pointer, then defgenerics in all modules will be included in parameter **out**; otherwise, only defgenerics in the specified module will be included.

The function **ListDefgenerics** is the C equivalent of the CLIPS **list‑defgenerics** command). Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the router output destination; and parameter **d** is a pointer to a defmodule. If parameter **d** is a null pointer, then defgenerics in all modules will be listed; otherwise, only defgenerics in the specified module will be listed.

### 12.10.2 Attributes

const char \*DefgenericModule(\
Defgeneric \*d);

const char \*DefgenericName(\
Defgeneric \*d);

const char \*DefgenericPPForm(\
Defgeneric \*d);

The function **DefgenericModule** is the C equivalent of the CLIPS **defgeneric-module** command. The return value of this function is the name of the module in which the defgeneric specified by parameter **d** is defined.

The function **DefgenericName** returns the name of the defgeneric specified by the **d** parameter.

The function **DefgenericPPForm** returns the text representation of the **Defgeneric** specified by the **d** parameter. The null pointer is returned if the text representation is not available.

### 12.10.3 Deletion

bool DefgenericIsDeletable(\
Defgeneric \*d);

bool Undefgeneric(\
Defgeneric \*d,\
Environment \*env);

The function **DefgenericIsDeletable** returns true if the defgeneric specified by parameter **d** can be deleted; otherwise it returns false.

The function **Undefgeneric** is the C equivalent of the CLIPS **undefgeneric** command. It deletes the defgeneric specified by parameter **d**; or if parameter **d** is a null pointer, it deletes all defgenerics in the environment specified by parameter **env**. This function returns true if the deletion is successful; otherwise, it returns false.

### 12.10.4 Watching Defgenerics

bool DefgenericGetWatch(\
Defgeneric \*d);

void DefgenericSetWatch(\
Defgeneric \*d,\
bool b);

The function **DefgenericGetWatch** returns true if execution is being watched for the defgeneric specified by the **d** parameter value; otherwise, it returns false.

The function **DefgenericSetWatch** sets the watch state for the defgeneric specified by the **d** parameter value to the value specified by the parameter **b**.

## 12.11 Defmethod Functions

The following function calls are used for manipulating generic function methods.

### 12.11.1 Iteration and Listing

unsigned GetNextDefmethod(\
Defgeneric \*d,\
unsigned index);

void GetDefmethodList(\
Environment \*environment,\
CLIPSValue \*out,\
Defgeneric \*d);

void ListDefmethods(\
Environment \*env,\
const char \*logicalName,\
Defgeneric \*d);

The function **GetNextDefmethod** provides iteration support for the list of defmethods for a defgeneric. If parameter **index** is a 0, then a pointer to the first **Defmethod** for the defgeneric specified by parameter **d** is returned by this function; otherwise, a pointer to the next **Defmethod** following the **Defmethod** specified by parameter **index** is returned. If parameter **index** is the last **Defmethod** for the specified defgeneric, 0 is returned.

The function **GetDefmethodList** is the C equivalent of the CLIPS **get‑defmethod-list** command. Parameter **env** is a pointer to a previously created environment; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **d** is a pointer to a **Defgeneric**. The output of the function call---a multifield containing a list of defmethod name and index pairs---is stored in the **out** parameter value. If parameter **d** is a null pointer, then defmethods for all defgenerics will be included in parameter **out**; otherwise, only defmethods for the specified defgeneric will be included.

The function **ListDefmethods** is the C equivalent of the CLIPS **list‑defmethods** command. Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the router output destination; and parameter **d** is a pointer to a defgeneric. If parameter **d** is a null pointer, then defmethods for all defgenerics will be listed; otherwise, only defmethods for the specified defgeneric will be listed.

### 12.11.2 Attributes

void DefmethodDescription(\
Defgeneric \*d,\
unsigned index,\
StringBuilder \*sb);

const char \*DefmethodPPForm(\
Defgeneric \*d,\
unsigned index);

void GetMethodRestrictions(\
Defgeneric \*d,\
unsigned index,\
CLIPSValue \*out);

The function **DefmethodDescription** provides a synopsis of a method's parameter restrictions. Parameter **d** is a pointer to a **Defgeneric**; parameter **index** is the method index; and parameter **sb** is a pointer to a **StringBuilder** allocated by the caller in which the method description is stored.

The function **DefmethodPPForm** returns the text representation of the **Defmethod** specified by parameter **d,** the generic function, and parameter **index**, the method index. The null pointer is returned if the text representation is not available.

The function **GetMethodRestrictions** is the C equivalent of the CLIPS **get‑method-restrictions** function. Parameter **d** is a pointer to a generic function; parameter **index** is a method index; and parameter **out** is a pointer to a CLIPSValue allocated by the caller. The output of the function call---a multifield containing the method restrictions---is stored in the **out** parameter value.

### 12.11.3 Deletion

bool DefmethodIsDeletable(\
Defgeneric \*d,\
unsigned index);

bool Undefmethod(\
Defgeneric \*d,\
unsigned index,\
Environment \*env);

The function **DefmethodIsDeletable** returns true if the defmethod specified by parameter **d**, the generic function, and **index**, the method index, can be deleted; otherwise it returns false.

The function **Undefmethod** is the C equivalent of the CLIPS **undefmethod** command. It deletes the defmethod specified by parameter **d**, parameter **index**, and parameter **env**. If parameter **d** is a null pointer and parameter **index** is 0, it deletes all methods for all generic functions in the environment specified by parameter **env**; if parameter **d** is not a null pointer and parameter **index** is 0, it deletes all methods of the generic function; otherwise, the defmethod specified by the generic function and method index is deleted. This function returns true if the deletion is successful; otherwise, it returns false.

### 12.11.4 Watching Methods

bool DefmethodGetWatch(\
Defgeneric \*d,\
unsigned index);

void DefmethodSetWatch(\
Defgeneric \*d,\
unsigned index,\
bool b);

The function **DefmethodGetWatch** returns true if the method specified by parameter **d**, the generic function, and parameter **index**, the method index, is being watched; otherwise, it returns false.

The function **DefmethodSetWatch** sets the method watch state for the defmethod specified by the **d** parameter, the generic function, and parameter **index**, the method index, to the value specified by the parameter **b**.

## 12.12 Defclass Functions

The following function calls are used for manipulating defclasses.

### 12.12.1 Search, Iteration, and Listing

Defclass \*FindDefclass(\
Environment \*env,\
const char \*name);

Defclass \*GetNextDefclass(\
Environment \*env,\
Defclass \*d);

void GetDefclassList(\
Environment \*env,\
CLIPSValue \*out,\
Defmodule \*d);

void ListDefclasses(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d);

void BrowseClasses(,\
Defclass \*d,\
const char \*logicalName);

void DescribeClass(\
Defclass \*d,\
const char \*logicalName);

The function **FindDefclass** searches for the defclass specified by parameter **name** in the environment specified by parameter **env**. This function returns a pointer to the named defclass if it exists; otherwise, it returns a null pointer.

The function **GetNextDefclass** provides iteration support for the list of defclasses in the current module. If parameter **d** is a null pointer, then a pointer to the first **Defclass** in the current module is returned by this function; otherwise, a pointer to the next **Defclass** following the **Defclass** specified by parameter **d** is returned. If parameter **d** is the last **Defclass** in the current module, a null pointer is returned.

The function **GetDefclassList** is the C equivalent of the CLIPS **get-defclass-list** function). Parameter **env** is a pointer to a previously created environment; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **d** is a pointer to a **Defmodule**. The output of the function call---a multifield containing a list of defclass names---is stored in the **out** parameter value. If parameter **d** is a null pointer, then defclasses in all modules will be included in parameter **out**; otherwise, only defclasses in the specified module will be included.

The function **ListDefclass** is the C equivalent of the CLIPS **list‑defclass** command. Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the router output destination; and parameter **d** is a pointer to a defmodule. If parameter **d** is a null pointer, then defclasses in all modules will be listed; otherwise, only defclasses in the specified module will be listed.

The function **BrowseClasses** is the C equivalent of the CLIPS **browse‑classes** command. It prints a "graph" of all classes which inherit from the class specified by parameter **d** to the router output destination specified by the **logicalName** parameter.

The function **DescribeClass** is the C equivalent of the CLIPS **describe‑class** command. It prints a summary of the class specified by parameter **d** to the router output destination specified by the **logicalName** parameter. This summary includes abstract/concrete behavior, slots and facets (direct and inherited), and recognized message-handlers (direct and inherited).

### 12.12.2 Class Attributes

const char \*DefclassModule(\
Defclass \*d);

const char \*DefclassName(\
Defclass \*d);

const char \*DefclassPPForm(\
Defclass \*d);

void ClassSlots(\
Defclass \*d,\
CLIPSValue \*out,\
bool inherit);

void ClassSubclasses(\
Defclass \*d,\
CLIPSValue \*out,\
bool inherit);

void ClassSuperclasses(\
Defclass \*d,\
CLIPSValue \*out,\
bool inherit);

The function **DefclassModule** is the C equivalent of the CLIPS **defclass-module** function. The return value of this function is the name of the module in which the defclass specified by parameter **d** is defined.

The function **DefclassName** returns the name of the defclass specified by the **d** parameter.

The function **DefclassPPForm** returns the text representation of the **Defclass** specified by the **d** parameter. The null pointer is returned if the text representation is not available.

The function **ClassSlots** is the C equivalent of the CLIPS **class-slots** command. Parameter **d** is a pointer to a **Defclass**; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **inherit** is a boolean flag. The output of the function call---a multifield containing the defclass's slot names---is stored in the **out** parameter value. If the **inherit** parameter is true, then inherited slots are included; otherwise, only slot explicitly defined by the class are included.

The function **ClassSubclasses** is the C equivalent of the CLIPS **class-subclasses** command. Parameter **d** is a pointer to a **Defclass**; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **inherit** is a boolean flag. The output of the function call---a multifield containing the defclass's subclass names---is stored in the **out** parameter value. If the **inherit** parameter is true, then inherited subclasses are included; otherwise, only direct subclasses explicitly defined by the class are included.

The function **ClassSuperclasses** is the C equivalent of the CLIPS **class-superclasses** command. Parameter **d** is a pointer to a **Defclass**; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **inherit** is a boolean flag. The output of the function call---a multifield containing the defclass's superclass names---is stored in the **out** parameter value. If the **inherit** parameter is true, then inherited superclasses are included; otherwise, only direct superclasses explicitly defined by the class are included.

### 12.12.3 Deletion

bool DefclassIsDeletable(\
Defclass \*d);

bool Undefclass(\
Defclass \*d,\
Environment \*env);

The function **DefclassIsDeletable** returns true if the defclass specified by parameter **d** can be deleted; otherwise it returns false.

The **Undefclass** function is the C equivalent of the CLIPS **undefclass** command. It deletes the defclass specified by parameter **d**; or if parameter **d** is a null pointer, it deletes all defclasses in the environment specified by parameter **env**. This function returns true if the deletion is successful; otherwise, it returns false.

### 12.12.4 Watching Instances and Slots

bool DefclassGetWatchInstances(\
Defclass \*d);

bool DefclassGetWatchSlots(\
Defclass \*d);

void DefclassSetWatchInstances(\
Defclass \*d,\
bool b);

void DefclassSetWatchSlots(\
Defclass \*d,\
bool b);

The function **DefclassGetWatchInstances** returns true if instances (creations and deletions) are being watched for the defclass specified by the **d** parameter value; otherwise, it returns false.

The function **DefclassGetWatchSlots** returns true if slot changes are being watched for the defclass specified by the **d** parameter value; otherwise, it returns false.

The function **DefclassSetWatchInstances** sets the instances creation and deletion watch state for the defclass specified by the **d** parameter value to the value specified by the parameter **b**.

The function **DefclassSetWatchSlots** sets the slot changes watch state for the defclass specified by the **d** parameter value to the value specified by the parameter **b**.

### 12.12.5 Class Predicates

bool ClassAbstractP(\
Defclass \*d);

bool ClassReactiveP(\
Defclass \*d);

bool SubclassP(\
Defclass \*d1,\
Defclass \*d2);

bool SuperclassP(\
Defclass \*d1,\
Defclass \*d2);

The function **ClassAbstractP** is the C equivalent of the CLIPS **class-abstractp** command. It returns true if the defclass specified by parameter **d** is abstract; otherwise, it returns false.

The function **ClassReactiveP** is the C equivalent of the CLIPS **class-reactivep** command. It returns true if the defclass specified by parameter **d** is reactive; otherwise, it returns false.

The function **SubclassP** returns true if the class specified by parameter **d1** is a subclass of the class specified by parameter **d2**; otherwise, it returns false.

The function **SuperclassP** returns true if the class specified by parameter **d1** is a superclass of the class specified by parameter **d2**; otherwise, it returns false.

### 12.12.6 Slot Attributes

bool SlotAllowedClasses(\
Defclass \*d,\
const char \*name,\
CLIPSValue \*out);

bool SlotAllowedValues(\
Defclass \*d,\
const char \*name,\
CLIPSValue \*out);

bool SlotCardinality(\
Defclass \*d,\
const char \*name,\
CLIPSValue \*out);

bool SlotDefaultValue(\
Defclass \*d,\
const char \*name,\
CLIPSValue \*out);

bool SlotFacets(\
Defclass \*d,\
const char \*name,\
CLIPSValue \*out);

bool SlotRange(\
Defclass \*d,\
const char \*name,\
CLIPSValue \*out);

bool SlotSources(\
Defclass \*d,\
const char \*name\
CLIPSValue \*out);

bool SlotTypes(\
Defclass \*d,\
const char \*name,\
CLIPSValue \*out);

The function **SlotAllowedClasses** is the C equivalent of the CLIPS **slot‑allowed-classes** function. The function **SlotAllowedValues** is the C equivalent of the CLIPS **slot‑allowed-values** function. The function **SlotCardinality** is the C equivalent of the CLIPS **slot-cardinality** function. The function **SlotDefaultValue** is the C equivalent of the CLIPS **slot-default-value** function. The function **SlotFacets** is the C equivalent of the CLIPS **slot-facets** command. The function **SlotRange** is the C equivalent of the CLIPS **slot‑range** function. The function **SlotSources** is the C equivalent of the CLIPS **slot-sources** command. The function **SlotTypes** is the C equivalent of the CLIPS **slot-types** function.

Parameter **d** is a pointer to a **Defclass**; parameter **name** specifies a valid slot name for the specified defclass; and parameter **out** is a pointer to a **CLIPSValue** allocated by the caller. The output of the function call---a multifield containing the attribute values---is stored in the **out** parameter value. These function return true if a valid slot name was specified and the output value is successfully set; otherwise, false is returned.

### 12.12.7 Slot Predicates

bool SlotDirectAccessP(\
Defclass \*d,\
const char \*name);

bool SlotExistP(\
Defclass \*d,\
const char \*name,\
bool inherit);

bool SlotInitableP(\
Defclass \*d,\
const char \*name);

bool SlotPublicP(\
Defclass \*d,\
const char \*name);

bool SlotWritableP(\
Defclass \*d,\
const char \*name);

The function **SlotDirectAccessP** is the C equivalent of the CLIPS **slot-direct-accessp** function. Parameter **d** is a pointer to a **Defclass**; and parameter **name** specifies a slot name. This function returns true if the slot is directly accessible; otherwise, it returns false.

The function **SlotExistP** is the C equivalent of the CLIPS **slot-existp** function. Parameter **d** is a pointer to a **Defclass**; parameter **name** specifies a slot name; and parameter **inherit** is a boolean flag. This function returns true if the specified slot exists; otherwise, it returns false. If the **inherit** parameter value is true, then inherited classes will be searched for the slot; otherwise, only the specified class will be searched.

The function **SlotInitableP** is the C equivalent of the CLIPS **slot-initablep** function. Parameter **d** is a pointer to a **Defclass**; and parameter **name** specifies a slot name. This function returns true if the slot is initable; otherwise, it returns false.

The function **SlotPublicP** is the C equivalent of the CLIPS **slot-publicp** function. Parameter **d** is a pointer to a **Defclass**; and parameter **name** specifies a slot name. This function returns true if the slot is public; otherwise, it returns false.

The function **SlotWritableP** is the C equivalent of the CLIPS **slot-writablep** function. Parameter **d** is a pointer to a **Defclass**; and parameter **name** specifies a slot name. This function returns true if the slot is writable; otherwise, it returns false.

### 12.12.8 Settings

ClassDefaultsMode GetClassDefaultsMode(\
Environment \*env);

ClassDefaultsMode SetClassDefaultsMode(\
Environment \*env,\
ClassDefaultsMode mode);

typedef enum\
{\
CONVENIENCE_MODE,\
CONSERVATION_MODE\
} ClassDefaultsMode;

The function **GetClassDefaultsMode** is the C equivalent of the CLIPS **get‑class‑defaults‑mode** command. The **env** parameter is a pointer to a previously created environment. This function returns the ClassDefaultsMode enumeration corresponding to the current setting.

The function **SetClassDefaultsMode** the C equivalent of the CLIPS command **set‑class‑defaults-mode**‑‑). The **env** parameter is a pointer to a previously created environment; the **mode** parameter is the new setting for the behavior. This function returns the old setting for the behavior.

## 12.13 Instance Functions

The following function calls are used for manipulating instances.

### 12.13.1 Search, Iteration, and Listing

Instance \*FindInstance(\
Environment \*env,\
Defmodule \*d,\
const char \*name,\
bool searchImports);

Instance \*GetNextInstance(\
Environment \*env,\
Instance \*i);

Instance \*GetNextInstanceInClass(\
Defclass \*d,\
Instance \*i);

Instance \*GetNextInstanceInClassAndSubclasses(\
Defclass \*\*d,\
Instance \*i,\
UDFValue \*iterator);

void Instances(\
Environment \*env,\
const char \*logicalName,\
Defmodule \*d,\
const char \*className,\
bool listSubclasses);

The function **FindInstance** searches for the named instance specified by parameter **name** in the module specified by parameter **d** in the environment specified by parameter **env**. If parameter **d** is a null pointer, then the current module will be searched. If parameter **searchImports** is true, then imported modules will also be searched for the instance. If the named instance is found, a pointer to it is returned; otherwise, the null pointer is returned.

The function **GetNextInstance** provides iteration support for the list of instance in an environment. If parameter **i** is a null pointer, then a pointer to the first **Instance** in the environment specified by parameter **env** is returned by this function; otherwise, a pointer to the next **Instance** following the **Instance** specified by parameter **i** is returned. If parameter **i** is the last **Instance** in the specified environment, a null pointer is returned.

The function **GetNextInstanceInClass** provides iteration support for the list of instances belonging to a defclass. If parameter **i** is a null pointer, then a pointer to the first **Instance** for the defclass specified by parameter **d** is returned by this function; otherwise, a pointer to the next **Instance** of the specified defclass following the **Instance** specified by parameter **i** is returned. If parameter **i** is the last **Instance** for the specified defclass, a null pointer is returned.

The function **GetNextInstanceInClassAndSubclasses** provides iteration support for the list of instances belonging to a defclass and its subclasses. If parameter **i** is a null pointer, then a pointer to the first **Instance** for the defclass or subclasses specified by parameter **d** is returned by this function; otherwise, a pointer to the next **Instance** of the specified defclass or its subclasses following the **Instance** specified by parameter **i** is returned. If parameter **i** is the last **Instance** for the specified defclass or its subclasses, a null pointer is returned. Parameter **d** is a pointer to a pointer to a **Defclass** declared by the caller. As the subclasses of the specified class are iterated through to find instances, the value referenced by the **d** parameter value is updated to indicate the class of the instance returned by this function. Parameter **iterator** is a pointer to a **UDFValue** declared by the caller that is used to store instance iteration information; no initialization of this argument is required and the values stored in this argument are not intended for examination by the calling function.

The function **Instances** is the C equivalent of the CLIPS **instances** command. Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the router output destination; parameter **d** is a pointer to a **Defmodule**; parameter **name** is the name of a defclass; and parameter **listSubclasses** is a boolean value indicating whether instances of subclasses should be listed. If parameter **d** is a null pointer, then all instances of all classes in all modules are listed (and the parameters values for **name** and **listSubclasses** are ignored). If parameter **d** is not a null pointer and parameter **name** is a null pointer, all instance of all classes in the specified module are listed (and parameter **listSubclasses** is ignored).

### 12.13.2 Attributes

Defclass \*InstanceClass(\
Instance \*i);

const char \*InstanceName(\
Instance \*i);

void InstancePPForm(\
Instance \*i,\
StringBuilder \*sb);

GetSlotError DirectGetSlot(\
Instance \*i,\
const char \*name,\
CLIPSValue \*out);

PutSlotError DirectPutSlot(\
Instance \*i,\
const char \*name,\
CLIPSValue \*value);

PutSlotError DirectPutSlotInteger(\
Instance \*i,\
const char \*name,\
long long value);

PutSlotError DirectPutSlotFloat(\
Instance \*i,\
const char \*name,\
double value);

PutSlotError DirectPutSlotSymbol(\
Instance \*i,\
const char \*name,\
const char \*value);

PutSlotError DirectPutSlotString(\
Instance \*i,\
const char \*name,\
const char \*value);

PutSlotError DirectPutSlotInstanceName(\
Instance \*i,\
const char \*name,\
const char \*value);

PutSlotError DirectPutSlotCLIPSInteger(\
Instance \*i,\
const char \*name,\
CLIPSInteger \*value);

PutSlotError DirectPutSlotCLIPSFloat(\
Instance \*i,\
const char \*name,\
CLIPSFloat \*value);

PutSlotError DirectPutSlotCLIPSLexeme(\
Instance \*i,\
const char \*name,\
CLIPSLexeme \*value);

PutSlotError DirectPutSlotFact(\
Instance \*i,\
const char \*name,\
Fact \*value);

PutSlotError DirectPutSlotInstance(\
Instance \*i,\
const char \*name,\
Instance \*value);

PutSlotError DirectPutSlotMultifield(\
Instance \*i,\
const char \*name,\
Multifield \*value);

PutSlotError DirectPutSlotCLIPSExternalAddress(\
Instance \*i,\
const char \*name,\
CLIPSExternalAddress \*value);

typedef enum\
{\
GSE_NO_ERROR,\
GSE_NULL_POINTER_ERROR,\
GSE_INVALID_TARGET_ERROR,\
GSE_SLOT_NOT_FOUND_ERROR,\
} GetSlotError;

typedef enum\
{\
PSE_NO_ERROR,\
PSE_NULL_POINTER_ERROR,\
PSE_INVALID_TARGET_ERROR,\
PSE_SLOT_NOT_FOUND_ERROR,\
PSE_TYPE_ERROR,\
PSE_RANGE_ERROR,\
PSE_ALLOWED_VALUES_ERROR,\
PSE_CARDINALITY_ERROR,\
PSE_ALLOWED_CLASSES_ERROR,\
PSE_RULE_NETWORK_ERROR\
} PutSlotError;

The function **InstanceClass** returns a pointer to the **Defclass** associated with the **Instance** specified by parameter **i**.

The function **InstanceName** returns the instance name of the **Instance** specified by parameter **i**. If the instance has been deleted, a NULL pointer is returned.

The function **InstancePPForm** stores the text representation of the **Instance** specified by the parameter **i** in the **StringBuilder** specified by parameter **sb**.

The function **DirectGetSlot** is the C equivalent of the CLIPS **dynamic‑get** function. It retrieves the slot value specified by parameter **name** from the instance specified by parameter **i** and stores it in parameter **out**, a **CLIPSValue** previously allocated by the caller. This function bypasses message‑passing. The error codes returned by this function are:

  --------------------------------- -------------------------------------------------------------
  **Error Code**                    **Meaning**

  GSE_NO_ERROR                      No error occurred.

  GSE_INVALID_TARGET_ERROR          One of the function arguments was a NULL pointer.

  GSE_INVALID_TARGET_ERROR          The instance specified by parameter **i** has been deleted.

  GSE_SLOT_NOT_FOUND_ERROR          The instance does not have the specified slot.
  --------------------------------- -------------------------------------------------------------

The function **DirectPutSlot** function is the C equivalent of the CLIPS **dynamic‑put** function. It sets the slot value specified by parameter **name** of the instance specified by parameter **i** to the value stored in parameter **value**, a **CLIPSValue** allocated and set by the caller. This function bypasses message‑passing. The additional **DirectPutSlot...** functions are wrappers for the **DirectPutSlot** function which allow you to assign other CLIPS and C data types to a slot without the need to allocate a **CLIPSValue** structure. The error codes returned by this function are:

  --------------------------------- --------------------------------------------------------------------------------------
  **Error Code**                    **Meaning**

  PSE_NO_ERROR                      No error occurred.

  PSE_NULL_POINTER_ERROR            One of the function arguments was a NULL pointer.

  PSE_INVALID_TARGET_ERROR          The instance specified by parameter **i** has been deleted.

  PSE_SLOT_NOT_FOUND_ERROR          The fact or instance does not have the specified slot.

  PSE_TYPE_ERROR                    The slot value violates the type constraint.

  PSE_RANGE_ERROR                   The slot value violates the range constraint.

  PSE_ALLOWED_VALUES_ERROR          The slot value violates the allowed values constraint.

  PSE_CARDINALITY_ERROR             The slot value violates the slot cardinality.

  PSE_ALLOWED_CLASSES_ERROR         The slot value violates the allowed classes constraint.

  PSE_RULE_NETWORK_ERROR            An error occurred while the slot assignment was being processed in the rule network.
  --------------------------------- --------------------------------------------------------------------------------------

The error codes for slot constraint violations are only returned when dynamic constraint checking is enabled.

### 12.13.3 Deletion

UnmakeInstanceError UnmakeAllInstances(\
Environment \*env);

UnmakeInstanceError DeleteInstance(\
Instance \*i);

UnmakeInstanceError DeleteAllInstances(\
Environment \*env);

bool ValidInstanceAddress(\
Instance \*i);

The function **UnmakeAllInstances** deletes all instances in the environment specified by parameter **env** using message-passing. It returns UE_NO_ERROR if successful. See the **Unmake** command in section 3.3.4 for the list of error codes in the **UnmakeInstanceError** enumeration.

The function **DeleteInstance** directly deletes the instance specified by parameter **i** bypassing message-passing. The function **DeleteAllInstances** directly deletes all instances in the environment specified by parameter **env** bypassing message-passing. Both functions returns UE_NO_ERROR if deletion is successful. See the **Unmake** command in section 3.3.4 for the list of error codes in the **UnmakeInstanceError** enumeration.

The function **ValidInstanceAddress** determines if an instance referenced by an address still exists. It returns true if the instance still exists; otherwise, it returns false. The parameter **i** must be a **Instance** that has not been deleted or has been retained (see section 5.2).

### 12.13.4 Detecting Changes to Instances

bool GetInstancesChanged(\
Environment \*env);

void SetInstancesChanged(\
Environment \*env,\
bool b);

The function **GetInstancesChanged** returns true if changes to instances for the environment specified by parameter **env** have occurred (either creations, deletions, or slot value changes); otherwise, it returns false. To track future changes, **SetInstanceChanged** should reset the change tracking value to false.

The function **SetInstancesChanged** sets the instances change tracking value for the environment specified by the parameter **env** to the value specified by the parameter **b**.

### 12.13.5 Send

void Send(\
Environment \*env,\
CLIPSValue \*in,\
const char \*msg,\
const char \*msgArgs\
CLIPSValue \*out);

The function **Send** is the C equivalent of the CLIPS **send** function. Parameter **env** is a pointer to a previously created environment; parameter **in** is a CLIPSValue allocated and assigned the value of the object (instance, instance name, symbol, etc.) to receive the message; parameter **msg** is the message to be received; parameter **msgArgs** is a string containing the constants arguments to the message separated by spaces (a null pointer indicates no arguments); and parameter **out** is a CLIPSValue allocated by the caller that is assigned the return value of the message call. If the calling function does not need to examine the return value of the message, a null pointer can be specified for the **out** parameter value. This function can trigger garbage collection.

### 12.13.6 Examples

#### 12.13.6.1 Instance Iteration

#include \"clips.h\"

int main()

{

Environment \*theEnv;

UDFValue iterate;

Instance \*theInstance;

Defclass \*theClass;

theEnv = CreateEnvironment();

Build(theEnv,\"(defclass A (is-a USER))\");

Build(theEnv,\"(defclass B (is-a USER))\");

MakeInstance(theEnv,\"(a1 of A)\");

MakeInstance(theEnv,\"(a2 of A)\");

MakeInstance(theEnv,\"(b1 of B)\");

MakeInstance(theEnv,\"(b2 of B)\");

theClass = FindDefclass(theEnv,\"USER\");

for (theInstance = GetNextInstanceInClassAndSubclasses(&theClass,NULL,&iterate);

theInstance != NULL;

theInstance = GetNextInstanceInClassAndSubclasses(&theClass,

theInstance,&iterate))

{ Writeln(theEnv,InstanceName(theInstance)); }

DestroyEnvironment(theEnv);

}

The output when running this example is:

a1

a2

b1

b2

#### 12.13.6.2 Send

#include \"clips.h\"

int main()

{

Environment \*theEnv;

char \*cs;

CLIPSValue insdata;

theEnv = CreateEnvironment();

Build(theEnv,\"(defclass MY-CLASS (is-a USER))\");

// Note the use of escape characters to embed quotation marks.

// (defmessage-handler MY-CLASS my-msg (?x ?y ?z)

// (printout t ?x \" \" ?y \" \" ?z crlf))

cs = \"(defmessage-handler MY-CLASS my-msg (?x ?y ?z)\"

\" (printout t ?x \\\" \\\" ?y \\\" \\\" ?z crlf))\";

Build(theEnv,cs);

insdata.instanceValue = MakeInstance(theEnv,\"(my-instance of MY-CLASS)\");

Send(theEnv,&insdata,\"my-msg\",\"1 abc 3\",NULL);

DestroyEnvironment(theEnv);

}

The output when running this example is:

1 abc 3

## 12.14 Defmessage-handler Functions

The following function calls are used for manipulating defmessage‑handlers.

### 12.14.1 Search, Iteration, and Listing

unsigned FindDefmessageHandler(\
Defclass \*d,\
const char \*name,\
const char \*type);

unsigned GetNextDefmessageHandler(\
Defclass \*d,\
unsigned id);

void GetDefmessageHandlerList(\
Environment \*env,\
Defclass \*d,\
CLIPSValue \*out,\
bool inherited);

void ListDefmessageHandlers(\
Environment \*env,\
Defclass \*d,\
const char \*logicalName,\
bool inherited);

The function **FindDefmessageHandler** searches for the defmessage-handler specified by parameters **name** and **type** in the defclass specified by parameter **d**. Parameter **type** should be one of the following values: \"around\", \"before\", \"primary\", or \"around\". This function returns an integer id for the defmessage-handler if it exists; otherwise, it returns 0.

The function **GetNextDefmessageHandler** provides iteration support for the list of defmessage-handlers for a defclass. If parameter **id** is a 0, then the integer id to the first defmessage-handler for the defclass specified by parameter **d** is returned by this function; otherwise, the integer id to the next defmessage-handler following the defmessage-handler specified by parameter **id** is returned. If parameter **id** is the last defmessage-handler for the specified defclass, 0 is returned.

The function **GetDefmessageHandlerList** is the C equivalent of the CLIPS **get‑defmessage-handler-list** command. Parameter **env** is a pointer to a previously created environment; parameter **d** is a pointer to a **Defclass**; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **inherited** is a boolean value that indicates whether inherited message-handlers are included. The output of the function call---a multifield containing a list of class name/handler name/handler type triplets---is stored in the **out** parameter value. If parameter **d** is a null pointer, then message-handlers for all defclasses will be included in parameter **out**; otherwise, only message-handlers for the specified defclass will be included.

The function **ListDefmessageHandlers** is the C equivalent of the CLIPS **list‑defmessage-handlers** command. Parameter **env** is a pointer to a previously created environment; parameter **d** is a pointer to a defclass; parameter **logicalName** is the router output destination; and parameter **inherited** is a boolean value that indicates whether inherited message-handlers are listed. If parameter **d** is a null pointer, then defmessage-handlers for all defclasses will be listed; otherwise, only defmessage-handlers for the specified defclass will be listed.

### 12.14.2 Attributes

const char \*DefmessageHandlerName(\
Defclass \*defclassPtr,\
unsigned id);

const char \*DefmessageHandlerPPForm(\
Defclass \*d,\
unsigned id);

const char \*DefmessageHandlerType(\
Defclass \*d,\
unsigned id);

The function **DefmessageHandlerName** returns the name of the defmessage-handler specified by parameters **d**, a **Defclass**, and **id**, the message-handler id.

The function **DefmessageHandlerPPForm** returns the text representation of the defmessage-handler specified by parameter **d,** a defclass, and parameter **id**, a message-handler id. The null pointer is returned if the text representation is not available.

The function **DefmessageHandlerType** returns the type of the defmessage-handler specified by parameter **d,** a defclass, and parameter **id**, a message-handler id. The return value of this function is one of the following values: \"around\", \"before\", \"primary\", or \"around\".

### 12.14.3 Deletion

bool DefmessageHandlerIsDeletable(\
Defclass \*d,\
unsigned id);

bool UndefmessageHandler(\
Defclass \*d,\
unsigned id,\
Environment \*env);

The function **DefmessageHandleIsDeletable** returns true if the defmessage-handler specified by parameter **d**, a defclass, and **id**, a message-handler id, can be deleted; otherwise it returns false.

The function **UndefmessageHandler** is the C equivalent of the CLIPS **undefmessage-handler** command. It deletes the defmessage-handler specified by parameter **d**, parameter **d**, and parameter **env**. If parameter **d** is a null pointer and parameter **id** is 0, it deletes all message-handlers for all classes in the environment specified by parameter **env**; if parameter **d** is not a null pointer and parameter **id** is 0, it deletes all message-handlers of the defclass; otherwise, the defmessage-handler specified by the defclass and message-handler id is deleted. This function returns true if the deletion is successful; otherwise, it returns false.

### 12.14.4 Watching Message-Handlers

bool DefmessageHandlerGetWatch(\
Defclass \*d,\
unsigned id);

void DefmessageHandlerSetWatch(\
Defclass \*d,\
unsigned id,\
bool b);

The function **DefmessageHandlerGetWatch** returns true if the message-handler specified by parameter **d**, the defclass, and parameter **id**, the message-handler id, is being watched; otherwise, it returns false.

The function **DefmessageHandlerSetWatch** sets the message-handler watch state for the defmessage-handler specified by parameter **d**, the defclass, and parameter **id**, the message-handler id, to the value specified by the parameter **b**.

### 12.14.5 PreviewSend

void PreviewSend(\
Defclass \*d,\
const char \*logicalName,\
const char \*message);

The function **PreviewSend** is the C equivalent of the CLIPS **preview‑send** command. Parameter **d** is a pointer to a defclass; parameter **logicalName** is the router output destination; and parameter **message** is the name of the message-handler to be previewed.

### 12.14.6 Example

This example demonstrates how to preview a send message and watch specific message-handlers when a message is executed. The following output shows how you would typically perform this task from the CLIPS command prompt:

CLIPS\> (defclass A (is-a USER))

CLIPS\> (defmessage-handler A foo (?x))

CLIPS\> (defmessage-handler A foo before (?x))

CLIPS\> (defmessage-handler A foo after (?x))

CLIPS\> (defclass B (is-a A))

CLIPS\> (defmessage-handler B foo (?x) (call-next-handler))

CLIPS\> (defmessage-handler B foo around (?x) (call-next-handler))

CLIPS\> (preview-send B foo)

\>\> foo around in class B

\| \>\> foo before in class A

\| \<\< foo before in class A

\| \>\> foo primary in class B

\| \| \>\> foo primary in class A

\| \| \<\< foo primary in class A

\| \<\< foo primary in class B

\| \>\> foo after in class A

\| \<\< foo after in class A

\<\< foo around in class B

CLIPS\> (watch message-handlers A foo primary)

CLIPS\> (watch message-handlers B foo around)

CLIPS\> (make-instance \[b1\] of B)

\[b1\]

CLIPS\> (send \[b1\] foo 3)

HND \>\> foo around in class B

ED:1 (\<Instance-b1\> 3)

HND \>\> foo primary in class A

ED:1 (\<Instance-b1\> 3)

HND \<\< foo primary in class A

ED:1 (\<Instance-b1\> 3)

HND \<\< foo around in class B

ED:1 (\<Instance-b1\> 3)

FALSE

CLIPS\>

To achieve the same result from a C program, change the contents of the main.c source file to the following:

#include \"clips.h\"

int main()

{

Environment \*env;

Defclass \*classA, \*classB;

env = CreateEnvironment();

Build(env,\"(defclass A (is-a USER))\");

Build(env,\"(defmessage-handler A foo (?x))\");

Build(env,\"(defmessage-handler A foo before (?x))\");

Build(env,\"(defmessage-handler A foo after (?x))\");

Build(env,\"(defclass B (is-a A))\");

Build(env,\"(defmessage-handler B foo (?x) (call-next-handler))\");

Build(env,\"(defmessage-handler B foo around (?x) (call-next-handler))\");

classA = FindDefclass(env,\"A\");

classB = FindDefclass(env,\"B\");

Write(env,\"Preview Send:\\n\\n\");

PreviewSend(classB,STDOUT,\"foo\");

Write(env,\"\\nWatch Handlers and Send Message:\\n\\n\");

DefmessageHandlerSetWatch(classA,

FindDefmessageHandler(classA,\"foo\",\"primary\"),

true);

DefmessageHandlerSetWatch(classB,

FindDefmessageHandler(classB,\"foo\",\"around\"),

true);

MakeInstance(env,\"(\[b1\] of B)\");

Eval(env,\"(send \[b1\] foo 3)\",NULL);

DestroyEnvironment(env);

}

The following output will be produced when the program is run:

Preview Send:

\>\> foo around in class B

\| \>\> foo before in class A

\| \<\< foo before in class A

\| \>\> foo primary in class B

\| \| \>\> foo primary in class A

\| \| \<\< foo primary in class A

\| \<\< foo primary in class B

\| \>\> foo after in class A

\| \<\< foo after in class A

\<\< foo around in class B

Watch Handlers and Send Message:

HND \>\> foo around in class B

ED:1 (\<Instance-b1\> 3)

HND \>\> foo primary in class A

ED:1 (\<Instance-b1\> 3)

HND \<\< foo primary in class A

ED:1 (\<Instance-b1\> 3)

HND \<\< foo around in class B

ED:1 (\<Instance-b1\> 3)

## 12.15 Definstances Functions

The following function calls are used for manipulating definstances.

### 12.15.1 Search, Iteration, and Listing

Definstances \*FindDefinstances(\
Environment \*env,\
const char \*name);

Definstances \*GetNextDefinstances(\
Environment \*env,\
Definstances \*d);

void GetDefinstancesList(\
Environment \*env,\
CLIPSValue \*out,\
Defmodule \*d);

void ListDefinstances(\
Environment \*env,\
char \*logicalName,\
Defmodule \*d);

The function **FindDefinstances** searches for the definstances specified by parameter **name** in the environment specified by parameter **env**. This function returns a pointer to the named definstances if it exists; otherwise, it returns a null pointer.

The function **GetNextDefinstances** provides iteration support for the list of definstances in the current module. If parameter **d** is a null pointer, then a pointer to the first **Definstances** in the current module is returned by this function; otherwise, a pointer to the next **Definstances** following the **Definstancess** specified by parameter **d** is returned. If parameter **d** is the last **Deffacts** in the current module, a null pointer is returned.

The function **GetDefinstancesList** the C equivalent of the CLIPS **get-definstances-list** function. Parameter **env** is a pointer to a previously created environment; parameter **out** is a pointer to a **CLIPSValue** allocated by the caller; and parameter **d** is a pointer to a **Defmodule**. The output of the function call---a multifield containing a list of definstances names---is stored in the **out** parameter value. If parameter **d** is a null pointer, then definstancess in all modules will be included in parameter **out**; otherwise, only definstancess in the specified module will be included.

The function **ListDefinstances** is the C equivalent of the CLIPS **list‑definstances** command. Parameter **env** is a pointer to a previously created environment; parameter **logicalName** is the router output destination; and parameter **d** is a pointer to a defmodule. If parameter **d** is a null pointer, then definstances in all modules will be listed; otherwise, only definstances in the specified module will be listed.

### 12.15.2 Attributes

const char \*DefinstancesModule(\
Definstances \*d);

const char \*DefinstancesName(\
Definstances \*d);

const char \*DefinstancesPPForm(\
Definstances \*d);

The function **DefinstancesModule** is the C equivalent of the CLIPS **definstances-module** command.

The function **DefinstancesName** returns the name of the deffacts specified by the **d** parameter.

The function **DefinstancePPForm** returns the text representation of the **Definstancess** specified by the **d** parameter. The null pointer is returned if the text representation is not available.

### 12.15.3 Deletion

bool DefinstancesIsDeletable(\
Definstances \*d);

bool Undefinstances(\
Definstances \*d,\
Environment \*env);

The function **DefinstancesIsDeletable** returns true if the definstances specified by parameter **d** can be deleted; otherwise it returns false.

The function **Undefinstances** is the C equivalent of the CLIPS **undefinstances** command. It deletes the definstances specified by parameter **d**; or if parameter **d** is a null pointer, it deletes all definstances in the environment specified by parameter **env**. This function returns true if the deletion is successful; otherwise, it returns false.

## 12.16 Defmodule Functions

The following function calls are used for manipulating defmodules.

### 12.16.1 Search, Iteration, and Listing

Defmodule \*FindDefmodule(\
Environment \*env,\
const char \*name);

Defmodule \*GetNextDefmodule(\
Environment \*env,\
Defmodule \*d);

void GetDefmoduleList(\
Environment \*env,\
CLIPSValue \*out);

void ListDefmodules(\
Environment \*env,\
const char \*logicalName);

The function **FindDefmodule** searches for the defmodule specified by parameter **name** in the environment specified by parameter **env**. This function returns a pointer to the named defmodule if it exists; otherwise, it returns a null pointer.

The function **GetNextDefmodule** provides iteration support for the list of defmodules. If parameter **d** is a null pointer, then a pointer to the first **Defmodule** in the environment is returned by this function; otherwise, a pointer to the next **Defmodule** following the **Defmodule** specified by parameter **d** is returned. If parameter **d** is the last **Defmodule** in the environment, a null pointer is returned.

The function **GetDefmoduleList** is the C equivalent of the CLIPS **get-defmodule-list** function. Parameter **env** is a pointer to a previously created environment; and parameter **out** is a pointer to a **CLIPSValue** allocated by the caller. The output of the function call---a multifield containing a list of defmodule names---is stored in the **out** parameter value.

The function **ListDefmodules** is the C equivalent of the CLIPS **list‑defmodules** command. Parameter **env** is a pointer to a previously created environment; and parameter **logicalName** is the router output destination.

### 12.16.2 Attributes

const char \*DefmoduleName(\
Defmodule \*d);

const char \*DefmodulePPForm(\
Defmodule \*d);

The function **DefmoduleName** returns the name of the defmodule specified by the **d** parameter.

The function **DefmodulePPForm** returns the text representation of the **Defmodule** specified by the **d** parameter. The null pointer is returned if the text representation is not available.

### 12.16.3 Current Module

Defmodule \*GetCurrentModule(\
Environment \*env);

Defmodule \*SetCurrentModule(\
Environment \*env,\
Defmodule \*d);

The function **GetCurrentModule** is the C equivalent of the CLIPS **get-current-module** function. Parameter **env** is a pointer to a previously created environment. This function returns a pointer to the current environment.

The function **SetCurrentModule** is the C equivalent of the CLIPS **set-current-module** function. Parameter **env** is a pointer to a previously created environment; and parameter **d** is a pointer to a **Defmodule** that will become the current module. The return value of this function is the prior current module.

## 12.17 Standard Memory Functions

CLIPS provides functions that can be used to monitor and control memory usage.

### 12.17.1 Memory Allocation and Deallocation

void \*genalloc(\
Environment \*env,\
size_t size);

void genfree(\
Environment \*env,\
void \*ptr,\
size_t size);

The function **genalloc** allocates a block of memory using the CLIPS memory management routines. CLIPS caches memory to improve to performance. Calls to genalloc will first attempt to allocate memory from the cache before making a call to the C library **malloc** function. Parameter **env** is a pointer to a previously allocated environment; and parameter **size** is the number of bytes to be allocated. This function returns a pointer to a memory block of the specified size if successful; otherwise, a null pointer is returned.

The function **genfree** returns a block of memory to the CLIPS memory management routines. Calls to **genfree** adds the freed memory to the CLIPS cache for later reuse. The CLIPS **ReleaseMem** function can be used to clear the cache and release memory back to the operating system. Parameter **env** is a pointer to a previously allocated environment; parameter **ptr** is a pointer to memory previously allocated by **genalloc**; and parameter **size** is the size in bytes of the block of memory.

### 12.17.2 Settings

bool GetConserveMemory(\
Environment \*env);

bool SetConserveMemory(\
Environment \*env,\
bool b;)

The function **GetConserveMemory** returns the current value of the conserve memory behavior. If enabled (true), newly loaded constructs do not have their text (printy print) representation stored with the construct. If there is no need to save or pretty print constructs, this will reduce the amount of memory needed to load constructs.

The function **SetConserveMemory** sets the conserve memory behavior for the environment specified by the parameter **env** to the value specified by the parameter **b**. Changing the value for this behavior does not affect existing constructs.

### 12.17.3 Memory Tracking 

long long MemRequests(\
Environment \*env);

long long MemUsed(\
Environment \*env);

long long ReleaseMem(\
Environment \*env,\
long long limit);

The function **MemRequests** is the C equivalent of the CLIPS **mem-requests** command. The return value of this function is the number of memory requests currently held by CLIPS. When used in conjunction with **MemUsed**, the user can estimate the number of bytes CLIPS requests per call to **malloc**.

The function **MemUsed** is the C equivalent of the CLIPS **mem-used** command. The return value of this function is the total number of bytes requested and currently held by CLIPS. The number of bytes used does not include any overhead for memory management or data creation. It does include all free memory being held by CLIPS for later use; there­fore, it is not a completely accurate measure of the amount of mem­ory actually used to store or process information. It is used primarily as a minimum indication.

The function **ReleaseMem** is the C equivalent of the CLIPS **release-mem** command. It allows free memory being cached by CLIPS to be returned to the operating system. Parameter **env** is a previously allocated environment; and parameter **limit** is the amount of memory to be released. If the **limit** parameter value is 0 or less, then all cached memory will be released; otherwise, cached memory will be released until the amount of released memory exceeds the **limit** parameter value. The return value of this function is the amount of cached memory released.

## 12.18 Embedded Application Examples

### 12.18.1 User‑Defined Functions

### 12.18.2 Manipulating Objects and Calling CLIPS Functions

This section lists the steps needed to define and use an embedded CLIPS application. The example illustrates how to call deffunctions and generic functions as well as manipulate objects from C.

1\) Copy all of the CLIPS source code file to the user directory.

2\) Define a new main routine in a new file.

#include \"clips.h\"

int main()

{

Environment \*env;

Instance \*c1, \*c2, \*c3;

CLIPSValue insdata, result;

env = CreateEnvironment();

/\*=============================================\*/

/\* Load the code for handling complex numbers. \*/

/\*=============================================\*/

Load(env,\"complex.clp\");

/\*=========================================================\*/

/\* Create two complex numbers. Message-passing is used to \*/

/\* create the first instance c1, but c2 is created and has \*/

/\* its slots set directly. \*/

/\*=========================================================\*/

c1 = MakeInstance(env,\"(c1 of COMPLEX (real 1) (imag 10))\");

c2 = CreateRawInstance(env,FindDefclass(env,\"COMPLEX\"),\"c2\");

result.integerValue = CreateInteger(env,3);

DirectPutSlot(c2,\"real\",&result);

result.integerValue = CreateInteger(env,-7);

DirectPutSlot(c2,\"imag\",&result);

/\*===========================================================\*/

/\* Call the function \'+\' which has been overloaded to handle \*/

/\* complex numbers. The result of the complex addition is \*/

/\* stored in a new instance of the COMPLEX class. \*/

/\*===========================================================\*/

Eval(env,\"(+ \[c1\] \[c2\])\",&result);

c3 = FindInstance(env,NULL,result.lexemeValue-\>contents,true);

/\*=======================================================\*/

/\* Print out a summary of the complex addition using the \*/

/\* \"print\" and \"magnitude\" messages to get information \*/

/\* about the three complex numbers. \*/

/\*=======================================================\*/

Write(env,\"The addition of\\n\\n\");

insdata.instanceValue = c1;

Send(env,&insdata,\"print\",NULL,NULL);

Write(env,\"\\nand\\n\\n\");

insdata.instanceValue = c2;

Send(env,&insdata,\"print\",NULL,NULL);

Write(env,\"\\nis\\n\\n\");

insdata.instanceValue = c3;

Send(env,&insdata,\"print\",NULL,NULL);

Write(env,\"\\nand the resulting magnitude is \");

Send(env,&insdata,\"magnitude\",NULL,&result);

WriteCLIPSValue(env,STDOUT,&result);

Write(env,\"\\n\");

return 0;

}

3\) Define constructs which use the new function in a file called **complex.clp** (or any file; just be sure the call to **Load** loads all necessary constructs prior to execution).

(defclass COMPLEX

(is-a USER)

(slot real)

(slot imag))

(defmethod + ((?a COMPLEX) (?b COMPLEX))

(make-instance of COMPLEX

(real (+ (send ?a get-real) (send ?b get-real)))

(imag (+ (send ?a get-imag) (send ?b get-imag)))))

(defmessage-handler COMPLEX magnitude ()

(sqrt (+ (\*\* ?self:real 2) (\*\* ?self:imag 2))))

4\) Compile all CLIPS files, *except* **main.c**, along with all user files.

5\) Link all object code files.

6\) Execute new CLIPS executable. The output is:

The addition of

\[c1\] of COMPLEX

(real 1)

(imag 10)

and

\[c2\] of COMPLEX

(real 3)

(imag -7)

is

\[gen1\] of COMPLEX

(real 4)

(imag 3)

and the resulting magnitude is 5.000000
