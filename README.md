SensorHub
=========

<p align="center">
  <img src="images/raspberry-pi-4b.jpeg" alt="My Raspberry Pi" width="600"><br>
  <em>Figure 1: My Raspberry Pi 4B setup running headless.</em>
</p>

## 🏗️ System Architecture

This project is built around an event-driven, hybrid-cloud IoT architecture designed for high availability, local resilience, and secure remote monitoring. The system splits responsibilities across localized edge collection, a centralized home message broker, a dedicated gateway processor, and a mirrored cloud visualization layer.

```mermaid
graph TD
    %% Styles and Definitions
    classDef hardware fill:#2d3748,stroke:#4a5568,stroke-width:2px,color:#fff;
    classDef container fill:#1a202c,stroke:#3182ce,stroke-width:2px,color:#fff;
    classDef cloud fill:#2c5282,stroke:#4299e1,stroke-width:2px,color:#fff;

    %% Remote Nodes & Edge Devices
    subgraph Edge ["Sensors & Edge Collection"]
        WS[Weather Station]
        BT[Bluetooth Thermometers]
        RPiEdge[Remote Raspberry Pi Devices]
    end

    %% Synology NAS Host
    subgraph NAS ["Synology NAS (Docker Host)"]
        MQ[Mosquitto MQTT Broker]
    end

    %% Raspberry Pi 4B Host (IoTStack)
    subgraph Pi4 ["Raspberry Pi 4B (IoTStack Docker Host)"]
        NR[Node-RED Flow]
        IDB_Loc[(InfluxDB Local)]
        GF_Loc[Grafana Local]
    end

    %% Cloud Infrastructure
    subgraph Cloud ["Cloud Infrastructure"]
        IDB_Cld[(InfluxDB Cloud)]
        GF_Cld[Grafana Cloud]
    end

    %% Apply Styles
    class RPiEdge,NAS,Pi4 hardware;
    class MQ,NR,IDB_Loc,GF_Loc container;
    class IDB_Cld,GF_Cld cloud;

    %% Data Flow Connections
    WS -->|Sensor Readings| RPiEdge
    BT -->|BLE Readings| RPiEdge
    RPiEdge -->|Publish MQTT Messages| MQ
    MQ -->|Subscribe / Stream Messages| NR
    
    NR -->|Sanitise & Write| IDB_Loc
    NR -->|Sanitise & Upload| IDB_Cld
    
    IDB_Loc -->|Read Data| GF_Loc
    IDB_Cld -->|Read Data| GF_Cld
```

### Architectural Breakdown

#### 1. Data Acquisition & Edge Collection
* **Sensors**: Data originates from an outdoor weather station and multiple room/outbuilding Bluetooth Low Energy (BLE) thermometers.
* **Edge Collectors**: Distributed, secondary Raspberry Pi devices continuously sample these sensors, format the telemetry data, and transmit it upstream.

#### 2. Message Brokerage (Ingestion Layer)
* **Host**: Synology NAS running Docker.
* **Component**: **Eclipse Mosquitto MQTT Broker**.
* **Function**: Acts as a decoupled, central ingestion point. The edge devices publish sensor readings asynchronously to specific MQTT topics, ensuring that network fluctuations at the gateway do not result in data loss at the sensor level.

#### 3. Processing & Storage Gateway (IoTStack)
* **Host**: Raspberry Pi 4B managed via an **IoTStack** Docker container ecosystem.
* **ETL Pipeline (Node-RED)**: Node-RED subscribes to the Mosquitto broker topics on the NAS. It ingests the raw MQTT strings, sanitises and validates the payloads (handling missing values or malformed data), and executes a dual-write strategy.
* **Local Storage (InfluxDB)**: A time-series database running in a local container receives the sanitised data for low-latency, long-term historical storage within the local network.

#### 4. Visualization & Remote Access Layer
* **Local Dashboards (Grafana)**: A local Grafana container queries the local InfluxDB instance, providing real-time, high-resolution dashboards accessible anywhere inside the home network.
* **Cloud Mirroring (InfluxDB Cloud & Grafana Cloud)**: To bypass complex home-network port forwarding or VPN setups, Node-RED simultaneously pushes data to InfluxDB Cloud. A mirrored Grafana Cloud dashboard reads from this cloud instance, granting secure, encrypted remote access from anywhere in the world.

### System Resilience Features
* **Decoupling**: If the Raspberry Pi 4B goes offline for maintenance, the Mosquitto broker on the Synology NAS caches incoming MQTT data (if configured with persistence), preventing data loss.
* **Hybrid Cloud**: If the home internet connection drops, the local InfluxDB and Grafana instances continue to function perfectly. Data resumes syncing to the cloud once the connection is restored.
* **Containerization**: All software components run in isolated Docker containers, allowing for easy updates, independent scaling, and trivial backups via IoTStack.

