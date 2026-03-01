# Section 5: CLIPS DLL Interface

This section describes various techniques for integrating CLIPS and creating executables using Microsoft Windows. The examples in this section have been tested running Windows 10 Operating System with Visual Studio Community 2019.

## 5.1 Installing the Source Code

In order to run the integration examples, you must install the source code by downloading the *clips_windows_projects_641.zip* file (see appendix A for information on obtaining CLIPS). Once downloaded, you must then extract the contents of the file by right clicking on it and selecting the **Extract All...** menu item. Drag the *clips_windows_projects_641* directory into the directory you'll be using for development. In addition to the source code specific to the Windows projects, the core CLIPS source code is also included, so there is no need to download this code separately.

## 5.2 Building the CLIPS Libraries

The Visual Studio CLIPS solution file includes four projects for building libraries. They are:

- WrappedLib

- DLL

- WrappedDLL

- CLIPSJNI

WrappedLib is a starter project that demonstrates how to build a CLIPS C++ library that is statically linked with an executable. CLIPSJNI is a starter project that demonstrates how to build a CLIPS library for use with the Java Native Interface. DLL is a starter project that demonstrates how to build a CLIPS Dynamic Link Library (DLL) that is dynamically linked with an executable. WrappedDLL is a C++ "wrapper" library that simplifies the use of the CLIPS DLL.

Unless you want to make changes to the libraries, there is no need to build them. Windows executables are available through a separate installer and the precompiled libraries are available in the Libraries directory of the corresponding project directory.

### 5.2.1 Building the Projects Using Microsoft Visual Studio Community 2022

Navigate to the *Projects\\MVS_2022* directory. Open the file CLIPS.sln by double clicking on it or right click on it and select the *Open* menu item. After the file opens in Visual Studio, select *Configuration Manager...* from the *Build* menu. Select the Configuration (Debug or Release) for the library project and then click the *Close* button. Right click on the library project name in the *Solution Explorer* pane and select the *Build* menu item. When compilation is complete, the example executable will be in the corresponding \<Platform\>\\\<Configuration\> directory of the *Library* directory of the corresponding DLL, WrappedLib, or WrappedDLL directory.

The CLIPSJNI project assumes that Java SE Development Kit 11.0.17 is installed on your computer and that the Java header files are contained in the directories C:\\Program Files\\Java\\ jdk-11.0.17\\include and C:\\Program Files\\Java\\ jdk-11.0.17\\include\\win32. To change the directory setting for the location of the headers files, right click on the CLIPSJNI project and select the *Properties* menu item. In the tree view control, open the *Configuration Properties* and *C/C++* branches, then select the *General* leaf item. Edit the value in the *Additional Include Directories* editable text box to include the appropriate directory for the Java include files.

## 5.3 Running the Library Examples

The Visual Studio CLIPS solution file includes three projects that demonstrate the use of the static and dynamic libraries from Section 5.2. They are:

- DLLExample

- WrappedLibExample

- WrappedDLLExample

The DLLExample project demonstrates how to statically load the CLIPS DLL. The example code links with the DLL import library (CLIPS.dll). The WrappedLibExample project demonstrates how to statically load the CLIPS Wrapped C++ library (WrappedLib.lib). The C++ class *CLIPSCPPEnv* is used to provide a C++ wrapper to the CLIPS API. The WrappedDLLExample project demonstrates the use of a C++ wrapper to simplify the use of the DLL. The example code used in this project is identical to the code used with the WrappedLibExample project.

### 5.3.1 Building the Examples Using Microsoft Visual Studio Community 2022

Navigate to the *MVS_2022* directory. Open the file *CLIPS.sln* by double clicking on it (or right click on it and select the **Open** menu item). After the file opens in Visual Studio, select **Configuration Manager...** from the **Build** menu. Select the Configuration (**Debug** or Release) for the example project, the appropriate platform (either **x64** for a 64-bit system or **Win32** for a 32-bit system), and then click the **Close** button. Note that the configuration chosen should match the configuration of the libraries/DLL projects (DLL, WrappedLib, and WrappedDLL). Right click on the example project name in the Solution Explorer pane and select the **Build** menu item. When compilation is complete, the example executable will be in the corresponding \<Platform\>\\\<Configuration\> directory of the *Executables* directory of the corresponding DLLExample, WrappedLibExample, or WrappedDLLExample directory.
