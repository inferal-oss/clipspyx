# Appendix B: Update Release Notes

The following changes were introduced in version 6.4 of CLIPS.

• **Environment API** -- The environment API is the only supported API. The Env prefix has been removed from all API calls.

• **Void Pointers** -- The use of generic (or universal) pointers in API calls when an appropriate typed pointer exists has been discontinued.

• **Bool Support** -- The APIs now utilize the bool type for representing boolean values.

• **Primitive Value Redesign** -- The implementation of primitive values has been redesigned. The function **AddSymbol** has been replaced with the functions **CreateSymbol**, **CreateString**, **CreateInstanceName**, and **CreateBoolean**. The function **AddLong** has been replaced with the function **CreateInteger**. The function **AddDouble** has been replaced with the function **CreateFloat**. The function **CreateMultifield** has been replaced with the **MultifieldBuilder** API and the functions **EmptyMultifield** and **StringToMultifield**. See section 4.1 and section 6 for more information.

• **User Defined Function API Redesign** -- The User Defined Function API has been redesigned. The DefineFunction function has been renamed to **AddUDF** and its parameters have changed. The function **RtnArgCount** has been renamed to **UDFArgumentCount** and its parameters have changed. The functions **ArgCountCheck** and **ArgRangeCheck** are no longer supported since the UDF argument count is automatically checked before a UDF is invoked. The functions **UDFFirstArgument**, **UDFNextArgument**, **UDFNthArgument**, and **UDFHasNextArgument** should be used to replace the function **ArgTypeCheck** (which is no longer supported). See section 8 for more information.

• **I/O Router API Redesign** -- The I/O router API has been redesigned. The parameters for the **AddRouter** function have changed. The **GetcRouter**, **UngetcRouter**, and **PrintRouter** functions have been renamed to **ReadRouter**, **UnreadRouter**, and **WriteString**. The **WPROMPT**, **WDISPLAY**, **WTRACE**, and **WDIALOG** logical names are no longer supported. The **WWARNING** and **WERROR** logical names have been renamed to **STDWRN** and **STDERR**. See section 9 for more information.

• **Garbage Collection API Redesign** -- The Garbage Collection API has been redesigned. The **Retain** and **Release** functions should be used to prevent primitive values from being garbage collected. The functions **IncrementGCLocks**, **DecrementGCLocks**, **IncrementFactCount**, **DecrementFactCount**, **IncrementInstanceCount**, and **DecrementInstanceCount** are no longer supported. See section 5 for more information.

• **FactBuilder and FactModifier APIs** -- The FactBuilder and FactModifier APIs provides functions for creating a modifying facts. See section 7 for more information.

• **InstanceBuilder and InstanceModifier APIs** -- The InstanceBuilder and InstanceModifier APIs provides functions for creating a modifying instances. See section 7 for more information.

• **FunctionCallBuilder API** -- The FunctionCallBuilder API provides functions for dynamically calling CLIPS functions. See section 4.3 for more information.

• **StringBuilder API** -- The StringBuilder API provides functions for dynamically allocating and appending strings. See section 4.4 for more information.

• **Eval Function** -- The Eval function is now available for use in run-time programs. See sections 4.2 and 11 for more information.

• **Compiler Directives** -- The **ALLOW_ENVIRONMENT_GLOBALS** flag has been removed. The **VAX_VMS** and **WINDOW_INTERFACE**[]{.indexref entry="WINDOW_INTERFACE"} flags has been removed.

The following changes were introduced in version 6.4.1 of CLIPS.

• **FunctionCallBuilder API** ---- The **FCBPopArgument** function was added. See section 4.3 for more information.

• **Compiler Directives** -- The **SYSTEM_FUNCTION** flag has been added. See section 2.2 for more information.
