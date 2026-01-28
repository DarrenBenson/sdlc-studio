<!--
Module: C4 Architecture Diagrams
Extends: templates/core/trd.md
Section: 2.5 (after Architecture Overview)
Load: trd create --with-diagrams or trd create --full
-->

## Architecture Diagrams

> Generated with `/sdlc-studio trd visualise`. Edit TRD content and regenerate to update.

### System Context (C4 Level 1)

Shows the system in context with users and external systems.

```mermaid
graph TB
    subgraph boundary [System Boundary]
        SYS[{{system_name}}]
    end

    %% Users
    {{#each users}}
    {{user_id}}(({{user_name}}))
    {{user_id}} -->|{{user_interaction}}| SYS
    {{/each}}

    %% External Systems
    {{#each external_systems}}
    {{ext_id}}[{{ext_name}}]
    SYS -->|{{ext_protocol}}| {{ext_id}}
    {{/each}}
```

### Container Diagram (C4 Level 2)

Shows the high-level technology choices and communication.

```mermaid
graph TB
    %% Containers (applications)
    {{#each containers}}
    {{container_id}}[{{container_name}}<br/><i>{{container_tech}}</i>]
    {{/each}}

    %% Data stores
    {{#each data_stores}}
    {{store_id}}[({{store_name}}<br/><i>{{store_tech}}</i>)]
    {{/each}}

    %% Container relationships
    {{#each container_relations}}
    {{rel_from}} -->|{{rel_protocol}}| {{rel_to}}
    {{/each}}
```

### Component Diagram (C4 Level 3)

Shows the internal structure of the main application container.

```mermaid
graph LR
    %% Components
    {{#each components}}
    {{comp_id}}[{{comp_name}}]
    {{/each}}

    %% Component relationships
    {{#each component_relations}}
    {{comp_from}} --> {{comp_to}}
    {{/each}}
```

**Diagram Notes:**
- Diagrams render automatically in GitHub/GitLab markdown preview
- For VS Code, install Mermaid extension
- Use `/sdlc-studio trd visualise` to regenerate after TRD changes
