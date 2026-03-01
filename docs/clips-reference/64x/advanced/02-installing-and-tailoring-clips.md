# Section 2: Installing and Tailoring CLIPS

This section describes how to install and tailor CLIPS to meet specific needs. Instructions are included for creating a console executable by compiling the portable core CLIPS source files. For instructions on compiling the Windows, macOS, and Java Integrated Development Environments for CLIPS, see the *Utilities and Interfaces Guide*.

## 2.1 Installing CLIPS

CLIPS executables for DOS, Windows, and macOS are available for download from the internet. See Appendix A for details. To tailor CLIPS or to install it on another operating system, the user must port the source code and create a new executable version.

Testing of CLIPS 6.4.2 included the following software environments:

• Windows 11 with Visual Studio Community 2022

• MacOS 15.2 using Xcode 16.2

• Linux: Ubuntu 22.04 LTS, Debian 11.3, Fedora 36, Mint 20.3, and CentOS 9

CLIPS is designed for portability and should run on any operating system which supports an ANSI C or C++ compiler. The following steps de­scribe how to create a new executable version of CLIPS:

1\) **Load the source code onto the user's system**

The following C source files are necessary to set up the basic CLIPS system:

  ----------------- ----------------- ----------------- ----------------
  agenda.h          dfinscmp.h        immthpsr.h        prcdrpsr.h

  analysis.h        drive.h           incrrset.h        prdctfun.h

  argacces.h        emathfun.h        inherpsr.h        prntutil.h

  bload.h           engine.h          inscom.h          proflfun.h

  bmathfun.h        entities.h        insfile.h         reorder.h

  bsave.h           envrnbld.h        insfun.h          reteutil.h

  classcom.h        envrnmnt.h        insmngr.h         retract.h

  classexm.h        evaluatn.h        insmoddp.h        router.h

  classfun.h        expressn.h        insmult.h         rulebin.h

  classinf.h        exprnbin.h        inspsr.h          rulebld.h

  classini.h        exprnops.h        globlpsr.h        prcdrfun.h

  classpsr.h        exprnpsr.h        insquery.h        rulebsc.h

  clips.h           extnfunc.h        insqypsr.h        rulecmp.h

  clsltpsr.h        factbin.h         iofun.h           rulecom.h

  commline.h        factbld.h         lgcldpnd.h        rulecstr.h

  conscomp.h        factcmp.h         match.h           ruledef.h

  constant.h        factcom.h         memalloc.h        ruledlt.h

  constrct.h        factfile.h        miscfun.h         rulelhs.h

  constrnt.h        factfun.h         modulbin.h        rulepsr.h

  crstrtgy.h        factgen.h         modulbsc.h        scanner.h

  cstrcbin.h        facthsh.h         modulcmp.h        setup.h

  cstrccmp.h        factlhs.h         moduldef.h        sortfun.h

  cstrccom.h        factmch.h         modulpsr.h        strngfun.h

  cstrcpsr.h        factmngr.h        modulutl.h        strngrtr.h

  cstrnbin.h        factprt.h         msgcom.h          symblbin.h

  cstrnchk.h        factqpsr.h        msgfun.h          symblcmp.h

  cstrncmp.h        factqury.h        msgpass.h         symbol.h

  cstrnops.h        factrete.h        msgpsr.h          sysdep.h

  cstrnpsr.h        factrhs.h         multifld.h        textpro.h

  cstrnutl.h        filecom.h         multifun.h        tmpltbin.h

  default.h         filertr.h         network.h         tmpltbsc.h

  defins.h          fileutil.h        objbin.h          tmpltcmp.h

  developr.h        generate.h        objcmp.h          tmpltdef.h

  dffctbin.h        genrcbin.h        object.h          tmpltfun.h

  dffctbsc.h        genrccmp.h        objrtbin.h        tmpltlhs.h

  dffctcmp.h        genrccom.h        objrtbld.h        tmpltpsr.h

  dffctdef.h        genrcexe.h        objrtcmp.h        tmpltrhs.h

  dffctpsr.h        genrcfun.h        objrtfnx.h        tmpltutl.h

  dffnxbin.h        genrcpsr.h        objrtgen.h        userdata.h

  dffnxcmp.h        globlbin.h        objrtmch.h        usrsetup.h

  dffnxexe.h        globlbsc.h        parsefun.h        utility.h

  dffnxfun.h        globlcmp.h        pattern.h         watch.h

  dffnxpsr.h        globlcom.h        pprint.h          

  dfinsbin.h        globldef.h        prccode.h         
  ----------------- ----------------- ----------------- ----------------

  ----------------- ----------------- ----------------- -----------------
  agenda.c          drive.c           globlpsr.c        prcdrfun.c

  analysis.c        emathfun.c        immthpsr.c        prcdrpsr.c

  argacces.c        engine.c          incrrset.c        prdctfun.c

  bload.c           envrnbld.c        inherpsr.c        prntutil.c

  bmathfun.c        envrnmnt.c        inscom.c          proflfun.c

  bsave.c           evaluatn.c        insfile.c         reorder.c

  classcom.c        expressn.c        insfun.c          reteutil.c

  classexm.c        exprnbin.c        insmngr.c         retract.c

  classfun.c        exprnops.c        insmoddp.c        router.c

  classinf.c        exprnpsr.c        insmult.c         rulebin.c

  classini.c        extnfunc.c        inspsr.c          rulebld.c

  classpsr.c        factbin.c         insquery.c        rulebsc.c

  clsltpsr.c        factbld.c         insqypsr.c        rulecmp.c

  commline.c        factcmp.c         iofun.c           rulecom.c

  conscomp.c        factcom.c         lgcldpnd.c        rulecstr.c

  constrct.c        factfile.c        main.c            ruledef.c

  constrnt.c        factfun.c         memalloc.c        ruledlt.c

  crstrtgy.c        factgen.c         miscfun.c         rulelhs.c

  cstrcbin.c        facthsh.c         modulbin.c        rulepsr.c

  cstrccom.c        factlhs.c         modulbsc.c        scanner.c

  cstrcpsr.c        factmch.c         modulcmp.c        sortfun.c

  cstrnbin.c        factmngr.c        moduldef.c        strngfun.c

  cstrnchk.c        factprt.c         modulpsr.c        strngrtr.c

  cstrncmp.c        factqpsr.c        modulutl.c        symblbin.c

  cstrnops.c        factqury.c        msgcom.c          symblcmp.c

  cstrnpsr.c        factrete.c        msgfun.c          symbol.c

  cstrnutl.c        factrhs.c         msgpass.c         sysdep.c

  default.c         filecom.c         msgpsr.c          textpro.c

  defins.c          filertr.c         multifld.c        tmpltbin.c

  developr.c        fileutil.c        multifun.c        tmpltbsc.c

  dffctbin.c        generate.c        objbin.c          tmpltcmp.c

  dffctbsc.c        genrcbin.c        objcmp.c          tmpltdef.c

  dffctcmp.c        genrccmp.c        objrtbin.c        tmpltfun.c

  dffctdef.c        genrccom.c        objrtbld.c        tmpltlhs.c

  dffctpsr.c        genrcexe.c        objrtcmp.c        tmpltpsr.c

  dffnxbin.c        genrcfun.c        objrtfnx.c        tmpltrhs.c

  dffnxcmp.c        genrcpsr.c        objrtgen.c        tmpltutl.c

  dffnxexe.c        globlbin.c        objrtmch.c        userdata.c

  dffnxfun.c        globlbsc.c        parsefun.c        userfunctions.c

  dffnxpsr.c        globlcmp.c        pattern.c         utility.c

  dfinsbin.c        globlcom.c        pprint.c          watch.c

  dfinscmp.c        globldef.c        prccode.c         
  ----------------- ----------------- ----------------- -----------------

In addition to these core files, the Integrated Development Environments require additional files for compilation. See the *Utilities and Interfaces Guide* for details on compiling the IDEs.

2\) **Tailor CLIPS environment and/or features**

Edit the setup.h file and set any special options. CLIPS uses preprocessor definitions to allow machine‑dependent features. The first set of definitions in the setup.h file tells CLIPS on what kind of machine the code is being compiled. The default setting for this definition is GENERIC, which will create a ver­sion of CLIPS that will run on any computer. The user may set the definition for the user's type of system. If the system type is unknown, the definition should be set to GENERIC (so for this situation you do not need to edit setup.h). Other preprocessor definitions in the setup.h file also allow a user to tailor the features in CLIPS to specific needs. For more information on using the flags, see section 2.2.

Optionally, preprocessor definitions can be set using the appropriate command line argument used by your compiler, removing the need to directly edit the setup.h file. For example, the command line option --DLINUX will work on many compilers to set the preprocessor definition of LINUX to 1.

3\) **Compile all of the ".c" files to object code**

Use the standard compiler syntax for the user\'s machine. The \".h\" files are include files used by the other files and do not need to be com­piled. Some options may have to be set, depending on the compiler.

If user‑de­fined functions are needed, compile the source code for those functions as well and modify the UserFunctions definition in userfunctions.c[]{.indexref entry="files:source:userfunctions.c"} to reflect the user\'s functions (see section 3 for more on user‑defined functions).

4\) **Create the interactive CLIPS executable element**

To create the interactive CLIPS executable, link together all of the object files. This executable will provide the interactive interface defined in section 2.1 of the *Basic Programming Guide*.

### 2.1.1 Makefiles

The makefiles 'makefile.win' and 'makefile' are provided with the core source code to create executables and static libraries for Windows, MacOS, and Linux. The makefiles can be used to create either release or debug versions of the executables/libraries and to compile the code as C or C++.

**Using the Windows Makefile**

The following steps assume you have Microsoft Visual Studio Community 2022 installed. First, launch the Command Prompt application from the Start menu by selecting *Visual Studio 2022* and then either *x64 Native Tools Command Prompt for VS 2022* or *x86 Native Tools Command Prompt for VS 2022*. Next, use the cd command to change the current directory to the one containing the core CLIPS source code and makefiles. To compile CLIPS as C code without debugging information, use the command

nmake --f makefile.win

or

nmake --f makefile.win BUILD=RELEASE

To compile CLIPS as C++ code without debugging information, use the following command:

nmake --f makefile.win BUILD=RELEASE_CPP

To compile CLIPS as C code with debugging information, use the following command:

nmake --f makefile.win BUILD=DEBUG

To compile CLIPS as C++ code with debugging information, use the following command:

nmake --f makefile.win BUILD=DEBUG_CPP

When compilation is complete, the executable file clips.exe and the static library file clips.lib will be created in the source directory.

Before rebuilding the executable and library with a different BUILD variable value, the clean action should be run:

nmake --f makefile.win clean

**Using the macOS and Linux Makefile**

First, launch the Terminal application. Use the cd command to change the current directory to the one containing the core CLIPS source code and makefiles. To compile CLIPS as C code without debugging information, use the command

make

or

make release

To compile CLIPS as C++ code without debugging information, use the following command:

make release_cpp

To compile CLIPS as C code with debugging information, use the following command:

make debug

To compile CLIPS as C++ code with debugging information, use the following command:

make debug_cpp

When compilation is complete, the executable file clips and the static library file libclips.a will be created in the source directory.

Before rebuilding the executable and library with a different configuration, the clean action should be run:

make clean

## 2.2 Tailoring CLIPS

CLIPS makes use of **preprocessor definitions**[]{.indexref entry="preprocessor definitions"} (also referred to in this document as **compiler directives** or **setup flags**) to allow easier porting and recompiling of CLIPS. Compiler directives allow the incorporation of system‑dependent features into CLIPS and also make it easier to tailor CLIPS to specific applications. All avail­able compiler options are controlled by a set of flags defined in the **setup.h** file.

The first flag in **setup.h** indicates on what type of compiler/machine CLIPS is to run. The source code is sent out with the flag for GENERIC CLIPS turned on. When com­piled in this mode, all system‑dependent features of CLIPS are excluded and the program should run on any system. A number of other flags are available in this file, indi­cating the types of compilers/machines on which CLIPS has been compiled previ­ously. If the user\'s implementation matches one of the available flags, set that flag to 1 and turn the **GENERIC** flag off (set it to 0). The code for most of the features controlled by the compil­er/machine‑type flag is in the **sysdep.c** file.

Many other flags are provided in **setup.h**. Each flag is described below.

**BLOAD** This flag controls access to the binary load command (bload). This would be used to save some memory in systems which require binary load but not save capability. This is off in the standard CLIPS executable.

BLOAD_AND_BSAVE

This flag controls access to the binary load and save commands. This would be used to save some memory in systems which require neither binary load nor binary save capability. This is on in the standard CLIPS executable.

BLOAD_INSTANCES

; This flag controls the ability to load instances in binary format from a file via the **bload‑instances** command (see section 13.11.4.7 of the *Basic Programming Guide*). This is on in the standard CLIPS executable. Turning this flag off can save some memory.

**BLOAD_ONLY** This flag controls access to the binary and ASCII load commands (bload and load). This would be used to save some memory in systems which require binary load capability only. This flag is off in the standard CLIPS executable.

BSAVE_INSTANCES

; This flag controls the ability to save instances in binary format to a file via the **bsave‑instances** command (see section 13.11.4.4 of the *Basic Programming Guide*). This is on in the standard CLIPS executable. Turning this flag off can save some memory.

CONSTRUCT_COMPILER

This flag controls the construct compiler functions. If it is turned on, constructs may be compiled to C code for use in a run‑time module (see section 11). This is on in the standard CLIPS executable. Turning this flag off can save some memory.

DEBUGGING_FUNCTIONS

This flag controls access to commands such as agenda, facts, ppdefrule, ppdeffacts, etc. This would be used to save some memory in BLOAD_ONLY or RUN_TIME systems. This flag is on in the standard CLIPS executable.

DEFFACTS_CONSTRUCT

This flag controls the use of deffacts. If it is off, deffacts are not allowed which can save some memory and performance during resets. This is on in the standard CLIPS executable.

DEFFUNCTION_CONSTRUCT

; This flag controls the use of deffunction. If it is off, deffunction is not allowed which can save some memory. This is on in the standard CLIPS executable.

DEFGENERIC_CONSTRUCT

; This flag controls the use of defgeneric and defmethod. If it is off, defgeneric and defmethod are not allowed which can save some memory. This is on in the standard CLIPS executable.

DEFGLOBAL_CONSTRUCT

; This flag controls the use of defglobal. If it is off, defglobal is not allowed which can save some memory. This is on in the standard CLIPS executable.

DEFINSTANCES_CONSTRUCT

This flag controls the use of definstances (see section 9.6.1.1 of the *Basic Programming Guide*). If it is off, definstances are not allowed which can save some memory and performance during resets. This is on in the standard CLIPS executable.

DEFMODULE_CONSTRUCT

; This flag controls the use of the defmodule construct. If it is off, then new defmodules cannot be defined (however the MAIN module will exist). This is on in the standard CLIPS executable.

DEFRULE_CONSTRUCT

This flag controls the use of the defrule construct. If it is off, the defrule construct is not recognized by CLIPS. This is on in the standard CLIPS executable.

DEFTEMPLATE_CONSTRUCT

; This flag controls the use of deftemplate. If it is off, deftemplate is not allowed which can save some memory. This is on in the standard CLIPS executable.

**EXTENDED_MATH_FUNCTIONS** **\**
This flag indicates whether the extend­ed math package should be included in the compilation. If this flag is turned off (set to 0), the final executable will be about 25‑30K smaller, a consideration for machines with limited memory. This is on in the standard CLIPS executable.

FACT_SET_QUERIES

; This flag determines if the fact‑set query functions are available. These functions are **any‑factp**, **do‑for‑fact**, **do‑for‑all‑facts**, **delayed‑do‑for‑all‑facts**,, **find‑fact**, and **find‑all‑facts**. This is on in the standard CLIPS executable. Turning this flag off can save some memory.

INSTANCE_SET_QUERIES

; This flag determines if the instance‑set query functions are available. These functions are **any‑instancep**, **do‑for‑instance**, **do‑for‑all‑instances**, **delayed‑do‑for‑all‑instances**,, **find‑instance**, and **find‑all‑instances**. This is on in the standard CLIPS executable. Turning this flag off can save some memory.

**IO_FUNCTIONS** This flag controls access to the I/O functions in CLIPS. These functions are **close**, **format**, **get-char**, **open**, **print**, **println**, **printout**, **put-char**, **read**, **readline**, **read-number**, **rename**, **remove**, and **set-locale**. If this If this flag is off, these functions are not available. This would be used to save some memory in systems which used custom I/O routines. This is on in the standard CLIPS executable.

MULTIFIELD_FUNCTIONS

This flag controls access to the multifield manipulation func­tions in CLIPS. These functions are **delete\$**, **delete-member\$**, **difference\$**, **explode\$**, **first\$**, **foreach**, **implode\$**, **insert\$**, **intersection\$**, **member\$**, **nth\$**, **progn\$**, **replace\$**, **replace-member\$**, **rest\$**, **subseq\$**, **subsetp**, and **union\$**. The functions **create\$**, **expand\$**, and **length\$** are always available regardless of the setting of this flag. This would be used to save some memory in systems which performed limited or no operations with multifield values. This flag is on in the standard CLIPS executable.

OBJECT_SYSTEM

; This flag controls the use of defclass, definstances, and defmessage-handler. If it is off, these constructs are not allowed which can save some memory. This is on in the standard CLIPS executable.

PROFILING_FUNCTIONS

This flag controls access to the profiling func­tions in CLIPS. These functions are **get-profile-percent-threshold**, **profile**, **profile-info**, **profile-reset**, and **set-profile-percent-threshold**. This flag is on in the standard CLIPS executable.

**RUN_TIME** This flag will create a run‑time version of CLIPS for use with compiled constructs. It should be turned on only *after* the constructs-to-c function has been used to generate the C code representation of the constructs, but *before* compiling the constructs C code. See section 11 for a de­scription of how to use this. This is off in the standard CLIPS executable.

STRING_FUNCTIONS

This flag controls access to the string manipulation functions in CLIPS. These functions are **build**, **eval**, **lowcase**, **string-to-field**, **str-cat**, **str‑compare**, **str‑index**, **str‑length**, **sub‑string**, **sym-cat**, and **upcase**. This would be used to save some memory in systems which perform limited or no operations with strings. This flag is on in the standard CLIPS executable.

SYSTEM_FUNCTION

This flag controls access to the **system** function in CLIPS. This would be used to remove this function on platforms which do not support the associated C library function. This flag is on in the standard CLIPS executable.

**TEXTPRO_FUNCTIONS\**
This flag controls the CLIPS text-processing functions. It must be turned on to use the **fetch**, **get-region**, **print-region**, and **toss** functions in a user‑defined help system. This is on in the standard CLIPS executable.

#
