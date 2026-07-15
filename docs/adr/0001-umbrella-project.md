# ADR-0001

Title:
Use Elixir Umbrella Project

Status:
Accepted

Reason:

OPECore consists of multiple independent concerns:

- Domain
- Persistence
- Services
- gRPC

Umbrella architecture provides clear boundaries and
supports long-term maintainability.