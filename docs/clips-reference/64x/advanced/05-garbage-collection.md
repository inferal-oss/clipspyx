# Section 5: Garbage Collection

## 5.1 Introduction

CLIPS primitive values (including those which have counterparts to C primitive values such as integer, floats, and strings) are represented using data structures. As a CLIPS program executes, it allocates memory for primitive values dynamically (such as when facts/instances are created or functions are evaluated). CLIPS automatically tracks references to these primitive values so that they can be deallocated once there are no longer any outstanding references to them. Data which has been marked for later deallocation is referred to as **garbage**. The process of deallocating this garbage is referred to as **garbage collection**[]{.indexref entry="garbage collection" bold=""}.

If you use one of the interactive CLIPS executables, all garbage collection is handled automatically for you including garbage created when entering commands and by constructs which execute code (such as defrules and deffunctions).

Embedded applications, however, can generate garbage and trigger garbage collection when invoking certain API calls to CLIPS, so it is necessary to follow some guidelines when using the APIs to allow CLIPS to safely garbage collect data that is no longer needed and to prevent primitive values that are referenced by user code from being garbage collected. First, functions which can cause CLIPS code to be executed (such as Clear, Load, Reset, Run, Send, and Eval) can trigger garbage collection. Second, a primitive value returned through an API call (such as Eval) is not subject to garbage collection until a subsequent API call triggering garbage collection is invoked. Third, use the Retain API functions to create an outstanding reference to a primitive value and the Release API functions to remove an outstanding reference.

The following code illustrates the first two guidelines:

#include \"clips.h\"

int main()

{

Environment \*env;

CLIPSValue cv;

CLIPSLexeme \*sym1, \*sym2;

env = CreateEnvironment();

Eval(env,\"(sym-cat abc def)\",&cv);

sym1 = cv.lexemeValue;

// Safe to refer to sym1 here. \*/

Eval(env,\"(sym-cat ghi jkl)\",&cv);

sym2 = cv.lexemeValue;

// Not safe to refer to sym1 here.

// Safe to refer to sym2 here.

}

The first call to **Eval** triggers garbage collection, but since no data has been returned yet to the embedding program this does not cause any problems. The **lexemeValue** field of the **CLIPSLexeme** returned in the variable **cv** is assigned to the variable **sym1**. The **contents** field of this variable can be safely referenced because the returned value was excluded from garbage collection.

The second call to **Eval** also triggers garbage collection. In this case, however, the value returned by the prior call to **Eval** will be garbage collected as a result. Therefore it is not safe to reference the value stored in the variable **sym1** after this point. This is a problem if, for example, you want to compare the **contents** fields of variables **sym1** and **sym2**.

For float and integer primitive values, the **contents** field of the **CLIPSInteger** or **CLIPSFloat** structure can be directly copied to a variable if the value needs to be preserved, however for primitive types this problem can be corrected by using the Retain/Release APIs to inform CLIPS about values that should not be garbage collected. For example:

#include \"clips.h\"

int main()

{

Environment \*env;

CLIPSValue cv;

CLIPSLexeme \*sym1, \*sym2;

env = CreateEnvironment();

Eval(env,\"(sym-cat abc def)\",&cv);

sym1 = cv.lexemeValue;

RetainLexeme(env,sym1);

// Safe to refer to sym1 here. \*/

Eval(env,\"(sym-cat ghi jkl)\",&cv);

sym2 = cv.lexemeValue;

// Safe to refer to sym1 here.

// Safe to refer to sym2 here.

ReleaseLexeme(env,sym1);

// Not safe to refer to sym1 here.

// Safe to refer to sym2 here.

}

In this case, the **RetainLexeme** function is called to prevent the result of the first **Eval** call from being garbaged collected when the second **Eval** call is made. That result is protected until the call to **ReleaseLexeme** is made.

## 5.2 Retain and Release Functions

CLIPS provides numerous function for retaining and releasing primitive values. A primitive value can be retained multiple times and will not be garbage collected until a corresponding number of release function calls have been made.

  -----------------------------------------------------------------------
  void Retain(\                       void Release(\
  Environment \*env,\                 Environment \*env,\
  TypeHeader \*value);                TypeHeader \*value);
  ----------------------------------- -----------------------------------
  void RetainCV(\                     void ReleaseCV(\
  Environment \*env,\                 Environment \*env,\
  CLIPSValue \*value);                CLIPSValue \*value);

  void RetainUDFV(\                   void ReleaseUDFV(\
  Environment \*env,\                 Environment \*env,\
  UDFValue \*value);                  UDFValue \*value);

  void RetainFact(\                   void ReleaseFact(\
  Fact \*value);                      Fact \*value);

  void RetainInstance(\               void ReleaseInstance(\
  Instance \*value);                  Instance \*value);

  void RetainMultifield(\             void ReleaseMultifield(\
  Environment \*env,\                 Environment \*env,\
  Multifield \*value);                Multifield \*value);

  void RetainLexeme(\                 void ReleaseLexeme(\
  Environment \*env,\                 Environment \*env,\
  CLIPSLexeme \*value);               CLIPSLexeme \*value);

  void RetainFloat(\                  void ReleaseFloat(\
  Environment \*env,\                 Environment \*env,\
  CLIPSFloat \*value);                CLIPSFLoat \*value);

  void RetainInteger(\                void ReleaseInteger(\
  Environment \*env,\                 Environment \*env,\
  CLIPSInteger \*value);              CLIPSInteger \*value);
  -----------------------------------------------------------------------

## 5.3 Example

This example demonstrates how to retain a fact so that a subsequent call to retract the fact will produce the correct result is the fact is retracted by a rule.

#include \"clips.h\"

int main()

{

Environment \*env;

Fact \*f1, \*f2;

env = CreateEnvironment();

Build(env,\"(deftemplate list\"

\" (multislot numbers))\");

Build(env,\"(defrule sort\"

\" ?f \<- (list (numbers \$?b ?x ?y&:(\> ?x ?y) \$?e))\"

\" =\>\"

\" (retract ?f) \"

\" (assert (list (numbers ?b ?y ?x ?e))))\");

// Create and retain two facts.

// The first requires sorting.

// The second does not require sorting.

f1 = AssertString(env,\"(list (numbers 61 31 27 48))\");

RetainFact(f1);

f2 = AssertString(env,\"(list (numbers 13 19 88 99))\");

RetainFact(f2);

// Display facts before and after

// the sort rule is executed.

Eval(env,\"(facts)\",NULL);

Run(env,-1);

Eval(env,\"(facts)\",NULL);

// Release and retract both facts.

ReleaseFact(f1);

Retract(f1);

ReleaseFact(f2);

Retract(f2);

// Display remaining facts.

// Fact f-1 had already been retracted by the sort rule.

// Fact f-2 was retracted by the \"Retract(f2);\" call.

Eval(env,\"(facts)\",NULL);

DestroyEnvironment(env);

}

The resulting output is:

f-1 (list (numbers 61 31 27 48))

f-2 (list (numbers 13 19 88 99))

For a total of 2 facts.

f-2 (list (numbers 13 19 88 99))

f-6 (list (numbers 27 31 48 61))

For a total of 2 facts.

f-6 (list (numbers 27 31 48 61))

For a total of 1 fact.

If the fact stored in the variable **f1** had not been retained, the memory allocated for that fact could have been reallocated to store another fact (such as f-6). In that case, the \"Retract(f1);\" function call would have retracted the wrong fact rather than recognizing that the fact f-1 had already been retracted.
