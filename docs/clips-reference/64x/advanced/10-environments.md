# Section 10: Environments

CLIPS provides the ability to create multiple environments into which programs can be loaded and run. Each environment maintains its own set of data structures and can be run independently of the other environments. In many cases, the program's main function will create a single environment to be used as the argument for all embedded API calls. In other cases, such as creating shared libraries or DLLs, new instances of environments will be created as they are needed.

## 10.1 Creating and Destroying Environments

Environments are created using the **CreateEnvironment** function. The return value of the **CreateEnvironment** function is pointer to an **Environment** data structure. This pointer should be used for the embedded API function calls require an Environment pointer argument.

If you have integrated code with CLIPS and use multiple concurrent environments, any functions or extensions which use global data should allocate this data for each environment by using the **AllocateEnvironmentData** function, otherwise one environment may overwrite the data used by another environment.

Once you are done with an environment, it can be deleted with the **DestroyEnvironment** function call. This will deallocate all memory associated with that environment.

The following is an of example of a main program which makes use of multiple environments:

#include \"clips.h\"

int main()

{

Environment \*theEnv1, \*theEnv2;

theEnv1 = CreateEnvironment();

theEnv2 = CreateEnvironment();

Load(theEnv1,\"program1.clp\");

Load(theEnv2,\"program2.clp\");

Reset(theEnv1);

Reset(theEnv2);

Run(theEnv1,-1);

Run(theEnv2,-1);

DestroyEnvironment(theEnv1);

DestroyEnvironment(theEnv2);

}

## 10.2 Environment Data Functions

User-defined functions (or other extensions) that make use of global data that could differ for each environment should allocate and retrieve this data using the environment data functions.

### 10.2.1 Allocating Environment Data

bool AllocateEnvironmentData(\
Environment \*env,\
unsigned id,\
size_t size,\
EnvironmentCleanupFunction f);

bool AddEnvironmentCleanupFunction(\
Environment \*env,\
const char \*name,\
EnvironmentCleanupFunction f,\
int p);

typedef void EnvironmentCleanupFunction(\
Environment \*environment);

The function **AllocateEnvironmentData** allocates memory for storage of data in an environment. Parameter **env** is a pointer to a previously created environment; parameter **id** is an integer that uniquely identifies the data for other functions which reference it; parameter **size** is the amount of memory allocated; and parameter **f** is a callback function invoked when an environment is destroyed. This function returns true if the environment data was successfully allocated; otherwise, it returns false.

The **id** parameter value must be unique; calls to **AllocateEnvironmentData** using a value that has already been allocated will fail. To avoid collisions with environment ids predefined by CLIPS, use the macro constant USER_ENVIRONMENT_DATA as the base index for any ids defined by user code.

For the **size** parameter, you\'ll typically you'll define a struct containing the various values to be stored in the environment data and use the sizeof operator to pass in the size of the struct to this function which will automatically allocate the specified amount of memory, initialize it to contain all zeroes, and then store the memory in the environment position associated with the **id** parameter. Once the base storage has been allocated, additional allocation can be performed by user code. When the environment is destroyed, CLIPS automatically deallocates the amount of memory previously allocated for the base storage.

If the **f** parameter value is not a null pointer, then the specified callback function is invoked when the associated environment is destroyed. CLIPS automatically handles the allocation and deallocation of the base storage for environment data (the amount of data specified by the **size** parameter value). If the base storage includes pointers to memory allocated by user code, then this should be deallocated either by an **EnvironmentCleanupFunction** function specified by this function or the function **AddEnvironmentCleanupFunction**.

Environment cleanup functions specified using by the **AllocateEnvironmentData** function are called in ascending order of their **id** parameter value. If the deallocation of your environment data has order dependencies, you can either assign the ids appropriately to achieve the proper order or you can use the **AddEnvironmentCleanupFunction** function to more explicitly specify the order in which your environment data must be deallocated.

The function **AddEnvironmentCleanupFunction** adds a callback function to the list of functions invoked when an environment is destroyed. Parameter **env** is a pointer to a previously created environment; parameter **name** is a string that uniquely identifies the callback; parameter **f** is a pointer to the callback function of type **EnvironmentCleanupFunction**; and parameter **p** is the priority of the callback function. The **priority** parameter determines the order in which the callback functions are invoked (higher priority items are called first); the values -2000 to 2000 are reserved for internal use by CLIPS. This function returns true if the callback function was successfully added; otherwise, it returns false.

Environment cleanup functions created using this function are called after all the cleanup functions associated with environment data created using **AllocateEnvironmentData** have been called.

### 10.2.2 Retrieving Environment Data

void \*GetEnvironmentData(\
Environment \*env,\
unsigned id);

The function **GetEnvironmentData** returns a pointer to the environment data associated with the identifier specified by parameter **id**.

### 10.2.3 Environment Data Example

As an example of allocating environment data, we'll look at a **get-index** function that returns an integer index starting with one and increasing by one each time it is called. For example:

CLIPS\> (get-index)

1

CLIPS\> (get-index)

2

CLIPS\> (get-index)

3

CLIPS\>

Each environment will need global data to store the current value of the index. The C source code that implements the environment data first needs to specify the position index and specify a data structure for storing the data:

#define INDEX_DATA USER_ENVIRONMENT_DATA + 0

struct indexData

{

long index;

};

#define IndexData(theEnv) \\

((struct indexData \*) GetEnvironmentData(theEnv,INDEX_DATA))

First, the position index GET_INDEX_DATA is defined as USER_ENVIRONMENT_DATA with an offset of zero. If you were to define additional environment data, the offset would be increased each time by one to get to the next available position. Next, the *indexData* struct is defined. This struct contains a single member, *index*, which will use to store the next value returned by the **get-index** function. Finally, the IndexData macro is defined which merely provides a convenient mechanism for access to the environment data.

The next step in the C source code is to add the initialization code to the **UserFunctions** function:

void UserFunctions(

Environment \*env)

{

if (! AllocateEnvironmentData(env,INDEX_DATA,

sizeof(struct indexData),NULL))

{

Writeln(env,\"Error allocating environment data for INDEX_DATA\");

ExitRouter(env,EXIT_FAILURE);

}

IndexData(env)-\>index = 1;

AddUDF(env,\"get-index\",\"l\",0,0,NULL,GetIndex,\"GetIndex\",NULL);

}

First, the call to **AllocateEnvironmentData** is made. If this fails, then an error message is printed and a call to **ExitRouter** is made to terminate the program. Otherwise, the *index* member of the environment data is initialized to one. If a starting value of zero was desired, it would not be necessary to perform any initialization since the value of *index* is automatically initialized to zero when the environment data is initialized. Finally, **AddUDF** is called to register the **get-index** function.

The last piece of the C source code is the **GetIndex** C function which implements the **get-index** function:

void GetIndex(Environment \*,UDFContext \*,UDFValue \*);

void GetIndex(

Environment \*env,

UDFContext \*context,

UDFValue \*returnValue)

{

returnValue-\>integerValue = CreateInteger(env,IndexData(env)-\>index++);

}

#
