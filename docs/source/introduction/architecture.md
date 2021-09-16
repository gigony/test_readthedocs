# Architecture

## Overview

The MONAI Deploy App SDK enables the designing of usable, reproducible, and production-ready AI inference applications in the healthcare domain. The SDK was designed with the following four core design goals:

- **Usability**: Provides a usable API for structuring the code as a workflow, i.e. as a directed graph of operators

- **Composability**: Provides a collection of operators as building blocks to address common tasks prevalent in the healthcare domain.

- **Portability**: Enables packaging the application, associated models, and relevant metadata in a self-contained package that is easy to port

- **Production Readiness**: Designed to execute an app in various environments, from development to production

## High-Level Architecture Diagram

Below is a high-level architecture diagram of the MONAI Deploy Application SDK.

![image](https://user-images.githubusercontent.com/1928522/133539726-fd148075-c37e-485f-b2d5-672741488181.png)

In the following sections, the components of the architecture are described in more detail. To highlight the time-dimension of the architecture, the descriptions have been grouped by Development-time & Run-time.

### Development Time Components

The core development-time concept in the MONAI Deploy App SDK is an inference application in the healthcare domain. An Application represents the business logic of what needs to be computed given some healthcare domain-specific data as input. How to provide a framework where developers can easily create a healthcare inference application using building blocks & custom code is the central design concern of the MONAI Deploy App SDK.

The user is encouraged to structure the application code in a way that enables reproducibility and debuggability. In contrast, the SDK itself is designed to minimize concerns related to production readiness during development time. Optimally, the user can write idiomatic Python code focusing on the logic itself and the guard rails of the framework enable the code to be production-ready.

**Application**: An application represents a collection of computational tasks that together accomplish a meaningful goal in the healthcare domain. Typically, an app defines a workflow that reads medical imaging data from disk, processes it in one or more operators (some of which could be AI inference related), and produces output data. User implements an app by subclassing [monai.deploy.core.Application](/modules/_autosummary/monai.deploy.core.Application) class. An app makes use of instances of Operators as stages in the application.

**Graph**: The SDK provides a mechanism to define a directed acyclic graph which can be composed of operators. This acyclic property is important, as it prevents the framework from running into circular dependencies between operators. The graph consists of one or more vertices and edges, with each edge directed from one vertex to another, such that there is no way to start at any vertex and follow a consistently directed sequence of edges that eventually loops back to the same vertex again. Each vertex in the graph represents an Operator. The edge between two operators contains connectivity information.

**Operator**: An operator is the smallest unit of computation. It is implemented by the user by inheriting a class from the [monai.deploy.core.Operator](/modules/_autosummary/monai.deploy.core.Operator). An operator is an element of a MONAI Deploy Application. Each operator is typically designed to perform a specific function/analysis on incoming input data. Common examples of such functions are: reading images from disk, performing image processing, performing AI inference, writing images to disk, etc. The SDK comes with a bundled set of operators.

### Run-Time Concepts

The core runtime concepts in the MONAI Deploy App SDK are the MONAI Application Package (MAP) and a MONAI Application Runner (MAR). A key design decision of the SDK is to make the framework runtime-agnostic. The same code should be runnable in various environments, such as on a workstation during development or on a production-ready workflow orchestrator during production.

**MONAI Application Packager**: Once an application is built using the MONAI App SDK, it can be packaged into a portable MONAI Application Package (MAP). A MAP contains an executable application & provides sufficient information to execute the application as intended. It consists of a single container and metadata that provides additional information about the application. A MAP is self-describing and provides a mechanism for extracting its description. It provides information about its expected inputs such that an external agent is able to determine if the MAP is capable of receiving a workload. The containerized portion of a MAP complies with Open Container Initiative (OCI) format standards. The MONAI Application Packager utility helps developers to package an app written using the SDK into a MAP.

**Executor**: An executor in the SDK is an entity that ingests an Application, parses the Directed Acyclic Graph inside it, and executes the operators in the specified order. The SDK has provisions to support multiple types of Executors depending on single/multi-process and execution order needs.

**MONAI Application Runner**: The MONAI Application Runner (MAR) is a command-line utility that allows users to run and test their MONAI Application Package (MAP) locally. MAR is developed to make the running and testing of MAPs locally an easy process for developers by abstracting away the need to understand the internal details of the MAP. MAR allows users to specify input and output paths on the local file system which it maps to the input and output of MAP during execution.
