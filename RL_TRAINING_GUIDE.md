# RL Training System - Complete Guide

## What Gets RL Trained?

The Reinforcement Learning system trains **three main components**:

### 1. Supervisor's Decision-Making

**What**: Which agents to assign to which tasks, and in what order

**How it learns**:
- Observes: Task type, task description, available agents
- Decides: Which agent should handle each step
- Gets rewarded: Based on success rate, speed, quality

**Training data**:
- Every workflow execution creates state-action-reward tuples
- State: Current task, available agents, workflow step
- Action: Agent selected for the task
- Reward: Calculated from success, user feedback, speed

**Result**:
- Learned patterns like "For content_creation, use Research → Writer → Analyst"
- Agent collaboration patterns
- Optimal workflow structures

### 2. Agent Prompts/Instructions

**What**: The instructions each agent follows (their "behavior")

**How it learns**:
- Tracks performance of each agent
- Identifies underperforming agents
- Evolves their instructions based on failures
- Adds improvements like "Double-check your work" if accuracy is low

**Training data**:
- Agent performance metrics (success rate, duration)
- User feedback on agent outputs
- Error patterns

**Result**:
- Better agent instructions over time
- Specialized behaviors for different task types
- Self-improving agent prompts

### 3. Workflow Structure

**What**: The sequence of steps in a workflow

**How it learns**:
- Analyzes successful vs failed workflow runs
- Identifies optimal step ordering
- Learns when to add/remove steps

**Training data**:
- Complete workflow execution logs
- Which workflows succeeded/failed
- Bottlenecks and failure points

**Result**:
- Optimized workflow templates
- Dynamic workflow adaptation
- Self-modifying workflows

---

## The RL Training Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                 1. EXPERIENCE COLLECTION                     │
│                                                              │
│  Workflow Execution → Every run logged as experiences       │
│  Format: (State, Action, Reward, Next State)                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  2. REWARD CALCULATION                       │
│                                                              │
│  Components:                                                 │
│  • Success/Failure: +10 / -10                                │
│  • User Satisfaction: +5 * (rating - 0.5) * 2                │
│  • Speed: +2 * (1 - duration/baseline)                       │
│  • Cost: -1 * extra_steps                                    │
│  • Quality: +3 * feedback_rating                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                3. EXPERIENCE REPLAY BUFFER                   │
│                                                              │
│  Stores up to 10,000 experiences                             │
│  Prioritizes successful experiences (70% good, 30% bad)      │
│  Enables learning from past runs                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  4. POLICY OPTIMIZATION                      │
│                                                              │
│  Current: Pattern extraction from successful runs           │
│  Future: Neural network policy gradient                     │
│                                                              │
│  Learns:                                                     │
│  • "For task X, use agent Y"                                 │
│  • "Agent A works well with agent B"                         │
│  • "Step order: Research → Analyze → Write"                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   5. PROMPT EVOLUTION                        │
│                                                              │
│  Analyzes agent performance                                  │
│  Mutates prompts for underperformers                         │
│  Tracks prompt versions                                      │
│  Keeps best performing prompts                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               6. AGENT EVOLUTION & CREATION                  │
│                                                              │
│  • Kill: Agents with success rate < 70%                      │
│  • Evolve: Apply RL-learned improvements                     │
│  • Create: Spawn new agents when needed                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    7. DEPLOY & ITERATE                       │
│                                                              │
│  Updated agents used in next workflows                       │
│  Performance monitored                                       │
│  Continuous improvement loop                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components Explained

### RewardCalculator

**Purpose**: Determines what the system optimizes for

**Configurable weights**:
```python
weights = {
    "success": 10.0,          # Completing successfully is most important
    "user_satisfaction": 5.0,  # User feedback matters
    "speed": 2.0,             # Faster is better
    "cost": -1.0,             # Fewer LLM calls = lower cost
    "quality": 3.0,           # Quality of output
}
```

**Customization**: Adjust these weights to optimize for different goals
- Business focused on quality: Increase `quality` weight
- Cost-sensitive: Increase `cost` weight (negative)
- Speed-critical: Increase `speed` weight

### ExperienceBuffer

**Purpose**: Stores past experiences for learning

**Features**:
- **Capacity**: 10,000 experiences
- **Prioritization**: 70% successful, 30% failed (learn what works!)
- **Separate buffers**: Success and failure experiences stored separately
- **Task-specific retrieval**: Get experiences for specific workflow types

**Why prioritize success?**
- Learning from failures teaches what to avoid
- Learning from successes teaches what to repeat
- 70/30 split balances both

### PolicyOptimizer

**Purpose**: Learns optimal decision-making

**Current approach** (v1):
- **Pattern extraction**: "For content_creation at step 0, Research Agent works best"
- **Keyword matching**: "If task contains 'analyze', use Analyst"
- **Step ordering**: Learn sequence from successful runs

**Future approach** (v2):
- **Neural network**: Small model that predicts best agent for any task
- **Embedding-based**: Use task embeddings for similarity
- **Continuous learning**: Real-time updates

### PromptEvolver

**Purpose**: Evolves agent instructions based on performance

**Evolution rules**:
```
IF success_rate < 0.5:
  ADD "Double-check your work before responding"
  ADD "If unsure, ask for clarification"

IF avg_duration > 3000ms:
  ADD "Be concise and efficient"

IF quality_score < 0.7:
  ADD "Focus on accuracy over speed"
```

**Version tracking**: All prompt versions saved with metrics

---

## How to Use the RL Training System

### 1. Automatic Training (Recommended)

The system trains automatically during evolution:

```python
from workflow_engine import WorkflowEngine

engine = WorkflowEngine()

# Run some workflows...
engine.execute("Create a blog post", "content_creation")
engine.execute("Analyze data trends", "data_analysis")
# ... run 10-20 workflows

# Trigger evolution (includes RL training)
engine.evolve_system()
```

This will:
1. Collect experiences from all recent runs
2. Train the Supervisor's policy
3. Evolve agent prompts
4. Apply evolutionary selection
5. Show performance trends

### 2. Manual Training

For more control:

```python
from workflow_engine import WorkflowEngine

engine = WorkflowEngine()

# Access RL system directly
rl = engine.rl_system

# Collect experiences from last 100 runs
rl.collect_experiences_from_recent_runs(limit=100)

# Train Supervisor policy
rl.train_supervisor_policy(batch_size=32, iterations=50)

# Evolve agent prompts
evolved = rl.evolve_agent_prompts(engine.supervisor.agent_metrics)

# Get recommendations for a new task
recommendations = rl.get_policy_recommendations(
    "content_creation",
    "Write a technical article"
)

# Show performance trends
rl.print_performance_trends()
```

### 3. Continuous Training Loop

For production deployment:

```python
import time
from workflow_engine import WorkflowEngine

engine = WorkflowEngine()

# Run continuous training
while True:
    # Every 100 workflows, trigger training
    stats = engine.storage.get_run_statistics()

    if stats["total_runs"] % 100 == 0:
        print("Running periodic RL training...")
        engine.evolve_system(run_rl_training=True)

    time.sleep(3600)  # Check hourly
```

---

## What the System Learns Over Time

### Phase 1: Basic Patterns (0-100 runs)

- "Research Agent is good for research tasks"
- "Writer Agent creates content"
- "Analyst Agent analyzes data"

### Phase 2: Collaboration Patterns (100-500 runs)

- "Research → Writer → Analyst works well for content_creation"
- "Analyst → Planner works well for strategy tasks"
- "Coder Agent should come after Planner Agent"

### Phase 3: Task-Specific Optimization (500-1000 runs)

- "For 'blog post' tasks, skip Analyst, go Research → Writer directly"
- "For 'data analysis', use Analyst → Analyst → Writer (double analysis)"
- "For coding tasks, create specialized Coder Agent"

### Phase 4: Self-Modification (1000+ runs)

- Workflows modify themselves based on performance
- Agents rewrite their own instructions
- New specialized agents spawned automatically
- Optimal workflow structures discovered

---

## Performance Metrics

### What We Track

**Run-level metrics**:
- Total runs
- Success rate
- Average duration
- User satisfaction (from feedback)

**Agent-level metrics**:
- Tasks completed
- Tasks failed
- Success rate
- Average duration
- Collaboration effectiveness

**Workflow-level metrics**:
- Most/least successful workflows
- Optimal agent sequences
- Bottlenecks
- Failure patterns

### How to Monitor

```python
# System-wide statistics
engine.print_statistics()

# Performance trends over time
engine.rl_system.print_performance_trends()

# Agent-specific performance
for agent_name, metrics in engine.supervisor.agent_metrics.items():
    print(f"{agent_name}: {metrics['success_rate']:.1%} success")
```

---

## Advanced: Training Small Action Models

### Current State

Right now, the Supervisor uses the LLM for every decision. This works but is:
- Slow (LLM inference time)
- Expensive (many API calls)
- Requires internet connection

### Future: Distilled Action Models

Once we have enough data (10,000+ runs), we can train a small action model:

**Architecture**:
```
Input: [task_embedding, available_agents, step]
   ↓
Small Neural Network (< 1MB)
   ↓
Output: [agent_1_prob, agent_2_prob, ..., agent_n_prob]
```

**Benefits**:
- **Fast**: Inference in microseconds
- **Cheap**: No API costs
- **Offline**: Works without internet
- **Specialized**: Tuned for your workflows

**Training data**:
- All the state-action-reward tuples we've collected
- Millions of experiences from successful runs
- Supervised learning: Learn to mimic successful decisions

**Deployment**:
```python
# Instead of asking LLM for decision
best_agent = supervisor.agent.run("Which agent should handle this?")

# Use small action model
best_agent = action_model.predict(task_embedding, available_agents, step)
```

**Continuous improvement**:
- Action model handles common cases (fast)
- LLM handles novel cases (smart)
- Learn from LLM decisions to improve action model
- Continuous distillation loop

---

## Customizing the RL System

### Adjust Reward Weights

```python
# In rl_trainer.py
rl_system.reward_calculator.weights = {
    "success": 20.0,    # 2x emphasis on success
    "speed": 5.0,       # Optimize more for speed
    "cost": -3.0,       # Penalize cost heavily
}
```

### Customize Evolution Rules

```python
# In agent_factory.py
def custom_evolution_rule(agent_name, metrics):
    if metrics["success_rate"] < 0.6:  # Stricter threshold
        return ["Be more careful", "Validate outputs"]
    if metrics["avg_duration"] > 5000:  # Custom duration target
        return ["Work faster", "Skip unnecessary steps"]
```

### Create Custom Agent Templates

```python
# Add to AgentFactory
def _get_custom_specialist_template(self):
    return AgentSpecification(
        name="Custom Specialist",
        role="Your specialized role",
        instructions=[
            "Your custom instructions",
            "Optimized for your use case",
        ]
    )
```

---

## Troubleshooting

### "Not enough experiences yet"

**Problem**: Need minimum experiences before training

**Solution**: Run at least 10-20 workflows before triggering evolution

```python
# Check buffer size
print(f"Experiences: {engine.rl_system.policy_optimizer.experience_buffer.size()}")

# Need at least 32 for default batch size
```

### "No patterns learned"

**Problem**: Not enough successful runs

**Solution**:
- Check that workflows are completing successfully
- Lower success threshold in reward calculator
- Run more varied workflows

### "Agent performance not improving"

**Problem**: RL training not being applied

**Solution**:
- Ensure `evolve_system(run_rl_training=True)` is called
- Check that evolved prompts are being applied
- Monitor agent metrics before/after evolution

---

## Best Practices

1. **Run many workflows before first evolution**
   - Minimum: 20 runs
   - Recommended: 50-100 runs
   - This gives RL enough data to learn patterns

2. **Trigger evolution periodically**
   - After every 100 runs
   - Or weekly for production systems
   - Don't evolve too frequently (need time to gather data)

3. **Monitor performance trends**
   - Use `rl_system.print_performance_trends()`
   - Watch for improving success rates
   - Track agent metrics

4. **Collect user feedback**
   - Explicit ratings (0.0 to 1.0)
   - Qualitative feedback
   - This is the most valuable training signal

5. **Start conservative, then optimize**
   - Initial weights favor success over speed
   - Once stable, optimize for speed and cost
   - Adjust based on your priorities

6. **Version control learned policies**
   - Policies saved to `workflow_db/rl_models/policy.json`
   - Commit to git after major improvements
   - Can rollback if evolution goes wrong

---

## Summary

**The RL training system learns**:
1. ✅ Which agents work best for which tasks
2. ✅ Optimal agent collaboration patterns
3. ✅ How to improve agent instructions
4. ✅ When to create new specialized agents
5. ✅ Workflow structures that succeed

**It does this by**:
1. Logging every workflow execution as experiences
2. Calculating rewards based on success, speed, quality
3. Learning patterns from successful runs
4. Evolving agent prompts based on performance
5. Applying evolutionary selection (kill/modify/create)

**Result**: A self-improving system that gets better over time!

---

**Ready to start?**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the production system
python production_example.py

# Execute some workflows
# Then trigger evolution
# Watch the system improve!
```
