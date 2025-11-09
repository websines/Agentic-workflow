# Agentic Workflow Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Manager Agent                               │
│              (User-Facing Interface)                         │
│  • Understands user requests                                 │
│  • Translates to workflows                                   │
│  • Returns final results                                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 Supervisor Agent                             │
│              (Team Orchestration)                            │
│  • Breaks down tasks into subtasks                           │
│  • Assigns work to specialized agents                        │
│  • Monitors progress                                         │
│  • Synthesizes results                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐     ┌──────────┐    ┌──────────┐
    │ Research │     │  Writer  │    │  Analyst │
    │  Agent   │     │  Agent   │    │  Agent   │
    └──────────┘     └──────────┘    └──────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Git-Style Logging Database                      │
│                                                              │
│  • Run History (commits)                                     │
│  • Tool Calls (operations)                                   │
│  • Agent Decisions (reasoning)                               │
│  • Results & Feedback (outcomes)                             │
│  • Versioned Workflows (branches)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              RL Training Pipeline                            │
│                                                              │
│  • Replay successful runs                                    │
│  • Learn from feedback                                       │
│  • Optimize agent behaviors                                  │
│  • Fine-tune decision making                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           Small Action Model (Future)                        │
│                                                              │
│  • Distilled from agent behaviors                            │
│  • Fast, specialized decision making                         │
│  • Deployable to edge                                        │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Manager Agent
- **Role**: User-facing interface
- **Responsibilities**:
  - Natural language understanding of business requests
  - Workflow selection/creation
  - Result presentation
  - User feedback collection

### 2. Supervisor Agent
- **Role**: Team orchestration
- **Responsibilities**:
  - Task decomposition
  - Agent assignment
  - Progress monitoring
  - Result synthesis
  - Error handling & recovery

### 3. Specialized Worker Agents
- Research Agent
- Writer Agent
- Data Analyst Agent
- Code Agent
- (Extensible - add as needed)

### 4. Git-Style Logging Database

#### Data Model

```
Run (like a Git commit)
├── run_id: unique identifier
├── timestamp: when run started
├── workflow_type: business workflow type
├── user_input: original user request
├── parent_run_id: for workflow chains
├── status: pending/running/completed/failed
├── result: final output
└── metadata: additional context

Step (like operations within a commit)
├── step_id: unique identifier
├── run_id: parent run
├── agent_name: which agent
├── action_type: tool_call/decision/delegation
├── input: what was provided
├── output: what was produced
├── reasoning: agent's thought process
├── timestamp: when step occurred
└── duration: how long it took

ToolCall (detailed operation log)
├── tool_call_id: unique identifier
├── step_id: parent step
├── tool_name: which tool
├── parameters: input params
├── result: tool output
├── success: boolean
└── error: if any

Feedback (for RL)
├── feedback_id: unique identifier
├── run_id: which run
├── rating: quality score
├── corrections: what should've been different
├── human_feedback: explicit feedback
└── implicit_feedback: success metrics
```

### 5. Storage Strategy

```
workflow_db/
├── runs/
│   ├── 2025-01-15/
│   │   ├── run_abc123.json
│   │   └── run_def456.json
│   └── 2025-01-16/
├── steps/
│   ├── run_abc123/
│   │   ├── step_001.json
│   │   ├── step_002.json
│   │   └── ...
├── feedback/
│   ├── run_abc123_feedback.json
│   └── ...
├── workflows/
│   ├── content_creation.yaml
│   ├── data_analysis.yaml
│   └── ...
└── models/
    ├── checkpoints/
    └── metrics/
```

## Workflow Execution Flow

1. **User Request** → Manager Agent
2. **Manager** analyzes request, selects/creates workflow
3. **Manager** delegates to Supervisor with context
4. **Supervisor** breaks down into steps
5. **Supervisor** assigns steps to specialized agents
6. **Each Agent** executes, logs every action
7. **Supervisor** synthesizes results
8. **Manager** presents to user
9. **System** logs entire run for RL training

## RL Training Loop

```
1. Collect runs → Store in database
2. Identify successful patterns
3. Replay failed runs with variations
4. Update agent prompts/behaviors
5. A/B test improvements
6. Iterate
```

## Future: Action Model

Once enough data:
- Train small model on decision patterns
- Use for common/fast decisions
- Fall back to LLM for complex cases
- Continuous learning loop

## Business Workflow Examples

### Content Creation Workflow
```
User: "Create a blog post about AI agents"
↓
Manager: Understands content creation request
↓
Supervisor: Plans workflow
  1. Research Agent: Gather information about AI agents
  2. Writer Agent: Draft blog post
  3. Critic Agent: Review and suggest improvements
  4. Writer Agent: Final version
↓
Manager: Presents polished blog post to user
```

### Data Analysis Workflow
```
User: "Analyze sales trends from Q4"
↓
Manager: Understands analytics request
↓
Supervisor: Plans workflow
  1. Data Agent: Load and clean Q4 data
  2. Analyst Agent: Perform trend analysis
  3. Visualization Agent: Create charts
  4. Writer Agent: Write summary report
↓
Manager: Presents report with visualizations
```

## Implementation Phases

### Phase 1: Core System (Current)
- ✓ Basic agents
- ✓ LMStudio integration
- ○ Manager Agent
- ○ Supervisor Agent
- ○ Logging system

### Phase 2: Logging & Replay
- ○ Git-style database
- ○ Complete run tracking
- ○ Replay functionality
- ○ Feedback collection

### Phase 3: RL Pipeline
- ○ Pattern analysis
- ○ Agent improvement
- ○ A/B testing
- ○ Metrics dashboard

### Phase 4: Action Model
- ○ Data collection (large scale)
- ○ Model training
- ○ Integration
- ○ Continuous learning
