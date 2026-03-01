# Section 3: Core Functions

The core functions can be used to embed CLIPS within a simple C program for situations where the user interacts with CLIPS through a text-only computer interface and there is no need for the C program to retrieve information from CLIPS. This removes the need for users to have to interact in any way with the CLIPS command prompt.

## 3.1 Creating and Destroying Environments

### 3.1.1 CreateEnvironment

Environment \*CreateEnvironment();

The function **CreateEnvironment** creates and initializes a CLIPS environment. A pointer of type **Environment \*** is returned to identify the target for other functions which operate on environments. If any error occurs, a null pointer is returned.

### 3.1.2 DestroyEnvironment

bool DestroyEnvironment(\
Environment \*env);

The function **DestroyEnvironment** deallocates all memory associated with an environment. Parameter **env** is a pointer to a previously created environment. This function returns true if successful; otherwise, it returns false. It should not be called to destroy an environment that is currently executing.

## 3.2 Loading Constructs

### 3.2.1 Clear

bool Clear(\
Environment \*env);

The function **Clear** is the C equivalent of the CLIPS **clear** command. Parameter **env** is a pointer to a previously created environment. This function removes all constructs and associated data from the specified environment. It returns true if successful; otherwise, it returns false.

### 3.2.2 Load

LoadError Load(\
Environment \*env,\
const char \*fileName);

typedef enum\
{\
LE_NO_ERROR,\
LE_OPEN_FILE_ERROR,\
LE_PARSING_ERROR,\
} LoadError;

The function **Load** is the C equivalent of the CLIPS **load** command. Parameter **env** is a pointer to a previously created environment; and parameter **fileName** is a full or partial path string to an ASCII or UTF-8 text file containing CLIPS constructs. The error codes for this function are:

  -------------------------------- -------------------------------------------------------------------
  **Error Code**                   **Meaning**

  LE_NO_ERROR                      No error occurred.

  LE_OPEN_FILE_ERROR               An error occurred opening the file.

  LE_PARSING_ERROR                 An error occurred while parsing constructs contained in the file.
  -------------------------------- -------------------------------------------------------------------

### 3.2.3 Bload

bool Bload(\
Environment \*env,\
const char \*fileName);

The function **Bload** is the C equivalent of the CLIPS **bload** command. The **env** parameter is a pointer to a previously created environment; the **filename** parameter is a full or partial path string to a binary save file that was created using the C **Bsave** function or the CLIPS **bsave** command. This function returns true if the file was successfully opened; otherwise, it returns false.

## 3.3 Creating and Removing Facts and Instances

### 3.3.1 AssertString

Fact \*AssertString(\
Environment \*env,\
const char \*str);

AssertStringError GetAssertStringError(\
Environment \*env);

typedef enum\
{\
ASE_NO_ERROR,\
ASE_NULL_POINTER_ERROR,\
ASE_PARSING_ERROR,\
ASE_COULD_NOT_ASSERT_ERROR,\
ASE_RULE_NETWORK_ERROR\
} AssertStringError;

The function **AssertString** is the C equivalent of the CLIPS **assert-string** command. Parameter **env** is a pointer to a previously created environment; and parameter **str** is a pointer to a character array containing the text representation of an ordered or deftemplate fact. An example ordered fact string is \"(colors red green blue)\". An example deftemplate fact string is \"(person (name Fred Jones) (age 37))\". A pointer of type **Fact \*** is returned if a fact is successfully created or already exists; otherwise, a null pointer is returned. If the return value from **AssertString** is persistently stored in a variable or data structure for later reference, then the function **RetainFact** should be called to insure that the reference remains valid even if the fact has been retracted.

The function **GetAssertStringError** returns the error code for the last fact assertion. The error codes are:

  -------------------------------- ------------------------------------------------------------------------------------------------------------
  **Error Code**                   **Meaning**

  ASE_NO_ERROR                     No error occurred.

  ASE_NULL_POINTER_ERROR           The **str** parameter was NULL.

  ASE_PARSING_ERROR                An error was encountered parsing the **str** parameter.

  ASE_COULD_NOT_ASSERT_ERROR       The fact could not be asserted (such as when pattern matching of a fact or instance is already occurring).

  ASE_RULE_NETWORK_ERROR           An error occurred while the assertion was being processed in the rule network.
  -------------------------------- ------------------------------------------------------------------------------------------------------------

### 3.3.2 MakeInstance

Instance \*MakeInstance(\
Environment \*env,\
const char \*str);

typedef enum\
{\
MIE_NO_ERROR,\
MIE_NULL_POINTER_ERROR,\
MIE_PARSING_ERROR,\
MIE_COULD_NOT_CREATE_ERROR,\
MIE_RULE_NETWORK_ERROR\
} MakeInstanceError;

MakeInstanceError GetMakeInstanceError(\
Environment \*env);

The function **MakeInstance** is the C equivalent of the CLIPS **make‑instance** function. Parameter **env** is a pointer to a previously created environment; and parameter **str** is a pointer to a character array containing the text representation of an instance. Example instances strings are \"(\[p1\] of POINT)\" and \"(of POINT (x 1) (y 1))\". Unlike the CLIPS **make-instance** function, slot overrides in the **instanceString** parameter to the function **MakeInstance** are restricted to constants; function calls are not permitted. This function returns a pointer of type **Instance \*** if an instance is successfully created; otherwise, a null pointer it returned. If the return value from **MakeInstance** is persistently stored in a variable or data structure for later reference, then the function **RetainInstance** should be called to insure that the reference remains valid even if the instance has been deleted.

The function **GetMakeInstanceError** returns the error code for the last **MakeInstance** call. The error codes are:

  -------------------------------- ---------------------------------------------------------------------------------------------------------------
  **Error Code**                   **Meaning**

  MIE_NO_ERROR                     No error occurred.

  MIE_NULL_POINTER_ERROR           The **str** parameter was NULL.

  MIE_PARSING_ERROR                An error was encountered parsing the **str** parameter.

  MIE_COULD_NOT_CREATE             The instance could not be created (such as when pattern matching of a fact or instance is already occurring).

  MIE_RULE_NETWORK_ERROR           An error occurred while the instance was being processed in the rule network.
  -------------------------------- ---------------------------------------------------------------------------------------------------------------

### 3.3.3 Retract

RetractError Retract(\
Fact \*f);

typedef enum\
{\
RE_NO_ERROR,\
RE_NULL_POINTER_ERROR,\
RE_COULD_NOT_RETRACT_ERROR,\
RE_RULE_NETWORK_ERROR\
} RetractError;

The function **Retract** is the C equivalent of the CLIPS **retract** command. Parameter **f** is the fact to be retracted. The function error codes are:

  -------------------------------- -------------------------------------------------------------------------------------------------------------
  **Error Code**                   **Meaning**

  RE_NO_ERROR                      No error occurred.

  RE_NULL_POINTER_ERROR            The **f** parameter was NULL.

  RE_COULD_NOT_RETRACT_ERROR       The fact could not be retracted (such as when pattern matching of a fact or instance is already occurring).

  RE_RULE_NETWORK_ERROR            An error occurs while the retraction was being processed in the rule network.
  -------------------------------- -------------------------------------------------------------------------------------------------------------

The caller of **Retract** is responsible for insuring that the fact passed as an argument is still valid. If a persistent reference to this fact was previously created using **RetainFact**, the function **ReleaseFact** should be called to remove that reference.

### 3.3.4 UnmakeInstance

UnmakeInstanceError UnmakeInstance(\
Instance \*i);

typedef enum\
{\
UIE_NO_ERROR,\
UIE_NULL_POINTER_ERROR,\
UIE_COULD_NOT_DELETE_ERROR,\
UIE_DELETED_ERROR,\
UIE_RULE_NETWORK_ERROR\
} UnmakeInstanceError;

The function **UnmakeInstance** is the C equivalent of the CLIPS **unmake-instance** command. Parameter **i** is the instance to be deleted using message-passing. The function error codes are:

  -------------------------------- ---------------------------------------------------------------------------------------------------------------
  **Error Code**                   **Meaning**

  UIE_NO_ERROR                     No error occurred.

  UIE_NULL_POINTER_ERROR           The **i** parameter was NULL.

  UIE_COULD_NOT_DELETE_ERROR       The instance could not be deleted (such as when pattern matching of a fact or instance is already occurring).

  UIE_DELETED_ERROR                The instance was already deleted.

  UIE_RULE_NETWORK_ERROR           An error occured while the deletion was being processed in the rule network
  -------------------------------- ---------------------------------------------------------------------------------------------------------------

The caller of **UnmakeInstance** is responsible for insuring that the instance passed as an argument is still valid. If a persistent reference to this instance was previously created using **RetainInstancee**, the function **ReleaseInstance** should be called to remove that reference.

### 3.3.5 LoadFacts, BinaryLoadFacts, and LoadFactsFromString

long LoadFacts(\
Environment \*env,\
const char \*fileName);

long BinaryLoadFacts(\
Environment \*env,\
const char \*fileName);

long LoadFactsFromString(\
Environment \*env,\
const char \*str,\
size_t length);

The function **LoadFacts** is the C equivalent of the CLIPS **load-facts** command. Parameter **env** is a pointer to a previously created environment; and parameter **fileName** is a full or partial path string to an ASCII or UTF-8 file containing facts. This function returns the number of facts loaded, or -1 if an error occurs.

The function **BinaryLoadFacts** is the C equivalent of the CLIPS **bload‑facts** command. Parameter **env** is a pointer to a previously created environment; and parameter **fileName** is a full or partial path string to binary facts save file created using **BinarySaveFacts**. This function returns the number of facts loaded, or -1 if an error occurs.

The function **LoadFactsFromString** loads a set of facts from a string input source (much like the **LoadFacts** function only using a string for input rather than a file). Parameter **env** is a pointer to a previously created environment; parameter **str** is a string containing facts; and parameter **length** is the maximum number of characters to be read from the input string. If the **length** parameter value is SIZE_MAX, then the **str** parameter value must be terminated by a null character; otherwise, the **length** parameter value indicates the maximum number characters that will be read from the **str** parameter value. This function returns the number of facts loaded, or -1 if an error occurs.

### 3.3.6 SaveFacts and BinarySaveFacts

long SaveFacts(\
Environment \*env,\
const char \*filename,\
SaveScope scope);

long BinarySaveFacts(\
Environment \*env,\
const char \*filename,\
SaveScope scope);

typedef enum\
{\
LOCAL_SAVE,\
VISIBLE_SAVE\
} SaveScope;

The function **SaveFacts** is the C equivalent of the CLIPS **save-facts** command. Parameter **env** is a pointer to a previously created environment; parameter **fileName** is a full or partial path string to the fact save file that will be created; and parameter **scope** indicates whether all facts visible to the current module should be saved (VISIBLE_SAVE) or just those associated with deftemplates defined in the current module (LOCAL_SAVE). This function returns the number of facts saved, or -1 if an error occurs.

The function **BinarySaveFacts** is the C equivalent of the CLIPS **bsave-facts** command. Parameter **env** is a pointer to a previously created environment; parameter **fileName** is a full or partial path string to the binary facts save file that will be created; and parameter **scope** indicates whether all facts visible to the current module should be saved (VISIBLE_SAVE) or just those associated with deftemplates defined in the current module (LOCAL_SAVE). This function returns the number of facts saved, or -1 if an error occurs.

### 3.3.7 LoadInstances, BinaryLoadInstances, and LoadInstancesFromString

long LoadInstances(\
Environment \*env,\
const char \*fileName);

long BinaryLoadInstances(\
Environment \*env,\
const char \*fileName);

long LoadInstancesFromString(\
Environment \*env,\
const char \*str,\
size_t length);

The function **LoadInstances** is the C equivalent of the CLIPS **load-instances** command. Parameter **env** is a pointer to a previously created environment; and parameter **fileName** is a full or partial path string to an ASCII or UTF-8 file containing instances. This function returns the number of instances loaded, or -1 if an error occurs.

The function **BinaryLoadInstances** is the C equivalent of the CLIPS **bload‑instances** command. Parameter **env** is a pointer to a previously created environment; and parameter **fileName** is a full or partial path string to binary instances save file created using **BinarySaveInstances**. This function returns the number of instances loaded, or -1 if an error occurs.

The function **LoadInstancesFromString** loads a set of instances from a string input source (much like the **LoadInstances** function only using a string for input rather than a file). Parameter **env** is a pointer to a previously created environment; parameter **str** is a string containing instances; and parameter **length** is the maximum number of characters to be read from the input string. If the **length** parameter value is SIZE_MAX, then the **str** parameter value must be terminated by a null character; otherwise, the **length** parameter value indicates the maximum number characters that will be read from the **str** parameter value. This function returns the number of instances restored, or -1 if an error occurs.

### 3.3.8 RestoreInstances and RestoreInstancesFromString

long RestoreInstances(\
Environment \*env,\
const char \*fileName);

long RestoreInstancesFromString(\
Environment \*env,\
const char \*str,\
size_t length);

The function **RestoreInstances** is the C equivalent of the CLIPS **restore-instances** command. Parameter **env** is a pointer to a previously created environment; and parameter **fileName** is a full or partial path string to an ASCII or UTF-8 file containing instances. This function returns the number of instances restored, or -1 if an error occurs.

The function **RestoreInstancesFromString** loads a set of instances from a string input source (much like the **RestoreInstances** function only using a string for input rather than a file). Parameter **env** is a pointer to a previously created environment; parameter **str** is a string containing instances; and parameter **length** is the maximum number of characters to be read from the input string. If the **length** parameter value is SIZE_MAX, then the **str** parameter value must be terminated by a null character; otherwise, the **length** parameter value indicates the maximum number characters that will be read from the **str** parameter value. This function returns the number of instances restored, or -1 if an error occurs.

### 3.3.9 SaveInstances and BinarySaveInstances

long SaveInstances(\
Environment \*env,\
const char \*fileName,\
SaveScope saveCode);

long BinarySaveInstances(\
Environment \*env,\
const char \*fileName,\
SaveScope saveCode);

typedef enum\
{\
LOCAL_SAVE,\
VISIBLE_SAVE\
} SaveScope;

The function **SaveInstances** is the C equivalent of the CLIPS **save-instances** command. Parameter **env** is a pointer to a previously created environment; parameter **fileName** is a full or partial path string to the instance save file that will be created; and parameter **scope** indicates whether all instances visible to the current module should be saved (VISIBLE_SAVE) or just those associated with defclasses defined in the current module (LOCAL_SAVE). This function returns the number of instances saved, or -1 if an error occurs.

The function **BinarySaveInstances** is the C equivalent of the CLIPS **bsave-instances** command. Parameter **env** is a pointer to a previously created environment; parameter **fileName** is a full or partial path string to the binary instances save file that will be created; and parameter **scope** indicates whether all instances visible to the current module should be saved (VISIBLE_SAVE) or just those associated with defclasses defined in the current module (LOCAL_SAVE). This function returns the number of instances saved, or -1 if an error occurs.

## 3.4 Executing Rules

### 3.4.1 Reset

void Reset(\
Environment \*env);

The function **Reset** is the C equivalent of the CLIPS **reset** command. Parameter **env** is a pointer to a previously created environment. This function removes all facts and instances; creates facts and instances defined in deffacts and definstances constructs; and resets the values of global variables in the specified environment.

### 3.4.2 Run

long long Run(\
Environment \*env,\
long long limit);

The function **Run** is the C equivalent of the CLIPS **run** command. Parameter **env** is a pointer to a previously created environment; and parameter **limit** parameter is the maximum number of rules that will fire before the function returns. If the **limit** parameter value is negative, rules will fire until the agenda is empty. The return value of this function is the number of rules that were fired.

## 3.5 Debugging

### 3.5.1 DribbleOn and DribbleOff

bool DribbleOn(\
Environment \*env,\
const char \*fileName);

bool DribbleOff(\
Environment \*env);

The function **DribbleOn** is the C equivalent of the CLIPS **dribble-on** command. Parameter **env** is a pointer to a previously created environment; and parameter **fileName** is a full or partial path string to the dribble file to be created. This function returns true if the dribble file is successfully opened; otherwise, it returns false.

The function **DribbleOff** is the C equivalent of the CLIPS **dribble-off** command. Parameter **env** is a pointer to a previously created environment. This function returns true if the dribble file is successfully closed; otherwise, it returns false.

### 3.5.2 Watch and Unwatch

void Watch(\
Environment \*env,\
WatchItem item);

void Unwatch(\
Environment \*env,\
WatchItem item);

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

The function **Watch** is the C equivalent of the CLIPS **watch** command. The function **Unwatch** is the C equivalent of the CLIPS **unwatch** command. Parameter **env** is a pointer to a previously created environment; and parameter **item** is one of the specified **WatchItem** enumeration values to be enabled (for watch) or disabled (for unwatch). If the **ALL** enumeration value is specified, then all watch items will be enabled (for watch) or disabled (for unwatch).

## 3.6 Examples

### 3.6.1 Hello World

This example demonstrates how to load and run rules from a C program. The following output shows how you would typically perform this task from the CLIPS command prompt:

CLIPS\> (load \"hello.clp\")

\*

TRUE

CLIPS\> (reset)

CLIPS\> (run)

Hello World!

CLIPS\>

To achieve the same result from a C program, first create a text file named *hello.clp* with the following contents:

(defrule hello

=\>

(println \"Hello World!\"))

Next, change the contents of the main.c source file to the following:

#include \"clips.h\"

int main()

{

Environment \*env;

env = CreateEnvironment();

// The file hello.clp must be in the same directory

// as the CLIPS executable or you must specify the

// full directory path as part of the file name.

Load(env,\"hello.clp\");

Reset(env);

Run(env,-1);

DestroyEnvironment(env);

}

Finally, recompile the CLIPS source code to create an executable.

The following output will be produced when the program is run:

Hello World!

### 3.6.2 Debugging

This example demonstrates how to generate and capture debugging information from a C program. The following output shows how you would typically perform this task from the CLIPS command prompt:

CLIPS\> (load sort.clp)

%\*

TRUE

CLIPS\> (watch facts)

CLIPS\> (watch rules)

CLIPS\> (watch activations)

CLIPS\> (dribble-on \"sort.dbg\")

TRUE

CLIPS\> (reset)

CLIPS\> (assert (list (numbers 61 31 27 48)))

==\> f-1 (list (numbers 61 31 27 48))

==\> Activation 0 sort: f-1

==\> Activation 0 sort: f-1

\<Fact-1\>

CLIPS\> (run)

FIRE 1 sort: f-1

\<== f-1 (list (numbers 61 31 27 48))

\<== Activation 0 sort: f-1

==\> f-1 (list (numbers 31 61 27 48))

==\> Activation 0 sort: f-1

FIRE 2 sort: f-1

\<== f-1 (list (numbers 31 61 27 48))

==\> f-1 (list (numbers 31 27 61 48))

==\> Activation 0 sort: f-1

==\> Activation 0 sort: f-1

FIRE 3 sort: f-1

\<== f-1 (list (numbers 31 27 61 48))

\<== Activation 0 sort: f-1

==\> f-1 (list (numbers 27 31 61 48))

==\> Activation 0 sort: f-1

FIRE 4 sort: f-1

\<== f-1 (list (numbers 27 31 61 48))

==\> f-1 (list (numbers 27 31 48 61))

CLIPS\> (dribble-off)

TRUE

CLIPS\>

To achieve the same result from a C program, first create a text file named *sort.clp* with the following contents:

(deftemplate list

(multislot numbers))

(defrule sort

?f \<- (list (numbers \$?b ?x ?y&:(\> ?x ?y) \$?e))

=\>

(modify ?f (numbers ?b ?y ?x ?e)))

Next, change the contents of the main.c source file to the following:

#include \"clips.h\"

int main()

{

Environment \*env;

env = CreateEnvironment();

Load(env,\"sort.clp\");

Watch(env,FACTS);

Watch(env,RULES);

Watch(env,ACTIVATIONS);

DribbleOn(env,\"sort.dbg\");

Reset(env);

AssertString(env,\"(list (numbers 61 31 27 48))\");

Run(env,-1);

DribbleOff(env);

DestroyEnvironment(env);

}

Finally, recompile the CLIPS source code to create an executable.

The following output will be produced when the program is run:

==\> f-1 (list (numbers 61 31 27 48))

==\> Activation 0 sort: f-1

==\> Activation 0 sort: f-1

FIRE 1 sort: f-1

\<== f-1 (list (numbers 61 31 27 48))

\<== Activation 0 sort: f-1

==\> f-2 (list (numbers 31 61 27 48))

==\> Activation 0 sort: f-2

FIRE 2 sort: f-2

\<== f-2 (list (numbers 31 61 27 48))

==\> f-3 (list (numbers 31 27 61 48))

==\> Activation 0 sort: f-3

==\> Activation 0 sort: f-3

FIRE 3 sort: f-3

\<== f-3 (list (numbers 31 27 61 48))

\<== Activation 0 sort: f-3

==\> f-4 (list (numbers 27 31 61 48))

==\> Activation 0 sort: f-4

FIRE 4 sort: f-4

\<== f-4 (list (numbers 27 31 61 48))

==\> f-5 (list (numbers 27 31 48 61))

The file *sort.dbg* will contain the same output that is printed to the screen.

#
