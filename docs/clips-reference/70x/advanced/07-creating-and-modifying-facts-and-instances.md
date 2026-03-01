# Section 7: Creating and Modifying Facts and Instances

This section documents the **FactBuilder**, **FactModifier**, **InstanceBuilder**, and **InstanceModifier** APIs.

## 7.1 FactBuilder Functions

The **FactBuilder** functions provide a mechanism for dynamically creating facts. A **FactBuilder** is created using the **CreateFactBuilder** function. The slot assignment functions described in section 7.5 are used to assign slot values to the fact being created. Once slots have been assigned, the **FBAssert** function can be used to assert the fact and then reset the **FactBuilder** to its initial state. Alternately, the **FBAbort** function can be called to cancel the creation of the current fact and reset the **FactBuilder** to its initial state. The **FBSetDeftemplate** function can be called to initialize the **FactBuilder** to create facts of a different deftemplate type. Once it is no longer needed, the **FactBuilder** can be deallocated using the **FBDispose** function.

The **FactBuilder** type definition is:

typedef struct factBuilder\
{\
} FactBuilder;

The prototypes for the **FactBuilder** functions are:

FactBuilder \*CreateFactBuilder(\
Environment \*env,\
const char \*name);

Fact \*FBAssert(\
FactBuilder \*fb);

void FBDispose(\
FactBuilder \*fb);

FactBuilderError FBSetDeftemplate(\
FactBuilder \*fb,\
const char \*name);

void FBAbort(\
FactBuilder \*fb);

FactBuilderError FBError (\
Environment \*env);

typedef enum\
{\
FBE_NO_ERROR,\
FBE_NULL_POINTER_ERROR,\
FBE_DEFTEMPLATE_NOT_FOUND_ERROR,\
FBE_IMPLIED_DEFTEMPLATE_ERROR,\
FBE_COULD_NOT_ASSERT_ERROR,\
FBE_RULE_NETWORK_ERROR\
} FactBuilderError;

The function **CreateFactBuilder** allocates and initializes a struct of type **FactBuilder**. Parameter **env** is a pointer to a previously created environment; and parameter **name** is the name of the deftemplate that will be created by the fact builder. Only deftemplates that have been explicitly defined can by used with a **FactBuilder**. The **name** parameter can be NULL in which case the **FBSetDeftemplate** function must be used to assign the deftemplate before slot values can be assigned and facts can be asserted.

If successful, this function returns a pointer to the created **FactBuilder**; otherwise, it returns a null pointer. The error code for the function call can be retrieved using the **FBError** function:

  -------------------------------------- --------------------------------------------------------------------------------------------
  **Error Code**                         **Meaning**

  FBE_NO_ERROR                           No error occurred.

  FBE_DEFTEMPLATE_NOT_FOUND_ERROR        The specified deftemplate was either not in scope in the current module or does not exist.

  FBE_IMPLIED_DEFTEMPLATE_ERROR          The specified deftemplate was not explicitly defined.
  -------------------------------------- --------------------------------------------------------------------------------------------

The function **FBAssert** asserts the fact based on slot assignments made to the fact builder specified by parameter **fb**. Slots which have not been explicitly assigned a value are set to their default value. If successful, this function returns a pointer to the asserted **Fact**; otherwise it returns a null pointer. Slot assignments are discarded after the fact is asserted, so slot values need to be reassigned if the fact builder is used to build another fact. The error code for the function call be retrieved using the **FBError** function:

  --------------------------------- ------------------------------------------------------------------------------------------------------------
  **Error Code**                    **Meaning**

  FBE_NO_ERROR                      No error occurred.

  FBE_NULL_POINTER_ERROR            The **FactBuilder** does not have an associated deftemplate.

  FBE_COULD_NOT_ASSERT_ERROR        The fact could not be asserted (such as when pattern matching of a fact or instance is already occurring).

  FBE_RULE_NETWORK_ERROR            An error occurred while the assertion was being processed in the rule network.
  --------------------------------- ------------------------------------------------------------------------------------------------------------

The function **FBDispose** deallocates the memory associated with the **FactBuilder** specified by parameter **fb**.

The function **FBSetDeftemplate** changes the type of fact created by the fact builder to the deftemplate specified by the parameter **name**. Any slot values that have been assigned to the builder are discarded. The error codes for this function are:

  ------------------------------------- --------------------------------------------------------------------------
  **Error Code**                        **Meaning**

  FBE_NO_ERROR                          No error occurred.

  FBE_NULL_POINTER_ERROR                The parameter **fb** was NULL.

  FBE_DEFTEMPLATE_NOT_FOUND_ERROR       The deftemplate was not in scope in the current module or does not exist

  FBE_IMPLIED_DEFTEMPLATE_ERROR         The deftemplate was not explicitly defined.
  ------------------------------------- --------------------------------------------------------------------------

The function **FBAbort** discards the slot value assignments that have been made for the fact builder specified by parameter **fb**.

## 7.2 FactModifier Functions

The **FactModifier** functions provide a mechanism for dynamically modifying facts. A **FactModifier** is created using the **CreateFactModifier** function. The slot assignment functions described in section 7.5 are used to assign slot values to the fact being modified. Once slots have been assigned, the **FMModify** function can be used to modify the fact and then reset the **FactModifier** to its initial state. Alternately, the **FMAbort** function can be called to cancel the modification of the current fact and reset the **FactModifier** to its initial state. The **FMSetFact** function can be called to initialize the **FactModifier** to modify a different fact. Once it is no longer needed, the **FactModifier** can be deallocated using the **FMDispose** function.

The **FactModifier** type definition is:

typedef struct factModifier\
{\
} FactModifier;

The prototypes for the **FactModifier** functions are:

FactModifier \*CreateFactModifier(\
Environment \*env,\
Fact \*f);

Fact \*FMModify(\
FactModifier \*fm);

void FMDispose(\
FactModifier \*fm);

FactModifierError FMSetFact(\
FactModifier \*fm,\
Fact \*f);

void FMAbort(\
FactModifier \*fm);

FactModifierError FMError (\
Environment \*env);

typedef enum\
{\
FME_NO_ERROR,\
FME_NULL_POINTER_ERROR,\
FME_RETRACTED_ERROR,\
FME_IMPLIED_DEFTEMPLATE_ERROR,\
FME_COULD_NOT_MODIFY_ERROR,\
FME_RULE_NETWORK_ERROR\
} FactModifierError;

The function **CreateFactModifier** allocates and initializes a struct of type **FactModifier**. Parameter **env** is a pointer to a previously created environment; and parameter **f** is a pointer to the **Fact** to be modified. The **f** parameter can be NULL in which case the **FMSetFact** function must be used to assign the fact before slot values can be assigned and the fact modified.

If successful, this function returns a pointer to the created **FactModifier**; otherwise, it returns a null pointer. The error code for the function call be retrieved using the **FMError** function:

  ---------------------------------- --------------------------------------------------------------------------------------
  **Error Code**                     **Meaning**

  FME_NO_ERROR                       No error occurred.

  FME_RETRACTED_ERROR                The specified fact to be modified has been retracted.

  FBE_IMPLIED_DEFTEMPLATE_ERROR      The specified fact is associated with a deftemplate that was not explicitly defined.
  ---------------------------------- --------------------------------------------------------------------------------------

The function **FMModify** modifies the fact based on slot assignments made to the fact modifier specified by parameter **fm**. If successful, this function returns a pointer to the modified **Fact**; otherwise it returns a null pointer. Slot assignments are discarded after the fact is asserted, so slot values need to be reassigned if the fact builder is used to modify another fact. The error code for the function call be retrieved using the **FMError** function:

  --------------------------------- ------------------------------------------------------------------------------------------------------------
  **Error Code**                    **Meaning**

  FME_NO_ERROR                      No error occurred.

  FME_NULL_POINTER_ERROR            The **FactModifier** does not have an associated fact.

  FME_RETRACTED_ERROR               The fact was retracted and cannot be modified.

  FME_COULD_NOT_MODIFY_ERROR        The fact could not be modified (such as when pattern matching of a fact or instance is already occurring).

  FME_RULE_NETWORK_ERROR            An error occurred while the modification was being processed in the rule network.
  --------------------------------- ------------------------------------------------------------------------------------------------------------

The function **FMDispose** deallocates the memory associated with the **FactModifier** specified by parameter **fm**.

The function **FMSetFact** changes the fact being modified to the value specified by parameter **f**. Any slot values that have been assigned to the modifier are discarded. The error codes for this function are:

  ---------------------------------- --------------------------------------------------------------------------------------
  **Error Code**                     **Meaning**

  FME_NO_ERROR                       No error occurred.

  FME_NULL_POINTER_ERROR             The parameter **fm** was NULL.

  FME_RETRACTED_ERROR                The fact has been retracted and cannot be modified.

  FME_IMPLIED_DEFTEMPLATE_ERROR      The specified fact is associated with a deftemplate that was not explicitly defined.
  ---------------------------------- --------------------------------------------------------------------------------------

The function **FMAbort** discards the slot value assignments that have been made for the fact modifier specified by parameter **fm**.

## 7.3 InstanceBuilder Functions

The **InstanceBuilder** functions provide a mechanism for dynamically creating instances. An **InstanceBuilder** is created using the **CreateInstanceBuilder** function. The slot assignment functions described in section 7.5 are used to assign slot values to the instance being created. Once slots have been assigned, the **IBMake** function can be used to create the instance and then reset the **InstanceBuilder** to its initial state. Alternately, the **IBAbort** function can be called to cancel the creation of the current instance and reset the **InstanceBuilder** to its initial state. The **FBSetDefclass** function can be called to initialize the **InstanceBuilder** to create instances of a different defclass type. Once it is no longer needed, the **InstanceBuilder** can be deallocated using the **IBDispose** function.

The **InstanceBuilder** type definition is:

typedef struct instanceBuilder

{

} InstanceBuilder;

The prototypes for the **InstanceBuilder** functions are:

InstanceBuilder \*CreateInstanceBuilder(\
Environment \*env,\
const char \*name);

Instance \*IBMake(\
InstanceBuilder \*ib,\
const char \*name);

void IBDispose(\
InstanceBuilder \*ib);

InstanceBuilderError IBSetDefclass(\
InstanceBuilder \*ib,\
const char \*name);

void IBAbort(\
InstanceBuilder \*ib);

InstanceBuilderError IBError (\
Environment \*env);

typedef enum\
{\
IBE_NO_ERROR,\
IBE_NULL_POINTER_ERROR,\
IBE_DEFCLASS_NOT_FOUND_ERROR,\
IBE_COULD_NOT_CREATE_ERROR,\
IBE_RULE_NETWORK_ERROR\
} InstanceBuilderError;

The function **CreateInstanceBuilder** allocates and initializes a struct of type **InstanceBuilder**. Parameter **env** is a pointer to a previously created environment; and parameter **name** is the name of the instance defclass that will be created by the instance builder. The **name** parameter can be NULL in which case the **FBSetDefclass** function must be used to assign the defclass before slot values can be assigned and instances can be created.

If successful, this function returns a pointer to the created **InstanceBuilder**; otherwise, it returns a null pointer. The error code for the function call be retrieved using the **IBError** function:

  --------------------------------- -----------------------------------------------------------------------------------------
  **Error Code**                    **Meaning**

  IBE_NO_ERROR                      No error occurred.

  IBE_DEFCLASS_NOT_FOUND_ERROR      The specified defclass was either not in scope in the current module or does not exist.
  --------------------------------- -----------------------------------------------------------------------------------------

The function **IBMake** creates the instance based on slot assignments made to the instance builder specified by parameter **ib**. Slots which have not been explicitly assigned a value are set to their default value. If the parameter **name** is a null pointer, then an instance name is generated for the newly created instance; otherwise, the **name** parameter value is used as the instance name. If successful, this function returns a pointer to the created **Instance**; otherwise it returns a null pointer. Slot assignments are discarded after the instance is created, so slot values need to be reassigned if the instance builder is used to build another instance. The error code for the function call be retrieved using the **IBError** function:

  --------------------------------- ---------------------------------------------------------------------------------------------------------------
  **Error Code**                    **Meaning**

  IBE_NO_ERROR                      No error occurred.

  IBE_NULL_POINTER_ERROR            The **InstanceBuilder** does not have an associated defclass.

  IBE_COULD_NOT_CREATE              The instance could not be created (such as when pattern matching of a fact or instance is already occurring).

  IBE_RULE_NETWORK_ERROR            An error occurred while the instance was being processed in the rule network.
  --------------------------------- ---------------------------------------------------------------------------------------------------------------

The function **IBDispose** deallocates the memory associated with the **InstanceBuilder** specified by parameter **ib**.

The function **IBSetDefclass** changes the type of instance created by the instance builder to the defclass specified by the parameter **name**. Any slot values that have been assigned to the builder are discarded. The error codes for this function are:

  --------------------------------- -----------------------------------------------------------------------
  **Error Code**                    **Meaning**

  IBE_NO_ERROR                      No error occurred.

  IBE_NULL_POINTER_ERROR            The parameter **ib** was NULL.

  IBE_DEFCLASS_NOT_FOUND_ERROR      The defclass is not in scope in the current module or does not exist.
  --------------------------------- -----------------------------------------------------------------------

The function **IBAbort** discards the slot value assignments that have been made for the instance builder specified by parameter **ib**.

## 7.4 InstanceModifier Functions

The **InstanceModifier** functions provide a mechanism for dynamically modifying instances. An **InstanceModifier** is created using the **CreateInstanceModifier** function. The slot assignment functions described in section 7.5 are used to assign slot values to the instance being modified. Once slots have been assigned, the **IMModify** function can be used to modify the instance and then reset the **InstanceModifier** to its initial state. Alternately, the **IMAbort** function can be called to cancel the modification of the current instance and reset the **InstanceModifier** to its initial state. The **IMSetInstance** function can be called to initialize the **InstanceModifier** to modify a different instance. Once it is no longer needed, the **InstanceModifier** can be deallocated using the **IMDispose** function.

The **InstanceModifier** type definition is:

typedef struct instanceModifier

{

} InstanceModifier;

The prototypes for the **InstanceModifier** functions are:

InstanceModifier \*CreateInstanceModifier(\
Environment \*env,\
Instance \*i);

Instance \*IMModify(\
InstanceModifier \*im);

void IMDispose(\
InstanceModifier \*im);

InstanceModifierError IMSetInstance(\
InstanceModifier \*im,\
Instance \*i);

void IMAbort(\
InstanceModifier \*im);

InstanceModifierError IMError (\
Environment \*env);

typedef enum\
{\
IME_NO_ERROR,\
IME_NULL_POINTER_ERROR,\
IME_DELETED_ERROR,\
IME_COULD_NOT_MODIFY_ERROR,\
IME_RULE_NETWORK_ERROR\
} InstanceModifierError;

The function **CreateInstanceModifier** allocates and initializes a struct of type **InstanceModifier**. Parameter **env** is a pointer to a previously created environment; and parameter **i** is a pointer to the **Instance** to be modified. The **i** parameter can be NULL in which case the **IMSetInstance** function must be used to assign the instance before slot values can be assigned and instance modified.

If successful, this function returns a pointer to the created **InstanceModifier**; otherwise, it returns a null pointer. The error code for the function call be retrieved using the **IMError** function:

  --------------------------------- ---------------------------------------------------------
  **Error Code**                    **Meaning**

  IME_NO_ERROR                      No error occurred.

  IME_DELETED_ERROR                 The specified instance to be modified has been deleted.
  --------------------------------- ---------------------------------------------------------

The function **IMModify** modifies the instance based on slot assignments made to the instance modifier specified by parameter **im**. If successful, this function returns a pointer to the modified **Instance**; otherwise it returns a null pointer. Slot assignments are discarded after the instance is modified, so slot values need to be reassigned if the instance builder is used to modify a different instance. The error code for the function call be retrieved using the **IMError** function:

  --------------------------------- ----------------------------------------------------------------------------------------------------------------
  **Error Code**                    **Meaning**

  IME_NO_ERROR                      No error occurred.

  IME_NULL_POINTER_ERROR            The **InstanceModifier** does not have an associated instance.

  IME_DELETED                       The instance was deleted and cannot be modified.

  IME_COULD_NOT_MODIFY              The instance could not be modified (such as when pattern matching of a fact or instance is already occurring).

  IME_RULE_NETWORK_ERROR            An error occurred while the modification was being processed in the rule network.
  --------------------------------- ----------------------------------------------------------------------------------------------------------------

The function **IMDispose** deallocates the memory associated with the **InstanceModifier** specified by parameter **im**.

The function **IMSetInstance** changes the instance being modified to the value specified by parameter **i**. Any slot values that have been assigned to the modifier are discarded. The error codes for this function are:

  --------------------------------- -------------------------------------------------------
  **Error Code**                    **Meaning**

  IME_NO_ERROR                      No error occurred.

  IME_NULL_POINTER_ERROR            The **im** parameter was NULL.

  IME_DELETED_ERROR                 The instance has been deleted and cannot be modified.
  --------------------------------- -------------------------------------------------------

The function **IMAbort** discards the slot value assignments that have been made for the instance modifier specified by parameter **im**.

## 7.5 Slot Assignment Functions

The **FactBuilder**, **FactModifier**, **InstanceBuilder**, and **InstanceModifier** APIs each provide a set of functions for assigning slot values. The slot assignment functions return one of the following **PutSlotError** enumerations:

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
PSE_ALLOWED_CLASSES_ERROR\
} PutSlotError;

The meanings of the error codes are:

  --------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------
  **Error Code**                    **Meaning**

  PSE_NO_ERROR                      No error occurred.

  PSE_NULL_POINTER_ERROR            One of the function arguments was a NULL pointer.

  PSE_INVALID_TARGET_ERROR          A fact/instance cannot be modified because the fact or instance pointer assigned to a **FactModifier** or **InstanceModifier** has been deleted.

  PSE_SLOT_NOT_FOUND_ERROR          The fact or instance does not have the specified slot.

  PSE_TYPE_ERROR                    The slot value violates the type constraint.

  PSE_RANGE_ERROR                   The slot value violates the range constraint.

  PSE_ALLOWED_VALUES_ERROR          The slot value violates the allowed values constraint.

  PSE_CARDINALITY_ERROR             The slot value violates the slot cardinality.

  PSE_ALLOWED_CLASSES_ERROR         The slot value violates the allowed classes constraint.
  --------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------

### 7.5.1 Assigning Generic Slot Values

  -----------------------------------------------------------------------
  PutSlotError FBPutSlot(\            PutSlotError IBPutSlot(\
  FactBuilder \*fb,\                  InstanceBuilder \*ib,\
  const char \*name,\                 const char \*name,\
  CLIPSValue \*v);                    CLIPSValue \*v);
  ----------------------------------- -----------------------------------
  PutSlotError FMPutSlot(\            PutSlotError IMPutSlot(\
  FactModifier \*fm,\                 InstanceModifier \*im,\
  const char \*name,\                 const char \*name,\
  CLIPSValue \*v);                    CLIPSValue \*v);

  -----------------------------------------------------------------------

The function **FBPutSlot** sets the slot specified by the parameter **name** to the value specified by parameter **v** for the fact builder specified by parameter **fb**. This function returns true if the slot was successfully set; otherwise, it returns false.

The function **FMPutSlot** sets the slot specified by the parameter **name** to the value specified by parameter **v** for the fact modifier specified by parameter **fm**. This function returns true if the slot was successfully set; otherwise, it returns false.

The function **IBPutSlot** sets the slot specified by the parameter **name** to the value specified by parameter **v** for the instance builder specified by parameter **ib**. This function returns true if the slot was successfully set; otherwise, it returns false.

The function **IMPutSlot** sets the slot specified by the parameter **name** to the value specified by parameter **v** for the instance modifier specified by parameter **im**. This function returns true if the slot was successfully set; otherwise, it returns false.

### 7.5.2 Assigning Integer Slot Values

  -----------------------------------------------------------------------------
  PutSlotError FBPutSlotCLIPSInteger(\   PutSlotError FMPutSlotCLIPSInteger(\
  FactBuilder \*fb,\                     FactModifier \*fm,\
  const char \*name,\                    const char \*name,\
  CLIPSInteger \*i);                     CLIPSInteger \*i);
  -------------------------------------- --------------------------------------
  PutSlotError FBPutSlotInteger(\        PutSlotError FMPutSlotInteger(\
  FactBuilder \*fb,\                     FactModifier \*fm,\
  const char \*name,\                    const char \*name,\
  long long i);                          long long i);

  PutSlotError IBPutSlotCLIPSInteger(\   PutSlotError IMPutSlotCLIPSInteger(\
  InstanceBuilder \*ib,\                 InstanceModifier \*im,\
  const char \*name,\                    const char \*name,\
  CLIPSInteger \*i);                     CLIPSInteger \*i);

  PutSlotError IBPutSlotInteger(\        PutSlotError IMPutSlotInteger(\
  InstanceBuilder \*ib,\                 InstanceModifier \*im,\
  const char \*name,\                    const char \*name,\
  long long i);                          long long i);
  -----------------------------------------------------------------------------

These functions assign an integer value in one of various forms to a **FactBuilder** (for parameter **fb**), **FactModifier** (for parameter **fm**), **InstanceBuilder** (for parameter ib), or **InstanceModifier** (for parameter **im**). Parameter **name** is the slot of either the fact or instance to be assigned. Parameter i is the value assigned to the slot: a **CLIPSInteger**, int, long, or long long value. These functions return true if the slot was successfully set; otherwise, they return false.

### 7.5.3 Assigning Float Slot Values

  -------------------------------------------------------------------------
  PutSlotError FBPutSlotCLIPSFloat(\   PutSlotError FMPutSlotCLIPSFloat(\
  FactBuilder \*fb,\                   FactModifier \*fm,\
  const char \*name,\                  const char \*name,\
  CLIPSFloat \*f);                     CLIPSFloat \*f);
  ------------------------------------ ------------------------------------
  PutSlotError FBPutSlotFloat(\        PutSlotError FMPutSlotFloat(\
  FactBuilder \*fb,\                   FactModifier \*fm,\
  const char \*name,\                  const char \*name,\
  double f);                           double f);

  PutSlotError IBPutSlotCLIPSFloat(\   PutSlotError IMPutSlotCLIPSFloat(\
  InstanceBuilder \*ib,\               InstanceModifier \*im,\
  const char \*name,\                  const char \*name,\
  CLIPSFloat \*f);                     CLIPSFloat \*f);

  PutSlotError IBPutSlotFloat(\        PutSlotError IMPutSlotFloat(\
  InstanceBuilder \*ib,\               InstanceModifier \*im,\
  const char \*name,\                  const char \*name,\
  double f);                           double f);
  -------------------------------------------------------------------------

These functions assign a floating point value in one of various forms to a **FactBuilder** (for parameter **fb**), **FactModifier** (for parameter **fm**), **InstanceBuilder** (for parameter ib), or **InstanceModifier** (for parameter **im**). Parameter **name** is the slot of either the fact or instance to be assigned. Parameter **f** is the value assigned to the slot: a **CLIPSFloat**, float, or double value. These functions return true if the slot was successfully set; otherwise, they return false.

### 7.5.4 Assigning Symbol, String, and Instance Name Slot Values

  -----------------------------------------------------------------------------
  PutSlotError FBPutSlotCLIPSLexeme(\    PutSlotError FMPutSlotCLIPSLexeme(\
  FactBuilder \*fb,\                     FactModifier \*fm,\
  const char \*name,\                    const char \*name,\
  CLIPSLexeme \*lex);                    CLIPSLexeme \*lex);
  -------------------------------------- --------------------------------------
  PutSlotError FBPutSlotInstanceName(\   PutSlotError FMPutSlotInstanceName(\
  FactBuilder \*fb,\                     FactModifier \*fm,\
  const char \*name,\                    const char \*name,\
  const char \*lex);                     const char \*lex);

  PutSlotError FBPutSlotString(\         PutSlotError FMPutSlotString(\
  FactBuilder \*fb,\                     FactModifier \*fm,\
  const char \*name,\                    const char \*name,\
  const char \*lex);                     const char \*lex);

  PutSlotError FBPutSlotSymbol(\         PutSlotError FMPutSlotSymbol(\
  FactBuilder \*fb,\                     FactModifier \*fm,\
  const char \*name,\                    const char \*name,\
  const char \*lex);                     const char \*lex);

  PutSlotError IBPutSlotCLIPSLexeme(\    PutSlotError IMPutSlotCLIPSLexeme(\
  InstanceBuilder \*ib,\                 InstanceModifier \*im,\
  const char \*name,\                    const char \*name,\
  CLIPSLexeme \*lex);                    CLIPSLexeme \*lex);

  PutSlotError IBPutSlotInstanceName(\   PutSlotError IMPutSlotInstanceName(\
  InstanceBuilder \*ib,\                 InstanceModifier \*im,\
  const char \*name,\                    const char \*name,\
  const char \*lex);                     const char \*lex);

  PutSlotError IBPutSlotString(\         PutSlotError IMPutSlotString(\
  InstanceBuilder \*ib,\                 InstanceModifier \*im,\
  const char \*name,\                    const char \*name,\
  const char \*lex);                     const char \*lex);

  PutSlotError IBPutSlotSymbol(\         PutSlotError IMPutSlotSymbol(\
  InstanceBuilder \*ib,\                 InstanceModifier \*im,\
  const char \*name,\                    const char \*name,\
  const char \*lex);                     const char \*lex);
  -----------------------------------------------------------------------------

These functions assign a lexeme value (symbol, string, or instance name) in one of various forms to a **FactBuilder** (for parameter **fb**), **FactModifier** (for parameter **fm**), **InstanceBuilder** (for parameter ib), or **InstanceModifier** (for parameter **im**). Parameter **name** is the slot of either the fact or instance to be assigned. Parameter **lex** is the value assigned to the slot: a **CLIPSLexeme** or C string. These functions return true if the slot was successfully set; otherwise, they return false.

### 7.5.5 Assigning Fact and Instance Values

  -----------------------------------------------------------------------
  PutSlotError FBPutSlotFact(\        PutSlotError IBPutSlotFact(\
  FactBuilder \*fb,\                  InstanceBuilder \*ib,\
  const char \*name,\                 const char \*name,\
  Fact \*f);                          Fact \*f);
  ----------------------------------- -----------------------------------
  PutSlotError FBPutSlotInstance(\    PutSlotError IBPutSlotInstance(\
  FactBuilder \*fb,\                  InstanceBuilder \*ib,\
  const char \*name,\                 const char \*name,\
  Instance \*i);                      Instance \*i);

  PutSlotError FMPutSlotFact(\        PutSlotError IMPutSlotFact(\
  FactModifier \*fm,\                 InstanceModifier \*im,\
  const char \*name,\                 const char \*name,\
  Fact \*f);                          Fact \*f);

  PutSlotError FMPutSlotInstance(\    PutSlotError IMPutSlotInstance(\
  FactModifier \*fm,\                 InstanceModifier \*im,\
  const char \*name,\                 const char \*name,\
  Instance \*i);                      Instance \*i);
  -----------------------------------------------------------------------

These functions assign a fact or instance value to a **FactBuilder** (for parameter **fb**), **FactModifier** (for parameter **fm**), **InstanceBuilder** (for parameter ib), or **InstanceModifier** (for parameter **im**). Parameter **name** is the slot of either the fact or instance to be assigned. Parameter **f** is the **Fact** value assigned to the slot; or parameter **i** is the **Instance** value assigned to the slot. These functions return true if the slot was successfully set; otherwise, they return false.

### 7.5.6 Assigning Multifield and External Address Slot Values

  -----------------------------------------------------------------------------------
  PutSlotError FBPutSlotExternalAddress(\   PutSlotError IBPutSlotExternalAddress(\
  FactBuilder \*fb,\                        InstanceBuilder \*ib,\
  const char \*name,\                       const char \*name,\
  CLIPSExternalAddress \*ea);               CLIPSExternalAddress \*ea);
  ----------------------------------------- -----------------------------------------
  PutSlotError FBPutSlotMultifield(\        PutSlotError IBPutSlotMultifield(\
  FactBuilder \*fb,\                        InstanceBuilder \*ib,\
  const char \*name,\                       const char \*name,\
  Multifield \*mf);                         Multifield \*mf);

  PutSlotError FMPutSlotExternalAddress(\   PutSlotError IMPutSlotExternalAddress(\
  FactModifier \*fm,\                       FactModifier \*im,\
  const char \*name,\                       const char \*name,\
  CLIPSExternalAddress \*ea);               CLIPSExternalAddress \*ea);

  PutSlotError FMPutSlotMultifield(\        PutSlotError IMPutSlotMultifield(\
  FactModifier \*fm,\                       InstanceModifier \*im,\
  const char \*name,\                       const char \*name,\
  Multifield \*mf);                         Multifield \*mf);
  -----------------------------------------------------------------------------------

These functions assign an external address or multifield value to a **FactBuilder** (for parameter **fb**), **FactModifier** (for parameter **fm**), **InstanceBuilder** (for parameter ib), or **InstanceModifier** (for parameter **im**). Parameter **name** is the slot of either the fact or instance to be assigned. Parameter **ea** is the **CLIPSExternalAddress** value assigned to the slot; or parameter **mf** is the **Multifield** value assigned to the slot. These functions return true if the slot was successfully set; otherwise, they return false.

## 7.6 Examples

### 7.6.1 FactBuilder

This example illustrates use of the **FactBuilder** API.

#include \"clips.h\"

int main()

{

Environment \*theEnv;

FactBuilder \*theFB;

CLIPSValue cv;

theEnv = CreateEnvironment();

Build(theEnv,\"(deftemplate person\"

\" (slot name)\"

\" (slot gender)\"

\" (slot age)\"

\" (slot marital-status (default single))\"

\" (multislot hobbies))\");

theFB = CreateFactBuilder(theEnv,\"person\");

// Technique #1

FBPutSlotString(theFB,\"name\",\"Mary Sue Smith\");

FBPutSlotSymbol(theFB,\"gender\",\"female\");

FBPutSlotInteger(theFB,\"age\",25);

FBAssert(theFB);

// Technique #2

FBPutSlotCLIPSLexeme(theFB,\"name\",CreateString(theEnv,\"Sam Jones\"));

FBPutSlotCLIPSLexeme(theFB,\"gender\",CreateSymbol(theEnv,\"male\"));

FBPutSlotCLIPSInteger(theFB,\"age\",CreateInteger(theEnv,48));

FBPutSlotCLIPSLexeme(theFB,\"marital-status\",CreateSymbol(theEnv,\"married\"));

FBPutSlotMultifield(theFB,\"hobbies\",StringToMultifield(theEnv,\"reading skiing\"));

FBAssert(theFB);

// Technique #3

cv.lexemeValue = CreateString(theEnv,\"John Doe\");

FBPutSlot(theFB,\"name\",&cv);

cv.lexemeValue = CreateSymbol(theEnv,\"male\");

FBPutSlot(theFB,\"gender\",&cv);

cv.integerValue = CreateInteger(theEnv,73);

FBPutSlot(theFB,\"age\",&cv);

cv.lexemeValue = CreateSymbol(theEnv,\"widowed\");

FBPutSlot(theFB,\"marital-status\",&cv);

cv.multifieldValue = StringToMultifield(theEnv,\"gardening\");

FBPutSlot(theFB,\"hobbies\",&cv);

FBAssert(theFB);

FBDispose(theFB);

Eval(theEnv,\"(do-for-all-facts ((?f person)) TRUE (ppfact ?f))\",NULL);

DestroyEnvironment(theEnv);

}

The resulting output is:

(person

(name \"Mary Sue Smith\")

(gender female)

(age 25)

(marital-status single)

(hobbies))

(person

(name \"Sam Jones\")

(gender male)

(age 48)

(marital-status married)

(hobbies reading skiing))

(person

(name \"John Doe\")

(gender male)

(age 73)

(marital-status widowed)

(hobbies gardening))

### 7.6.2 FactModifier

This example illustrates use of the **FactModifier** API.

#include \"clips.h\"

int main()

{

Environment \*theEnv;

FactModifier \*theFM;

Fact \*theFact;

theEnv = CreateEnvironment();

Build(theEnv,\"(deftemplate print\"

\" (slot value))\");

Build(theEnv,\"(defrule print\"

\" (print (value ?v))\"

\" =\>\"

\" (println ?v))\");

theFact = AssertString(theEnv,\"(print (value \\\"Beginning\\\"))\");

Run(theEnv,-1);

theFM = CreateFactModifier(theEnv,theFact);

FMPutSlotString(theFM,\"value\",\"Middle\");

FMModify(theFM);

Run(theEnv,-1);

FMPutSlotString(theFM,\"value\",\"End\");

FMModify(theFM);

Run(theEnv,-1);

FMDispose(theFM);

DestroyEnvironment(theEnv);

}

The resulting output is:

Beginning

Middle

End

### 7.6.3 Fact Modifier with Referenced Facts

This example illustrates use of the **FactBuilder** and **FactModifier** APIs to iteratively change a group of facts.

#include \"clips.h\"

int main()

{

Environment \*theEnv;

FactBuilder \*theFB;

FactModifier \*theFM;

CLIPSValue cv;

Fact \*sensors\[2\];

long long sensorValues\[2\] = { 6, 5 };

theEnv = CreateEnvironment();

// Create a deftemplate and defrule

Build(theEnv,\"(deftemplate sensor\"

\" (slot id)\"

\" (multislot range)\"

\" (slot value))\");

Build(theEnv,\"(defrule sensor-value-out-of-range\"

\" (sensor (id ?id) (value ?value) (range ?lower ?upper))\"

\" (test (or (\< ?value ?lower) (\> ?value ?upper)))\"

\" =\>\"

\" (println ?id \\\" value \\\" ?value \"

\" \\\" out of range \\\" ?lower \\\" - \\\" ?upper))\");

// Watch changes to facts

Watch(theEnv,FACTS);

// Create the facts

theFB = CreateFactBuilder(theEnv,\"sensor\");

FBPutSlotSymbol(theFB,\"id\",\"sensor-1\");

FBPutSlotMultifield(theFB,\"range\",StringToMultifield(theEnv,\"4 8\"));

FBPutSlotInteger(theFB,\"value\",sensorValues\[0\]);

sensors\[0\] = FBAssert(theFB);

RetainFact(sensors\[0\]);

FBPutSlotSymbol(theFB,\"id\",\"sensor-2\");

FBPutSlotMultifield(theFB,\"range\",StringToMultifield(theEnv,\"2 7\"));

FBPutSlotInteger(theFB,\"value\",sensorValues\[1\]);

sensors\[1\] = FBAssert(theFB);

RetainFact(sensors\[1\]);

FBDispose(theFB);

// Seed the random number generator

Eval(theEnv,\"(seed (integer (time)))\",NULL);

// Create the FactModifier

theFM = CreateFactModifier(theEnv,NULL);

// Loop through 4 cycles of changes

for (int cycle = 1; cycle \< 5; cycle++)

{

Write(theEnv,\"Cycle #\");

WriteInteger(theEnv,STDOUT,cycle);

Write(theEnv,\"\\n\");

// Loop through each sensor

for (int s = 0; s \< 2; s++)

{

Fact \*oldValue = sensors\[s\];

FMSetFact(theFM,oldValue);

// Change the sensor value

Eval(theEnv,\"(random -3 3)\",&cv);

sensorValues\[s\] += cv.integerValue-\>contents;

FMPutSlotInteger(theFM,\"value\",sensorValues\[s\]);

sensors\[s\] = FMModify(theFM);

// Retain the new fact and release the old fact

RetainFact(sensors\[s\]);

ReleaseFact(oldValue);

}

// Execute Rules

Run(theEnv,-1);

}

// Dispose of the FactModifier

FMDispose(theFM);

DestroyEnvironment(theEnv);

}

The resulting output is:

==\> f-1 (sensor (id sensor-1) (range 4 8) (value 6))

==\> f-2 (sensor (id sensor-2) (range 2 7) (value 5))

Cycle #1

\<== f-1 (sensor \... (value 6))

==\> f-1 (sensor \... (value 9))

\<== f-2 (sensor \... (value 5))

==\> f-2 (sensor \... (value 3))

sensor-1 value 9 out of range 4 - 8

Cycle #2

\<== f-1 (sensor \... (value 9))

==\> f-1 (sensor \... (value 10))

sensor-1 value 10 out of range 4 - 8

Cycle #3

\<== f-1 (sensor \... (value 10))

==\> f-1 (sensor \... (value 13))

\<== f-2 (sensor \... (value 3))

==\> f-2 (sensor \... (value 2))

sensor-1 value 13 out of range 4 - 8

Cycle #4

\<== f-1 (sensor \... (value 13))

==\> f-1 (sensor \... (value 16))

\<== f-2 (sensor \... (value 2))

==\> f-2 (sensor \... (value 1))

sensor-2 value 1 out of range 2 - 7

sensor-1 value 16 out of range 4 - 8

Note that the specific values will vary because of calls to the random function.
