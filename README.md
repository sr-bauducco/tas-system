# Tele Assistance System (TAS) - GoalD Framework

## Overview
This project is a reactive microservices implementation of the TAS exemplar, following the GoalD architectural pattern.

## System Architecture
The system is divided into three functional agents orchestrated through a MAPE-K loop:
1. **Monitor (ms-monitor)**: Fulfills **G1 (GetVitalParams)**. Generates a reactive stream of patient vitals.
2. **Analysis (ms-analysis)**: Fulfills **G6 (AnalyzeData)**. Evaluates vitals and orchestrates the response.
3. **Execution (ms-emergency)**: Fulfills **G10 (NotifyEmergencyCall)**. Dispatches medical alerts.

## Tech Stack
- Java 17
- Spring Boot 3.2.2
- Project Reactor (Reactive Streams)
- Maven Multi-module

## How to Run
1. **Build the entire system:**
   ```bash
   mvn clean install
   ```
2. **Start the services (in separate terminals):**
    ```bash
    Emergency (Port 8080): cd ms-emergency && mvn spring-boot:run

    Monitor (Port 8081): cd ms-monitor && mvn spring-boot:run

    Analysis (Port 8082): cd ms-analysis && mvn spring-boot:run
    ```
3. **Goal Traceability**

    G1: tas.goals.G1GetVitalParams

    G6: tas.analysis.AnalysisAgent (Autonomic Loop)

    G10: tas.goals.G10NotifyEmergency
